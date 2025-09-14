#!/usr/bin/env python3
"""
Debug script for AI Financial Assistant
Helps identify issues with the AI engine
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

def debug_ai_engine():
    """Debug the AI engine with real data"""
    
    print("🔍 Debugging AI Financial Assistant")
    print("=" * 50)
    
    # Check if we have any users
    users = User.objects.all()
    print(f"📊 Total users in database: {users.count()}")
    
    if users.count() == 0:
        print("❌ No users found in database!")
        print("Please create a user first.")
        return
    
    # Get the first user
    user = users.first()
    print(f"👤 Testing with user: {user.username} (ID: {user.id})")
    
    # Check accounts
    accounts = Account.objects.filter(user_id=user.id)
    print(f"🏦 Total accounts: {accounts.count()}")
    
    for account in accounts:
        print(f"   - {account.account_name}: ₹{account.total_balance:,.0f}")
    
    # Check transactions
    transactions = Transaction.objects.filter(user_id=user.id)
    print(f"💳 Total transactions: {transactions.count()}")
    
    income_transactions = transactions.filter(type="income")
    expense_transactions = transactions.filter(type="expense")
    print(f"   - Income transactions: {income_transactions.count()}")
    print(f"   - Expense transactions: {expense_transactions.count()}")
    
    # Check debts
    debts = Debt.objects.filter(user_id=user.id)
    print(f"💸 Total debts: {debts.count()}")
    
    for debt in debts:
        print(f"   - {debt.name}: ₹{debt.remaining_amount:,.0f} at {debt.interest_rate}%")
    
    # Check portfolio
    portfolio = Portfolio.objects.filter(user_id=user.id)
    print(f"📈 Total portfolio items: {portfolio.count()}")
    
    # Test AI engine
    print("\n🤖 Testing AI Engine")
    print("-" * 30)
    
    ai_engine = FinancialAIEngine()
    
    # Test data loading
    print("Loading financial data...")
    data = ai_engine.load_financial_data(str(user.id))
    
    if not data:
        print("❌ Failed to load financial data")
        return
    
    print("✅ Financial data loaded successfully")
    print(f"   - User: {data['profile']['name']}")
    print(f"   - Total income: ₹{data['totals']['total_income']:,.0f}")
    print(f"   - Total expenses: ₹{data['totals']['total_expenses']:,.0f}")
    print(f"   - Total balance: ₹{data['totals']['total_balance']:,.0f}")
    print(f"   - Total debt: ₹{data['totals']['total_debt']:,.0f}")
    print(f"   - Net worth: ₹{data['totals']['net_worth']:,.0f}")
    
    # Test queries
    test_queries = [
        "Can I afford to take a vacation next month?",
        "Why did my expenses increase last quarter?",
        "What's my best option for repaying my loan faster?"
    ]
    
    print("\n🧪 Testing AI Queries")
    print("-" * 30)
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        try:
            result = ai_engine.process_query(query, str(user.id))
            print(f"✅ Response: {result['response']}")
            print(f"💡 Recommendation: {result['recommendation']}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug_ai_engine()
