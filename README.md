# AI-901 Study Studio

An interactive **Microsoft Azure AI Fundamentals (Exam AI-901)** study, practice exam, and **Dual-Mode Microsoft Foundry Lab** web application.

Exam **AI-901** replaced AI-900 in June 2026 and evaluates two official domains:
- **Domain 1 (40–45%)** — Identify AI concepts and capabilities (Responsible AI, model components & configuration, AI workloads)
- **Domain 2 (55–60%)** — Implement AI solutions by using Microsoft Foundry (generative AI chat & single-agent apps, text & speech, computer vision & image generation, and Azure Content Understanding)

---

## Features

1. **Interactive Study Guides (7 Modules)**
   - Complete coverage of all Domain 1 and Domain 2 objectives with progress tracking.
   - Built-in **Responsible AI Scenario Mapper** (Module 1.1) and **Live Decoding Parameter Simulator** (`temperature` & `top_p` probability visualizer in Module 1.2).
   - Copyable Python **Microsoft Foundry SDK**, **Azure Language**, **Azure Speech**, and **Azure Content Understanding** code snippets.
2. **Spaced-Repetition Flashcards (32 Cards)**
   - 3D flip deck filterable by domain and mastery status (`Unseen`, `Needs Review`, `Mastered`).
   - Full keyboard support: `Space` to flip, `←`/`→` to navigate, `1`/`2`/`3` to rate confidence.
3. **Exam AI-901 Practice Simulator (30 Weighted Questions)**
   - **Timed Mock Exam**: 45-minute countdown, question navigator, flag-for-review, Microsoft **700/1000** scaled scoring, and domain-by-domain breakdown.
   - **Study Quiz + AI-901 Study Coach**: Immediate rationale plus interactive follow-up coaching via `/api/study-coach`.
4. **Dual-Mode Microsoft Foundry Sandbox**
   - Works out-of-the-box in **Demo Mode** with realistic telemetry, token usage, tool execution traces, sentiment/NER/PII redaction, SSML synthesis, and multimodal Content Understanding schema extraction (`document`, `image`, `audio`, `video`).
   - Seamlessly upgrades per-service to **Live Microsoft Foundry / Azure SDKs** when `.env` credentials are provided.

---

## Quick Start (Local Demo Mode)

No Azure subscription or API keys are required to start:

```bash
cd ai-901-study-studio
pip install -r requirements.txt
python3 run.py
```

Open `http://localhost:8000` in your browser.

---

## Switching to Live Microsoft Foundry Mode

1. Install the optional Microsoft Foundry / Azure SDK dependencies:
   ```bash
   pip install -r requirements.txt -r requirements-azure.txt
   ```
2. Copy `.env.example` to `.env` and fill in any services you want to run live:
   ```bash
   cp .env.example .env
   ```
3. Restart `python3 run.py`. Click the status pill in the top-right header (`Demo Mode` / `Hybrid Mode` / `Live Foundry`) to verify which services are running live.

---

## Running Tests

```bash
python3 -m unittest discover -s tests -v
```

---

## Project Structure

```text
ai-901-study-studio/
├── run.py                          # Uvicorn launcher
├── .env.example                    # Dual-mode Microsoft Foundry & Azure credentials template
├── requirements.txt                # Core FastAPI server dependencies
├── requirements-azure.txt          # Optional Live Azure / Microsoft Foundry SDKs
├── backend/
│   ├── config.py                   # Dual-mode .env loader & per-service mode detector
│   ├── main.py                     # FastAPI API routes + static frontend hosting
│   ├── models.py                   # Pydantic request/response schemas
│   ├── data/curriculum.py          # Official AI-901 modules, 32 flashcards, 30 exam questions
│   └── services/
│       ├── foundry_service.py      # Dual-mode Foundry Chat, Single-Agent, & Study Coach
│       ├── text_speech_service.py  # Dual-mode Azure Language & Azure Speech
│       └── content_service.py      # Dual-mode Azure Content Understanding & Vision
├── frontend/
│   ├── index.html
│   ├── styles/main.css
│   └── js/
│       ├── app.js
│       ├── api.js
│       ├── state.js
│       ├── utils.js
│       └── views/                  # domains.js, flashcards.js, exam.js, sandbox.js
└── tests/
    └── test_services.py            # Automated curriculum, config, and dual-mode service tests
```
