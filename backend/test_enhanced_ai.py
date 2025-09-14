#!/usr/bin/env python3
"""
Test script to demonstrate enhanced natural language processing and conversation context
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'item_service.settings')
django.setup()

from api.financial_ai_engine import FinancialAIEngine

def test_enhanced_ai():
    """Test the enhanced AI engine with natural language queries and context"""
    print("🤖 Testing Enhanced Financial AI Engine")
    print("=" * 50)
    
    ai_engine = FinancialAIEngine()
    user_id = "user_001"
    
    # Test queries that demonstrate natural language processing and context
    test_queries = [
        "How much did I spend last month?",
        "What about last 3 months?",
        "How much did I spend on food this month?",
        "What's my income last month?",
        "What about this month?",
        "Can I afford a vacation next month?",
        "What's my current balance?",
        "How about compared to last month?",
        "Show me my spending trends",
        "What about my income trends?"
    ]
    
    print(f"Testing with user: {user_id}")
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: {query}")
        print("-" * 30)
        
        try:
            result = ai_engine.process_query(query, user_id)
            
            print(f"Query Type: {result.get('query_type', 'unknown')}")
            print(f"Response: {result.get('response', 'No response')}")
            print(f"Recommendation: {result.get('recommendation', 'No recommendation')}")
            
            # Show context if available
            context = ai_engine._get_conversation_context(user_id)
            if context.get('last_query_type'):
                print(f"Context: Last query was about {context['last_query_type']} for {context.get('last_time_period', 'unknown period')}")
            
            print()
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            print()
    
    # Show final conversation context
    print("Final Conversation Context:")
    print("-" * 30)
    final_context = ai_engine._get_conversation_context(user_id)
    print(f"Last Query Type: {final_context.get('last_query_type', 'None')}")
    print(f"Last Time Period: {final_context.get('last_time_period', 'None')}")
    print(f"Last Category: {final_context.get('last_category', 'None')}")
    print(f"Last Amount: {final_context.get('last_amount', 'None')}")
    print(f"Conversation History: {len(final_context.get('conversation_history', []))} entries")

if __name__ == "__main__":
    test_enhanced_ai()
