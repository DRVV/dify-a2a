#!/usr/bin/env python3
"""
Enhanced test script for the Dify Orchestrator.
This script demonstrates both new dynamic functionality and backward compatibility.
"""

import logging
import json
import warnings
from orchestrator import DifyOrchestrator

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_orchestrator_initialization(orchestrator: DifyOrchestrator):
    """Test the new dynamic initialization."""
    print("\n" + "="*60)
    print("Testing Dynamic Orchestrator Initialization")
    print("="*60)
    
    try:
        chatflow_names = orchestrator.get_chatflow_names()
        print(f"✓ Successfully initialized {len(chatflow_names)} chatflows:")
        for name in chatflow_names:
            config = orchestrator.get_chatflow_config(name)
            print(f"  - {name}: {config.description}")
        return True
    except Exception as e:
        print(f"❌ Error in initialization test: {e}")
        return False

def test_new_individual_chatflow_access(orchestrator: DifyOrchestrator):
    """Test sending messages to individual chatflows using new API."""
    print("\n" + "="*60)
    print("Testing New Individual Chatflow Access")
    print("="*60)
    
    test_message = "Hello, this is a test message using the new API."
    chatflow_names = orchestrator.get_chatflow_names()
    test_results = {}
    
    for chatflow_name in chatflow_names:
        print(f"\n--- Testing Chatflow '{chatflow_name}' (New API) ---")
        try:
            response = orchestrator.send_to_chatflow(
                chatflow_name=chatflow_name,
                query=test_message
            )
            print(f"✓ Response from '{chatflow_name}': {json.dumps(response, indent=2, ensure_ascii=False)}")
            test_results[chatflow_name] = True
        except Exception as e:
            print(f"❌ Error with chatflow '{chatflow_name}': {e}")
            test_results[chatflow_name] = False
    
    return test_results

def test_parallel_orchestration(orchestrator: DifyOrchestrator):
    """Test sending the same message to multiple chatflows in parallel."""
    print("\n" + "="*60)
    print("Testing Parallel Orchestration (New Feature)")
    print("="*60)
    
    test_message = "Compare your capabilities with other AI systems."
    chatflow_names = orchestrator.get_chatflow_names()
    
    if len(chatflow_names) < 2:
        print("⚠️ Need at least 2 chatflows for parallel testing. Skipping...")
        return False
    
    try:
        # Test sending to all chatflows
        print("\n--- Testing Send to All Chatflows ---")
        all_response = orchestrator.send_to_all_chatflows(test_message)
        print(f"✓ All Chatflows Response: {json.dumps(all_response, indent=2, ensure_ascii=False)}")
        
        # Test sending to specific subset
        print(f"\n--- Testing Send to Subset: {chatflow_names[:2]} ---")
        subset_response = orchestrator.send_to_multiple_chatflows(
            chatflow_names=chatflow_names[:2],
            query=test_message
        )
        print(f"✓ Subset Response: {json.dumps(subset_response, indent=2, ensure_ascii=False)}")
        
        return True
    except Exception as e:
        print(f"❌ Error in parallel orchestration: {e}")
        return False

def test_sequential_orchestration(orchestrator: DifyOrchestrator):
    """Test sequential workflow using new API."""
    print("\n" + "="*60)
    print("Testing Sequential Orchestration (New Feature)")
    print("="*60)
    
    chatflow_names = orchestrator.get_chatflow_names()
    
    if len(chatflow_names) < 2:
        print("⚠️ Need at least 2 chatflows for sequential testing. Skipping...")
        return False
    
    initial_query = "Generate a short creative story about a robot."
    
    try:
        sequential_result = orchestrator.orchestrate_sequential(
            chatflow_sequence=chatflow_names,
            initial_query=initial_query
        )
        
        if sequential_result.get("status") == "success":
            print(f"✓ Sequential Orchestration Result: {json.dumps(sequential_result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Sequential Orchestration Failed: {json.dumps(sequential_result, indent=2, ensure_ascii=False)}")
            return False
    except Exception as e:
        print(f"❌ Error in sequential orchestration: {e}")
        return False

