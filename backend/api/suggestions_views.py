"""
AI-Powered Suggestions Views
Provides actionable insights based on user data and permissions
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import User, Account, Transaction, Budget, Goal, Portfolio, Debt, IncomeSource, UserPermission
from .ml_suggestions_engine import MLSuggestionsEngine
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

class AISuggestionsView(APIView):
    """
    AI-Powered Suggestions endpoint for personalized financial insights with ML
    """
    permission_classes = [AllowAny]
    
    def __init__(self):
        super().__init__()
        self.ml_engine = MLSuggestionsEngine()
    
    def get(self, request):
        """Get AI-powered suggestions based on user data and permissions"""
        try:
            user_id = request.GET.get('user_id', '')
            category = request.GET.get('category', 'all')  # all, debt, account, loan, investment, budget
            use_ml = request.GET.get('use_ml', 'true').lower() == 'true'  # Enable/disable ML features
            
            if not user_id:
                return Response({
                    'error': 'User ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user permissions
            permissions = self._get_user_permissions(user_id)
            
            # Generate suggestions based on category
            suggestions = self._generate_suggestions(user_id, category, permissions, use_ml)
            
            return Response({
                'user_id': user_id,
                'category': category,
                'use_ml': use_ml,
                'suggestions': suggestions,
                'ml_enabled': use_ml,
                'timestamp': datetime.now().isoformat() + "Z"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error generating suggestions: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_user_permissions(self, user_id: str) -> Dict[str, bool]:
        """Get user permissions for data access"""
        try:
            permission = UserPermission.objects(user_id=user_id).first()
            if permission:
                return permission.get_permissions_dict()
            else:
                # Default permissions if none set
                return {
                    'accounts': True,
                    'transactions': True,
                    'budgets': True,
                    'goals': True,
                    'investments': True,
                    'debts': True
                }
        except:
            return {
                'accounts': True,
                'transactions': True,
                'budgets': True,
                'goals': True,
                'investments': True,
                'debts': True
            }
    
    def _generate_suggestions(self, user_id: str, category: str, permissions: Dict[str, bool], use_ml: bool = True) -> List[Dict[str, Any]]:
        """Generate personalized suggestions based on user data with optional ML enhancement"""
        suggestions = []
        
        # Get user data for ML analysis
        user_data = self._get_user_data(user_id, permissions) if use_ml else {}
        
        # Generate ML-powered suggestions if enabled
        if use_ml and user_data:
            ml_suggestions = self.ml_engine.generate_ml_suggestions(user_id, user_data)
            suggestions.extend(ml_suggestions)
        
        # Generate traditional rule-based suggestions
        if category == 'all' or category == 'debt':
            suggestions.extend(self._get_debt_suggestions(user_id, permissions))
        
        if category == 'all' or category == 'account':
            suggestions.extend(self._get_account_suggestions(user_id, permissions))
        
        if category == 'all' or category == 'loan':
            suggestions.extend(self._get_loan_suggestions(user_id, permissions))
        
        if category == 'all' or category == 'investment':
            suggestions.extend(self._get_investment_suggestions(user_id, permissions))
        
        if category == 'all' or category == 'budget':
            suggestions.extend(self._get_budget_suggestions(user_id, permissions))
        
        if category == 'all' or category == 'savings':
            suggestions.extend(self._get_savings_suggestions(user_id, permissions))
        
        if category == 'all' or category == 'spending':
            suggestions.extend(self._get_spending_suggestions(user_id, permissions))
        
        # Remove duplicates and sort by priority
        suggestions = self._deduplicate_and_sort_suggestions(suggestions)
        
        return suggestions
    
    def _get_user_data(self, user_id: str, permissions: Dict[str, bool]) -> Dict[str, Any]:
        """Get user data for ML analysis"""
        user_data = {}
        
        try:
            # Get transactions if permission granted
            if permissions.get('transactions', False):
                transactions = Transaction.objects(user_id=user_id)
                user_data['transactions'] = [
                    {
                        'amount': float(t.amount),
                        'type': t.type,
                        'category': t.category,
                        'date': t.date.isoformat() if t.date else None,
                        'description': t.description or ''
                    }
                    for t in transactions
                ]
            
            # Get debts if permission granted
            if permissions.get('debts', False):
                debts = Debt.objects(user_id=user_id)
                user_data['debts'] = [
                    {
                        'name': d.name,
                        'remaining_amount': float(d.remaining_amount),
                        'interest_rate': float(d.interest_rate),
                        'minimum_payment': float(d.minimum_payment),
                        'type': d.type
                    }
                    for d in debts
                ]
            
            # Get investments if permission granted
            if permissions.get('investments', False):
                investments = Portfolio.objects(user_id=user_id)
                user_data['investments'] = [
                    {
                        'name': inv.name or 'Unknown',
                        'totalValue': float(inv.totalValue) if hasattr(inv, 'totalValue') else 0,
                        'gainLoss': float(inv.gainLoss) if hasattr(inv, 'gainLoss') else 0,
                        'gainLossPercent': float(inv.gainLossPercent) if hasattr(inv, 'gainLossPercent') else 0
                    }
                    for inv in investments
                ]
            
            # Get budgets if permission granted
            if permissions.get('budgets', False):
                budgets = Budget.objects(user_id=user_id)
                user_data['budgets'] = [
                    {
                        'name': b.name,
                        'limit': float(b.limit),
                        'spent': float(b.spent),
                        'remaining': float(b.remaining)
                    }
                    for b in budgets
                ]
            
        except Exception as e:
            print(f"Error getting user data for ML: {str(e)}")
        
        return user_data
    
    def _deduplicate_and_sort_suggestions(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and sort suggestions by priority"""
        # Remove duplicates based on title and type
        seen = set()
        unique_suggestions = []
        
        for suggestion in suggestions:
            key = (suggestion.get('title', ''), suggestion.get('type', ''))
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        # Sort by priority (high -> medium -> low -> info)
        priority_order = {'high': 0, 'medium': 1, 'low': 2, 'info': 3, 'success': 4}
        unique_suggestions.sort(key=lambda x: priority_order.get(x.get('priority', 'info'), 3))
        
        return unique_suggestions
    
    def _get_debt_suggestions(self, user_id: str, permissions: Dict[str, bool]) -> List[Dict[str, Any]]:
        """Generate debt-related suggestions"""
        suggestions = []
        
        if not permissions.get('debts', False):
            return [{
                'type': 'permission_required',
                'title': 'Debt Insights Unavailable',
                'description': 'Please enable debt data access in your AI permissions to get personalized debt suggestions.',
                'priority': 'info',
                'category': 'debt'
            }]
        
        try:
            debts = Debt.objects(user_id=user_id)
            if not debts:
                return [{
                    'type': 'no_debt',
                    'title': '🎉 Congratulations! No Active Debts',
                    'description': 'You currently have no active debts. This is excellent for your financial health!',
                    'priority': 'success',
                    'category': 'debt',
                    'action': 'Consider starting an emergency fund or investment portfolio.'
                }]
            
            total_debt = sum(debt.remaining_amount for debt in debts)
            highest_interest_debt = max(debts, key=lambda d: d.interest_rate)
            
            # Debt optimization suggestions
            suggestions.append({
                'type': 'debt_optimization',
                'title': '💡 Optimize Your Debt Repayment',
                'description': f'Your highest interest debt is {highest_interest_debt.name} at {highest_interest_debt.interest_rate}% APR. Focus extra payments here first.',
                'priority': 'high',
                'category': 'debt',
                'action': f'Pay extra ₹{highest_interest_debt.minimum_payment * 0.5:.0f} monthly towards {highest_interest_debt.name}',
                'savings_potential': f'₹{highest_interest_debt.remaining_amount * 0.1:.0f} in interest savings'
            })
            
            # Debt consolidation suggestion
            if len(debts) > 2:
                suggestions.append({
                    'type': 'debt_consolidation',
                    'title': '🔄 Consider Debt Consolidation',
                    'description': f'You have {len(debts)} active debts totaling ₹{total_debt:,.0f}. Consolidating could simplify payments.',
                    'priority': 'medium',
                    'category': 'debt',
                    'action': 'Research personal loans with lower interest rates for consolidation',
                    'savings_potential': '₹5,000-15,000 annually in interest'
                })
            
        except Exception as e:
            suggestions.append({
                'type': 'error',
                'title': 'Unable to Analyze Debt Data',
                'description': 'There was an issue accessing your debt information.',
                'priority': 'info',
                'category': 'debt'
            })
        
        return suggestions
    
    def _get_account_suggestions(self, user_id: str, permissions: Dict[str, bool]) -> List[Dict[str, Any]]:
        """Generate account-related suggestions"""
        suggestions = []
        
        if not permissions.get('accounts', False):
            return [{
                'type': 'permission_required',
                'title': 'Account Insights Unavailable',
                'description': 'Please enable account data access in your AI permissions to get personalized account suggestions.',
                'priority': 'info',
                'category': 'account'
            }]
        
        try:
            accounts = Account.objects(user_id=user_id)
            if not accounts:
                return [{
                    'type': 'no_accounts',
                    'title': '📱 Set Up Your First Account',
                    'description': 'Start tracking your finances by adding your bank account or wallet.',
                    'priority': 'high',
                    'category': 'account',
                    'action': 'Add your primary bank account to begin financial tracking'
                }]
            
            # Account balance analysis
            low_balance_accounts = [acc for acc in accounts if acc.total_balance < 10000]
            if low_balance_accounts:
                suggestions.append({
                    'type': 'low_balance',
                    'title': '⚠️ Low Account Balances Detected',
                    'description': f'{len(low_balance_accounts)} account(s) have balances below ₹10,000. Consider transferring funds.',
                    'priority': 'high',
                    'category': 'account',
                    'action': 'Review and consolidate low-balance accounts',
                    'accounts': [acc.account_name for acc in low_balance_accounts]
                })
            
            # Multiple accounts suggestion
            if len(accounts) > 3:
                suggestions.append({
                    'type': 'account_consolidation',
                    'title': '🔄 Simplify Your Accounts',
                    'description': f'You have {len(accounts)} accounts. Consider consolidating for easier management.',
                    'priority': 'medium',
                    'category': 'account',
                    'action': 'Review which accounts you actively use and close unused ones'
                })
            
        except Exception as e:
            suggestions.append({
                'type': 'error',
                'title': 'Unable to Analyze Account Data',
                'description': 'There was an issue accessing your account information.',
                'priority': 'info',
                'category': 'account'
            })
        
        return suggestions
    
    def _get_loan_suggestions(self, user_id: str, permissions: Dict[str, bool]) -> List[Dict[str, Any]]:
        """Generate loan-related suggestions"""
        suggestions = []
        
        if not permissions.get('debts', False):
            return [{
                'type': 'permission_required',
                'title': 'Loan Insights Unavailable',
                'description': 'Please enable debt data access in your AI permissions to get personalized loan suggestions.',
                'priority': 'info',
                'category': 'loan'
            }]
        
        try:
            loans = Debt.objects(user_id=user_id, type__in=['Personal Loan', 'Home Loan', 'Auto Loan', 'Student Loan'])
            if not loans:
                return [{
                    'type': 'no_loans',
                    'title': '🏠 Loan Opportunities',
                    'description': 'You have no active loans. Consider if a home loan or personal loan could benefit your financial goals.',
                    'priority': 'low',
                    'category': 'loan',
                    'action': 'Evaluate if loans align with your financial objectives'
                }]
            
            # Loan refinancing suggestions
            high_interest_loans = [loan for loan in loans if loan.interest_rate > 12]
            if high_interest_loans:
                suggestions.append({
                    'type': 'loan_refinancing',
                    'title': '💡 Consider Loan Refinancing',
                    'description': f'You have {len(high_interest_loans)} loan(s) with interest rates above 12%. Refinancing could save money.',
                    'priority': 'high',
                    'category': 'loan',
                    'action': 'Research refinancing options with lower interest rates',
                    'savings_potential': '₹10,000-50,000 annually in interest'
                })
            
        except Exception as e:
            suggestions.append({
                'type': 'error',
                'title': 'Unable to Analyze Loan Data',
                'description': 'There was an issue accessing your loan information.',
                'priority': 'info',
                'category': 'loan'
            })
        
        return suggestions
    
    def _get_investment_suggestions(self, user_id: str, permissions: Dict[str, bool]) -> List[Dict[str, Any]]:
        """Generate investment-related suggestions"""
        suggestions = []
        
        if not permissions.get('investments', False):
            return [{
                'type': 'permission_required',
                'title': 'Investment Insights Unavailable',
                'description': 'Please enable investment data access in your AI permissions to get personalized investment suggestions.',
                'priority': 'info',
                'category': 'investment'
            }]
        
        try:
            investments = Portfolio.objects(user_id=user_id)
            if not investments:
                return [{
                    'type': 'start_investing',
                    'title': '📈 Start Your Investment Journey',
                    'description': 'You have no investments yet. Even small amounts can grow significantly over time.',
                    'priority': 'high',
                    'category': 'investment',
                    'action': 'Consider starting with ₹5,000 monthly in mutual funds or ETFs',
                    'potential_growth': '₹50,000+ in 5 years with 12% returns'
                }]
            
            # Portfolio diversification
            if len(investments) < 3:
                suggestions.append({
                    'type': 'diversification',
                    'title': '🎯 Diversify Your Portfolio',
                    'description': f'You have {len(investments)} investment(s). Diversification reduces risk.',
                    'priority': 'medium',
                    'category': 'investment',
                    'action': 'Consider adding different asset classes (stocks, bonds, REITs)',
                    'risk_reduction': '30-50% lower portfolio volatility'
                })
            
            # Performance analysis
            losing_investments = [inv for inv in investments if inv.gainLoss < 0]
            if losing_investments:
                suggestions.append({
                    'type': 'portfolio_review',
                    'title': '📊 Review Underperforming Investments',
                    'description': f'{len(losing_investments)} investment(s) are currently at a loss. Consider your strategy.',
                    'priority': 'medium',
                    'category': 'investment',
                    'action': 'Review and potentially rebalance your portfolio',
                    'investments': [inv.name for inv in losing_investments[:3]]
                })
            
        except Exception as e:
            suggestions.append({
                'type': 'error',
                'title': 'Unable to Analyze Investment Data',
                'description': 'There was an issue accessing your investment information.',
                'priority': 'info',
                'category': 'investment'
            })
        
        return suggestions
    
    def _get_budget_suggestions(self, user_id: str, permissions: Dict[str, bool]) -> List[Dict[str, Any]]:
        """Generate budget-related suggestions"""
        suggestions = []
        
        if not permissions.get('budgets', False):
            return [{
                'type': 'permission_required',
                'title': 'Budget Insights Unavailable',
                'description': 'Please enable budget data access in your AI permissions to get personalized budget suggestions.',
                'priority': 'info',
                'category': 'budget'
            }]
        
        try:
            budgets = Budget.objects(user_id=user_id)
            if not budgets:
                return [{
                    'type': 'create_budget',
                    'title': '📋 Create Your First Budget',
                    'description': 'Start managing your money better with a monthly budget.',
                    'priority': 'high',
                    'category': 'budget',
                    'action': 'Set up monthly budgets for your main expense categories'
                }]
            
            # Budget overspending analysis
            overspent_budgets = [budget for budget in budgets if budget.spent > budget.limit]
            if overspent_budgets:
                suggestions.append({
                    'type': 'budget_overspend',
                    'title': '⚠️ Budget Overspending Alert',
                    'description': f'{len(overspent_budgets)} budget(s) are over their limits. Review your spending.',
                    'priority': 'high',
                    'category': 'budget',
                    'action': 'Adjust spending or increase budget limits for overspent categories',
                    'budgets': [budget.name for budget in overspent_budgets]
                })
            
        except Exception as e:
            suggestions.append({
                'type': 'error',
                'title': 'Unable to Analyze Budget Data',
                'description': 'There was an issue accessing your budget information.',
                'priority': 'info',
                'category': 'budget'
            })
        
        return suggestions
    
    def _get_savings_suggestions(self, user_id: str, permissions: Dict[str, bool]) -> List[Dict[str, Any]]:
        """Generate savings-related suggestions"""
        suggestions = []
        
        if not permissions.get('accounts', False) or not permissions.get('transactions', False):
            return [{
                'type': 'permission_required',
                'title': 'Savings Insights Unavailable',
                'description': 'Please enable account and transaction data access in your AI permissions to get personalized savings suggestions.',
                'priority': 'info',
                'category': 'savings'
            }]
        
        try:
            # Calculate monthly income and expenses
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_transactions = Transaction.objects(
                user_id=user_id,
                date__gte=thirty_days_ago
            )
            
            monthly_income = sum(t.amount for t in recent_transactions if t.type == 'income')
            monthly_expenses = sum(t.amount for t in recent_transactions if t.type == 'expense')
            monthly_savings = monthly_income - monthly_expenses
            
            if monthly_savings < 0:
                suggestions.append({
                    'type': 'negative_savings',
                    'title': '🚨 Spending More Than You Earn',
                    'description': f'You spent ₹{abs(monthly_savings):,.0f} more than you earned this month. This is unsustainable.',
                    'priority': 'high',
                    'category': 'savings',
                    'action': 'Immediately reduce expenses or increase income',
                    'urgency': 'Critical - Review all expenses'
                })
            elif monthly_savings < monthly_income * 0.1:
                suggestions.append({
                    'type': 'low_savings',
                    'title': '💰 Increase Your Savings Rate',
                    'description': f'You\'re saving only ₹{monthly_savings:,.0f} monthly ({monthly_savings/monthly_income*100:.1f}% of income). Aim for 20%.',
                    'priority': 'medium',
                    'category': 'savings',
                    'action': 'Try to save at least 20% of your monthly income',
                    'target_savings': f'₹{monthly_income * 0.2:,.0f} monthly'
                })
            else:
                suggestions.append({
                    'type': 'good_savings',
                    'title': '🎉 Great Savings Habits!',
                    'description': f'You\'re saving ₹{monthly_savings:,.0f} monthly ({monthly_savings/monthly_income*100:.1f}% of income). Keep it up!',
                    'priority': 'low',
                    'category': 'savings',
                    'action': 'Consider increasing your savings rate or investing the excess'
                })
            
        except Exception as e:
            suggestions.append({
                'type': 'error',
                'title': 'Unable to Analyze Savings Data',
                'description': 'There was an issue accessing your savings information.',
                'priority': 'info',
                'category': 'savings'
            })
        
        return suggestions
    
    def _get_spending_suggestions(self, user_id: str, permissions: Dict[str, bool]) -> List[Dict[str, Any]]:
        """Generate spending-related suggestions"""
        suggestions = []
        
        if not permissions.get('transactions', False):
            return [{
                'type': 'permission_required',
                'title': 'Spending Insights Unavailable',
                'description': 'Please enable transaction data access in your AI permissions to get personalized spending suggestions.',
                'priority': 'info',
                'category': 'spending'
            }]
        
        try:
            # Analyze spending patterns
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_expenses = Transaction.objects(
                user_id=user_id,
                type='expense',
                date__gte=thirty_days_ago
            )
            
            # Category-wise spending analysis
            category_spending = {}
            for expense in recent_expenses:
                category = expense.category
                if category not in category_spending:
                    category_spending[category] = 0
                category_spending[category] += expense.amount
            
            if category_spending:
                highest_spending_category = max(category_spending.items(), key=lambda x: x[1])
                suggestions.append({
                    'type': 'spending_analysis',
                    'title': '📊 Top Spending Category',
                    'description': f'Your highest expense is {highest_spending_category[0]} at ₹{highest_spending_category[1]:,.0f} this month.',
                    'priority': 'medium',
                    'category': 'spending',
                    'action': f'Review {highest_spending_category[0]} expenses for potential savings',
                    'percentage': f'{highest_spending_category[1]/sum(category_spending.values())*100:.1f}% of total spending'
                })
            
        except Exception as e:
            suggestions.append({
                'type': 'error',
                'title': 'Unable to Analyze Spending Data',
                'description': 'There was an issue accessing your spending information.',
                'priority': 'info',
                'category': 'spending'
            })
        
        return suggestions


