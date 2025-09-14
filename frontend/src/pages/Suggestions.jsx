import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Info,
  Lightbulb,
  Target,
  DollarSign,
  CreditCard,
  PiggyBank,
  BarChart3,
  Home,
  Briefcase,
  ShoppingCart,
  Filter,
  RefreshCw,
  Shield,
  Zap,
  Star,
  ArrowRight,
  Calendar,
  Users,
  PieChart,
  Brain,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { API_BASE } from "@/lib/api";
import axios from "axios";

const Suggestions = () => {
  const [suggestions, setSuggestions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [permissions, setPermissions] = useState({});
  const [mlEnabled, setMlEnabled] = useState(true);
  const [mlSuggestions, setMlSuggestions] = useState([]);

  useEffect(() => {
    fetchCategories();
    fetchSuggestions("all");
    fetchUserPermissions();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API_BASE}/ai/suggestions/categories/`);
      setCategories(response.data.categories);
    } catch (error) {
      console.error("Error fetching categories:", error);
    }
  };

  const fetchSuggestions = async (category) => {
    setLoading(true);
    setError(null);
    
    try {
      const userId = localStorage.getItem("userId") || "user_001";
      const response = await axios.get(`${API_BASE}/ai/suggestions/`, {
        params: {
          user_id: userId,
          category: category,
          use_ml: mlEnabled,
        },
      });
      
      const allSuggestions = response.data.suggestions;
      const mlSuggestions = allSuggestions.filter(s => s.ml_generated);
      const regularSuggestions = allSuggestions.filter(s => !s.ml_generated);
      
      setSuggestions(allSuggestions);
      setMlSuggestions(mlSuggestions);
      setSelectedCategory(category);
    } catch (error) {
      console.error("Error fetching suggestions:", error);
      setError("Failed to load suggestions. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const fetchUserPermissions = async () => {
    try {
      const userId = localStorage.getItem("userId") || "user_001";
      const response = await axios.get(`${API_BASE}/permissions/status/?user_id=${userId}`);
      setPermissions(response.data.permissions || {});
    } catch (error) {
      console.error("Error fetching permissions:", error);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case "high":
        return "bg-red-100 text-red-800 border-red-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "low":
        return "bg-green-100 text-green-800 border-green-200";
      case "success":
        return "bg-emerald-100 text-emerald-800 border-emerald-200";
      case "info":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case "high":
        return <AlertTriangle className="w-4 h-4" />;
      case "medium":
        return <Info className="w-4 h-4" />;
      case "low":
        return <CheckCircle className="w-4 h-4" />;
      case "success":
        return <Star className="w-4 h-4" />;
      case "info":
        return <Info className="w-4 h-4" />;
      default:
        return <Lightbulb className="w-4 h-4" />;
    }
  };

  const getCategoryIcon = (categoryId) => {
    switch (categoryId) {
      case "debt":
        return <CreditCard className="w-5 h-5" />;
      case "account":
        return <Briefcase className="w-5 h-5" />;
      case "loan":
        return <Home className="w-5 h-5" />;
      case "investment":
        return <TrendingUp className="w-5 h-5" />;
      case "budget":
        return <BarChart3 className="w-5 h-5" />;
      case "savings":
        return <PiggyBank className="w-5 h-5" />;
      case "spending":
        return <ShoppingCart className="w-5 h-5" />;
      default:
        return <Target className="w-5 h-5" />;
    }
  };

  const getCategoryColor = (color) => {
    const colorMap = {
      blue: "bg-blue-500",
      red: "bg-red-500",
      green: "bg-green-500",
      purple: "bg-purple-500",
      emerald: "bg-emerald-500",
      orange: "bg-orange-500",
      yellow: "bg-yellow-500",
      pink: "bg-pink-500",
    };
    return colorMap[color] || "bg-gray-500";
  };

  const groupedSuggestions = suggestions.reduce((acc, suggestion) => {
    const category = suggestion.category || "other";
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(suggestion);
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-4 sm:p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              🤖 AI-Powered Financial Suggestions
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Get personalized, actionable insights to optimize your financial health. 
              All suggestions are based on your data and respect your privacy settings.
            </p>
          </motion.div>
        </div>

        {/* ML Status & Permission Status */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="space-y-4"
        >
          {/* ML Status */}
          <Card className="border-l-4 border-l-purple-500 bg-purple-50/50">
            <CardContent className="p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Brain className="w-5 h-5 text-purple-600" />
                  <h3 className="font-semibold text-purple-800">Machine Learning Engine</h3>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={mlEnabled ? "default" : "secondary"} className={mlEnabled ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"}>
                    {mlEnabled ? "🟢 ML Enabled" : "⚪ ML Disabled"}
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setMlEnabled(!mlEnabled);
                      fetchSuggestions(selectedCategory);
                    }}
                    className="text-xs"
                  >
                    {mlEnabled ? "Disable ML" : "Enable ML"}
                  </Button>
                </div>
              </div>
              <p className="text-sm text-purple-700">
                {mlEnabled 
                  ? "Advanced ML algorithms analyze your patterns for intelligent predictions and anomaly detection."
                  : "Using traditional rule-based suggestions. Enable ML for advanced insights."
                }
              </p>
              {mlSuggestions.length > 0 && (
                <div className="mt-2">
                  <Badge variant="outline" className="bg-purple-100 text-purple-800 border-purple-300">
                    🧠 {mlSuggestions.length} ML-Powered Insights Available
                  </Badge>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Permission Status */}
          {Object.keys(permissions).length > 0 && (
            <Card className="border-l-4 border-l-blue-500 bg-blue-50/50">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-blue-800">Data Access Permissions</h3>
                </div>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(permissions).map(([key, value]) => (
                    <Badge
                      key={key}
                      variant={value ? "default" : "secondary"}
                      className={value ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"}
                    >
                      {key.charAt(0).toUpperCase() + key.slice(1)}: {value ? "Enabled" : "Disabled"}
                    </Badge>
                  ))}
                </div>
                <p className="text-sm text-blue-700 mt-2">
                  Suggestions are only generated for data categories you've granted access to.
                </p>
              </CardContent>
            </Card>
          )}
        </motion.div>

        {/* Category Filter */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Filter className="w-5 h-5" />
                Filter Suggestions by Category
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4">
                {categories.map((category) => (
                  <Button
                    key={category.id}
                    variant={selectedCategory === category.id ? "default" : "outline"}
                    onClick={() => fetchSuggestions(category.id)}
                    disabled={loading}
                    className={`h-auto p-4 flex flex-col items-center justify-center gap-3 min-h-[100px] w-full ${
                      selectedCategory === category.id
                        ? `${getCategoryColor(category.color)} text-white hover:opacity-90`
                        : "hover:bg-gray-50"
                    }`}
                  >
                    <span className="text-xl flex items-center justify-center">{category.icon}</span>
                    <span className="text-xs font-medium text-center leading-tight break-all px-2 w-full">{category.name}</span>
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Loading State */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-center items-center py-12"
          >
            <div className="flex items-center gap-3">
              <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />
              <span className="text-lg font-medium text-gray-600">
                Analyzing your financial data...
              </span>
            </div>
          </motion.div>
        )}

        {/* Error State */}
        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex justify-center"
          >
            <Card className="border-red-200 bg-red-50 max-w-md">
              <CardContent className="p-6 text-center">
                <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                <h3 className="font-semibold text-red-800 mb-2">Error Loading Suggestions</h3>
                <p className="text-red-600 mb-4">{error}</p>
                <Button onClick={() => fetchSuggestions(selectedCategory)} variant="outline">
                  Try Again
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Suggestions */}
        {!loading && !error && suggestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="space-y-6"
          >
            {Object.entries(groupedSuggestions).map(([category, categorySuggestions]) => (
              <div key={category} className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${getCategoryColor(categories.find(c => c.id === category)?.color || 'gray')}`}>
                    {getCategoryIcon(category)}
                  </div>
                  <h2 className="text-xl font-semibold text-gray-800 capitalize">
                    {categories.find(c => c.id === category)?.name || category} Suggestions
                  </h2>
                  <Badge variant="secondary">{categorySuggestions.length}</Badge>
                </div>

                <div className="grid gap-4">
                  <AnimatePresence>
                    {categorySuggestions.map((suggestion, index) => (
                      <motion.div
                        key={`${suggestion.type}-${index}`}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.4, delay: index * 0.1 }}
                      >
                        <Card className={`border-l-4 ${
                          suggestion.priority === 'high' ? 'border-l-red-500 bg-red-50/30' :
                          suggestion.priority === 'medium' ? 'border-l-yellow-500 bg-yellow-50/30' :
                          suggestion.priority === 'low' ? 'border-l-green-500 bg-green-50/30' :
                          'border-l-blue-500 bg-blue-50/30'
                        } hover:shadow-lg transition-shadow duration-300 ${suggestion.ml_generated ? 'ring-2 ring-purple-200' : ''}`}>
                          <CardContent className="p-6">
                            <div className="flex items-start justify-between mb-4">
                              <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-full ${
                                  suggestion.priority === 'high' ? 'bg-red-100' :
                                  suggestion.priority === 'medium' ? 'bg-yellow-100' :
                                  suggestion.priority === 'low' ? 'bg-green-100' :
                                  'bg-blue-100'
                                }`}>
                                  {getPriorityIcon(suggestion.priority)}
                                </div>
                                <div>
                                  <div className="flex items-center gap-2 mb-1">
                                    <h3 className="font-semibold text-gray-800 text-lg">
                                      {suggestion.title}
                                    </h3>
                                    {suggestion.ml_generated && (
                                      <Badge variant="outline" className="bg-purple-100 text-purple-800 border-purple-300 text-xs">
                                        🧠 ML
                                      </Badge>
                                    )}
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <Badge className={`${getPriorityColor(suggestion.priority)} mt-1`}>
                                      {suggestion.priority?.charAt(0).toUpperCase() + suggestion.priority?.slice(1)} Priority
                                    </Badge>
                                    {suggestion.ml_confidence && (
                                      <Badge variant="outline" className="bg-blue-100 text-blue-800 border-blue-300 text-xs">
                                        {suggestion.ml_confidence}
                                      </Badge>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>

                            <p className="text-gray-700 mb-4 leading-relaxed">
                              {suggestion.description}
                            </p>

                            {suggestion.action && (
                              <div className="bg-white/70 rounded-lg p-4 mb-4">
                                <div className="flex items-center gap-2 mb-2">
                                  <Zap className="w-4 h-4 text-blue-600" />
                                  <span className="font-medium text-blue-800">Recommended Action:</span>
                                </div>
                                <p className="text-blue-700">{suggestion.action}</p>
                              </div>
                            )}

                            {(suggestion.savings_potential || suggestion.potential_growth || suggestion.target_savings) && (
                              <div className="bg-green-50 rounded-lg p-4 mb-4">
                                <div className="flex items-center gap-2 mb-2">
                                  <DollarSign className="w-4 h-4 text-green-600" />
                                  <span className="font-medium text-green-800">Potential Impact:</span>
                                </div>
                                <p className="text-green-700">
                                  {suggestion.savings_potential || suggestion.potential_growth || suggestion.target_savings}
                                </p>
                              </div>
                            )}

                            {suggestion.accounts && (
                              <div className="bg-purple-50 rounded-lg p-4 mb-4">
                                <div className="flex items-center gap-2 mb-2">
                                  <Briefcase className="w-4 h-4 text-purple-600" />
                                  <span className="font-medium text-purple-800">Affected Accounts:</span>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                  {suggestion.accounts.map((account, idx) => (
                                    <Badge key={idx} variant="outline" className="text-purple-700 border-purple-300">
                                      {account}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}

                            {suggestion.investments && (
                              <div className="bg-emerald-50 rounded-lg p-4 mb-4">
                                <div className="flex items-center gap-2 mb-2">
                                  <TrendingUp className="w-4 h-4 text-emerald-600" />
                                  <span className="font-medium text-emerald-800">Investments:</span>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                  {suggestion.investments.map((investment, idx) => (
                                    <Badge key={idx} variant="outline" className="text-emerald-700 border-emerald-300">
                                      {investment}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}

                            {suggestion.budgets && (
                              <div className="bg-orange-50 rounded-lg p-4 mb-4">
                                <div className="flex items-center gap-2 mb-2">
                                  <BarChart3 className="w-4 h-4 text-orange-600" />
                                  <span className="font-medium text-orange-800">Budgets:</span>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                  {suggestion.budgets.map((budget, idx) => (
                                    <Badge key={idx} variant="outline" className="text-orange-700 border-orange-300">
                                      {budget}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}

                            {suggestion.percentage && (
                              <div className="bg-indigo-50 rounded-lg p-4">
                                <div className="flex items-center gap-2 mb-2">
                                  <PieChart className="w-4 h-4 text-indigo-600" />
                                  <span className="font-medium text-indigo-800">Percentage:</span>
                                </div>
                                <p className="text-indigo-700">{suggestion.percentage}</p>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                </div>
              </div>
            ))}
          </motion.div>
        )}

        {/* No Suggestions State */}
        {!loading && !error && suggestions.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex justify-center"
          >
            <Card className="max-w-md">
              <CardContent className="p-8 text-center">
                <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="font-semibold text-gray-800 mb-2">No Suggestions Available</h3>
                <p className="text-gray-600 mb-4">
                  {selectedCategory === "all" 
                    ? "We need more data to generate personalized suggestions. Try adding some transactions, accounts, or goals."
                    : `No suggestions available for ${categories.find(c => c.id === selectedCategory)?.name || selectedCategory}. Try a different category.`
                  }
                </p>
                <Button onClick={() => fetchSuggestions("all")} variant="outline">
                  View All Suggestions
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Footer Info */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="text-center py-8"
        >
          <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
            <CardContent className="p-6">
              <div className="flex items-center justify-center gap-2 mb-3">
                <Shield className="w-5 h-5 text-blue-600" />
                <span className="font-semibold text-blue-800">Privacy & Security</span>
              </div>
              <p className="text-blue-700 text-sm max-w-2xl mx-auto">
                All suggestions are generated locally using your data and respect your privacy settings. 
                No financial information is shared with external services. You can control data access 
                through the AI Insights page.
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default Suggestions;
