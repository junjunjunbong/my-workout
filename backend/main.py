from fastapi import FastAPI, HTTPException, Depends, status, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import date
from pydantic import BaseModel
import uuid
import json
import os
from pathlib import Path

# Prefer package-qualified imports when running as backend.main; fall back for test context
try:
    from backend.storage import read_json, write_json, append_workouts
    from backend.schemas.user_schemas import (
        UserRegisterRequest,
        UserRegisterResponse,
        UserLoginRequest,
        UserLoginResponse,
    )
    from backend.schemas.user_profile_schemas import (
        UserProfileResponse,
        UserProfileUpdateRequest,
    )
    from backend.services.user_service import (
        create_user,
        authenticate_user,
        get_user_by_email,
        get_user_profile,
        update_user_profile,
    )
    from backend.services.auth_service import create_access_token, auth_dependency
    from backend.services.social_service import (
        record_activity,
        follow_user,
        unfollow_user,
        get_feed as get_social_feed,
        like_item,
        unlike_item,
        create_comment,
        get_comments,
        delete_comment,
    )
    from backend.services.analytics_service import pr_trend, muscle_volume_by_category, exercise_detail
    from backend.services.coach_service import recommend as coach_recommend
except ImportError:
    from storage import read_json, write_json, append_workouts
    from schemas.user_schemas import (
        UserRegisterRequest,
        UserRegisterResponse,
        UserLoginRequest,
        UserLoginResponse,
    )
    from schemas.user_profile_schemas import (
        UserProfileResponse,
        UserProfileUpdateRequest,
    )
    from services.user_service import (
        create_user,
        authenticate_user,
        get_user_by_email,
        get_user_profile,
        update_user_profile,
    )
    from services.auth_service import create_access_token, auth_dependency
    from services.social_service import (
        record_activity,
        follow_user,
        unfollow_user,
        get_feed as get_social_feed,
        like_item,
        unlike_item,
        create_comment,
        get_comments,
        delete_comment,
    )
    from services.analytics_service import pr_trend, muscle_volume_by_category, exercise_detail
    from services.coach_service import recommend as coach_recommend

app = FastAPI(title="My Workout API")

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'data', 'workout.db')

# External AI via OpenAI SDK targeting OpenRouter
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-oss-20b:free")
SITE_TITLE = os.getenv("SITE_TITLE", "My Workout Tracker")
SITE_REFERER = os.getenv("SITE_REFERER", "https://localhost:3001")

client = None

def get_openai_client():
    global client
    if client is None:
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")
        client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
    return client

# Services (legacy removed)
# from services.ai_service import generate_today_routine

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class SetRecordModel(BaseModel):
    weight_kg: float
    reps: int

class CardioRecordModel(BaseModel):
    minutes: float
    distance_km: Optional[float] = None

class WorkoutCreateModel(BaseModel):
    date: str
    category: str
    exercise: str
    type: str
    sets: Optional[List[SetRecordModel]] = None
    cardio: Optional[CardioRecordModel] = None
    notes: Optional[str] = None

class RoutineItemModel(BaseModel):
    exercise: str
    category: str
    sets: int
    reps: str

class RoutineCreateModel(BaseModel):
    name: str
    memo: Optional[str] = None
    items: List[RoutineItemModel] = []

class ActivityCreateModel(BaseModel):
    type: str
    ref_id: Optional[str] = None

# API Routes

@app.get("/")
def read_root():
    return {"message": "My Workout API"}

@app.get("/api/config")
def get_config():
    return read_json("config")

@app.get("/api/workouts")
def get_workouts():
    return read_json("workouts")

@app.get("/api/workouts/{target_date}")
def get_workouts_by_date(target_date: str):
    workouts = read_json("workouts")
    return [w for w in workouts if w.get("date") == target_date]

@app.post("/api/workouts")
def add_workout(workout: WorkoutCreateModel):
    # Normalize sets to weight_kg/reps only
    norm_sets = []
    if workout.sets:
        for s in workout.sets:
            norm_sets.append({
                "weight_kg": float(s.weight_kg),
                "reps": int(s.reps),
            })

    entry = {
        "id": str(uuid.uuid4()),
        "date": workout.date,
        "category": workout.category,
        "exercise": workout.exercise,
        "type": workout.type,
        "sets": norm_sets,
        "cardio": workout.cardio.model_dump() if workout.cardio else None,
        "notes": workout.notes,
    }
    
    data = read_json("workouts")
    data.append(entry)
    write_json("workouts", data)
    return entry

@app.delete("/api/workouts/{workout_id}")
def remove_workout(workout_id: str):
    data = read_json("workouts")
    data = [w for w in data if w.get("id") != workout_id]
    write_json("workouts", data)
    return {"message": "Workout deleted"}

@app.get("/api/workouts/exercise/{exercise}/last")
def get_last_workout_for_exercise(exercise: str):
    workouts = read_json("workouts")
    items = [w for w in workouts if w.get("exercise") == exercise]
    items.sort(key=lambda x: x.get("date", ""), reverse=True)
    return items[0] if items else None

@app.get("/api/routines")
def get_routines():
    return read_json("routines")

