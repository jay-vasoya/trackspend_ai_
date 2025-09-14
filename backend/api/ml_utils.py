# ml_utils.py
import math
from collections import defaultdict
from statistics import mean, pstdev
from datetime import datetime, timedelta
from bson import ObjectId

from .models import (
    User, Transaction, Goal,
    MLPrediction, SpendingAnomaly, RecurringPattern
)

# -------------------------------
# Helpers
# -------------------------------
def _get_user(user_id: str) -> User:
    return User.objects.get(id=ObjectId(user_id))

def _month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")

def _next_month_label(now: datetime) -> str:
    y, m = now.year, now.month
    if m == 12:
        return f"{y+1}-01"
    return f"{y:04d}-{m+1:02d}"

# -------------------------------
# 1) Expense/Income Forecast (Monthly)
# -------------------------------
def predict_next_month_expense(user_id: str) -> MLPrediction:
    user = _get_user(user_id)

    window_days = 120
    cutoff = datetime.utcnow() - timedelta(days=window_days)
    tx_qs = Transaction.objects(user_id=user, date__gte=cutoff)

    month_income = defaultdict(float)
    month_expense = defaultdict(float)

    for tx in tx_qs:
        key = _month_key(tx.date)
        if tx.type == "income":
            month_income[key] += float(tx.amount or 0)
        elif tx.type == "expense":
            month_expense[key] += float(tx.amount or 0)

    months = sorted(set(month_income.keys()) | set(month_expense.keys()))
    months = months[-3:]

    if months:
        incomes = [month_income[m] for m in months]
        expenses = [month_expense[m] for m in months]
        predicted_income = mean(incomes)
        predicted_expense = mean(expenses)
        predicted_balance = predicted_income - predicted_expense
        confidence = 0.4 if len(months) == 1 else (0.6 if len(months) == 2 else 0.8)
    else:
        predicted_income = 0.0
        predicted_expense = 0.0
        predicted_balance = 0.0
        confidence = 0.2

    pred = MLPrediction(
        user_id=user,
        prediction_type="monthly_forecast",
        target_period=_next_month_label(datetime.utcnow()),
        predicted_income=float(predicted_income),
        predicted_expense=float(predicted_expense),
        predicted_balance=float(predicted_balance),
        confidence=float(confidence),
        model_version="v1.0",
    )
    pred.save()
    return pred

# -------------------------------
# 2) Spending Anomaly Detection
# -------------------------------
def detect_spending_anomalies(user_id: str):
    user = _get_user(user_id)
    expenses = list(Transaction.objects(user_id=user, type="expense"))
    if not expenses:
        return []

    by_cat = defaultdict(list)
    for tx in expenses:
        by_cat[tx.category].append(float(tx.amount or 0))

    cat_stats = {}
    all_amounts = [float(tx.amount or 0) for tx in expenses]
    overall_mean = mean(all_amounts) if all_amounts else 0.0
    overall_threshold = overall_mean * 1.6 if overall_mean > 0 else float("inf")

    for cat, vals in by_cat.items():
        m = mean(vals)
        s = pstdev(vals) if len(vals) > 1 else 0.0
        cat_stats[cat] = (m, s)

    created = []
    for tx in expenses:
        amt = float(tx.amount or 0)
        m, s = cat_stats.get(tx.category, (overall_mean, 0.0))
        z_like = 0 if s == 0 else (amt - m) / s
        ratio = (amt / m) if m > 0 else 0
        is_anomaly = (s > 0 and z_like >= 2.0) or (amt >= overall_threshold) or (ratio >= 1.6)
        if is_anomaly:
            existing = SpendingAnomaly.objects(user_id=user, transaction_id=tx).first()
            if existing:
                continue
            reason_parts = []
            if s > 0 and z_like >= 2.0:
                reason_parts.append(f"z≈{round(z_like,2)}")
            if ratio >= 1.6 and m > 0:
                reason_parts.append(f"{round(ratio,2)}x category avg")
            if amt >= overall_threshold and overall_mean > 0:
                reason_parts.append(">1.6x overall avg")

            anomaly = SpendingAnomaly(
                user_id=user,
                transaction_id=tx,
                anomaly_score=float(max(ratio, z_like if s > 0 else 0)),
                flag_reason="; ".join(reason_parts) or "High deviation",
            )
            anomaly.save()
            created.append(anomaly)
    return created

