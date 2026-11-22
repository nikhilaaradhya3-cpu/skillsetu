import io
import json
import os
import secrets
import shutil
import tempfile
from pathlib import Path

import qrcode
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from scorer import score_video

load_dotenv()

app = FastAPI(title="SkillSetu API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

RUBRIC_DIR = Path(__file__).parent / "rubrics"
PASSPORTS: dict[str, dict] = {}  # in memory for the demo; resets when the server restarts. Supabase later.


def load_rubrics() -> dict[str, dict]:
    rubrics = {}
    for path in sorted(RUBRIC_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rubrics[data["task_id"]] = data
    return rubrics


@app.get("/health")
def health():
    return {"ok": True, "mock_ai": os.getenv("MOCK_AI", "0") == "1"}


@app.get("/tasks")
def tasks():
    return [
        {k: r[k] for k in ("task_id", "trade", "title", "instructions")}
        for r in load_rubrics().values()
    ]


@app.post("/score")
async def score(
    task_id: str = Form(...),
    liveness_code: str = Form(""),
    video: UploadFile = File(...),
):
    rubric = load_rubrics().get(task_id)
    if rubric is None:
        raise HTTPException(404, "Unknown task_id")
    if not (video.content_type or "").startswith("video/"):
        raise HTTPException(400, "Please upload a video file")

    suffix = Path(video.filename or "video.mp4").suffix or ".mp4"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(video.file, tmp)
        tmp_path = tmp.name
    try:
        return score_video(tmp_path, rubric, liveness_code)
    except Exception as exc:  # show a readable error instead of a crash
        raise HTTPException(502, f"Scoring failed: {exc}")
    finally:
        os.unlink(tmp_path)


class PassportIn(BaseModel):
    worker_name: str
    area: str = ""
    result: dict


@app.post("/passports")
def create_passport(body: PassportIn):
    passport_id = secrets.token_urlsafe(6)
    PASSPORTS[passport_id] = {
        "id": passport_id,
        "worker_name": body.worker_name,
        "area": body.area,
        "result": body.result,
        "vouches": [],  # vouching with OTP is not built yet
        "verified": False,
    }
    return PASSPORTS[passport_id]


@app.get("/passports/{passport_id}")
def get_passport(passport_id: str):
    if passport_id not in PASSPORTS:
        raise HTTPException(404, "Passport not found")
    return PASSPORTS[passport_id]


@app.get("/passports/{passport_id}/qr")
def passport_qr(passport_id: str):
    if passport_id not in PASSPORTS:
        raise HTTPException(404, "Passport not found")
    base = os.getenv("PUBLIC_BASE_URL", "http://localhost:5500")
    img = qrcode.make(f"{base}/index.html?passport={passport_id}")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")
