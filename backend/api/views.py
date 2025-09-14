

from .ml_utils import (
    predict_next_month_expense,
    detect_spending_anomalies,
    find_recurring_patterns,
    predict_goal_completion,
)


from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, AuthenticationFailed
from bson import ObjectId
from datetime import datetime, timedelta
from django.conf import settings
import jwt

from .models import (
    RecurringPattern, Review, SpendingAnomaly, User, Transaction, Budget, Account,
    Goal, Portfolio
)
from .serializers import (
    RecurringPatternSerializer, ReviewSerializer, SignupSerializer, LoginSerializer, SpendingAnomalySerializer,
    TransactionSerializer, BudgetSerializer, AccountSerializer,
    GoalSerializer, PortfolioSerializer,
    update_account_totals, update_matching_budgets
)

# ========================
# AUTHENTICATION
# ========================

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise AuthenticationFailed("Incorrect password")
            except User.DoesNotExist:
                raise AuthenticationFailed("User not found")

            payload = {
                "user_id": str(user.id),
                "username": user.username,
                "email": user.email,
                "exp": datetime.utcnow() + timedelta(hours=1),
                "iat": datetime.utcnow()
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

            return Response({
                "token": token,
                "username": user.username,
                "email": user.email
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_logged_in_user(request):
    token = request.headers.get("Authorization")
    if not token:
        raise AuthenticationFailed("Authentication token missing")
    try:
        payload = jwt.decode(token.split(" ")[1], settings.SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token expired")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")


# =================
# USER DELETE API (cascade)
# =================

class UserDeleteView(APIView):
    def delete(self, request, pk):
        try:
            user = User.objects.get(id=ObjectId(pk))
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # delete all accounts, transactions, budgets for this user
        accounts = Account.objects(user_id=user)
        for acc in accounts:
            Transaction.objects(account_id=acc).delete()
            Budget.objects(account_id=acc).delete()
            acc.delete()

        user.delete()
        return Response({"message": "User and related data deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



# =================
# ACCOUNT API
# =================

class AccountListCreateAPIView(APIView):
    def get(self, request):
        user_id = request.query_params.get("user_id")

        # ✅ agar user_id missing ya 'null' ho to empty list bhejna
        if not user_id or user_id == "null":
            return Response([], status=status.HTTP_200_OK)

        try:
            user = User.objects.get(id=ObjectId(user_id))
            accounts = Account.objects(user_id=user)
        except (User.DoesNotExist, Exception):
            # agar user hi exist nahi karta ya ObjectId invalid hai
            return Response([], status=status.HTTP_200_OK)

        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AccountSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountDetailView(APIView):
    def get(self, request, pk):
        try:
            account = Account.objects.get(id=ObjectId(pk))
        except Account.DoesNotExist:
            raise NotFound("Account not found")

        return Response(AccountSerializer(account).data)


class AccountUpdateView(APIView):
    def put(self, request, pk):
        try:
            account = Account.objects(id=ObjectId(pk)).first()
            if not account:
                return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

            data = request.data
            account.account_name = data.get("account_name", account.account_name)
            account.account_type = data.get("account_type", account.account_type)
            account.description = data.get("description", account.description)
            account.save()

            return Response({"message": "Account updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AccountDeleteView(APIView):
    def delete(self, request, pk):
        try:
            account = Account.objects(id=ObjectId(pk)).first()
            if not account:
                return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

            # ✅ delete related transactions and budgets also
            Transaction.objects(account_id=account).delete()
            Budget.objects(account_id=account).delete()

            account.delete()
            return Response({"message": "Account and related data deleted"}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# =====================
# TRANSACTION API
# =====================

from mongoengine.errors import DoesNotExist

class TransactionListCreateAPIView(APIView):
    def get(self, request):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=ObjectId(user_id))
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        transactions = Transaction.objects(user_id=user)

        clean_transactions = []
        for txn in transactions:
            try:
                _ = txn.account_id.id
                clean_transactions.append(txn)
            except DoesNotExist:
                continue

        serializer = TransactionSerializer(clean_transactions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                txn = serializer.save()
                return Response(TransactionSerializer(txn).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionsByUserView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=ObjectId(user_id))
        transactions = Transaction.objects(user_id=user)
        return Response(TransactionSerializer(transactions, many=True).data)


class TransactionsByAccountView(APIView):
    def get(self, request, account_id):
        if not account_id or account_id == "null":
            return Response({"error": "Valid account_id is required"}, status=400)

        try:
            account = Account.objects.get(id=ObjectId(account_id))
        except (Account.DoesNotExist, Exception):
            return Response({"error": "Account not found"}, status=404)

        transactions = Transaction.objects(account_id=account)

        clean_transactions = []
        for tx in transactions:
            try:
                _ = tx.account_id.id
                clean_transactions.append(tx)
            except Exception:
                continue

        return Response(TransactionSerializer(clean_transactions, many=True).data)


class TransactionDetailView(APIView):
    def get(self, request, pk):
        tx = get_object_or_404(Transaction, id=pk)
        return Response(TransactionSerializer(tx).data)


class TransactionUpdateView(APIView):
    def put(self, request, pk):
        try:
            tx = Transaction.objects.get(id=ObjectId(pk))
        except Transaction.DoesNotExist:
            raise NotFound("Transaction not found")

        serializer = TransactionSerializer(tx, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionDeleteView(APIView):
    def delete(self, request, pk):
        try:
            tx = Transaction.objects.get(id=ObjectId(pk))
        except Transaction.DoesNotExist:
            raise NotFound("Transaction not found")

        account = tx.account_id
        tx.delete()
        update_account_totals(account)
        update_matching_budgets(tx)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ===============
# BUDGET API
# ===============

class BudgetCreateView(APIView):
    def post(self, request):
        serializer = BudgetSerializer(data=request.data)
        if serializer.is_valid():
            budget = serializer.save()
            return Response(BudgetSerializer(budget).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BudgetListByUserView(APIView):
    def get(self, request, user_id=None):
        logged_in_user_id = get_logged_in_user(request)
        budgets = Budget.objects(user_id=ObjectId(logged_in_user_id))
        return Response(BudgetSerializer(budgets, many=True).data)


class BudgetListByAccountView(APIView):
    def get(self, request, account_id):
        try:
            user_id = request.query_params.get("user_id")
            if not user_id:
                return Response({"error": "user_id query param is required"}, status=400)

            try:
                user = User.objects.get(id=ObjectId(user_id))
            except User.DoesNotExist:
                raise NotFound("User not found")

            try:
                account = Account.objects.get(id=ObjectId(account_id), user_id=user)
            except Account.DoesNotExist:
                raise NotFound("Account not found for this user")

            budgets = Budget.objects(user_id=user, account_id=account)
            serializer = BudgetSerializer(budgets, many=True)
            return Response(serializer.data)

        except NotFound as e:
            return Response({"error": str(e)}, status=404)
        except Exception as e:
            return Response({"error": "Invalid account_id or no data", "details": str(e)},
                            status=status.HTTP_400_BAD_REQUEST)


class BudgetDetailView(APIView):
    def get_object(self, pk):
        try:
            return Budget.objects.get(id=ObjectId(pk))
        except Budget.DoesNotExist:
            raise NotFound("❌ Budget not found")

    def _ensure_owner(self, request, budget):
        uid = request.query_params.get("user_id")
        if uid and str(budget.user_id.id) != uid:
            raise NotFound("Budget not found")

    def get(self, request, pk):
        budget = self.get_object(pk)
        self._ensure_owner(request, budget)
        serializer = BudgetSerializer(budget)
        return Response(serializer.data)

    def put(self, request, pk):
        budget = self.get_object(pk)
        self._ensure_owner(request, budget)
        serializer = BudgetSerializer(budget, data=request.data, partial=True)
        if serializer.is_valid():
            updated_budget = serializer.save()
            return Response(BudgetSerializer(updated_budget).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        budget = self.get_object(pk)
        self._ensure_owner(request, budget)
        budget.delete()
        return Response({"message": "✅ Budget deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from mongoengine.errors import DoesNotExist, ValidationError
from .models import Goal
from .serializers import GoalSerializer


class GoalAPIView(APIView):
    # ------------------
    # GET (list or detail)
    # ------------------
    def get(self, request, pk=None):
        user_id = request.query_params.get("user_id") or request.data.get("user_id")

        if pk:  # detail view
            try:
                goal = Goal.objects.get(id=ObjectId(pk))
                if user_id and str(goal.user_id.id) != str(user_id):
                    return Response({"error": "Not authorized to view this goal"}, status=status.HTTP_403_FORBIDDEN)
            except (DoesNotExist, ValidationError):
                return Response({"error": "Goal not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = GoalSerializer(goal)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # list view
        if user_id:
            goals = Goal.objects.filter(user_id=ObjectId(user_id))
        else:
            goals = Goal.objects.none()  # 👈 empty if no user_id
        serializer = GoalSerializer(goals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------
    # POST (create)
    # ------------------
    def post(self, request):
        serializer = GoalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # user_id already sent from frontend
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------
    # PUT (update)
    # ------------------
    def put(self, request, pk=None):
        if not pk:
            return Response({"error": "Goal ID required"}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.data.get("user_id")
        try:
            goal = Goal.objects.get(id=ObjectId(pk))
            if user_id and str(goal.user_id.id) != str(user_id):
                return Response({"error": "Not authorized to update this goal"}, status=status.HTTP_403_FORBIDDEN)
        except (DoesNotExist, ValidationError):
            return Response({"error": "Goal not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = GoalSerializer(goal, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------
    # DELETE
    # ------------------
    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "Goal ID required"}, status=status.HTTP_400_BAD_REQUEST)

        user_id = request.query_params.get("user_id") or request.data.get("user_id")
        try:
            goal = Goal.objects.get(id=ObjectId(pk))
            if user_id and str(goal.user_id.id) != str(user_id):
                return Response({"error": "Not authorized to delete this goal"}, status=status.HTTP_403_FORBIDDEN)
        except (DoesNotExist, ValidationError):
            return Response({"error": "Goal not found"}, status=status.HTTP_404_NOT_FOUND)

        goal.delete()
        return Response({"message": "Goal deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# =================
# PORTFOLIO API
# =================

class PortfolioListCreateAPIView(APIView):
    def get(self, request):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            portfolios = Portfolio.objects(user_id=ObjectId(user_id))
        except Exception:
            return Response({"error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PortfolioSerializer(portfolios, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PortfolioSerializer(data=request.data)
        if serializer.is_valid():
            portfolio = serializer.save()
            return Response(PortfolioSerializer(portfolio).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PortfolioDetailView(APIView):
    def get_object(self, pk):
        try:
            return Portfolio.objects.get(id=ObjectId(pk))
        except Portfolio.DoesNotExist:
            raise NotFound("Portfolio not found")

    def get(self, request, pk):
        portfolio = self.get_object(pk)
        serializer = PortfolioSerializer(portfolio)
        return Response(serializer.data)

    def put(self, request, pk):
        portfolio = self.get_object(pk)
        serializer = PortfolioSerializer(portfolio, data=request.data, partial=True)
        if serializer.is_valid():
            portfolio = serializer.save()
            return Response(PortfolioSerializer(portfolio).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        portfolio = self.get_object(pk)
        portfolio.delete()
        return Response({"message": "Portfolio deleted"}, status=status.HTTP_204_NO_CONTENT)



# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from mongoengine.errors import DoesNotExist, ValidationError
from .models import Debt
from .serializers import DebtSerializer

class DebtAPIView(APIView):
    # ------------------
    # GET (list or detail)
    # ------------------
    def get(self, request, pk=None):
        if pk:
            try:
                debt = Debt.objects.get(id=ObjectId(pk))
            except (DoesNotExist, ValidationError):
                return Response({"error": "Debt not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = DebtSerializer(debt)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # list all debts (filter by user_id if given)
        user_id = request.query_params.get("user_id")
        if user_id:
            debts = Debt.objects.filter(user_id=ObjectId(user_id))
        else:
            debts = Debt.objects.all()

        serializer = DebtSerializer(debts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------
    # POST (create)
    # ------------------
    def post(self, request):
        serializer = DebtSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------
    # PUT (update)
    # ------------------
    def put(self, request, pk=None):
        if not pk:
            return Response({"error": "Debt ID required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            debt = Debt.objects.get(id=ObjectId(pk))
        except (DoesNotExist, ValidationError):
            return Response({"error": "Debt not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DebtSerializer(debt, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------
    # DELETE
    # ------------------
    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "Debt ID required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            debt = Debt.objects.get(id=ObjectId(pk))
        except (DoesNotExist, ValidationError):
            return Response({"error": "Debt not found"}, status=status.HTTP_404_NOT_FOUND)

        debt.delete()
        return Response({"message": "Debt deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# =========
# REVIEWS
# =========

class ReviewView(APIView):
    def get(self, request):
        reviews = Review.objects.all()
        return Response(ReviewSerializer(reviews, many=True).data)

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save()
            return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========
# CONTACT
# =========
# contat us page
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .serializers import ContactMessageSerializer

class ContactMessageView(APIView):
    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()

            # Send email to admin with proper formatting
            admin_subject = f"New Contact Message: {contact.subject}"
            admin_message = f"""
            New Contact Form Submission - TrackSpendAI
            
            Contact Details:
            ----------------------------
            Name:    {contact.name}
            Email:   {contact.email}
            Subject: {contact.subject}
            
            Message:
            ----------------------------
            {contact.message}
            
            ----------------------------
            Received at: {contact.created_at.strftime('%Y-%m-%d %H:%M')}
            """
            
            # Confirmation email to user
            user_subject = "Thank you for contacting TrackSpendAI"
            user_message = f"""
            Dear {contact.name},
            
            Thank you for reaching out to TrackSpendAI. We have received your message and our team will get back to you shortly.
            
            Here's a copy of your message for your reference:
            ----------------------------
            Subject: {contact.subject}
            
            {contact.message}
            
            ----------------------------
            If you have any further questions, please don't hesitate to contact us.
            
            Best regards,
            The TrackSpendAI Team
            """
            
            try:
                # Send email to admin
                send_mail(
                    subject=admin_subject,
                    message=admin_message.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )

                # Confirmation email to user
                send_mail(
                    subject=user_subject,
                    message=user_message.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[contact.email],
                    fail_silently=False,
                )

                return Response(
                    {"message": "Your message has been sent successfully!"}, 
                    status=status.HTTP_201_CREATED
                )
                
            except Exception as e:
                error_message = "Message was saved but there was an error sending emails."
                
                # Show detailed error only in DEBUG mode
                if settings.DEBUG:
                    return Response(
                        {"message": error_message, "error": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                else:
                    return Response(
                        {"message": error_message},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ExpensePredictionAPIView(APIView):
    def get(self, request, user_id):
        try:
            pred = predict_next_month_expense(user_id)
            return Response({
                "user_id": str(pred.user_id.id),
                "prediction_type": pred.prediction_type,
                "target_period": pred.target_period,
                "predicted_income": pred.predicted_income,
                "predicted_expense": pred.predicted_expense,
                "predicted_balance": pred.predicted_balance,
                "confidence": pred.confidence,
                "model_version": pred.model_version,
                "created_at": pred.created_at.isoformat(),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RunAnomalyDetectionAPIView(APIView):
    def post(self, request, user_id):
        try:
            created = detect_spending_anomalies(user_id)
            return Response({
                "created": len(created),
                "anomaly_ids": [str(a.id) for a in created]
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RunRecurringDetectionAPIView(APIView):
    def post(self, request, user_id):
        try:
            created = find_recurring_patterns(user_id)
            return Response({
                "created": len(created),
                "pattern_ids": [str(p.id) for p in created]
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GoalETAPredictionAPIView(APIView):
    def get(self, request, user_id):
        try:
            result = predict_goal_completion(user_id)
            return Response({"results": result}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class AnomalyByUserAPIView(APIView):
#     def get(self, request, user_id):
#         try:
#             anomalies = SpendingAnomaly.objects(user_id=ObjectId(user_id))
#             serializer = SpendingAnomalySerializer(anomalies, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class RecurringByUserAPIView(APIView):
    def get(self, request, user_id):
        try:
            patterns = RecurringPattern.objects(user_id=ObjectId(user_id))
            serializer = RecurringPatternSerializer(patterns, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AnomalyByUserAPIView(APIView):
    def get(self, request, user_id):
        anomalies = SpendingAnomaly.objects(user_id=ObjectId(user_id))
        serializer = SpendingAnomalySerializer(anomalies, many=True)
        return Response(serializer.data, status=200)


from rest_framework.permissions import AllowAny

class BudgetListByUserNoAuthView(APIView):
    authentication_classes = []  # disable JWT/Auth checks
    permission_classes = [AllowAny]  # allow public access

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=ObjectId(user_id))
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        budgets = Budget.objects(user_id=user)
        return Response(BudgetSerializer(budgets, many=True).data, status=status.HTTP_200_OK)








######################################################################################



# ===========================
# NEW: ML Forecasting APIs (Income/Expense/Balance)
# ===========================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .ml_utils import (
    build_forecast_payload,
    forecast_dispatch,  # legacy single-series support (if needed elsewhere)
)

class ExpenseForecastUnifiedAPIView(APIView):
    """
    Unified Forecast API

    GET /api/ml/forecast/?user_id=<id>&model=<holt|arima|sarima|prophet|xgb>&horizon=<week|month|year>&periods=<int>&granularity=<daily|weekly|monthly>&target_date=YYYY-MM-DD

    Priority:
      - If `periods` given -> use it (days)
      - Else if `horizon` given -> week=7, month=30, year=365
      - Else default periods=30

    Returns income/expense/balance daily forecasts + summary totals.
    """
    def get(self, request):
        user_id = request.query_params.get("user_id")
        model = request.query_params.get("model", "holt").lower()
        horizon = request.query_params.get("horizon")  # week|month|year
        periods = request.query_params.get("periods")
        granularity = request.query_params.get("granularity", "daily").lower()
        target_date = request.query_params.get("target_date")  # optional YYYY-MM-DD

        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # resolve periods
        if periods is not None:
            try:
                periods = int(periods)
            except Exception:
                return Response({"error": "periods must be integer days"}, status=400)
        else:
            horizon = (horizon or "").lower()
            if horizon == "week":
                periods = 7
            elif horizon == "month":
                periods = 30
            elif horizon == "year":
                periods = 365
            else:
                periods = 30

        if granularity not in ("daily", "weekly", "monthly"):
            return Response({"error": "granularity must be daily|weekly|monthly"}, status=400)

        try:
            payload = build_forecast_payload(
                user_id=user_id,
                model=model,
                periods=periods,
                granularity=granularity,
                target_date=target_date
            )
            return Response({"status": "ok", **payload}, status=200)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=500)


from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Transaction, User
from bson import ObjectId

class TransactionCountAPIView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=ObjectId(user_id))
            count = Transaction.objects(user_id=user).count()
            return Response({"count": count})
        except Exception as e:
            return Response({"error": str(e)}, status=400)



from rest_framework.views import APIView
from rest_framework.response import Response
from bson import ObjectId
from .ml_utils import ml_predict_debt_payoff
from .models import Transaction, Debt

class DebtPayoffMLAPIView(APIView):
    def get(self, request, user_id):
        try:
            user_obj_id = ObjectId(user_id)   # Convert string → ObjectId
        except Exception:
            return Response({"error": "Invalid user_id format"}, status=400)

        # Fetch debts and transactions using ReferenceField
        debts = Debt.objects.filter(user_id=user_obj_id)
        transactions = Transaction.objects.filter(user_id=user_obj_id)

        if not debts:
            return Response({"error": "No debts found"}, status=404)

        total_debt = sum(float(d.remaining_amount) for d in debts)

        prediction = ml_predict_debt_payoff(transactions, total_debt)

        return Response(prediction)

# # Income Source Views
# # Add this to your existing views.py file

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from mongoengine.errors import DoesNotExist, ValidationError
from .models import IncomeSource
from .serializers import IncomeSourceSerializer

class IncomeSourceAPIView(APIView):
    # ------------------
    # GET (list or detail)
    # ------------------
    def get(self, request, pk=None):
        if pk:
            try:
                income_source = IncomeSource.objects.get(id=ObjectId(pk))
            except (DoesNotExist, ValidationError):
                return Response({"error": "Income source not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = IncomeSourceSerializer(income_source)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # list all income sources (filter by user_id if given)
        user_id = request.query_params.get("user_id")
        if user_id:
            income_sources = IncomeSource.objects.filter(user_id=ObjectId(user_id))
        else:
            income_sources = IncomeSource.objects.all()

        serializer = IncomeSourceSerializer(income_sources, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------
    # POST (create)
    # ------------------
    def post(self, request):
        serializer = IncomeSourceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------
    # PUT (update)
    # ------------------
    def put(self, request, pk=None):
        if not pk:
            return Response({"error": "Income source ID required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            income_source = IncomeSource.objects.get(id=ObjectId(pk))
        except (DoesNotExist, ValidationError):
            return Response({"error": "Income source not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = IncomeSourceSerializer(income_source, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------
    # DELETE
    # ------------------
    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "Income source ID required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            income_source = IncomeSource.objects.get(id=ObjectId(pk))
        except (DoesNotExist, ValidationError):
            return Response({"error": "Income source not found"}, status=status.HTTP_404_NOT_FOUND)

        income_source.delete()
        return Response({"message": "Income source deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Income Collection Views - Add this to your views.py file
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from bson import ObjectId
from mongoengine.errors import DoesNotExist, ValidationError
from .models import IncomeCollection
from .serializers import IncomeCollectionSerializer

class IncomeCollectionAPIView(APIView):
    # ------------------
    # GET (list or detail)
    # ------------------
    def get(self, request, pk=None):
        if pk:
            try:
                income_collection = IncomeCollection.objects.get(id=ObjectId(pk))
            except (DoesNotExist, ValidationError):
                return Response({"error": "Income collection not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer = IncomeCollectionSerializer(income_collection)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # list all income collections (filter by user_id if given)
        user_id = request.query_params.get("user_id")
        income_source_id = request.query_params.get("income_source_id")
        
        filters = {}
        if user_id:
            filters["user_id"] = ObjectId(user_id)
        if income_source_id:
            filters["income_source_id"] = ObjectId(income_source_id)
        
        income_collections = IncomeCollection.objects.filter(**filters).order_by("-collection_date")
        serializer = IncomeCollectionSerializer(income_collections, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------
    # POST (create)
    # ------------------
    def post(self, request):
        serializer = IncomeCollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------
    # PUT (update)
    # ------------------
    def put(self, request, pk=None):
        if not pk:
            return Response({"error": "Income collection ID required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            income_collection = IncomeCollection.objects.get(id=ObjectId(pk))
        except (DoesNotExist, ValidationError):
            return Response({"error": "Income collection not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = IncomeCollectionSerializer(income_collection, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ------------------
    # DELETE
    # ------------------
    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "Income collection ID required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            income_collection = IncomeCollection.objects.get(id=ObjectId(pk))
        except (DoesNotExist, ValidationError):
            return Response({"error": "Income collection not found"}, status=status.HTTP_404_NOT_FOUND)

        income_collection.delete()
        return Response({"message": "Income collection deleted successfully"}, status=status.HTTP_204_NO_CONTENT)