"""
Natural Language Interaction Engine
Handles context-aware conversations and intelligent financial queries
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from .models import User, Account, Transaction, Budget, Goal, Portfolio, Debt, UserPermission
from .financial_ai_engine import FinancialAIEngine

class ConversationContext:
    """Maintains conversation context and history"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.conversation_history = []
        self.current_topic = None
        self.last_query_type = None
        self.last_time_period = None
        self.last_category = None
        self.last_amount = None
        self.follow_up_intent = None
        
    def add_interaction(self, user_query: str, ai_response: str, query_type: str = None):
        """Add interaction to conversation history"""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user_query': user_query,
            'ai_response': ai_response,
            'query_type': query_type
        })
        
        # Keep only last 10 interactions to manage context size
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_context_summary(self) -> str:
        """Get a summary of recent conversation context"""
        if not self.conversation_history:
            return "No previous context"
        
        recent = self.conversation_history[-3:]  # Last 3 interactions
        context_parts = []
        
        for interaction in recent:
            context_parts.append(f"User: {interaction['user_query']}")
            context_parts.append(f"Assistant: {interaction['ai_response'][:100]}...")
        
        return "\n".join(context_parts)

class NaturalLanguageEngine:
    """Enhanced natural language processing for financial queries"""
    
    def __init__(self):
        self.ai_engine = FinancialAIEngine()
        self.conversation_contexts = {}  # user_id -> ConversationContext
        
    def _get_or_create_context(self, user_id: str) -> ConversationContext:
        """Get or create conversation context for user"""
        if user_id not in self.conversation_contexts:
            self.conversation_contexts[user_id] = ConversationContext(user_id)
        return self.conversation_contexts[user_id]
    
    def _parse_time_references(self, query: str, context: ConversationContext) -> Dict[str, Any]:
        """Parse time references in natural language"""
        query_lower = query.lower()
        
        # Direct time references
        if 'today' in query_lower:
            return {'period': 'today', 'days': 1}
        elif 'yesterday' in query_lower:
            return {'period': 'yesterday', 'days': 1, 'offset': 1}
        elif 'this week' in query_lower:
            return {'period': 'this_week', 'days': 7}
        elif 'last week' in query_lower:
            return {'period': 'last_week', 'days': 7, 'offset': 7}
        elif 'this month' in query_lower:
            return {'period': 'this_month', 'days': 30}
        elif 'last month' in query_lower:
            return {'period': 'last_month', 'days': 30, 'offset': 30}
        elif 'this year' in query_lower:
            return {'period': 'this_year', 'days': 365}
        elif 'last year' in query_lower:
            return {'period': 'last_year', 'days': 365, 'offset': 365}
        
        # Relative time references
        elif 'last 3 months' in query_lower or 'past 3 months' in query_lower:
            return {'period': 'last_3_months', 'days': 90}
        elif 'last 6 months' in query_lower or 'past 6 months' in query_lower:
            return {'period': 'last_6_months', 'days': 180}
        elif 'last 12 months' in query_lower or 'past year' in query_lower:
            return {'period': 'last_12_months', 'days': 365}
        
        # Number-based references
        elif re.search(r'last (\d+) days?', query_lower):
            match = re.search(r'last (\d+) days?', query_lower)
            days = int(match.group(1))
            return {'period': f'last_{days}_days', 'days': days}
        elif re.search(r'past (\d+) days?', query_lower):
            match = re.search(r'past (\d+) days?', query_lower)
            days = int(match.group(1))
            return {'period': f'past_{days}_days', 'days': days}
        elif re.search(r'(\d+) months? ago', query_lower):
            match = re.search(r'(\d+) months? ago', query_lower)
            months = int(match.group(1))
            return {'period': f'{months}_months_ago', 'days': months * 30, 'offset': months * 30}
        
        # Use context if no specific time mentioned
        elif context.last_time_period:
            return context.last_time_period
        
        # Default to current month
        return {'period': 'this_month', 'days': 30}
    
    def _parse_follow_up_intent(self, query: str, context: ConversationContext) -> str:
        """Detect follow-up intent based on context"""
        query_lower = query.lower()
        
        # Follow-up patterns
        follow_up_patterns = {
            'time_extension': [
                r'what about (.+)',
                r'how about (.+)',
                r'and (.+)',
                r'also (.+)',
                r'(.+) too',
                r'(.+) as well'
            ],
            'comparison': [
                r'compare (.+)',
                r'difference between (.+)',
                r'vs (.+)',
                r'versus (.+)'
            ],
            'clarification': [
                r'what do you mean',
                r'explain (.+)',
                r'tell me more about (.+)',
                r'can you elaborate'
            ],
            'action_request': [
                r'how can i (.+)',
                r'what should i do',
                r'suggest (.+)',
                r'recommend (.+)',
                r'help me (.+)'
            ]
        }
        
        for intent, patterns in follow_up_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        return 'new_query'
    
    def _extract_query_intent(self, query: str) -> Dict[str, Any]:
        """Extract intent and entities from natural language query"""
        query_lower = query.lower()
        
        # Spending queries
        spending_patterns = [
            r'how much did i spend',
            r'what did i spend',
            r'spending on (.+)',
            r'expenses for (.+)',
            r'cost of (.+)',
            r'money spent on (.+)'
        ]
        
        # Income queries
        income_patterns = [
            r'how much did i earn',
            r'what did i earn',
            r'income from (.+)',
            r'money earned',
            r'revenue from (.+)'
        ]
        
        # Balance queries
        balance_patterns = [
            r'what is my balance',
            r'current balance',
            r'how much money do i have',
            r'total balance',
            r'account balance'
        ]
        
        # Budget queries
        budget_patterns = [
            r'budget for (.+)',
            r'budget remaining',
            r'budget status',
            r'budget progress',
            r'how much left in budget'
        ]
        
        # Goal queries
        goal_patterns = [
            r'goal progress',
            r'savings goal',
            r'how close am i to (.+)',
            r'goal completion',
            r'target amount'
        ]
        
        # Debt queries
        debt_patterns = [
            r'debt balance',
            r'how much do i owe',
            r'debt progress',
            r'debt payoff',
            r'remaining debt'
        ]
        
        # Investment queries
        investment_patterns = [
            r'portfolio value',
            r'investment performance',
            r'stock performance',
            r'investment returns',
            r'portfolio balance'
        ]
        
        # Analysis queries
        analysis_patterns = [
            r'spending patterns',
            r'financial trends',
            r'analysis of (.+)',
            r'insights about (.+)',
            r'summary of (.+)'
        ]
        
        # Prediction queries
        prediction_patterns = [
            r'predict (.+)',
            r'forecast (.+)',
            r'future (.+)',
            r'what will happen',
            r'projection for (.+)'
        ]
        
        # Recommendation queries
        recommendation_patterns = [
            r'what should i do',
            r'how can i improve',
            r'suggestions for (.+)',
            r'recommendations',
            r'advice on (.+)'
        ]
        
        # Match patterns
        if any(re.search(pattern, query_lower) for pattern in spending_patterns):
            return {'intent': 'spending_query', 'category': 'expense'}
        elif any(re.search(pattern, query_lower) for pattern in income_patterns):
            return {'intent': 'income_query', 'category': 'income'}
        elif any(re.search(pattern, query_lower) for pattern in balance_patterns):
            return {'intent': 'balance_query', 'category': 'balance'}
        elif any(re.search(pattern, query_lower) for pattern in budget_patterns):
            return {'intent': 'budget_query', 'category': 'budget'}
        elif any(re.search(pattern, query_lower) for pattern in goal_patterns):
            return {'intent': 'goal_query', 'category': 'goal'}
        elif any(re.search(pattern, query_lower) for pattern in debt_patterns):
            return {'intent': 'debt_query', 'category': 'debt'}
        elif any(re.search(pattern, query_lower) for pattern in investment_patterns):
            return {'intent': 'investment_query', 'category': 'investment'}
        elif any(re.search(pattern, query_lower) for pattern in analysis_patterns):
            return {'intent': 'analysis_query', 'category': 'analysis'}
        elif any(re.search(pattern, query_lower) for pattern in prediction_patterns):
            return {'intent': 'prediction_query', 'category': 'prediction'}
        elif any(re.search(pattern, query_lower) for pattern in recommendation_patterns):
            return {'intent': 'recommendation_query', 'category': 'recommendation'}
        else:
            return {'intent': 'general_query', 'category': 'general'}
    
    def _generate_contextual_response(self, query: str, context: ConversationContext, 
                                    query_intent: Dict[str, Any], time_info: Dict[str, Any]) -> str:
        """Generate contextual response based on conversation history"""
        
        # Build context-aware query
        contextual_query = query
        
        # Add time context if this is a follow-up
        if context.last_time_period and 'what about' in query.lower():
            contextual_query = f"{query} for {context.last_time_period.get('period', 'the same period')}"
        
        # Add category context if this is a follow-up
        if context.last_category and 'also' in query.lower():
            contextual_query = f"{query} for {context.last_category}"
        
        return contextual_query
    
    def _generate_suggested_actions(self, query_intent: Dict[str, Any], 
                                  time_info: Dict[str, Any], user_data: Dict[str, Any]) -> List[str]:
        """Generate suggested actions based on query intent"""
        suggestions = []
        
        intent = query_intent.get('intent', 'general_query')
        category = query_intent.get('category', 'general')
        
        if intent == 'spending_query':
            suggestions.extend([
                "💡 Create a budget for this category",
                "📊 View spending trends over time",
                "🎯 Set spending limits",
                "📋 Review recent transactions"
            ])
        elif intent == 'income_query':
            suggestions.extend([
                "💰 Set up income tracking",
                "📈 Analyze income trends",
                "🎯 Create income goals",
                "📊 Compare income vs expenses"
            ])
        elif intent == 'balance_query':
            suggestions.extend([
                "💳 Check all account balances",
                "📊 View balance history",
                "🎯 Set balance goals",
                "💰 Optimize account allocation"
            ])
        elif intent == 'budget_query':
            suggestions.extend([
                "📋 Review budget performance",
                "🎯 Adjust budget limits",
                "📊 Track budget progress",
                "💡 Get budget optimization tips"
            ])
        elif intent == 'goal_query':
            suggestions.extend([
                "🎯 Update goal progress",
                "💰 Increase savings rate",
                "📊 View goal timeline",
                "💡 Get goal achievement tips"
            ])
        elif intent == 'debt_query':
            suggestions.extend([
                "💳 Create debt payoff plan",
                "📊 Analyze debt trends",
                "🎯 Set debt reduction goals",
                "💡 Get debt optimization advice"
            ])
        elif intent == 'investment_query':
            suggestions.extend([
                "📈 Review portfolio performance",
                "🎯 Rebalance investments",
                "📊 Analyze returns",
                "💡 Get investment advice"
            ])
        elif intent == 'analysis_query':
            suggestions.extend([
                "📊 Generate detailed reports",
                "📈 View trend analysis",
                "🎯 Set improvement goals",
                "💡 Get personalized insights"
            ])
        elif intent == 'prediction_query':
            suggestions.extend([
                "🔮 View financial forecasts",
                "📊 Analyze future trends",
                "🎯 Plan for future goals",
                "💡 Get predictive insights"
            ])
        elif intent == 'recommendation_query':
            suggestions.extend([
                "💡 Get personalized recommendations",
                "🎯 Create action plan",
                "📊 Review financial health",
                "🚀 Optimize financial strategy"
            ])
        
        return suggestions[:4]  # Limit to 4 suggestions
    
    def process_natural_language_query(self, user_id: str, query: str) -> Dict[str, Any]:
        """Process natural language query with context awareness"""
        
        # Get conversation context
        context = self._get_or_create_context(user_id)
        
        # Parse query intent
        query_intent = self._extract_query_intent(query)
        
        # Parse time references
        time_info = self._parse_time_references(query, context)
        
        # Detect follow-up intent
        follow_up_intent = self._parse_follow_up_intent(query, context)
        
        # Generate contextual query
        contextual_query = self._generate_contextual_response(query, context, query_intent, time_info)
        
        # Process with AI engine
        try:
            ai_result = self.ai_engine.process_query(contextual_query, user_id)
            
            # Get user data for suggestions
            user_data = self._get_user_data_summary(user_id)
            
            # Generate suggested actions
            suggested_actions = self._generate_suggested_actions(query_intent, time_info, user_data)
            
            # Update context
            context.current_topic = query_intent.get('category')
            context.last_query_type = query_intent.get('intent')
            context.last_time_period = time_info
            context.last_category = query_intent.get('category')
            context.follow_up_intent = follow_up_intent
            
            # Add to conversation history
            context.add_interaction(query, ai_result['response'], query_intent.get('intent'))
            
            return {
                'response': ai_result['response'],
                'recommendation': ai_result.get('recommendation', ''),
                'query_type': query_intent.get('intent'),
                'category': query_intent.get('category'),
                'time_period': time_info.get('period'),
                'follow_up_intent': follow_up_intent,
                'suggested_actions': suggested_actions,
                'context_summary': context.get_context_summary(),
                'conversation_id': f"{user_id}_{len(context.conversation_history)}",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'response': f"I understand you're asking about {query_intent.get('category', 'your finances')}, but I encountered an error processing your request. Please try rephrasing your question.",
                'recommendation': 'Try asking a more specific question about your financial data.',
                'query_type': 'error',
                'category': query_intent.get('category'),
                'time_period': time_info.get('period'),
                'follow_up_intent': 'new_query',
                'suggested_actions': ['🔄 Try rephrasing your question', '📊 Check your data permissions', '💡 Ask a specific financial question'],
                'context_summary': context.get_context_summary(),
                'conversation_id': f"{user_id}_error",
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _get_user_data_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user data for context"""
        try:
            # Get user permissions
            permissions = UserPermission.objects(user_id=user_id).first()
            if not permissions:
                return {'permissions': {}}
            
            user_data = {'permissions': permissions.get_permissions_dict()}
            
            # Get basic counts if permissions allow
            if permissions.transactions_permission:
                transaction_count = Transaction.objects(user_id=user_id).count()
                user_data['transaction_count'] = transaction_count
            
            if permissions.accounts_permission:
                account_count = Account.objects(user_id=user_id).count()
                user_data['account_count'] = account_count
            
            if permissions.budgets_permission:
                budget_count = Budget.objects(user_id=user_id).count()
                user_data['budget_count'] = budget_count
            
            if permissions.goals_permission:
                goal_count = Goal.objects(user_id=user_id).count()
                user_data['goal_count'] = goal_count
            
            if permissions.debts_permission:
                debt_count = Debt.objects(user_id=user_id).count()
                user_data['debt_count'] = debt_count
            
            if permissions.investments_permission:
                investment_count = Portfolio.objects(user_id=user_id).count()
                user_data['investment_count'] = investment_count
            
            return user_data
            
        except Exception as e:
            return {'permissions': {}, 'error': str(e)}
    
    def get_conversation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for user"""
        context = self._get_or_create_context(user_id)
        return context.conversation_history
    
    def clear_conversation_history(self, user_id: str) -> bool:
        """Clear conversation history for user"""
        if user_id in self.conversation_contexts:
            self.conversation_contexts[user_id] = ConversationContext(user_id)
            return True
        return False
