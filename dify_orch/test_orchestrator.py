#!/usr/bin/env python3
"""
Test script for the Dify Orchestrator.
This script demonstrates how to use the orchestrator to send messages to two Dify chatflows.
"""

import logging
import json
from orchestrator import DifyOrchestrator

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_individual_chatflows(orchestrator: DifyOrchestrator):
    """Test sending messages to individual chatflows."""
    print("\n" + "="*50)
    print("Testing Individual Chatflows")
    print("="*50)
    
    test_message = "Hello, this is a test message for the chatflow."
    test_results = {"chatflow_1": False, "chatflow_2": False}
    
    # Test chatflow 1
    print("\n--- Testing Chatflow 1 ---")
    try:
        response_1 = orchestrator.send_to_chatflow_1(test_message)
        print(f"✓ Chatflow 1 Response: {json.dumps(response_1, indent=2, ensure_ascii=False)}")
        test_results["chatflow_1"] = True
    except Exception as e:
        print(f"❌ Error with Chatflow 1: {e}")
    
    # Test chatflow 2
    print("\n--- Testing Chatflow 2 ---")
    try:
        response_2 = orchestrator.send_to_chatflow_2(test_message)
        print(f"✓ Chatflow 2 Response: {json.dumps(response_2, indent=2, ensure_ascii=False)}")
        test_results["chatflow_2"] = True
    except Exception as e:
        print(f"❌ Error with Chatflow 2: {e}")
    
    return test_results

def test_dual_response(orchestrator: DifyOrchestrator):
    """Test sending the same message to both chatflows."""
    print("\n" + "="*50)
    print("Testing Dual Response")
    print("="*50)
    
    test_message = "Compare your capabilities with other AI systems."
    
    try:
        dual_response = orchestrator.orchestrate_dual_response(test_message)
        print(f"✓ Dual Response Result: {json.dumps(dual_response, indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"❌ Error in dual response: {e}")
        return False

def test_sequential_workflow(orchestrator: DifyOrchestrator):
    """Test sequential workflow where output of chatflow 1 feeds into chatflow 2."""
    print("\n" + "="*50)
    print("Testing Sequential Workflow")
    print("="*50)
    
    initial_query = "Generate a short creative story about a robot."
    
    try:
        sequential_result = orchestrator.sequential_workflow(initial_query)
        if sequential_result.get("status") == "success":
            print(f"✓ Sequential Workflow Result: {json.dumps(sequential_result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Sequential Workflow Failed: {json.dumps(sequential_result, indent=2, ensure_ascii=False)}")
            return False
    except Exception as e:
        print(f"❌ Error in sequential workflow: {e}")
        return False

def main():
    """Main test function."""
    setup_logging()
    
    print("Dify Orchestrator Test Script")
    print("="*50)
    
    try:
        # Initialize the orchestrator
        print("Initializing Dify Orchestrator...")
        orchestrator = DifyOrchestrator()
        print("✓ Orchestrator initialized successfully!")
        
        # Run tests and track results
        individual_results = test_individual_chatflows(orchestrator)
        dual_result = test_dual_response(orchestrator)
        sequential_result = test_sequential_workflow(orchestrator)
        
        # Generate test summary
        print("\n" + "="*50)
        print("TEST RESULTS SUMMARY")
        print("="*50)
        
        total_tests = 0
        passed_tests = 0
        
        # Individual chatflow tests
        for chatflow, success in individual_results.items():
            total_tests += 1
            if success:
                passed_tests += 1
                print(f"✓ {chatflow.replace('_', ' ').title()}: PASSED")
            else:
                print(f"❌ {chatflow.replace('_', ' ').title()}: FAILED")
        
        # Dual response test
        total_tests += 1
        if dual_result:
            passed_tests += 1
            print("✓ Dual Response: PASSED")
        else:
            print("❌ Dual Response: FAILED")
        
        # Sequential workflow test
        total_tests += 1
        if sequential_result:
            passed_tests += 1
            print("✓ Sequential Workflow: PASSED")
        else:
            print("❌ Sequential Workflow: FAILED")
        
        print("\n" + "-"*50)
        print(f"TOTAL: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {total_tests - passed_tests} test(s) failed")
            
        print("="*50)
        
    except Exception as e:
        print(f"❌ Failed to initialize orchestrator: {e}")
        print("\nPlease check your .env file and ensure:")
        print("1. DIFY_CHATFLOW_1_API_KEY is set")
        print("2. DIFY_CHATFLOW_2_API_KEY is set") 
        print("3. DIFY_BASE_URL is set correctly")
        print("4. The Dify service is running and accessible")

if __name__ == "__main__":
    main()
