"""
AI Chat Views for Natural Language Financial Conversations
Handles the three specific query types mentioned in requirements
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .financial_ai_engine import FinancialAIEngine

class AIChatView(APIView):
    """
    Main AI Chat endpoint for natural language financial queries
    """
    permission_classes = [AllowAny]
    
    def __init__(self):
        super().__init__()
        self.ai_engine = FinancialAIEngine()
    
    def post(self, request):
        """Handle natural language queries"""
        try:
            data = request.data
            query = data.get('query', '').strip()
            user_id = data.get('user_id', '')
            
            if not query:
                return Response({
                    'error': 'Query is required',
                    'suggestions': [
                        "Can I afford to take a vacation next month?",
                        "Why did my expenses increase last quarter?",
                        "What's my best option for repaying my loan faster?"
                    ]
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not user_id:
                return Response({
                    'error': 'User ID is required',
                    'suggestions': [
                        "Please provide a valid user_id in your request"
                    ]
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Process the query using AI engine
            result = self.ai_engine.process_query(query, user_id)
            
            return Response({
                'query': query,
                'response': result['response'],
                'recommendation': result['recommendation'],
                'query_type': result['query_type'],
                'financial_data': result['financial_data'],
                'timestamp': self._get_current_timestamp()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print(f"Error processing query: {str(e)}")
            traceback.print_exc()
            return Response({
                'error': f'Error processing query: {str(e)}',
                'query': request.data.get('query', ''),
                'suggestions': [
                    "Try asking about vacation affordability",
                    "Ask about expense analysis", 
                    "Inquire about debt repayment strategies"
                ]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"


class FinancialSummaryView(APIView):
    """
    Get financial summary for context
    """
    permission_classes = [AllowAny]
    
    def __init__(self):
        super().__init__()
        self.ai_engine = FinancialAIEngine()
    
    def get(self, request):
        """Get comprehensive financial summary"""
        try:
            user_id = request.GET.get('user_id', '')
            
            if not user_id:
                return Response({
                    'error': 'User ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            data = self.ai_engine.load_financial_data(user_id)
            
            if not data:
                return Response({
                    'error': 'No financial data available for this user'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Use the totals from the database
            totals = data.get("totals", {})
            
            summary = {
                'user_id': data.get('user_id'),
                'profile': data.get('profile', {}),
                'monthly_income': totals.get('total_income', 0),
                'monthly_expenses': totals.get('total_expenses', 0),
                'net_cash_flow': totals.get('total_income', 0) - totals.get('total_expenses', 0),
                'total_assets': totals.get('total_balance', 0) + totals.get('total_investments', 0),
                'total_liabilities': totals.get('total_debt', 0),
                'net_worth': totals.get('net_worth', 0),
                'total_investments': totals.get('total_investments', 0),
                'timestamp': self._get_current_timestamp()
            }
            
            return Response(summary, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': f'Error generating summary: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
