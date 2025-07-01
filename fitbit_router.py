# fitbit_router.py

import os
import base64
import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from dotenv import load_dotenv
import httpx

load_dotenv()

router = APIRouter()

CLIENT_ID = os.getenv("FITBIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("FITBIT_CLIENT_SECRET")
REDIRECT_URI = os.getenv("FITBIT_REDIRECT_URI")

TOKEN_FILE = "tokens.json"
user_tokens = {}

def save_tokens():
    with open(TOKEN_FILE, "w") as f:
        json.dump(user_tokens, f)

def load_tokens():
    global user_tokens
    try:
        with open(TOKEN_FILE, "r") as f:
            user_tokens = json.load(f)
    except FileNotFoundError:
        user_tokens = {}

load_tokens()

@router.get("/")
def index():
    return HTMLResponse("<h1>Fitbit LLM Integration Demo</h1><a href='/fitbit/auth/fitbit/start'>Connect to Fitbit</a>")

@router.get("/auth/fitbit/start")
def fitbit_auth_start():
    scope = "activity heartrate sleep profile"
    auth_url = (
        "https://www.fitbit.com/oauth2/authorize"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={scope}"
        f"&expires_in=604800"
        f"&prompt=consent"
    )
    return RedirectResponse(auth_url)

@router.get("/auth/fitbit/callback")
async def fitbit_auth_callback(code: Optional[str] = None):
    if not code:
        return HTMLResponse("Authorization failed", status_code=400)
    token_url = "https://api.fitbit.com/oauth2/token"
    basic_auth = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI,
        "code": code
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(token_url, data=data, headers=headers)
    if resp.status_code != 200:
        return HTMLResponse(f"Failed to get token: {resp.text}", status_code=400)
    tokens = resp.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    user_id = tokens["user_id"]
    user_tokens[user_id] = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    save_tokens()
    return HTMLResponse(
        f"<h2>Fitbit Connected!</h2>"
        f"<p>Your User ID: <b>{user_id}</b></p>"
        f"<p><a href='/fitbit/activity-range?user_id={user_id}&metrics=steps&start_date=2022-01-01&end_date=2022-01-01'>See Activity Data</a></p>"
    )

def get_user_token(user_id: str):
    if user_id not in user_tokens:
        raise HTTPException(401, "User not authorized or token missing")
    return user_tokens[user_id]["access_token"]

async def fetch_metric(client, metric, start_date, end_date, headers):
    # Map metrics to Fitbit API fields and endpoints
    metric_map = {
        "steps": ("activities-steps", f"https://api.fitbit.com/1/user/-/activities/steps/date/{start_date}/{end_date}.json"),
        "distance": ("activities-distance", f"https://api.fitbit.com/1/user/-/activities/distance/date/{start_date}/{end_date}.json"),
        "calories": ("activities-calories", f"https://api.fitbit.com/1/user/-/activities/calories/date/{start_date}/{end_date}.json"),
        "minutesAsleep": ("sleep-minutesAsleep", f"https://api.fitbit.com/1.2/user/-/sleep/minutesAsleep/date/{start_date}/{end_date}.json"),
        "sleepScore": ("sleep-score", f"https://api.fitbit.com/1.2/user/-/sleep/score/date/{start_date}/{end_date}.json"),
        "restingHeartRate": ("activities-heart", f"https://api.fitbit.com/1/user/-/activities/heart/date/{start_date}/{end_date}.json"),
    }
    if metric not in metric_map:
        return []
    field, url = metric_map[metric]
    r = await client.get(url, headers=headers)
    if r.status_code == 200:
        return r.json().get(field, [])
    elif r.status_code == 400 or r.status_code == 429:
        print(f"Warning: No {field} data or rate limit: {r.status_code}")
        return []
    elif r.status_code == 404:
        print(f"Not Found: {field} data: {r.text}")
        return []
    else:
        print(f"ERROR: {field} failed: {r.status_code} {r.text}")
        raise HTTPException(r.status_code, f"{field} error: {r.text}")

@router.get("/activity-range")
async def activity_range(
    user_id: str,
    metrics: str = Query(..., description="Comma-separated list of metrics (steps, calories, etc.)"),
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD")
):
    metrics_list = [m.strip() for m in metrics.split(",")]
    access_token = get_user_token(user_id)
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=60) as client:
        results_by_metric = {}
        for metric in metrics_list:
            data = await fetch_metric(client, metric, start_date, end_date, headers)
            results_by_metric[metric] = data

    # Merge results by date
    dates = set()
    for metric, data in results_by_metric.items():
        for entry in data:
            dates.add(entry["dateTime"])

    merged = []
    for dt in sorted(dates):
        entry = {"date": dt}
        for metric in metrics_list:
            data = results_by_metric.get(metric, [])
            value = next((d.get("value") for d in data if d["dateTime"] == dt), None)
            if value is not None:
                try:
                    value = float(value)
                    if value.is_integer():
                        value = int(value)
                except Exception:
                    pass
            entry[metric] = value
        merged.append(entry)
    return merged
