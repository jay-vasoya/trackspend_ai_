"""
API views for managing user permissions for AI assistant data access
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
import traceback

from .models import UserPermission


class UserPermissionView(APIView):
    """View for managing user permissions for AI assistant"""
    
    def get(self, request):
        """Get current user permissions"""
        try:
            user_id = request.GET.get('user_id')
            if not user_id:
                return Response(
                    {"error": "user_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create user permissions
            try:
                permission = UserPermission.objects.get(user_id=user_id)
                created = False
            except UserPermission.DoesNotExist:
                permission = UserPermission(
                    user_id=user_id,
                    accounts_permission=False,
                    transactions_permission=False,
                    budgets_permission=False,
                    goals_permission=False,
                    investments_permission=False,
                    debts_permission=False
                )
                permission.save()
                created = True
            
            return Response({
                "user_id": user_id,
                "permissions": permission.get_permissions_dict(),
                "created": created,
                "message": "Permissions retrieved successfully"
            })
            
        except Exception as e:
            print(f"Error getting user permissions: {str(e)}")
            traceback.print_exc()
            return Response(
                {"error": "Failed to retrieve permissions"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Update user permissions"""
        try:
            user_id = request.data.get('user_id')
            permissions = request.data.get('permissions', {})
            
            if not user_id:
                return Response(
                    {"error": "user_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create user permissions
            try:
                permission = UserPermission.objects.get(user_id=user_id)
                created = False
            except UserPermission.DoesNotExist:
                permission = UserPermission(
                    user_id=user_id,
                    accounts_permission=False,
                    transactions_permission=False,
                    budgets_permission=False,
                    goals_permission=False,
                    investments_permission=False,
                    debts_permission=False
                )
                permission.save()
                created = True
            
            # Update permissions
            permission.update_permissions(permissions)
            
            return Response({
                "user_id": user_id,
                "permissions": permission.get_permissions_dict(),
                "updated": True,
                "message": "Permissions updated successfully"
            })
            
        except Exception as e:
            print(f"Error updating user permissions: {str(e)}")
            traceback.print_exc()
            return Response(
                {"error": "Failed to update permissions"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PermissionStatusView(APIView):
    """View for checking permission status for specific data categories"""
    
    def get(self, request):
        """Check if user has permission for specific data categories"""
        try:
            user_id = request.GET.get('user_id')
            categories = request.GET.getlist('categories')
            
            if not user_id:
                return Response(
                    {"error": "user_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not categories:
                return Response(
                    {"error": "categories parameter is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get user permissions
            try:
                permission = UserPermission.objects.get(user_id=user_id)
            except UserPermission.DoesNotExist:
                # No permissions set, return all False
                return Response({
                    "user_id": user_id,
                    "permissions": {cat: False for cat in categories},
                    "message": "No permissions set for user"
                })
            
            # Check permissions for requested categories
            permission_dict = permission.get_permissions_dict()
            result = {}
            
            for category in categories:
                if category in permission_dict:
                    result[category] = permission_dict[category]
                else:
                    result[category] = False
            
            return Response({
                "user_id": user_id,
                "permissions": result,
                "message": "Permission status retrieved successfully"
            })
            
        except Exception as e:
            print(f"Error checking permission status: {str(e)}")
            traceback.print_exc()
            return Response(
                {"error": "Failed to check permission status"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BulkPermissionView(APIView):
    """View for bulk permission operations"""
    
    def post(self, request):
        """Grant or revoke permissions for multiple categories at once"""
        try:
            user_id = request.data.get('user_id')
            action = request.data.get('action')  # 'grant' or 'revoke'
            categories = request.data.get('categories', [])
            
            if not user_id:
                return Response(
                    {"error": "user_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if action not in ['grant', 'revoke']:
                return Response(
                    {"error": "action must be 'grant' or 'revoke'"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not categories:
                return Response(
                    {"error": "categories list is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create user permissions
            try:
                permission = UserPermission.objects.get(user_id=user_id)
                created = False
            except UserPermission.DoesNotExist:
                permission = UserPermission(
                    user_id=user_id,
                    accounts_permission=False,
                    transactions_permission=False,
                    budgets_permission=False,
                    goals_permission=False,
                    investments_permission=False,
                    debts_permission=False
                )
                permission.save()
                created = True
            
            # Update permissions based on action
            permission_dict = permission.get_permissions_dict()
            new_value = (action == 'grant')
            
            for category in categories:
                if category in permission_dict:
                    if category == 'accounts':
                        permission.accounts_permission = new_value
                    elif category == 'transactions':
                        permission.transactions_permission = new_value
                    elif category == 'budgets':
                        permission.budgets_permission = new_value
                    elif category == 'goals':
                        permission.goals_permission = new_value
                    elif category == 'investments':
                        permission.investments_permission = new_value
                    elif category == 'debts':
                        permission.debts_permission = new_value
            
            permission.save()
            
            return Response({
                "user_id": user_id,
                "action": action,
                "categories": categories,
                "permissions": permission.get_permissions_dict(),
                "message": f"Successfully {action}ed permissions for {len(categories)} categories"
            })
            
        except Exception as e:
            print(f"Error in bulk permission operation: {str(e)}")
            traceback.print_exc()
            return Response(
                {"error": "Failed to perform bulk permission operation"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
