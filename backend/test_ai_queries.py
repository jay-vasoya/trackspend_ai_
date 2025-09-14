#!/usr/bin/env python3
"""
Test script for AI Financial Assistant - Three Specific Query Types
Tests the exact queries mentioned in the requirements
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
USER_ID = "user_001"  # Change this to a real user ID from your database

def test_specific_queries():
    """Test the three specific query types mentioned in requirements"""
    
    # The three specific queries from the requirements
    test_queries = [
        "Can I afford to take a vacation next month?",
        "Why did my expenses increase last quarter?", 
        "What's my best option for repaying my loan faster?"
    ]
    
    print("🤖 AI Financial Assistant - Testing Specific Query Types")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"📝 Test {i}: {query}")
        print("-" * 50)
        
        try:
            response = requests.post(f"{BASE_URL}/ai/chat/", json={
                "query": query,
                "user_id": USER_ID
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response']}")
                print()
                print(f"💡 Recommendation: {data['recommendation']}")
                print()
                print(f"🏷️  Query Type: {data['query_type']}")
                
                # Show financial data if available
                if data.get('financial_data'):
                    print(f"📊 Financial Data:")
                    for key, value in data['financial_data'].items():
                        if isinstance(value, (int, float)):
                            print(f"   {key}: ₹{value:,.0f}")
                        else:
                            print(f"   {key}: {value}")
                
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("\n" + "="*60 + "\n")

def test_financial_summary():
    """Test the financial summary endpoint"""
    
    print("📊 Testing Financial Summary")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/ai/summary/?user_id={USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Financial summary retrieved:")
            print(f"   User: {data.get('profile', {}).get('name', 'Unknown')}")
            print(f"   Monthly Income: ₹{data.get('monthly_income', 0):,.0f}")
            print(f"   Monthly Expenses: ₹{data.get('monthly_expenses', 0):,.0f}")
            print(f"   Net Cash Flow: ₹{data.get('net_cash_flow', 0):,.0f}")
            print(f"   Net Worth: ₹{data.get('net_worth', 0):,.0f}")
            print(f"   Total Assets: ₹{data.get('total_assets', 0):,.0f}")
            print(f"   Total Liabilities: ₹{data.get('total_liabilities', 0):,.0f}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_additional_queries():
    """Test additional related queries"""
    
    additional_queries = [
        "Can I afford a new car worth ₹500000?",
        "How much do I spend on entertainment?",
        "What's my current net worth?",
        "Should I pay off my credit card debt first?"
    ]
    
    print("\n🔍 Testing Additional Related Queries")
    print("-" * 40)
    
    for i, query in enumerate(additional_queries, 1):
        print(f"\n📝 Additional Test {i}: {query}")
        print("-" * 30)
        
        try:
            response = requests.post(f"{BASE_URL}/ai/chat/", json={
                "query": query,
                "user_id": USER_ID
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response']}")
                print(f"💡 Recommendation: {data['recommendation']}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Starting AI Financial Assistant Tests")
    print("Testing the three specific query types from requirements:")
    print("1. 'Can I afford to take a vacation next month?'")
    print("2. 'Why did my expenses increase last quarter?'")
    print("3. 'What's my best option for repaying my loan faster?'")
    print()
    
    # Test financial summary first
    test_financial_summary()
    
    # Test the three specific queries
    test_specific_queries()
    
    # Test additional queries
    test_additional_queries()
    
    print("\n🎉 All tests completed!")
    print(f"⏰ Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
