import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

import {
  TrendingUp,
  PieChart,
  Shield,
  Smartphone,
  CreditCard,
  Wallet,
  BarChart,
  BrainCircuit,
  Cpu,
  Repeat,
  AlertTriangle,
  ArrowRight,
  Bot
} from "lucide-react";

import { useNavigate } from "react-router-dom";

const HomePage = () => {
  const navigate = useNavigate();

  // const features = [
  //   {
  //     icon: <TrendingUp className="w-8 h-8" />,
  //     title: "Smart Analytics",
  //     description: "AI-powered insights to optimize your financial decisions",
  //   },
  //   {
  //     icon: <PieChart className="w-8 h-8" />,
  //     title: "Budget Tracking",
  //     description: "Visualize your spending patterns with interactive charts",
  //   },
  //   {
  //     icon: <Shield className="w-8 h-8" />,
  //     title: "Secure & Private",
  //     description: "Bank-level security to protect your financial data",
  //   },
  //   {
  //     icon: <Smartphone className="w-8 h-8" />,
  //     title: "Mobile Ready",
  //     description: "Access your finances anywhere, anytime",
  //   },
  // ];

  const features = [
  {
    icon: <TrendingUp className="w-8 h-8" />,
    title: "Smart Analytics",
    description: "AI-powered insights and trend detection to optimise spending & saving.",
  },
  {
    icon: <PieChart className="w-8 h-8" />,
    title: "Budget Tracking",
    description: "Create budgets, track progress and visualise category-wise spending.",
  },
  {
    icon: <Shield className="w-8 h-8" />,
    title: "Secure & Private",
    description: "Bank-level encryption and strict data privacy for all accounts.",
  },
  {
    icon: <Smartphone className="w-8 h-8" />,
    title: "Mobile Ready",
    description: "Full mobile support — manage finances anytime, anywhere.",
  },
  {
    icon: <CreditCard className="w-8 h-8" />,
    title: "Transaction Management",
    description: "Add, edit, categorise and reconcile transactions across accounts.",
  },
  {
    icon: <Wallet className="w-8 h-8" />,
    title: "Multi-account Support",
    description: "Link multiple bank accounts, wallets and cards in one place.",
  },
  {
    icon: <BarChart className="w-8 h-8" />,
    title: "Detailed Analytics",
    description: "Dashboards, charts and historical reports for better decisions.",
  },
  {
    icon: <BrainCircuit className="w-8 h-8" />,
    title: "AI Insights",
    description: "Personalised recommendations (save, invest, repay) driven by ML.",
  },
  {
    icon: <Cpu className="w-8 h-8" />,
    title: "Forecast & Planning",
    description: "Income/expense/balance forecasts and goal ETA predictions.",
  },
  {
    icon: <Repeat className="w-8 h-8" />,
    title: "Recurring Detection",
    description: "Auto-detect recurring payments and subscriptions to avoid surprises.",
  },
  {
    icon: <AlertTriangle className="w-8 h-8" />,
    title: "Anomaly Alerts",
    description: "Flag unusual spending and notify you instantly for investigation.",
  },
   {
    icon: <Bot className="w-8 h-8" />,
    title: "AI Chat Assistant",
    description: "Ask financial questions and get instant AI-powered answers.",
  },
];



  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                TrackSpend AI
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                onClick={() => navigate("/login")}
                className="hover:bg-blue-50"
              >
                Login
              </Button>
              <Button
                onClick={() => navigate("/signup")}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg hover:shadow-xl transition-all duration-300"
              >
                Sign Up
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <div className="animate-fade-in-up">
              <h1 className="text-5xl md:text-7xl font-bold mb-6">
                <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                  Smart Money
                </span>
                <br />
                <span className="text-gray-900">Management</span>
              </h1>
              <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
                Take control of your finances with AI-powered insights,
                automated tracking, and personalized recommendations. Make
                smarter financial decisions today.
              </p>
            </div>

            <div className="animate-fade-in-up animation-delay-200">
              <Button
                size="lg"
                onClick={() => navigate("/dashboard")}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 text-lg font-semibold shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-105"
              >
                Try This App
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </div>
          </div>
        </div>

        {/* Background Decorations */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-10 w-20 h-20 bg-blue-200 rounded-full opacity-20 animate-pulse"></div>
          <div className="absolute top-40 right-20 w-32 h-32 bg-purple-200 rounded-full opacity-20 animate-pulse animation-delay-1000"></div>
          <div className="absolute bottom-20 left-1/4 w-16 h-16 bg-pink-200 rounded-full opacity-20 animate-pulse animation-delay-2000"></div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Why Choose TrackSpend AI?
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Powerful features designed to simplify your financial life
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <Card
                key={index}
                className="group hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2"
              >
                <CardContent className="p-6 text-center">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300">
                    <div className="text-white">{feature.icon}</div>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

    

      {/* CTA Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Ready to Transform Your Finances?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Join thousands of users who are already making smarter financial
            decisions
          </p>
          <Button
            size="lg"
            onClick={() => navigate("/dashboard")}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 text-lg font-semibold shadow-2xl hover:shadow-3xl transition-all duration-300 transform hover:scale-105"
          >
            Start Your Journey
            <ArrowRight className="ml-2 w-5 h-5" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">TrackSpend AI</span>
            </div>
            <p className="text-gray-400">
              © 2025 TrackSpend AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