class SuggestionCategoriesView(APIView):
    """
    Get available suggestion categories
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Get list of available suggestion categories"""
        categories = [
            {
                'id': 'all',
                'name': 'All Suggestions',
                'description': 'Get personalized insights across all financial areas',
                'icon': '🎯',
                'color': 'blue'
            },
            {
                'id': 'debt',
                'name': 'Debt Management',
                'description': 'Optimize your debt repayment strategy',
                'icon': '💳',
                'color': 'red'
            },
            {
                'id': 'account',
                'name': 'Account Management',
                'description': 'Manage and optimize your accounts',
                'icon': '🏦',
                'color': 'green'
            },
            {
                'id': 'loan',
                'name': 'Loan Optimization',
                'description': 'Smart loan management and refinancing',
                'icon': '🏠',
                'color': 'purple'
            },
            {
                'id': 'investment',
                'name': 'Investment Strategy',
                'description': 'Build and optimize your investment portfolio',
                'icon': '📈',
                'color': 'emerald'
            },
            {
                'id': 'budget',
                'name': 'Budget Planning',
                'description': 'Create and manage effective budgets',
                'icon': '📋',
                'color': 'orange'
            },
            {
                'id': 'savings',
                'name': 'Savings Goals',
                'description': 'Increase your savings rate and reach goals',
                'icon': '💰',
                'color': 'yellow'
            },
            {
                'id': 'spending',
                'name': 'Spending Analysis',
                'description': 'Analyze and optimize your spending patterns',
                'icon': '🛒',
                'color': 'pink'
            }
        ]
        
        return Response({
            'categories': categories,
            'timestamp': datetime.now().isoformat() + "Z"
        }, status=status.HTTP_200_OK)
