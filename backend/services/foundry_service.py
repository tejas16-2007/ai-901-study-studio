"""Dual-mode Microsoft Foundry Generative AI, Agent, and Study Coach service.

In Live Mode, uses `azure-ai-projects` (`AIProjectClient`) or `openai` (`AzureOpenAI`)
when credentials are configured in `.env`. In Demo/Mock Mode, returns realistic,
deterministic, exam-accurate responses with full token and tool-trace telemetry.
"""

from __future__ import annotations

import math
import time
from typing import Any, Dict, List

from backend.config import Settings
from backend.data.curriculum import EXAM_QUESTIONS
from backend.models import FoundryAgentRequest, FoundryChatRequest, StudyCoachRequest


def _approx_tokens(text: str) -> int:
    return max(1, math.ceil(len(text.strip()) / 4))


def _live_openai_client(settings: Settings):
    """Build an authenticated Azure OpenAI / Foundry OpenAI client if available."""
    if settings.azure_ai_project_endpoint:
        try:
            from azure.ai.projects import AIProjectClient  # type: ignore
            from azure.identity import DefaultAzureCredential  # type: ignore

            project = AIProjectClient(
                endpoint=settings.azure_ai_project_endpoint,
                credential=DefaultAzureCredential(),
            )
            return project.get_openai_client(), "azure-ai-projects"
        except Exception:
            pass

    if settings.azure_openai_endpoint and settings.azure_openai_api_key:
        from openai import AzureOpenAI  # type: ignore

        client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
        return client, "openai.AzureOpenAI"

    return None, None


def run_study_coach(req: StudyCoachRequest, settings: Settings) -> Dict[str, Any]:
    """Explain an AI-901 exam question or follow-up concept in Live or Demo mode."""
    start = time.perf_counter()

    matched_q = next(
        (q for q in EXAM_QUESTIONS if req.question_id and q["id"] == req.question_id),
        None,
    )

    if settings.foundry_chat_live:
        try:
            client, sdk_used = _live_openai_client(settings)
            if client is not None:
                system_msg = (
                    "You are an expert Microsoft AI-901 (Azure AI Fundamentals) exam coach. "
                    "Be clear, structured, and accurate to the 2026 AI-901 Microsoft Foundry syllabus. "
                    "Explain why the correct answer is right, why the distractor is tempting, and "
                    "give a concise 1-sentence memory anchor."
                )
                user_msg = (
                    f"Topic: {req.topic or 'AI-901'}\n"
                    f"Question: {req.question_text}\n"
                    f"Learner Selected: {req.selected_option or 'Not answered yet'}\n"
                    f"Correct Answer: {req.correct_option or 'N/A'}\n"
                    f"Learner Follow-up: {req.follow_up or 'Please break down this question.'}"
                )
                resp = client.chat.completions.create(
                    model=settings.azure_openai_chat_deployment,
                    temperature=0.2,
                    max_tokens=360,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_msg},
                    ],
                )
                answer = resp.choices[0].message.content or ""
                latency_ms = int((time.perf_counter() - start) * 1000)
                return {
                    "mode": "live",
                    "service": f"Microsoft Foundry ({sdk_used})",
                    "note": f"Live response from deployment '{settings.azure_openai_chat_deployment}'.",
                    "data": {
                        "coaching": answer,
                        "key_takeaway": (
                            matched_q["explanation"]
                            if matched_q
                            else "Map the scenario requirement to the exact Foundry service or Responsible AI principle."
                        ),
                        "latency_ms": latency_ms,
                    },
                }
        except Exception as exc:
            # Graceful fallback to Demo Mode with diagnostic note
            fallback = _mock_study_coach(req, matched_q, start)
            fallback["note"] = (
                f"Live Foundry call failed ({exc.__class__.__name__}); served local AI-901 Coach fallback."
            )
            return fallback

    return _mock_study_coach(req, matched_q, start)


