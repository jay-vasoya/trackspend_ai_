#!/usr/bin/env python3
"""
Test script for user permission system
Tests granting/revoking permissions and AI engine respect for permissions
"""

import os
import sys
import django
import requests
import json

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'item_service.settings')
django.setup()

# Test configuration
API_BASE = "http://localhost:8000/api"
USER_ID = "user_001"  # Change this to test with different users

def test_permission_endpoints():
    """Test all permission management endpoints"""
    
    print("🔐 Testing User Permission System")
    print("=" * 50)
    
    # Test 1: Get initial permissions (should create default permissions)
    print("\n1. Testing GET permissions (initial state)")
    try:
        response = requests.get(f"{API_BASE}/permissions/?user_id={USER_ID}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Initial permissions: {data['permissions']}")
            print(f"📊 Created: {data['created']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 2: Update permissions (grant some permissions)
    print("\n2. Testing POST permissions (grant accounts and transactions)")
    try:
        new_permissions = {
            "accounts": True,
            "transactions": True,
            "budgets": False,
            "goals": False,
            "investments": False,
            "debts": False
        }
        
        response = requests.post(
            f"{API_BASE}/permissions/",
            json={
                "user_id": USER_ID,
                "permissions": new_permissions
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Updated permissions: {data['permissions']}")
            print(f"📊 Updated: {data['updated']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 3: Check permission status for specific categories
    print("\n3. Testing permission status check")
    try:
        response = requests.get(
            f"{API_BASE}/permissions/status/",
            params={
                "user_id": USER_ID,
                "categories": ["accounts", "transactions", "budgets"]
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Permission status: {data['permissions']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 4: Bulk grant permissions
    print("\n4. Testing bulk permission grant")
    try:
        response = requests.post(
            f"{API_BASE}/permissions/bulk/",
            json={
                "user_id": USER_ID,
                "action": "grant",
                "categories": ["budgets", "goals"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bulk grant result: {data['permissions']}")
            print(f"📊 Action: {data['action']}, Categories: {data['categories']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 5: Bulk revoke permissions
    print("\n5. Testing bulk permission revoke")
    try:
        response = requests.post(
            f"{API_BASE}/permissions/bulk/",
            json={
                "user_id": USER_ID,
                "action": "revoke",
                "categories": ["accounts"]
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Bulk revoke result: {data['permissions']}")
            print(f"📊 Action: {data['action']}, Categories: {data['categories']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 6: Final permission state
    print("\n6. Testing final permission state")
    try:
        response = requests.get(f"{API_BASE}/permissions/?user_id={USER_ID}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Final permissions: {data['permissions']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

def test_ai_with_permissions():
    """Test AI engine behavior with different permission states"""
    
    print("\n" + "=" * 50)
    print("🤖 Testing AI Engine with Permissions")
    print("=" * 50)
    
    # Test queries that should be affected by permissions
    test_queries = [
        {
            "name": "Balance Query (requires accounts permission)",
            "query": "What's my current balance?",
            "required_permission": "accounts"
        },
        {
            "name": "Income Query (requires transactions permission)",
            "query": "What's my income last month?",
            "required_permission": "transactions"
        },
        {
            "name": "Budget Query (requires budgets permission)",
            "query": "How are my budgets doing?",
            "required_permission": "budgets"
        },
        {
            "name": "Debt Query (requires debts permission)",
            "query": "How can I optimize my debt repayment?",
            "required_permission": "debts"
        }
    ]
    
    for test in test_queries:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"Query: '{test['query']}'")
        print(f"Required permission: {test['required_permission']}")
        
        try:
            response = requests.post(
                f"{API_BASE}/ai/chat/",
                json={
                    "query": test["query"],
                    "user_id": USER_ID
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                
                # Check if response indicates permission issue
                if "permission" in response_text.lower() or "access" in response_text.lower():
                    print(f"✅ AI correctly respects permissions - response indicates permission issue")
                else:
                    print(f"📊 AI response: {response_text[:100]}...")
                
                print(f"💡 Recommendation: {data.get('recommendation', '')[:100]}...")
                
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def test_permission_edge_cases():
    """Test edge cases for permission system"""
    
    print("\n" + "=" * 50)
    print("🧪 Testing Permission Edge Cases")
    print("=" * 50)
    
    # Test 1: Non-existent user
    print("\n1. Testing with non-existent user")
    try:
        response = requests.get(f"{API_BASE}/permissions/?user_id=nonexistent_user")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Non-existent user handled: {data['permissions']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 2: Invalid permission categories
    print("\n2. Testing with invalid permission categories")
    try:
        response = requests.post(
            f"{API_BASE}/permissions/",
            json={
                "user_id": USER_ID,
                "permissions": {
                    "invalid_category": True,
                    "accounts": True
                }
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Invalid categories handled: {data['permissions']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
    
    # Test 3: Empty categories list
    print("\n3. Testing with empty categories list")
    try:
        response = requests.post(
            f"{API_BASE}/permissions/bulk/",
            json={
                "user_id": USER_ID,
                "action": "grant",
                "categories": []
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 400:
            print(f"✅ Empty categories list correctly rejected")
        else:
            print(f"❌ Should have been rejected: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting User Permission System Testing")
    print("Make sure your Django server is running on localhost:8000")
    print("=" * 60)
    
    # Test permission endpoints
    test_permission_endpoints()
    
    # Test AI engine with permissions
    test_ai_with_permissions()
    
    # Test edge cases
    test_permission_edge_cases()
    
    print("\n🎉 All permission tests completed!")
    print("Check the results above to verify the permission system is working correctly.")
