#!/usr/bin/env python3
"""
Test script to check database connection and UserPermission model
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'item_service.settings')
django.setup()

from api.models import UserPermission

def test_database_connection():
    """Test database connection and UserPermission model"""
    print("🔍 Testing database connection...")
    
    try:
        # Test creating a UserPermission
        permission = UserPermission(
            user_id="test_user_001",
            accounts_permission=True,
            transactions_permission=False
        )
        permission.save()
        print("✅ UserPermission model works - created test permission")
        
        # Test retrieving the permission
        retrieved = UserPermission.objects.get(user_id="test_user_001")
        print(f"✅ UserPermission retrieval works - found: {retrieved.get_permissions_dict()}")
        
        # Clean up
        retrieved.delete()
        print("✅ UserPermission deletion works - cleaned up test data")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_database_connection()