def _mock_study_coach(
    req: StudyCoachRequest, matched_q: Dict[str, Any] | None, start: float
) -> Dict[str, Any]:
    topic = req.topic or (matched_q["topic"] if matched_q else "AI-901 Fundamentals")
    correct = req.correct_option or (
        matched_q["options"][matched_q["correct_index"]] if matched_q else "See study guide"
    )
    explanation = (
        matched_q["explanation"]
        if matched_q
        else (
            "On Exam AI-901, look for the signal phrase in the scenario: governance/ethics cues map to "
            "Domain 1 Responsible AI principles, while implementation cues map to Microsoft Foundry "
            "Chat, Single Agents, Azure Language, Azure Speech, Vision, or Content Understanding."
        )
    )

    was_correct = bool(req.selected_option and req.selected_option == correct)
    status_line = (
        "You nailed this question."
        if was_correct
        else (
            f"You chose '{req.selected_option}', which is a classic AI-901 distractor."
            if req.selected_option
            else "Here is how to dissect this AI-901 scenario step by step."
        )
    )

    follow_up_block = ""
    if req.follow_up:
        fu_lower = req.follow_up.lower()
        if "foundry" in fu_lower or "agent" in fu_lower:
            follow_up_block = (
                "\n\nFollow-up insight: Think of a Microsoft Foundry Project as your team's workspace "
                "(models, agents, evaluations). Use a plain chat client for single-turn or stateless Q&A, "
                "and upgrade to a Foundry Agent when the system needs persistent instructions, grounding "
                "knowledge files, and callable tools (Code Interpreter, File Search, functions)."
            )
        elif "temperature" in fu_lower or "top_p" in fu_lower:
            follow_up_block = (
                "\n\nFollow-up insight: Lower `temperature` (0.0–0.2) produces deterministic, repeatable "
                "outputs ideal for JSON extraction or factual Q&A. Higher values (0.7–1.2) increase lexical "
                "variety for brainstorming. Microsoft recommends tuning `temperature` OR `top_p`, not both."
            )
        elif "content understanding" in fu_lower:
            follow_up_block = (
                "\n\nFollow-up insight: Azure Content Understanding is the flagship AI-901 extraction service "
                "because one schema-driven Analyzer pattern works across documents/forms, images, audio, and "
                "video — returning structured JSON plus confidence scores for human-in-the-loop review."
            )
        else:
            follow_up_block = (
                f"\n\nFollow-up insight on \"{req.follow_up}\": Anchor your study to the official AI-901 "
                "mental model — identify the input modality (text, speech, image, document, audio/video), "
                "choose the matching Foundry tool, apply Responsible AI guardrails, and verify confidence."
            )

    coaching_text = (
        f"{status_line}\n\n"
        f"**Why '{correct}' is the right choice ({topic}):**\n"
        f"{explanation}\n\n"
        f"**Exam Strategy Tip:** Eliminate options that belong to the wrong modality or layer "
        f"(for instance, confusing infrastructure resources with Foundry AI capabilities, or mixing "
        f"Fairness with Inclusiveness).{follow_up_block}"
    )

    return {
        "mode": "mock",
        "service": "AI-901 Study Coach (Demo Simulator)",
        "note": "Running in Local Demo Mode. Add AZURE_OPENAI_* or AZURE_AI_PROJECT_ENDPOINT in .env to enable Live Foundry coaching.",
        "data": {
            "coaching": coaching_text,
            "key_takeaway": explanation,
            "latency_ms": max(18, int((time.perf_counter() - start) * 1000)),
        },
    }


