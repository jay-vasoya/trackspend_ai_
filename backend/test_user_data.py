#!/usr/bin/env python3
"""
Test script to check user data and AI responses
"""

import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'item_service.settings')
django.setup()

from api.models import User, Account, Transaction, Debt, Portfolio
from api.financial_ai_engine import FinancialAIEngine

def test_user_data():
    """Test what data exists for users"""
    
    print("🔍 Checking User Data")
    print("=" * 50)
    
    # Check all users
    users = User.objects.all()
    print(f"📊 Total users in database: {users.count()}")
    
    if users.count() == 0:
        print("❌ No users found! Please create a user first.")
        return
    
    # Check each user's data
    for user in users:
        print(f"\n👤 User: {user.username} (ID: {user.id})")
        print("-" * 30)
        
        # Check accounts
        accounts = Account.objects.filter(user_id=user.id)
        print(f"🏦 Accounts: {accounts.count()}")
        for account in accounts:
            print(f"   - {account.account_name}: ₹{account.total_balance:,.0f}")
        
        # Check transactions
        transactions = Transaction.objects.filter(user_id=user.id)
        print(f"💳 Transactions: {transactions.count()}")
        
        income_transactions = transactions.filter(type="income")
        expense_transactions = transactions.filter(type="expense")
        print(f"   - Income: {income_transactions.count()}")
        print(f"   - Expenses: {expense_transactions.count()}")
        
        # Show some sample transactions
        if transactions.count() > 0:
            print("   Sample transactions:")
            for t in transactions[:3]:
                print(f"     - {t.type}: ₹{t.amount:,.0f} ({t.category})")
        
        # Check debts
        debts = Debt.objects.filter(user_id=user.id)
        print(f"💸 Debts: {debts.count()}")
        
        # Check portfolio
        portfolio = Portfolio.objects.filter(user_id=user.id)
        print(f"📈 Portfolio: {portfolio.count()}")
        
        # Test AI engine
        print(f"\n🤖 Testing AI Engine for {user.username}")
        print("-" * 30)
        
        ai_engine = FinancialAIEngine()
        
        # Test data loading
        data = ai_engine.load_financial_data(str(user.id))
        if data:
            print("✅ Data loaded successfully")
            print(f"   - Total income: ₹{data['totals']['total_income']:,.0f}")
            print(f"   - Total expenses: ₹{data['totals']['total_expenses']:,.0f}")
            print(f"   - Total balance: ₹{data['totals']['total_balance']:,.0f}")
        else:
            print("❌ Failed to load data")
        
        # Test specific queries
        test_queries = [
            "What's my income last month?",
            "What's my current balance?",
            "How much did I spend this month?"
        ]
        
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            try:
                result = ai_engine.process_query(query, str(user.id))
                print(f"✅ Response: {result['response']}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_user_data()
