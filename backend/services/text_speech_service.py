"""Dual-mode Azure Language (Text Analysis) & Azure Speech service adapter."""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List
from xml.sax.saxutils import escape as xml_escape

from backend.config import Settings
from backend.models import SpeechSimulationRequest, TextAnalysisRequest

POSITIVE_WORDS = {
    "love", "loves", "great", "accurate", "accuracy", "fast", "relief", "thank",
    "unified", "cut", "improved", "seamless", "helpful", "excellent", "reliable",
    "smooth", "success", "resolved", "quickly", "clear", "strong",
}
NEGATIVE_WORDS = {
    "failed", "struggled", "delayed", "longer", "slow", "missing", "faded",
    "broken", "issue", "problem", "error", "frustrated", "bad", "poor", "damp",
    "damaged", "sorry", "outage", "crash", "risk",
}
STOPWORDS = {
    "the", "and", "for", "that", "with", "this", "from", "our", "your", "have",
    "has", "was", "were", "are", "been", "being", "into", "over", "after", "about",
    "than", "then", "also", "very", "just", "more", "some", "such", "their", "they",
    "them", "when", "where", "which", "while", "will", "would", "could", "should",
    "there", "here", "however", "within", "under", "through", "between", "onto",
}


def analyze_text(req: TextAnalysisRequest, settings: Settings) -> Dict[str, Any]:
    """Run sentiment, key phrases, NER/PII, and extractive summary (Live or Demo)."""
    start = time.perf_counter()

    if settings.text_analytics_live:
        try:
            from azure.ai.textanalytics import TextAnalyticsClient  # type: ignore
            from azure.core.credentials import AzureKeyCredential  # type: ignore

            client = TextAnalyticsClient(
                endpoint=settings.azure_language_endpoint,
                credential=AzureKeyCredential(settings.azure_language_key),
            )
            docs = [req.text]
            data: Dict[str, Any] = {}

            if "sentiment" in req.tasks:
                res = client.analyze_sentiment(docs)[0]
                data["sentiment"] = {
                    "overall": res.sentiment,
                    "scores": {
                        "positive": round(res.confidence_scores.positive, 2),
                        "neutral": round(res.confidence_scores.neutral, 2),
                        "negative": round(res.confidence_scores.negative, 2),
                    },
                }
            if "key_phrases" in req.tasks:
                kp = client.extract_key_phrases(docs)[0]
                data["key_phrases"] = list(kp.key_phrases)
            if "entities" in req.tasks:
                ents = client.recognize_entities(docs)[0]
                data["entities"] = [
                    {
                        "text": e.text,
                        "category": e.category,
                        "confidence": round(e.confidence_score, 2),
                    }
                    for e in ents.entities
                ]
                pii = client.recognize_pii_entities(docs)[0]
                data["pii_redacted_text"] = pii.redacted_text
            if "summary" in req.tasks:
                data["extractive_summary"] = _extractive_summary(req.text)

            data["latency_ms"] = int((time.perf_counter() - start) * 1000)
            return {
                "mode": "live",
                "service": "Azure Language (`TextAnalyticsClient`)",
                "note": "Executed live against AZURE_LANGUAGE_ENDPOINT.",
                "data": data,
            }
        except Exception as exc:
            mock = _mock_analyze_text(req, start)
            mock["note"] = f"Live Azure Language call failed ({exc.__class__.__name__}); using Demo Mode."
            return mock

    return _mock_analyze_text(req, start)


def _extractive_summary(text: str) -> str:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    if len(sentences) <= 2:
        return text.strip()
    return f"{sentences[0]} {sentences[-1]}"