@app.post("/api/routines")
def add_routine(routine: RoutineCreateModel):
    routines = read_json("routines")
    new_routine = {
        "id": str(uuid.uuid4()),
        "name": routine.name,
        "memo": routine.memo,
        "items": [item.model_dump() for item in routine.items],
    }
    routines.append(new_routine)
    write_json("routines", routines)
    return new_routine

@app.delete("/api/routines/{routine_id}")
def remove_routine(routine_id: str):
    routines = read_json("routines")
    routines = [r for r in routines if r.get("id") != routine_id]
    write_json("routines", routines)
    return {"message": "Routine deleted"}

@app.get("/api/analytics/weekly-volume")
def get_weekly_volume():
    from services.analytics_service import weekly_volume
    return weekly_volume().to_dict(orient="records")

@app.get("/api/analytics/monthly-volume")
def get_monthly_volume():
    from services.analytics_service import monthly_volume
    return monthly_volume().to_dict(orient="records")

@app.get("/api/analytics/pr-trend")
def get_pr_trend(exercise: str, start: str | None = None, end: str | None = None):
    """Return PR (1RM) trend for an exercise within [start, end]."""
    if not exercise or not exercise.strip():
        raise HTTPException(status_code=400, detail="exercise required")
    return pr_trend(exercise.strip(), start, end)

@app.get("/api/analytics/muscle-volume-range")
def get_muscle_volume_range(start: str | None = None, end: str | None = None):
    """Return aggregated volume by category within [start, end]."""
    return muscle_volume_by_category(start, end)

@app.get("/api/analytics/exercise-detail")
def get_exercise_detail(exercise: str, start: str | None = None, end: str | None = None):
    if not exercise or not exercise.strip():
        raise HTTPException(status_code=400, detail="exercise required")
    return exercise_detail(exercise.strip(), start, end)

@app.get("/api/coach/recommendations")
def get_coach_recommendations(days: int = 30):
    if days < 7 or days > 180:
        raise HTTPException(status_code=400, detail="days must be in [7, 180]")
    return coach_recommend(days)

@app.post("/api/social/activity", status_code=status.HTTP_201_CREATED)
def create_activity(act: ActivityCreateModel, payload: dict = Depends(auth_dependency)):
    """Create a simple activity row for feed demos/tests."""
    user_id = int(payload.get("sub"))
    if not act.type or not act.type.strip():
        raise HTTPException(status_code=400, detail="type required")
    new_id = record_activity(user_id=user_id, activity_type=act.type.strip(), ref_id=(act.ref_id or None))
    return {"id": new_id}

@app.get("/api/calendar-summary/{target_date}")
def get_calendar_summary(target_date: str):
    from services.workouts_service import compute_daily_summary
    sets_count, volume = compute_daily_summary(target_date)
    return {"sets_count": sets_count, "volume": volume}

# AI endpoints
class TodayAIRequest(BaseModel):
    workouts: List[dict]

class AIChatRequest(BaseModel):
    message: str
    routine: dict | None = None
    workouts: List[dict] | None = None

PROMPT_TODAY = (
    "You are a professional strength and conditioning coach. Based on the user's recent workouts, "
    "propose an optimal routine for today in concise JSON with the following schema: {name, memo, items:[{exercise, category, sets, reps}]}. "
    "Prefer balancing muscle groups across recent sessions, include at most 5 items, keep reps as string (e.g., '8-12' or '30분'). "
    "Return ONLY the JSON and nothing else. Use Korean for names and memo."
)

PROMPT_CHAT = (
    "You are a training assistant chatting in Korean. Given the user's recent workouts and the proposed routine, "
    "answer the user's question. If a specific routine change is requested, reply normally and also output an optional 'updatedRoutine' JSON matching {name, memo, items}."
)

def call_openai(messages: list[dict], json_only: bool = False) -> str:
    try:
        openai_client = get_openai_client()
        kwargs = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.7,
            "extra_headers": {
                "HTTP-Referer": SITE_REFERER,
                "X-Title": SITE_TITLE,
            },
        }
        if json_only:
            kwargs["response_format"] = {"type": "json_object"}
        completion = openai_client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content
    except Exception as e:
        # Catching the specific HTTPException from get_openai_client
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=502, detail=f"AI error: {e}")

@app.post("/api/ai/today-routine")
async def create_today_routine(req: TodayAIRequest):
    sys = {"role": "system", "content": PROMPT_TODAY}
    user = {"role": "user", "content": f"최근 운동 기록 JSON:\n{json.dumps(req.workouts, ensure_ascii=False)}"}
    out = call_openai([sys, user], json_only=True)
    # Expect pure JSON
    routine = json.loads(out)
    if not isinstance(routine.get("items"), list):
        raise HTTPException(status_code=500, detail="Invalid AI response: items missing")
    return routine

