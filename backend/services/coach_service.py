from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from storage import read_json
import storage as _storage
from services.analytics_service import epley_one_rm


def _parse_date(d: str) -> datetime:
    return datetime.strptime(d, "%Y-%m-%d")


def _window_bounds(dates: List[str], days: int) -> Tuple[datetime, datetime]:
    if not dates:
        now = datetime.utcnow()
        start = now - timedelta(days=days - 1)
        return start, now
    end = max(_parse_date(d) for d in dates)
    start = end - timedelta(days=days - 1)
    return start, end


def _weekly_key(dt: datetime) -> str:
    # ISO year-week representation
    iso_year, iso_week, _ = dt.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _calc_weekly_metrics(workouts: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    volume_by_week: Dict[str, float] = {}
    days_by_week: Dict[str, set] = {}
    for w in workouts:
        try:
            dt = _parse_date(w.get("date", ""))
        except Exception:
            continue
        week = _weekly_key(dt)
        days_by_week.setdefault(week, set()).add(w.get("date"))
        sets = w.get("sets") or []
        vol = 0.0
        for s in sets:
            try:
                vol += float(s.get("weight_kg", 0)) * int(s.get("reps", 0))
            except Exception:
                continue
        volume_by_week[week] = volume_by_week.get(week, 0.0) + vol

    weekly_volume = [
        {"week": k, "volume": round(v, 2)} for k, v in sorted(volume_by_week.items())
    ]
    weekly_frequency = [
        {"week": k, "days": len(days_by_week.get(k, set()))}
        for k in sorted(days_by_week.keys())
    ]
    return weekly_volume, weekly_frequency


def _calc_pr_trend(workouts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Compute best (max) estimated 1RM per date per exercise
    per_exercise: Dict[str, Dict[str, float]] = {}
    for w in workouts:
        ex = (w.get("exercise") or "").strip()
        d = w.get("date")
        if not ex or not d:
            continue
        best_for_date = 0.0
        for s in (w.get("sets") or []):
            try:
                est = epley_one_rm(float(s.get("weight_kg", 0)), int(s.get("reps", 0)))
                if est > best_for_date:
                    best_for_date = est
            except Exception:
                continue
        if best_for_date > 0:
            per_exercise.setdefault(ex, {})
            prev = per_exercise[ex].get(d, 0.0)
            if best_for_date > prev:
                per_exercise[ex][d] = best_for_date

    trend: List[Dict[str, Any]] = []
    for ex, date_to_rm in per_exercise.items():
        if len(date_to_rm) < 2:
            continue
        dates_sorted = sorted(date_to_rm.keys())
        first_rm = date_to_rm[dates_sorted[0]]
        last_rm = date_to_rm[dates_sorted[-1]]
        change_pct = 0.0 if first_rm == 0 else (last_rm - first_rm) / first_rm * 100.0
        trend.append(
            {
                "exercise": ex,
                "first": round(first_rm, 2),
                "last": round(last_rm, 2),
                "changePct": round(change_pct, 2),
            }
        )
    # sort by magnitude of change ascending (flat first)
    trend.sort(key=lambda x: abs(x["changePct"]))
    return trend


def _analyze_rules(
    weekly_volume: List[Dict[str, Any]],
    weekly_frequency: List[Dict[str, Any]],
    pr_trend: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    recs: List[Dict[str, Any]] = []

    # Low frequency: average days/week < 2
    if weekly_frequency:
        avg_days = sum(w["days"] for w in weekly_frequency) / max(1, len(weekly_frequency))
        if avg_days < 2.0:
            recs.append(
                {
                    "title": "Increase Training Frequency",
                    "reason": f"Average weekly sessions is {avg_days:.1f} (< 2).",
                    "action": "Add 1 additional training day per week.",
                    "priority": "high",
                }
            )

    # Stagnant volume: last >= 3 weeks within ±15% band (less strict for small samples)
    if len(weekly_volume) >= 3:
        vols = [w["volume"] for w in weekly_volume[-4:]]  # last up to 4 weeks
        if vols:
            avg = sum(vols) / len(vols)
            if avg > 0 and max(vols) - min(vols) <= 0.15 * avg:
                recs.append(
                    {
                        "title": "Apply Progressive Overload",
                        "reason": "Weekly volume has been relatively flat for several weeks.",
                        "action": "Increase load or total reps by 5–10% next week.",
                        "priority": "medium",
                    }
                )

    # Spike caution: last week ≥ 150% of previous week (or previous is small but jump large)
    if len(weekly_volume) >= 2:
        last = weekly_volume[-1]["volume"]
        prev = weekly_volume[-2]["volume"]
        if prev > 0 and last >= 1.5 * prev:
            recs.append(
                {
                    "title": "Manage Recovery After Volume Spike",
                    "reason": f"Last week's volume jumped by {(last/prev-1)*100:.0f}%.",
                    "action": "Add an extra rest day and monitor fatigue; avoid further increases this week.",
                    "priority": "medium",
                }
            )

    # Flat PR trend: any exercise change within ±2%
    for t in pr_trend:
        if abs(t["changePct"]) <= 2.0:
            recs.append(
                {
                    "title": "Plateau Detected in PR",
                    "reason": f"{t['exercise']} 1RM change is {t['changePct']}% (flat).",
                    "action": "Consider a deload week or change rep range (e.g., 8–12 to 5–8).",
                    "priority": "low",
                }
            )
            break

    return recs


_CACHE: Dict[Tuple[int, str], Tuple[float, Dict[str, Any]]] = {}
_TTL_SECONDS = 60.0


def recommend(days: int = 30) -> Dict[str, Any]:
    # Simple TTL cache
    try:
        import time
        cache_key = (int(days), str(getattr(_storage, "DATA_DIR", "data")))
        ts, cached = _CACHE.get(cache_key, (0.0, None))
        if cached is not None and time.time() - ts < _TTL_SECONDS:
            return cached
    except Exception:
        cached = None

    workouts = read_json("workouts")
    dates = [w.get("date") for w in workouts if w.get("date")]
    start, end = _window_bounds(dates, days)

    # filter within window
    win_items = []
    for w in workouts:
        d = w.get("date")
        if not d:
            continue
        try:
            dt = _parse_date(d)
        except Exception:
            continue
        if start <= dt <= end:
            win_items.append(w)

    insufficient = len(win_items) < 6

    weekly_volume, weekly_frequency = _calc_weekly_metrics(win_items)
    pr_tr = _calc_pr_trend(win_items)

    # Always compute recommendations; use insufficientData flag for UI/UX only
    recs = _analyze_rules(weekly_volume, weekly_frequency, pr_tr)

    result = {
        "insufficientData": insufficient,
        "metrics": {
            "weeklyVolume": weekly_volume,
            "weeklyFrequency": weekly_frequency,
            "prTrend": pr_tr,
        },
        "recommendations": recs,
    }

    try:
        import time
        _CACHE[cache_key] = (time.time(), result)
    except Exception:
        pass

    return result


