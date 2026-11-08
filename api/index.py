import json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.scoring import score_lead

app = FastAPI()


@app.post("/")
async def score(request: Request):
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 100_000:
            return JSONResponse({"error": "request_too_large"}, status_code=413)
    try:
        data = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return JSONResponse({"error": "invalid_json"}, status_code=400)
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("lead_id"), str)
        or not data["lead_id"].strip()
        or not isinstance(data.get("channel"), str)
        or not isinstance(data.get("conversation"), list)
    ):
        return JSONResponse({"error": "validation_error"}, status_code=422)
    messages = data["conversation"]
    invalid_message = any(
        not isinstance(message, dict)
        or not isinstance(message.get("role"), str)
        or not isinstance(message.get("text"), str)
        for message in messages
    )
    if invalid_message:
        return JSONResponse({"error": "validation_error"}, status_code=422)

    lead_messages = [message["text"] for message in messages if message["role"] == "lead"]
    if not any(text.strip() for text in lead_messages):
        return JSONResponse({"error": "validation_error"}, status_code=422)
    try:
        return score_lead(data["lead_id"], lead_messages)
    except Exception:
        return JSONResponse({"error": "internal_error"}, status_code=500)
