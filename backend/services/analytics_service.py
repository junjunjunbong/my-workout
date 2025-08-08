import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
import sys

# Add the parent directory to the path to import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage import read_json


def epley_one_rm(weight_kg: float, reps: int) -> float:
    """Estimate 1RM using Epley formula: weight × (1 + reps/30)."""
    try:
        w = float(weight_kg)
        r = int(reps)
        if r <= 0 or w <= 0:
            return 0.0
        return w * (1.0 + (r / 30.0))
    except Exception:
        return 0.0


def pr_trend(exercise: str, start: Optional[str] = None, end: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Compute date-wise PR trend (estimated 1RM) for a specific exercise.
    Returns list of {date: 'YYYY-MM-DD', one_rm: float} sorted ascending by date.
    """
    workouts = read_json("workouts")
    rows: List[Dict[str, Any]] = []
    for w in workouts:
        if w.get("exercise") != exercise:
            continue
        date_str = w.get("date")
        sets = w.get("sets") or []
        best = 0.0
        for s in sets:
            best = max(best, epley_one_rm(s.get("weight_kg", 0), s.get("reps", 0)))
        if best > 0 and date_str:
            rows.append({"date": date_str, "one_rm": best})

    # Filter by date range
    def to_dt(d: Optional[str]) -> Optional[datetime]:
        return datetime.fromisoformat(d) if d else None

    start_dt = to_dt(start)
    end_dt = to_dt(end)

    def within_range(d: str) -> bool:
        try:
            dt = datetime.fromisoformat(d)
        except Exception:
            return False
        if start_dt and dt < start_dt:
            return False
        if end_dt and dt > end_dt:
            return False
        return True

    rows = [r for r in rows if within_range(r["date"])]

    # Consolidate by date (take max per date)
    by_date: Dict[str, float] = {}
    for r in rows:
        by_date[r["date"]] = max(by_date.get(r["date"], 0.0), float(r["one_rm"]))

    out = [{"date": k, "one_rm": v} for k, v in by_date.items()]
    out.sort(key=lambda x: x["date"])  # ISO date sorts lexicographically
    return out


def muscle_volume_by_category(start: Optional[str] = None, end: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Aggregate total training volume (sum of weight×reps) by category for the date range.
    Returns list of {category, volume}.
    """
    workouts = read_json("workouts")
    start_dt = datetime.fromisoformat(start) if start else None
    end_dt = datetime.fromisoformat(end) if end else None

    totals: Dict[str, float] = {}
    for w in workouts:
        date_str = w.get("date")
        try:
            dt = datetime.fromisoformat(date_str)
        except Exception:
            continue
        if start_dt and dt < start_dt:
            continue
        if end_dt and dt > end_dt:
            continue
        category = w.get("category") or "Unknown"
        vol = 0.0
        for s in (w.get("sets") or []):
            vol += float(s.get("weight_kg", 0)) * float(s.get("reps", 0))
        totals[category] = totals.get(category, 0.0) + vol

    return [{"category": k, "volume": v} for k, v in totals.items()]

def calculate_volume(sets: List[Dict[str, Any]]) -> float:
    """Calculate total volume for a workout (weight × reps for all sets)"""
    return sum(set_record.get("weight_kg", 0) * set_record.get("reps", 0) for set_record in sets)

def weekly_volume() -> pd.DataFrame:
    """Calculate weekly volume of workouts"""
    workouts = read_json("workouts")
    
    # Convert to DataFrame
    df = pd.DataFrame(workouts)
    
    if df.empty:
        # Return empty DataFrame with correct columns if no data
        return pd.DataFrame(columns=["week_start", "volume"])
    
    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"])
    
    # Calculate volume for each workout
    df["volume"] = df["sets"].apply(calculate_volume)
    
    # Group by week and sum volume
    df["week_start"] = df["date"].dt.to_period("W").dt.start_time
    weekly = df.groupby("week_start")["volume"].sum().reset_index()
    
    # Format for output
    weekly["week_start"] = weekly["week_start"].dt.strftime("%Y-%m-%d")
    
    return weekly

def monthly_volume() -> pd.DataFrame:
    """Calculate monthly volume of workouts"""
    workouts = read_json("workouts")
    
    # Convert to DataFrame
    df = pd.DataFrame(workouts)
    
    if df.empty:
        # Return empty DataFrame with correct columns if no data
        return pd.DataFrame(columns=["month", "volume"])
    
    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"])
    
    # Calculate volume for each workout
    df["volume"] = df["sets"].apply(calculate_volume)
    
    # Group by month and sum volume
    df["month"] = df["date"].dt.to_period("M").dt.start_time
    monthly = df.groupby("month")["volume"].sum().reset_index()
    
    # Format for output
    monthly["month"] = monthly["month"].dt.strftime("%Y-%m")
    
    return monthly


def exercise_detail(exercise: str, start: Optional[str] = None, end: Optional[str] = None) -> List[Dict[str, Any]]:
    """Return per-date series for a given exercise: volume and top weight per date.

    Output: [{date, volume, top_weight}] sorted ascending by date.
    """
    if not exercise or not exercise.strip():
        return []
    workouts = read_json("workouts")

    def to_dt(d: Optional[str]) -> Optional[datetime]:
        return datetime.fromisoformat(d) if d else None

    start_dt = to_dt(start)
    end_dt = to_dt(end)

    by_date: Dict[str, Dict[str, float]] = {}
    for w in workouts:
        if w.get("exercise") != exercise:
            continue
        d = w.get("date")
        if not d:
            continue
        try:
            dt = datetime.fromisoformat(d)
        except Exception:
            continue
        if start_dt and dt < start_dt:
            continue
        if end_dt and dt > end_dt:
            continue
        vol = 0.0
        top = 0.0
        for s in (w.get("sets") or []):
            try:
                wkg = float(s.get("weight_kg", 0))
                reps = float(s.get("reps", 0))
                vol += wkg * reps
                if wkg > top:
                    top = wkg
            except Exception:
                continue
        agg = by_date.setdefault(d, {"volume": 0.0, "top_weight": 0.0})
        agg["volume"] += vol
        if top > agg["top_weight"]:
            agg["top_weight"] = top

    out = [{"date": d, "volume": round(v["volume"], 2), "top_weight": round(v["top_weight"], 2)} for d, v in by_date.items()]
    out.sort(key=lambda x: x["date"])  # ISO sort
    return out