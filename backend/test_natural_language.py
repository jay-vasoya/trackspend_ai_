#!/usr/bin/env python3
"""
Test script for Natural Language Interaction API
Tests context-aware conversations and intelligent financial queries
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
USER_ID = "user_001"  # Change this to a real user ID from your database

def test_natural_language_chat():
    """Test natural language chat with context awareness"""
    print("🗣️ Testing Natural Language Chat")
    print("-" * 40)
    
    try:
        # Test basic natural language query
        response = requests.post(f"{BASE_URL}/ai/natural-chat/", json={
            "query": "How much did I spend last month?",
            "user_id": USER_ID
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Natural Language Query processed:")
            print(f"   Query: {data['query']}")
            print(f"   Response: {data['response'][:100]}...")
            print(f"   Query Type: {data.get('query_type', 'Unknown')}")
            print(f"   Category: {data.get('category', 'Unknown')}")
            print(f"   Time Period: {data.get('time_period', 'Unknown')}")
            print(f"   Follow-up Intent: {data.get('follow_up_intent', 'Unknown')}")
            print(f"   Natural Language: {data.get('natural_language', False)}")
            print(f"   Context Aware: {data.get('context_aware', False)}")
            
            if data.get('suggested_actions'):
                print(f"   Suggested Actions: {len(data['suggested_actions'])}")
                for action in data['suggested_actions'][:3]:
                    print(f"     • {action}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_context_aware_conversation():
    """Test context-aware conversation flow"""
    print("\n🔄 Testing Context-Aware Conversation")
    print("-" * 45)
    
    conversation_flow = [
        "How much did I spend last month?",
        "What about the last 3 months?",
        "Show me spending by category",
        "How can I reduce expenses?"
    ]
    
    try:
        for i, query in enumerate(conversation_flow, 1):
            print(f"\n📝 Query {i}: {query}")
            print("-" * 30)
            
            response = requests.post(f"{BASE_URL}/ai/natural-chat/", json={
                "query": query,
                "user_id": USER_ID
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response'][:150]}...")
                print(f"   Follow-up Intent: {data.get('follow_up_intent', 'Unknown')}")
                print(f"   Context Maintained: {data.get('context_aware', False)}")
                
                if data.get('suggested_actions'):
                    print(f"   Next Actions: {data['suggested_actions'][0]}")
            else:
                print(f"❌ Error: {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_time_reference_parsing():
    """Test natural language time reference parsing"""
    print("\n⏰ Testing Time Reference Parsing")
    print("-" * 40)
    
    time_queries = [
        "How much did I spend today?",
        "What was my income yesterday?",
        "Show me expenses this week",
        "What about last month?",
        "Compare with last 3 months",
        "How much did I earn this year?",
        "What about 6 months ago?"
    ]
    
    try:
        for query in time_queries:
            response = requests.post(f"{BASE_URL}/ai/natural-chat/", json={
                "query": query,
                "user_id": USER_ID
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ '{query}' → Time Period: {data.get('time_period', 'Unknown')}")
            else:
                print(f"❌ '{query}' → Error: {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_intent_recognition():
    """Test intent recognition for different query types"""
    print("\n🎯 Testing Intent Recognition")
    print("-" * 35)
    
    intent_queries = {
        "spending_query": "How much did I spend on groceries?",
        "income_query": "What was my total income this month?",
        "balance_query": "What's my current account balance?",
        "budget_query": "How is my budget performing?",
        "goal_query": "How close am I to my savings goal?",
        "debt_query": "How much debt do I have remaining?",
        "investment_query": "How are my investments performing?",
        "analysis_query": "Analyze my spending patterns",
        "prediction_query": "Predict my future savings",
        "recommendation_query": "What should I do to improve my finances?"
    }
    
    try:
        for expected_intent, query in intent_queries.items():
            response = requests.post(f"{BASE_URL}/ai/natural-chat/", json={
                "query": query,
                "user_id": USER_ID
            })
            
            if response.status_code == 200:
                data = response.json()
                detected_intent = data.get('query_type', 'unknown')
                category = data.get('category', 'unknown')
                
                status = "✅" if detected_intent == expected_intent else "⚠️"
                print(f"{status} '{query[:30]}...' → Intent: {detected_intent}, Category: {category}")
            else:
                print(f"❌ '{query[:30]}...' → Error: {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_conversation_history():
    """Test conversation history retrieval"""
    print("\n📚 Testing Conversation History")
    print("-" * 35)
    
    try:
        # First, make a few queries to build history
        test_queries = [
            "How much did I spend last month?",
            "What about this month?",
            "Show me my budget progress"
        ]
        
        for query in test_queries:
            requests.post(f"{BASE_URL}/ai/natural-chat/", json={
                "query": query,
                "user_id": USER_ID
            })
        
        # Now get conversation history
        response = requests.get(f"{BASE_URL}/ai/conversation-history/?user_id={USER_ID}")
        
        if response.status_code == 200:
            data = response.json()
            history = data.get('conversation_history', [])
            print(f"✅ Conversation History Retrieved:")
            print(f"   Total Interactions: {data.get('total_interactions', 0)}")
            
            for i, interaction in enumerate(history[-3:], 1):  # Show last 3
                print(f"   {i}. User: {interaction.get('user_query', '')[:50]}...")
                print(f"      Assistant: {interaction.get('ai_response', '')[:50]}...")
                print(f"      Type: {interaction.get('query_type', 'Unknown')}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_context_suggestions():
    """Test context-aware suggestions"""
    print("\n💡 Testing Context-Aware Suggestions")
    print("-" * 40)
    
    try:
        # Test suggestions for different topics
        topics = ['spending', 'income', 'balance', 'budget', 'goal', 'debt']
        
        for topic in topics:
            response = requests.get(f"{BASE_URL}/ai/context-suggestions/?user_id={USER_ID}&topic={topic}")
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get('suggestions', [])
                print(f"✅ {topic.capitalize()} Suggestions ({len(suggestions)}):")
                for suggestion in suggestions[:3]:
                    print(f"   • {suggestion}")
            else:
                print(f"❌ {topic.capitalize()} Suggestions → Error: {response.status_code}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_clear_conversation():
    """Test conversation history clearing"""
    print("\n🗑️ Testing Conversation History Clearing")
    print("-" * 45)
    
    try:
        response = requests.post(f"{BASE_URL}/ai/clear-conversation/", json={
            "user_id": USER_ID
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conversation History Cleared:")
            print(f"   Cleared: {data.get('cleared', False)}")
            print(f"   Message: {data.get('message', '')}")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all natural language interaction tests"""
    print("🗣️ Natural Language Interaction API Tests")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Testing against: {BASE_URL}")
    print(f"👤 Using User ID: {USER_ID}")
    print()
    
    # Run all natural language tests
    test_natural_language_chat()
    test_context_aware_conversation()
    test_time_reference_parsing()
    test_intent_recognition()
    test_conversation_history()
    test_context_suggestions()
    test_clear_conversation()
    
    print("\n🎉 All natural language interaction tests completed!")
    print(f"⏰ Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Natural Language Features Tested:")
    print("   ✅ Context-Aware Conversations")
    print("   ✅ Time Reference Parsing")
    print("   ✅ Intent Recognition")
    print("   ✅ Follow-up Query Understanding")
    print("   ✅ Conversation History Management")
    print("   ✅ Context-Aware Suggestions")
    print("   ✅ Conversation Clearing")
    print("\n🚀 Next steps:")
    print("   1. Test the enhanced Live Chat interface")
    print("   2. Try natural language queries like 'How much did I spend last month?'")
    print("   3. Test follow-up questions like 'What about the last 3 months?'")
    print("   4. Verify context awareness and suggestions")

if __name__ == "__main__":
    main()
