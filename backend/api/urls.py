from django.urls import path
from .views import (
    # Auth Views
    AnomalyByUserAPIView,
    BudgetListByUserNoAuthView,
    DebtAPIView,
    DebtPayoffMLAPIView,

    ExpenseForecastUnifiedAPIView,
    ExpensePredictionAPIView,
   
    GoalAPIView,
    GoalETAPredictionAPIView,
    IncomeCollectionAPIView,
    IncomeSourceAPIView,
    RecurringByUserAPIView,
    RunAnomalyDetectionAPIView,
    RunRecurringDetectionAPIView,
    # GoalDetailAPIView,
    SignupView,
    LoginView,

    # Account Views
    AccountListCreateAPIView,
    AccountDetailView,
    AccountUpdateView,
    AccountDeleteView,
    TransactionCountAPIView,

    # Transaction Views
    TransactionListCreateAPIView,
    TransactionDetailView,
    TransactionUpdateView,
    TransactionDeleteView,
    TransactionsByUserView,
    TransactionsByAccountView,

    # Budget Views
    BudgetCreateView,
    BudgetListByUserView,
    BudgetListByAccountView,
    BudgetDetailView,

    # Goal Views
    # GoalListCreateAPIView,


    # Portfolio Views
    PortfolioListCreateAPIView,
    PortfolioDetailView,

    # Debt Views


    # Other Features
    ReviewView,
    ContactMessageView,
)

# AI Chat Views
from .ai_chat_views import (
    AIChatView,
    FinancialSummaryView,
)

# AI Suggestions Views
from .suggestions_views import (
    AISuggestionsView,
    SuggestionCategoriesView,
)

# Natural Language Views
from .natural_language_views import (
    NaturalLanguageChatView,
    ConversationHistoryView,
    ClearConversationView,
    ContextAwareSuggestionsView,
)

# Permission Views
from .permission_views import (
    UserPermissionView,
    PermissionStatusView,
    BulkPermissionView,
)

