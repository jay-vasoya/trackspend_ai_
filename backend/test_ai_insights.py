#!/usr/bin/env python3
"""
Test script for AI-powered insights functionality
Tests the new prediction, anomaly detection, debt optimization, and insights features
"""

import os
import sys
import django
import requests
import json

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'item_service.settings')
django.setup()

# Test configuration
API_BASE = "http://localhost:8000/api"
USER_ID = "user_001"  # Change this to test with different users

def test_ai_insights():
    """Test all AI-powered insights features"""
    
    print("🧠 Testing AI-Powered Insights Features")
    print("=" * 50)
    
    # Test queries for each insight type
    test_queries = [
        {
            "name": "Future Savings Prediction",
            "query": "Predict my future savings for the next 2 years",
            "expected_type": "prediction"
        },
        {
            "name": "Anomaly Detection",
            "query": "Detect unusual spending patterns in my transactions",
            "expected_type": "anomaly_detection"
        },
        {
            "name": "Debt Optimization",
            "query": "How can I optimize my debt repayment strategy?",
            "expected_type": "debt_optimization"
        },
        {
            "name": "Financial Insights",
            "query": "Give me comprehensive financial insights and recommendations",
            "expected_type": "insights"
        },
        {
            "name": "General Prediction",
            "query": "What will my financial situation look like in 6 months?",
            "expected_type": "prediction"
        },
        {
            "name": "Spending Anomalies",
            "query": "Are there any strange or abnormal expenses in my data?",
            "expected_type": "anomaly_detection"
        },
        {
            "name": "Smart Debt Advice",
            "query": "What's the smartest way to pay off my loans?",
            "expected_type": "debt_optimization"
        },
        {
            "name": "Financial Analysis",
            "query": "Analyze my financial health and provide recommendations",
            "expected_type": "insights"
        }
    ]
    
    results = []
    
    for test in test_queries:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"Query: '{test['query']}'")
        
        try:
            # Make API request
            response = requests.post(
                f"{API_BASE}/ai/chat/",
                json={
                    "query": test["query"],
                    "user_id": USER_ID
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                query_type = data.get("query_type", "unknown")
                response_text = data.get("response", "")
                recommendation = data.get("recommendation", "")
                
                print(f"✅ Status: Success")
                print(f"📊 Query Type: {query_type}")
                print(f"💬 Response: {response_text[:100]}...")
                print(f"💡 Recommendation: {recommendation[:100]}...")
                
                # Check if we got the expected query type
                if query_type == test["expected_type"]:
                    print(f"✅ Query type matches expected: {test['expected_type']}")
                else:
                    print(f"⚠️ Query type mismatch. Expected: {test['expected_type']}, Got: {query_type}")
                
                results.append({
                    "test": test["name"],
                    "status": "success",
                    "query_type": query_type,
                    "expected_type": test["expected_type"],
                    "response_length": len(response_text)
                })
                
            else:
                print(f"❌ Status: Failed ({response.status_code})")
                print(f"Error: {response.text}")
                results.append({
                    "test": test["name"],
                    "status": "failed",
                    "error": response.text
                })
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results.append({
                "test": test["name"],
                "status": "error",
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    successful_tests = [r for r in results if r["status"] == "success"]
    failed_tests = [r for r in results if r["status"] != "success"]
    
    print(f"✅ Successful: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        print(f"\n🎯 Query Type Distribution:")
        type_counts = {}
        for result in successful_tests:
            query_type = result["query_type"]
            type_counts[query_type] = type_counts.get(query_type, 0) + 1
        
        for query_type, count in type_counts.items():
            print(f"  • {query_type}: {count} tests")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for result in failed_tests:
            print(f"  • {result['test']}: {result.get('error', 'Unknown error')}")
    
    print(f"\n🚀 AI-Powered Insights Testing Complete!")
    return results

def test_edge_cases():
    """Test edge cases for AI insights"""
    
    print("\n🧪 Testing Edge Cases")
    print("=" * 30)
    
    edge_cases = [
        {
            "name": "No Data User",
            "query": "Predict my future savings",
            "user_id": "user_no_data"
        },
        {
            "name": "Minimal Data",
            "query": "Detect unusual spending",
            "user_id": "user_minimal"
        },
        {
            "name": "No Debt User",
            "query": "How can I optimize my debt?",
            "user_id": "user_no_debt"
        }
    ]
    
    for case in edge_cases:
        print(f"\n🔍 Testing: {case['name']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/ai/chat/",
                json={
                    "query": case["query"],
                    "user_id": case["user_id"]
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                print(f"✅ Response: {response_text[:150]}...")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting AI-Powered Insights Testing")
    print("Make sure your Django server is running on localhost:8000")
    print("=" * 60)
    
    # Test main functionality
    results = test_ai_insights()
    
    # Test edge cases
    test_edge_cases()
    
    print("\n🎉 All tests completed!")
    print("Check the results above to verify AI-powered insights are working correctly.")
