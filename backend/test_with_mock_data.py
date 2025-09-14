#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced AI with mock data
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

def test_with_mock_data():
    """Test the AI engine with mock data to demonstrate full functionality"""
    print("🤖 Testing Enhanced AI with Mock Data")
    print("=" * 50)
    
    ai_engine = FinancialAIEngine()
    user_id = "user_001"
    
    # Mock some financial data for demonstration
    mock_data = {
        "user_id": user_id,
        "accounts": [
            {"name": "Savings Account", "balance": 150000, "type": "savings"},
            {"name": "Checking Account", "balance": 25000, "type": "checking"}
        ],
        "transactions": [
            {"type": "income", "amount": 80000, "category": "salary", "date": "2024-08-15T00:00:00Z"},
            {"type": "income", "amount": 80000, "category": "salary", "date": "2024-09-15T00:00:00Z"},
            {"type": "expense", "amount": 15000, "category": "food", "date": "2024-08-20T00:00:00Z"},
            {"type": "expense", "amount": 12000, "category": "transportation", "date": "2024-08-25T00:00:00Z"},
            {"type": "expense", "amount": 18000, "category": "food", "date": "2024-09-10T00:00:00Z"},
            {"type": "expense", "amount": 10000, "category": "transportation", "date": "2024-09-12T00:00:00Z"},
            {"type": "expense", "amount": 8000, "category": "entertainment", "date": "2024-09-05T00:00:00Z"}
        ]
    }
    
    # Temporarily override the load_financial_data method for testing
    original_load_data = ai_engine.load_financial_data
    ai_engine.load_financial_data = lambda user_id: mock_data
    
    # Test queries that demonstrate the enhanced functionality
    test_queries = [
        "How much did I spend last month?",
        "What about last 3 months?",
        "What's my income last month?",
        "What about this month?",
        "What's my current balance?",
        "How much did I spend on food this month?"
    ]
    
    print(f"Testing with user: {user_id}")
    print("Mock data includes:")
    print(f"- 2 accounts with total balance: ₹{sum(acc['balance'] for acc in mock_data['accounts']):,}")
    print(f"- {len(mock_data['transactions'])} transactions")
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
    
    # Restore original method
    ai_engine.load_financial_data = original_load_data
    
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
    test_with_mock_data()
