"""FastAPI application for AI-901 Study Studio (Dual-Mode Study & Foundry Lab)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import PROJECT_ROOT, Settings
from backend.data.curriculum import (
    EXAM_METADATA,
    EXAM_QUESTIONS,
    FLASHCARDS,
    SANDBOX_SAMPLES,
    STUDY_MODULES,
)
from backend.models import (
    ContentExtractionRequest,
    FoundryAgentRequest,
    FoundryChatRequest,
    SpeechSimulationRequest,
    StudyCoachRequest,
    TextAnalysisRequest,
    VisionLabRequest,
)
from backend.services.content_service import extract_content, run_vision_lab
from backend.services.foundry_service import (
    run_foundry_chat,
    run_single_agent,
    run_study_coach,
)
from backend.services.text_speech_service import analyze_text, run_speech_lab

FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(
    title="AI-901 Study Studio",
    description=(
        "Interactive Microsoft Azure AI Fundamentals (AI-901) Study, Practice Exam, "
        "and Dual-Mode Microsoft Foundry Lab Web App."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_settings() -> Settings:
    return Settings.load()


@app.get("/api/health")
def health() -> Dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ok",
        "overall_mode": settings.overall_mode,
        "exam": EXAM_METADATA["code"],
    }


@app.get("/api/status")
def status() -> Dict[str, Any]:
    settings = get_settings()
    return {
        "overall_mode": settings.overall_mode,
        "configured_mode_flag": settings.mode,
        "services": settings.service_status(),
        "env_hint": "Copy .env.example to .env and fill in Microsoft Foundry credentials to enable Live Mode.",
    }


@app.get("/api/curriculum")
def curriculum() -> Dict[str, Any]:
    return {
        "exam": EXAM_METADATA,
        "modules": STUDY_MODULES,
        "flashcards": FLASHCARDS,
        "questions": EXAM_QUESTIONS,
        "sandbox_samples": SANDBOX_SAMPLES,
    }


@app.post("/api/study-coach")
def study_coach_endpoint(req: StudyCoachRequest) -> Dict[str, Any]:
    return run_study_coach(req, get_settings())


@app.post("/api/labs/chat")
def foundry_chat_endpoint(req: FoundryChatRequest) -> Dict[str, Any]:
    return run_foundry_chat(req, get_settings())


@app.post("/api/labs/agent")
def foundry_agent_endpoint(req: FoundryAgentRequest) -> Dict[str, Any]:
    return run_single_agent(req, get_settings())


@app.post("/api/labs/text-analysis")
def text_analysis_endpoint(req: TextAnalysisRequest) -> Dict[str, Any]:
    return analyze_text(req, get_settings())


@app.post("/api/labs/speech")
def speech_endpoint(req: SpeechSimulationRequest) -> Dict[str, Any]:
    return run_speech_lab(req, get_settings())


@app.post("/api/labs/content-understanding")
def content_understanding_endpoint(req: ContentExtractionRequest) -> Dict[str, Any]:
    return extract_content(req, get_settings())


@app.post("/api/labs/vision")
def vision_endpoint(req: VisionLabRequest) -> Dict[str, Any]:
    return run_vision_lab(req, get_settings())


if (FRONTEND_DIR / "styles").exists():
    app.mount("/styles", StaticFiles(directory=str(FRONTEND_DIR / "styles")), name="styles")
if (FRONTEND_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")


@app.get("/")
def serve_index() -> FileResponse:
    return FileResponse(str(FRONTEND_DIR / "index.html"))
