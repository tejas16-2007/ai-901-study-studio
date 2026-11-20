"""Dual-mode Azure Content Understanding & Multimodal Vision service adapter."""

from __future__ import annotations

import re
import time
from typing import Any, Dict, List

from backend.config import Settings
from backend.models import ContentExtractionRequest, VisionLabRequest


def extract_content(req: ContentExtractionRequest, settings: Settings) -> Dict[str, Any]:
    """Extract schema-typed structured fields across document, image, audio, or video."""
    start = time.perf_counter()

    # Note: Live Azure Content Understanding requires a reachable media URL or binary upload.
    # When live credentials are configured AND the input starts with https://, call the REST API.
    if settings.content_understanding_live and req.content.strip().startswith(("http://", "https://")):
        try:
            import httpx  # type: ignore

            analyzer_map = {
                "document": "prebuilt-documentAnalyzer",
                "image": "prebuilt-imageAnalyzer",
                "audio": "prebuilt-callCenter",
                "video": "prebuilt-videoAnalyzer",
            }
            analyzer_id = analyzer_map.get(req.modality, "prebuilt-documentAnalyzer")
            endpoint = settings.azure_content_understanding_endpoint.rstrip("/")
            url = (
                f"{endpoint}/contentunderstanding/analyzers/{analyzer_id}:analyze"
                f"?api-version={settings.azure_content_understanding_api_version}"
            )
            headers = {
                "Ocp-Apim-Subscription-Key": settings.azure_content_understanding_key,
                "Content-Type": "application/json",
            }
            resp = httpx.post(url, headers=headers, json={"url": req.content.strip()}, timeout=20.0)
            resp.raise_for_status()
            return {
                "mode": "live",
                "service": f"Azure Content Understanding ({analyzer_id})",
                "note": "Submitted live to Azure Content Understanding REST endpoint.",
                "data": {
                    "analyzer_id": analyzer_id,
                    "modality": req.modality,
                    "operation_location": resp.headers.get("Operation-Location", ""),
                    "status": "Running",
                    "latency_ms": int((time.perf_counter() - start) * 1000),
                },
            }
        except Exception as exc:
            mock = _mock_content_extraction(req, start)
            mock["note"] = (
                f"Live Content Understanding call failed ({exc.__class__.__name__}); using Demo Mode."
            )
            return mock

    return _mock_content_extraction(req, start)


