#!/usr/bin/env python3
"""
Test script for AI-Powered Suggestions API
Tests the personalized financial suggestions feature
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
USER_ID = "user_001"  # Change this to a real user ID from your database

def test_suggestion_categories():
    """Test the suggestion categories endpoint"""
    print("📋 Testing Suggestion Categories")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/ai/suggestions/categories/")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Categories retrieved successfully:")
            for category in data['categories']:
                print(f"   {category['icon']} {category['name']}: {category['description']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_all_suggestions():
    """Test getting all suggestions"""
    print("\n🎯 Testing All Suggestions")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/ai/suggestions/", params={
            "user_id": USER_ID,
            "category": "all"
        })
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data['suggestions']
            print(f"✅ Retrieved {len(suggestions)} suggestions:")
            
            # Group by category
            categories = {}
            for suggestion in suggestions:
                category = suggestion.get('category', 'other')
                if category not in categories:
                    categories[category] = []
                categories[category].append(suggestion)
            
            for category, category_suggestions in categories.items():
                print(f"\n📊 {category.upper()} ({len(category_suggestions)} suggestions):")
                for suggestion in category_suggestions:
                    priority_icon = "🔴" if suggestion['priority'] == 'high' else "🟡" if suggestion['priority'] == 'medium' else "🟢"
                    print(f"   {priority_icon} {suggestion['title']}")
                    print(f"      {suggestion['description']}")
                    if suggestion.get('action'):
                        print(f"      💡 Action: {suggestion['action']}")
                    if suggestion.get('savings_potential'):
                        print(f"      💰 Savings: {suggestion['savings_potential']}")
                    print()
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_category_specific_suggestions():
    """Test getting suggestions for specific categories"""
    categories = ['debt', 'account', 'investment', 'budget', 'savings']
    
    print("\n🔍 Testing Category-Specific Suggestions")
    print("-" * 45)
    
    for category in categories:
        print(f"\n📋 Testing {category.upper()} suggestions:")
        print("-" * 25)
        
        try:
            response = requests.get(f"{BASE_URL}/ai/suggestions/", params={
                "user_id": USER_ID,
                "category": category
            })
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data['suggestions']
                print(f"✅ Retrieved {len(suggestions)} {category} suggestions:")
                
                for suggestion in suggestions:
                    priority_icon = "🔴" if suggestion['priority'] == 'high' else "🟡" if suggestion['priority'] == 'medium' else "🟢"
                    print(f"   {priority_icon} {suggestion['title']}")
                    print(f"      {suggestion['description']}")
                    if suggestion.get('action'):
                        print(f"      💡 Action: {suggestion['action']}")
                    print()
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_permission_based_suggestions():
    """Test suggestions with different permission settings"""
    print("\n🔒 Testing Permission-Based Suggestions")
    print("-" * 40)
    
    # Test with no user ID
    print("Testing with no user ID:")
    try:
        response = requests.get(f"{BASE_URL}/ai/suggestions/", params={
            "category": "all"
        })
        
        if response.status_code == 400:
            print("✅ Correctly requires user ID")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test with invalid user ID
    print("\nTesting with invalid user ID:")
    try:
        response = requests.get(f"{BASE_URL}/ai/suggestions/", params={
            "user_id": "invalid_user",
            "category": "all"
        })
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data['suggestions']
            print(f"✅ Retrieved {len(suggestions)} suggestions for invalid user")
            # Should show permission required messages
            permission_required = [s for s in suggestions if s.get('type') == 'permission_required']
            if permission_required:
                print("✅ Correctly shows permission required messages")
            else:
                print("⚠️ No permission required messages found")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_suggestion_priorities():
    """Test suggestion priority levels"""
    print("\n⚡ Testing Suggestion Priorities")
    print("-" * 35)
    
    try:
        response = requests.get(f"{BASE_URL}/ai/suggestions/", params={
            "user_id": USER_ID,
            "category": "all"
        })
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data['suggestions']
            
            priorities = {}
            for suggestion in suggestions:
                priority = suggestion.get('priority', 'unknown')
                if priority not in priorities:
                    priorities[priority] = []
                priorities[priority].append(suggestion)
            
            print("Priority distribution:")
            for priority, priority_suggestions in priorities.items():
                icon = "🔴" if priority == 'high' else "🟡" if priority == 'medium' else "🟢" if priority == 'low' else "ℹ️"
                print(f"   {icon} {priority.upper()}: {len(priority_suggestions)} suggestions")
                
                # Show examples
                for suggestion in priority_suggestions[:2]:  # Show first 2 examples
                    print(f"      - {suggestion['title']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all suggestion tests"""
    print("🤖 AI-Powered Suggestions API Tests")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Testing against: {BASE_URL}")
    print(f"👤 Using User ID: {USER_ID}")
    print()
    
    # Run all tests
    test_suggestion_categories()
    test_all_suggestions()
    test_category_specific_suggestions()
    test_permission_based_suggestions()
    test_suggestion_priorities()
    
    print("\n🎉 All suggestion tests completed!")
    print(f"⏰ Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 Next steps:")
    print("   1. Check the frontend at /suggestions")
    print("   2. Test with real user data")
    print("   3. Verify permission controls work")
    print("   4. Test different financial scenarios")

if __name__ == "__main__":
    main()