@app.post("/api/ai/chat")
async def ai_chat(req: AIChatRequest):
    sys = {"role": "system", "content": PROMPT_CHAT}
    ctx = {
        "routine": req.routine,
        "recentWorkouts": req.workouts,
    }
    user = {"role": "user", "content": f"사용자 질문: {req.message}\n컨텍스트:\n{json.dumps(ctx, ensure_ascii=False)}"}
    out = call_openai([sys, user])
    reply = out
    updated = None
    try:
        # 요청 반영한 updatedRoutine만 JSON으로 재요청
        sys2 = {"role": "system", "content": "아래 요청/컨텍스트를 반영한 updatedRoutine만 JSON으로 출력. 다른 텍스트 금지."}
        schema = '{"name":"","memo":"","items":[{"exercise":"","category":"","sets":0,"reps":""}]}'
        user2 = {"role": "user", "content": f"요청:\n{req.message}\n컨텍스트:\n{json.dumps(ctx, ensure_ascii=False)}\n스키마: {schema}"}
        out2 = call_openai([sys2, user2], json_only=True)
        parsed = json.loads(out2)
        if isinstance(parsed, dict) and parsed.get('items'):
            updated = parsed
    except Exception:
        updated = None
    return {"reply": reply, "updatedRoutine": updated}

# -----------------
# Auth & Protected
# -----------------

@app.post("/api/auth/login", response_model=UserLoginResponse)
async def login_user(login_data: UserLoginRequest):
    user = authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(subject=user["id"]) 
    return UserLoginResponse(success=True, message="Login successful", user_id=user["id"], token=token)

@app.get("/api/protected/ping")
async def protected_ping(payload: dict = Depends(auth_dependency)):
    return {"message": "pong", "user_id": int(payload.get("sub"))}

@app.post("/api/auth/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterRequest):
    """
    Register a new user account.
    
    Args:
        user_data: User registration data including email and password
        
    Returns:
        UserRegisterResponse with success status and message
        
    Raises:
        HTTPException: 400 for validation errors, 409 for duplicate email
    """
    try:
        # Create user using the service function
        user = create_user(user_data.email, user_data.password)
        return UserRegisterResponse(
            success=True,
            message="User registered successfully",
            user_id=user["id"]
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions (like 400 for validation errors)
        raise e
    except Exception as e:
        # Handle duplicate email error specifically
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        # Handle other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during registration"
        )

@app.get("/api/users/me", response_model=UserProfileResponse)
async def get_me(payload: dict = Depends(auth_dependency)):
    user_id = int(payload.get("sub"))
    profile = get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile

@app.patch("/api/users/me", response_model=UserProfileResponse)
async def update_me(update: UserProfileUpdateRequest, payload: dict = Depends(auth_dependency)):
    user_id = int(payload.get("sub"))
    # The `update_user_profile` service handles the logic of checking for fields
    updated_profile = update_user_profile(user_id, update.model_dump())
    if not updated_profile:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_profile

# -----------------
# Social (Follow & Feed)
# -----------------

class FollowRequest(BaseModel):
    user_id: int

@app.post("/api/social/follow", status_code=status.HTTP_201_CREATED)
async def follow_user_endpoint(req: FollowRequest, payload: dict = Depends(auth_dependency)):
    follower_id = int(payload.get("sub"))
    followee_id = req.user_id
    follow_user(follower_id, followee_id)
    return {"success": True}

@app.delete("/api/social/follow", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user_endpoint(req: FollowRequest, payload: dict = Depends(auth_dependency)):
    follower_id = int(payload.get("sub"))
    followee_id = req.user_id
    unfollow_user(follower_id, followee_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/api/social/feed")
async def get_feed_endpoint(limit: int = 20, cursor: Optional[str] = None, payload: dict = Depends(auth_dependency)):
    user_id = int(payload.get("sub"))
    return get_social_feed(user_id, limit, cursor)

# -----------------
# Likes & Comments
# -----------------

class LikeRequest(BaseModel):
    ref_id: str

@app.post("/api/social/like", status_code=status.HTTP_201_CREATED)
async def like_item_endpoint(req: LikeRequest, payload: dict = Depends(auth_dependency)):
    user_id = int(payload.get("sub"))
    like_item(user_id, req.ref_id)
    return {"success": True}

@app.delete("/api/social/like", status_code=status.HTTP_204_NO_CONTENT)
async def unlike_item_endpoint(req: LikeRequest, payload: dict = Depends(auth_dependency)):
    user_id = int(payload.get("sub"))
    unlike_item(user_id, req.ref_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

class CommentCreateRequest(BaseModel):
    ref_id: str
    content: str

@app.post("/api/social/comment", status_code=status.HTTP_201_CREATED)
async def create_comment_endpoint(req: CommentCreateRequest, payload: dict = Depends(auth_dependency)):
    user_id = int(payload.get("sub"))
    new_comment = create_comment(user_id, req.ref_id, req.content)
    return new_comment

@app.get("/api/social/comments")
async def list_comments_endpoint(ref_id: str, payload: dict = Depends(auth_dependency)):
    # The auth dependency is kept to ensure the user is logged in, even if user_id isn't used directly
    return get_comments(ref_id)

@app.delete("/api/social/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_endpoint(comment_id: int, payload: dict = Depends(auth_dependency)):
    user_id = int(payload.get("sub"))
    delete_comment(comment_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)