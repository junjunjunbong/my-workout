from typing import List, Dict, Any, Tuple
from storage import read_json

def compute_daily_summary(target_date: str) -> Tuple[int, float]:
    """Compute summary statistics for a specific date"""
    workouts = read_json("workouts")
    
    # Filter workouts for the target date
    daily_workouts = [w for w in workouts if w.get("date") == target_date]
    
    # Calculate total sets count and volume
    sets_count = 0
    volume = 0.0
    
    for workout in daily_workouts:
        if workout.get("sets"):
            sets_count += len(workout["sets"])
            for set_record in workout["sets"]:
                volume += set_record.get("weight_kg", 0) * set_record.get("reps", 0)
    
    return sets_count, volume