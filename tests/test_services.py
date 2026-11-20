"""Unit tests for AI-901 curriculum integrity, dual-mode config, and Foundry lab services."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from backend.config import Settings
from backend.data.curriculum import EXAM_METADATA, EXAM_QUESTIONS, FLASHCARDS, STUDY_MODULES
from backend.main import curriculum, health, status
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


class TestCurriculumBlueprint(unittest.TestCase):
    def test_domains_and_modules(self):
        self.assertEqual(EXAM_METADATA["code"], "AI-901")
        self.assertEqual(EXAM_METADATA["passing_score"], 700)
        self.assertEqual(len(STUDY_MODULES), 7)
        d1_mods = [m for m in STUDY_MODULES if m["domain_id"] == "domain-1"]
        d2_mods = [m for m in STUDY_MODULES if m["domain_id"] == "domain-2"]
        self.assertEqual(len(d1_mods), 3)
        self.assertEqual(len(d2_mods), 4)
        # All Domain 2 modules should include a Python Foundry SDK code snippet
        for mod in d2_mods:
            self.assertIsNotNone(mod["code_snippet"])
            self.assertTrue(mod["code_snippet"]["code"].strip())

    def test_flashcards_integrity(self):
        self.assertGreaterEqual(len(FLASHCARDS), 30)
        ids = [c["id"] for c in FLASHCARDS]
        self.assertEqual(len(ids), len(set(ids)))
        for card in FLASHCARDS:
            self.assertTrue(card["front"].strip())
            self.assertTrue(card["back"].strip())

    def test_exam_questions_match_ai901_weights(self):
        self.assertEqual(len(EXAM_QUESTIONS), 30)
        ids = [q["id"] for q in EXAM_QUESTIONS]
        self.assertEqual(len(ids), len(set(ids)))

        d1_count = sum(1 for q in EXAM_QUESTIONS if q["domain_id"] == "domain-1")
        d2_count = sum(1 for q in EXAM_QUESTIONS if q["domain_id"] == "domain-2")
        d1_pct = (d1_count / len(EXAM_QUESTIONS)) * 100
        d2_pct = (d2_count / len(EXAM_QUESTIONS)) * 100
        self.assertTrue(40.0 <= d1_pct <= 45.0, f"Domain 1 weight {d1_pct:.1f}% outside 40-45%")
        self.assertTrue(55.0 <= d2_pct <= 60.0, f"Domain 2 weight {d2_pct:.1f}% outside 55-60%")

        for q in EXAM_QUESTIONS:
            self.assertEqual(len(q["options"]), 4)
            self.assertIn(q["correct_index"], {0, 1, 2, 3})
            self.assertTrue(len(q["explanation"]) > 20)


class TestDualModeConfig(unittest.TestCase):
    def test_default_mock_mode_without_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            cfg = Settings.load(env_file=None)
            self.assertEqual(cfg.overall_mode, "mock")
            self.assertFalse(cfg.foundry_chat_live)
            self.assertFalse(cfg.content_understanding_live)

    def test_hybrid_mode_when_content_understanding_configured(self):
        env = {
            "AI901_MODE": "auto",
            "AZURE_CONTENT_UNDERSTANDING_ENDPOINT": "https://demo.services.ai.azure.com",
            "AZURE_CONTENT_UNDERSTANDING_KEY": "fake-key",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = Settings.load(env_file=None)
            self.assertTrue(cfg.content_understanding_live)
            self.assertEqual(cfg.overall_mode, "hybrid")

    def test_mock_override_forces_demo_mode(self):
        env = {
            "AI901_MODE": "mock",
            "AZURE_CONTENT_UNDERSTANDING_ENDPOINT": "https://demo.services.ai.azure.com",
            "AZURE_CONTENT_UNDERSTANDING_KEY": "fake-key",
        }
        with patch.dict(os.environ, env, clear=True):
            cfg = Settings.load(env_file=None)
            self.assertFalse(cfg.content_understanding_live)
            self.assertEqual(cfg.overall_mode, "mock")


class TestDualModeServices(unittest.TestCase):
    def setUp(self):
        with patch.dict(os.environ, {"AI901_MODE": "mock"}, clear=True):
            self.settings = Settings.load(env_file=None)

    def test_study_coach_demo(self):
        req = StudyCoachRequest(
            question_id="q-01",
            question_text=EXAM_QUESTIONS[0]["question"],
            selected_option="Inclusiveness",
            correct_option="Fairness",
            topic="Responsible AI — Fairness",
            follow_up="How does temperature affect this?",
        )
        res = run_study_coach(req, self.settings)
        self.assertEqual(res["mode"], "mock")
        self.assertIn("Fairness", res["data"]["coaching"])
        self.assertIn("temperature", res["data"]["coaching"].lower())

    def test_foundry_chat_demo(self):
        req = FoundryChatRequest(
            user_prompt="Explain Microsoft Foundry Single-Agent threads and tools.",
            temperature=0.2,
            max_tokens=200,
        )
        res = run_foundry_chat(req, self.settings)
        self.assertEqual(res["mode"], "mock")
        self.assertIn("Thread", res["data"]["reply"])
        self.assertEqual(res["data"]["content_safety"]["prompt_shield"], "passed")

    def test_single_agent_demo(self):
        req = FoundryAgentRequest(
            goal="Extract invoice totals from vendor PDFs and route low-confidence records to human review."
        )
        res = run_single_agent(req, self.settings)
        self.assertEqual(res["mode"], "mock")
        self.assertEqual(res["data"]["run_status"], "completed")
        self.assertEqual(len(res["data"]["tool_calls"]), 3)
        self.assertIn("Content Understanding", res["data"]["final_response"])

    def test_text_analysis_and_speech_demo(self):
        t_req = TextAnalysisRequest(
            text="Contoso Retail loves Microsoft Foundry in Seattle! Contact elena.morales@contoso.example."
        )
        t_res = analyze_text(t_req, self.settings)
        self.assertEqual(t_res["mode"], "mock")
        self.assertEqual(t_res["data"]["sentiment"]["overall"], "positive")
        self.assertIn("********", t_res["data"]["pii_redacted_text"])

        s_req = SpeechSimulationRequest(
            direction="tts",
            text="Hello Azure AI-901!",
            voice="en-US-AvaMultilingualNeural",
        )
        s_res = run_speech_lab(s_req, self.settings)
        self.assertEqual(s_res["mode"], "mock")
        self.assertIn("<speak", s_res["data"]["ssml"])

    def test_content_understanding_all_modalities(self):
        for modality in ("document", "image", "audio", "video"):
            req = ContentExtractionRequest(
                modality=modality,
                content="Sample invoice #INV-2026-999 Vendor: Contoso Total Due: $420.00 SKU: ALP-9042 ORD-77319",
            )
            res = extract_content(req, self.settings)
            self.assertEqual(res["mode"], "mock")
            self.assertEqual(res["data"]["modality"], modality)
            self.assertTrue(len(res["data"]["fields"]) >= 4)

    def test_vision_lab_analyze_and_generate(self):
        a_res = run_vision_lab(
            VisionLabRequest(task="analyze", prompt="Check shelf gaps", scene_preset="retail_shelf"),
            self.settings,
        )
        self.assertEqual(a_res["data"]["task"], "analyze")
        self.assertTrue(len(a_res["data"]["detections"]) >= 2)

        g_res = run_vision_lab(
            VisionLabRequest(task="generate", prompt="Isometric Azure AI Foundry workflow"),
            self.settings,
        )
        self.assertEqual(g_res["data"]["task"], "generate")
        self.assertEqual(g_res["data"]["content_safety"]["prompt_filter"], "passed")

    def test_api_route_functions(self):
        self.assertEqual(health()["status"], "ok")
        self.assertIn("services", status())
        curr = curriculum()
        self.assertEqual(len(curr["modules"]), 7)
        self.assertEqual(len(curr["questions"]), 30)


if __name__ == "__main__":
    unittest.main()
