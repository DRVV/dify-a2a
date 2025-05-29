#!/usr/bin/env python3
"""
Chainlit Web UI for Dify Orchestrator Debugging
Interactive chat interface for testing multiple chatflows in parallel with role-based routing
"""

import asyncio
import json
import time
from typing import Dict, Any
import chainlit as cl
from orchestrator import DifyOrchestrator

# Global orchestrator instance
orchestrator = None

# Global storage for the last workflow result (for event builder)
last_workflow_result = None

def format_speaker_message(speaker_icon: str, speaker_name: str, content: str) -> str:
    """Format message with prominent speaker identification."""
    return f"{speaker_icon} **{speaker_name}**\n━━━━━━━━━━━━━━━━━━━━\n{content}"

@cl.on_chat_start
async def start():
    """Initialize the orchestrator when chat starts."""
    global orchestrator
    
    # Send welcome message
    await cl.Message(
        content=format_speaker_message(
            "⚙️", "SYSTEM", 
            "🚀 **Dify Orchestrator Chat Interface**\n\nInitializing orchestrator..."
        )
    ).send()
    
    try:
        # Initialize orchestrator
        orchestrator = DifyOrchestrator()
        
        # Get chatflow information
        chatflow_names = orchestrator.get_chatflow_names()
        content_chatflows = orchestrator.get_content_chatflows()
        summarizer_chatflow = orchestrator.get_summarizer_chatflow()
        event_builder_chatflow = orchestrator.get_event_builder_chatflow()
        
        if not chatflow_names:
            await cl.Message(
                content=format_speaker_message(
                    "❌", "ERROR",
                    "⚠️ **No chatflows configured!**\n\nPlease check your .env file and ensure:\n- `DIFY_CHATFLOW_COUNT` is set\n- `DIFY_CHATFLOW_N_API_KEY` variables are configured"
                )
            ).send()
            return
        
        # Display configured chatflows by role
        content_info = []
        for name in content_chatflows:
            config = orchestrator.get_chatflow_config(name)
            content_info.append(f"• **{name}**: {config.description}")
        
        summarizer_info = "📝 **Summarizer Agent**: Not configured" if not summarizer_chatflow else f"📝 **Summarizer Agent**: {summarizer_chatflow}"
        event_builder_info = "🎯 **Event Builder**: Not configured" if not event_builder_chatflow else f"🎯 **Event Builder**: {event_builder_chatflow}"
        
        welcome_msg = f"""✅ **Role-Based Orchestrator Ready!**

**Content Chatflows ({len(content_chatflows)}):**
{chr(10).join(content_info) if content_info else '• None configured'}

{summarizer_info}
{event_builder_info}

🔄 **Enhanced Workflow:**
- Type any message below
- Your message will be sent to content chatflows in parallel
- Individual responses will appear first
- Then responses will be summarized (if summarizer is configured)
- Finally, events and actions will be generated automatically (if event builder is configured)
- Perfect for multi-agent analysis and synthesis!

Ready to chat! 🎉"""
        
        await cl.Message(
            content=format_speaker_message("⚙️", "SYSTEM", welcome_msg)
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=format_speaker_message(
                "❌", "ERROR",
                f"❌ **Failed to initialize orchestrator:**\n```\n{str(e)}\n```\n\nPlease check your configuration and try again."
            )
        ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming user messages and orchestrate responses."""
    global orchestrator
    
    if not orchestrator:
        await cl.Message(
            content=format_speaker_message(
                "❌", "ERROR",
                "❌ Orchestrator not initialized. Please refresh the page."
            )
        ).send()
        return
    
    user_message = message.content
    content_chatflows = orchestrator.get_content_chatflows()
    summarizer_chatflow = orchestrator.get_summarizer_chatflow()
    
    if not content_chatflows:
        await cl.Message(
            content=format_speaker_message(
                "❌", "ERROR",
                "❌ No content chatflows available."
            )
        ).send()
        return
    
    # Show initial processing message
    processing_msg = await cl.Message(
        content=format_speaker_message(
            "⚡", "PROCESSING",
            f"📤 **Step 1/2**: Sending your message to {len(content_chatflows)} content chatflows..."
        )
    ).send()
    
    start_time = time.time()
    
    try:
        # Use the new orchestrate_with_summary method
        result = orchestrator.orchestrate_with_summary(
            query=user_message,
            user="chainlit_user"
        )
        
        total_time = time.time() - start_time
        
        # Remove processing message
        await processing_msg.remove()
        
        # Display results using the new transparent multi-step flow
        await display_orchestrated_results(result, total_time, summarizer_chatflow is not None)
            
    except Exception as e:
        await processing_msg.remove()
        await cl.Message(
            content=format_speaker_message(
                "❌", "ERROR",
                f"❌ **Orchestrator Error:**\n```\n{str(e)}\n```"
            )
        ).send()

async def display_orchestrated_results(result: Dict[str, Any], total_time: float, has_summarizer: bool):
    """Display results from the orchestrated multi-step workflow."""
    global last_workflow_result
    
    # Store the result for potential event builder use
    last_workflow_result = result
    
    content_responses = result.get("content_responses", {})
    content_errors = result.get("content_errors", {})
    content_success_count = result.get("content_success_count", 0)
    content_total_count = result.get("content_total_count", 0)
    summary_response = result.get("summary_response")
    summary_error = result.get("summary_error")
    status = result.get("status", "unknown")
    
    # Step 1: Display content chatflow results
    if content_responses:
        if content_success_count == content_total_count:
            status_msg = f"✅ **All {content_success_count} content chatflows responded successfully**"
        else:
            status_msg = f"⚠️ **Partial success: {content_success_count}/{content_total_count} content chatflows responded**"
        
        await cl.Message(
            content=format_speaker_message(
                "📊", "CONTENT RESULTS",
                f"{status_msg} (Step 1 completed in {total_time:.2f}s)"
            )
        ).send()
        
        # Add small delay to prevent payload bundling
        await asyncio.sleep(0.1)
        
        # Display individual content responses with delays
        for chatflow_name, response in content_responses.items():
            await display_chatflow_response(chatflow_name, response, success=True)
            await asyncio.sleep(0.1)  # Small delay between messages
        
        # Display content errors if any
        for chatflow_name, error in content_errors.items():
            await cl.Message(
                content=format_speaker_message(
                    "❌", f"{chatflow_name} ERROR",
                    f"❌ **Error:** {error}"
                )
            ).send()
            await asyncio.sleep(0.1)  # Small delay between messages
    else:
        # All content chatflows failed
        await cl.Message(
            content=format_speaker_message(
                "📊", "CONTENT RESULTS",
                f"❌ **All content chatflows failed** (Step 1 failed in {total_time:.2f}s)"
            )
        ).send()
        
        await asyncio.sleep(0.1)
        
        for chatflow_name, error in content_errors.items():
            await cl.Message(
                content=format_speaker_message(
                    "❌", f"{chatflow_name} ERROR",
                    f"❌ **Error:** {error}"
                )
            ).send()
            await asyncio.sleep(0.1)
        return
    
    # Step 2: Handle summarization (if configured)
    if has_summarizer:
        # Add visual separator
        await cl.Message(
            content=format_speaker_message(
                "🔄", "PROCESSING",
                "📝 **Step 2/2**: Generating summary from responses..."
            )
        ).send()
        
        await asyncio.sleep(0.2)  # Longer delay before summary
        
        if summary_response:
            # Extract summary content
            summary_content = summary_response.get("answer", "")
            if not summary_content:
                summary_content = summary_response.get("data", summary_response.get("content", str(summary_response)))
            
            await cl.Message(
                content=format_speaker_message(
                    "📝", "SUMMARY",
                    summary_content if summary_content else "*(No summary content)*"
                )
            ).send()
            
            await asyncio.sleep(0.2)  # Delay after summary
            
            # Check if event builder is available and call it automatically
            event_builder_chatflow = orchestrator.get_event_builder_chatflow()
            if event_builder_chatflow:
                # Automatically trigger event builder
                await cl.Message(
                    content=format_speaker_message(
                        "🔄", "PROCESSING",
                        f"🎯 **Step 3/3**: Generating events and actions using {event_builder_chatflow}..."
                    )
                ).send()
                
                await asyncio.sleep(0.2)  # Delay before event builder
                
                try:
                    start_time = time.time()
                    
                    # Format data for event builder
                    event_builder_input = orchestrator.format_data_for_event_builder(
                        original_query=last_workflow_result.get("query", ""),
                        content_responses=last_workflow_result.get("content_responses", {}),
                        summary_response=last_workflow_result.get("summary_response")
                    )
                    
                    # Send to event builder
                    event_builder_response = orchestrator.send_to_chatflow(
                        chatflow_name=event_builder_chatflow,
                        query=event_builder_input,
                        user="chainlit_user"
                    )
                    
                    total_time = time.time() - start_time
                    
                    # Extract event builder content
                    event_content = event_builder_response.get("answer", "")
                    if not event_content:
                        event_content = event_builder_response.get("data", event_builder_response.get("content", str(event_builder_response)))
                    
                    # Display event builder result
                    await cl.Message(
                        content=format_speaker_message(
                            "🎯", "EVENT BUILDER",
                            event_content if event_content else "*(No event content generated)*"
                        )
                    ).send()
                    
                    await asyncio.sleep(0.2)  # Delay after event builder
                    
                    # Final completion message
                    final_msg = f"🎉 **Complete 3-step workflow finished successfully!**\n\n✅ Content analysis completed\n✅ Summary generated\n✅ Events and actions created (in {total_time:.2f}s)"
                    
                except Exception as e:
                    await cl.Message(
                        content=format_speaker_message(
                            "❌", "EVENT BUILDER ERROR",
                            f"❌ **Event builder failed:** {str(e)}"
                        )
                    ).send()
                    await asyncio.sleep(0.1)
                    final_msg = "⚠️ **Workflow completed with partial success.** Content responses received and summarized, but event generation failed."
            else:
                # No event builder configured
                if status == "success":
                    final_msg = "🎉 **2-step workflow completed successfully!**\n\n✅ Content analysis completed\n✅ Summary generated"
                else:
                    final_msg = "⚠️ **Workflow completed with partial success.** Content responses received and summarized, but some errors occurred."
            
            await cl.Message(
                content=format_speaker_message(
                    "✅", "WORKFLOW COMPLETE",
                    final_msg
                )
            ).send()
        elif summary_error:
            await cl.Message(
                content=format_speaker_message(
                    "❌", "SUMMARY ERROR",
                    f"❌ **Summary generation failed:** {summary_error}"
                )
            ).send()
        else:
            await cl.Message(
                content=format_speaker_message(
                    "⚠️", "SUMMARY",
                    "⚠️ **No summary generated** (unknown error)"
                )
            ).send()
    else:
        # No summarizer configured - add delay before final message
        await asyncio.sleep(0.2)
        await cl.Message(
            content=format_speaker_message(
                "ℹ️", "INFO",
                "ℹ️ **No summarizer configured.** Only content chatflow responses are shown."
            )
        ).send()

async def display_chatflow_response(chatflow_name: str, response: Dict[str, Any], success: bool = True):
    """Display an individual chatflow response."""
    # Extract the main answer
    answer = response.get("answer", "")
    
    if not answer:
        # Fallback to other possible response fields
        answer = response.get("data", response.get("content", str(response)))
    
    # Create the main response message
    content = answer if answer else "*(No response content)*"
    
    await cl.Message(
        content=format_speaker_message(
            "🤖", chatflow_name,
            content
        )
    ).send()
    
    # Debug info is hidden - can be enabled by uncommenting below
    # debug_info = create_debug_info(response)
    # if debug_info:
    #     await cl.Message(
    #         content=f"**Debug Info for {chatflow_name}:**\n```json\n{debug_info}\n```",
    #         author=f"🔍 {chatflow_name} Debug"
    #     ).send()

def create_debug_info(response: Dict[str, Any]) -> str:
    """Create formatted debug information from response."""
    try:
        # Remove the answer to avoid duplication
        debug_data = {k: v for k, v in response.items() if k not in ["answer", "_query", "_chatflow_name"]}
        
        if not debug_data:
            return ""
        
        return json.dumps(debug_data, indent=2, ensure_ascii=False)[:500] + ("..." if len(str(debug_data)) > 500 else "")
    except Exception:
        return ""

# Note: Event builder now runs automatically after summarization
# No need for manual button triggers

@cl.on_stop
async def stop():
    """Cleanup when chat stops."""
    await cl.Message(
        content=format_speaker_message(
            "⚙️", "SYSTEM",
            "👋 Chat session ended. Refresh to start a new session."
        )
    ).send()

if __name__ == "__main__":
    # This allows running the file directly for development
    import subprocess
    import sys
    
    print("🚀 Starting Chainlit Dify Orchestrator...")
    print("📝 Make sure your .env file is configured with chatflow settings!")
    print("🌐 The web interface will open automatically...")
    
    subprocess.run([sys.executable, "-m", "chainlit", "run", __file__, "--watch"])