def _mock_content_extraction(req: ContentExtractionRequest, start: float) -> Dict[str, Any]:
    text = req.content.strip()
    fields: Dict[str, Dict[str, Any]] = {}

    if req.modality == "document":
        vendor = re.search(r"Vendor:\s*(.+)", text, re.IGNORECASE)
        inv_num = re.search(r"(INV-[0-9-]+|#[A-Z0-9-]+)", text, re.IGNORECASE)
        date_m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        total = re.search(r"Total(?:\s+Due)?:\s*(\$[0-9,]+\.\d{2})", text, re.IGNORECASE)
        terms = re.search(r"Terms:\s*([^|\n]+)", text, re.IGNORECASE)
        fields = {
            "VendorName": {
                "method": "extract",
                "value": vendor.group(1).strip() if vendor else "Fabrikam Cloud Components Ltd.",
                "confidence": 0.98,
                "grounding": "page 1, line 2",
            },
            "InvoiceNumber": {
                "method": "extract",
                "value": inv_num.group(1).lstrip("#") if inv_num else "INV-2026-0001",
                "confidence": 0.99,
                "grounding": "page 1, header",
            },
            "InvoiceDate": {
                "method": "extract",
                "value": date_m.group(1) if date_m else "2026-11-12",
                "confidence": 0.97,
                "grounding": "page 1, line 3",
            },
            "TotalAmount": {
                "method": "extract",
                "value": total.group(1) if total else "$1,585.44",
                "confidence": 0.96,
                "grounding": "page 1, totals block",
            },
            "PaymentTerms": {
                "method": "extract",
                "value": terms.group(1).strip() if terms else "Net 30",
                "confidence": 0.91,
                "grounding": "page 1, footer",
            },
            "Category": {
                "method": "classify",
                "value": "Hardware & IoT Equipment",
                "confidence": 0.89,
                "grounding": "derived from line items",
            },
        }
    elif req.modality == "image":
        sku = re.search(r"SKU:\s*([A-Z0-9-]+)", text, re.IGNORECASE)
        price = re.search(r"(\$[0-9,]+\.\d{2})", text)
        has_dent = "dent" in text.lower() or "damage" in text.lower()
        fields = {
            "ProductName": {
                "method": "extract",
                "value": "Alpine Smart Thermostat Pro",
                "confidence": 0.95,
                "grounding": "bbox [120, 84, 540, 410]",
            },
            "SKU": {
                "method": "extract",
                "value": sku.group(1) if sku else "ALP-9042",
                "confidence": 0.97,
                "grounding": "bbox [180, 420, 340, 460]",
            },
            "PriceTag": {
                "method": "extract",
                "value": price.group(1) if price else "$189.99",
                "confidence": 0.96,
                "grounding": "bbox [90, 470, 230, 520]",
            },
            "Condition": {
                "method": "classify",
                "value": "Minor Packaging Damage" if has_dent else "Good",
                "confidence": 0.78 if has_dent else 0.93,
                "grounding": "bbox [410, 110, 520, 210]",
            },
            "ShelfStockLevel": {
                "method": "generate",
                "value": "Low (2 units visible — recommend restock alert)",
                "confidence": 0.88,
                "grounding": "full frame analysis",
            },
        }
    elif req.modality == "audio":
        order = re.search(r"(ORD-[0-9]+)", text, re.IGNORECASE)
        fields = {
            "CallerIntent": {
                "method": "classify",
                "value": "Missing Accessory / Replacement Request",
                "confidence": 0.96,
                "grounding": "00:06–00:16 (Speaker 2)",
            },
            "Sentiment": {
                "method": "classify",
                "value": "Frustrated -> Resolved Positive",
                "confidence": 0.93,
                "grounding": "00:06 vs 00:34",
            },
            "OrderReference": {
                "method": "extract",
                "value": order.group(1) if order else "ORD-77319",
                "confidence": 0.99,
                "grounding": "00:08 (Speaker 2)",
            },
            "ActionItems": {
                "method": "generate",
                "value": "Dispatch overnight replacement power adapter; apply $25 account credit.",
                "confidence": 0.94,
                "grounding": "00:18–00:30 (Speaker 1)",
            },
            "EscalationRequired": {
                "method": "classify",
                "value": "No — resolved on first call",
                "confidence": 0.92,
                "grounding": "00:34 (Speaker 2)",
            },
        }
    else:  # video
        fields = {
            "Title": {
                "method": "generate",
                "value": "Microsoft Foundry AI-901 End-to-End Walkthrough",
                "confidence": 0.95,
                "grounding": "00:00–00:45",
            },
            "Chapters": {
                "method": "extract",
                "value": [
                    "00:00–00:45 Foundry Project Setup",
                    "00:45–02:10 Deploying gpt-4o-mini & System Prompts",
                    "02:10–03:30 Single-Agent File Search Demo",
                    "03:30–04:15 Content Safety & Transparency Review",
                ],
                "confidence": 0.94,
                "grounding": "4 key-frame segments",
            },
            "KeyTopics": {
                "method": "extract",
                "value": ["Microsoft Foundry", "gpt-4o-mini", "Single-Agent", "File Search", "Responsible AI"],
                "confidence": 0.96,
                "grounding": "transcript + slide OCR",
            },
            "TargetAudience": {
                "method": "classify",
                "value": "AI-901 Fundamentals Learners & Junior Developers",
                "confidence": 0.91,
                "grounding": "narration tone & UI steps",
            },
            "Summary": {
                "method": "generate",
                "value": "Demonstrates creating a Foundry project, tuning a chat deployment at low temperature, adding File Search to an agent, and reviewing Content Safety guardrails.",
                "confidence": 0.93,
                "grounding": "full timeline 00:00–04:15",
            },
        }

    # Filter if user requested specific custom fields (keep defaults if none matched)
    if req.schema_fields:
        filtered = {k: v for k, v in fields.items() if k in req.schema_fields}
        if filtered:
            fields = filtered

    low_conf_fields = [k for k, v in fields.items() if float(v["confidence"]) < 0.85]

    return {
        "mode": "mock",
        "service": f"Azure Content Understanding — {req.modality.title()} Analyzer (Demo Simulator)",
        "note": "Demo Mode active. Configure AZURE_CONTENT_UNDERSTANDING_ENDPOINT & KEY in .env to invoke live analyzers.",
        "data": {
            "analyzer_id": f"ai901-{req.modality}-analyzer",
            "modality": req.modality,
            "status": "Succeeded",
            "fields": fields,
            "human_review_recommended": len(low_conf_fields) > 0,
            "low_confidence_fields": low_conf_fields,
            "latency_ms": max(28, int((time.perf_counter() - start) * 1000)),
        },
    }