# -------------------------------
# 3) Recurring Pattern Detection
# -------------------------------
def find_recurring_patterns(user_id: str):
    user = _get_user(user_id)
    expenses = list(Transaction.objects(user_id=user, type="expense"))
    if not expenses:
        return []

    buckets = defaultdict(list)
    for tx in expenses:
        approx_amt = int(round(float(tx.amount or 0) / 100.0) * 100)
        key = (tx.category, approx_amt)
        buckets[key].append(tx)

    created = []
    for (cat, approx_amt), txs in buckets.items():
        if len(txs) < 3:
            continue
        txs.sort(key=lambda t: t.date)
        gaps = [(txs[i].date - txs[i-1].date).days for i in range(1, len(txs))]
        if not gaps:
            continue
        avg_gap = mean(gaps)
        if 5 <= avg_gap <= 10:
            freq = "Weekly"
        elif 20 <= avg_gap <= 40:
            freq = "Monthly"
        else:
            freq = "Irregular"

        avg_amount = mean([float(t.amount or 0) for t in txs])
        pattern_str = f"{cat} ~{approx_amt}"

        existing = RecurringPattern.objects(user_id=user, category=cat, pattern=pattern_str).first()
        if existing:
            existing.average_amount = float(avg_amount)
            existing.frequency = freq
            existing.last_detected = datetime.utcnow()
            existing.save()
            continue

        rp = RecurringPattern(
            user_id=user,
            pattern=pattern_str,
            category=cat,
            frequency=freq,
            average_amount=float(avg_amount),
            last_detected=datetime.utcnow(),
        )
        rp.save()
        created.append(rp)
    return created

# -------------------------------
# 4) Goal Completion Prediction (Account-aware)
# -------------------------------
from statistics import mean
from datetime import datetime, timedelta
from collections import defaultdict

def predict_goal_completion(user_id: str):
    """
    For each Goal:
      remaining = target_amount - current_amount
      monthly_net = avg (income - expense) from user's accounts (last 3 months)
      ETA = now + months_needed * 30 days (if monthly_net > 0 else 'N/A')
    """
    user = _get_user(user_id)
    goals = list(Goal.objects(user_id=user))

    # ✅ Get all accounts of user
    from .models import Account, Transaction
    accounts = list(Account.objects(user_id=user))
    account_ids = [acc.id for acc in accounts]

    # ✅ Last 120 days transactions of these accounts
    window_days = 120
    cutoff = datetime.utcnow() - timedelta(days=window_days)
    tx_qs = Transaction.objects(user_id=user, account_id__in=account_ids, date__gte=cutoff)

    # ✅ Group by month
    month_income = defaultdict(float)
    month_expense = defaultdict(float)
    for tx in tx_qs:
        key = _month_key(tx.date)
        if tx.type == "income":
            month_income[key] += float(tx.amount or 0)
        elif tx.type == "expense":
            month_expense[key] += float(tx.amount or 0)

    months = sorted(set(month_income.keys()) | set(month_expense.keys()))
    months = months[-3:]  # last 3 months

    monthly_nets = [(month_income[m] - month_expense[m]) for m in months] if months else []

    # ✅ Safe fallback
    if monthly_nets:
        positive_nets = [n for n in monthly_nets if n > 0]
        monthly_net = mean(positive_nets) if positive_nets else 0.0
    else:
        monthly_net = 0.0

    # ✅ For each goal, compute ETA
    results = []
    for g in goals:
        target = float(getattr(g, "target_amount", 0) or 0)
        saved = float(getattr(g, "current_amount", 0) or 0)
        remaining = max(0.0, target - saved)

        if monthly_net > 0 and remaining > 0:
            months_needed = remaining / monthly_net
            eta = datetime.utcnow() + timedelta(days=30 * months_needed)
            eta_str = eta.isoformat()
        else:
            eta_str = "N/A"

        results.append({
            "goal_id": str(g.id),
            "title": getattr(g, "title", ""),
            "target_amount": target,
            "current_saved": saved,
            "predicted_completion_date": eta_str,
            "assumptions": {
                "monthly_net_saving": monthly_net,
                "months_window_used": len(months)
            }
        })

    return results


