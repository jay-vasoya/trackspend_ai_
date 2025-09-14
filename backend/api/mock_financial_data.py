# mock_financial_data.py
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os

class MockFinancialMCPServer:
    """
    Simulates a Financial MCP (Multi-Channel Processing) Server
    Generates realistic mock financial data for AI assistant testing
    """
    
    def __init__(self):
        self.data_dir = "mock_data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def generate_mock_user_data(self, user_id: str) -> Dict[str, Any]:
        """Generate comprehensive mock financial data for a user"""
        
        # Generate realistic financial profile
        base_income = random.randint(50000, 150000)  # Annual income
        monthly_income = base_income / 12
        
        data = {
            "user_id": user_id,
            "generated_at": datetime.utcnow().isoformat(),
            "assets": self._generate_assets(monthly_income),
            "liabilities": self._generate_liabilities(monthly_income),
            "transactions": self._generate_transactions(monthly_income),
            "epf_retirement": self._generate_epf_data(base_income),
            "credit_score": self._generate_credit_score(),
            "investments": self._generate_investments(monthly_income),
            "permissions": {
                "assets": True,
                "liabilities": True,
                "transactions": True,
                "epf_retirement": True,
                "credit_score": True,
                "investments": True
            }
        }
        
        # Save to file
        file_path = os.path.join(self.data_dir, f"{user_id}_financial_data.json")
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return data
    
    def _generate_assets(self, monthly_income: float) -> Dict[str, Any]:
        """Generate realistic asset data"""
        cash = random.randint(5000, 50000)
        savings = random.randint(10000, 100000)
        checking = random.randint(2000, 20000)
        
        # Property value based on income
        property_value = monthly_income * random.randint(60, 120)  # 5-10 years of income
        
        return {
            "cash": cash,
            "bank_accounts": {
                "savings": savings,
                "checking": checking,
                "total": savings + checking
            },
            "property": {
                "primary_residence": property_value,
                "other_properties": random.randint(0, 2) * property_value * 0.3
            },
            "vehicles": {
                "primary_vehicle": random.randint(15000, 60000),
                "other_vehicles": random.randint(0, 1) * random.randint(10000, 30000)
            },
            "total_assets": cash + savings + checking + property_value
        }
    
    def _generate_liabilities(self, monthly_income: float) -> Dict[str, Any]:
        """Generate realistic liability data"""
        # Mortgage (typically 3-5x annual income)
        mortgage_balance = monthly_income * 12 * random.uniform(2.5, 4.5)
        mortgage_payment = monthly_income * random.uniform(0.25, 0.35)
        
        # Credit card debt (typically 1-3 months income)
        credit_card_debt = monthly_income * random.uniform(0.5, 2.0)
        credit_card_limit = credit_card_debt * random.uniform(2, 4)
        
        # Auto loan
        auto_loan_balance = random.randint(10000, 50000)
        auto_loan_payment = auto_loan_balance / random.randint(36, 72)  # 3-6 years
        
        # Personal loans
        personal_loan_balance = random.randint(5000, 25000)
        personal_loan_payment = personal_loan_balance / random.randint(24, 60)
        
        return {
            "mortgage": {
                "balance": mortgage_balance,
                "monthly_payment": mortgage_payment,
                "interest_rate": random.uniform(3.5, 6.5),
                "remaining_term_months": random.randint(180, 360)
            },
            "credit_cards": {
                "total_debt": credit_card_debt,
                "total_limit": credit_card_limit,
                "utilization_rate": (credit_card_debt / credit_card_limit) * 100,
                "monthly_payment": credit_card_debt * random.uniform(0.02, 0.05)
            },
            "auto_loans": {
                "balance": auto_loan_balance,
                "monthly_payment": auto_loan_payment,
                "interest_rate": random.uniform(4.0, 8.0)
            },
            "personal_loans": {
                "balance": personal_loan_balance,
                "monthly_payment": personal_loan_payment,
                "interest_rate": random.uniform(6.0, 12.0)
            },
            "total_liabilities": mortgage_balance + credit_card_debt + auto_loan_balance + personal_loan_balance,
            "total_monthly_payments": mortgage_payment + (credit_card_debt * 0.03) + auto_loan_payment + personal_loan_payment
        }
    
    def _generate_transactions(self, monthly_income: float) -> List[Dict[str, Any]]:
        """Generate realistic transaction history (last 12 months)"""
        transactions = []
        base_date = datetime.utcnow()
        
        # Income transactions (bi-weekly)
        for month in range(12):
            for week in range(2):  # Bi-weekly pay
                pay_date = base_date - timedelta(days=30*month + 14*week)
                transactions.append({
                    "date": pay_date.isoformat(),
                    "type": "income",
                    "amount": monthly_income / 2,
                    "category": "salary",
                    "description": "Bi-weekly salary",
                    "account": "checking"
                })
        
        # Expense transactions
        expense_categories = {
            "groceries": {"min": 200, "max": 600, "frequency": 8},  # per month
            "rent_mortgage": {"min": monthly_income*0.25, "max": monthly_income*0.35, "frequency": 1},
            "utilities": {"min": 150, "max": 400, "frequency": 1},
            "transportation": {"min": 200, "max": 500, "frequency": 1},
            "dining": {"min": 100, "max": 400, "frequency": 6},
            "entertainment": {"min": 50, "max": 300, "frequency": 4},
            "healthcare": {"min": 50, "max": 200, "frequency": 2},
            "shopping": {"min": 100, "max": 500, "frequency": 3},
            "insurance": {"min": 100, "max": 300, "frequency": 1},
            "savings": {"min": monthly_income*0.1, "max": monthly_income*0.2, "frequency": 1}
        }
        
        for month in range(12):
            for category, config in expense_categories.items():
                for _ in range(config["frequency"]):
                    amount = random.uniform(config["min"], config["max"])
                    if config["frequency"] > 1:  # Multiple transactions per month
                        amount = amount / config["frequency"]
                    
                    transaction_date = base_date - timedelta(
                        days=30*month + random.randint(0, 29)
                    )
                    
                    transactions.append({
                        "date": transaction_date.isoformat(),
                        "type": "expense",
                        "amount": round(amount, 2),
                        "category": category,
                        "description": f"{category.replace('_', ' ').title()} payment",
                        "account": "checking" if category != "savings" else "savings"
                    })
        
        # Sort by date
        transactions.sort(key=lambda x: x["date"], reverse=True)
        return transactions
    
    def _generate_epf_data(self, annual_income: float) -> Dict[str, Any]:
        """Generate EPF/Retirement data"""
        # EPF contribution is typically 12% of salary
        monthly_contribution = (annual_income * 0.12) / 12
        employer_contribution = monthly_contribution  # Employer matches
        
        # Current balance (accumulated over years)
        years_worked = random.randint(2, 15)
        current_balance = (monthly_contribution + employer_contribution) * 12 * years_worked * random.uniform(1.1, 1.3)
        
        return {
            "current_balance": current_balance,
            "monthly_contribution": monthly_contribution,
            "employer_contribution": employer_contribution,
            "total_monthly_contribution": monthly_contribution + employer_contribution,
            "years_contributed": years_worked,
            "estimated_retirement_balance": current_balance * random.uniform(2.5, 4.0)
        }
    
    def _generate_credit_score(self) -> Dict[str, Any]:
        """Generate realistic credit score data"""
        score = random.randint(580, 850)
        
        if score >= 800:
            rating = "Excellent"
        elif score >= 740:
            rating = "Very Good"
        elif score >= 670:
            rating = "Good"
        elif score >= 580:
            rating = "Fair"
        else:
            rating = "Poor"
        
        return {
            "score": score,
            "rating": rating,
            "last_updated": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat(),
            "factors": {
                "payment_history": random.uniform(0.8, 1.0),
                "credit_utilization": random.uniform(0.1, 0.8),
                "length_of_credit": random.uniform(0.6, 1.0),
                "credit_mix": random.uniform(0.7, 1.0),
                "new_credit": random.uniform(0.8, 1.0)
            }
        }
    
    def _generate_investments(self, monthly_income: float) -> Dict[str, Any]:
        """Generate investment portfolio data"""
        # Investment amount (typically 10-20% of income)
        monthly_investment = monthly_income * random.uniform(0.1, 0.2)
        
        # Portfolio allocation
        total_invested = monthly_investment * random.randint(12, 60)  # 1-5 years
        
        stocks_percentage = random.uniform(0.4, 0.7)
        bonds_percentage = random.uniform(0.2, 0.4)
        mutual_funds_percentage = 1 - stocks_percentage - bonds_percentage
        
        # Current value with some growth
        growth_factor = random.uniform(1.05, 1.25)
        current_value = total_invested * growth_factor
        
        return {
            "total_invested": total_invested,
            "current_value": current_value,
            "total_gain_loss": current_value - total_invested,
            "total_gain_loss_percentage": ((current_value - total_invested) / total_invested) * 100,
            "monthly_contribution": monthly_investment,
            "allocation": {
                "stocks": {
                    "percentage": stocks_percentage * 100,
                    "value": current_value * stocks_percentage,
                    "gain_loss": (current_value * stocks_percentage) - (total_invested * stocks_percentage)
                },
                "bonds": {
                    "percentage": bonds_percentage * 100,
                    "value": current_value * bonds_percentage,
                    "gain_loss": (current_value * bonds_percentage) - (total_invested * bonds_percentage)
                },
                "mutual_funds": {
                    "percentage": mutual_funds_percentage * 100,
                    "value": current_value * mutual_funds_percentage,
                    "gain_loss": (current_value * mutual_funds_percentage) - (total_invested * mutual_funds_percentage)
                }
            },
            "recent_performance": {
                "1_month": random.uniform(-5, 8),
                "3_months": random.uniform(-10, 15),
                "6_months": random.uniform(-15, 25),
                "1_year": random.uniform(-20, 35)
            }
        }
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user's financial data"""
        file_path = os.path.join(self.data_dir, f"{user_id}_financial_data.json")
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            return self.generate_mock_user_data(user_id)
    
    def update_permissions(self, user_id: str, permissions: Dict[str, bool]) -> bool:
        """Update user's data access permissions"""
        file_path = os.path.join(self.data_dir, f"{user_id}_financial_data.json")
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            data["permissions"] = permissions
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        return False
    
    def get_filtered_data(self, user_id: str) -> Dict[str, Any]:
        """Get user data filtered by permissions"""
        data = self.get_user_data(user_id)
        permissions = data.get("permissions", {})
        
        filtered_data = {
            "user_id": data["user_id"],
            "generated_at": data["generated_at"]
        }
        
        # Only include data categories that user has granted access to
        for category in ["assets", "liabilities", "transactions", "epf_retirement", "credit_score", "investments"]:
            if permissions.get(category, False):
                filtered_data[category] = data[category]
        
        return filtered_data

# Global instance
mock_mcp_server = MockFinancialMCPServer()
