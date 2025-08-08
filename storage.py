from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "workouts": DATA_DIR / "workouts.json",
    "routines": DATA_DIR / "routines.json",
    "config": DATA_DIR / "config.json",
}

DEFAULT_CONFIG = {
    "categories": ["상체", "하체", "전신", "유산소"],
    "exercises": {
        "상체": ["벤치프레스", "덤벨프레스", "랫풀다운", "오버헤드프레스", "바벨로우"],
        "하체": ["스쿼트", "레그프레스", "루마니안 데드리프트", "레그컬"],
        "전신": ["데드리프트", "클린&프레스", "버피"],
        "유산소": ["런닝", "사이클", "로잉"]
    },
    "week_start": "monday",
}

for key, path in FILES.items():
    if not path.exists():
        if key == "config":
            path.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            path.write_text("[]", encoding="utf-8")


def read_json(name: str):
    path = FILES[name]
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(name: str, data: Any):
    path = FILES[name]
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


def append_workouts(entries: List[Dict[str, Any]]):
    data = read_json("workouts")
    data.extend(entries)
    write_json("workouts", data)


def save_workouts(entries: List[Dict[str, Any]]):
    write_json("workouts", entries)


def save_routines(routines: List[Dict[str, Any]]):
    write_json("routines", routines)