def test_error_handling(orchestrator: DifyOrchestrator):
    """Test error handling for invalid chatflow names."""
    print("\n" + "="*60)
    print("Testing Error Handling")
    print("="*60)
    
    test_message = "This should fail gracefully."
    
    # Test invalid chatflow name
    print("\n--- Testing Invalid Chatflow Name ---")
    try:
        orchestrator.send_to_chatflow("non_existent_chatflow", test_message)
        print("❌ Should have raised an error for invalid chatflow name")
        return False
    except ValueError as e:
        print(f"✓ Correctly handled invalid chatflow name: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error type: {e}")
        return False
    
    # Test partial failure in multiple chatflows
    print("\n--- Testing Partial Failure Handling ---")
    try:
        invalid_names = ["valid_name", "invalid_name"]
        if orchestrator.get_chatflow_names():
            invalid_names[0] = orchestrator.get_chatflow_names()[0]
        
        result = orchestrator.send_to_multiple_chatflows(
            chatflow_names=invalid_names,
            query=test_message
        )
        
        if result.get("status") == "partial_success":
            print(f"✓ Correctly handled partial failure: {result['success_count']}/{result['total_count']} successful")
            return True
        else:
            print(f"⚠️ Unexpected result status: {result.get('status')}")
            return False
    except Exception as e:
        print(f"❌ Error in partial failure test: {e}")
        return False