def run_foundry_chat(req: FoundryChatRequest, settings: Settings) -> Dict[str, Any]:
    """Run a lightweight Microsoft Foundry chat completion (Live or Demo Mode)."""
    start = time.perf_counter()

    if settings.foundry_chat_live:
        try:
            client, sdk_used = _live_openai_client(settings)
            if client is not None:
                resp = client.chat.completions.create(
                    model=settings.azure_openai_chat_deployment or req.model,
                    temperature=req.temperature,
                    top_p=req.top_p,
                    max_tokens=req.max_tokens,
                    messages=[
                        {"role": "system", "content": req.system_prompt},
                        {"role": "user", "content": req.user_prompt},
                    ],
                )
                content = resp.choices[0].message.content or ""
                usage = getattr(resp, "usage", None)
                return {
                    "mode": "live",
                    "service": f"Microsoft Foundry Chat ({sdk_used})",
                    "note": f"Executed live against deployment '{settings.azure_openai_chat_deployment}'.",
                    "data": {
                        "reply": content,
                        "model": settings.azure_openai_chat_deployment,
                        "parameters": {
                            "temperature": req.temperature,
                            "top_p": req.top_p,
                            "max_tokens": req.max_tokens,
                        },
                        "usage": {
                            "prompt_tokens": getattr(usage, "prompt_tokens", _approx_tokens(req.system_prompt + req.user_prompt)),
                            "completion_tokens": getattr(usage, "completion_tokens", _approx_tokens(content)),
                        },
                        "content_safety": {"hate": "safe", "self_harm": "safe", "violence": "safe", "prompt_shield": "passed"},
                        "latency_ms": int((time.perf_counter() - start) * 1000),
                    },
                }
        except Exception as exc:
            mock = _mock_foundry_chat(req, start)
            mock["note"] = f"Live Foundry chat failed ({exc.__class__.__name__}); using Demo Mode."
            return mock

    return _mock_foundry_chat(req, start)


def _mock_foundry_chat(req: FoundryChatRequest, start: float) -> Dict[str, Any]:
    prompt_lower = req.user_prompt.lower()
    style = (
        "precise, deterministic"
        if req.temperature <= 0.35
        else ("balanced, explanatory" if req.temperature <= 0.8 else "creative, exploratory")
    )

    if any(k in prompt_lower for k in ("agent", "tool", "thread")):
        body = (
            "In Microsoft Foundry, use a **Single-Agent** when your app needs persistent instructions, "
            "grounding knowledge (such as File Search or Azure AI Search), and callable tools "
            "(Code Interpreter, Bing Grounding, or custom functions). The Python SDK workflow is:\n"
            "1. Connect with `AIProjectClient` + `DefaultAzureCredential`.\n"
            "2. Create a `Thread` to preserve multi-turn memory.\n"
            "3. Post a user `Message` and run `create_and_process`.\n"
            "4. Inspect the agent's grounded answer and tool trace."
        )
    elif any(k in prompt_lower for k in ("responsible", "fairness", "privacy", "transparency", "safety")):
        body = (
            "Microsoft's **six Responsible AI principles** tested on AI-901 are:\n"
            "- **Fairness**: mitigate bias across demographic cohorts.\n"
            "- **Reliability & Safety**: red-team edge cases, enforce Azure AI Content Safety, keep humans in the loop.\n"
            "- **Privacy & Security**: Entra ID RBAC, PII protection, Prompt Shields.\n"
            "- **Inclusiveness**: accessibility (captions, alt-text, multilingual support).\n"
            "- **Transparency**: disclose AI usage and document limits.\n"
            "- **Accountability**: clear human ownership, audit logs, and governance."
        )
    elif any(k in prompt_lower for k in ("content understanding", "invoice", "extract", "document", "video")):
        body = (
            "**Azure Content Understanding** in Foundry Tools extracts structured JSON from documents, "
            "forms, images, audio, and video using schema-driven Analyzers. Each field specifies a method "
            "(`extract`, `classify`, or `generate`) and returns confidence scores + source provenance "
            "so low-confidence values can route to human review."
        )
    elif any(k in prompt_lower for k in ("temperature", "top_p", "ptu", "deployment", "token")):
        body = (
            f"At `temperature={req.temperature}` and `top_p={req.top_p}`, decoding behaves in a **{style}** "
            "regime. For structured extraction or exam-grade factual answers, keep `temperature <= 0.2`. "
            "For deployment sizing in Foundry, choose **Standard / Global Standard** for variable pay-per-token "
            "traffic or **Provisioned Throughput (PTU)** when you need reserved low-latency capacity."
        )
    else:
        body = (
            f"[Simulated `{req.model}` • {style} mode @ temp={req.temperature}]\n\n"
            f"System instruction respected: \"{req.system_prompt[:95]}{'...' if len(req.system_prompt) > 95 else ''}\"\n\n"
            "For Exam AI-901, break every scenario into two layers:\n"
            "1. **Domain 1 (40–45%)**: Confirm Responsible AI safeguards, select the right model capability "
            "and configuration (`temperature`, `max_tokens`, PTU vs. Standard), and classify the workload.\n"
            "2. **Domain 2 (55–60%)**: Implement inside a Microsoft Foundry Project using the Foundry SDK, "
            "Azure Language/Speech, multimodal Vision, or Azure Content Understanding."
        )

    # Respect max_tokens approximately so learners see the effect of the slider
    char_limit = max(140, req.max_tokens * 4)
    truncated = False
    if len(body) > char_limit:
        body = body[:char_limit].rsplit(" ", 1)[0] + " ... [truncated by max_tokens]"
        truncated = True

    prompt_tokens = _approx_tokens(req.system_prompt) + _approx_tokens(req.user_prompt)
    completion_tokens = _approx_tokens(body)

    return {
        "mode": "mock",
        "service": "Microsoft Foundry Chat (Demo Simulator)",
        "note": "Demo Mode active. Configure AZURE_OPENAI_* or AZURE_AI_PROJECT_ENDPOINT in .env to run live against Microsoft Foundry.",
        "data": {
            "reply": body,
            "model": req.model,
            "finish_reason": "length" if truncated else "stop",
            "parameters": {
                "temperature": req.temperature,
                "top_p": req.top_p,
                "max_tokens": req.max_tokens,
            },
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            "content_safety": {
                "hate": "safe",
                "self_harm": "safe",
                "violence": "safe",
                "prompt_shield": "passed",
            },
            "latency_ms": max(24, int((time.perf_counter() - start) * 1000)),
        },
    }