# # ================================
# # ML Based Debt Payoff Prediction
# # ================================
# import numpy as np
# import pandas as pd
# from sklearn.linear_model import LinearRegression
# from datetime import datetime
# from dateutil.relativedelta import relativedelta

# def ml_predict_debt_payoff(transactions, debt_amount: float):
#     """
#     ML model to predict when user can finish paying debt based on past transactions.

#     Args:
#         transactions (QuerySet or list): User's transactions (should have 'date' and 'amount' fields).
#         debt_amount (float): Current debt amount.

#     Returns:
#         dict with prediction results.
#     """

#     if not transactions or debt_amount <= 0:
#         return {
#             "total_debt": debt_amount,
#             "status": "No transactions or invalid debt amount",
#             "months_to_clear": None,
#             "expected_clear_date": None,
#         }

#     # Convert transactions into DataFrame
#     data = []
#     for t in transactions:
#         try:
#             amt = float(t.amount)
#             dt = pd.to_datetime(str(t.date))
#             data.append([dt, amt])
#         except Exception:
#             continue

#     if not data:
#         return {
#             "total_debt": debt_amount,
#             "status": "Invalid transaction data",
#             "months_to_clear": None,
#             "expected_clear_date": None,
#         }

#     df = pd.DataFrame(data, columns=["date", "amount"])
#     df["month"] = df["date"].dt.to_period("M").astype(str)

#     # Aggregate by month (total repayment per month)
#     monthly = df.groupby("month")["amount"].sum().reset_index()
#     monthly["month_num"] = np.arange(len(monthly))

#     # Features (X) → month index, Target (y) → monthly repayment
#     X = monthly[["month_num"]]
#     y = monthly["amount"]

#     # Train Linear Regression model
#     model = LinearRegression()
#     model.fit(X, y)

#     # Predict next few months repayment
#     future_months = 12  # horizon
#     X_future = np.arange(len(monthly), len(monthly) + future_months).reshape(-1, 1)
#     y_pred = model.predict(X_future)

#     # Ensure no negative predictions
#     y_pred = np.maximum(y_pred, 0)

#     # Estimate how many months required
#     remaining = debt_amount
#     months_needed = 0
#     for repayment in y_pred:
#         months_needed += 1
#         remaining -= repayment
#         if remaining <= 0:
#             break

#     # Final clear date
#     clear_date = None
#     if remaining <= 0:
#         clear_date = (datetime.today().replace(day=1) + relativedelta(months=months_needed)).strftime("%Y-%m-%d")

#     return {
#         "total_debt": debt_amount,
#         "avg_monthly_repayment": round(y.mean(), 2),
#         "predicted_monthly_repayments": [round(val, 2) for val in y_pred.tolist()],
#         "months_to_clear": months_needed if remaining <= 0 else None,
#         "expected_clear_date": clear_date,
#         "status": "Prediction successful" if remaining <= 0 else "Debt too high for current trend",
#     }



# ================================
# ML Based Debt Payoff Prediction
# ================================
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime
from dateutil.relativedelta import relativedelta

