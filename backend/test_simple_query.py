#!/usr/bin/env python3
"""
Test script to debug the AI engine with a simple query
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

def test_simple_query():
    """Test the AI engine with a simple query"""
    print("🤖 Testing Simple Query")
    print("=" * 30)
    
    ai_engine = FinancialAIEngine()
    user_id = "user_001"
    
    # Test the specific query that's causing issues
    query = "what about last month"
    print(f"Query: {query}")
    print("-" * 20)
    
    try:
        result = ai_engine.process_query(query, user_id)
        
        print(f"Query Type: {result.get('query_type', 'unknown')}")
        print(f"Response: {result.get('response', 'No response')}")
        print(f"Recommendation: {result.get('recommendation', 'No recommendation')}")
        
        # Show context
        context = ai_engine._get_conversation_context(user_id)
        print(f"Context: {context}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_query()