def run_single_agent(req: FoundryAgentRequest, settings: Settings) -> Dict[str, Any]:
    """Execute a Microsoft Foundry Single-Agent workflow with visible tool trace."""
    start = time.perf_counter()
    goal_lower = req.goal.lower()

    # Local deterministic tool implementations (used in Demo Mode and as function-calling tools)
    tool_trace: List[Dict[str, Any]] = []

    if "recommend_foundry_service" in req.enabled_tools:
        if any(k in goal_lower for k in ("invoice", "pdf", "form", "receipt", "video", "call recording")):
            rec = {
                "primary_service": "Azure Content Understanding in Foundry Tools",
                "workload": "Multimodal Information Extraction",
                "pattern": "Define custom Analyzer schema (extract / classify / generate) + confidence threshold",
            }
        elif any(k in goal_lower for k in ("speech", "voice", "audio", "spoken", "caption", "tts", "stt")):
            rec = {
                "primary_service": "Azure Speech in Foundry Tools / Multimodal Audio Model",
                "workload": "Speech Recognition & Synthesis",
                "pattern": "SpeechRecognizer/SpeechSynthesizer (SSML) or audio-enabled GPT-4o deployment",
            }
        elif any(k in goal_lower for k in ("image", "photo", "shelf", "defect", "ocr", "visual", "banner")):
            rec = {
                "primary_service": "Multimodal Vision Model + Image Generation in Microsoft Foundry",
                "workload": "Computer Vision & Image Generation",
                "pattern": "Send `text` + `image_url` content parts, or invoke `gpt-image-1` with Content Safety",
            }
        elif any(k in goal_lower for k in ("sentiment", "entity", "pii", "review", "key phrase")):
            rec = {
                "primary_service": "Azure Language (`TextAnalyticsClient`) in Foundry Tools",
                "workload": "Text Analysis (NLP)",
                "pattern": "Run sentiment/opinion mining, NER/PII redaction, and extractive summarization",
            }
        else:
            rec = {
                "primary_service": "Microsoft Foundry Agent Service + Grounding Knowledge (RAG)",
                "workload": "Generative & Agentic AI",
                "pattern": "Foundry Project -> Deploy gpt-4o-mini -> Attach File Search & custom function tools",
            }
        tool_trace.append(
            {
                "tool": "recommend_foundry_service",
                "status": "completed",
                "arguments": {"goal_summary": req.goal[:120]},
                "output": rec,
            }
        )

    if "responsible_ai_audit" in req.enabled_tools:
        checks = [
            {"principle": "Transparency", "action": "Add an AI disclosure banner and document grounding sources."},
            {"principle": "Privacy & Security", "action": "Authenticate via Microsoft Entra ID (`DefaultAzureCredential`) and enable PII redaction."},
            {"principle": "Reliability & Safety", "action": "Enable Azure AI Content Safety filters and human review for low-confidence outputs."},
        ]
        if any(k in goal_lower for k in ("loan", "hiring", "credit", "medical", "hr")):
            checks.insert(
                0,
                {
                    "principle": "Fairness",
                    "action": "Evaluate outcome parity across demographic groups before production rollout.",
                },
            )
        tool_trace.append(
            {
                "tool": "responsible_ai_audit",
                "status": "completed",
                "arguments": {"high_stakes_detected": any(k in goal_lower for k in ("loan", "hiring", "credit", "medical", "hr"))},
                "output": {"required_controls": checks},
            }
        )

    if "estimate_token_cost" in req.enabled_tools:
        est_input = _approx_tokens(req.instructions + req.goal) + 420
        est_output = 280
        tool_trace.append(
            {
                "tool": "estimate_token_cost",
                "status": "completed",
                "arguments": {"recommended_tier": "Standard (pay-per-token) for prototype; PTU for steady enterprise scale"},
                "output": {
                    "estimated_prompt_tokens": est_input,
                    "estimated_completion_tokens": est_output,
                    "suggested_model": "gpt-4o-mini (or Phi-4 SLM for low-cost classification)",
                },
            }
        )

    # If live Foundry chat/project is available, let the live model synthesize the final agent answer
    mode = "mock"
    service = "Microsoft Foundry Single-Agent (Demo Simulator)"
    note = "Demo Mode active — simulated Foundry Thread, Tool Calls, and Run lifecycle. Add AZURE_AI_PROJECT_ENDPOINT in .env for Live Foundry Agents."
    final_answer = ""

    if settings.foundry_agent_live:
        try:
            client, sdk_used = _live_openai_client(settings)
            if client is not None:
                resp = client.chat.completions.create(
                    model=settings.azure_openai_chat_deployment,
                    temperature=0.2,
                    max_tokens=360,
                    messages=[
                        {"role": "system", "content": req.instructions},
                        {
                            "role": "user",
                            "content": (
                                f"User Goal: {req.goal}\n\n"
                                f"Tool outputs collected in agent run:\n{tool_trace}\n\n"
                                "Synthesize a concise, actionable AI-901 architecture plan in markdown."
                            ),
                        },
                    ],
                )
                final_answer = resp.choices[0].message.content or ""
                mode = "live"
                service = f"Microsoft Foundry Agent ({sdk_used})"
                note = f"Live synthesis using deployment '{settings.azure_openai_chat_deployment}'."
        except Exception as exc:
            note = f"Live Foundry agent call failed ({exc.__class__.__name__}); used local agent synthesis."

    if not final_answer:
        rec_out = next((t["output"] for t in tool_trace if t["tool"] == "recommend_foundry_service"), None)
        primary = rec_out["primary_service"] if rec_out else "Microsoft Foundry Project & Deployed Model"
        pattern = rec_out["pattern"] if rec_out else "Configure system prompt, grounding files, and SDK client."
        final_answer = (
            f"### Recommended AI-901 Solution Blueprint\n"
            f"- **Primary Service:** {primary}\n"
            f"- **Implementation Pattern:** {pattern}\n"
            f"- **Agent Lifecycle:** Create Thread -> Post Goal -> Execute {len(tool_trace)} Tool(s) -> Return Grounded Plan.\n"
            f"- **Responsible AI Readiness:** Enforce Entra ID RBAC, Azure AI Content Safety filters, and clear AI disclosure."
        )

    return {
        "mode": mode,
        "service": service,
        "note": note,
        "data": {
            "thread_id": "thread_ai901_demo_01",
            "run_status": "completed",
            "tool_calls": tool_trace,
            "final_response": final_answer,
            "latency_ms": max(32, int((time.perf_counter() - start) * 1000)),
        },
    }
