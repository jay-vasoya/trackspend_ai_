#!/usr/bin/env python3
"""
Test script to test the permission endpoint directly
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'item_service.settings')
django.setup()

from api.permission_views import UserPermissionView
from django.test import RequestFactory
from django.http import QueryDict

def test_permission_endpoint():
    """Test the permission endpoint directly"""
    print("🔍 Testing permission endpoint...")
    
    try:
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/api/permissions/?user_id=user_001')
        
        # Create the view instance
        view = UserPermissionView()
        view.request = request
        
        # Call the get method
        response = view.get(request)
        
        print(f"✅ Permission endpoint works - Status: {response.status_code}")
        print(f"📊 Response data: {response.data}")
        
        return True
        
    except Exception as e:
        print(f"❌ Permission endpoint error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_permission_endpoint()