def _mock_analyze_text(req: TextAnalysisRequest, start: float) -> Dict[str, Any]:
    text = req.text.strip()
    words = re.findall(r"[A-Za-z][A-Za-z0-9'-]+", text)
    lower_words = [w.lower() for w in words]

    pos_hits = sum(1 for w in lower_words if w in POSITIVE_WORDS)
    neg_hits = sum(1 for w in lower_words if w in NEGATIVE_WORDS)
    total_hits = pos_hits + neg_hits

    if total_hits == 0:
        overall = "neutral"
        scores = {"positive": 0.14, "neutral": 0.78, "negative": 0.08}
    elif pos_hits > 0 and neg_hits > 0 and abs(pos_hits - neg_hits) <= 1:
        overall = "mixed"
        scores = {"positive": 0.46, "neutral": 0.12, "negative": 0.42}
    elif pos_hits > neg_hits:
        overall = "positive"
        p = min(0.92, round(0.55 + 0.1 * pos_hits, 2))
        n = round(max(0.03, (1 - p) * 0.35), 2)
        scores = {"positive": p, "neutral": round(1 - p - n, 2), "negative": n}
    else:
        overall = "negative"
        n = min(0.91, round(0.55 + 0.1 * neg_hits, 2))
        p = round(max(0.03, (1 - n) * 0.3), 2)
        scores = {"positive": p, "neutral": round(1 - p - n, 2), "negative": n}

    # Key phrases (capitalized multi-word phrases + salient domain terms)
    candidates: List[str] = []
    for match in re.findall(r"\b(?:[A-Z][a-zA-Z0-9-]+(?:\s+[A-Z][a-zA-Z0-9-]+)+)\b", text):
        if match not in candidates:
            candidates.append(match)
    freq: Dict[str, int] = {}
    for w in lower_words:
        if len(w) >= 5 and w not in STOPWORDS:
            freq[w] = freq.get(w, 0) + 1
    for term, _ in sorted(freq.items(), key=lambda item: (-item[1], -len(item[0]))):
        if len(candidates) >= 8:
            break
        if all(term not in c.lower() for c in candidates):
            candidates.append(term)

    # Entities & PII
    entities: List[Dict[str, Any]] = []
    redacted = text
    for email in re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", text):
        entities.append({"text": email, "category": "Email (PII)", "confidence": 0.99})
        redacted = redacted.replace(email, "********")
    for date_match in re.findall(
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}\b|\b\d{4}-\d{2}-\d{2}\b",
        text,
    ):
        entities.append({"text": date_match, "category": "DateTime", "confidence": 0.96})
    for pct in re.findall(r"\b\d+(?:\.\d+)?%\b", text):
        entities.append({"text": pct, "category": "Quantity", "confidence": 0.95})
    for org_or_loc in re.findall(r"\b(?:Microsoft Foundry|Contoso Retail|Northwind Logistics|Seattle|Chicago|Redmond|Elena Morales)\b", text):
        cat = (
            "Location"
            if org_or_loc in {"Seattle", "Chicago", "Redmond"}
            else ("Person (PII)" if org_or_loc == "Elena Morales" else "Organization")
        )
        if not any(e["text"] == org_or_loc for e in entities):
            entities.append({"text": org_or_loc, "category": cat, "confidence": 0.94})
        if cat == "Person (PII)":
            redacted = redacted.replace(org_or_loc, "***** *******")

    data: Dict[str, Any] = {}
    if "sentiment" in req.tasks:
        data["sentiment"] = {"overall": overall, "scores": scores}
    if "key_phrases" in req.tasks:
        data["key_phrases"] = candidates[:8]
    if "entities" in req.tasks:
        data["entities"] = entities
        data["pii_redacted_text"] = redacted
    if "summary" in req.tasks:
        data["extractive_summary"] = _extractive_summary(text)
    data["latency_ms"] = max(14, int((time.perf_counter() - start) * 1000))

    return {
        "mode": "mock",
        "service": "Azure Language Text Analysis (Demo Simulator)",
        "note": "Demo Mode active. Set AZURE_LANGUAGE_ENDPOINT and AZURE_LANGUAGE_KEY in .env for Live Azure Language.",
        "data": data,
    }


def run_speech_lab(req: SpeechSimulationRequest, settings: Settings) -> Dict[str, Any]:
    """Generate SSML + Azure Speech TTS/STT diagnostics (Live or Demo Mode)."""
    start = time.perf_counter()
    safe_text = xml_escape(req.text.strip())
    ssml = (
        f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{req.language}">\n'
        f'  <voice name="{req.voice}">\n'
        f'    <prosody rate="0%" pitch="0%">{safe_text}</prosody>\n'
        f"  </voice>\n"
        f"</speak>"
    )

    word_count = len(req.text.split())
    est_duration_sec = round(max(1.2, word_count / 2.6), 1)

    if settings.speech_live and req.direction == "tts":
        try:
            import azure.cognitiveservices.speech as speechsdk  # type: ignore

            cfg = speechsdk.SpeechConfig(
                subscription=settings.azure_speech_key,
                region=settings.azure_speech_region,
            )
            cfg.speech_synthesis_voice_name = req.voice
            synth = speechsdk.SpeechSynthesizer(speech_config=cfg, audio_config=None)
            res = synth.speak_ssml_async(ssml).get()
            audio_bytes = len(res.audio_data) if res and res.audio_data else 0
            return {
                "mode": "live",
                "service": "Azure Speech in Foundry Tools (`SpeechSynthesizer`)",
                "note": f"Synthesized live in Azure region '{settings.azure_speech_region}' ({audio_bytes} bytes).",
                "data": {
                    "direction": req.direction,
                    "voice": req.voice,
                    "language": req.language,
                    "ssml": ssml,
                    "estimated_duration_sec": est_duration_sec,
                    "audio_bytes": audio_bytes,
                    "latency_ms": int((time.perf_counter() - start) * 1000),
                },
            }
        except Exception as exc:
            pass

    return {
        "mode": "mock",
        "service": "Azure Speech in Foundry Tools (Demo Simulator)",
        "note": (
            "Demo Mode active (browser Web Speech API can also preview audio). "
            "Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in .env for Live Azure Neural Speech."
        ),
        "data": {
            "direction": req.direction,
            "voice": req.voice,
            "language": req.language,
            "ssml": ssml,
            "transcript": req.text.strip(),
            "recognition_confidence": 0.97 if req.direction == "stt" else None,
            "estimated_duration_sec": est_duration_sec,
            "latency_ms": max(15, int((time.perf_counter() - start) * 1000)),
        },
    }
