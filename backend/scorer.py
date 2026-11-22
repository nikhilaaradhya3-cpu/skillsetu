"""Scores a task video against a trade rubric.

Two modes:
  * MOCK_AI=1  -> returns a sample result, clearly marked mock=True (no API key needed)
  * otherwise  -> uploads the video to the Gemini API and asks for a JSON rubric result
The AI only PRE-SCORES. A human vouch is still needed for the Verified badge.
"""
import json
import os
import time


def build_prompt(rubric: dict, liveness_code: str) -> str:
    lines = "\n".join(f"- {c['id']}: {c['text']}" for c in rubric["criteria"])
    return f"""You are checking a short video of a tradesperson doing this task: {rubric['title']}.
Judge ONLY what is visible or audible in the video. If something cannot be seen, mark it as not passed and say so.
The worker should read this code aloud or show it on screen: {liveness_code or '(none given)'}.

Rubric criteria:
{lines}

Reply with JSON only, in exactly this shape:
{{"liveness_code_seen": true or false,
  "criteria": [{{"id": "<criterion id>", "passed": true or false, "reason": "<one short sentence>"}}],
  "summary": "<two sentences for the worker, in simple words>"}}"""


def mock_result(rubric: dict) -> dict:
    criteria = []
    for i, c in enumerate(rubric["criteria"]):
        passed = i != len(rubric["criteria"]) - 1  # last one fails, so the demo shows both states
        criteria.append({
            "id": c["id"],
            "passed": passed,
            "reason": "Sample result (mock mode): no real video analysis was done.",
        })
    return {
        "liveness_code_seen": True,
        "criteria": criteria,
        "summary": "This is a sample result from mock mode. Turn off MOCK_AI and add a Gemini key to score real videos.",
        "mock": True,
    }


def score_with_gemini(video_path: str, rubric: dict, liveness_code: str) -> dict:
    from google import genai  # imported here so mock mode works without the package configured

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    video = client.files.upload(file=video_path)
    while video.state and video.state.name == "PROCESSING":
        time.sleep(2)
        video = client.files.get(name=video.name)
    if video.state and video.state.name == "FAILED":
        raise RuntimeError("The video could not be processed by the AI service.")

    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        contents=[video, build_prompt(rubric, liveness_code)],
        config={"response_mime_type": "application/json"},
    )
    data = json.loads(response.text)
    data["mock"] = False
    return data


def score_video(video_path: str, rubric: dict, liveness_code: str = "") -> dict:
    if os.getenv("MOCK_AI", "0") == "1":
        raw = mock_result(rubric)
    else:
        raw = score_with_gemini(video_path, rubric, liveness_code)

    passed = sum(1 for c in raw["criteria"] if c.get("passed"))
    total = len(rubric["criteria"])
    return {
        "task_id": rubric["task_id"],
        "trade": rubric["trade"],
        "title": rubric["title"],
        "criteria": raw["criteria"],
        "passed": passed,
        "total": total,
        "score_percent": round(100 * passed / total),
        "liveness_code_seen": raw.get("liveness_code_seen", False),
        "summary": raw.get("summary", ""),
        "mock": raw.get("mock", False),
        "status": "AI pre-score only. Needs a human vouch to be Verified.",
    }
