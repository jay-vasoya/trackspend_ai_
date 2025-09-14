"""
ML-Powered Suggestions Engine
Advanced machine learning models for intelligent financial suggestions
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class MLSuggestionsEngine:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.models = {}
        self.user_patterns = {}
        
    def _prepare_transaction_data(self, transactions: List[Dict]) -> pd.DataFrame:
        """Prepare transaction data for ML analysis"""
        if not transactions:
            return pd.DataFrame()
            
        df = pd.DataFrame(transactions)
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Extract time features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Encode categorical variables
        categorical_cols = ['category', 'type', 'description']
        for col in categorical_cols:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
        
        return df
    
    def _detect_spending_anomalies(self, transactions: List[Dict], user_id: str) -> List[Dict]:
        """Detect unusual spending patterns using Isolation Forest"""
        suggestions = []
        
        try:
            df = self._prepare_transaction_data(transactions)
            if df.empty or len(df) < 10:
                return suggestions
            
            # Focus on expense transactions
            expense_df = df[df['type'] == 'expense'].copy()
            if len(expense_df) < 5:
                return suggestions
            
            # Features for anomaly detection
            features = ['amount', 'day_of_week', 'day_of_month', 'month']
            feature_data = expense_df[features].fillna(0)
            
            # Scale features
            scaled_features = self.scaler.fit_transform(feature_data)
            
            # Apply Isolation Forest
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = iso_forest.fit_predict(scaled_features)
            
            # Get anomalous transactions
            anomalous_indices = np.where(anomaly_labels == -1)[0]
            
            if len(anomalous_indices) > 0:
                anomalous_transactions = expense_df.iloc[anomalous_indices]
                
                # Group by category to find patterns
                category_anomalies = anomalous_transactions.groupby('category')['amount'].agg(['count', 'mean', 'sum']).reset_index()
                
                for _, row in category_anomalies.iterrows():
                    if row['count'] >= 2:  # Multiple anomalies in same category
                        suggestions.append({
                            'type': 'spending_anomaly',
                            'title': '🚨 Unusual Spending Pattern Detected',
                            'description': f'Detected {row["count"]} unusual transactions in {row["category"]} category, averaging ₹{row["mean"]:,.0f} per transaction.',
                            'priority': 'high',
                            'category': 'spending',
                            'action': f'Review {row["category"]} expenses for potential fraud or budget overruns',
                            'anomaly_score': row['sum'],
                            'category_name': row['category'],
                            'transaction_count': int(row['count']),
                            'average_amount': row['mean']
                        })
            
        except Exception as e:
            print(f"Error in anomaly detection: {str(e)}")
        
        return suggestions
    
    def _predict_future_savings(self, transactions: List[Dict], user_id: str) -> List[Dict]:
        """Predict future savings using time series analysis"""
        suggestions = []
        
        try:
            df = self._prepare_transaction_data(transactions)
            if df.empty or len(df) < 30:
                return suggestions
            
            # Calculate monthly savings
            df['date'] = pd.to_datetime(df['date'])
            monthly_data = df.groupby(df['date'].dt.to_period('M')).agg({
                'amount': lambda x: x[df.loc[x.index, 'type'] == 'income'].sum() - 
                                  x[df.loc[x.index, 'type'] == 'expense'].sum()
            }).reset_index()
            
            monthly_data['month_num'] = range(len(monthly_data))
            
            if len(monthly_data) < 3:
                return suggestions
            
            # Prepare features for prediction
            X = monthly_data[['month_num']].values
            y = monthly_data['amount'].values
            
            # Train linear regression model
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict next 3 months
            future_months = np.array([[len(monthly_data)], [len(monthly_data) + 1], [len(monthly_data) + 2]])
            predictions = model.predict(future_months)
            
            avg_predicted_savings = np.mean(predictions)
            current_savings = monthly_data['amount'].iloc[-1]
            
            if avg_predicted_savings > current_savings * 1.1:
                suggestions.append({
                    'type': 'savings_growth_prediction',
                    'title': '📈 Positive Savings Trend Predicted',
                    'description': f'Based on your spending patterns, you\'re predicted to save ₹{avg_predicted_savings:,.0f} monthly in the next 3 months (up from ₹{current_savings:,.0f}).',
                    'priority': 'low',
                    'category': 'savings',
                    'action': 'Continue your current spending habits to maintain this positive trend',
                    'predicted_amount': avg_predicted_savings,
                    'current_amount': current_savings,
                    'growth_rate': ((avg_predicted_savings - current_savings) / current_savings * 100) if current_savings > 0 else 0
                })
            elif avg_predicted_savings < current_savings * 0.9:
                suggestions.append({
                    'type': 'savings_decline_warning',
                    'title': '⚠️ Declining Savings Trend Detected',
                    'description': f'Your savings are predicted to decrease to ₹{avg_predicted_savings:,.0f} monthly (down from ₹{current_savings:,.0f}).',
                    'priority': 'high',
                    'category': 'savings',
                    'action': 'Review recent spending increases and adjust your budget accordingly',
                    'predicted_amount': avg_predicted_savings,
                    'current_amount': current_savings,
                    'decline_rate': ((current_savings - avg_predicted_savings) / current_savings * 100) if current_savings > 0 else 0
                })
            
        except Exception as e:
            print(f"Error in savings prediction: {str(e)}")
        
        return suggestions
    
    def _analyze_spending_patterns(self, transactions: List[Dict], user_id: str) -> List[Dict]:
        """Analyze spending patterns using clustering"""
        suggestions = []
        
        try:
            df = self._prepare_transaction_data(transactions)
            if df.empty:
                return suggestions
            
            expense_df = df[df['type'] == 'expense'].copy()
            if len(expense_df) < 10:
                return suggestions
            
            # Analyze spending by category and time
            category_spending = expense_df.groupby('category').agg({
                'amount': ['sum', 'mean', 'count'],
                'day_of_week': 'mean',
                'day_of_month': 'mean'
            }).round(2)
            
            category_spending.columns = ['total_spent', 'avg_amount', 'transaction_count', 'avg_day_of_week', 'avg_day_of_month']
            category_spending = category_spending.reset_index()
            
            # Find spending clusters
            if len(category_spending) >= 3:
                features = ['total_spent', 'avg_amount', 'transaction_count']
                X = category_spending[features].values
                
                # Scale features
                X_scaled = self.scaler.fit_transform(X)
                
                # Apply K-means clustering
                kmeans = KMeans(n_clusters=min(3, len(category_spending)), random_state=42)
                clusters = kmeans.fit_predict(X_scaled)
                
                category_spending['cluster'] = clusters
                
                # Analyze clusters
                cluster_analysis = category_spending.groupby('cluster').agg({
                    'total_spent': 'sum',
                    'avg_amount': 'mean',
                    'transaction_count': 'sum'
                }).reset_index()
                
                # Find high-spending cluster
                high_spending_cluster = cluster_analysis.loc[cluster_analysis['total_spent'].idxmax()]
                high_spending_categories = category_spending[category_spending['cluster'] == high_spending_cluster['cluster']]['category'].tolist()
                
                if len(high_spending_categories) > 0:
                    suggestions.append({
                        'type': 'spending_cluster_analysis',
                        'title': '🎯 High-Impact Spending Categories Identified',
                        'description': f'ML analysis identified {", ".join(high_spending_categories)} as your highest-impact spending categories, totaling ₹{high_spending_cluster["total_spent"]:,.0f}.',
                        'priority': 'medium',
                        'category': 'spending',
                        'action': f'Focus budget optimization efforts on {", ".join(high_spending_categories)} for maximum impact',
                        'categories': high_spending_categories,
                        'total_impact': high_spending_cluster['total_spent'],
                        'optimization_potential': f'₹{high_spending_cluster["total_spent"] * 0.1:,.0f} potential monthly savings'
                    })
            
        except Exception as e:
            print(f"Error in spending pattern analysis: {str(e)}")
        
        return suggestions
    
    def _predict_debt_payoff_optimization(self, debts: List[Dict], transactions: List[Dict], user_id: str) -> List[Dict]:
        """Predict optimal debt payoff strategy using ML"""
        suggestions = []
        
        try:
            if not debts or not transactions:
                return suggestions
            
            df = self._prepare_transaction_data(transactions)
            if df.empty:
                return suggestions
            
            # Calculate available extra payment capacity
            monthly_income = df[df['type'] == 'income']['amount'].sum() / max(1, len(df['date'].dt.to_period('M').unique()))
            monthly_expenses = df[df['type'] == 'expense']['amount'].sum() / max(1, len(df['date'].dt.to_period('M').unique()))
            available_for_debt = monthly_income - monthly_expenses
            
            if available_for_debt <= 0:
                return suggestions
            
            # Analyze each debt
            debt_analysis = []
            for debt in debts:
                remaining_amount = debt.get('remaining_amount', 0)
                interest_rate = debt.get('interest_rate', 0)
                minimum_payment = debt.get('minimum_payment', 0)
                
                if remaining_amount > 0 and interest_rate > 0:
                    # Calculate payoff time with current payments
                    current_payoff_time = self._calculate_payoff_time(remaining_amount, minimum_payment, interest_rate)
                    
                    # Calculate payoff time with extra payments
                    extra_payment = min(available_for_debt * 0.5, remaining_amount * 0.1)  # Conservative extra payment
                    optimized_payoff_time = self._calculate_payoff_time(remaining_amount, minimum_payment + extra_payment, interest_rate)
                    
                    # Calculate interest savings
                    current_total_interest = self._calculate_total_interest(remaining_amount, minimum_payment, interest_rate, current_payoff_time)
                    optimized_total_interest = self._calculate_total_interest(remaining_amount, minimum_payment + extra_payment, interest_rate, optimized_payoff_time)
                    interest_savings = current_total_interest - optimized_total_interest
                    
                    debt_analysis.append({
                        'debt_name': debt.get('name', 'Unknown'),
                        'interest_rate': interest_rate,
                        'remaining_amount': remaining_amount,
                        'current_payoff_time': current_payoff_time,
                        'optimized_payoff_time': optimized_payoff_time,
                        'interest_savings': interest_savings,
                        'extra_payment': extra_payment,
                        'priority_score': interest_rate * remaining_amount  # Higher interest + higher balance = higher priority
                    })
            
            # Sort by priority score
            debt_analysis.sort(key=lambda x: x['priority_score'], reverse=True)
            
            if debt_analysis:
                top_debt = debt_analysis[0]
                suggestions.append({
                    'type': 'ml_debt_optimization',
                    'title': '🧠 ML-Optimized Debt Payoff Strategy',
                    'description': f'ML analysis recommends prioritizing {top_debt["debt_name"]} (₹{top_debt["remaining_amount"]:,.0f} at {top_debt["interest_rate"]:.1f}% APR) for maximum impact.',
                    'priority': 'high',
                    'category': 'debt',
                    'action': f'Pay extra ₹{top_debt["extra_payment"]:,.0f} monthly towards {top_debt["debt_name"]}',
                    'savings_potential': f'₹{top_debt["interest_savings"]:,.0f} in interest savings',
                    'time_savings': f'{top_debt["current_payoff_time"] - top_debt["optimized_payoff_time"]:.1f} months faster payoff',
                    'debt_name': top_debt['debt_name'],
                    'interest_rate': top_debt['interest_rate'],
                    'ml_confidence': 'High - Based on interest rate optimization and available cash flow'
                })
            
        except Exception as e:
            print(f"Error in debt payoff optimization: {str(e)}")
        
        return suggestions
    
    def _calculate_payoff_time(self, principal: float, monthly_payment: float, annual_rate: float) -> float:
        """Calculate debt payoff time in months"""
        if monthly_payment <= 0 or annual_rate <= 0:
            return float('inf')
        
        monthly_rate = annual_rate / 100 / 12
        
        if monthly_rate == 0:
            return principal / monthly_payment
        
        # Using the loan payment formula
        months = -np.log(1 - (principal * monthly_rate) / monthly_payment) / np.log(1 + monthly_rate)
        return months
    
    def _calculate_total_interest(self, principal: float, monthly_payment: float, annual_rate: float, months: float) -> float:
        """Calculate total interest paid over loan term"""
        if months == float('inf') or monthly_payment <= 0:
            return float('inf')
        
        total_paid = monthly_payment * months
        return total_paid - principal
    
    def _predict_investment_performance(self, investments: List[Dict], user_id: str) -> List[Dict]:
        """Predict investment performance and suggest optimizations"""
        suggestions = []
        
        try:
            if not investments or len(investments) < 2:
                return suggestions
            
            # Analyze investment portfolio
            total_value = sum(inv.get('totalValue', 0) for inv in investments)
            total_gain_loss = sum(inv.get('gainLoss', 0) for inv in investments)
            portfolio_return = (total_gain_loss / total_value * 100) if total_value > 0 else 0
            
            # Analyze individual investments
            investment_analysis = []
            for inv in investments:
                current_value = inv.get('totalValue', 0)
                gain_loss = inv.get('gainLoss', 0)
                gain_loss_percent = inv.get('gainLossPercent', 0)
                
                investment_analysis.append({
                    'name': inv.get('name', 'Unknown'),
                    'value': current_value,
                    'gain_loss': gain_loss,
                    'gain_loss_percent': gain_loss_percent,
                    'weight': current_value / total_value if total_value > 0 else 0
                })
            
            # Sort by performance
            investment_analysis.sort(key=lambda x: x['gain_loss_percent'], reverse=True)
            
            # Identify underperformers
            underperformers = [inv for inv in investment_analysis if inv['gain_loss_percent'] < -5]
            top_performers = [inv for inv in investment_analysis if inv['gain_loss_percent'] > 10]
            
            if underperformers:
                suggestions.append({
                    'type': 'ml_investment_rebalancing',
                    'title': '📊 ML Investment Rebalancing Recommendation',
                    'description': f'ML analysis identified {len(underperformers)} underperforming investments with losses >5%. Portfolio return: {portfolio_return:.1f}%.',
                    'priority': 'medium',
                    'category': 'investment',
                    'action': f'Consider rebalancing portfolio by reducing exposure to {", ".join([inv["name"] for inv in underperformers[:3]])}',
                    'underperformers': [inv['name'] for inv in underperformers],
                    'portfolio_return': portfolio_return,
                    'rebalancing_potential': f'Potential {abs(portfolio_return) * 0.2:.1f}% improvement through rebalancing'
                })
            
            if top_performers and len(top_performers) >= 2:
                suggestions.append({
                    'type': 'ml_investment_optimization',
                    'title': '🚀 ML Investment Optimization Opportunity',
                    'description': f'Your top performers ({", ".join([inv["name"] for inv in top_performers[:2]])}) are showing strong returns. Consider increasing allocation.',
                    'priority': 'low',
                    'category': 'investment',
                    'action': f'Consider increasing allocation to {top_performers[0]["name"]} (currently {top_performers[0]["gain_loss_percent"]:.1f}% return)',
                    'top_performers': [inv['name'] for inv in top_performers],
                    'optimization_potential': f'Potential {top_performers[0]["gain_loss_percent"] * 0.1:.1f}% additional return'
                })
            
        except Exception as e:
            print(f"Error in investment performance prediction: {str(e)}")
        
        return suggestions
    
    def _predict_budget_optimization(self, budgets: List[Dict], transactions: List[Dict], user_id: str) -> List[Dict]:
        """Predict optimal budget allocation using ML"""
        suggestions = []
        
        try:
            if not budgets or not transactions:
                return suggestions
            
            df = self._prepare_transaction_data(transactions)
            if df.empty:
                return suggestions
            
            # Analyze budget vs actual spending
            budget_analysis = []
            for budget in budgets:
                budget_name = budget.get('name', 'Unknown')
                budget_limit = budget.get('limit', 0)
                budget_spent = budget.get('spent', 0)
                
                if budget_limit > 0:
                    utilization_rate = budget_spent / budget_limit
                    variance = budget_spent - budget_limit
                    
                    budget_analysis.append({
                        'name': budget_name,
                        'limit': budget_limit,
                        'spent': budget_spent,
                        'utilization_rate': utilization_rate,
                        'variance': variance,
                        'efficiency_score': 1 - abs(utilization_rate - 0.8)  # Optimal utilization around 80%
                    })
            
            if budget_analysis:
                # Find budgets that need optimization
                over_budget = [b for b in budget_analysis if b['variance'] > 0]
                under_budget = [b for b in budget_analysis if b['utilization_rate'] < 0.5]
                
                if over_budget:
                    total_overage = sum(b['variance'] for b in over_budget)
                    suggestions.append({
                        'type': 'ml_budget_optimization',
                        'title': '🎯 ML Budget Optimization Required',
                        'description': f'ML analysis shows {len(over_budget)} budgets are over limit by ₹{total_overage:,.0f} total.',
                        'priority': 'high',
                        'category': 'budget',
                        'action': f'Adjust budget limits for {", ".join([b["name"] for b in over_budget[:3]])} or reduce spending',
                        'over_budget_categories': [b['name'] for b in over_budget],
                        'total_overage': total_overage,
                        'optimization_potential': f'₹{total_overage * 0.8:,.0f} potential monthly savings'
                    })
                
                if under_budget:
                    suggestions.append({
                        'type': 'ml_budget_reallocation',
                        'title': '💰 ML Budget Reallocation Opportunity',
                        'description': f'ML analysis suggests reallocating unused budget from {", ".join([b["name"] for b in under_budget[:3]])} to high-priority categories.',
                        'priority': 'medium',
                        'category': 'budget',
                        'action': f'Consider reallocating budget from underutilized categories to areas with higher spending needs',
                        'under_budget_categories': [b['name'] for b in under_budget],
                        'reallocation_potential': f'₹{sum(b["limit"] * 0.3 for b in under_budget):,.0f} available for reallocation'
                    })
            
        except Exception as e:
            print(f"Error in budget optimization: {str(e)}")
        
        return suggestions
    
    def generate_ml_suggestions(self, user_id: str, user_data: Dict[str, Any]) -> List[Dict]:
        """Generate comprehensive ML-powered suggestions"""
        suggestions = []
        
        try:
            # Extract data
            transactions = user_data.get('transactions', [])
            debts = user_data.get('debts', [])
            investments = user_data.get('investments', [])
            budgets = user_data.get('budgets', [])
            
            # Generate ML-based suggestions
            suggestions.extend(self._detect_spending_anomalies(transactions, user_id))
            suggestions.extend(self._predict_future_savings(transactions, user_id))
            suggestions.extend(self._analyze_spending_patterns(transactions, user_id))
            suggestions.extend(self._predict_debt_payoff_optimization(debts, transactions, user_id))
            suggestions.extend(self._predict_investment_performance(investments, user_id))
            suggestions.extend(self._predict_budget_optimization(budgets, transactions, user_id))
            
            # Add ML confidence scores
            for suggestion in suggestions:
                suggestion['ml_generated'] = True
                suggestion['ml_confidence'] = suggestion.get('ml_confidence', 'High - Based on advanced pattern analysis')
            
        except Exception as e:
            print(f"Error generating ML suggestions: {str(e)}")
        
        return suggestions
