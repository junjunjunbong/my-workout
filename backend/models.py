from typing import List, Optional
from datetime import date

class SetRecord:
    def __init__(self, weight_kg: float, reps: int):
        self.weight_kg = weight_kg
        self.reps = reps

class CardioRecord:
    def __init__(self, minutes: float, distance_km: Optional[float] = None):
        self.minutes = minutes
        self.distance_km = distance_km

class WorkoutEntry:
    def __init__(self, id: str, date: str, category: str, exercise: str, 
                 type: str, sets: Optional[List[SetRecord]] = None,
                 cardio: Optional[CardioRecord] = None, notes: Optional[str] = None):
        self.id = id
        self.date = date
        self.category = category
        self.exercise = exercise
        self.type = type
        self.sets = sets or []
        self.cardio = cardio
        self.notes = notes

class RoutineItem:
    def __init__(self, exercise: str, sets_count: int, target_reps: int, target_weight: float):
        self.exercise = exercise
        self.sets_count = sets_count
        self.target_reps = target_reps
        self.target_weight = target_weight

class Routine:
    def __init__(self, id: str, name: str, memo: Optional[str], items: List[RoutineItem]):
        self.id = id
        self.name = name
        self.memo = memo
        self.items = items