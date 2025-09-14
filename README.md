# 💸 TrackSpendAI

**TrackSpendAI** is a comprehensive AI-powered personal finance management application that combines traditional financial tracking with cutting-edge machine learning and natural language processing to provide intelligent financial insights and recommendations.

![TrackSpendAI Logo](https://img.shields.io/badge/TrackSpendAI-AI%20Finance%20Manager-blue?style=for-the-badge&logo=robot)
![Version](https://img.shields.io/badge/version-1.0.0-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)

---

## 🌟 Key Features

### 🤖 **AI-Powered Intelligence**
- **Natural Language Chat**: Ask questions in plain English like "How much did I spend last month?" or "What's my savings trend?"
- **ML-Powered Suggestions**: Get personalized recommendations for debt management, investment strategies, and budget optimization
- **Smart Financial Insights**: AI-driven analysis of spending patterns, income trends, and financial health
- **Predictive Analytics**: Forecast future savings, detect spending anomalies, and predict financial outcomes

### 📊 **Comprehensive Financial Tracking**
- **Multi-Account Management**: Track checking, savings, credit cards, and investment accounts
- **Transaction Management**: Categorize and analyze income and expenses with smart categorization
- **Budget Planning**: Create and monitor budgets with real-time tracking and alerts
- **Goal Setting**: Set and track financial goals with progress monitoring
- **Debt Tracking**: Monitor and optimize debt repayment strategies

### 📈 **Advanced Analytics**
- **Financial Health Score**: Comprehensive 0-100 score based on 5 key financial factors
- **Credit Score Simulation**: AI-calculated credit score (300-850) based on financial behavior
- **Income Stability Analysis**: Track income consistency and growth trends
- **Spending Pattern Analysis**: Identify spending habits and optimization opportunities
- **Interactive Dashboards**: Real-time charts and visualizations

### 🔒 **Privacy & Security**
- **Permission-Based Data Access**: Granular control over which data categories AI can access
- **JWT Authentication**: Secure user authentication and session management
- **Data Encryption**: Secure storage and transmission of financial data
- **Privacy Controls**: Users control their data sharing preferences

---

## 🛠 Tech Stack

### 🌐 **Frontend**
- **React 18** with Vite for fast development and building
- **Tailwind CSS** for responsive and modern UI design
- **Shadcn/ui** for accessible and beautiful component library
- **Framer Motion** for smooth animations and transitions
- **Chart.js & Recharts** for interactive data visualizations
- **React Router** for client-side routing
- **Axios** for API communication

### 🧠 **Backend**
- **Django 5.0** with Django REST Framework
- **MongoDB** with MongoEngine ODM for flexible data storage
- **JWT Authentication** with SimpleJWT for secure sessions
- **CORS** support for cross-origin requests

### 🤖 **AI & Machine Learning**
- **Scikit-learn** for ML algorithms (Isolation Forest, Linear Regression, K-Means)
- **NumPy & Pandas** for data processing and analysis
- **Natural Language Processing** for conversational AI
- **Prophet** for time series forecasting
- **Statsmodels** for statistical analysis

### 🗃️ **Database**
- **MongoDB** for flexible document storage
- **MongoEngine** for Python object-document mapping

---

## 📁 Project Structure

```
TrackSpendAI/
├── 📁 frontend/                    # React frontend application
│   ├── 📁 src/
│   │   ├── 📁 components/          # Reusable UI components
│   │   │   ├── 📁 ui/             # Shadcn/ui components
│   │   │   ├── Layout.jsx         # Main layout wrapper
│   │   │   ├── Sidebar.jsx        # Navigation sidebar
│   │   │   └── PermissionManager.jsx # Data permission controls
│   │   ├── 📁 pages/              # Page components
│   │   │   ├── Dashboard.jsx      # Main dashboard
│   │   │   ├── Analytics.jsx      # Financial analytics & scoring
│   │   │   ├── Suggestions.jsx    # AI-powered suggestions
│   │   │   ├── Livechat.jsx       # Natural language chat
│   │   │   ├── Transactions.jsx   # Transaction management
│   │   │   ├── Budgets.jsx        # Budget planning
│   │   │   ├── Goals.jsx          # Financial goals
│   │   │   ├── Debttracker.jsx    # Debt management
│   │   │   ├── Portfolio.jsx      # Investment tracking
│   │   │   └── Accounts.jsx       # Account management
│   │   ├── 📁 lib/                # Utility functions
│   │   └── 📁 hooks/              # Custom React hooks
│   ├── package.json
│   └── vite.config.js
├── 📁 backend/                     # Django backend API
│   ├── 📁 api/                    # API application
│   │   ├── 📁 predict/            # ML prediction models
│   │   ├── models.py              # MongoDB data models
│   │   ├── views.py               # API endpoints
│   │   ├── serializers.py         # Data serialization
│   │   ├── urls.py                # URL routing
│   │   ├── ai_chat_views.py       # AI chat endpoints
│   │   ├── suggestions_views.py   # AI suggestions API
│   │   ├── natural_language_views.py # NLP chat API
│   │   ├── ml_suggestions_engine.py # ML recommendation engine
│   │   ├── natural_language_engine.py # NLP processing
│   │   ├── ai_insights_engine.py  # Financial insights AI
│   │   └── financial_data_manager.py # Data management
│   ├── 📁 item_service/           # Django project settings
│   ├── requirements.txt           # Python dependencies
│   └── manage.py
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v18 or higher)
- **Python** (v3.11 or higher)
- **MongoDB** (v5.0 or higher)
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/TrackSpendAI.git
   cd TrackSpendAI
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Edit .env with your MongoDB connection and other settings
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   
   # Install dependencies
   npm install
   # or
   pnpm install
   ```

4. **Database Setup**
   ```bash
   # Make sure MongoDB is running
   # The app will automatically create the database and collections
   ```

### Running the Application

1. **Start the Backend Server**
   ```bash
   cd backend
   python manage.py runserver
   ```
   Backend will be available at `http://localhost:8000`

2. **Start the Frontend Development Server**
   ```bash
   cd frontend
   npm run dev
   # or
   pnpm dev
   ```
   Frontend will be available at `http://localhost:5173`

3. **Access the Application**
   Open your browser and navigate to `http://localhost:5173`

---

## 🔧 Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
MONGODB_URI=mongodb://localhost:27017/trackspendai
MONGODB_DATABASE_NAME=trackspendai

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOWED_ORIGIN_REGEXES=^https://.*\.vercel\.app$

# Email Settings (Optional)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 🤖 AI Features Deep Dive

### 1. **Natural Language Chat**
- **Context Awareness**: Maintains conversation context across multiple queries
- **Intent Recognition**: Understands user queries about spending, income, budgets, etc.
- **Smart Responses**: Provides direct answers with actionable suggestions
- **Query Types**: Supports spending analysis, income tracking, balance inquiries, and more

### 2. **ML-Powered Suggestions**
- **Anomaly Detection**: Uses Isolation Forest to identify unusual spending patterns
- **Predictive Analytics**: Linear Regression for future savings forecasting
- **Spending Clustering**: K-Means clustering to identify spending behavior patterns
- **Debt Optimization**: Heuristic algorithms for optimal debt repayment strategies
- **Investment Analysis**: Portfolio assessment and optimization recommendations

### 3. **Financial Health Scoring**
- **Health Score (0-100)**: Based on 5 key factors:
  - Savings Rate (40% weight)
  - Income Stability (25% weight)
  - Income Growth (15% weight)
  - Expense Control (10% weight)
  - Budget Adherence (10% weight)

- **Credit Score (300-850)**: Simulated based on:
  - Payment History (30%)
  - Credit Utilization (25%)
  - Debt-to-Income Ratio (20%)
  - Length of Credit History (15%)
  - Financial Stability Bonus (10%)

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/refresh/` - Token refresh

### Financial Data
- `GET /api/transactions/` - Get user transactions
- `POST /api/transactions/` - Create transaction
- `GET /api/accounts/` - Get user accounts
- `GET /api/budgets/` - Get user budgets
- `GET /api/goals/` - Get financial goals

### AI Features
- `POST /api/ai/chat/` - Basic AI chat
- `POST /api/ai/natural-chat/` - Natural language chat
- `GET /api/ai/suggestions/` - AI-powered suggestions
- `GET /api/ai/insights/` - Financial insights
- `GET /api/ai/conversation-history/` - Chat history

### Permissions
- `GET /api/permissions/` - Get user permissions
- `POST /api/permissions/` - Update permissions

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

### AI Feature Tests
```bash
cd backend
python test_ai_assistant.py
python test_suggestions.py
python test_natural_language.py
```

---

## 🚀 Deployment

### Frontend (Vercel)
1. Connect your GitHub repository to Vercel
2. Set build command: `npm run build`
3. Set output directory: `dist`
4. Deploy!

### Backend (Railway/Heroku)
1. Create a new project on Railway/Heroku
2. Connect your GitHub repository
3. Set environment variables
4. Deploy!

### Database (MongoDB Atlas)
1. Create a MongoDB Atlas cluster
2. Get connection string
3. Update environment variables
4. Deploy!

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Shadcn/ui** for the beautiful component library
- **Tailwind CSS** for the utility-first CSS framework
- **Django REST Framework** for the robust API framework
- **MongoDB** for the flexible document database
- **Scikit-learn** for machine learning capabilities

---

## 📞 Support

If you have any questions or need help, please:

1. Check the [Issues](https://github.com/your-username/TrackSpendAI/issues) page
2. Create a new issue with detailed description
3. Contact us at support@trackspendai.com

---

## 🔮 Roadmap

- [ ] **Mobile App**: React Native mobile application
- [ ] **Bank Integration**: Direct bank account connections
- [ ] **Advanced ML**: Deep learning models for better predictions
- [ ] **Multi-Currency**: Support for multiple currencies
- [ ] **Team Features**: Family/team financial management
- [ ] **Tax Integration**: Tax planning and filing assistance
- [ ] **Investment Tracking**: Real-time investment portfolio tracking
- [ ] **Voice Commands**: Voice-activated financial queries

---

<div align="center">

**Made with ❤️ by the TrackSpendAI Team**

[⭐ Star this repo](https://github.com/your-username/TrackSpendAI) | [🐛 Report Bug](https://github.com/your-username/TrackSpendAI/issues) | [💡 Request Feature](https://github.com/your-username/TrackSpendAI/issues)

</div>