def run_vision_lab(req: VisionLabRequest, settings: Settings) -> Dict[str, Any]:
    """Demonstrate Multimodal Vision analysis & Image Generation prompts (Live or Demo)."""
    start = time.perf_counter()

    presets: Dict[str, Dict[str, Any]] = {
        "retail_shelf": {
            "scene": "Warehouse & Retail Shelf Photo (1280x720)",
            "detections": [
                {"label": "Thermostat Box", "confidence": 0.96, "bbox": [118, 92, 310, 398]},
                {"label": "Empty Shelf Slot", "confidence": 0.92, "bbox": [332, 110, 610, 398]},
                {"label": "Price Label ($189.99)", "confidence": 0.95, "bbox": [125, 412, 278, 456]},
            ],
            "analysis": (
                "Visual inspection identified 2 remaining thermostat units on the left, 1 out-of-stock "
                "gap occupying the middle shelf bay (~35% width), and a clear OCR-readable shelf price tag "
                "of $189.99. Recommended action: trigger restock task for SKU ALP-9042."
            ),
        },
        "whiteboard_arch": {
            "scene": "Engineering Architecture Whiteboard (1920x1080)",
            "detections": [
                {"label": "Box: User Web App", "confidence": 0.97, "bbox": [60, 180, 260, 310]},
                {"label": "Box: Foundry Project", "confidence": 0.96, "bbox": [380, 140, 740, 420]},
                {"label": "Box: Azure AI Search (RAG)", "confidence": 0.94, "bbox": [820, 210, 1080, 350]},
            ],
            "analysis": (
                "Handwritten diagram depicts a client web app authenticating via Microsoft Entra ID into "
                "a Microsoft Foundry Project. Inside Foundry, a Single Agent connects to Azure AI Search "
                "for grounded policy documents and Azure Content Understanding for uploaded PDF invoices."
            ),
        },
        "safety_floor": {
            "scene": "Manufacturing Floor Camera Frame (1280x720)",
            "detections": [
                {"label": "Worker — Hard Hat & Vest", "confidence": 0.98, "bbox": [210, 140, 360, 560]},
                {"label": "Worker — Missing High-Vis Vest", "confidence": 0.89, "bbox": [620, 155, 765, 550]},
                {"label": "Clear Yellow Walkway", "confidence": 0.94, "bbox": [80, 570, 1190, 700]},
            ],
            "analysis": (
                "Detected two personnel in Zone B. Worker 1 meets PPE compliance (hard hat + high-vis vest). "
                "Worker 2 appears to be missing a high-visibility vest (confidence 0.89). Per Responsible AI "
                "Reliability & Safety, flag for supervisor verification rather than automated disciplinary action."
            ),
        },
    }

    if req.task == "generate":
        refined = (
            f"Editorial technical illustration of {req.prompt.strip()}, crisp isometric geometry, "
            "soft studio daylight, clean azure and slate color accents, high legibility, no watermark text."
        )
        return {
            "mode": "mock",
            "service": "Microsoft Foundry Image Generation (Demo Simulator)",
            "note": (
                "Demo Mode active — returns engineered prompt, safety check, and Foundry SDK payload. "
                "Configure AZURE_OPENAI_ENDPOINT + image deployment in .env for Live generation."
            ),
            "data": {
                "task": "generate",
                "original_prompt": req.prompt,
                "enhanced_prompt": refined,
                "model": "gpt-image-1",
                "size": "1024x1024",
                "content_safety": {
                    "prompt_filter": "passed",
                    "transparency_note": "Attach C2PA Content Credentials / disclose AI-generated asset.",
                },
                "latency_ms": max(26, int((time.perf_counter() - start) * 1000)),
            },
        }

    preset = presets.get(req.scene_preset or "retail_shelf", presets["retail_shelf"])
    return {
        "mode": "mock",
        "service": "Microsoft Foundry Multimodal Vision (Demo Simulator)",
        "note": "Demo Mode active. Configure AZURE_OPENAI_ENDPOINT & VISION deployment in .env for Live visual reasoning.",
        "data": {
            "task": "analyze",
            "scene": preset["scene"],
            "prompt": req.prompt,
            "analysis": preset["analysis"],
            "detections": preset["detections"],
            "payload_shape": [
                {"type": "text", "text": req.prompt},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,<encoded_frame>"}},
            ],
            "latency_ms": max(22, int((time.perf_counter() - start) * 1000)),
        },
    }
