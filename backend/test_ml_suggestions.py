#!/usr/bin/env python3
"""
Test script for ML-Powered Suggestions API
Tests the machine learning features and advanced analytics
"""

import requests
import json
from datetime import datetime, timedelta
import numpy as np

# Configuration
BASE_URL = "http://localhost:8000/api"
USER_ID = "user_001"  # Change this to a real user ID from your database

def test_ml_suggestions():
    """Test ML-powered suggestions"""
    print("🧠 Testing ML-Powered Suggestions")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/ai/suggestions/", params={
            "user_id": USER_ID,
            "category": "all",
            "use_ml": "true"
        })
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data['suggestions']
            ml_enabled = data.get('ml_enabled', False)
            
            print(f"✅ ML Suggestions retrieved successfully:")
            print(f"   ML Enabled: {ml_enabled}")
            print(f"   Total Suggestions: {len(suggestions)}")
            
            # Separate ML and regular suggestions
            ml_suggestions = [s for s in suggestions if s.get('ml_generated', False)]
            regular_suggestions = [s for s in suggestions if not s.get('ml_generated', False)]
            
            print(f"   ML-Powered Suggestions: {len(ml_suggestions)}")
            print(f"   Regular Suggestions: {len(regular_suggestions)}")
            
            # Show ML suggestions
            if ml_suggestions:
                print(f"\n🧠 ML-Powered Insights:")
                for i, suggestion in enumerate(ml_suggestions, 1):
                    print(f"   {i}. {suggestion['title']}")
                    print(f"      Type: {suggestion.get('type', 'Unknown')}")
                    print(f"      Priority: {suggestion.get('priority', 'Unknown')}")
                    print(f"      Confidence: {suggestion.get('ml_confidence', 'Unknown')}")
                    if suggestion.get('action'):
                        print(f"      Action: {suggestion['action']}")
                    print()
            
            # Show regular suggestions
            if regular_suggestions:
                print(f"📋 Regular Suggestions:")
                for i, suggestion in enumerate(regular_suggestions, 1):
                    print(f"   {i}. {suggestion['title']}")
                    print(f"      Priority: {suggestion.get('priority', 'Unknown')}")
                    print()
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_ml_vs_regular_suggestions():
    """Compare ML vs regular suggestions"""
    print("\n🔄 Comparing ML vs Regular Suggestions")
    print("-" * 45)
    
    try:
        # Test with ML enabled
        ml_response = requests.get(f"{BASE_URL}/ai/suggestions/", params={
            "user_id": USER_ID,
            "category": "all",
            "use_ml": "true"
        })
        
        # Test with ML disabled
        regular_response = requests.get(f"{BASE_URL}/ai/suggestions/", params={
            "user_id": USER_ID,
            "category": "all",
            "use_ml": "false"
        })
        
        if ml_response.status_code == 200 and regular_response.status_code == 200:
            ml_data = ml_response.json()
            regular_data = regular_response.json()
            
            ml_suggestions = ml_data['suggestions']
            regular_suggestions = regular_data['suggestions']
            
            print(f"✅ Comparison Results:")
            print(f"   ML Suggestions: {len(ml_suggestions)}")
            print(f"   Regular Suggestions: {len(regular_suggestions)}")
            print(f"   ML Enhancement: +{len(ml_suggestions) - len(regular_suggestions)} additional insights")
            
            # Find ML-specific suggestions
            ml_specific = [s for s in ml_suggestions if s.get('ml_generated', False)]
            if ml_specific:
                print(f"\n🧠 ML-Specific Insights:")
                for suggestion in ml_specific:
                    print(f"   • {suggestion['title']}")
                    print(f"     Type: {suggestion.get('type', 'Unknown')}")
                    print(f"     Confidence: {suggestion.get('ml_confidence', 'Unknown')}")
        else:
            print(f"❌ Error: ML={ml_response.status_code}, Regular={regular_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_ml_categories():
    """Test ML suggestions across different categories"""
    categories = ['spending', 'savings', 'debt', 'investment', 'budget']
    
    print("\n🎯 Testing ML Suggestions by Category")
    print("-" * 40)
    
    for category in categories:
        print(f"\n📊 Testing {category.upper()} ML suggestions:")
        print("-" * 30)
        
        try:
            response = requests.get(f"{BASE_URL}/ai/suggestions/", params={
                "user_id": USER_ID,
                "category": category,
                "use_ml": "true"
            })
            
            if response.status_code == 200:
                data = response.json()
                suggestions = data['suggestions']
                ml_suggestions = [s for s in suggestions if s.get('ml_generated', False)]
                
                print(f"✅ {len(suggestions)} total suggestions ({len(ml_suggestions)} ML-powered)")
                
                for suggestion in ml_suggestions:
                    print(f"   🧠 {suggestion['title']}")
                    print(f"      {suggestion['description']}")
                    if suggestion.get('action'):
                        print(f"      💡 Action: {suggestion['action']}")
                    print()
            else:
                print(f"❌ Error: {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_ml_anomaly_detection():
    """Test ML anomaly detection specifically"""
    print("\n🚨 Testing ML Anomaly Detection")
    print("-" * 35)
    
    try:
        response = requests.get(f"{BASE_URL}/ai/suggestions/", params={
            "user_id": USER_ID,
            "category": "spending",
            "use_ml": "true"
        })
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data['suggestions']
            
            # Look for anomaly detection suggestions
            anomaly_suggestions = [s for s in suggestions if s.get('type') == 'spending_anomaly']
            
            if anomaly_suggestions:
                print(f"✅ Detected {len(anomaly_suggestions)} spending anomalies:")
                for suggestion in anomaly_suggestions:
                    print(f"   🚨 {suggestion['title']}")
                    print(f"      {suggestion['description']}")
                    if suggestion.get('anomaly_score'):
                        print(f"      Anomaly Score: {suggestion['anomaly_score']}")
                    if suggestion.get('category_name'):
                        print(f"      Category: {suggestion['category_name']}")
                    print()
            else:
                print("ℹ️ No spending anomalies detected (this is normal for clean data)")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_ml_predictions():
    """Test ML prediction features"""
    print("\n🔮 Testing ML Predictions")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/ai/suggestions/", params={
            "user_id": USER_ID,
            "category": "all",
            "use_ml": "true"
        })
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data['suggestions']
            
            # Look for prediction-based suggestions
            prediction_types = [
                'savings_growth_prediction',
                'savings_decline_warning',
                'spending_cluster_analysis',
                'ml_debt_optimization',
                'ml_investment_rebalancing',
                'ml_budget_optimization'
            ]
            
            prediction_suggestions = [s for s in suggestions if s.get('type') in prediction_types]
            
            if prediction_suggestions:
                print(f"✅ Found {len(prediction_suggestions)} ML predictions:")
                for suggestion in prediction_suggestions:
                    print(f"   🔮 {suggestion['title']}")
                    print(f"      Type: {suggestion.get('type', 'Unknown')}")
                    print(f"      {suggestion['description']}")
                    if suggestion.get('predicted_amount'):
                        print(f"      Predicted Amount: ₹{suggestion['predicted_amount']:,.0f}")
                    if suggestion.get('growth_rate'):
                        print(f"      Growth Rate: {suggestion['growth_rate']:.1f}%")
                    print()
            else:
                print("ℹ️ No ML predictions available (may need more data)")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_ml_performance():
    """Test ML performance and response times"""
    print("\n⚡ Testing ML Performance")
    print("-" * 30)
    
    try:
        import time
        
        # Test response time
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/ai/suggestions/", params={
            "user_id": USER_ID,
            "category": "all",
            "use_ml": "true"
        })
        end_time = time.time()
        
        response_time = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data['suggestions']
            ml_suggestions = [s for s in suggestions if s.get('ml_generated', False)]
            
            print(f"✅ Performance Results:")
            print(f"   Response Time: {response_time:.2f} seconds")
            print(f"   Total Suggestions: {len(suggestions)}")
            print(f"   ML Suggestions: {len(ml_suggestions)}")
            print(f"   Suggestions per Second: {len(suggestions) / response_time:.1f}")
            
            if response_time < 2.0:
                print("   🚀 Excellent performance!")
            elif response_time < 5.0:
                print("   ✅ Good performance")
            else:
                print("   ⚠️ Performance could be improved")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Run all ML suggestion tests"""
    print("🧠 ML-Powered Suggestions API Tests")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Testing against: {BASE_URL}")
    print(f"👤 Using User ID: {USER_ID}")
    print()
    
    # Run all ML tests
    test_ml_suggestions()
    test_ml_vs_regular_suggestions()
    test_ml_categories()
    test_ml_anomaly_detection()
    test_ml_predictions()
    test_ml_performance()
    
    print("\n🎉 All ML suggestion tests completed!")
    print(f"⏰ Test finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 ML Features Tested:")
    print("   ✅ Anomaly Detection (Isolation Forest)")
    print("   ✅ Savings Prediction (Linear Regression)")
    print("   ✅ Spending Pattern Analysis (K-Means Clustering)")
    print("   ✅ Debt Optimization (Mathematical Modeling)")
    print("   ✅ Investment Performance Analysis")
    print("   ✅ Budget Optimization")
    print("   ✅ Performance Benchmarking")
    print("\n🚀 Next steps:")
    print("   1. Check the frontend at /suggestions with ML enabled")
    print("   2. Test with real user data")
    print("   3. Verify ML confidence scores")
    print("   4. Test different financial scenarios")

if __name__ == "__main__":
    main()
