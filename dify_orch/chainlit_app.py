#!/usr/bin/env python3
"""
Chainlit Web UI for Dify Orchestrator Debugging
Interactive chat interface for testing multiple chatflows in parallel
"""

import asyncio
import json
import time
from typing import Dict, Any
import chainlit as cl
from orchestrator import DifyOrchestrator

# Global orchestrator instance
orchestrator = None

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
        
        if not chatflow_names:
            await cl.Message(
                content=format_speaker_message(
                    "❌", "ERROR",
                    "⚠️ **No chatflows configured!**\n\nPlease check your .env file and ensure:\n- `DIFY_CHATFLOW_COUNT` is set\n- `DIFY_CHATFLOW_N_API_KEY` variables are configured"
                )
            ).send()
            return
        
        # Display configured chatflows
        chatflow_info = []
        for name in chatflow_names:
            config = orchestrator.get_chatflow_config(name)
            chatflow_info.append(f"• **{name}**: {config.description}")
        
        welcome_msg = f"""✅ **Orchestrator Ready!**

**Active Chatflows ({len(chatflow_names)}):**
{chr(10).join(chatflow_info)}

💬 **How it works:**
- Type any message below
- Your message will be sent to all chatflows in parallel
- Each chatflow response will appear as a separate chat bubble
- Perfect for debugging and comparing responses!

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
    chatflow_names = orchestrator.get_chatflow_names()
    
    if not chatflow_names:
        await cl.Message(
            content=format_speaker_message(
                "❌", "ERROR",
                "❌ No chatflows available."
            )
        ).send()
        return
    
    # Show thinking message
    thinking_msg = await cl.Message(
        content=format_speaker_message(
            "⚡", "PROCESSING",
            f"🤔 Sending your message to {len(chatflow_names)} chatflows..."
        )
    ).send()
    
    start_time = time.time()
    
    try:
        # Send to all chatflows in parallel
        result = orchestrator.send_to_all_chatflows(
            query=user_message,
            user="chainlit_user"
        )
        
        total_time = time.time() - start_time
        
        # Remove thinking message
        await thinking_msg.remove()
        
        # Display results
        if result.get("status") == "success":
            await display_successful_responses(result, total_time)
        elif result.get("status") == "partial_success":
            await display_partial_responses(result, total_time)
        else:
            await display_failed_responses(result, total_time)
            
    except Exception as e:
        await thinking_msg.remove()
        await cl.Message(
            content=format_speaker_message(
                "❌", "ERROR",
                f"❌ **Orchestrator Error:**\n```\n{str(e)}\n```"
            )
        ).send()

async def display_successful_responses(result: Dict[str, Any], total_time: float):
    """Display successful responses from all chatflows."""
    responses = result.get("responses", {})
    
    # Summary message
    await cl.Message(
        content=format_speaker_message(
            "📊", "RESULTS",
            f"✅ **All {len(responses)} chatflows responded successfully** (Total time: {total_time:.2f}s)"
        )
    ).send()
    
    # Individual responses
    for chatflow_name, response in responses.items():
        await display_chatflow_response(chatflow_name, response, success=True)

async def display_partial_responses(result: Dict[str, Any], total_time: float):
    """Display partial responses when some chatflows fail."""
    responses = result.get("responses", {})
    errors = result.get("errors", {})
    success_count = result.get("success_count", 0)
    total_count = result.get("total_count", 0)
    
    # Summary message
    await cl.Message(
        content=format_speaker_message(
            "📊", "RESULTS",
            f"⚠️ **Partial success: {success_count}/{total_count} chatflows responded** (Total time: {total_time:.2f}s)"
        )
    ).send()
    
    # Successful responses
    for chatflow_name, response in responses.items():
        await display_chatflow_response(chatflow_name, response, success=True)
    
    # Failed responses
    for chatflow_name, error in errors.items():
        await cl.Message(
            content=format_speaker_message(
                "❌", f"{chatflow_name} ERROR",
                f"❌ **Error:** {error}"
            )
        ).send()

async def display_failed_responses(result: Dict[str, Any], total_time: float):
    """Display when all chatflows fail."""
    errors = result.get("errors", {})
    
    await cl.Message(
        content=format_speaker_message(
            "📊", "RESULTS",
            f"❌ **All chatflows failed** (Total time: {total_time:.2f}s)"
        )
    ).send()
    
    for chatflow_name, error in errors.items():
        await cl.Message(
            content=format_speaker_message(
                "❌", f"{chatflow_name} ERROR",
                f"❌ **Error:** {error}"
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
