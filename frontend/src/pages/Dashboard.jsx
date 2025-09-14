
"use client";

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import {
  Bell,
  Menu,
  TrendingUp,
  TrendingDown,
  CalendarIcon,
  AlertTriangle,
  CheckCircle,
  Info,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Sidebar } from "@/components/Sidebar";
import { Calendar } from "@/components/ui/calendar";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { API_BASE } from "@/lib/api";

const Dashboard = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [account, setAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [showAllAlerts, setShowAllAlerts] = useState(false);
  const accountName = localStorage.getItem("selectedAccountName");

  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const accountId = localStorage.getItem("selectedAccountId");
        const userId = localStorage.getItem("userId");

        if (accountId) {
          const accRes = await axios.get(`${API_BASE}/accounts/${accountId}/`);
          setAccount(accRes.data);

          const txnRes = await axios.get(
            `${API_BASE}/transactions/accounts/${accountId}`
          );
          const sortedTxns = txnRes.data.sort(
            (a, b) => new Date(b.date) - new Date(a.date)
          );
          const recentTxns = sortedTxns.slice(0, 5);
          setTransactions(recentTxns);
        }

        if (userId) {
          const alertsRes = await axios.get(
            `${API_BASE}/ml/anomalies/users/${userId}/`
          );
          setAlerts(alertsRes.data || []);
        }
      } catch (error) {
        console.error("❌ Failed to load dashboard data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  const getTotals = (txns, account) => {
    if (!localStorage.getItem("userId")) {
      return { balance: 0, income: 0, expenses: 0, savingsRate: 0 };
    }

    let income = 0;
    let expenses = 0;
    txns.forEach((txn) => {
      const amount = Number.parseFloat(txn.amount) || 0;
      if (txn.type === "income") income += amount;
      else if (txn.type === "expense") expenses += amount;
    });

    const balance =
      account?.total_balance != null
        ? Number.parseFloat(account.total_balance)
        : (Number.parseFloat(account?.initial_balance) || 0) +
          income -
          expenses;

    const savingsRate =
      income > 0 ? (((income - expenses) / income) * 100).toFixed(2) : 0;

    return {
      balance: Number.parseFloat(balance.toFixed(2)),
      income: Number.parseFloat(income.toFixed(2)),
      expenses: Number.parseFloat(expenses.toFixed(2)),
      savingsRate: Number.parseFloat(savingsRate),
    };
  };

  const totals = getTotals(transactions, account);

  const handleLogout = () => {
    localStorage.clear();
    navigate("/");
  };

  const dismissAlert = (idx) => {
    setAlerts((prev) => prev.filter((_, i) => i !== idx));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-foreground">
              Loading Dashboard
            </h3>
            <p className="text-muted-foreground">
              Preparing your financial overview...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        handleLogout={handleLogout}
      />

      <main className="flex-1 overflow-y-auto">
        <header className="bg-card border-b border-border px-4 sm:px-6 py-4 sticky top-0 z-30 backdrop-blur-sm bg-card/95">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 sm:space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden"
              >
                <Menu className="w-5 h-5" />
              </Button>
              <div>
                <h1 className="text-lg sm:text-2xl font-bold text-blue-700 dark:text-blue-300 flex flex-wrap items-center gap-2">
                  <span>Financial Dashboard</span>
                  {accountName && (
                    <span className="text-sm sm:text-base font-medium text-slate-600 dark:text-slate-400">
                      ({accountName})
                    </span>
                  )}
                </h1>
                <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400">
                  {new Date().toLocaleDateString("en-US", {
                    weekday: "long",
                    month: "long",
                    day: "numeric",
                    year: "numeric",
                  })}
                </p>
              </div>
            </div>
          </div>
        </header>

        <div className="p-4 sm:p-6 space-y-6 sm:space-y-8">
          {children ? (
            children
          ) : (
            <>
              {/* Stats Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6">
                <StatCard
                  title="Total Balance"
                  value={`₹${totals.balance.toLocaleString()}`}
                  trend={totals.balance >= 0 ? "up" : "down"}
                  color="blue"
                />
                <StatCard
                  title="Total Income"
                  value={`₹${totals.income.toLocaleString()}`}
                  trend="up"
                  color="green"
                />
                <StatCard
                  title="Total Expenses"
                  value={`₹${totals.expenses.toLocaleString()}`}
                  trend="down"
                  color="red"
                />
                <StatCard
                  title="Savings Rate"
                  value={`${totals.savingsRate}%`}
                  trend={totals.savingsRate > 0 ? "up" : "down"}
                  color="purple"
                />
              </div>

              {alerts.length > 0 && (
                <Card className="border-0 shadow-lg bg-gradient-to-r from-warning/10 to-destructive/10 border-l-4 border-l-warning">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg font-semibold text-amber-700 dark:text-amber-300 flex items-center gap-2">
                      <Bell className="w-5 h-5" />
                      Financial Alerts
                      <Badge variant="destructive" className="ml-auto">
                        {alerts.length}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {(showAllAlerts ? alerts : alerts.slice(0, 3)).map(
                        (alert, idx) => (
                          <AlertCard
                            key={idx}
                            alert={alert}
                            onDismiss={() => dismissAlert(idx)}
                          />
                        )
                      )}
                      {alerts.length > 3 && (
                        <div className="text-center pt-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setShowAllAlerts((p) => !p)}
                          >
                            {showAllAlerts
                              ? "Show Less"
                              : `View All ${alerts.length} Alerts`}
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Recent Transactions */}
                <div className="lg:col-span-2 order-2 lg:order-1">
                  <Card className="border-0 shadow-lg h-full">
                    <CardHeader className="pb-5">
                      <CardTitle className="text-xl font-semibold text-indigo-700 dark:text-indigo-300 flex items-center justify-between">
                        Recent Transactions
                        <Badge variant="secondary">{transactions.length}</Badge>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <TransactionList data={transactions} />
                    </CardContent>
                  </Card>
                </div>

                <div className="order-1 lg:order-2">
                  <Card className="border-0 shadow-lg h-full">
                    <CardHeader className="pb-4">
                      <CardTitle className="text-lg font-semibold text-purple-700 dark:text-purple-300 flex items-center gap-2">
                        <CalendarIcon className="w-5 h-5" />
                        Transaction Calendar
                      </CardTitle>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        Days with transactions are highlighted
                      </p>
                    </CardHeader>
                    <CardContent className="p-4">
                      <div className="flex justify-center">
                        <Calendar
                          mode="single"
                          selected={selectedDate}
                          onSelect={setSelectedDate}
                          modifiers={{
                            hasTransaction: transactions.map(
                              (t) => new Date(t.date)
                            ),
                          }}
                          modifiersClassNames={{
                            hasTransaction:
                              "bg-primary text-primary-foreground font-semibold rounded-full",
                          }}
                          className="rounded-lg border shadow-sm w-full max-w-sm mx-auto"
                          classNames={{
                            months: "flex flex-col space-y-4",
                            month: "space-y-4",
                            caption:
                              "flex justify-center pt-1 relative items-center",
                            caption_label: "text-sm font-medium",
                            nav: "space-x-1 flex items-center",
                            nav_button:
                              "h-7 w-7 bg-transparent p-0 opacity-50 hover:opacity-100",
                            nav_button_previous: "absolute left-1",
                            nav_button_next: "absolute right-1",
                            table: "w-full border-collapse space-y-1",
                            head_row: "flex",
                            head_cell:
                              "text-muted-foreground rounded-md w-8 font-normal text-[0.8rem]",
                            row: "flex w-full mt-2",
                            cell: "text-center text-sm p-0 relative [&:has([aria-selected])]:bg-accent first:[&:has([aria-selected])]:rounded-l-md last:[&:has([aria-selected])]:rounded-r-md focus-within:relative focus-within:z-20",
                            day: "h-8 w-8 p-0 font-normal aria-selected:opacity-100 hover:bg-accent hover:text-accent-foreground rounded-md transition-colors",
                            day_selected:
                              "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground focus:bg-primary focus:text-primary-foreground",
                            day_today:
                              "bg-accent text-accent-foreground font-semibold",
                            day_outside: "text-muted-foreground opacity-50",
                            day_disabled: "text-muted-foreground opacity-50",
                            day_range_middle:
                              "aria-selected:bg-accent aria-selected:text-accent-foreground",
                            day_hidden: "invisible",
                          }}
                        />
                      </div>
                      {selectedDate && (
                        <div className="mt-4 p-3 bg-muted rounded-lg">
                          <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                            {selectedDate.toLocaleDateString("en-US", {
                              weekday: "long",
                              month: "long",
                              day: "numeric",
                            })}
                          </p>
                          <p className="text-xs text-slate-600 dark:text-slate-400">
                            {
                              transactions.filter(
                                (t) =>
                                  new Date(t.date).toDateString() ===
                                  selectedDate.toDateString()
                              ).length
                            }{" "}
                            transaction(s)
                          </p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
};

const AlertCard = ({ alert, onDismiss }) => {
  const getAlertIcon = (type) => {
    switch (type) {
      case "warning":
        return <AlertTriangle className="w-4 h-4" />;
      case "success":
        return <CheckCircle className="w-4 h-4" />;
      default:
        return <Info className="w-4 h-4" />;
    }
  };

  const getAlertColor = (type) => {
    switch (type) {
      case "warning":
        return "border-warning bg-warning/10 text-warning-foreground";
      case "success":
        return "border-success bg-success/10 text-success-foreground";
      default:
        return "border-primary bg-primary/10 text-primary-foreground";
    }
  };

  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-lg border-l-4 ${getAlertColor(
        alert.type || "info"
      )} bg-card`}
    >
      <div className="flex-shrink-0 mt-0.5">{getAlertIcon(alert.type)}</div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-slate-800 dark:text-slate-200">
          {alert.description || "Unusual transaction detected"}
        </p>
        {alert.transaction && (
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            {alert.transaction.category} • ₹
            {Number(alert.transaction.amount).toLocaleString()}
          </p>
        )}
      </div>

      {/* Close button */}
      <button
        onClick={onDismiss}
        className="text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
      >
        <X className="w-4 h-4" />
      </button>

      {/* Details Dialog */}
      <Dialog>
        <DialogTrigger asChild>
          <Button
            size="sm"
            variant="outline"
            className="flex-shrink-0 bg-transparent ml-2"
          >
            Details
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {getAlertIcon(alert.type)}
              Alert Details
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="p-4 bg-muted rounded-lg">
              <p className="font-medium text-sm">
                {alert.description || "Unusual transaction detected"}
              </p>
            </div>
            {alert.transaction && (
              <div className="space-y-3">
                <h4 className="font-semibold text-sm">
                  Transaction Information
                </h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-muted-foreground">Type</p>
                    <p className="font-medium capitalize">
                      {alert.transaction.type}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Amount</p>
                    <p className="font-medium">
                      ₹{Number(alert.transaction.amount).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Category</p>
                    <p className="font-medium">{alert.transaction.category}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Date</p>
                    <p className="font-medium">
                      {new Date(alert.transaction.date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                {alert.transaction.description && (
                  <div>
                    <p className="text-muted-foreground text-sm">Description</p>
                    <p className="font-medium text-sm">
                      {alert.transaction.description}
                    </p>
                  </div>
                )}
                {alert.transaction.is_recurring && (
                  <Badge variant="secondary" className="w-fit">
                    Recurring Transaction
                  </Badge>
                )}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

const StatCard = ({ title, value, trend, percent, color }) => {
  const Icon = trend === "up" ? TrendingUp : TrendingDown;
  const colorClasses = {
    blue: "from-blue-500 to-blue-600",
    green: "from-green-500 to-green-600",
    red: "from-red-500 to-red-600",
    purple: "from-purple-500 to-purple-600",
  };

  return (
    <Card className="border-0 shadow-lg card-hover group">
      <CardContent className="p-4 sm:p-6">
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 font-medium">
            {title}
          </p>
          <div
            className={`w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-r ${colorClasses[color]} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}
          >
            <Icon className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
          </div>
        </div>
        <div className="flex items-end justify-between">
          <h3 className="text-lg sm:text-2xl font-bold text-slate-800 dark:text-slate-200">
            {value}
          </h3>
          <Badge variant="secondary" className="text-xs">
            {percent}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
};

const TransactionList = ({ data }) => {
  return (
    <div className="space-y-3 max-h-80 overflow-y-auto">
      {data.slice(0, 5).map((item, index) => (
        <div
          key={index}
          className="flex items-center justify-between p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors duration-200 group"
        >
          <div className="flex items-center space-x-3 min-w-0 flex-1">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                item.type === "income"
                  ? "bg-green-100 text-green-600 dark:bg-green-900/20 dark:text-green-400"
                  : "bg-red-100 text-red-600 dark:bg-red-900/20 dark:text-red-400"
              }`}
            >
              {item.type === "income" ? (
                <TrendingUp className="w-5 h-5" />
              ) : (
                <TrendingDown className="w-5 h-5" />

              )}
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-medium text-slate-800 dark:text-slate-200 truncate">
                {item.category}
              </p>
              <p className="text-sm text-slate-600 dark:text-slate-400 truncate">
                {item.description || "No description"}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-500">
                {new Date(item.date).toLocaleDateString()}
              </p>
            </div>
          </div>
          <div className="text-right flex-shrink-0 ml-2">
            <span
              className={`font-semibold text-sm sm:text-base ${
                item.type === "income"
                  ? "text-green-600 dark:text-green-400"
                  : "text-red-600 dark:text-red-400"
              }`}
            >
              {item.type === "income" ? "+" : "-"}₹
              {Number(item.amount).toLocaleString()}
            </span>
          </div>
        </div>
      ))}
      {data.length === 0 && (
        <div className="text-center py-12 text-muted-foreground">
          <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
            <TrendingUp className="w-8 h-8" />
          </div>
          <p className="font-medium text-slate-700 dark:text-slate-300">
            No transactions yet
          </p>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Start by adding your first transaction
          </p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
