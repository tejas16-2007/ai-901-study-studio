"""Dual-mode configuration loader for AI-901 Study Studio.

Supports running immediately in local Demo/Mock Mode with zero credentials,
and seamlessly switches individual Microsoft Foundry / Azure AI workloads
to Live Mode when corresponding credentials are provided in `.env` or the
environment.
"""

from __future__ import annotations

import importlib.util
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv_file(env_path: Path) -> None:
    """Load key=value pairs from .env without requiring external packages."""
    if not env_path.exists():
        return
    try:
        import dotenv  # type: ignore

        dotenv.load_dotenv(env_path, override=False)
        return
    except ImportError:
        pass

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _has_package(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ModuleNotFoundError, ValueError):
        return False


@dataclass(frozen=True)
class Settings:
    mode: str
    # Microsoft Foundry / Azure OpenAI
    azure_ai_project_endpoint: str
    azure_openai_endpoint: str
    azure_openai_api_key: str
    azure_openai_api_version: str
    azure_openai_chat_deployment: str
    azure_openai_vision_deployment: str
    azure_ai_agent_id: str
    # Azure Language
    azure_language_endpoint: str
    azure_language_key: str
    # Azure Speech
    azure_speech_key: str
    azure_speech_region: str
    # Azure Content Understanding
    azure_content_understanding_endpoint: str
    azure_content_understanding_key: str
    azure_content_understanding_api_version: str
    # Server
    host: str
    port: int

    @classmethod
    def load(cls, env_file: Path | None = None) -> "Settings":
        _load_dotenv_file(env_file or (PROJECT_ROOT / ".env"))
        mode = os.getenv("AI901_MODE", "auto").strip().lower()
        if mode not in {"auto", "mock", "live"}:
            mode = "auto"

        return cls(
            mode=mode,
            azure_ai_project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").strip(),
            azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", "").strip(),
            azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY", "").strip(),
            azure_openai_api_version=os.getenv(
                "AZURE_OPENAI_API_VERSION", "2024-12-01-preview"
            ).strip(),
            azure_openai_chat_deployment=os.getenv(
                "AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini"
            ).strip(),
            azure_openai_vision_deployment=os.getenv(
                "AZURE_OPENAI_VISION_DEPLOYMENT", "gpt-4o-mini"
            ).strip(),
            azure_ai_agent_id=os.getenv("AZURE_AI_AGENT_ID", "").strip(),
            azure_language_endpoint=os.getenv("AZURE_LANGUAGE_ENDPOINT", "").strip(),
            azure_language_key=os.getenv("AZURE_LANGUAGE_KEY", "").strip(),
            azure_speech_key=os.getenv("AZURE_SPEECH_KEY", "").strip(),
            azure_speech_region=os.getenv("AZURE_SPEECH_REGION", "eastus").strip(),
            azure_content_understanding_endpoint=os.getenv(
                "AZURE_CONTENT_UNDERSTANDING_ENDPOINT", ""
            ).strip(),
            azure_content_understanding_key=os.getenv(
                "AZURE_CONTENT_UNDERSTANDING_KEY", ""
            ).strip(),
            azure_content_understanding_api_version=os.getenv(
                "AZURE_CONTENT_UNDERSTANDING_API_VERSION", "2025-05-01-preview"
            ).strip(),
            host=os.getenv("HOST", "0.0.0.0").strip(),
            port=int(os.getenv("PORT", "8000")),
        )

    def _service_live(self, has_creds: bool, sdk_ready: bool = True) -> bool:
        if self.mode == "mock":
            return False
        if self.mode == "live":
            return has_creds and sdk_ready
        return has_creds and sdk_ready

    @property
    def foundry_chat_live(self) -> bool:
        has_openai = bool(self.azure_openai_endpoint and self.azure_openai_api_key)
        has_project = bool(self.azure_ai_project_endpoint) and _has_package(
            "azure.ai.projects"
        )
        return self._service_live(has_openai or has_project)

    @property
    def foundry_agent_live(self) -> bool:
        has_project = bool(self.azure_ai_project_endpoint) and _has_package(
            "azure.ai.projects"
        )
        has_openai = bool(self.azure_openai_endpoint and self.azure_openai_api_key)
        return self._service_live(has_project or has_openai)

    @property
    def text_analytics_live(self) -> bool:
        has_creds = bool(self.azure_language_endpoint and self.azure_language_key)
        return self._service_live(has_creds)

    @property
    def speech_live(self) -> bool:
        has_creds = bool(self.azure_speech_key and self.azure_speech_region)
        return self._service_live(has_creds)

    @property
    def content_understanding_live(self) -> bool:
        has_creds = bool(
            self.azure_content_understanding_endpoint
            and self.azure_content_understanding_key
        )
        return self._service_live(has_creds)

    @property
    def vision_live(self) -> bool:
        has_creds = bool(self.azure_openai_endpoint and self.azure_openai_api_key)
        return self._service_live(has_creds)

    def service_status(self) -> Dict[str, dict]:
        """Return per-service dual-mode status for the UI status drawer."""
        services = {
            "foundry_chat": {
                "label": "Microsoft Foundry Chat & Study Coach",
                "mode": "live" if self.foundry_chat_live else "mock",
                "configured": bool(
                    (self.azure_openai_endpoint and self.azure_openai_api_key)
                    or self.azure_ai_project_endpoint
                ),
                "sdk_installed": _has_package("openai") or _has_package("azure.ai.projects"),
                "env_vars": [
                    "AZURE_OPENAI_ENDPOINT",
                    "AZURE_OPENAI_API_KEY",
                    "AZURE_OPENAI_CHAT_DEPLOYMENT",
                ],
            },
            "foundry_agent": {
                "label": "Microsoft Foundry Single-Agent Service",
                "mode": "live" if self.foundry_agent_live else "mock",
                "configured": bool(
                    self.azure_ai_project_endpoint
                    or (self.azure_openai_endpoint and self.azure_openai_api_key)
                ),
                "sdk_installed": _has_package("azure.ai.projects") or _has_package("openai"),
                "env_vars": ["AZURE_AI_PROJECT_ENDPOINT", "AZURE_AI_AGENT_ID"],
            },
            "text_analytics": {
                "label": "Azure Language (Text Analysis)",
                "mode": "live" if self.text_analytics_live else "mock",
                "configured": bool(self.azure_language_endpoint and self.azure_language_key),
                "sdk_installed": _has_package("azure.ai.textanalytics"),
                "env_vars": ["AZURE_LANGUAGE_ENDPOINT", "AZURE_LANGUAGE_KEY"],
            },
            "speech": {
                "label": "Azure Speech in Foundry Tools",
                "mode": "live" if self.speech_live else "mock",
                "configured": bool(self.azure_speech_key and self.azure_speech_region),
                "sdk_installed": _has_package("azure.cognitiveservices.speech"),
                "env_vars": ["AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION"],
            },
            "content_understanding": {
                "label": "Azure Content Understanding",
                "mode": "live" if self.content_understanding_live else "mock",
                "configured": bool(
                    self.azure_content_understanding_endpoint
                    and self.azure_content_understanding_key
                ),
                "sdk_installed": True,  # Uses REST API directly
                "env_vars": [
                    "AZURE_CONTENT_UNDERSTANDING_ENDPOINT",
                    "AZURE_CONTENT_UNDERSTANDING_KEY",
                ],
            },
            "vision": {
                "label": "Multimodal Vision & Image Generation",
                "mode": "live" if self.vision_live else "mock",
                "configured": bool(self.azure_openai_endpoint and self.azure_openai_api_key),
                "sdk_installed": _has_package("openai"),
                "env_vars": [
                    "AZURE_OPENAI_ENDPOINT",
                    "AZURE_OPENAI_API_KEY",
                    "AZURE_OPENAI_VISION_DEPLOYMENT",
                ],
            },
        }
        return services

    @property
    def overall_mode(self) -> str:
        statuses = [s["mode"] for s in self.service_status().values()]
        if all(m == "live" for m in statuses):
            return "live"
        if any(m == "live" for m in statuses):
            return "hybrid"
        return "mock"
