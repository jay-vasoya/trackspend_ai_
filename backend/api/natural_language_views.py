"""
Natural Language Interaction Views
Handles context-aware conversations and intelligent financial queries
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .natural_language_engine import NaturalLanguageEngine
from datetime import datetime
from typing import Dict, List, Any

class NaturalLanguageChatView(APIView):
    """
    Enhanced natural language chat endpoint with context awareness
    """
    permission_classes = [AllowAny]
    
    def __init__(self):
        super().__init__()
        self.nl_engine = NaturalLanguageEngine()
    
    def post(self, request):
        """Process natural language query with context awareness"""
        try:
            data = request.data
            query = data.get('query', '').strip()
            user_id = data.get('user_id', '')
            conversation_id = data.get('conversation_id', '')
            
            if not query:
                return Response({
                    'error': 'Query is required',
                    'suggestions': [
                        "💬 Try asking: 'How much did I spend last month?'",
                        "📊 Ask: 'What's my current balance?'",
                        "🎯 Query: 'Show me my budget progress'",
                        "📈 Ask: 'Predict my future savings'"
                    ]
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not user_id:
                return Response({
                    'error': 'User ID is required',
                    'suggestions': [
                        "🔑 Please provide a valid user ID",
                        "👤 Make sure you're logged in",
                        "🔄 Try refreshing the page"
                    ]
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process natural language query
            result = self.nl_engine.process_natural_language_query(user_id, query)
            
            return Response({
                'query': query,
                'response': result['response'],
                'recommendation': result.get('recommendation', ''),
                'query_type': result.get('query_type', 'general_query'),
                'category': result.get('category', 'general'),
                'time_period': result.get('time_period', 'current'),
                'follow_up_intent': result.get('follow_up_intent', 'new_query'),
                'suggested_actions': result.get('suggested_actions', []),
                'context_summary': result.get('context_summary', ''),
                'conversation_id': result.get('conversation_id', ''),
                'timestamp': result.get('timestamp', datetime.now().isoformat()),
                'natural_language': True,
                'context_aware': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error processing natural language query: {str(e)}',
                'query': request.data.get('query', ''),
                'suggestions': [
                    "🔄 Try rephrasing your question",
                    "💡 Ask a more specific question",
                    "📊 Check your data permissions",
                    "🎯 Try: 'What's my spending this month?'"
                ]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ConversationHistoryView(APIView):
    """
    Get conversation history for context-aware responses
    """
    permission_classes = [AllowAny]
    
    def __init__(self):
        super().__init__()
        self.nl_engine = NaturalLanguageEngine()
    
    def get(self, request):
        """Get conversation history for user"""
        try:
            user_id = request.GET.get('user_id', '')
            
            if not user_id:
                return Response({
                    'error': 'User ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            history = self.nl_engine.get_conversation_history(user_id)
            
            return Response({
                'user_id': user_id,
                'conversation_history': history,
                'total_interactions': len(history),
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error retrieving conversation history: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ClearConversationView(APIView):
    """
    Clear conversation history for fresh start
    """
    permission_classes = [AllowAny]
    
    def __init__(self):
        super().__init__()
        self.nl_engine = NaturalLanguageEngine()
    
    def post(self, request):
        """Clear conversation history for user"""
        try:
            data = request.data
            user_id = data.get('user_id', '')
            
            if not user_id:
                return Response({
                    'error': 'User ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            success = self.nl_engine.clear_conversation_history(user_id)
            
            return Response({
                'user_id': user_id,
                'cleared': success,
                'message': 'Conversation history cleared successfully',
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error clearing conversation history: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ContextAwareSuggestionsView(APIView):
    """
    Get context-aware suggestions based on conversation history
    """
    permission_classes = [AllowAny]
    
    def __init__(self):
        super().__init__()
        self.nl_engine = NaturalLanguageEngine()
    
    def get(self, request):
        """Get context-aware suggestions"""
        try:
            user_id = request.GET.get('user_id', '')
            current_topic = request.GET.get('topic', '')
            
            if not user_id:
                return Response({
                    'error': 'User ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get conversation history
            history = self.nl_engine.get_conversation_history(user_id)
            
            # Generate context-aware suggestions
            suggestions = self._generate_context_suggestions(history, current_topic)
            
            return Response({
                'user_id': user_id,
                'current_topic': current_topic,
                'suggestions': suggestions,
                'conversation_context': len(history) > 0,
                'timestamp': datetime.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error generating context suggestions: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_context_suggestions(self, history: List[Dict[str, Any]], current_topic: str) -> List[str]:
        """Generate suggestions based on conversation context"""
        suggestions = []
        
        if not history:
            # No history - provide general suggestions
            suggestions = [
                "💬 Ask: 'How much did I spend last month?'",
                "📊 Query: 'What's my current balance?'",
                "🎯 Ask: 'Show me my budget progress'",
                "📈 Question: 'Predict my future savings'",
                "💳 Ask: 'What are my recent transactions?'",
                "🏦 Query: 'How are my investments performing?'"
            ]
        else:
            # Analyze recent conversation
            recent_topics = [interaction.get('query_type', '') for interaction in history[-3:]]
            
            if 'spending_query' in recent_topics:
                suggestions.extend([
                    "💡 Ask: 'What about last 3 months?'",
                    "📊 Query: 'Show me spending by category'",
                    "🎯 Ask: 'How can I reduce expenses?'",
                    "📈 Question: 'What's my spending trend?'"
                ])
            
            if 'income_query' in recent_topics:
                suggestions.extend([
                    "💰 Ask: 'What about my total income?'",
                    "📊 Query: 'Compare income vs expenses'",
                    "🎯 Ask: 'How can I increase income?'",
                    "📈 Question: 'What's my income trend?'"
                ])
            
            if 'balance_query' in recent_topics:
                suggestions.extend([
                    "💳 Ask: 'What about my savings account?'",
                    "📊 Query: 'Show me balance history'",
                    "🎯 Ask: 'How can I grow my balance?'",
                    "📈 Question: 'What's my balance trend?'"
                ])
            
            if 'budget_query' in recent_topics:
                suggestions.extend([
                    "📋 Ask: 'What about other budgets?'",
                    "📊 Query: 'Show me budget performance'",
                    "🎯 Ask: 'How can I optimize budgets?'",
                    "📈 Question: 'What's my budget trend?'"
                ])
            
            if 'goal_query' in recent_topics:
                suggestions.extend([
                    "🎯 Ask: 'What about my other goals?'",
                    "📊 Query: 'Show me goal progress'",
                    "💰 Ask: 'How can I reach goals faster?'",
                    "📈 Question: 'What's my goal timeline?'"
                ])
            
            if 'debt_query' in recent_topics:
                suggestions.extend([
                    "💳 Ask: 'What about my other debts?'",
                    "📊 Query: 'Show me debt payoff plan'",
                    "🎯 Ask: 'How can I pay off debt faster?'",
                    "📈 Question: 'What's my debt trend?'"
                ])
            
            if 'investment_query' in recent_topics:
                suggestions.extend([
                    "📈 Ask: 'What about my portfolio performance?'",
                    "📊 Query: 'Show me investment returns'",
                    "🎯 Ask: 'How can I optimize investments?'",
                    "📈 Question: 'What's my investment trend?'"
                ])
            
            # Add general follow-up suggestions
            suggestions.extend([
                "🔄 Ask: 'What about the last 3 months?'",
                "📊 Query: 'Show me a summary'",
                "🎯 Ask: 'Give me recommendations'",
                "💡 Question: 'What should I do next?'"
            ])
        
        # Remove duplicates and limit to 6 suggestions
        unique_suggestions = list(dict.fromkeys(suggestions))
        return unique_suggestions[:6]
