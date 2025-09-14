import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Transactions from "./pages/Transactions";
import Accounts from "./pages/Accounts";
import Analytics from "./pages/Analytics";
import Reviews from "./pages/Reviews";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import FinancialDashboard from "./pages/Dashboard";
import HomePage from "./pages/Homepage";
import Portfolio from "./pages/Portfolio";
import Goals from "./pages/Goals";
import DebtTracker from "./pages/Debttracker";
import Budgets from "./pages/Budgets";
import Simulator from "./pages/Simulator";
import NeedHelp from "./pages/Needhelp";
import AIInsights from "./pages/Aiinsights";
import Livechat from "./pages/Livechat"
import IncomeSource from "./pages/IncomeSource"
import Suggestions from "./pages/Suggestions"
import { useEffect } from "react";

function App() {
  useEffect(() => {
    // reload only once on first visit
    if (!localStorage.getItem("siteReloadedOnce")) {
      localStorage.setItem("siteReloadedOnce", "true");
      window.location.reload();
    }
  }, []);

  return (
    <Router>
      <Routes>
        {/* Pages without layout */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* Pages with layout */}

        <Route path="/dashboard" element={<FinancialDashboard />} />
        <Route
          path="/transactions"
          element={
            <Layout
              title="Transactions"
              subtitle="Manage your income and expenses"
            >
              <Transactions />
            </Layout>
          }
        />
        <Route
          path="/accounts"
          element={
            <Layout title="Accounts" subtitle="Track your Accounts goals">
              <Accounts />
            </Layout>
          }
        />
        <Route
          path="/analytics"
          element={
            <Layout title="Analytics" subtitle="Financial insights and reports">
              <Analytics />
            </Layout>
          }
        />
        <Route
          path="/reviews"
          element={
            <Layout
              title="Reviews"
              subtitle="Review your financial performance"
            >
              <Reviews />
            </Layout>
          }
        />

        <Route
          path="/budgets"
          element={
            <Layout title="Budgets" subtitle="Plan and track your spending">
              <Budgets />
            </Layout>
          }
        />

        <Route
          path="/incomesource"
          element={
            <Layout
              title="Income Source"
              subtitle="Have a look at your financial performance"
            >
              <IncomeSource />
            </Layout>
          }
        />

        <Route
          path="/debt"
          element={
            <Layout
              title="Debt Tracker"
              subtitle="Monitor and manage your debts"
            >
              <DebtTracker />
            </Layout>
          }
        />
        <Route
          path="/goals"
          element={
            <Layout
              title="Financial Goals"
              subtitle="Set and achieve your targets"
            >
              <Goals />
            </Layout>
          }
        />
        <Route
          path="/portfolio"
          element={
            <Layout
              title="Investment Portfolio"
              subtitle="Track your investments"
            >
              <Portfolio />
            </Layout>
          }
        />
        <Route
          path="/simulator"
          element={
            <Layout
              title="Financial Simulator"
              subtitle="Plan your financial future"
            >
              <Simulator />
            </Layout>
          }
        />
        <Route
          path="/help"
          element={
            <Layout title="Help Center" subtitle="Get assistance and support">
              <NeedHelp />
            </Layout>
          }
        />
        <Route
          path="/ai-insights"
          element={
            <Layout
              title="AI Insights"
              subtitle="Smart financial recommendations"
            >
              <AIInsights />
            </Layout>
          }
        />
       
        <Route
          path="/livechat"
          element={
            <Layout title="livechat" subtitle="Ai live chat">
              <Livechat />
            </Layout>
          }
        />
        
        <Route
          path="/suggestions"
          element={
            <Layout title="AI Suggestions" subtitle="Personalized financial insights and recommendations">
              <Suggestions />
            </Layout>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;