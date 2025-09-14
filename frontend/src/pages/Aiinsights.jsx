

"use client";
import { API_BASE } from "@/lib/api";
import { useEffect, useMemo, useState, useCallback, useRef } from "react";
import axios from "axios";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
// 👆 sab imports same rakhna, bas ye extra icon add karo
import { Banknote } from "lucide-react";

import {
  Brain,
  RefreshCw,
  TrendingUp,
  Wallet,
  AlertTriangle,
  Repeat,
  Target,
  Loader2,
  Clock,
  BarChart3,
  Receipt,
  XCircle,
} from "lucide-react";

// =============================================
// CONFIG
// =============================================
const ML_BASE = `${API_BASE}/ml`;

// =============================================
// UTILS
// =============================================
const fmt = (n) => Number(n || 0).toLocaleString();
const inr = (n) => `₹${fmt(n)}`;

const asDate = (d) => {
  if (!d || d === "N/A") return null;
  try {
    return new Date(d);
  } catch {
    return null;
  }
};

const shortDate = (d) => {
  const dt = asDate(d);
  return dt ? dt.toLocaleString() : "N/A";
};

const capitalize = (s) =>
  typeof s === "string" && s.length ? s[0].toUpperCase() + s.slice(1) : s;

function toast(message, type = "success") {
  const el = document.createElement("div");
  el.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg z-50 animate-slide-in-right ${
    type === "success" ? "bg-green-600 text-white" : "bg-red-600 text-white"
  }`;
  el.innerHTML = `
    <div class="flex items-center gap-2">
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
      </svg>
      <span>${message}</span>
    </div>`;
  document.body.appendChild(el);
  setTimeout(() => {
    try {
      document.body.removeChild(el);
    } catch {}
  }, 2200);
}

// A tiny delay helper for UX sequencing
const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

// =============================================
// MAIN COMPONENT
// =============================================
const Aiinsights = () => {
  // user id
  const [userId, setUserId] = useState("");

  // ---- loading flags
  const [loadingAll, setLoadingAll] = useState(false);
  const [loadingForecast, setLoadingForecast] = useState(false);
  const [loadingAnoms, setLoadingAnoms] = useState(false);
  const [loadingRecurring, setLoadingRecurring] = useState(false);
  const [loadingEta, setLoadingEta] = useState(false);
  const [loadingAdvancedForecast, setLoadingAdvancedForecast] = useState(false);

  // ---- data
  const [forecast, setForecast] = useState(null);
  const [advancedForecast, setAdvancedForecast] = useState(null);
  const [anomsSummary, setAnomsSummary] = useState(null); // {created, anomaly_ids}
  const [recurringSummary, setRecurringSummary] = useState(null); // {created, pattern_ids}
  const [etas, setEtas] = useState([]); // results array

  // Persisted history lists (full detail)
  const [anomsList, setAnomsList] = useState([]); // Array of anomalies with joined transaction
  const [recurringList, setRecurringList] = useState([]); // Array of recurring patterns

  // ---- error states
  const [errForecast, setErrForecast] = useState("");
  const [errAdvancedForecast, setErrAdvancedForecast] = useState("");
  const [errAnoms, setErrAnoms] = useState("");
  const [errRecurring, setErrRecurring] = useState("");
  const [errEta, setErrEta] = useState("");

  // ---- timestamps
  const [tForecast, setTForecast] = useState(null);
  const [tAdvancedForecast, setTAdvancedForecast] = useState(null);
  const [tAnoms, setTAnoms] = useState(null);
  const [tRecurring, setTRecurring] = useState(null);
  const [tEta, setTEta] = useState(null);

  // ---- debt states
  const [loadingDebt, setLoadingDebt] = useState(false);
  const [debts, setDebts] = useState([]);
  const [errDebt, setErrDebt] = useState("");
  const [tDebt, setTDebt] = useState(null);

  // Forecast options
  const [forecastOptions, setForecastOptions] = useState({
    model: "holt",
    horizon: "month",
    periods: "",
    granularity: "daily",
    target_date: "",
  });

  // Keep a mounted flag to avoid state updates on unmounted
  const mountedRef = useRef(true);
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Load userId from localStorage on mount
  useEffect(() => {
    const id = localStorage.getItem("userId");
    if (id) setUserId(id);
  }, []);

  // ================================
  // API CALLERS
  // ================================
  const fetchForecast = useCallback(async () => {
    if (!userId) {
      // fallback when not logged in
      setForecast({
        predicted_income: 0,
        predicted_expense: 0,
        predicted_balance: 0,
        target_period: "N/A",
        confidence: 0,
        model_version: "v1",
        created_at: null,
      });
      return;
    }
    setLoadingForecast(true);
    try {
      const { data } = await axios.get(`${ML_BASE}/predict-expense/${userId}/`);
      if (!mountedRef.current) return;
      setForecast(data || null);
      setTForecast(new Date());
    } catch (err) {
      if (!mountedRef.current) return;
      setErrForecast(
        err?.response?.data?.error || err.message || "Failed to fetch forecast"
      );
    } finally {
      if (!mountedRef.current) return;
      setLoadingForecast(false);
    }
  }, [userId]);

  const fetchAdvancedForecast = useCallback(async () => {
    if (!userId) {
      setAdvancedForecast(null);
      return;
    }

    setLoadingAdvancedForecast(true);
    setErrAdvancedForecast("");

    try {
      // ✅ Step 1: check transaction count before hitting forecast API
      const { data: txData } = await axios.get(
        `${API_BASE}/transactions/count/${userId}/`
      );
      const txCount = txData?.count || 0;

      if (txCount < 10) {
        // show popup / toast instead of crashing API
        alert(
          "⚠️ Please add at least 10 transactions before using advanced forecast."
        );
        setLoadingAdvancedForecast(false);
        return;
      }

      // ✅ Step 2: prepare params only if enough data
      const params = {
        user_id: userId,
        model: forecastOptions.model,
        granularity: forecastOptions.granularity,
      };

      if (forecastOptions.periods) params.periods = forecastOptions.periods;
      else if (forecastOptions.horizon)
        params.horizon = forecastOptions.horizon;
      if (forecastOptions.target_date)
        params.target_date = forecastOptions.target_date;

      const { data } = await axios.get(`${API_BASE}/ml/forecast/`, { params });
      if (!mountedRef.current) return;
      setAdvancedForecast(data || null);
      setTAdvancedForecast(new Date());
    } catch (err) {
      if (!mountedRef.current) return;
      setErrAdvancedForecast(
        err?.response?.data?.error ||
          err.message ||
          "Failed to fetch advanced forecast"
      );
      console.error("Advanced forecast error:", err);
    } finally {
      if (!mountedRef.current) return;
      setLoadingAdvancedForecast(false);
    }
  }, [userId, forecastOptions]);

  // fetch full anomaly list (persisted history)
  const fetchAnomaliesList = useCallback(async () => {
    if (!userId) {
      setAnomsList([]); // no anomalies
      return;
    }
    try {
      const { data } = await axios.get(`${ML_BASE}/anomalies/users/${userId}/`);
      if (!mountedRef.current) return;
      const list = Array.isArray(data)
        ? data
        : Array.isArray(data?.results)
        ? data.results
        : [];
      setAnomsList(list);
    } catch (err) {
      if (!mountedRef.current) return;
      setAnomsList([]);
    }
  }, [userId]);

  // fetch full recurring list (persisted history)
  const fetchRecurringList = useCallback(async () => {
    if (!userId) {
      setEtas([]); // no goals
      return;
    }
    try {
      const { data } = await axios.get(`${ML_BASE}/recurring/users/${userId}/`);
      if (!mountedRef.current) return;
      const list = Array.isArray(data)
        ? data
        : Array.isArray(data?.results)
        ? data.results
        : [];
      setRecurringList(list);
    } catch (err) {
      if (!mountedRef.current) return;
      setRecurringList([]);
    }
  }, [userId]);

  const runAnomalyDetection = useCallback(async () => {
    if (!userId) return;
    setErrAnoms("");
    setLoadingAnoms(true);
    try {
      const { data } = await axios.post(`${ML_BASE}/anomalies/run/${userId}/`);
      if (!mountedRef.current) return;
      setAnomsSummary(data || null);
      setTAnoms(new Date());
      toast(`Anomaly scan complete • ${data?.created || 0} new`);
      // IMPORTANT: refresh full list so old + new show together
      await fetchAnomaliesList();
    } catch (err) {
      if (!mountedRef.current) return;
      setErrAnoms(
        err?.response?.data?.error || err.message || "Failed to run anomalies"
      );
      toast("Anomaly detection failed", "error");
    } finally {
      if (!mountedRef.current) return;
      setLoadingAnoms(false);
    }
  }, [userId, fetchAnomaliesList]);

  const runRecurringDetection = useCallback(async () => {
    if (!userId) return;
    setErrRecurring("");
    setLoadingRecurring(true);
    try {
      const { data } = await axios.post(`${ML_BASE}/recurring/run/${userId}/`);
      if (!mountedRef.current) return;
      setRecurringSummary(data || null);
      setTRecurring(new Date());
      toast(`Recurring patterns updated • ${data?.created || 0} new`);
      // refresh full list
      await fetchRecurringList();
    } catch (err) {
      if (!mountedRef.current) return;
      setErrRecurring(
        err?.response?.data?.error ||
          err.message ||
          "Failed to run recurring detection"
      );
      toast("Recurring detection failed", "error");
    } finally {
      if (!mountedRef.current) return;
      setLoadingRecurring(false);
    }
  }, [userId, fetchRecurringList]);

  const fetchGoalEtas = useCallback(async () => {
    if (!userId) return;
    setErrEta("");
    setLoadingEta(true);
    try {
      const { data } = await axios.get(`${ML_BASE}/goals/eta/${userId}/`);
      if (!mountedRef.current) return;
      const list = Array.isArray(data)
        ? data
        : Array.isArray(data?.results)
        ? data.results
        : [];
      setEtas(list);
      setTEta(new Date());
    } catch (err) {
      if (!mountedRef.current) return;
      setErrEta(
        err?.response?.data?.error || err.message || "Failed to fetch goal ETAs"
      );
    } finally {
      if (!mountedRef.current) return;
      setLoadingEta(false);
    }
  }, [userId]);

  const runAll = async () => {
    if (!userId) {
      toast("Missing userId in localStorage", "error");
      return;
    }
    setLoadingAll(true);
    try {
      // First load the read-only + history lists so old detections are visible.
      await Promise.all([
        fetchForecast(),
        fetchGoalEtas(),
        fetchAnomaliesList(),
        fetchRecurringList(),
      ]);
      // Then run mutating ones so new items append to the already shown lists
      await sleep(150); // tiny gap for nicer UX
      await runAnomalyDetection();
      await runRecurringDetection();
      toast("AI Insights refreshed");
    } finally {
      setLoadingAll(false);
    }
  };

  // Handle forecast option changes
  const handleForecastOptionChange = (field, value) => {
    setForecastOptions({ ...forecastOptions, [field]: value });
  };

  const fetchDebt = useCallback(async () => {
    if (!userId) return;
    setErrDebt("");
    setLoadingDebt(true);
    try {
      const { data } = await axios.get(`${ML_BASE}/debts/${userId}/`);
      if (!mountedRef.current) return;
      setDebts(data); // <- object directly save karna hai
      setTDebt(new Date());
    } catch (err) {
      if (!mountedRef.current) return;
      setErrDebt(
        err?.response?.data?.error || err.message || "Failed to fetch debts"
      );
    } finally {
      if (!mountedRef.current) return;
      setLoadingDebt(false);
    }
  }, [userId]);

  // auto-load read-only + history on userId ready
  useEffect(() => {
    if (!userId) return;
    fetchForecast();
    fetchGoalEtas();
    fetchAnomaliesList();
    fetchRecurringList();
    fetchDebt();
  }, [
    userId,
    fetchForecast,
    fetchGoalEtas,
    fetchAnomaliesList,
    fetchRecurringList,
    fetchDebt,
  ]);

  // helpers for Goal cards
  const progressPct = (curr, targ) => {
    const t = Number(targ || 0);
    if (t <= 0) return 0;
    const p = (Number(curr || 0) / t) * 100;
    return Math.max(0, Math.min(100, p));
  };

  // ================================
  // HEADER
  // ================================
  const HeaderBar = useMemo(
    () => (
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-4 sm:mb-6">
        {/* <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 grid place-items-center">
          <Brain className="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-white" />
        </div> */}
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            AI Insights
          </h1>
          <p className="text-xs sm:text-sm text-muted-foreground">
            Forecasts • Anomalies • Recurring • Goal ETA • Debts
          </p>
        </div>
      </div>
    ),
    [loadingAll]
  );

  // ================================
  // RENDER
  // ================================
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-3 sm:p-4 md:p-6 lg:p-8">
      {HeaderBar}

      <Tabs defaultValue="forecast" className="space-y-4 sm:space-y-6">
        <TabsList className="grid grid-cols-2 md:grid-cols-4 gap-1 sm:gap-2 w-full h-auto p-1">
          <TabsTrigger
            value="forecast"
            className="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm p-2 sm:p-3"
          >
            <BarChart3 className="w-3 h-3 sm:w-4 sm:h-4" />
            <span className="hidden sm:inline">Forecast</span>
            <span className="sm:hidden">Forecast</span>
          </TabsTrigger>
          <TabsTrigger
            value="anomalies"
            className="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm p-2 sm:p-3"
          >
            <AlertTriangle className="w-3 h-3 sm:w-4 sm:h-4" />
            <span className="hidden sm:inline">Anomalies</span>
            <span className="sm:hidden">Anomalies</span>
          </TabsTrigger>
          <TabsTrigger
            value="recurring"
            className="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm p-2 sm:p-3"
          >
            <Repeat className="w-3 h-3 sm:w-4 sm:h-4" />
            <span className="hidden sm:inline">Recurring</span>
            <span className="sm:hidden">Recurring</span>
          </TabsTrigger>
          <TabsTrigger
            value="goals"
            className="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm p-2 sm:p-3"
          >
            <Target className="w-3 h-3 sm:w-4 sm:h-4" />
            <span className="hidden sm:inline">Goal ETA</span>
            <span className="sm:hidden">Goals</span>
          </TabsTrigger>
          <TabsTrigger
            value="debts"
            className="flex items-center gap-1 sm:gap-2 text-xs sm:text-sm p-2 sm:p-3"
          >
            <Banknote className="w-3 h-3 sm:w-4 sm:h-4" />
            <span className="hidden sm:inline">Debts</span>
            <span className="sm:hidden">Debts</span>
          </TabsTrigger>
        </TabsList>

        {/* ================= FORECAST ================= */}
        <TabsContent value="forecast">
          <Card className="shadow-sm border border-gray-200">
            <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <CardTitle className="flex items-center gap-2 text-lg sm:text-x">
                <TrendingUp className="w-4 h-4 sm:w-5 sm:h-5" /> Monthly
                Forecast (Basic)
              </CardTitle>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                {tForecast && (
                  <span className="hidden sm:inline">
                    Updated: {shortDate(tForecast)}
                  </span>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={fetchForecast}
                  disabled={loadingForecast}
                  className="text-xs sm:text-sm bg-transparent"
                >
                  {loadingForecast ? (
                    <Loader2 className="w-3 h-3 sm:w-4 sm:h-4 animate-spin" />
                  ) : (
                    <RefreshCw className="w-3 h-3 sm:w-4 sm:h-4" />
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {errForecast && <ErrorAlert message={errForecast} />}

              {!forecast && !errForecast ? (
                <SkeletonRow label="Loading forecast" />
              ) : (
                forecast && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                    <StatTile
                      icon={<Wallet className="w-3 h-3 sm:w-4 sm:h-4" />}
                      label="Predicted Income"
                      value={inr(forecast?.predicted_income || 0)}
                    />
                    <StatTile
                      icon={<AlertTriangle className="w-3 h-3 sm:w-4 sm:h-4" />}
                      label="Predicted Expense"
                      value={inr(forecast?.predicted_expense || 0)}
                    />
                    <StatTile
                      icon={<TrendingUp className="w-3 h-3 sm:w-4 sm:h-4" />}
                      label="Predicted Balance"
                      value={inr(forecast?.predicted_balance || 0)}
                    />
                  </div>
                )
              )}

              {forecast && (
                <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground mt-2">
                  <Badge variant="secondary" className="text-xs">
                    Period: {forecast?.target_period || "—"}
                  </Badge>
                  <Badge variant="secondary" className="text-xs">
                    Confidence: {((forecast?.confidence || 0) * 100).toFixed(0)}
                    %
                  </Badge>
                  <Badge variant="secondary" className="text-xs">
                    Model: {forecast?.model_version || "v1"}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    Created: {shortDate(forecast?.created_at)}
                  </Badge>
                </div>
              )}

              <div className="mt-6 pt-10 border-t border-gray-200">
                <CardTitle className="flex items-center gap-2 text-lg sm:text-xl ">
                  <TrendingUp className="w-4 h-4 sm:w-5 sm:h-5 pt-10" />{" "}
                  Advanced Forecast Options
                </CardTitle>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                  {/* Forecast Type (Model) */}
                  <div>
                    <label className="text-sm font-medium mb-1 block">
                      Choose Forecast Method
                    </label>
                    <select
                      className="w-full p-2 border rounded-md text-sm"
                      value={forecastOptions.model}
                      onChange={(e) =>
                        handleForecastOptionChange("model", e.target.value)
                      }
                    >
                      <option value="holt">
                        🚀 Quick & Simple (Recommended)
                      </option>
                      <option value="arima">
                        📈 Trend-Based Forecast
                      </option>
                      <option value="sarima">
                        🔄 Seasonal Pattern Forecast
                      </option>
                      <option value="prophet">
                        🧠 Advanced AI Forecast
                      </option>
                      <option value="xgb">
                        🤖 Smart Machine Learning
                      </option>
                    </select>
                    <div className="text-xs text-gray-600 mt-1">
                      {forecastOptions.model === "holt" &&
                        "⚡ Fast results, good for general predictions"}
                      {forecastOptions.model === "arima" &&
                        "📊 Captures your spending trends over time"}
                      {forecastOptions.model === "sarima" &&
                        "🔄 Accounts for monthly/weekly patterns"}
                      {forecastOptions.model === "prophet" &&
                        "🎯 Most accurate but takes longer to process"}
                      {forecastOptions.model === "xgb" &&
                        "🤖 AI-powered predictions using advanced algorithms"}
                    </div>
                  </div>

                  {/* Horizon */}
                  <div>
                    <label className="text-sm font-medium mb-1 block">
                      How far ahead?
                    </label>
                    <select
                      className="w-full p-2 border rounded-md text-sm"
                      value={forecastOptions.horizon}
                      onChange={(e) =>
                        handleForecastOptionChange("horizon", e.target.value)
                      }
                    >
                      <option value="week">Next 7 days</option>
                      <option value="month">Next 30 days</option>
                      <option value="year">Next 12 months</option>
                    </select>
                  </div>

                  {/* Custom Periods */}
                  <div>
                    <label className="text-sm font-medium mb-1 block">
                      Custom Period (days)
                    </label>
                    <input
                      type="number"
                      className="w-full p-2 border rounded-md text-sm"
                      placeholder="Optional, e.g. 45"
                      value={forecastOptions.periods}
                      onChange={(e) =>
                        handleForecastOptionChange("periods", e.target.value)
                      }
                    />
                  </div>

                  {/* Granularity */}
                  <div>
                    <label className="text-sm font-medium mb-1 block">
                      Show forecast as
                    </label>
                    <select
                      className="w-full p-2 border rounded-md text-sm"
                      value={forecastOptions.granularity}
                      onChange={(e) =>
                        handleForecastOptionChange(
                          "granularity",
                          e.target.value
                        )
                      }
                    >
                      <option value="daily">Day-wise</option>
                      <option value="weekly">Week-wise</option>
                      <option value="monthly">Month-wise</option>
                    </select>
                  </div>

                  {/* Target Date */}
                  <div>
                    <label className="text-sm font-medium mb-1 block">
                      Target Date (Optional)
                    </label>
                    <input
                      type="date"
                      className="w-full p-2 border rounded-md text-sm"
                      value={forecastOptions.target_date || ""}
                      onChange={(e) =>
                        handleForecastOptionChange(
                          "target_date",
                          e.target.value
                        )
                      }
                    />
                  </div>
                </div>

                <Button
                  onClick={fetchAdvancedForecast}
                  disabled={loadingAdvancedForecast}
                  className="w-full"
                >
                  {loadingAdvancedForecast ? (
                    <span className="flex items-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" /> Loading
                      Advanced Forecast...
                    </span>
                  ) : (
                    "Get Advanced Forecast"
                  )}
                </Button>

                {errAdvancedForecast && (
                  <ErrorAlert message={errAdvancedForecast} className="mt-3" />
                )}

                {advancedForecast && (
                  <div className="mt-4 space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                      <StatTile
                        icon={<Wallet className="w-3 h-3 sm:w-4 sm:h-4" />}
                        label="Total Income Forecast"
                        value={inr(
                          advancedForecast?.summary?.income_total || 0
                        )}
                      />
                      <StatTile
                        icon={
                          <AlertTriangle className="w-3 h-3 sm:w-4 sm:h-4" />
                        }
                        label="Total Expense Forecast"
                        value={inr(
                          advancedForecast?.summary?.expense_total || 0
                        )}
                      />
                      <StatTile
                        icon={<TrendingUp className="w-3 h-3 sm:w-4 sm:h-4" />}
                        label="Expected Balance"
                        value={inr(
                          (advancedForecast?.summary?.income_total || 0) -
                            (advancedForecast?.summary?.expense_total || 0)
                        )}
                      />
                    </div>

                    <div className="text-sm">
                      <p>
                        <strong>Model:</strong>{" "}
                        {advancedForecast?.model || "N/A"}
                      </p>
                      <p>
                        <strong>Granularity:</strong>{" "}
                        {advancedForecast?.granularity || "N/A"}
                      </p>
                      {advancedForecast?.target_point && (
                        <p>
                          <strong>Target Date:</strong>{" "}
                          {advancedForecast?.target_point?.date} → Balance:{" "}
                          {inr(advancedForecast?.target_point?.balance || 0)}
                        </p>
                      )}
                    </div>

                    {advancedForecast?.forecast?.balance &&
                      advancedForecast.forecast.balance.length > 0 && (
                        <div className="mt-4">
                          <h4 className="font-medium mb-2">Forecast Details</h4>
                          <div className="overflow-x-auto">
                            <table className="w-full text-sm border-collapse border border-gray-300">
                              <thead>
                                <tr className="bg-gray-100">
                                  <th className="border border-gray-300 p-1">
                                    Date
                                  </th>
                                  <th className="border border-gray-300 p-1">
                                    Income
                                  </th>
                                  <th className="border border-gray-300 p-1">
                                    Expense
                                  </th>
                                  <th className="border border-gray-300 p-1">
                                    Balance
                                  </th>
                                </tr>
                              </thead>
                              <tbody>
                                {advancedForecast.forecast.balance.map(
                                  (item, idx) => (
                                    <tr key={idx} className="text-center">
                                      <td className="border border-gray-300 p-1">
                                        {item.ds}
                                      </td>
                                      <td className="border border-gray-300 p-1">
                                        {inr(
                                          advancedForecast.forecast.income[idx]
                                            ?.yhat || 0
                                        )}
                                      </td>
                                      <td className="border border-gray-300 p-1">
                                        {inr(
                                          advancedForecast.forecast.expense[idx]
                                            ?.yhat || 0
                                        )}
                                      </td>
                                      <td className="border border-gray-300 p-1">
                                        {inr(item.yhat || 0)}
                                      </td>
                                    </tr>
                                  )
                                )}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ================= ANOMALIES ================= */}
        <TabsContent value="anomalies">
          <Card className="shadow-sm border border-gray-200">
            <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
                <AlertTriangle className="w-4 h-4 sm:w-5 sm:h-5" /> Spending
                Anomalies
              </CardTitle>
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 text-xs text-muted-foreground">
                {tAnoms && (
                  <span className="hidden sm:inline">
                    Last run: {shortDate(tAnoms)}
                  </span>
                )}
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={fetchAnomaliesList}
                    disabled={loadingAnoms}
                    className="text-xs bg-transparent"
                  >
                    Refresh list
                  </Button>
                  <Button
                    size="sm"
                    onClick={runAnomalyDetection}
                    disabled={loadingAnoms}
                    className="text-xs"
                  >
                    {loadingAnoms ? (
                      <span className="flex items-center gap-1">
                        <Loader2 className="w-3 h-3 animate-spin" /> Running…
                      </span>
                    ) : (
                      <span className="flex items-center gap-1">
                        <RefreshCw className="w-3 h-3" /> Run detection
                      </span>
                    )}
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {errAnoms && <ErrorAlert message={errAnoms} />}

              {anomsSummary && (
                <div className="flex items-center gap-3 flex-wrap">
                  <Badge
                    variant={anomsSummary.created > 0 ? "default" : "secondary"}
                    className="text-xs"
                  >
                    {anomsSummary.created || 0} new anomalies
                  </Badge>
                </div>
              )}

              {!anomsList || anomsList.length === 0 ? (
                <EmptyState
                  icon={<AlertTriangle className="w-5 h-5 sm:w-6 sm:h-6" />}
                  title="No anomalies yet"
                  subtitle="Click 'Run detection' to scan your recent expenses."
                  actionLabel="Run detection"
                  onAction={runAnomalyDetection}
                  loading={loadingAnoms}
                />
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                  {anomsList.map((a, idx) => (
                    <AnomalyCard key={a.id || a._id || idx} a={a} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ================= RECURRING ================= */}
        <TabsContent value="recurring">
          <Card className="shadow-sm border border-gray-200">
            <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
                <Repeat className="w-4 h-4 sm:w-5 sm:h-5" /> Recurring Patterns
              </CardTitle>
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 text-xs text-muted-foreground">
                {tRecurring && (
                  <span className="hidden sm:inline">
                    Last run: {shortDate(tRecurring)}
                  </span>
                )}
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={fetchRecurringList}
                    disabled={loadingRecurring}
                    className="text-xs bg-transparent"
                  >
                    Refresh list
                  </Button>
                  <Button
                    size="sm"
                    onClick={runRecurringDetection}
                    disabled={loadingRecurring}
                    className="text-xs"
                  >
                    {loadingRecurring ? (
                      <span className="flex items-center gap-1">
                        <Loader2 className="w-3 h-3 animate-spin" /> Running…
                      </span>
                    ) : (
                      <span className="flex items-center gap-1">
                        <RefreshCw className="w-3 h-3" /> Run detection
                      </span>
                    )}
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {errRecurring && <ErrorAlert message={errRecurring} />}

              {recurringSummary && (
                <div className="flex items-center gap-3 flex-wrap">
                  <Badge
                    variant={
                      recurringSummary.created > 0 ? "default" : "secondary"
                    }
                    className="text-xs"
                  >
                    {recurringSummary.created || 0} new patterns
                  </Badge>
                </div>
              )}

              {!recurringList || recurringList.length === 0 ? (
                <EmptyState
                  icon={<Repeat className="w-5 h-5 sm:w-6 sm:h-6" />}
                  title="No recurring patterns detected yet"
                  subtitle="Run the detector to discover weekly or monthly patterns."
                  actionLabel="Run detection"
                  onAction={runRecurringDetection}
                  loading={loadingRecurring}
                />
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                  {/* {recurringList.map((r, idx) => (
                    <RecurringCard key={r.id || r._id || idx} r={r} />
                  ))} */}
                  {recurringList.map((r, idx) => (
                    <RecurringCard
                      key={r.id || r._id || idx}
                      r={{
                        amount: r.average_amount,
                        description: r.pattern,
                        category: r.category,
                        period: r.frequency,
                        last_detected: r.last_detected,
                      }}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ================= GOAL ETA ================= */}
        <TabsContent value="goals">
          <Card className="shadow-sm border border-gray-200">
            <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
                <Target className="w-4 h-4 sm:w-5 sm:h-5" /> Goal Completion ETA
              </CardTitle>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                {tEta && (
                  <span className="hidden sm:inline">
                    Updated: {shortDate(tEta)}
                  </span>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={fetchGoalEtas}
                  disabled={loadingEta}
                  className="text-xs bg-transparent"
                >
                  {loadingEta ? (
                    <Loader2 className="w-3 h-3 sm:w-4 sm:h-4 animate-spin" />
                  ) : (
                    <RefreshCw className="w-3 h-3 sm:w-4 sm:h-4" />
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {errEta && <ErrorAlert message={errEta} />}

              {(!etas || etas.length === 0) && !errEta ? (
                <SkeletonRow label="No goals or not enough savings data" />
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                  {etas.map((g, idx) => (
                    <GoalCard key={g.goal_id || idx} g={g} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* ================= DEBT ================= */}
        <TabsContent value="debts">
          <Card className="shadow-sm border border-gray-200">
            <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
                <Banknote className="w-4 h-4 sm:w-5 sm:h-5" /> Debt Payoff
                Prediction
              </CardTitle>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                {tDebt && (
                  <span className="hidden sm:inline">
                    Updated: {shortDate(tDebt)}
                  </span>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={fetchDebt}
                  disabled={loadingDebt}
                  className="text-xs bg-transparent"
                >
                  {loadingDebt ? (
                    <Loader2 className="w-3 h-3 sm:w-4 sm:h-4 animate-spin" />
                  ) : (
                    <RefreshCw className="w-3 h-3 sm:w-4 sm:h-4" />
                  )}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {errDebt && <ErrorAlert message={errDebt} />}

              {!debts && !errDebt ? (
                <SkeletonRow label="No debts found or not enough data" />
              ) : (
                <DebtCard d={debts} />
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// =============================================
// SUB-COMPONENTS & UI HELPERS
// =============================================
function StatTile({ icon, label, value }) {
  return (
    <div className="p-3 sm:p-4 rounded-xl bg-white/70 backdrop-blur border border-gray-200">
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          <div className="text-xs uppercase tracking-wide text-muted-foreground mb-1">
            {label}
          </div>
          <div className="text-base sm:text-lg lg:text-xl font-semibold truncate">
            {value}
          </div>
        </div>
        <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 grid place-items-center text-white flex-shrink-0 ml-2">
          {icon}
        </div>
      </div>
    </div>
  );
}

function ErrorAlert({ message, className = "" }) {
  if (!message) return null;
  return (
    <div
      className={`flex items-center gap-2 p-3 rounded-lg bg-red-50 text-red-700 border border-red-200 text-sm ${className}`}
    >
      <XCircle className="w-4 h-4" />
      <span className="truncate">{message}</span>
    </div>
  );
}

function SkeletonRow({ label = "Loading…" }) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white/70 backdrop-blur p-4">
      <div className="flex items-center gap-3 animate-pulse">
        <div className="w-10 h-10 rounded-lg bg-gray-200" />
        <div className="flex-1">
          <div className="h-3 w-40 bg-gray-200 rounded" />
          <div className="h-3 w-24 bg-gray-100 rounded mt-2" />
        </div>
      </div>
      <div className="mt-3 text-xs text-muted-foreground">{label}</div>
    </div>
  );
}

function EmptyState({ icon, title, subtitle, actionLabel, onAction, loading }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 p-8 border border-dashed rounded-xl bg-white/60">
      <div className="w-10 h-10 rounded-full bg-gray-100 grid place-items-center text-muted-foreground">
        {icon}
      </div>
      <div className="text-center">
        <h3 className="font-medium text-sm">{title}</h3>
        <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
      </div>
      {onAction && (
        <Button size="sm" onClick={onAction} disabled={loading}>
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : actionLabel}
        </Button>
      )}
    </div>
  );
}

function AnomalyCard({ a }) {
  const tx = a.transaction || a;
  const amount = Number(tx.amount || 0);
  const isNegative = amount < 0;
  const absAmount = Math.abs(amount);
  const category = tx.category || "Uncategorized";
  const description = tx.description || "No description";
  const date = asDate(tx.date) || new Date();

  return (
    <div className="p-3 sm:p-4 rounded-xl bg-white/70 backdrop-blur border border-red-200">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 mb-1">
            <AlertTriangle className="w-3 h-3 sm:w-4 sm:h-4 text-red-500" />
            <span className="text-xs text-red-600 font-medium">Anomaly</span>
          </div>
          <div className="text-sm font-medium truncate">{description}</div>
          <div className="text-xs text-muted-foreground mt-1">{category}</div>
          <div className="text-xs text-muted-foreground mt-1">
            {date.toLocaleDateString()}
          </div>
        </div>
        <div className="text-right flex-shrink-0 ml-2">
          <div
            className={`text-sm sm:text-base font-semibold ${
              isNegative ? "text-red-600" : "text-green-600"
            }`}
          >
            {isNegative ? "-" : "+"}
            {inr(absAmount)}
          </div>
        </div>
      </div>
    </div>
  );
}

function RecurringCard({ r }) {
  const amount = Number(r.amount || 0);
  const isNegative = amount < 0;
  const absAmount = Math.abs(amount);
  const category = r.category || "Uncategorized";
  const description = r.description || "No description";
  const period = r.period || "monthly";

  return (
    <div className="p-3 sm:p-4 rounded-xl bg-white/70 backdrop-blur border border-blue-200">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1 mb-1">
            <Repeat className="w-3 h-3 sm:w-4 sm:h-4 text-blue-500" />
            <span className="text-xs text-blue-600 font-medium capitalize">
              {period}
            </span>
          </div>
          <div className="text-sm font-medium truncate">{description}</div>
          <div className="text-xs text-muted-foreground mt-1">{category}</div>
        </div>
        <div className="text-right flex-shrink-0 ml-2">
          <div
            className={`text-sm sm:text-base font-semibold ${
              isNegative ? "text-red-600" : "text-green-600"
            }`}
          >
            {isNegative ? "-" : "+"}
            {inr(absAmount)}
          </div>
        </div>
      </div>
    </div>
  );
}
const getProgressPct = (current, target) => {
  if (!target || target <= 0) return 0;
  return Math.min(
    Math.round((Number(current || 0) / Number(target)) * 100),
    100
  );
};

function GoalCard({ g }) {
  const pct = getProgressPct(g.current_saved, g.target_amount);
  const eta = g.predicted_completion_date;

  return (
    <div className="rounded-xl border border-gray-200 bg-white/70 backdrop-blur p-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-sm text-muted-foreground mb-1">Goal</div>
          <div className="text-lg font-semibold">
            {g.title || "Untitled Goal"}
          </div>
        </div>
        <Badge variant={eta === "N/A" ? "secondary" : "default"}>
          {eta === "N/A" ? "No ETA" : shortDate(eta)}
        </Badge>
      </div>

      <div className="mt-3 space-y-2">
        <div className="flex justify-between text-sm">
          <span>Saved: {inr(g.current_saved || 0)}</span>
          <span>Target: {inr(g.target_amount || 0)}</span>
        </div>
        <Progress value={pct} />
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Clock className="w-3.5 h-3.5" />
          <span>Progress: {pct}%</span>
          <span className="mx-1">•</span>
          <span>
            Monthly net used: {inr(g.assumptions?.monthly_net_saving || 0)}
          </span>
        </div>
      </div>
    </div>
  );
}

function DebtCard({ d }) {
  if (!d) return null;

  const repayments = d.predicted_monthly_repayments || [];

  return (
    <div className="rounded-xl border border-gray-200 bg-white/70 backdrop-blur p-4 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="text-sm text-muted-foreground mb-1">Debt Forecast</div>
          <div className="text-lg font-semibold text-red-600">
            Total Debt: {inr(d.total_debt || 0)}
          </div>
        </div>
        <Badge
          variant={d.months_to_clear ? "default" : "secondary"}
          className="text-xs"
        >
          {d.months_to_clear
            ? `${d.months_to_clear} months`
            : "Too high / N/A"}
        </Badge>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
        <div className="flex justify-between p-2 rounded-lg bg-gray-50">
          <span className="text-gray-600">Avg Monthly Repayment</span>
          <span className="font-medium text-blue-600">
            {inr(d.avg_monthly_repayment || 0)}
          </span>
        </div>
        <div className="flex justify-between p-2 rounded-lg bg-gray-50">
          <span className="text-gray-600">Expected Clear Date</span>
          <span className="font-medium">
            {d.expected_clear_date || "N/A"}
          </span>
        </div>
      </div>

      {/* Predicted Repayments */}
      <div>
        <div className="text-xs text-muted-foreground mb-2">
          Predicted Monthly Repayments
        </div>
        <div className="max-h-40 overflow-y-auto rounded-lg border border-gray-100">
          <table className="min-w-full text-xs">
            <thead>
              <tr className="bg-gray-50 text-gray-600">
                <th className="text-left py-2 px-3">Month</th>
                <th className="text-right py-2 px-3">Amount</th>
              </tr>
            </thead>
            <tbody>
              {repayments.map((amt, idx) => (
                <tr
                  key={idx}
                  className="border-t last:border-0 text-gray-700"
                >
                  <td className="py-2 px-3">Month {idx + 1}</td>
                  <td
                    className={`py-2 px-3 text-right font-medium ${
                      amt > 0 ? "text-green-600" : "text-gray-400"
                    }`}
                  >
                    {inr(amt)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}


export default Aiinsights;