urlpatterns = [

    # ========================
    # AUTHENTICATION ENDPOINTS
    # ========================
    path('users/signup/', SignupView.as_view(), name='user-signup'),  # Register a new user
    path('users/login/', LoginView.as_view(), name='user-login'),     # Login and get JWT token

    # =================
    # ACCOUNT ENDPOINTS
    # =================
    path('accounts/', AccountListCreateAPIView.as_view(), name='account-list-create'),  # GET all accounts / POST new account
    path('accounts/<str:pk>/', AccountDetailView.as_view(), name='account-detail'),     # GET account details
    path('accounts/<str:pk>/update/', AccountUpdateView.as_view(), name='account-update'),  # PUT update account
    path('accounts/<str:pk>/delete/', AccountDeleteView.as_view(), name='account-delete'),  # DELETE account

    # =====================
    # TRANSACTION ENDPOINTS
    # =====================
    path('transactions/', TransactionListCreateAPIView.as_view(), name='transaction-list'),  # GET all / POST new transaction
    path('transactions/<str:pk>/', TransactionDetailView.as_view(), name='transaction-detail'),  # GET transaction details
    path('transactions/<str:pk>/update/', TransactionUpdateView.as_view(), name='transaction-update'),  # PUT update transaction
    path('transactions/<str:pk>/delete/', TransactionDeleteView.as_view(), name='transaction-delete'),  # DELETE transaction
    path('transactions/users/<str:user_id>/', TransactionsByUserView.as_view(), name='transactions-by-user'),  # GET transactions by user
    path('transactions/accounts/<str:account_id>/', TransactionsByAccountView.as_view(), name='transactions-by-account'),  # GET transactions by account

    # ===============
    # BUDGET ENDPOINTS
    # ===============
    path('budgets/', BudgetCreateView.as_view(), name='create-budget'),  # POST create budget
    path('budgets/users/<str:user_id>/', BudgetListByUserView.as_view(), name='list-budgets-by-user'),  # GET budgets by user
    path('budgets/accounts/<str:account_id>/', BudgetListByAccountView.as_view(), name='list-budgets-by-account'),  # GET budgets by account
    path('budgets/<str:pk>/', BudgetDetailView.as_view(), name='budget-detail'),  # GET, PUT, DELETE a specific budget
    path("budgets/noauth/<str:user_id>/", BudgetListByUserNoAuthView.as_view(), name="budgets-by-user-noauth"),
    # =============
    # GOAL ENDPOINTS
   
    # path("goals/", GoalListCreateAPIView.as_view(), name="goal-list-create"),
    # path("goals/<str:pk>/", GoalDetailAPIView.as_view(), name="goal-detail"),
    path("goals/", GoalAPIView.as_view(), name="goals"),
    path("goals/<str:pk>/", GoalAPIView.as_view(), name="goal-detail"),

    # =================
    # PORTFOLIO ENDPOINTS
    # =================
    path('portfolios/', PortfolioListCreateAPIView.as_view(), name='portfolio-list-create'),   # GET all / POST new
    path('portfolios/<str:pk>/', PortfolioDetailView.as_view(), name='portfolio-detail'),      # GET, PUT, DELETE single 
    
    # =============
    # DEBT ENDPOINTS
    # =============
    # urls.py  (add under Goals block)
    path("debts/", DebtAPIView.as_view(), name="debt-list-create"),
    path("debts/<str:pk>/", DebtAPIView.as_view(), name="debt-detail"),
   
    # =========
    # REVIEWS
    # =========
    path('review/', ReviewView.as_view(), name='review'),  # POST or GET reviews

    # =========
    # CONTACT
    # =========
    path("contact/", ContactMessageView.as_view(), name="contact"),
    
    # --- ML ROUTES ---
    path('ml/predict-expense/<str:user_id>/', ExpensePredictionAPIView.as_view(), name='predict-expense'),
    path('ml/anomalies/run/<str:user_id>/', RunAnomalyDetectionAPIView.as_view(), name='run-anomalies'),
    path('ml/recurring/run/<str:user_id>/', RunRecurringDetectionAPIView.as_view(), name='run-recurring'),
    path('ml/goals/eta/<str:user_id>/', GoalETAPredictionAPIView.as_view(), name='goals-eta'),
    # ML - Anomalies & Recurring Patterns
    path('ml/anomalies/users/<str:user_id>/', AnomalyByUserAPIView.as_view(), name='anomalies-by-user'),
    path('ml/recurring/users/<str:user_id>/', RecurringByUserAPIView.as_view(), name='recurring-by-user'),



    ##############################################################
    
    
    path("ml/forecast/", ExpenseForecastUnifiedAPIView.as_view(), name="ml-forecast-unified"),
    
    path("transactions/count/<str:user_id>/", TransactionCountAPIView.as_view(), name="transaction-count"),

   
    path("ml/debts/<str:user_id>/", DebtPayoffMLAPIView.as_view(), name="ml-debt-predict"),
    
    # ========================
    # AI CHAT ENDPOINTS
    # ========================
    path("ai/chat/", AIChatView.as_view(), name="ai-chat"),
    path("ai/summary/", FinancialSummaryView.as_view(), name="ai-summary"),
    
    # ========================
    # AI SUGGESTIONS ENDPOINTS
    # ========================
    path("ai/suggestions/", AISuggestionsView.as_view(), name="ai-suggestions"),
    path("ai/suggestions/categories/", SuggestionCategoriesView.as_view(), name="suggestion-categories"),
    
    # ================================
    # NATURAL LANGUAGE INTERACTION ENDPOINTS
    # ================================
    path("ai/natural-chat/", NaturalLanguageChatView.as_view(), name="natural-language-chat"),
    path("ai/conversation-history/", ConversationHistoryView.as_view(), name="conversation-history"),
    path("ai/clear-conversation/", ClearConversationView.as_view(), name="clear-conversation"),
    path("ai/context-suggestions/", ContextAwareSuggestionsView.as_view(), name="context-suggestions"),
    
    # ========================
    # PERMISSION ENDPOINTS
    # ========================
    path("permissions/", UserPermissionView.as_view(), name="user-permissions"),
    path("permissions/status/", PermissionStatusView.as_view(), name="permission-status"),
    path("permissions/bulk/", BulkPermissionView.as_view(), name="bulk-permissions"),
    
    path("income-sources/", IncomeSourceAPIView.as_view(), name="income-source-list-create"),
    path("income-sources/<str:pk>/", IncomeSourceAPIView.as_view(), name="income-source-detail"),
    path("income-collections/", IncomeCollectionAPIView.as_view(), name="income-collection-list-create"),
    path("income-collections/<str:pk>/", IncomeCollectionAPIView.as_view(), name="income-collection-detail"),
    
]
