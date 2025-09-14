"""
Financial AI Engine for Natural Language Conversations
Handles the three specific query types mentioned in the requirements
Uses real database data instead of JSON files
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
from .models import User, Account, Transaction, Budget, Goal, Portfolio, Debt, UserPermission

class FinancialAIEngine:
    def __init__(self):
        # Conversation context storage
        self.conversation_context = {}
    
    def _get_conversation_context(self, user_id: str) -> Dict[str, Any]:
        """Get conversation context for a user"""
        return self.conversation_context.get(user_id, {
            'last_query_type': None,
            'last_time_period': None,
            'last_category': None,
            'last_amount': None,
            'conversation_history': []
        })
    
    def _update_conversation_context(self, user_id: str, query_type: str, time_period: str = None, category: str = None, amount: float = None):
        """Update conversation context for a user"""
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = {
                'last_query_type': None,
                'last_time_period': None,
                'last_category': None,
                'last_amount': None,
                'conversation_history': []
            }
        
        self.conversation_context[user_id]['last_query_type'] = query_type
        self.conversation_context[user_id]['last_time_period'] = time_period
        self.conversation_context[user_id]['last_category'] = category
        self.conversation_context[user_id]['last_amount'] = amount
        self.conversation_context[user_id]['conversation_history'].append({
            'query_type': query_type,
            'time_period': time_period,
            'category': category,
            'amount': amount,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 conversation entries
        if len(self.conversation_context[user_id]['conversation_history']) > 10:
            self.conversation_context[user_id]['conversation_history'] = self.conversation_context[user_id]['conversation_history'][-10:]
    
    def _parse_time_period(self, query: str) -> Dict[str, Any]:
        """Parse time period from natural language query"""
        query_lower = query.lower()
        
        # Time period patterns
        time_patterns = {
            'today': {'days': 0, 'label': 'today'},
            'yesterday': {'days': 1, 'label': 'yesterday'},
            'this week': {'days': 7, 'label': 'this week'},
            'last week': {'days': 14, 'label': 'last week'},
            'this month': {'days': 30, 'label': 'this month'},
            'last month': {'days': 60, 'label': 'last month'},
            'this quarter': {'days': 90, 'label': 'this quarter'},
            'last quarter': {'days': 180, 'label': 'last quarter'},
            'this year': {'days': 365, 'label': 'this year'},
            'last year': {'days': 730, 'label': 'last year'},
            'last 3 months': {'days': 90, 'label': 'last 3 months'},
            'last 6 months': {'days': 180, 'label': 'last 6 months'},
            'last 12 months': {'days': 365, 'label': 'last 12 months'},
        }
        
        # Check for specific patterns
        for pattern, config in time_patterns.items():
            if pattern in query_lower:
                return config
        
        # Check for "last X months/days/weeks" patterns
        import re
        last_pattern = r'last (\d+) (months?|days?|weeks?)'
        match = re.search(last_pattern, query_lower)
        if match:
            number = int(match.group(1))
            unit = match.group(2)
            
            if unit.startswith('month'):
                days = number * 30
                label = f'last {number} month{"s" if number > 1 else ""}'
            elif unit.startswith('week'):
                days = number * 7
                label = f'last {number} week{"s" if number > 1 else ""}'
            else:  # days
                days = number
                label = f'last {number} day{"s" if number > 1 else ""}'
            
            return {'days': days, 'label': label}
        
        # Default to this month if no specific period mentioned
        return {'days': 30, 'label': 'this month'}
    
    def _parse_category_from_query(self, query: str) -> Optional[str]:
        """Parse spending category from natural language query"""
        query_lower = query.lower()
        
        category_mapping = {
            'food': ['food', 'restaurant', 'dining', 'groceries', 'eating'],
            'transportation': ['transport', 'gas', 'fuel', 'uber', 'taxi', 'bus', 'train'],
            'entertainment': ['entertainment', 'movie', 'game', 'fun', 'leisure'],
            'shopping': ['shopping', 'clothes', 'clothing', 'retail', 'store'],
            'utilities': ['utility', 'electricity', 'water', 'internet', 'phone'],
            'healthcare': ['health', 'medical', 'doctor', 'hospital', 'medicine'],
            'education': ['education', 'school', 'course', 'book', 'learning'],
            'travel': ['travel', 'vacation', 'hotel', 'flight', 'trip'],
            'housing': ['rent', 'mortgage', 'housing', 'home', 'apartment'],
        }
        
        for category, keywords in category_mapping.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return None
    
    def _extract_amount_from_query(self, query: str) -> Optional[float]:
        """Extract monetary amount from query"""
        import re
        
        # Look for currency amounts
        amount_patterns = [
            r'₹(\d+(?:,\d{3})*(?:\.\d{2})?)',  # ₹1,000.00
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:rupees?|rs)',  # 1000 rupees
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:thousand|k)',  # 1 thousand, 1k
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:lakh|l)',  # 1 lakh, 1l
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:crore|c)',  # 1 crore, 1c
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, query.lower())
            if match:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                
                # Handle multipliers
                if 'thousand' in query.lower() or 'k' in query.lower():
                    amount *= 1000
                elif 'lakh' in query.lower() or 'l' in query.lower():
                    amount *= 100000
                elif 'crore' in query.lower() or 'c' in query.lower():
                    amount *= 10000000
                
                return amount
        
        return None
    
    def _is_follow_up_query(self, query_lower: str, context: Dict[str, Any]) -> bool:
        """Check if query is a follow-up to previous conversation"""
        follow_up_indicators = [
            'what about', 'how about', 'and', 'also', 'then', 'next',
            'last 3 months', 'last 6 months', 'last year', 'this year',
            'compared to', 'vs', 'versus', 'difference', 'change',
            'more', 'less', 'higher', 'lower', 'increase', 'decrease'
        ]
        
        # Check if query contains follow-up indicators
        has_follow_up_indicators = any(indicator in query_lower for indicator in follow_up_indicators)
        
        # Check if we have previous context
        has_context = context.get('last_query_type') is not None
        
        # Also check if query is asking about a specific time period without context
        # This handles cases like "what about last month" when there's no previous context
        time_period_queries = [
            'what about last month', 'what about this month', 'what about last year',
            'what about last 3 months', 'what about last 6 months', 'what about this year'
        ]
        
        is_time_period_query = any(time_query in query_lower for time_query in time_period_queries)
        
        return (has_follow_up_indicators and has_context) or is_time_period_query
    
    def _handle_follow_up_query(self, query: str, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle follow-up queries using conversation context"""
        query_lower = query.lower()
        last_query_type = context.get('last_query_type')
        last_time_period = context.get('last_time_period')
        
        # Parse new time period from follow-up query
        new_time_period = self._parse_time_period(query)
        
        # Handle cases where there's no previous context but query is asking about a time period
        if not last_query_type and 'what about' in query_lower:
            # Default to spending query when no context is available
            return self._handle_spending_query(query, user_id)
        
        # Handle different types of follow-up queries
        if 'what about' in query_lower or 'how about' in query_lower:
            # Compare with different time period
            if last_query_type == 'spending':
                return self._handle_spending_comparison(query, user_id, last_time_period, new_time_period['label'])
            elif last_query_type == 'income':
                return self._handle_income_comparison(query, user_id, last_time_period, new_time_period['label'])
            elif last_query_type == 'balance':
                return self._handle_balance_comparison(query, user_id, last_time_period, new_time_period['label'])
        
        elif 'compared to' in query_lower or 'vs' in query_lower or 'versus' in query_lower:
            # Direct comparison request
            if last_query_type == 'spending':
                return self._handle_spending_comparison(query, user_id, last_time_period, new_time_period['label'])
            elif last_query_type == 'income':
                return self._handle_income_comparison(query, user_id, last_time_period, new_time_period['label'])
        
        elif any(word in query_lower for word in ['more', 'less', 'higher', 'lower', 'increase', 'decrease']):
            # Trend analysis
            if last_query_type == 'spending':
                return self._handle_spending_trend(query, user_id, last_time_period, new_time_period['label'])
            elif last_query_type == 'income':
                return self._handle_income_trend(query, user_id, last_time_period, new_time_period['label'])
        
        # Default: treat as new query with context
        return self._handle_contextual_query(query, user_id, context)
    
    def _handle_spending_comparison(self, query: str, user_id: str, period1: str, period2: str) -> Dict[str, Any]:
        """Handle spending comparison between two time periods"""
        data = self.load_financial_data(user_id)
        
        if not data or not data.get('transactions'):
            return {
                "query_type": "spending_comparison",
                "response": "I don't have access to your transaction data to compare spending periods.",
                "recommendation": "Please grant transaction permissions to get spending comparisons.",
                "financial_data": {}
            }
        
        # Calculate spending for both periods
        spending1 = self._calculate_spending_for_period(data['transactions'], period1)
        spending2 = self._calculate_spending_for_period(data['transactions'], period2)
        
        difference = spending2 - spending1
        percentage_change = (difference / spending1 * 100) if spending1 > 0 else 0
        
        if difference > 0:
            response = f"Your spending in {period2} was ₹{spending2:,.0f}, which is ₹{difference:,.0f} more than {period1} (₹{spending1:,.0f}). That's a {percentage_change:.1f}% increase."
            recommendation = "Consider reviewing your recent expenses to identify areas where spending increased."
        else:
            response = f"Your spending in {period2} was ₹{spending2:,.0f}, which is ₹{abs(difference):,.0f} less than {period1} (₹{spending1:,.0f}). That's a {abs(percentage_change):.1f}% decrease."
            recommendation = "Great job on reducing your spending! Keep up the good financial habits."
        
        # Update context
        self._update_conversation_context(user_id, 'spending_comparison', period2)
        
        return {
            "query_type": "spending_comparison",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "period1_spending": spending1,
                "period2_spending": spending2,
                "difference": difference,
                "percentage_change": percentage_change
            }
        }
    
    def _handle_income_comparison(self, query: str, user_id: str, period1: str, period2: str) -> Dict[str, Any]:
        """Handle income comparison between two time periods"""
        data = self.load_financial_data(user_id)
        
        if not data or not data.get('transactions'):
            return {
                "query_type": "income_comparison",
                "response": "I don't have access to your transaction data to compare income periods.",
                "recommendation": "Please grant transaction permissions to get income comparisons.",
                "financial_data": {}
            }
        
        # Calculate income for both periods
        income1 = self._calculate_income_for_period(data['transactions'], period1)
        income2 = self._calculate_income_for_period(data['transactions'], period2)
        
        difference = income2 - income1
        percentage_change = (difference / income1 * 100) if income1 > 0 else 0
        
        if difference > 0:
            response = f"Your income in {period2} was ₹{income2:,.0f}, which is ₹{difference:,.0f} more than {period1} (₹{income1:,.0f}). That's a {percentage_change:.1f}% increase."
            recommendation = "Great job on increasing your income! Consider investing the extra amount for long-term growth."
        else:
            response = f"Your income in {period2} was ₹{income2:,.0f}, which is ₹{abs(difference):,.0f} less than {period1} (₹{income1:,.0f}). That's a {abs(percentage_change):.1f}% decrease."
            recommendation = "Consider reviewing your income sources and look for opportunities to increase earnings."
        
        # Update context
        self._update_conversation_context(user_id, 'income_comparison', period2)
        
        return {
            "query_type": "income_comparison",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "period1_income": income1,
                "period2_income": income2,
                "difference": difference,
                "percentage_change": percentage_change
            }
        }
    
    def _handle_balance_comparison(self, query: str, user_id: str, period1: str, period2: str) -> Dict[str, Any]:
        """Handle balance comparison between two time periods"""
        data = self.load_financial_data(user_id)
        
        if not data or not data.get('accounts'):
            return {
                "query_type": "balance_comparison",
                "response": "I don't have access to your account data to compare balances.",
                "recommendation": "Please grant account permissions to get balance comparisons.",
                "financial_data": {}
            }
        
        # For balance comparison, we'll use current balance vs previous balance
        # This is a simplified version - in a real system, you'd track historical balances
        current_balance = sum(account.get('balance', 0) for account in data['accounts'])
        
        # Estimate previous balance based on transactions
        if data.get('transactions'):
            net_change = self._calculate_net_change_for_period(data['transactions'], period1)
            estimated_previous_balance = current_balance - net_change
        else:
            estimated_previous_balance = current_balance * 0.9  # Rough estimate
        
        difference = current_balance - estimated_previous_balance
        percentage_change = (difference / estimated_previous_balance * 100) if estimated_previous_balance > 0 else 0
        
        if difference > 0:
            response = f"Your current balance is ₹{current_balance:,.0f}, which is ₹{difference:,.0f} higher than estimated {period1} balance (₹{estimated_previous_balance:,.0f}). That's a {percentage_change:.1f}% increase."
            recommendation = "Great job on growing your savings! Consider investing some of the growth for better returns."
        else:
            response = f"Your current balance is ₹{current_balance:,.0f}, which is ₹{abs(difference):,.0f} lower than estimated {period1} balance (₹{estimated_previous_balance:,.0f}). That's a {abs(percentage_change):.1f}% decrease."
            recommendation = "Review your spending patterns to understand why your balance decreased."
        
        # Update context
        self._update_conversation_context(user_id, 'balance_comparison', period2)
        
        return {
            "query_type": "balance_comparison",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "current_balance": current_balance,
                "previous_balance": estimated_previous_balance,
                "difference": difference,
                "percentage_change": percentage_change
            }
        }
    
    def _handle_spending_trend(self, query: str, user_id: str, period1: str, period2: str) -> Dict[str, Any]:
        """Handle spending trend analysis"""
        data = self.load_financial_data(user_id)
        
        if not data or not data.get('transactions'):
            return {
                "query_type": "spending_trend",
                "response": "I don't have access to your transaction data to analyze spending trends.",
                "recommendation": "Please grant transaction permissions to get spending trend analysis.",
                "financial_data": {}
            }
        
        spending1 = self._calculate_spending_for_period(data['transactions'], period1)
        spending2 = self._calculate_spending_for_period(data['transactions'], period2)
        
        difference = spending2 - spending1
        percentage_change = (difference / spending1 * 100) if spending1 > 0 else 0
        
        if difference > 0:
            response = f"Your spending has increased by ₹{difference:,.0f} ({percentage_change:.1f}%) from {period1} to {period2}. This trend shows rising expenses."
            recommendation = "Consider creating a budget to control spending increases and identify areas for cost reduction."
        else:
            response = f"Your spending has decreased by ₹{abs(difference):,.0f} ({abs(percentage_change):.1f}%) from {period1} to {period2}. This trend shows improving financial discipline."
            recommendation = "Excellent work on reducing expenses! Consider investing the savings for long-term growth."
        
        # Update context
        self._update_conversation_context(user_id, 'spending_trend', period2)
        
        return {
            "query_type": "spending_trend",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "period1_spending": spending1,
                "period2_spending": spending2,
                "difference": difference,
                "percentage_change": percentage_change,
                "trend": "increasing" if difference > 0 else "decreasing"
            }
        }
    
    def _handle_income_trend(self, query: str, user_id: str, period1: str, period2: str) -> Dict[str, Any]:
        """Handle income trend analysis"""
        data = self.load_financial_data(user_id)
        
        if not data or not data.get('transactions'):
            return {
                "query_type": "income_trend",
                "response": "I don't have access to your transaction data to analyze income trends.",
                "recommendation": "Please grant transaction permissions to get income trend analysis.",
                "financial_data": {}
            }
        
        income1 = self._calculate_income_for_period(data['transactions'], period1)
        income2 = self._calculate_income_for_period(data['transactions'], period2)
        
        difference = income2 - income1
        percentage_change = (difference / income1 * 100) if income1 > 0 else 0
        
        if difference > 0:
            response = f"Your income has increased by ₹{difference:,.0f} ({percentage_change:.1f}%) from {period1} to {period2}. This trend shows growing earning potential."
            recommendation = "Great job on increasing your income! Consider investing the extra amount and building an emergency fund."
        else:
            response = f"Your income has decreased by ₹{abs(difference):,.0f} ({abs(percentage_change):.1f}%) from {period1} to {period2}. This trend shows declining earnings."
            recommendation = "Review your income sources and consider ways to increase earnings through side hustles or skill development."
        
        # Update context
        self._update_conversation_context(user_id, 'income_trend', period2)
        
        return {
            "query_type": "income_trend",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "period1_income": income1,
                "period2_income": income2,
                "difference": difference,
                "percentage_change": percentage_change,
                "trend": "increasing" if difference > 0 else "decreasing"
            }
        }
    
    def _handle_contextual_query(self, query: str, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle queries that use previous context but aren't direct follow-ups"""
        # Use the last query type as context for the new query
        last_query_type = context.get('last_query_type')
        
        if last_query_type == 'spending':
            return self._handle_spending_query(query, user_id)
        elif last_query_type == 'income':
            return self._handle_income_query(query, user_id)
        elif last_query_type == 'balance':
            return self._handle_balance_query(query, user_id)
        else:
            # Fall back to general query handling
            return self._handle_general_query(query, user_id)
    
    def _calculate_spending_for_period(self, transactions: List[Dict], period: str) -> float:
        """Calculate total spending for a given time period"""
        if not transactions:
            return 0.0
        
        # Calculate date range based on period
        end_date = datetime.now(timezone.utc)
        if period == 'last month':
            start_date = end_date - timedelta(days=60)
        elif period == 'last 3 months':
            start_date = end_date - timedelta(days=90)
        elif period == 'last 6 months':
            start_date = end_date - timedelta(days=180)
        elif period == 'last year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default to last month
        
        total_spending = 0.0
        for transaction in transactions:
            if transaction.get('type') == 'expense':
                transaction_date = datetime.fromisoformat(transaction.get('date', '').replace('Z', '+00:00'))
                if start_date <= transaction_date <= end_date:
                    total_spending += transaction.get('amount', 0)
        
        return total_spending
    
    def _calculate_income_for_period(self, transactions: List[Dict], period: str) -> float:
        """Calculate total income for a given time period"""
        if not transactions:
            return 0.0
        
        # Calculate date range based on period
        end_date = datetime.now(timezone.utc)
        if period == 'last month':
            start_date = end_date - timedelta(days=60)
        elif period == 'last 3 months':
            start_date = end_date - timedelta(days=90)
        elif period == 'last 6 months':
            start_date = end_date - timedelta(days=180)
        elif period == 'last year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default to last month
        
        total_income = 0.0
        for transaction in transactions:
            if transaction.get('type') == 'income':
                transaction_date = datetime.fromisoformat(transaction.get('date', '').replace('Z', '+00:00'))
                if start_date <= transaction_date <= end_date:
                    total_income += transaction.get('amount', 0)
        
        return total_income
    
    def _calculate_net_change_for_period(self, transactions: List[Dict], period: str) -> float:
        """Calculate net change (income - expenses) for a given time period"""
        income = self._calculate_income_for_period(transactions, period)
        expenses = self._calculate_spending_for_period(transactions, period)
        return income - expenses
    
    def get_user_permissions(self, user_id: str) -> Dict[str, bool]:
        """Get user permissions for data access"""
        try:
            permission = UserPermission.objects.get(user_id=user_id)
            return permission.get_permissions_dict()
        except UserPermission.DoesNotExist:
            # No permissions set, return all False (most restrictive)
            return {
                'accounts': False,
                'transactions': False,
                'budgets': False,
                'goals': False,
                'investments': False,
                'debts': False
            }
    
    def has_any_permissions(self, user_id: str) -> bool:
        """Check if user has granted any permissions"""
        permissions = self.get_user_permissions(user_id)
        return any(permissions.values())
    
    def get_permission_status_message(self, user_id: str) -> str:
        """Get a message about current permission status"""
        permissions = self.get_user_permissions(user_id)
        granted_permissions = [k for k, v in permissions.items() if v]
        
        if not granted_permissions:
            return "I don't have permission to access any of your financial data. Please grant permissions to get personalized insights."
        else:
            return f"I have access to: {', '.join(granted_permissions)}. Grant more permissions for comprehensive insights."
        
    def load_financial_data(self, user_id: str) -> Dict[str, Any]:
        """Load complete financial data from database respecting user permissions"""
        try:
            # Get user permissions first
            permissions = self.get_user_permissions(user_id)
            
            # Get user
            user = User.objects.get(id=user_id)
            
            # Get user's accounts (only if permission granted)
            accounts = []
            if permissions.get('accounts', False):
                accounts = Account.objects.filter(user_id=user_id)
            
            # Get transactions (only if permission granted)
            transactions = []
            if permissions.get('transactions', False):
                transactions = Transaction.objects.filter(user_id=user_id)
            
            # Get budgets (only if permission granted)
            budgets = []
            if permissions.get('budgets', False):
                budgets = Budget.objects.filter(user_id=user_id)
            
            # Get goals (only if permission granted)
            goals = []
            if permissions.get('goals', False):
                goals = Goal.objects.filter(user_id=user_id)
            
            # Get portfolio (only if permission granted)
            portfolio = []
            if permissions.get('investments', False):
                portfolio = Portfolio.objects.filter(user_id=user_id)
            
            # Get debts (only if permission granted)
            debts = []
            if permissions.get('debts', False):
                debts = Debt.objects.filter(user_id=user_id)
            
            # Calculate totals from accounts
            total_income = sum(account.total_income for account in accounts)
            total_expenses = sum(account.total_expenses for account in accounts)
            total_balance = sum(account.total_balance for account in accounts)
            
            # Calculate total debt
            total_debt = sum(debt.remaining_amount for debt in debts)
            
            # Calculate total investments
            total_investments = sum(item.totalValue for item in portfolio if hasattr(item, 'totalValue'))
            
            # Calculate monthly income and expenses from transactions
            current_month = datetime.now().replace(day=1)
            monthly_transactions = transactions.filter(date__gte=current_month)
            
            monthly_income_from_transactions = sum(
                t.amount for t in monthly_transactions if t.type == "income"
            )
            monthly_expenses_from_transactions = sum(
                t.amount for t in monthly_transactions if t.type == "expense"
            )
            
            return {
                "user_id": str(user_id),
                "profile": {
                    "name": user.username,
                    "email": user.email
                },
                "accounts": [
                    {
                        "id": str(account.id),
                        "name": account.account_name,
                        "type": account.account_type,
                        "balance": account.total_balance,
                        "income": account.total_income,
                        "expenses": account.total_expenses
                    } for account in accounts
                ],
                "transactions": [
                    {
                        "id": str(transaction.id),
                        "type": transaction.type,
                        "amount": transaction.amount,
                        "category": transaction.category,
                        "date": transaction.date.isoformat() if transaction.date else None,
                        "description": transaction.description
                    } for transaction in transactions
                ],
                "budgets": [
                    {
                        "id": str(budget.id),
                        "name": budget.name,
                        "limit": budget.limit,
                        "spent": budget.spent,
                        "remaining": budget.remaining,
                        "type": budget.type
                    } for budget in budgets
                ],
                "goals": [
                    {
                        "id": str(goal.id),
                        "title": goal.title,
                        "target_amount": goal.target_amount,
                        "current_amount": goal.current_amount,
                        "target_date": goal.target_date.isoformat() if goal.target_date else None,
                        "category": goal.category,
                        "priority": goal.priority,
                        "status": goal.status
                    } for goal in goals
                ],
                "portfolio": [
                    {
                        "id": str(item.id),
                        "name": item.name or item.asset_name or "Unknown",
                        "symbol": item.symbol or "N/A",
                        "type": item.type or item.asset_type or "Unknown",
                        "quantity": item.quantity or 0,
                        "buy_price": item.buyPrice or item.purchase_price or 0,
                        "current_price": item.currentPrice or 0,
                        "total_value": item.totalValue if hasattr(item, 'totalValue') else 0,
                        "gain_loss": item.gainLoss if hasattr(item, 'gainLoss') else 0,
                        "gain_loss_percent": item.gainLossPercent if hasattr(item, 'gainLossPercent') else 0
                    } for item in portfolio
                ],
                "debts": [
                    {
                        "id": str(debt.id),
                        "name": debt.name,
                        "type": debt.type,
                        "total_amount": debt.total_amount,
                        "remaining_amount": debt.remaining_amount,
                        "interest_rate": debt.interest_rate,
                        "minimum_payment": debt.minimum_payment,
                        "due_date": debt.due_date.isoformat() if debt.due_date else None
                    } for debt in debts
                ],
                "totals": {
                    "total_income": total_income,
                    "total_expenses": total_expenses,
                    "total_balance": total_balance,
                    "total_debt": total_debt,
                    "total_investments": total_investments,
                    "net_worth": total_balance + total_investments - total_debt,
                    "monthly_income_from_transactions": monthly_income_from_transactions,
                    "monthly_expenses_from_transactions": monthly_expenses_from_transactions
                }
            }
        except User.DoesNotExist:
            print(f"User with ID {user_id} does not exist")
            return {"error": "User not found", "permissions": self.get_user_permissions(user_id)}
        except Exception as e:
            print(f"Error loading financial data for user {user_id}: {e}")
            import traceback
            traceback.print_exc()
            return {"error": "Failed to load data", "permissions": self.get_user_permissions(user_id)}
    
    def process_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Process natural language financial queries with context awareness"""
        query_lower = query.lower()
        context = self._get_conversation_context(user_id)
        
        # Check for follow-up queries that reference previous context
        if self._is_follow_up_query(query_lower, context):
            return self._handle_follow_up_query(query, user_id, context)
        
        # Parse time period and category from query
        time_period = self._parse_time_period(query)
        category = self._parse_category_from_query(query)
        amount = self._extract_amount_from_query(query)
        
        # Determine query type and process accordingly - ORDER MATTERS!
        # More specific patterns first, then general ones
        
        # Income queries (very specific)
        if any(phrase in query_lower for phrase in ["what's my income", "my income", "income last month", "income this month", "how much do i earn", "my salary"]):
            return self._handle_income_query(query, user_id)
        
        # Balance queries (very specific)
        elif any(phrase in query_lower for phrase in ["what's my balance", "my balance", "current balance", "account balance", "how much money do i have"]):
            return self._handle_balance_query(query, user_id)
        
        # Spending queries (very specific)
        elif any(phrase in query_lower for phrase in ["how much did i spend", "my spending", "spending this month", "spending last month", "what did i spend"]):
            return self._handle_spending_query(query, user_id)
        
        # Net worth queries (very specific)
        elif any(phrase in query_lower for phrase in ["what's my net worth", "my net worth", "total assets", "my worth"]):
            return self._handle_net_worth_query(query, user_id)
        
        # Savings queries (very specific)
        elif any(phrase in query_lower for phrase in ["how much can i save", "my savings", "saving this month", "savings potential"]):
            return self._handle_savings_query(query, user_id)
        
        # Investment queries (very specific)
        elif any(phrase in query_lower for phrase in ["my investments", "investment portfolio", "should i invest", "invest more"]):
            return self._handle_investment_query(query, user_id)
        
        # Budget queries (very specific)
        elif any(phrase in query_lower for phrase in ["my budget", "budget status", "how are my budgets"]):
            return self._handle_budget_query(query, user_id)
        
        # Affordability queries (specific patterns)
        elif any(phrase in query_lower for phrase in ["can i afford", "afford a vacation", "afford to buy", "afford to take"]):
            return self._handle_affordability_query(query, user_id)
        
        # Expense analysis queries (specific patterns)
        elif any(phrase in query_lower for phrase in ["why did my expenses increase", "expenses increased", "expense analysis"]):
            return self._handle_expense_analysis_query(query, user_id)
        
        # Debt repayment queries (specific patterns)
        elif any(phrase in query_lower for phrase in ["repay my loan", "pay off debt", "debt repayment", "best option for repaying"]):
            return self._handle_debt_repayment_query(query, user_id)
        
        # General queries (fallback) - handle both financial and general conversation
        else:
            return self._handle_general_query(query, user_id)
    
    def _handle_affordability_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle affordability questions like 'Can I afford to take a vacation next month?'"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "affordability",
                "response": "I don't have access to your financial data yet. To help you with vacation affordability, I need to see your income, expenses, and account balances.",
                "recommendation": "Please add your bank accounts, income transactions, and expense transactions to get personalized vacation affordability analysis. I can then tell you exactly how much you can afford to spend on your next vacation!",
                "financial_data": {}
            }
        
        # Extract vacation cost (default to 50,000 if not specified)
        vacation_cost = self._extract_amount_from_query(query) or 50000
        
        # Calculate monthly cash flow from database data
        # Use transaction data for more accurate monthly calculations
        monthly_income = data.get("totals", {}).get("monthly_income_from_transactions", 0)
        monthly_expenses = data.get("totals", {}).get("monthly_expenses_from_transactions", 0)
        
        # If no transaction data, fall back to account totals
        if monthly_income == 0:
            monthly_income = data.get("totals", {}).get("total_income", 0)
        if monthly_expenses == 0:
            monthly_expenses = data.get("totals", {}).get("total_expenses", 0)
        
        # Add debt payments
        total_debt_payments = 0
        for debt in data.get("debts", []):
            total_debt_payments += debt.get("minimum_payment", 0)
        
        monthly_expenses += total_debt_payments
        net_monthly_cash_flow = monthly_income - monthly_expenses
        
        # Check affordability
        can_afford = net_monthly_cash_flow >= vacation_cost
        shortfall = max(0, vacation_cost - net_monthly_cash_flow)
        
        if can_afford:
            response = f"✅ Yes, you can afford a vacation next month! You have ₹{net_monthly_cash_flow:,.0f} available monthly, which covers the ₹{vacation_cost:,.0f} vacation cost. You'll still have ₹{net_monthly_cash_flow - vacation_cost:,.0f} left for other expenses."
            recommendation = "Go ahead and plan your vacation! Consider booking in advance for better deals."
        else:
            response = f"❌ Unfortunately, you cannot afford a ₹{vacation_cost:,.0f} vacation next month. You're short by ₹{shortfall:,.0f}."
            recommendation = f"Consider saving ₹{shortfall:,.0f} more this month, or look for a cheaper vacation option around ₹{net_monthly_cash_flow:,.0f}."
        
        return {
            "query_type": "affordability",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "net_cash_flow": net_monthly_cash_flow,
                "vacation_cost": vacation_cost,
                "can_afford": can_afford,
                "shortfall": shortfall
            }
        }
    
    def _handle_expense_analysis_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle expense analysis questions like 'Why did my expenses increase last quarter?'"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "expense_analysis",
                "response": "I don't have access to your financial data yet. To analyze your expenses and identify spending patterns, I need to see your transaction history.",
                "recommendation": "Please add your expense transactions with categories (like groceries, rent, entertainment) to get detailed spending analysis. I can then help you identify where your money is going and suggest ways to reduce expenses!",
                "financial_data": {}
            }
        
        # Analyze current expenses from database
        transactions = data.get("transactions", [])
        category_spending = {}
        
        for transaction in transactions:
            if transaction.get("type") == "expense":
                category = transaction.get("category", "other")
                amount = transaction.get("amount", 0)
                category_spending[category] = category_spending.get(category, 0) + amount
        
        total_spending = sum(category_spending.values())
        
        # Find highest spending categories
        sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
        highest_category = sorted_categories[0] if sorted_categories else None
        
        # Analyze spending patterns
        analysis = []
        if highest_category:
            percentage = (highest_category[1] / total_spending) * 100 if total_spending > 0 else 0
            analysis.append(f"Your highest expense is {highest_category[0].replace('_', ' ')} at ₹{highest_category[1]:,.0f} ({percentage:.1f}% of total spending).")
        
        # Check for potential causes of increase
        if category_spending.get("entertainment", 0) > 10000:
            analysis.append("Entertainment expenses are quite high - consider reducing dining out and subscriptions.")
        
        if category_spending.get("transportation", 0) > 8000:
            analysis.append("Transportation costs seem elevated - check if fuel prices or travel frequency increased.")
        
        # Generate response
        response = f"Your total monthly expenses are ₹{total_spending:,.0f}. "
        if analysis:
            response += " ".join(analysis)
        else:
            response += "Your spending appears to be within normal ranges."
        
        recommendation = "To reduce expenses, consider: 1) Reviewing subscription services, 2) Cooking more meals at home, 3) Using public transport more often, 4) Setting monthly spending limits for each category."
        
        return {
            "query_type": "expense_analysis",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "total_spending": total_spending,
                "category_breakdown": category_spending,
                "highest_category": highest_category[0] if highest_category else None,
                "highest_amount": highest_category[1] if highest_category else 0
            }
        }
    
    def _handle_debt_repayment_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle debt repayment questions like 'What's my best option for repaying my loan faster?'"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "debt_repayment",
                "response": "I don't have access to your financial data yet. To help you optimize your debt repayment strategy, I need to see your debts, income, and expenses.",
                "recommendation": "Please add your loans, credit cards, and other debts with interest rates and minimum payments. Also add your income and expense transactions. I can then create a personalized debt payoff plan that saves you the most money!",
                "financial_data": {}
            }
        
        # Analyze all debts from database
        debts = data.get("debts", [])
        
        total_debt = 0
        monthly_payments = 0
        debt_breakdown = {}
        
        # Process debts
        for debt in debts:
            debt_name = debt.get("name", "Unknown")
            remaining_amount = debt.get("remaining_amount", 0)
            minimum_payment = debt.get("minimum_payment", 0)
            interest_rate = debt.get("interest_rate", 0)
            debt_type = debt.get("type", "loan")
            
            total_debt += remaining_amount
            monthly_payments += minimum_payment
            debt_breakdown[debt_name] = {
                "type": debt_type,
                "remaining_amount": remaining_amount,
                "minimum_payment": minimum_payment,
                "interest_rate": interest_rate
            }
        
        # Calculate available extra payment
        # Use transaction data for more accurate monthly calculations
        monthly_income = data.get("totals", {}).get("monthly_income_from_transactions", 0)
        monthly_expenses = data.get("totals", {}).get("monthly_expenses_from_transactions", 0)
        
        # If no transaction data, fall back to account totals
        if monthly_income == 0:
            monthly_income = data.get("totals", {}).get("total_income", 0)
        if monthly_expenses == 0:
            monthly_expenses = data.get("totals", {}).get("total_expenses", 0)
        
        net_cash_flow = monthly_income - monthly_expenses
        extra_payment = max(0, net_cash_flow - monthly_payments)
        
        # Find highest interest debt
        highest_interest_debt = None
        highest_rate = 0
        for debt_name, debt_info in debt_breakdown.items():
            rate = debt_info.get("interest_rate", 0)
            if rate > highest_rate:
                highest_rate = rate
                highest_interest_debt = debt_name
        
        # Generate response
        response = f"You have a total debt of ₹{total_debt:,.0f} with monthly payments of ₹{monthly_payments:,.0f}. "
        
        if extra_payment > 0:
            response += f"You have ₹{extra_payment:,.0f} extra monthly that can be used for faster repayment. "
        
        if highest_interest_debt:
            response += f"Your highest interest debt is {highest_interest_debt} at {highest_rate}%."
        
        # Generate recommendations
        recommendations = []
        if highest_interest_debt:
            recommendations.append(f"Priority 1: Pay extra towards {highest_interest_debt} (highest interest rate: {highest_rate}%)")
        
        if extra_payment > 0:
            recommendations.append(f"Use your extra ₹{extra_payment:,.0f} monthly to accelerate debt payoff")
        
        recommendations.extend([
            "Consider debt consolidation if you have multiple high-interest debts",
            "Set up automatic payments to avoid late fees",
            "Review your budget to find additional money for debt repayment"
        ])
        
        recommendation = " ".join(recommendations)
        
        return {
            "query_type": "debt_repayment",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "total_debt": total_debt,
                "monthly_payments": monthly_payments,
                "extra_payment_available": extra_payment,
                "highest_interest_debt": highest_interest_debt,
                "highest_interest_rate": highest_rate,
                "debt_breakdown": debt_breakdown
            }
        }
    
    def _handle_general_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle general queries - both financial and conversational"""
        data = self.load_financial_data(user_id)
        query_lower = query.lower()
        
        # Check if it's a financial question that we can answer with data
        if any(word in query_lower for word in ["net worth", "worth", "total assets"]):
            return self._handle_net_worth_query(query, user_id)
        elif any(word in query_lower for word in ["save", "saving", "savings"]):
            return self._handle_savings_query(query, user_id)
        elif any(word in query_lower for word in ["invest", "investment", "portfolio"]):
            return self._handle_investment_query(query, user_id)
        elif any(word in query_lower for word in ["expense", "spending", "spend"]):
            return self._handle_spending_query(query, user_id)
        elif any(word in query_lower for word in ["budget", "budgeting"]):
            return self._handle_budget_query(query, user_id)
        elif any(word in query_lower for word in ["income", "earn", "salary"]):
            return self._handle_income_query(query, user_id)
        elif any(word in query_lower for word in ["balance", "account", "money"]):
            return self._handle_balance_query(query, user_id)
        
        # Handle greetings and general conversation
        elif any(word in query_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
            return {
                "query_type": "greeting",
                "response": "Hello! I'm your TrackSpendAI Assistant. I can help you with your finances - ask me about your income, expenses, savings, investments, or any financial questions you have!",
                "recommendation": "Try asking about your current balance, monthly income, or spending patterns.",
                "financial_data": {}
            }
        
        elif any(word in query_lower for word in ["how are you", "how's it going", "what's up"]):
            return {
                "query_type": "conversation",
                "response": "I'm doing great! I'm here to help you manage your finances better. What would you like to know about your financial situation?",
                "recommendation": "I can help you analyze your spending, track your savings, or plan your budget.",
                "financial_data": {}
            }
        
        elif any(word in query_lower for word in ["thank you", "thanks", "appreciate"]):
            return {
                "query_type": "conversation",
                "response": "You're welcome! I'm always here to help with your financial questions. Feel free to ask me anything about your money management!",
                "recommendation": "Is there anything else about your finances you'd like to know?",
                "financial_data": {}
            }
        
        elif any(word in query_lower for word in ["help", "what can you do", "capabilities"]):
            permission_message = self.get_permission_status_message(user_id)
            return {
                "query_type": "help",
                "response": f"I can help you with many financial topics! I can analyze your income, expenses, savings, investments, budgets, and more. I can also help you plan for purchases, track your spending patterns, and give you personalized financial advice based on your actual data.\n\n{permission_message}",
                "recommendation": "Try asking me about your current financial situation or specific questions like 'What's my income?' or 'How much can I save?' You can also manage your data permissions in the settings.",
                "financial_data": data.get("totals", {}) if data else {}
            }
        
        # Handle financial questions that don't match specific patterns
        elif any(word in query_lower for word in ["money", "finance", "financial", "budget", "expense", "income", "saving", "debt", "loan", "investment"]):
            permission_message = self.get_permission_status_message(user_id)
            return {
                "query_type": "financial_general",
                "response": f"I can help you with that financial question! However, I need more specific information to give you the best answer. Could you be more specific about what you'd like to know?\n\n{permission_message}",
                "recommendation": "Try asking specific questions like 'What's my current balance?' or 'How much did I spend last month?' You can also manage your data permissions in the settings.",
                "financial_data": data.get("totals", {}) if data else {}
            }
        
        # Handle AI-powered insights queries
        elif any(word in query_lower for word in ["predict", "prediction", "future", "forecast", "projection"]):
            return self._handle_prediction_query(query, user_id)
        elif any(word in query_lower for word in ["unusual", "anomaly", "strange", "weird", "abnormal", "outlier", "detect"]):
            return self._handle_anomaly_detection_query(query, user_id)
        elif any(word in query_lower for word in ["debt", "loan", "repay", "repayment", "pay off", "optimize", "smart"]):
            return self._handle_debt_optimization_query(query, user_id)
        elif any(word in query_lower for word in ["insights", "analysis", "recommendation", "suggest", "advice"]):
            return self._handle_insights_query(query, user_id)
        
        # Handle non-financial questions
        else:
            return {
                "query_type": "non_financial",
                "response": "I'm your TrackSpendAI Assistant, specialized in helping with financial questions and money management. I can help you with topics like budgeting, saving, investing, debt management, financial planning, and AI-powered insights. Is there something about your finances I can help you with?",
                "recommendation": "Try asking me about your income, expenses, savings goals, future predictions, unusual spending patterns, or debt optimization strategies!",
                "financial_data": {}
            }
    
    def _handle_net_worth_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle net worth questions"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "net_worth",
                "response": "I don't have access to your financial data. Please make sure you have accounts and transactions set up.",
                "recommendation": "Add some accounts and transactions to get your net worth calculated.",
                "financial_data": {}
            }
        
        totals = data.get("totals", {})
        net_worth = totals.get("net_worth", 0)
        total_assets = totals.get("total_balance", 0) + totals.get("total_investments", 0)
        total_debt = totals.get("total_debt", 0)
        
        if net_worth > 0:
            response = f"Your current net worth is ₹{net_worth:,.0f}. This is calculated as your total assets (₹{total_assets:,.0f}) minus your total debt (₹{total_debt:,.0f})."
            recommendation = "Great job maintaining a positive net worth! Consider increasing your investments to grow your wealth further."
        else:
            response = f"Your current net worth is ₹{net_worth:,.0f}. You have ₹{total_assets:,.0f} in assets but ₹{total_debt:,.0f} in debt."
            recommendation = "Focus on paying down high-interest debt first, then build your emergency fund and investments."
        
        return {
            "query_type": "net_worth",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "net_worth": net_worth,
                "total_assets": total_assets,
                "total_debt": total_debt,
                "breakdown": {
                    "cash_balance": totals.get("total_balance", 0),
                    "investments": totals.get("total_investments", 0),
                    "debt": total_debt
                }
            }
        }
    
    def _handle_savings_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle savings questions"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "savings",
                "response": "I don't have access to your financial data. Please make sure you have accounts and transactions set up.",
                "recommendation": "Add some accounts and transactions to analyze your savings potential.",
                "financial_data": {}
            }
        
        totals = data.get("totals", {})
        monthly_income = totals.get("monthly_income_from_transactions", 0) or totals.get("total_income", 0)
        monthly_expenses = totals.get("monthly_expenses_from_transactions", 0) or totals.get("total_expenses", 0)
        
        # Add debt payments
        total_debt_payments = sum(debt.get("minimum_payment", 0) for debt in data.get("debts", []))
        monthly_expenses += total_debt_payments
        
        potential_savings = monthly_income - monthly_expenses
        savings_rate = (potential_savings / monthly_income * 100) if monthly_income > 0 else 0
        
        if potential_savings > 0:
            response = f"Based on your current income and expenses, you can potentially save ₹{potential_savings:,.0f} per month. This represents a {savings_rate:.1f}% savings rate."
            recommendation = "Excellent! Consider setting up automatic transfers to a high-yield savings account or investment account."
        else:
            shortfall = abs(potential_savings)
            response = f"Your current expenses exceed your income by ₹{shortfall:,.0f} per month. You're spending more than you earn."
            recommendation = "Immediate action needed: reduce expenses, increase income, or both. Focus on eliminating non-essential spending first."
        
        return {
            "query_type": "savings",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "potential_savings": potential_savings,
                "savings_rate": savings_rate,
                "debt_payments": total_debt_payments
            }
        }
    
    def _handle_investment_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle investment questions"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "investment",
                "response": "I don't have access to your financial data. Please make sure you have accounts and transactions set up.",
                "recommendation": "Add some investment accounts to get investment analysis.",
                "financial_data": {}
            }
        
        portfolio = data.get("portfolio", [])
        total_investments = data.get("totals", {}).get("total_investments", 0)
        total_debt = data.get("totals", {}).get("total_debt", 0)
        
        if not portfolio:
            response = "You don't have any investments in your portfolio yet."
            recommendation = "Consider starting with low-cost index funds or ETFs. Even small amounts can grow significantly over time."
        else:
            total_gain_loss = sum(item.get("gain_loss", 0) for item in portfolio)
            response = f"You have ₹{total_investments:,.0f} invested across {len(portfolio)} holdings. Your total gain/loss is ₹{total_gain_loss:,.0f}."
            
            if total_debt > 0:
                recommendation = "You have debt. Consider paying off high-interest debt (above 6-8%) before investing more. For lower interest debt, investing might be better."
            else:
                recommendation = "Great! With no debt, you can focus on maximizing your investments. Consider increasing your investment contributions."
        
        return {
            "query_type": "investment",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "total_investments": total_investments,
                "portfolio_count": len(portfolio),
                "total_gain_loss": sum(item.get("gain_loss", 0) for item in portfolio),
                "portfolio": portfolio
            }
        }
    
    def _handle_spending_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle spending analysis questions with enhanced natural language processing"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "spending",
                "response": "I don't have access to your financial data. Please make sure you have accounts and transactions set up.",
                "recommendation": "Add some transactions to analyze your spending patterns.",
                "financial_data": {}
            }
        
        # Parse time period and category from query
        time_period = self._parse_time_period(query)
        category = self._parse_category_from_query(query)
        
        transactions = data.get("transactions", [])
        expense_transactions = [t for t in transactions if t.get("type") == "expense"]
        
        if not expense_transactions:
            response = "I don't see any expense transactions in your data."
            recommendation = "Add some expense transactions to get spending analysis."
        else:
            # Filter transactions by time period if specified
            if time_period['days'] > 0:
                end_date = datetime.now(timezone.utc)
                start_date = end_date - timedelta(days=time_period['days'])
                
                filtered_transactions = []
                for transaction in expense_transactions:
                    try:
                        transaction_date = datetime.fromisoformat(transaction.get('date', '').replace('Z', '+00:00'))
                        if start_date <= transaction_date <= end_date:
                            filtered_transactions.append(transaction)
                    except:
                        # If date parsing fails, include the transaction
                        filtered_transactions.append(transaction)
                
                expense_transactions = filtered_transactions
            
            # Filter by category if specified
            if category:
                expense_transactions = [t for t in expense_transactions if t.get("category", "").lower() == category.lower()]
            
            if not expense_transactions:
                if category:
                    response = f"I don't see any {category} expenses in your data for {time_period['label']}."
                else:
                    response = f"I don't see any expense transactions in your data for {time_period['label']}."
                recommendation = "Add some expense transactions to get spending analysis."
            else:
                # Analyze spending by category
                category_spending = {}
                total_spending = 0
                
                for transaction in expense_transactions:
                    trans_category = transaction.get("category", "other")
                    amount = transaction.get("amount", 0)
                    category_spending[trans_category] = category_spending.get(trans_category, 0) + amount
                    total_spending += amount
                
                # Find top spending categories
                top_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)[:3]
                
                # Build response based on query context
                if category:
                    response = f"Your {category} spending for {time_period['label']} is ₹{total_spending:,.0f}."
                    if top_categories:
                        response += f" This includes: {', '.join([f'{cat} (₹{amt:,.0f})' for cat, amt in top_categories])}."
                else:
                    response = f"Your total spending for {time_period['label']} is ₹{total_spending:,.0f}."
                    if top_categories:
                        response += f" Your top spending categories are: {', '.join([f'{cat} (₹{amt:,.0f})' for cat, amt in top_categories])}."
                
                # Add contextual recommendations
                if total_spending > 50000:  # High spending threshold
                    recommendation = "Your spending is quite high. Consider creating a budget to better control your expenses."
                elif len(top_categories) > 0 and top_categories[0][1] > total_spending * 0.4:
                    recommendation = f"Your {top_categories[0][0]} spending is quite high. Consider reducing expenses in this category."
                else:
                    recommendation = "Consider reviewing your spending patterns to identify areas for potential savings."
        
        # Update conversation context
        self._update_conversation_context(user_id, 'spending', time_period['label'], category, total_spending if 'total_spending' in locals() else 0)
        
        return {
            "query_type": "spending",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "total_spending": total_spending if 'total_spending' in locals() else 0,
                "transaction_count": len(expense_transactions),
                "category_breakdown": category_spending if 'category_spending' in locals() else {},
                "time_period": time_period['label'],
                "category": category
            }
        }
    
    def _handle_budget_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle budget questions"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "budget",
                "response": "I don't have access to your financial data. Please make sure you have accounts and transactions set up.",
                "recommendation": "Add some budgets to get budget analysis.",
                "financial_data": {}
            }
        
        budgets = data.get("budgets", [])
        
        if not budgets:
            response = "You don't have any budgets set up yet."
            recommendation = "Create budgets for your main expense categories to better control your spending."
        else:
            total_budget = sum(budget.get("limit", 0) for budget in budgets)
            total_spent = sum(budget.get("spent", 0) for budget in budgets)
            total_remaining = sum(budget.get("remaining", 0) for budget in budgets)
            
            # Find budgets that are over
            over_budget = [b for b in budgets if b.get("spent", 0) > b.get("limit", 0)]
            
            response = f"You have {len(budgets)} budgets with a total limit of ₹{total_budget:,.0f}. You've spent ₹{total_spent:,.0f} and have ₹{total_remaining:,.0f} remaining."
            
            if over_budget:
                response += f" You're over budget in {len(over_budget)} categories."
                recommendation = "Focus on the categories where you're over budget. Consider adjusting your spending or increasing those budget limits."
            else:
                recommendation = "Great job staying within your budgets! Consider increasing your savings rate or investing the remaining amounts."
        
        return {
            "query_type": "budget",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "total_budgets": len(budgets),
                "total_budget_limit": total_budget,
                "total_spent": total_spent,
                "total_remaining": total_remaining,
                "over_budget_count": len(over_budget) if budgets else 0
            }
            }
    
    def _handle_income_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle income questions with enhanced natural language processing"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "income",
                "response": "I don't have access to your financial data yet. To show your income, I need to see your income transactions.",
                "recommendation": "Please add your income transactions (salary, freelance, etc.) to get your income analysis.",
                "financial_data": {}
            }
        
        # Parse time period from query
        time_period = self._parse_time_period(query)
        
        # Calculate income from transactions
        transactions = data.get("transactions", [])
        income_transactions = [t for t in transactions if t.get("type") == "income"]
        
        if not income_transactions:
            return {
                "query_type": "income",
                "response": "I don't see any income transactions in your data yet.",
                "recommendation": "Add some income transactions to track your earnings.",
                "financial_data": {}
            }
        
        # Filter transactions by time period
        if time_period['days'] > 0:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=time_period['days'])
            
            filtered_transactions = []
            for transaction in income_transactions:
                try:
                    transaction_date = datetime.fromisoformat(transaction.get('date', '').replace('Z', '+00:00'))
                    if start_date <= transaction_date <= end_date:
                        filtered_transactions.append(transaction)
                except:
                    # If date parsing fails, include the transaction
                    filtered_transactions.append(transaction)
            
            income_transactions = filtered_transactions
        
        if not income_transactions:
            return {
                "query_type": "income",
                "response": f"I don't see any income transactions for {time_period['label']}.",
                "recommendation": "Add some income transactions to track your earnings.",
                "financial_data": {}
            }
        
        # Calculate total income for the period
        total_income = sum(t.get("amount", 0) for t in income_transactions)
        
        # Analyze income sources
        income_sources = {}
        for transaction in income_transactions:
            category = transaction.get("category", "other")
            amount = transaction.get("amount", 0)
            income_sources[category] = income_sources.get(category, 0) + amount
        
        top_source = max(income_sources.items(), key=lambda x: x[1]) if income_sources else None
        
        # Build response based on time period
        response = f"Your total income for {time_period['label']} is ₹{total_income:,.0f}."
        if top_source:
            response += f" Your main income source is {top_source[0].replace('_', ' ')} (₹{top_source[1]:,.0f})."
        
        # Add contextual recommendations
        if total_income > 100000:  # High income threshold
            recommendation = "Great income! Consider investing a portion of your earnings for long-term wealth building."
        elif total_income > 50000:
            recommendation = "Good income level. Consider setting up automatic savings and building an emergency fund."
        else:
            recommendation = "Consider looking for opportunities to increase your income through skill development or side hustles."
        
        # Update conversation context
        self._update_conversation_context(user_id, 'income', time_period['label'], None, total_income)
        
        return {
            "query_type": "income",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "total_income": total_income,
                "income_sources": income_sources,
                "transaction_count": len(income_transactions),
                "time_period": time_period['label']
            }
        }
    
    def _handle_balance_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle balance questions like 'What's my current balance?'"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "balance",
                "response": "I don't have access to your financial data yet. To show your balance, I need to see your accounts.",
                "recommendation": "Please add your bank accounts to get your balance information.",
                "financial_data": {}
            }
        
        accounts = data.get("accounts", [])
        if not accounts:
            return {
                "query_type": "balance",
                "response": "I don't see any accounts in your data yet.",
                "recommendation": "Add your bank accounts to track your balances.",
                "financial_data": {}
            }
        
        total_balance = sum(account.get("balance", 0) for account in accounts)
        
        # Show account breakdown
        account_breakdown = []
        for account in accounts:
            account_breakdown.append(f"{account.get('name', 'Unknown')}: ₹{account.get('balance', 0):,.0f}")
        
        response = f"Your total balance across all accounts is ₹{total_balance:,.0f}. "
        if len(accounts) > 1:
            response += f"Account breakdown: {', '.join(account_breakdown)}."
        
        # Add contextual recommendations
        if total_balance > 500000:  # High balance threshold
            recommendation = "Great savings! Consider investing some of your balance for better returns."
        elif total_balance > 100000:
            recommendation = "Good balance level. Consider keeping 3-6 months of expenses in your savings account for emergencies."
        else:
            recommendation = "Consider building up your savings. Aim for at least 3-6 months of expenses as an emergency fund."
        
        # Update conversation context
        self._update_conversation_context(user_id, 'balance', 'current', None, total_balance)
        
        return {
            "query_type": "balance",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "total_balance": total_balance,
                "account_count": len(accounts),
                "accounts": accounts
            }
        }
    
    def _extract_amount_from_query(self, query: str) -> Optional[float]:
        """Extract monetary amount from query"""
        import re
        
        # Look for patterns like "₹50000", "50,000", "50k", etc.
        patterns = [
            r'₹?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:\.\d{2})?)\s*(?:k|thousand)',
            r'(\d+(?:\.\d{2})?)\s*(?:lakh|lac)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    if 'k' in query.lower() or 'thousand' in query.lower():
                        amount *= 1000
                    elif 'lakh' in query.lower() or 'lac' in query.lower():
                        amount *= 100000
                    return amount
                except ValueError:
                    continue
        return None
    
    def _handle_prediction_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Handle future savings and spending predictions"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "prediction",
                "response": "I need access to your financial data to make predictions. Please ensure you have transactions and account information set up.",
                "recommendation": "Add your income and expense transactions to get personalized predictions.",
                "financial_data": {}
            }
        
        # Calculate current financial metrics
        totals = data.get("totals", {})
        monthly_income = totals.get("monthly_income_from_transactions", 0)
        monthly_expenses = totals.get("monthly_expenses_from_transactions", 0)
        current_savings = totals.get("total_balance", 0)
        
        # Simple prediction logic based on current patterns
        if monthly_income > 0 and monthly_expenses > 0:
            monthly_savings = monthly_income - monthly_expenses
            savings_rate = (monthly_savings / monthly_income) * 100 if monthly_income > 0 else 0
            
            # Predict future savings (6 months, 1 year, 2 years)
            future_6_months = current_savings + (monthly_savings * 6)
            future_1_year = current_savings + (monthly_savings * 12)
            future_2_years = current_savings + (monthly_savings * 24)
            
            if monthly_savings > 0:
                response = f"Based on your current spending patterns, here's what I predict:\n\n"
                response += f"📈 **Future Savings Predictions:**\n"
                response += f"• 6 months: ₹{future_6_months:,.0f} (₹{monthly_savings:,.0f} per month)\n"
                response += f"• 1 year: ₹{future_1_year:,.0f}\n"
                response += f"• 2 years: ₹{future_2_years:,.0f}\n\n"
                response += f"Your current savings rate is {savings_rate:.1f}%, which is {'excellent' if savings_rate >= 20 else 'good' if savings_rate >= 10 else 'needs improvement'}."
                
                recommendation = "To improve your savings, consider reducing non-essential expenses or increasing your income. Even a 5% increase in savings rate can significantly impact your future wealth."
            else:
                response = f"⚠️ **Spending Alert:** You're currently spending more than you earn (₹{abs(monthly_savings):,.0f} deficit per month).\n\n"
                response += f"This pattern will deplete your current savings of ₹{current_savings:,.0f} in approximately {abs(current_savings / monthly_savings):.1f} months if not addressed."
                
                recommendation = "Immediate action needed: Reduce expenses by at least ₹{:.0f} per month or increase income to achieve financial stability.".format(abs(monthly_savings))
        else:
            response = "I need more transaction data to make accurate predictions. Please add your income and expense transactions."
            recommendation = "Add at least 2-3 months of transaction data for better predictions."
        
        return {
            "query_type": "prediction",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "monthly_savings": monthly_savings if monthly_income > 0 and monthly_expenses > 0 else 0,
                "savings_rate": savings_rate if monthly_income > 0 and monthly_expenses > 0 else 0,
                "current_savings": current_savings
            }
        }
    
    def _handle_anomaly_detection_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Detect unusual spending patterns and anomalies"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "anomaly_detection",
                "response": "I need access to your transaction data to detect unusual spending patterns.",
                "recommendation": "Add your expense transactions to get anomaly detection insights.",
                "financial_data": {}
            }
        
        transactions = data.get("transactions", [])
        expense_transactions = [t for t in transactions if t.get("type") == "expense"]
        
        if len(expense_transactions) < 10:
            return {
                "query_type": "anomaly_detection",
                "response": "I need at least 10 expense transactions to detect patterns and anomalies effectively.",
                "recommendation": "Add more expense transactions to get better anomaly detection.",
                "financial_data": {}
            }
        
        # Analyze spending patterns
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        # Group expenses by category and month
        category_spending = defaultdict(list)
        monthly_totals = defaultdict(float)
        
        for transaction in expense_transactions:
            if transaction.get("date") and transaction.get("amount"):
                try:
                    date = datetime.fromisoformat(transaction.get("date").replace('Z', '+00:00'))
                    month_key = date.strftime('%Y-%m')
                    amount = transaction.get("amount", 0)
                    category = transaction.get("category", "uncategorized")
                    
                    category_spending[category].append(amount)
                    monthly_totals[month_key] += amount
                except:
                    continue
        
        # Detect anomalies
        anomalies = []
        
        # 1. Unusually high individual transactions
        all_amounts = [t.get("amount", 0) for t in expense_transactions if t.get("amount")]
        if all_amounts:
            avg_amount = sum(all_amounts) / len(all_amounts)
            threshold = avg_amount * 3  # 3x average is considered unusual
            
            for transaction in expense_transactions:
                if transaction.get("amount", 0) > threshold:
                    anomalies.append({
                        "type": "high_amount",
                        "amount": transaction.get("amount", 0),
                        "category": transaction.get("category", "uncategorized"),
                        "date": transaction.get("date", ""),
                        "description": f"Unusually high expense of ₹{transaction.get('amount', 0):,.0f} in {transaction.get('category', 'uncategorized')}"
                    })
        
        # 2. Category spending spikes
        for category, amounts in category_spending.items():
            if len(amounts) >= 3:
                avg_category = sum(amounts) / len(amounts)
                max_amount = max(amounts)
                if max_amount > avg_category * 2.5:
                    anomalies.append({
                        "type": "category_spike",
                        "category": category,
                        "amount": max_amount,
                        "description": f"Spending spike in {category}: ₹{max_amount:,.0f} (avg: ₹{avg_category:,.0f})"
                    })
        
        # 3. Monthly spending variations
        if len(monthly_totals) >= 3:
            monthly_values = list(monthly_totals.values())
            avg_monthly = sum(monthly_values) / len(monthly_values)
            max_month = max(monthly_totals.items(), key=lambda x: x[1])
            
            if max_month[1] > avg_monthly * 1.5:
                anomalies.append({
                    "type": "monthly_spike",
                    "month": max_month[0],
                    "amount": max_month[1],
                    "description": f"High spending month: {max_month[0]} with ₹{max_month[1]:,.0f} (avg: ₹{avg_monthly:,.0f})"
                })
        
        # Generate response
        if anomalies:
            response = "🔍 **Unusual Spending Patterns Detected:**\n\n"
            for i, anomaly in enumerate(anomalies[:5], 1):  # Show top 5 anomalies
                response += f"{i}. {anomaly['description']}\n"
            
            if len(anomalies) > 5:
                response += f"\n... and {len(anomalies) - 5} more anomalies detected."
            
            recommendation = "Review these unusual expenses to identify potential areas for cost reduction or legitimate large purchases that may need budgeting."
        else:
            response = "✅ **No Unusual Spending Patterns Detected**\n\nYour spending appears to be consistent with your normal patterns. This is a good sign of financial discipline!"
            recommendation = "Continue monitoring your spending patterns. Consider setting up alerts for large transactions to maintain this good financial behavior."
        
        return {
            "query_type": "anomaly_detection",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "total_transactions_analyzed": len(expense_transactions),
                "anomalies_detected": len(anomalies),
                "anomalies": anomalies[:10]  # Limit to 10 for performance
            }
        }
    
    def _handle_debt_optimization_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Provide smart debt repayment and optimization strategies"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "debt_optimization",
                "response": "I need access to your debt information to provide optimization strategies.",
                "recommendation": "Add your debt accounts (loans, credit cards) to get personalized debt optimization advice.",
                "financial_data": {}
            }
        
        debts = data.get("debts", [])
        if not debts:
            return {
                "query_type": "debt_optimization",
                "response": "Great news! I don't see any debt accounts in your data. You're debt-free! 🎉",
                "recommendation": "Focus on building your emergency fund and investments to grow your wealth.",
                "financial_data": {}
            }
        
        # Analyze debt portfolio
        total_debt = sum(d.get("balance", 0) for d in debts)
        monthly_income = data.get("totals", {}).get("monthly_income_from_transactions", 0)
        
        if monthly_income == 0:
            return {
                "query_type": "debt_optimization",
                "response": "I need your income information to provide optimal debt repayment strategies.",
                "recommendation": "Add your income transactions to get personalized debt optimization advice.",
                "financial_data": {}
            }
        
        # Calculate debt-to-income ratio
        debt_to_income = (total_debt / monthly_income) * 100 if monthly_income > 0 else 0
        
        # Sort debts by interest rate (highest first for avalanche method)
        debts_by_rate = sorted(debts, key=lambda x: x.get("interest_rate", 0), reverse=True)
        
        # Calculate minimum payments
        total_minimum_payments = sum(d.get("minimum_payment", 0) for d in debts)
        available_for_extra = monthly_income * 0.2 - total_minimum_payments  # 20% of income for debt
        
        response = f"💡 **Smart Debt Optimization Strategy:**\n\n"
        response += f"**Current Situation:**\n"
        response += f"• Total Debt: ₹{total_debt:,.0f}\n"
        response += f"• Debt-to-Income Ratio: {debt_to_income:.1f}%\n"
        response += f"• Monthly Minimum Payments: ₹{total_minimum_payments:,.0f}\n\n"
        
        if debt_to_income > 40:
            response += "⚠️ **High Debt Alert:** Your debt-to-income ratio is above 40%, which is concerning.\n\n"
        elif debt_to_income > 20:
            response += "📊 **Moderate Debt:** Your debt-to-income ratio is manageable but could be improved.\n\n"
        else:
            response += "✅ **Low Debt:** Your debt-to-income ratio is healthy!\n\n"
        
        # Debt repayment strategies
        response += "**Recommended Strategy - Debt Avalanche Method:**\n"
        response += "Pay minimums on all debts, then put extra money toward the highest interest rate debt.\n\n"
        
        for i, debt in enumerate(debts_by_rate[:3], 1):  # Show top 3 debts
            debt_name = debt.get("name", f"Debt {i}")
            balance = debt.get("balance", 0)
            interest_rate = debt.get("interest_rate", 0)
            min_payment = debt.get("minimum_payment", 0)
            
            response += f"{i}. **{debt_name}**\n"
            response += f"   • Balance: ₹{balance:,.0f}\n"
            response += f"   • Interest Rate: {interest_rate:.1f}%\n"
            response += f"   • Minimum Payment: ₹{min_payment:,.0f}\n"
            
            if i == 1 and available_for_extra > 0:
                extra_payment = min(available_for_extra, balance * 0.1)  # Max 10% of balance
                response += f"   • **Extra Payment: ₹{extra_payment:,.0f}** (recommended)\n"
            
            response += "\n"
        
        # Calculate payoff timeline
        if available_for_extra > 0:
            # Simple calculation for highest interest debt
            highest_debt = debts_by_rate[0]
            balance = highest_debt.get("balance", 0)
            min_payment = highest_debt.get("minimum_payment", 0)
            extra_payment = min(available_for_extra, balance * 0.1)
            total_payment = min_payment + extra_payment
            
            if total_payment > 0:
                months_to_payoff = balance / total_payment
                response += f"**Payoff Timeline:**\n"
                response += f"With extra payments of ₹{extra_payment:,.0f}/month, you could pay off your highest interest debt in approximately {months_to_payoff:.1f} months.\n\n"
        
        # Investment vs debt advice
        avg_interest_rate = sum(d.get("interest_rate", 0) for d in debts) / len(debts) if debts else 0
        if avg_interest_rate > 8:
            recommendation = "Focus on debt repayment first - your average interest rate is high. Consider debt consolidation or refinancing to lower rates."
        elif avg_interest_rate > 5:
            recommendation = "Balance debt repayment with investments. Pay extra on high-interest debts, but consider investing if you can earn more than 5% returns."
        else:
            recommendation = "Your debt has low interest rates. Consider investing extra money rather than paying off debt early, as you might earn higher returns."
        
        return {
            "query_type": "debt_optimization",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "total_debt": total_debt,
                "debt_to_income_ratio": debt_to_income,
                "number_of_debts": len(debts),
                "average_interest_rate": avg_interest_rate,
                "total_minimum_payments": total_minimum_payments
            }
        }
    
    def _handle_insights_query(self, query: str, user_id: str) -> Dict[str, Any]:
        """Provide comprehensive financial insights and recommendations"""
        data = self.load_financial_data(user_id)
        
        if not data:
            return {
                "query_type": "insights",
                "response": "I need access to your financial data to provide personalized insights.",
                "recommendation": "Add your accounts, transactions, and financial information to get comprehensive insights.",
                "financial_data": {}
            }
        
        totals = data.get("totals", {})
        transactions = data.get("transactions", [])
        
        # Calculate key metrics
        monthly_income = totals.get("monthly_income_from_transactions", 0)
        monthly_expenses = totals.get("monthly_expenses_from_transactions", 0)
        net_worth = totals.get("net_worth", 0)
        total_debt = totals.get("total_debt", 0)
        total_investments = totals.get("total_investments", 0)
        
        # Generate comprehensive insights
        insights = []
        
        # 1. Cash Flow Analysis
        if monthly_income > 0 and monthly_expenses > 0:
            monthly_savings = monthly_income - monthly_expenses
            savings_rate = (monthly_savings / monthly_income) * 100
            
            if savings_rate >= 20:
                insights.append("🌟 **Excellent Savings Rate**: You're saving 20%+ of your income - this is outstanding!")
            elif savings_rate >= 10:
                insights.append("✅ **Good Savings Rate**: You're saving 10%+ of your income - keep it up!")
            elif savings_rate > 0:
                insights.append("📈 **Positive Cash Flow**: You're saving money each month - consider increasing your savings rate.")
            else:
                insights.append("⚠️ **Negative Cash Flow**: You're spending more than you earn - immediate action needed.")
        
        # 2. Net Worth Analysis
        if net_worth > 0:
            insights.append(f"💰 **Positive Net Worth**: ₹{net_worth:,.0f} - you're building wealth!")
        elif net_worth < 0:
            insights.append(f"📉 **Negative Net Worth**: ₹{abs(net_worth):,.0f} - focus on debt reduction and asset building.")
        
        # 3. Debt Analysis
        if total_debt > 0:
            debt_to_income = (total_debt / monthly_income) * 100 if monthly_income > 0 else 0
            if debt_to_income > 40:
                insights.append("🚨 **High Debt Load**: Your debt is over 40% of annual income - prioritize debt reduction.")
            elif debt_to_income > 20:
                insights.append("📊 **Moderate Debt**: Manageable debt level - consider acceleration strategies.")
            else:
                insights.append("✅ **Low Debt**: Healthy debt-to-income ratio - maintain this level.")
        
        # 4. Investment Analysis
        if total_investments > 0:
            investment_ratio = (total_investments / (total_investments + totals.get("total_balance", 0))) * 100
            if investment_ratio >= 50:
                insights.append("📈 **Strong Investment Portfolio**: Over 50% of assets in investments - great wealth building!")
            elif investment_ratio >= 25:
                insights.append("💼 **Balanced Portfolio**: Good mix of cash and investments.")
            else:
                insights.append("💵 **Cash Heavy**: Consider investing more of your cash for better returns.")
        
        # 5. Spending Pattern Analysis
        expense_transactions = [t for t in transactions if t.get("type") == "expense"]
        if len(expense_transactions) >= 10:
            # Find top spending categories
            category_spending = {}
            for transaction in expense_transactions:
                category = transaction.get("category", "uncategorized")
                amount = transaction.get("amount", 0)
                category_spending[category] = category_spending.get(category, 0) + amount
            
            if category_spending:
                top_category = max(category_spending.items(), key=lambda x: x[1])
                insights.append(f"🛒 **Top Spending Category**: {top_category[0].replace('_', ' ').title()} - ₹{top_category[1]:,.0f}")
        
        # Generate response
        if insights:
            response = "🎯 **Your Financial Health Insights:**\n\n"
            for insight in insights:
                response += f"{insight}\n\n"
        else:
            response = "I need more financial data to provide comprehensive insights. Please add more transactions and account information."
        
        # Generate recommendations
        recommendations = []
        
        if monthly_income > 0 and monthly_expenses > 0:
            monthly_savings = monthly_income - monthly_expenses
            if monthly_savings < 0:
                recommendations.append("🚨 **Emergency**: Reduce expenses by at least ₹{:.0f} to stop losing money.".format(abs(monthly_savings)))
            elif monthly_savings < monthly_income * 0.1:
                recommendations.append("📈 **Improve Savings**: Aim to save at least 10% of your income (₹{:.0f}/month).".format(monthly_income * 0.1))
        
        if total_debt > 0:
            recommendations.append("💳 **Debt Strategy**: Focus on paying off high-interest debt first, then build emergency fund.")
        
        if total_investments < monthly_income * 6:
            recommendations.append("📊 **Investment Goal**: Build investments worth 6 months of income for financial security.")
        
        if not recommendations:
            recommendations.append("🎉 **Great Job**: Your finances look healthy! Consider advanced strategies like tax optimization or estate planning.")
        
        recommendation = "\n".join(recommendations)
        
        return {
            "query_type": "insights",
            "response": response,
            "recommendation": recommendation,
            "financial_data": {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "net_worth": net_worth,
                "total_debt": total_debt,
                "total_investments": total_investments,
                "insights_count": len(insights)
            }
        }