def test_backward_compatibility(orchestrator: DifyOrchestrator):
    """Test backward compatibility with legacy methods."""
    print("\n" + "="*60)
    print("Testing Backward Compatibility (Legacy Methods)")
    print("="*60)
    
    test_message = "Testing backward compatibility."
    test_results = {"legacy_individual": False, "legacy_dual": False, "legacy_sequential": False}
    
    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        
        # Test legacy individual chatflow methods
        print("\n--- Testing Legacy Individual Methods ---")
        try:
            response_1 = orchestrator.send_to_chatflow_1(test_message)
            print(f"✓ Legacy Chatflow 1 Response: {json.dumps(response_1, indent=2, ensure_ascii=False)}")
            
            response_2 = orchestrator.send_to_chatflow_2(test_message)
            print(f"✓ Legacy Chatflow 2 Response: {json.dumps(response_2, indent=2, ensure_ascii=False)}")
            
            test_results["legacy_individual"] = True
        except Exception as e:
            print(f"❌ Error with legacy individual methods: {e}")
        
        # Test legacy dual response
        print("\n--- Testing Legacy Dual Response ---")
        try:
            dual_response = orchestrator.orchestrate_dual_response(test_message)
            print(f"✓ Legacy Dual Response: {json.dumps(dual_response, indent=2, ensure_ascii=False)}")
            test_results["legacy_dual"] = True
        except Exception as e:
            print(f"❌ Error with legacy dual response: {e}")
        
        # Test legacy sequential workflow
        print("\n--- Testing Legacy Sequential Workflow ---")
        try:
            sequential_result = orchestrator.sequential_workflow("Generate a short poem.")
            if sequential_result.get("status") == "success":
                print(f"✓ Legacy Sequential Result: {json.dumps(sequential_result, indent=2, ensure_ascii=False)}")
                test_results["legacy_sequential"] = True
            else:
                print(f"❌ Legacy Sequential Failed: {json.dumps(sequential_result, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"❌ Error with legacy sequential workflow: {e}")
        
        # Check deprecation warnings
        deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
        if deprecation_warnings:
            print(f"\n✓ Deprecation warnings correctly issued: {len(deprecation_warnings)} warnings")
            for warning in deprecation_warnings:
                print(f"  - {warning.message}")
        else:
            print("\n⚠️ Expected deprecation warnings but none were issued")
    
    return test_results

def test_scalability_demo(orchestrator: DifyOrchestrator):
    """Demonstrate scalability with current configuration."""
    print("\n" + "="*60)
    print("Scalability Demonstration")
    print("="*60)
    
    chatflow_names = orchestrator.get_chatflow_names()
    print(f"Current configuration supports {len(chatflow_names)} chatflows")
    
    if len(chatflow_names) >= 2:
        print("\n--- Demonstrating Various Orchestration Patterns ---")
        
        # Pattern 1: Round-robin style
        query = "What's your primary function?"
        for i, name in enumerate(chatflow_names):
            print(f"Round {i+1}: Querying '{name}'")
            try:
                response = orchestrator.send_to_chatflow(name, query)
                answer = response.get("answer", "No answer field")[:100] + "..."
                print(f"  Response preview: {answer}")
            except Exception as e:
                print(f"  Error: {e}")
        
        # Pattern 2: Custom sequence
        print(f"\n--- Custom Sequence: {' -> '.join(chatflow_names)} ---")
        try:
            result = orchestrator.orchestrate_sequential(
                chatflow_sequence=chatflow_names,
                initial_query="Start a collaborative story."
            )
            if result.get("status") == "success":
                print(f"✓ Collaborative result created through {len(chatflow_names)} steps")
                final_answer = result.get("final_answer", "")[:200] + "..."
                print(f"  Final result preview: {final_answer}")
            else:
                print(f"❌ Collaborative sequence failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"❌ Error in custom sequence: {e}")
    
    print(f"\n💡 To add more chatflows:")
    print(f"   1. Increment DIFY_CHATFLOW_COUNT in .env")
    print(f"   2. Add DIFY_CHATFLOW_N_API_KEY, DIFY_CHATFLOW_N_NAME, DIFY_CHATFLOW_N_DESCRIPTION")
    print(f"   3. Restart the application")

def main():
    """Main test function."""
    setup_logging()
    
    print("Enhanced Dify Orchestrator Test Script")
    print("="*60)
    print("Testing both new dynamic features and backward compatibility")
    
    try:
        # Initialize the orchestrator
        print("Initializing Dify Orchestrator...")
        orchestrator = DifyOrchestrator()
        print("✓ Orchestrator initialized successfully!")
        
        # Run all tests
        tests = [
            ("Initialization", test_orchestrator_initialization),
            ("New Individual Access", test_new_individual_chatflow_access),
            ("Parallel Orchestration", test_parallel_orchestration),
            ("Sequential Orchestration", test_sequential_orchestration),
            ("Error Handling", test_error_handling),
            ("Backward Compatibility", test_backward_compatibility),
        ]
        
        test_results = {}
        
        for test_name, test_func in tests:
            try:
                result = test_func(orchestrator)
                test_results[test_name] = result
            except Exception as e:
                print(f"❌ {test_name} test failed with exception: {e}")
                test_results[test_name] = False
        
        # Run scalability demo
        test_scalability_demo(orchestrator)
        
        # Generate comprehensive test summary
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST RESULTS SUMMARY")
        print("="*60)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, result in test_results.items():
            if isinstance(result, dict):
                # Handle dict results (like individual chatflow tests)
                for sub_test, sub_result in result.items():
                    total_tests += 1
                    if sub_result:
                        passed_tests += 1
                        print(f"✓ {test_name} - {sub_test}: PASSED")
                    else:
                        print(f"❌ {test_name} - {sub_test}: FAILED")
            elif isinstance(result, bool):
                total_tests += 1
                if result:
                    passed_tests += 1
                    print(f"✓ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
        
        print("\n" + "-"*60)
        print(f"TOTAL: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED!")
            print("✓ New dynamic features working correctly")
            print("✓ Backward compatibility maintained")
            print("✓ Error handling robust")
        else:
            print(f"⚠️  {total_tests - passed_tests} test(s) failed")
            print("Please check the individual test results above")
        
        print("\n" + "="*60)
        print("MIGRATION GUIDE:")
        print("- Legacy methods still work but show deprecation warnings")
        print("- New methods: send_to_chatflow(), send_to_multiple_chatflows(), orchestrate_sequential()")
        print("- Dynamic configuration: Set DIFY_CHATFLOW_COUNT and indexed variables")
        print("- Supports arbitrary numbers of chatflows")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        print("\nPlease check your .env file and ensure:")
        print("1. DIFY_CHATFLOW_COUNT is set")
        print("2. DIFY_CHATFLOW_N_API_KEY variables are set")
        print("3. DIFY_BASE_URL is set correctly")
        print("4. The Dify service is running and accessible")

if __name__ == "__main__":
    main()
