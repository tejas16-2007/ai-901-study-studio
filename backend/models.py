"""Pydantic request and response models for AI-901 Study Studio API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StudyCoachRequest(BaseModel):
    question_id: Optional[str] = None
    question_text: str = Field(..., min_length=3, max_length=2000)
    selected_option: Optional[str] = None
    correct_option: Optional[str] = None
    topic: Optional[str] = None
    follow_up: Optional[str] = Field(default=None, max_length=1000)


class FoundryChatRequest(BaseModel):
    system_prompt: str = Field(
        default="You are a concise Azure AI Fundamentals (AI-901) assistant.",
        max_length=2000,
    )
    user_prompt: str = Field(..., min_length=1, max_length=2000)
    model: str = Field(default="gpt-4o-mini", max_length=100)
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    max_tokens: int = Field(default=300, ge=32, le=2048)


class FoundryAgentRequest(BaseModel):
    goal: str = Field(..., min_length=3, max_length=1500)
    instructions: str = Field(
        default=(
            "You are an Azure AI Solutions advisor agent. Use the available tools "
            "to recommend the best AI-901 workload, check responsible AI requirements, "
            "and estimate token budget."
        ),
        max_length=2000,
    )
    enabled_tools: List[str] = Field(
        default_factory=lambda: [
            "recommend_foundry_service",
            "responsible_ai_audit",
            "estimate_token_cost",
        ]
    )


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=5, max_length=5000)
    tasks: List[str] = Field(
        default_factory=lambda: ["sentiment", "key_phrases", "entities", "summary"]
    )


class SpeechSimulationRequest(BaseModel):
    direction: str = Field(default="tts", regex="^(tts|stt)$")
    text: str = Field(..., min_length=2, max_length=2000)
    voice: str = Field(default="en-US-AvaMultilingualNeural", max_length=100)
    language: str = Field(default="en-US", max_length=20)


class ContentExtractionRequest(BaseModel):
    modality: str = Field(
        default="document", regex="^(document|image|audio|video)$"
    )
    sample_id: Optional[str] = None
    content: str = Field(..., min_length=5, max_length=6000)
    schema_fields: List[str] = Field(default_factory=list)


class VisionLabRequest(BaseModel):
    task: str = Field(default="analyze", regex="^(analyze|generate)$")
    prompt: str = Field(..., min_length=3, max_length=1500)
    scene_preset: Optional[str] = Field(default="retail_shelf")


class ApiEnvelope(BaseModel):
    mode: str
    service: str
    note: str
    data: Dict[str, Any]
