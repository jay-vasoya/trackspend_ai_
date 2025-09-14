#!/usr/bin/env python3
"""
Test script for new AI Financial Assistant query handlers
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'item_service.settings')
django.setup()

from api.financial_ai_engine import FinancialAIEngine

def test_new_queries():
    """Test the new query handlers"""
    
    print("🧪 Testing New AI Query Handlers")
    print("=" * 50)
    
    ai_engine = FinancialAIEngine()
    
    # Test queries for the new handlers
    test_queries = [
        "What's my current net worth?",
        "How much can I save this month?", 
        "Should I invest more or pay off debt first?",
        "How can I reduce my monthly expenses?",
        "What's my spending pattern this month?",
        "How much do I spend on entertainment?",
        "What's my investment portfolio worth?",
        "How are my budgets doing?"
    ]
    
    # Use a test user ID (you can change this to a real user ID)
    test_user_id = "user_001"
    
    print(f"Testing with user ID: {test_user_id}")
    print("-" * 30)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        try:
            result = ai_engine.process_query(query, test_user_id)
            
            print(f"✅ Query Type: {result['query_type']}")
            print(f"📝 Response: {result['response']}")
            print(f"💡 Recommendation: {result['recommendation']}")
            
            # Show some financial data if available
            if result.get('financial_data'):
                print(f"📊 Financial Data: {len(result['financial_data'])} fields")
                for key, value in result['financial_data'].items():
                    if isinstance(value, (int, float)) and value != 0:
                        print(f"   - {key}: {value}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("✅ Testing completed!")

if __name__ == "__main__":
    test_new_queries()