def ml_predict_debt_payoff(transactions, debt_amount: float):
    """
    ML model to predict when user can finish paying debt based on past transactions.
    """

    if not transactions or debt_amount <= 0:
        return {
            "total_debt": debt_amount,
            "status": "No transactions or invalid debt amount",
            "months_to_clear": None,
            "expected_clear_date": None,
        }

    # Convert transactions into DataFrame
    data = []
    for t in transactions:
        try:
            amt = float(t.amount)
            dt = pd.to_datetime(str(t.date))
            data.append([dt, amt])
        except Exception:
            continue

    if not data:
        return {
            "total_debt": debt_amount,
            "status": "Invalid transaction data",
            "months_to_clear": None,
            "expected_clear_date": None,
        }

    df = pd.DataFrame(data, columns=["date", "amount"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # Aggregate by month (total repayment per month)
    monthly = df.groupby("month")["amount"].sum().reset_index()
    monthly["month_num"] = np.arange(len(monthly))

    # Features (X) → month index, Target (y) → monthly repayment
    X = monthly[["month_num"]]
    y = monthly["amount"]

    # Train Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict next 60 months (5 years instead of just 12)
    future_months = 60
    X_future = np.arange(len(monthly), len(monthly) + future_months).reshape(-1, 1)
    y_pred = model.predict(X_future)
    y_pred = np.maximum(y_pred, 0)

    # Estimate payoff
    remaining = debt_amount
    months_needed = 0
    for repayment in y_pred:
        months_needed += 1
        remaining -= repayment
        if remaining <= 0:
            break

    clear_date = None
    if remaining <= 0:
        clear_date = (
            datetime.today().replace(day=1) + relativedelta(months=months_needed)
        ).strftime("%Y-%m-%d")

    return {
        "total_debt": debt_amount,
        "avg_monthly_repayment": round(y.mean(), 2),
        "predicted_monthly_repayments": [round(val, 2) for val in y_pred.tolist()],
        "months_to_clear": months_needed if remaining <= 0 else None,
        "expected_clear_date": clear_date,
        "status": "Prediction successful" if remaining <= 0 else "Debt too high for current trend",
    }







#########################################################################################



# ===========================
# ML Forecasting Utils (Income/Expense/Balance)
# ===========================


import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, List
from bson import ObjectId
from .models import Transaction, User


# ---------------------------
# Helpers: fetch daily series
# ---------------------------
def _ensure_user(user_id: str):
    """
    Returns a User document by id (ObjectId string or str id).
    If it fails, returns None and lets caller fallback to fake data.
    """
    try:
        return User.objects.get(id=ObjectId(user_id))
    except Exception:
        try:
            return User.objects.get(id=user_id)
        except Exception:
            return None


def _fetch_user_daily_series_by_type(
    user_id: str,
    kind: Optional[str],              # "income" | "expense" | None
    min_days: int = 30,
    fallback_days: int = 120
) -> pd.Series:
    """
    Fetch user's transactions -> daily aggregated series (Pandas Series indexed by date).
    If no/low data, generate realistic fake series.
    kind=None => all; kind="income"/"expense" => filtered
    """
    user = _ensure_user(user_id)
    try:
        if user is None:
            qs = []
        else:
            if kind in ("income", "expense"):
                qs = Transaction.objects(user_id=user, type=kind).only('date', 'amount', 'type')
            else:
                qs = Transaction.objects(user_id=user).only('date', 'amount', 'type')
    except Exception:
        qs = []

    if qs:
        data = []
        for t in qs:
            d = t.date.date() if hasattr(t.date, "date") else t.date
            try:
                amt = float(t.amount)
            except Exception:
                amt = 0.0
            data.append({"date": d, "amount": amt})
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        daily = df.groupby("date")["amount"].sum().sort_index()
    else:
        # Fake data generator (stable & realistic)
        end = datetime.now().date()
        start = end - timedelta(days=fallback_days - 1)
        rng = pd.date_range(start, end, freq="D")
        base = np.linspace(600, 1200, len(rng))    # trend
        week = (np.sin(np.arange(len(rng)) * 2 * np.pi / 7) + 1) * 180  # weekly component
        noise = np.random.normal(0, 90, len(rng))

        if kind == "income":
            y = np.maximum(0, base * 1.0 + week * 0.6 + noise + 200)  # typically higher base for income
        elif kind == "expense":
            y = np.maximum(0, base * 0.8 + week * 1.0 + noise)
        else:
            y = np.maximum(0, base + week + noise)

        daily = pd.Series(y, index=rng)

    # ensure continuous dates
    full_idx = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    daily = daily.reindex(full_idx, fill_value=0.0)

    # if too short, pad a little by mirroring start
    if len(daily) < min_days:
        need = min_days - len(daily)
        pad_vals = daily.iloc[:need][::-1].values
        pad_idx = pd.date_range(daily.index.min() - pd.Timedelta(days=need), periods=need, freq="D")
        daily = pd.concat([pd.Series(pad_vals, index=pad_idx), daily]).sort_index()

    return daily.astype(float)


def _fetch_income_expense_series(user_id: str) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Return (income_series, expense_series, balance_series)"""
    inc = _fetch_user_daily_series_by_type(user_id, "income")
    exp = _fetch_user_daily_series_by_type(user_id, "expense")
    # reindex to a common date index
    full_idx = pd.date_range(min(inc.index.min(), exp.index.min()),
                             max(inc.index.max(), exp.index.max()),
                             freq="D")
    inc = inc.reindex(full_idx, fill_value=0.0)
    exp = exp.reindex(full_idx, fill_value=0.0)
    bal = inc - exp
    return inc, exp, bal


def _build_future_index(last_date: pd.Timestamp, periods: int) -> pd.DatetimeIndex:
    return pd.date_range(last_date + pd.Timedelta(days=1), periods=periods, freq="D")


# ---------------------------
# Model-specific forecasters
# ---------------------------
def _forecast_arima(series: pd.Series, periods=30, order=(5, 1, 0)) -> List[float]:
    from statsmodels.tsa.arima.model import ARIMA
    model = ARIMA(series, order=order)
    fit = model.fit()
    fc = fit.forecast(steps=periods)
    return fc.values.tolist()


def _forecast_sarima(series: pd.Series, periods=30,
                     order=(1, 1, 1), seasonal_order=(1, 1, 1, 7)) -> List[float]:
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    model = SARIMAX(series, order=order, seasonal_order=seasonal_order,
                    enforce_stationarity=False, enforce_invertibility=False)
    fit = model.fit(disp=False)
    fc = fit.get_forecast(steps=periods).predicted_mean
    return fc.values.tolist()


def _forecast_holt(series: pd.Series, periods=30,
                   seasonal_periods=7, trend='add', seasonal='add') -> List[float]:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    model = ExponentialSmoothing(series, trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods)
    fit = model.fit()
    fc = fit.forecast(periods)
    return fc.values.tolist()


def _forecast_prophet(series: pd.Series, periods=30) -> List[float]:
    # Prophet expects columns: ds, y
    from prophet import Prophet
    df = pd.DataFrame({"ds": series.index, "y": series.values})
    m = Prophet(daily_seasonality=True, weekly_seasonality=True, yearly_seasonality=False)
    m.fit(df)
    future = m.make_future_dataframe(periods=periods, freq="D")
    forecast = m.predict(future)[["ds", "yhat"]].tail(periods)
    return forecast["yhat"].astype(float).tolist()


def _make_features_from_series(series: pd.Series):
    df = pd.DataFrame({"ds": series.index, "y": series.values})
    df["dow"] = df["ds"].dt.weekday
    df["dom"] = df["ds"].dt.day
    df["month"] = df["ds"].dt.month
    for lag in [1, 2, 3, 7, 14]:
        df[f"lag_{lag}"] = df["y"].shift(lag)
    df = df.dropna()
    X = df.drop(columns=["ds", "y"])
    y = df["y"]
    return df, X, y


def _forecast_gbr(series: pd.Series, periods=30) -> List[float]:
    """GBRT as a light 'xgb-style' tree-based regressor to avoid extra deps."""
    from sklearn.ensemble import GradientBoostingRegressor
    df, X, y = _make_features_from_series(series)
    if len(df) < 30:
        # fallback to Holt when too little data
        return _forecast_holt(series, periods)
    model = GradientBoostingRegressor()
    model.fit(X, y)

    preds = []
    last_known = series.copy()
    future_dates = _build_future_index(series.index.max(), periods)
    for d in future_dates:
        row = {"dow": d.weekday(), "dom": d.day, "month": d.month}
        for lag in [1, 2, 3, 7, 14]:
            lag_date = d - pd.Timedelta(days=lag)
            row[f"lag_{lag}"] = float(last_known.get(lag_date, last_known.iloc[-1]))
        Xf = pd.DataFrame([row])
        yhat = float(model.predict(Xf)[0])
        preds.append(yhat)
        last_known.loc[d] = yhat
    return preds


# ---------------------------
# Generic dispatcher (single series)
# ---------------------------
def _forecast_one(series: pd.Series, model: str, periods: int) -> Tuple[pd.DatetimeIndex, List[float]]:
    # Ensure series is numeric and clean
    series = pd.to_numeric(series, errors="coerce").fillna(0.0)

    # ✅ If very little data, do not call heavy models
    if len(series) < 10:
        last_val = float(series.iloc[-1]) if len(series) > 0 else 0.0
        mean_val = float(series.mean()) if len(series) > 0 else 0.0
        safe_val = (last_val + mean_val) / 2.0   # stable fallback
        idx = _build_future_index(series.index.max(), periods)
        vals = [safe_val for _ in range(periods)]
        return idx, vals

    # Normal model flow
    model = (model or "holt").lower()
    try:
        if model == "arima":
            vals = _forecast_arima(series, periods=periods)
        elif model == "sarima":
            vals = _forecast_sarima(series, periods=periods)
        elif model in ("holt", "holt_winters", "expsmooth", "hw"):
            vals = _forecast_holt(series, periods=periods)
        elif model == "prophet":
            vals = _forecast_prophet(series, periods=periods)
        elif model in ("xgb", "gbrt", "tree"):
            vals = _forecast_gbr(series, periods=periods)
        else:
            vals = _forecast_holt(series, periods=periods)
    except Exception as e:
        # ✅ Emergency fallback (in case model training still fails)
        last_val = float(series.iloc[-1]) if len(series) > 0 else 0.0
        vals = [last_val for _ in range(periods)]

    idx = _build_future_index(series.index.max(), periods)
    return idx, vals

# ---------------------------
# Public API helpers
# ---------------------------
def forecast_income_expense_balance(
    user_id: str,
    model: str = "holt",
    periods: int = 30
) -> Dict:
    """
    Returns daily forecast for income, expense and balance lists:
      { income: [{ds, yhat}], expense: [...], balance: [...] }
    """
    inc_series, exp_series, _ = _fetch_income_expense_series(user_id)

    idx_inc, inc_vals = _forecast_one(inc_series, model, periods)
    idx_exp, exp_vals = _forecast_one(exp_series, model, periods)

    # Align lengths/indexes
    dates = idx_inc  # both will start from (last_date+1)
    inc_list = [{"ds": str(d.date()), "yhat": float(v)} for d, v in zip(dates, inc_vals)]
    exp_list = [{"ds": str(d.date()), "yhat": float(v)} for d, v in zip(dates, exp_vals)]

    bal_vals = (np.array(inc_vals) - np.array(exp_vals)).tolist()
    bal_list = [{"ds": str(d.date()), "yhat": float(v)} for d, v in zip(dates, bal_vals)]

    return {
        "income": inc_list,
        "expense": exp_list,
        "balance": bal_list,
        "last_observed_date": str(inc_series.index.max().date())
    }


def _aggregate_list(data_list: List[Dict], granularity: str = "daily") -> List[Dict]:
    """Aggregate [{ds,yhat}] into weekly/monthly if requested."""
    if granularity == "daily":
        return data_list

    if not data_list:
        return data_list

    df = pd.DataFrame(data_list)
    df["ds"] = pd.to_datetime(df["ds"])
    df = df.set_index("ds").sort_index()

    if granularity == "weekly":
        out = df.resample("W-SUN")["yhat"].sum()  # week ends Sunday
    elif granularity == "monthly":
        out = df.resample("M")["yhat"].sum()
    else:
        return data_list

    return [{"ds": str(d.date()), "yhat": float(v)} for d, v in out.items()]


def build_forecast_payload(
    user_id: str,
    model: str = "holt",
    periods: int = 30,
    granularity: str = "daily",
    target_date: Optional[str] = None
) -> Dict:
    """
    Create final payload including aggregated series + summary + (optional) target point.
    """
    fc = forecast_income_expense_balance(user_id, model=model, periods=periods)

    income_daily = fc["income"]
    expense_daily = fc["expense"]
    balance_daily = fc["balance"]

    income = _aggregate_list(income_daily, granularity)
    expense = _aggregate_list(expense_daily, granularity)
    balance = _aggregate_list(balance_daily, granularity)

    # summary totals (over the horizon at chosen granularity)
    income_total = float(sum(x["yhat"] for x in income))
    expense_total = float(sum(x["yhat"] for x in expense))
    balance_total = float(sum(x["yhat"] for x in balance))

    # ✅ Expected end date and balance = last balance point
    expected_end_date = None
    expected_end_date_balance = None
    if balance:
        last_point = balance[-1]   # last forecast entry
        expected_end_date = last_point["ds"]
        expected_end_date_balance = round(last_point["yhat"], 2)

    payload = {
        "model": model,
        "granularity": granularity,
        "periods": periods,
        "last_observed_date": fc["last_observed_date"],
        "forecast": {
            "income": income,
            "expense": expense,
            "balance": balance,
        },
        "summary": {
            "income_total": income_total,
            "expense_total": expense_total,
            "balance_total": balance_total,
            "expected_end_date": expected_end_date,
            "expected_end_date_balance": expected_end_date_balance,
        }
    }

    # Optional: particular date's point forecast
    if target_date:
        try:
            td = pd.to_datetime(target_date).date()
            # We need to ensure we have forecasts until td
            last_obs = pd.to_datetime(fc["last_observed_date"]).date()
            days_needed = (td - last_obs).days
            if days_needed > periods:
                # Extend horizon automatically to cover target_date
                fc_ext = forecast_income_expense_balance(user_id, model=model, periods=days_needed)
                income_daily = fc_ext["income"]
                expense_daily = fc_ext["expense"]
                balance_daily = fc_ext["balance"]

            # find that date in daily
            def _find_point(lst):
                for row in lst:
                    if row["ds"] == str(td):
                        return float(row["yhat"])
                return None

            income_point = _find_point(income_daily)
            expense_point = _find_point(expense_daily)
            balance_point = _find_point(balance_daily)

            payload["target_point"] = {
                "date": str(td),
                "income": income_point,
                "expense": expense_point,
                "balance": balance_point,
            }
        except Exception:
            payload["target_point"] = {"error": "Invalid target_date format. Use YYYY-MM-DD."}

    return payload

# ---------------------------
# Legacy simple dispatcher (single total series)
# (kept for backward compatibility; treats total = income+expense sum)
# ---------------------------
def forecast_dispatch(user_id, model="holt", periods=30):
    """
    Backward compatible: returns a single 'total' daily forecast (sum of amounts).
    Now built as income + expense (absolute sum). Prefer build_forecast_payload for rich output.
    """
    inc_series = _fetch_user_daily_series_by_type(user_id, "income")
    exp_series = _fetch_user_daily_series_by_type(user_id, "expense")
    total_series = inc_series + exp_series  # total volume
    idx, vals = _forecast_one(total_series, model, periods)
    return [{"ds": str(d.date()), "yhat": float(v)} for d, v in zip(idx, vals)]


