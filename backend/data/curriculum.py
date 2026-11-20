"""Official Exam AI-901: Microsoft Azure AI Fundamentals curriculum dataset.

Aligned to Microsoft's AI-901 Skills Measured outline (2026):
  - Domain 1: Identify AI concepts and capabilities (40-45%)
  - Domain 2: Implement AI solutions by using Microsoft Foundry (55-60%)
"""

from __future__ import annotations

from typing import Any, Dict, List

EXAM_METADATA: Dict[str, Any] = {
    "code": "AI-901",
    "title": "Microsoft Azure AI Fundamentals",
    "passing_score": 700,
    "max_score": 1000,
    "duration_minutes": 45,
    "replaced_exam": "AI-900 (retired June 30, 2026)",
    "domains": [
        {
            "id": "domain-1",
            "code": "Domain 1",
            "title": "Identify AI concepts and capabilities",
            "weight_label": "40–45%",
            "weight_min": 40,
            "weight_max": 45,
            "summary": (
                "Responsible AI governance, how generative models work and are configured, "
                "and selecting the right AI workload across text, speech, vision, agents, and extraction."
            ),
        },
        {
            "id": "domain-2",
            "code": "Domain 2",
            "title": "Implement AI solutions by using Microsoft Foundry",
            "weight_label": "55–60%",
            "weight_min": 55,
            "weight_max": 60,
            "summary": (
                "Hands-on implementation in Microsoft Foundry: prompt design, model deployment, "
                "chat and single-agent Python clients, text/speech, multimodal vision, and Azure Content Understanding."
            ),
        },
    ],
}

STUDY_MODULES: List[Dict[str, Any]] = [
    {
        "id": "m1-responsible-ai",
        "domain_id": "domain-1",
        "number": "1.1",
        "title": "Principles of Responsible AI",
        "exam_focus": "High Frequency",
        "overview": (
            "Microsoft anchors every Azure AI solution in six Responsible AI principles. "
            "AI-901 questions typically present a realistic deployment risk and ask you to map "
            "it to the exact principle and appropriate mitigation."
        ),
        "key_concepts": [
            {
                "term": "Fairness",
                "detail": "AI systems should treat all people fairly and avoid amplifying demographic or socioeconomic bias (e.g., loan approval or hiring scoring disparities across age/gender cohorts).",
            },
            {
                "term": "Reliability & Safety",
                "detail": "Systems must operate consistently under expected and edge-case conditions, with rigorous red-teaming, Azure AI Content Safety filters, and human-in-the-loop fallbacks for high-stakes actions.",
            },
            {
                "term": "Privacy & Security",
                "detail": "Protect personal data (PII), enforce Microsoft Entra ID RBAC, prevent prompt injection/data exfiltration, and ensure customer prompts are not used to retrain foundation models.",
            },
            {
                "term": "Inclusiveness",
                "detail": "Empower everyone across abilities, languages, and contexts — e.g., captioning with Azure Speech, screen-reader alt-text with Vision, and multilingual support.",
            },
            {
                "term": "Transparency",
                "detail": "Users should understand when they are interacting with AI, what data informs predictions, confidence limits, and documented system capabilities (Transparency Notes).",
            },
            {
                "term": "Accountability",
                "detail": "Clear organizational governance, audit trails, impact assessments, and designated human owners remain responsible for AI outcomes — never 'the algorithm did it'.",
            },
        ],
        "exam_tips": [
            "If a scenario mentions 'bias against a demographic group' -> Fairness.",
            "If a scenario mentions 'disclosing that a chatbot is AI-powered' or 'explaining model limitations' -> Transparency.",
            "If a scenario mentions 'accessibility for visually or hearing impaired users' -> Inclusiveness.",
            "If a scenario mentions 'governance committees, audit logs, or legal ownership' -> Accountability.",
        ],
        "code_snippet": None,
        "interactive_widget": "responsible_ai_checklist",
    },
    {
        "id": "m1-models-config",
        "domain_id": "domain-1",
        "number": "1.2",
        "title": "AI Model Components & Configurations",
        "exam_focus": "Core Concept",
        "overview": (
            "Understand the mechanics of generative AI models (tokens, embeddings, transformer attention), "
            "how to pick the right model class for a task, and how deployment options and inference "
            "parameters shape latency, cost, and determinism."
        ),
        "key_concepts": [
            {
                "term": "How Generative AI Works",
                "detail": "Text is split into tokens (~3–4 chars in English), mapped into high-dimensional vector embeddings capturing semantic meaning, processed by Transformer self-attention layers, and decoded probabilistically one next-token at a time.",
            },
            {
                "term": "Choosing Models by Capability",
                "detail": "Match capability to cost: SLMs (e.g., Phi-4) for fast/low-cost edge or summarization; flagship LLMs (e.g., GPT-4o) for multimodal chat; reasoning models (o-series) for multi-step math/coding; embedding models for vector search/RAG; image models for visual synthesis.",
            },
            {
                "term": "Deployment Options in Foundry",
                "detail": "Standard (pay-per-token, regional), Global Standard (pay-per-token with global routing for higher throughput), Provisioned Throughput / PTU (reserved capacity for predictable low latency at scale), and Serverless API (partner models like Llama/Mistral billed per token).",
            },
            {
                "term": "Configuration Parameters",
                "detail": "temperature (0 = deterministic, higher = more creative/random), top_p (nucleus sampling probability cutoff — usually tune temperature OR top_p, not both), max_tokens (caps response length & cost), frequency/presence penalties (discourage repetition).",
            },
        ],
        "exam_tips": [
            "Need repeatable JSON extraction or factual Q&A? Set temperature near 0.0–0.2.",
            "Need guaranteed low latency for a high-volume enterprise app? Choose Provisioned Throughput (PTU), not Standard.",
            "Grounding a model on private company docs without retraining weights? Use RAG (embeddings + search) rather than fine-tuning.",
        ],
        "code_snippet": None,
        "interactive_widget": "parameter_sandbox",
    },
    {
        "id": "m1-ai-workloads",
        "domain_id": "domain-1",
        "number": "1.3",
        "title": "Common AI Workloads & Scenarios",
        "exam_focus": "High Frequency",
        "overview": (
            "AI-901 tests your ability to map real business scenarios to the five foundational workload "
            "families: Generative & Agentic AI, Text Analysis, Speech, Computer Vision & Image Generation, "
            "and Multimodal Information Extraction."
        ),
        "key_concepts": [
            {
                "term": "Generative vs. Agentic AI",
                "detail": "Generative AI creates new content (text, code, images, audio) in response to prompts. Agentic AI adds goals, persistent instructions, grounding knowledge, and tool/function calling to plan and complete multi-step actions autonomously.",
            },
            {
                "term": "Text Analysis Techniques",
                "detail": "Key phrase extraction (main talking points), Entity recognition / NER (people, orgs, dates, PII), Sentiment analysis & opinion mining (positive/neutral/negative polarity), and Summarization (extractive picks verbatim sentences; abstractive writes a fresh summary).",
            },
            {
                "term": "Speech Recognition & Synthesis",
                "detail": "Speech-to-Text (STT / recognition) converts spoken audio into text (real-time or batch transcription). Text-to-Speech (TTS / synthesis) generates lifelike neural voices (supporting SSML for pitch, rate, and style). Speech Translation handles spoken cross-language workflows.",
            },
            {
                "term": "Computer Vision & Image Generation",
                "detail": "Vision interprets visual media: image classification, object detection (bounding boxes), optical character recognition (OCR), and dense captioning. Image generation synthesizes new images from text prompts or edits existing visuals.",
            },
            {
                "term": "Information Extraction",
                "detail": "Turns unstructured documents, forms, invoices, images, audio calls, and video recordings into structured schema-validated JSON fields (e.g., vendor name, line items, call disposition, video scene summaries).",
            },
        ],
        "exam_tips": [
            "Extractive summarization selects exact sentences from the source; abstractive summarization generates newly phrased sentences.",
            "Entity linking disambiguates entities (e.g., 'Mars' the planet vs 'Mars' the candy company) to a knowledge base.",
            "Need structured JSON extracted across PDFs, images, audio, AND video with one unified workflow? Think Azure Content Understanding.",
        ],
        "code_snippet": None,
        "interactive_widget": None,
    },
    {
        "id": "m2-foundry-genai-agents",
        "domain_id": "domain-2",
        "number": "2.1",
        "title": "Generative AI Apps & Agents in Microsoft Foundry",
        "exam_focus": "Core Implementation",
        "overview": (
            "Microsoft Foundry is the unified workspace for AI-901 Domain 2. Understand the distinction "
            "between a Foundry resource (Azure service boundary, RBAC, networking) and a Foundry project "
            "(workspace grouping deployed models, agents, evaluations, and connections), then build chat and agent clients."
        ),
        "key_concepts": [
            {
                "term": "Foundry Resource vs. Project",
                "detail": "A Microsoft Foundry resource is the underlying Azure resource managing billing, security, and endpoints. Projects live inside it to organize a team's models, prompts, datasets, connections, and agents.",
            },
            {
                "term": "System vs. User Prompts",
                "detail": "The system prompt defines role, tone, behavioral guardrails, and output schema (persistent instructions). The user prompt supplies the immediate request or task input. Few-shot examples improve output consistency.",
            },
            {
                "term": "Lightweight Chat Client (Foundry SDK)",
                "detail": "Use `AIProjectClient` with `DefaultAzureCredential` (Entra ID) to retrieve an authenticated OpenAI client, then send structured `messages` (`system`, `user`, `assistant`) to your deployed model.",
            },
            {
                "term": "Single-Agent Solutions",
                "detail": "In the Foundry portal or SDK, configure an Agent with: (1) a deployed model, (2) instructions, (3) optional knowledge/grounding files, and (4) tools (e.g., Code Interpreter, File Search, Bing Grounding, or custom functions). Client apps create a thread, add messages, run the agent, and read responses.",
            },
        ],
        "exam_tips": [
            "Prefer Microsoft Entra ID (`DefaultAzureCredential`) over hardcoded API keys for production Foundry SDK apps.",
            "Remember the Foundry Agent execution loop: create agent -> create thread -> post user message -> create & process run -> list messages.",
            "Put persona, safety boundaries, and output format rules in the `system` role, not just the `user` message.",
        ],
        "code_snippet": {
            "title": "Foundry SDK — Chat & Single-Agent Client (Python)",
            "language": "python",
            "code": """import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# 1. Connect to your Microsoft Foundry Project
project = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# 2. Lightweight Chat Client via Project OpenAI client
openai_client = project.get_openai_client()
chat_resp = openai_client.chat.completions.create(
    model=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o-mini"),
    temperature=0.2,
    max_tokens=250,
    messages=[
        {"role": "system", "content": "You are a concise Azure AI-901 tutor."},
        {"role": "user", "content": "When should I use a Foundry Agent vs plain chat?"},
    ],
)
print(chat_resp.choices[0].message.content)

# 3. Single-Agent invocation (using a Foundry Agent ID)
agent_id = os.environ["AZURE_AI_AGENT_ID"]
thread = project.agents.threads.create()
project.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content="Summarize our Q3 refund policy using the attached knowledge file.",
)
run = project.agents.runs.create_and_process(thread_id=thread.id, agent_id=agent_id)
print(f"Agent run status: {run.status}")""",
        },
        "interactive_widget": None,
    },
    {
        "id": "m2-text-speech",
        "domain_id": "domain-2",
        "number": "2.2",
        "title": "Text Analysis & Speech Solutions in Foundry",
        "exam_focus": "Core Implementation",
        "overview": (
            "Implement natural language and audio workloads using Azure Language (Text Analytics SDK), "
            "Azure Speech in Foundry Tools, and multimodal audio-capable models that respond directly "
            "to spoken prompts."
        ),
        "key_concepts": [
            {
                "term": "Text Analysis Client App",
                "detail": "Use `TextAnalyticsClient` from `azure-ai-textanalytics` to extract key phrases, recognize entities (NER), detect language, and evaluate sentiment polarity + confidence scores in a few lines of Python.",
            },
            {
                "term": "Responding to Spoken Prompts (Multimodal)",
                "detail": "Audio-capable multimodal models (e.g., GPT-4o audio / realtime deployments in Foundry) accept base64-encoded WAV/MP3 input directly inside chat messages and reason over spoken intent, tone, and content without a separate transcription pipeline.",
            },
            {
                "term": "Azure Speech in Foundry Tools",
                "detail": "Use `SpeechConfig` with region/endpoint and key (or Entra token), paired with `SpeechRecognizer` (microphone or audio file -> text) and `SpeechSynthesizer` (text or SSML -> neural voice output).",
            },
        ],
        "exam_tips": [
            "Know when to use Azure Speech SDK vs. Multimodal audio models: Speech SDK excels at deterministic real-time STT, custom pronunciation/vocab, and SSML neural TTS; multimodal models excel at reasoning directly over spoken prompts.",
            "Azure Speech supports SSML (Speech Synthesis Markup Language) to control voice style, speaking rate, pauses, and pronunciation.",
        ],
        "code_snippet": {
            "title": "Azure Language & Azure Speech Clients (Python)",
            "language": "python",
            "code": """import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import azure.cognitiveservices.speech as speechsdk

# 1. Text Analysis (Sentiment + Key Phrases)
ta_client = TextAnalyticsClient(
    endpoint=os.environ["AZURE_LANGUAGE_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["AZURE_LANGUAGE_KEY"]),
)
docs = ["Microsoft Foundry unified our chat, speech, and document workflows!"]
sentiment = ta_client.analyze_sentiment(docs)[0]
phrases = ta_client.extract_key_phrases(docs)[0]
print("Sentiment:", sentiment.sentiment, "| Key phrases:", phrases.key_phrases)

# 2. Speech Synthesis (Text-to-Speech via Azure Speech in Foundry Tools)
speech_cfg = speechsdk.SpeechConfig(
    subscription=os.environ["AZURE_SPEECH_KEY"],
    region=os.environ["AZURE_SPEECH_REGION"],
)
speech_cfg.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"
synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_cfg, audio_config=None)
result = synthesizer.speak_text_async("Welcome to Azure AI-901.").get()""",
        },
        "interactive_widget": None,
    },
    {
        "id": "m2-vision-imagegen",
        "domain_id": "domain-2",
        "number": "2.3",
        "title": "Computer Vision & Image Generation in Foundry",
        "exam_focus": "Core Implementation",
        "overview": (
            "Combine multimodal vision models to inspect images via prompts and generative image models "
            "to synthesize visuals from natural language descriptions — all deployed and governed inside Microsoft Foundry."
        ),
        "key_concepts": [
            {
                "term": "Multimodal Visual Prompts",
                "detail": "Pass an array of content parts in a user message: a `text` instruction plus one or more `image_url` entries (HTTPS URL or `data:image/jpeg;base64,...`). The model can describe scenes, read handwritten notes, inspect defects, or answer visual questions.",
            },
            {
                "term": "Image Generation Models",
                "detail": "Models like GPT-Image-1 / DALL-E 3 / FLUX deployed in Foundry generate novel visual assets from descriptive text prompts. Configure size, quality, and style, and always enforce Content Safety filters.",
            },
            {
                "term": "Specialized Vision vs. Multimodal LLMs",
                "detail": "Use Azure AI Vision when you need fast, structured bounding boxes, spatial analysis, or high-throughput OCR; use a multimodal LLM in Foundry when you need open-ended visual reasoning and rich explanations.",
            },
        ],
        "exam_tips": [
            "Multimodal vision chat prompts send a list of content blocks (`type: 'text'` and `type: 'image_url'`) inside the `user` message.",
            "Remember Responsible AI for generated images: apply Content Safety filters, disclose AI-generated media (Transparency / Content Credentials), and guard against impersonation.",
        ],
        "code_snippet": {
            "title": "Multimodal Vision & Image Generation in Foundry (Python)",
            "language": "python",
            "code": """import base64, os
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    api_version="2024-12-01-preview",
)

# 1. Interpret visual input with a multimodal deployment
with open("warehouse_shelf.jpg", "rb") as f:
    b64_img = base64.b64encode(f.read()).decode("utf-8")

vision_resp = client.chat.completions.create(
    model=os.environ.get("AZURE_OPENAI_VISION_DEPLOYMENT", "gpt-4o-mini"),
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Identify any empty shelf slots or safety hazards."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}},
            ],
        }
    ],
)
print(vision_resp.choices[0].message.content)

# 2. Generate a new visual output
img = client.images.generate(
    model="gpt-image-1",
    prompt="Clean isometric diagram of a solar-powered smart greenhouse, editorial style",
    size="1024x1024",
)""",
        },
        "interactive_widget": None,
    },
    {
        "id": "m2-content-understanding",
        "domain_id": "domain-2",
        "number": "2.4",
        "title": "Information Extraction with Azure Content Understanding",
        "exam_focus": "New in AI-901!",
        "overview": (
            "A signature addition in AI-901! Azure Content Understanding in Foundry Tools provides a single, "
            "schema-driven extraction pipeline across documents/forms, images, audio, and video — outputting "
            "structured JSON with confidence scores and grounding citations."
        ),
        "key_concepts": [
            {
                "term": "Analyzers & Field Schemas",
                "detail": "An Analyzer defines the modality (document, image, audio, video) and a target field schema (e.g., `VendorName`, `InvoiceTotal`, `CallSentiment`, `ActionItems`, `KeyFrames`) with extraction methods (`extract`, `classify`, or `generate`).",
            },
            {
                "term": "Documents & Forms",
                "detail": "Extract tables, key-value pairs, line items, checkboxes, and tax fields from invoices, receipts, contracts, and scanned PDFs with bounding-region provenance.",
            },
            {
                "term": "Images",
                "detail": "Extract structured catalog attributes (product SKU, color, defect flags, signage text) directly from photos into normalized JSON records.",
            },
            {
                "term": "Audio & Video",
                "detail": "Transcribe calls with speaker diarization, extract call reason/sentiment/follow-ups from audio, and segment videos into timestamped chapters, key frames, and structured summaries.",
            },
        ],
        "exam_tips": [
            "Azure Content Understanding is the go-to AI-901 service whenever a question asks to extract structured schema-based fields from multimodal content (documents, images, audio, or video).",
            "Content Understanding analyzers follow an asynchronous REST pattern: POST `:analyze` -> poll Operation-Location URL -> read structured JSON result with field confidence scores.",
            "Distinguish field methods: `extract` pulls literal values, `classify` picks from predefined labels, and `generate` synthesizes summaries or inferred fields.",
        ],
        "code_snippet": {
            "title": "Azure Content Understanding REST Client (Python)",
            "language": "python",
            "code": """import os, time, httpx

endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"].rstrip("/")
api_key = os.environ["AZURE_CONTENT_UNDERSTANDING_KEY"]
analyzer_id = "prebuilt-invoice"  # or your custom Foundry analyzer ID
url = f"{endpoint}/contentunderstanding/analyzers/{analyzer_id}:analyze?api-version=2025-05-01-preview"

headers = {"Ocp-Apim-Subscription-Key": api_key, "Content-Type": "application/json"}
payload = {"url": "https://example.com/samples/invoice_2026.pdf"}

# 1. Start asynchronous analysis
resp = httpx.post(url, headers=headers, json=payload, timeout=30)
resp.raise_for_status()
op_location = resp.headers["Operation-Location"]

# 2. Poll until succeeded
while True:
    poll = httpx.get(op_location, headers={"Ocp-Apim-Subscription-Key": api_key}).json()
    if poll["status"] in ("Succeeded", "Failed"):
        break
    time.sleep(1.5)

# 3. Inspect structured fields & confidence scores
fields = poll["result"]["contents"][0]["fields"]
print({k: v.get("valueString") or v.get("valueNumber") for k, v in fields.items()})""",
        },
        "interactive_widget": None,
    },
]

FLASHCARDS: List[Dict[str, Any]] = [
    # Domain 1 (14 cards)
    {
        "id": "fc-01",
        "domain_id": "domain-1",
        "module_id": "m1-responsible-ai",
        "tag": "Responsible AI",
        "front": "What are Microsoft's six principles of Responsible AI?",
        "back": "Fairness, Reliability & Safety, Privacy & Security, Inclusiveness, Transparency, and Accountability.",
    },
    {
        "id": "fc-02",
        "domain_id": "domain-1",
        "module_id": "m1-responsible-ai",
        "tag": "Responsible AI",
        "front": "A medical triage assistant fails to notify patients that responses are AI-generated and hides its confidence limits. Which Responsible AI principle is violated?",
        "back": "Transparency — users must know they are interacting with AI and understand the system's purpose, data basis, and limitations.",
    },
    {
        "id": "fc-03",
        "domain_id": "domain-1",
        "module_id": "m1-responsible-ai",
        "tag": "Responsible AI",
        "front": "Adding real-time live captions and screen-reader alt-text to an enterprise training portal primarily supports which Responsible AI principle?",
        "back": "Inclusiveness — designing AI solutions that empower people of all abilities, backgrounds, and languages.",
    },
    {
        "id": "fc-04",
        "domain_id": "domain-1",
        "module_id": "m1-responsible-ai",
        "tag": "Responsible AI",
        "front": "How do Reliability & Safety and Accountability differ in Responsible AI?",
        "back": "Reliability & Safety focuses on technical robustness, testing, guardrails, and avoiding harm during operation. Accountability establishes human governance, auditability, and organizational ownership for AI outcomes.",
    },
    {
        "id": "fc-05",
        "domain_id": "domain-1",
        "module_id": "m1-models-config",
        "tag": "Model Mechanics",
        "front": "What is a token, and why does tokenization matter in Microsoft Foundry?",
        "back": "A token is the basic unit of text (often a word fragment, ~3–4 English characters) processed by a language model. Context windows, latency, rate limits (TPM), and pay-per-token billing are all measured in tokens.",
    },
    {
        "id": "fc-06",
        "domain_id": "domain-1",
        "module_id": "m1-models-config",
        "tag": "Model Mechanics",
        "front": "What are embeddings used for in generative AI solutions?",
        "back": "Embeddings convert text (or other media) into dense numerical vectors so semantically similar items lie close together in vector space — powering semantic search, clustering, and Retrieval-Augmented Generation (RAG).",
    },
    {
        "id": "fc-07",
        "domain_id": "domain-1",
        "module_id": "m1-models-config",
        "tag": "Configuration",
        "front": "How does lowering `temperature` (e.g., to 0.0–0.2) affect model output?",
        "back": "It sharpens the next-token probability distribution so the model consistently picks the highest-probability tokens — making answers more deterministic, factual, and repeatable (ideal for extraction or code).",
    },
    {
        "id": "fc-08",
        "domain_id": "domain-1",
        "module_id": "m1-models-config",
        "tag": "Configuration",
        "front": "What is `top_p` (nucleus sampling), and what is the best practice when using it with `temperature`?",
        "back": "`top_p` limits token selection to the smallest set of top tokens whose cumulative probability reaches p (e.g., 0.9). Best practice is to adjust either `temperature` OR `top_p`, not both simultaneously.",
    },
    {
        "id": "fc-09",
        "domain_id": "domain-1",
        "module_id": "m1-models-config",
        "tag": "Deployment Options",
        "front": "When should you choose Provisioned Throughput (PTU) over Standard pay-per-token deployment in Microsoft Foundry?",
        "back": "Choose PTU when you have predictable, high-volume production traffic that requires reserved capacity and consistent low latency without noisy-neighbor throttling.",
    },
    {
        "id": "fc-10",
        "domain_id": "domain-1",
        "module_id": "m1-models-config",
        "tag": "Model Selection",
        "front": "Why might a team choose a Small Language Model (SLM, e.g., Phi-4) instead of a flagship frontier LLM?",
        "back": "SLMs deliver lower latency, significantly lower per-token or compute cost, and can even run on-device/edge — ideal for focused classification, summarization, or structured extraction tasks.",
    },
    {
        "id": "fc-11",
        "domain_id": "domain-1",
        "module_id": "m1-ai-workloads",
        "tag": "Text Analysis",
        "front": "What is the difference between extractive and abstractive summarization?",
        "back": "Extractive summarization selects and stitches together exact high-scoring sentences from the original text. Abstractive summarization paraphrases and generates new sentences capturing the core meaning.",
    },
    {
        "id": "fc-12",
        "domain_id": "domain-1",
        "module_id": "m1-ai-workloads",
        "tag": "Text Analysis",
        "front": "Distinguish Named Entity Recognition (NER) from Key Phrase Extraction.",
        "back": "NER identifies and categorizes specific entities (Person, Organization, Location, Date, Quantity, PII). Key Phrase Extraction identifies the main talking points or topics in a document.",
    },
    {
        "id": "fc-13",
        "domain_id": "domain-1",
        "module_id": "m1-ai-workloads",
        "tag": "Agentic AI",
        "front": "What distinguishes an Agentic AI workload from a standard Generative AI chat completion?",
        "back": "An agent combines a model with persistent instructions, grounding knowledge, and callable tools (functions, search, code execution) to plan and execute multi-step actions toward a goal.",
    },
    {
        "id": "fc-14",
        "domain_id": "domain-1",
        "module_id": "m1-ai-workloads",
        "tag": "Computer Vision",
        "front": "How do Image Classification and Object Detection differ?",
        "back": "Image Classification assigns one or more labels to the entire image. Object Detection locates multiple objects inside the image and returns both a label and bounding-box coordinates for each.",
    },
    # Domain 2 (18 cards)
    {
        "id": "fc-15",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "tag": "Foundry Architecture",
        "front": "In Microsoft Foundry, what is the difference between a Foundry Resource and a Foundry Project?",
        "back": "A Foundry Resource is the Azure service boundary (billing, RBAC, networking, endpoints). A Foundry Project sits inside it as the developer workspace grouping models, agents, connections, and evaluations for a specific AI app.",
    },
    {
        "id": "fc-16",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "tag": "Prompt Design",
        "front": "What belongs in a `system` prompt versus a `user` prompt?",
        "back": "System prompt: persona, tone, behavioral guardrails, grounding rules, and output formatting requirements. User prompt: the specific task, question, or data provided at runtime.",
    },
    {
        "id": "fc-17",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "tag": "Foundry SDK",
        "front": "Which Python class connects a client application to a Microsoft Foundry project using Microsoft Entra ID?",
        "back": "`AIProjectClient` from `azure.ai.projects`, authenticated with `DefaultAzureCredential` from `azure.identity`.",
    },
    {
        "id": "fc-18",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "tag": "Foundry Agents",
        "front": "What are the four core steps to invoke a Microsoft Foundry Agent from a Python client?",
        "back": "1) Create a Thread (`agents.threads.create`), 2) Add a user Message to the thread, 3) Run the Agent (`agents.runs.create_and_process`), 4) Retrieve the assistant Messages from the thread.",
    },
    {
        "id": "fc-19",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "tag": "Foundry Agents",
        "front": "What components define a single-agent solution in the Microsoft Foundry portal?",
        "back": "A deployed foundation model, system Instructions (role & rules), Knowledge sources (files/Azure AI Search for grounding), and Tools (Code Interpreter, File Search, Bing Grounding, OpenAPI/custom functions).",
    },
    {
        "id": "fc-20",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "tag": "Prompt Engineering",
        "front": "What is few-shot prompting, and when does it help in Foundry?",
        "back": "Providing 2–5 input/output examples inside the prompt so the model mirrors the desired tone, classification taxonomy, or JSON structure without fine-tuning.",
    },
    {
        "id": "fc-21",
        "domain_id": "domain-2",
        "module_id": "m2-text-speech",
        "tag": "Text Analysis SDK",
        "front": "Which Azure Python SDK client is used to run sentiment analysis, entity recognition, and key phrase extraction?",
        "back": "`TextAnalyticsClient` from the `azure-ai-textanalytics` package.",
    },
    {
        "id": "fc-22",
        "domain_id": "domain-2",
        "module_id": "m2-text-speech",
        "tag": "Azure Speech",
        "front": "Which two core classes in `azure.cognitiveservices.speech` perform Speech-to-Text and Text-to-Speech?",
        "back": "`SpeechRecognizer` converts spoken audio to text (STT), and `SpeechSynthesizer` converts text or SSML into spoken audio (TTS) — both configured with `SpeechConfig`.",
    },
    {
        "id": "fc-23",
        "domain_id": "domain-2",
        "module_id": "m2-text-speech",
        "tag": "Azure Speech",
        "front": "What is SSML in Azure Speech, and why would a developer use it?",
        "back": "Speech Synthesis Markup Language (XML-based) lets you fine-tune synthesized speech: voice selection, speaking rate, pitch, pauses/breaks, emphasis, and pronunciation phonemes.",
    },
    {
        "id": "fc-24",
        "domain_id": "domain-2",
        "module_id": "m2-text-speech",
        "tag": "Multimodal Audio",
        "front": "How does responding to a spoken prompt with a deployed multimodal model differ from a traditional STT -> LLM pipeline?",
        "back": "A multimodal audio-capable model processes raw audio input directly inside the chat request, capturing tone, intent, and non-verbal cues in a single model call with lower orchestration overhead.",
    },
    {
        "id": "fc-25",
        "domain_id": "domain-2",
        "module_id": "m2-vision-imagegen",
        "tag": "Multimodal Vision",
        "front": "How do you send an image alongside text to a multimodal chat model in Microsoft Foundry?",
        "back": "In the `user` message, set `content` to a list containing a `{\"type\": \"text\", \"text\": ...}` object and an `{\"type\": \"image_url\", \"image_url\": {\"url\": ...}}` object (HTTPS URL or base64 data URI).",
    },
    {
        "id": "fc-26",
        "domain_id": "domain-2",
        "module_id": "m2-vision-imagegen",
        "tag": "Image Generation",
        "front": "What safeguards should accompany an image-generation feature built in Microsoft Foundry?",
        "back": "Enable Azure AI Content Safety filters (blocking harmful/NSFW/copyrighted abuse), validate prompts, and disclose AI-generated visuals (Transparency / watermarking or Content Credentials).",
    },
    {
        "id": "fc-27",
        "domain_id": "domain-2",
        "module_id": "m2-vision-imagegen",
        "tag": "Computer Vision",
        "front": "What is OCR (Optical Character Recognition), and what kinds of text can Azure Vision read?",
        "back": "OCR extracts printed and handwritten text from images, scanned PDFs, receipts, street signs, and whiteboards, returning text lines along with bounding coordinates.",
    },
    {
        "id": "fc-28",
        "domain_id": "domain-2",
        "module_id": "m2-content-understanding",
        "tag": "Content Understanding",
        "front": "What is Azure Content Understanding in Foundry Tools?",
        "back": "A unified multimodal information-extraction service in Microsoft Foundry that uses schema-driven Analyzers to transform unstructured documents, forms, images, audio, and video into structured JSON with confidence scores.",
    },
    {
        "id": "fc-29",
        "domain_id": "domain-2",
        "module_id": "m2-content-understanding",
        "tag": "Content Understanding",
        "front": "What are the three field extraction methods you can define in an Azure Content Understanding analyzer schema?",
        "back": "1) `extract` (pull literal values directly from content), 2) `classify` (assign one of your predefined categories), and 3) `generate` (infer or summarize values based on the content).",
    },
    {
        "id": "fc-30",
        "domain_id": "domain-2",
        "module_id": "m2-content-understanding",
        "tag": "Content Understanding",
        "front": "How does Azure Content Understanding handle audio and video inputs?",
        "back": "For audio, it produces speaker-diarized transcripts plus structured call fields (topic, sentiment, action items). For video, it segments scenes/chapters, extracts key frames, and populates schema fields with timestamps.",
    },
    {
        "id": "fc-31",
        "domain_id": "domain-2",
        "module_id": "m2-content-understanding",
        "tag": "Content Understanding",
        "front": "Why are confidence scores and grounding citations valuable in Content Understanding outputs?",
        "back": "They enable human-in-the-loop review workflows: high-confidence extractions auto-process while low-confidence fields route to a human reviewer with exact source page/timestamp provenance.",
    },
    {
        "id": "fc-32",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "tag": "Foundry Safety",
        "front": "What role does grounding (RAG) play in reducing hallucinations in a Foundry chat or agent app?",
        "back": "Retrieval-Augmented Generation retrieves verified, up-to-date excerpts from your data sources and injects them into the model prompt so responses stay anchored to factual evidence rather than relying solely on pretraining memory.",
    },
]

EXAM_QUESTIONS: List[Dict[str, Any]] = [
    # =========================================================================
    # DOMAIN 1: Identify AI concepts and capabilities (13 questions = 43.3%)
    # =========================================================================
    {
        "id": "q-01",
        "domain_id": "domain-1",
        "module_id": "m1-responsible-ai",
        "topic": "Responsible AI — Fairness",
        "question": (
            "A financial services company trains a credit-scoring AI model on 15 years of historical loan "
            "decisions. During testing, the team discovers the model rejects applicants from certain postal "
            "codes at twice the rate of applicants with identical income and credit history in other areas. "
            "Which Microsoft Responsible AI principle is primarily at risk?"
        ),
        "options": [
            "Fairness",
            "Inclusiveness",
            "Transparency",
            "Privacy and security",
        ],
        "correct_index": 0,
        "explanation": (
            "Fairness ensures AI systems treat similar individuals equitably and do not perpetuate or amplify "
            "historical demographic or geographic bias. Inclusiveness addresses accessibility across abilities/languages, "
            "Transparency covers disclosing how the system works, and Privacy & Security protects personal data."
        ),
    },
    {
        "id": "q-02",
        "domain_id": "domain-1",
        "module_id": "m1-responsible-ai",
        "topic": "Responsible AI — Accountability",
        "question": (
            "An enterprise deploys a customer-facing generative AI support agent. Leadership establishes a "
            "cross-functional review board, mandates pre-release Responsible AI impact assessments, and logs "
            "every automated escalation with a named engineering owner. Which Responsible AI principle does "
            "this governance structure primarily uphold?"
        ),
        "options": [
            "Reliability and safety",
            "Transparency",
            "Accountability",
            "Fairness",
        ],
        "correct_index": 2,
        "explanation": (
            "Accountability establishes clear organizational governance, review boards, impact assessments, "
            "and human ownership for AI system outcomes. Reliability & Safety focuses on operational resilience "
            "and technical guardrails."
        ),
    },
    {
        "id": "q-03",
        "domain_id": "domain-1",
        "module_id": "m1-responsible-ai",
        "topic": "Responsible AI — Transparency",
        "question": (
            "You are launching an AI-powered HR policy assistant inside your company's intranet. You add a "
            "banner stating 'Responses are generated by AI and may contain inaccuracies — verify critical "
            "benefits decisions with HR' and publish a note explaining which handbook documents the assistant searches. "
            "Which Responsible AI principle are you implementing?"
        ),
        "options": [
            "Inclusiveness",
            "Transparency",
            "Privacy and security",
            "Fairness",
        ],
        "correct_index": 1,
        "explanation": (
            "Transparency requires clearly disclosing when users are interacting with AI, communicating system "
            "capabilities and limitations, and documenting the data sources used."
        ),
    },
    {
        "id": "q-04",
        "domain_id": "domain-1",
        "module_id": "m1-responsible-ai",
        "topic": "Responsible AI — Privacy & Security",
        "question": (
            "A healthcare startup builds a clinical note summarizer on Microsoft Foundry. To prevent sensitive "
            "patient records from leaking via unauthorized API access or adversarial prompts, the team enables "
            "Microsoft Entra ID RBAC, private endpoints, and Prompt Shields. Which Responsible AI principle do "
            "these controls primarily address?"
        ),
        "options": [
            "Fairness",
            "Inclusiveness",
            "Accountability",
            "Privacy and security",
        ],
        "correct_index": 3,
        "explanation": (
            "Privacy and security encompasses protecting personal/sensitive data (PHI/PII), enforcing access control "
            "(RBAC, private networking), and defending against prompt injection or data exfiltration."
        ),
    },
    {
        "id": "q-05",
        "domain_id": "domain-1",
        "module_id": "m1-responsible-ai",
        "topic": "Responsible AI — Reliability & Safety",
        "question": (
            "Before rolling out an automated warehouse robotics vision model, engineers run adversarial stress "
            "tests under dim lighting, configure automatic shutdown if detection confidence drops below 85%, "
            "and require a human supervisor to approve overrides. Which principle is being prioritized?"
        ),
        "options": [
            "Reliability and safety",
            "Transparency",
            "Inclusiveness",
            "Fairness",
        ],
        "correct_index": 0,
        "explanation": (
            "Reliability and safety ensures AI systems behave predictably under edge cases, detect low-confidence "
            "failure states safely, and include human-in-the-loop fail-safes to prevent physical or operational harm."
        ),
    },
    {
        "id": "q-06",
        "domain_id": "domain-1",
        "module_id": "m1-models-config",
        "topic": "Generative AI Mechanics",
        "question": (
            "How does a Transformer-based large language model generate a response to a user prompt?"
        ),
        "options": [
            "It queries a relational SQL database for an exact pre-written paragraph matching the prompt.",
            "It splits input into tokens, computes contextual relationships via attention, and predicts the next token probabilistically step by step.",
            "It compiles the prompt into Python bytecode and executes deterministic if-else rules.",
            "It converts the entire response into a single pixel grid and runs OCR to produce text.",
        ],
        "correct_index": 1,
        "explanation": (
            "Transformer LLMs tokenize input text into numerical IDs/embeddings, weigh contextual relationships "
            "across tokens using self-attention, and autoregressively sample one next token at a time."
        ),
    },
    {
        "id": "q-07",
        "domain_id": "domain-1",
        "module_id": "m1-models-config",
        "topic": "Model Configuration Parameters",
        "question": (
            "You are building a Microsoft Foundry app that extracts standardized SKU codes and JSON fields from "
            "supplier emails. Responses currently vary too much between identical runs. Which parameter change "
            "is most effective to make outputs more deterministic?"
        ),
        "options": [
            "Increase `temperature` to 1.6",
            "Set `temperature` close to 0.0 (for example, 0.0–0.2)",
            "Increase `presence_penalty` to 2.0",
            "Set `max_tokens` to 4096",
        ],
        "correct_index": 1,
        "explanation": (
            "Lower `temperature` (near 0) concentrates probability mass on the most likely tokens, producing "
            "consistent, repeatable outputs ideal for extraction. Higher temperature increases randomness, "
            "`presence_penalty` encourages introducing new topics, and `max_tokens` only limits length."
        ),
    },
    {
        "id": "q-08",
        "domain_id": "domain-1",
        "module_id": "m1-models-config",
        "topic": "Model Deployment Options",
        "question": (
            "A global retail company expects steady, high-volume traffic (thousands of requests per minute) "
            "for its checkout assistant and requires predictable low latency backed by reserved model capacity. "
            "Which Microsoft Foundry deployment option fits best?"
        ),
        "options": [
            "Provisioned Throughput (PTU)",
            "Standard pay-per-token in a single test region",
            "Free tier playground only",
            "Local CSV batch export",
        ],
        "correct_index": 0,
        "explanation": (
            "Provisioned Throughput Units (PTUs) allocate dedicated capacity for predictable latency and "
            "guaranteed throughput at enterprise scale. Standard pay-per-token is great for spiky or low/medium "
            "workloads but shares capacity pools."
        ),
    },
    {
        "id": "q-09",
        "domain_id": "domain-1",
        "module_id": "m1-models-config",
        "topic": "Model Selection by Capability",
        "question": (
            "Your team wants to build semantic search over 50,000 internal engineering runbooks so that a "
            "generative model can retrieve relevant passages before answering questions (RAG). Which type of "
            "AI model must you deploy to convert those runbooks into searchable vectors?"
        ),
        "options": [
            "An image-generation model",
            "A text-to-speech synthesis model",
            "An embeddings model",
            "An object detection model",
        ],
        "correct_index": 2,
        "explanation": (
            "An embeddings model converts text chunks and user queries into dense numerical vectors so a "
            "vector index (such as Azure AI Search) can retrieve semantically similar passages for RAG."
        ),
    },
    {
        "id": "q-10",
        "domain_id": "domain-1",
        "module_id": "m1-ai-workloads",
        "topic": "Text Analysis Techniques",
        "question": (
            "A product team analyzes 10,000 customer reviews and wants to automatically determine whether "
            "customers feel positive or negative specifically about 'battery life' versus 'screen brightness', "
            "while also pulling out mentions of competitor brand names. Which two text analysis techniques apply?"
        ),
        "options": [
            "Sentiment analysis (with opinion mining) and Entity recognition (NER)",
            "Speech synthesis and Optical Character Recognition (OCR)",
            "Image classification and Abstractive summarization",
            "Object detection and Speech translation",
        ],
        "correct_index": 0,
        "explanation": (
            "Sentiment analysis with opinion mining evaluates positive/negative polarity tied to specific aspects "
            "like 'battery life', and Named Entity Recognition (NER) identifies entities such as competitor organizations/products."
        ),
    },
    {
        "id": "q-11",
        "domain_id": "domain-1",
        "module_id": "m1-ai-workloads",
        "topic": "Text Summarization",
        "question": (
            "A legal compliance team wants an automated summary of lengthy regulatory filings, but auditors "
            "require that every sentence in the summary appear word-for-word from the original document. "
            "Which summarization approach should they select?"
        ),
        "options": [
            "Abstractive summarization",
            "Extractive summarization",
            "Key phrase extraction",
            "Language detection",
        ],
        "correct_index": 1,
        "explanation": (
            "Extractive summarization selects verbatim sentences from the source text, preserving exact wording. "
            "Abstractive summarization paraphrases and generates new sentences."
        ),
    },
    {
        "id": "q-12",
        "domain_id": "domain-1",
        "module_id": "m1-ai-workloads",
        "topic": "Speech Workloads",
        "question": (
            "A museum mobile guide wants to read exhibit descriptions aloud in natural-sounding English, "
            "Spanish, and Japanese voices, while allowing curators to adjust pauses and pronunciation of "
            "artists' names. Which capability meets this requirement?"
        ),
        "options": [
            "Speech recognition (STT)",
            "Speech synthesis (TTS) with SSML",
            "Named Entity Recognition",
            "Content Understanding video chaptering",
        ],
        "correct_index": 1,
        "explanation": (
            "Speech synthesis (Text-to-Speech / TTS) converts written descriptions into lifelike neural speech, "
            "and Speech Synthesis Markup Language (SSML) provides fine-grained control over pauses, pitch, and pronunciation."
        ),
    },
    {
        "id": "q-13",
        "domain_id": "domain-1",
        "module_id": "m1-ai-workloads",
        "topic": "Generative vs. Agentic AI",
        "question": (
            "Which scenario is the clearest example of an Agentic AI workload rather than a simple single-turn "
            "generative text prompt?"
        ),
        "options": [
            "Translating a static product description from French to German.",
            "Generating three subject lines for a marketing email.",
            "Receiving a customer's return request, querying the order database via a tool, checking return policy knowledge, issuing a refund ticket, and emailing confirmation.",
            "Counting the number of words in a PDF document.",
        ],
        "correct_index": 2,
        "explanation": (
            "Agentic AI systems combine a foundation model with instructions, grounding knowledge, and callable "
            "tools to plan and execute multi-step actions across external systems toward a goal."
        ),
    },
    # =========================================================================
    # DOMAIN 2: Implement AI solutions by using Microsoft Foundry (17 questions = 56.7%)
    # =========================================================================
    {
        "id": "q-14",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "topic": "Microsoft Foundry Architecture",
        "question": (
            "In Microsoft Foundry, your team is starting a new customer-support prototype and wants an isolated "
            "development workspace to organize its deployed models, agents, evaluations, and data connections "
            "under your organization's existing Azure AI service boundary. What should you create?"
        ),
        "options": [
            "A Microsoft Foundry Project inside the Foundry Resource",
            "A new Azure subscription for every prompt",
            "An Azure Virtual Machine scale set",
            "A static HTML file in Azure DNS",
        ],
        "correct_index": 0,
        "explanation": (
            "A Microsoft Foundry Project acts as the collaborative workspace for a specific AI solution's assets "
            "(models, agents, connections, evaluations), while the underlying Foundry Resource provides the Azure service boundary."
        ),
    },
    {
        "id": "q-15",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "topic": "Effective Prompt Engineering",
        "question": (
            "You are building a lightweight Foundry chat client for travel expense policy Q&A. You want the "
            "model to always respond in bullet points, refuse non-work questions, and cite section numbers "
            "regardless of what the employee types. Where should you place these rules?"
        ),
        "options": [
            "In the `system` message (system prompt)",
            "In the HTTP `User-Agent` header",
            "Inside the `max_tokens` integer parameter",
            "Only in the assistant's final response",
        ],
        "correct_index": 0,
        "explanation": (
            "The `system` prompt establishes persistent role, tone, safety/scope boundaries, and formatting rules "
            "that steer how the model handles every `user` prompt."
        ),
    },
    {
        "id": "q-16",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "topic": "Foundry SDK Authentication",
        "question": (
            "You are writing a Python chat client using `AIProjectClient` from `azure.ai.projects`. "
            "Your security team prohibits committing API keys into source code. What is the recommended "
            "authentication pattern in Microsoft Foundry?"
        ),
        "options": [
            "Hardcode the key in a base64 string inside `main.py`.",
            "Authenticate with Microsoft Entra ID using `DefaultAzureCredential` from `azure.identity`.",
            "Disable authentication on the Foundry endpoint.",
            "Pass the admin password as a URL query parameter.",
        ],
        "correct_index": 1,
        "explanation": (
            "Using Microsoft Entra ID via `DefaultAzureCredential` supports Managed Identity in Azure and "
            "Azure CLI / developer sign-in locally without ever storing static secrets in code."
        ),
    },
    {
        "id": "q-17",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "topic": "Single-Agent Solutions in Foundry",
        "question": (
            "You create a single-agent solution in the Microsoft Foundry portal that needs to answer employee "
            "IT questions grounded in 20 internal PDF troubleshooting manuals and run Python calculations on "
            "uploaded CSV logs. Which capabilities should you attach to the agent?"
        ),
        "options": [
            "File Search (knowledge) and Code Interpreter (tool)",
            "Speech Synthesizer and Image Classification",
            "Azure DNS and Load Balancer",
            "Only a higher `temperature` setting",
        ],
        "correct_index": 0,
        "explanation": (
            "Foundry Agents support built-in grounding and tools: File Search indexes and retrieves from your "
            "PDF knowledge base, and Code Interpreter executes Python safely for CSV analysis and calculations."
        ),
    },
    {
        "id": "q-18",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "topic": "Foundry Agent Client Lifecycle",
        "question": (
            "In a Python client application calling a Microsoft Foundry Agent, what is the purpose of a `Thread`?"
        ),
        "options": [
            "It allocates a dedicated GPU node in Azure Compute.",
            "It maintains the conversation state and ordered sequence of user and agent messages across turns.",
            "It compresses PDF files before uploading them to Azure Blob Storage.",
            "It replaces Microsoft Entra ID role assignments.",
        ],
        "correct_index": 1,
        "explanation": (
            "A Foundry Agent Thread stores the persistent conversation session (messages exchanged between the "
            "user and the agent) so the agent retains context across multiple turns."
        ),
    },
    {
        "id": "q-19",
        "domain_id": "domain-2",
        "module_id": "m2-foundry-genai-agents",
        "topic": "Foundry Chat Client Context",
        "question": (
            "A developer notices their lightweight chat client forgets what the user said in the previous turn "
            "when calling the stateless Chat Completions API. How should they fix this?"
        ),
        "options": [
            "Increase `temperature` to 1.0.",
            "Append prior `user` and `assistant` turns to the `messages` list sent on each request.",
            "Switch from Python to Bash.",
            "Remove the `system` prompt completely.",
        ],
        "correct_index": 1,
        "explanation": (
            "The standard Chat Completions API is stateless; multi-turn memory is maintained by passing the "
            "accumulated conversation history (`system`, `user`, `assistant` messages) with each request."
        ),
    },
    {
        "id": "q-20",
        "domain_id": "domain-2",
        "module_id": "m2-text-speech",
        "topic": "Text Analysis Client App",
        "question": (
            "You are building a Python app to triage incoming support tickets by extracting the main topics, "
            "identifying customer names/emails for PII redaction, and scoring customer frustration. Which "
            "methods on `TextAnalyticsClient` should you call?"
        ),
        "options": [
            "`extract_key_phrases`, `recognize_pii_entities`, and `analyze_sentiment`",
            "`generate_images`, `detect_objects`, and `speak_text_async`",
            "`create_thread`, `deploy_model`, and `extract_video_frames`",
            "`recognize_once_async` and `get_openai_client`",
        ],
        "correct_index": 0,
        "explanation": (
            "`TextAnalyticsClient` provides `extract_key_phrases` for main topics, `recognize_pii_entities` "
            "for sensitive entity detection/redaction, and `analyze_sentiment` for customer polarity scoring."
        ),
    },
    {
        "id": "q-21",
        "domain_id": "domain-2",
        "module_id": "m2-text-speech",
        "topic": "Spoken Prompts with Multimodal Models",
        "question": (
            "A field-service app lets technicians hold a button, speak a complex troubleshooting question with "
            "background noise, and receive a reasoned repair checklist directly from a single model endpoint "
            "in Microsoft Foundry. Which approach matches this AI-901 pattern?"
        ),
        "options": [
            "Send the spoken audio clip to a deployed audio-capable multimodal model in Microsoft Foundry.",
            "Convert the audio clip to a JPEG image and run OCR.",
            "Use `extract_key_phrases` directly on raw WAV bytes.",
            "Use an embeddings model to generate spoken audio.",
        ],
        "correct_index": 0,
        "explanation": (
            "AI-901 specifically covers responding to spoken prompts using a deployed multimodal model in "
            "Microsoft Foundry, which natively accepts audio input and generates reasoned responses."
        ),
    },
    {
        "id": "q-22",
        "domain_id": "domain-2",
        "module_id": "m2-text-speech",
        "topic": "Azure Speech in Foundry Tools",
        "question": (
            "In a Python application using `azure.cognitiveservices.speech`, which two configuration inputs "
            "are required to initialize `SpeechConfig` with key-based authentication?"
        ),
        "options": [
            "A Foundry Agent ID and a Thread ID",
            "A Speech resource subscription key and Azure region (or resource endpoint)",
            "A GitHub personal access token and model temperature",
            "An image URL and `max_tokens`",
        ],
        "correct_index": 1,
        "explanation": (
            "`speechsdk.SpeechConfig(subscription=key, region=region)` (or `endpoint=endpoint`) configures "
            "authentication and routing for `SpeechRecognizer` and `SpeechSynthesizer`."
        ),
    },
    {
        "id": "q-23",
        "domain_id": "domain-2",
        "module_id": "m2-vision-imagegen",
        "topic": "Interpreting Visual Inputs in Prompts",
        "question": (
            "You are sending a photo of an electrical panel to a deployed multimodal model in Microsoft Foundry "
            "to inspect whether any breaker switches are tripped. How must the `user` message `content` be structured?"
        ),
        "options": [
            "As a plain string containing only the local file path `C:\\panel.jpg`.",
            "As a list of content parts containing a `text` prompt and an `image_url` (HTTPS URL or base64 data URI).",
            "As a CSV string inside the `system` role.",
            "As an SSML XML document.",
        ],
        "correct_index": 1,
        "explanation": (
            "Multimodal Foundry chat models expect `content` to be an array of typed items — a `text` instruction "
            "paired with an `image_url` object referencing a reachable URL or base64-encoded data URI."
        ),
    },
    {
        "id": "q-24",
        "domain_id": "domain-2",
        "module_id": "m2-vision-imagegen",
        "topic": "Generative Image Creation",
        "question": (
            "A marketing team uses a Microsoft Foundry image-generation model to create campaign banners from "
            "text prompts. Which practice best aligns with both prompt quality and Responsible AI?"
        ),
        "options": [
            "Disable all content filters so prompts are never blocked.",
            "Specify subject, style, composition, and lighting clearly in the prompt while keeping Content Safety filters enabled and disclosing AI-generated media.",
            "Set `temperature` to 0 on an embeddings model.",
            "Embed customer passwords inside the image prompt for watermarking.",
        ],
        "correct_index": 1,
        "explanation": (
            "Detailed visual prompts (subject, style, lighting, framing) produce higher-quality generations, "
            "while Content Safety filters and transparent disclosure satisfy Reliability & Safety and Transparency."
        ),
    },
    {
        "id": "q-25",
        "domain_id": "domain-2",
        "module_id": "m2-vision-imagegen",
        "topic": "Choosing Vision Capabilities",
        "question": (
            "A manufacturing quality-assurance app needs to count defective circuit boards on a fast-moving "
            "conveyor belt and draw exact rectangular coordinates around every missing capacitor. Which computer "
            "vision capability is designed for this?"
        ),
        "options": [
            "Object detection",
            "Image generation",
            "Abstractive summarization",
            "Speech synthesis",
        ],
        "correct_index": 0,
        "explanation": (
            "Object detection identifies multiple items in an image and returns exact bounding-box coordinates "
            "and class labels for each detected object."
        ),
    },
    {
        "id": "q-26",
        "domain_id": "domain-2",
        "module_id": "m2-content-understanding",
        "topic": "Azure Content Understanding — Documents & Forms",
        "question": (
            "An accounts-payable team receives thousands of PDF invoices in varying vendor layouts and needs "
            "to populate an ERP database with normalized `VendorName`, `InvoiceDate`, `LineItems`, and `TotalAmount` "
            "JSON fields plus confidence scores. Which Foundry tool is purpose-built for this?"
        ),
        "options": [
            "Azure Content Understanding in Foundry Tools",
            "Azure Speech Synthesizer",
            "Image-generation models",
            "Language Detection only",
        ],
        "correct_index": 0,
        "explanation": (
            "Azure Content Understanding in Foundry Tools extracts schema-defined structured JSON fields, "
            "tables, and confidence scores from unstructured documents and forms (as well as images, audio, and video)."
        ),
    },
    {
        "id": "q-27",
        "domain_id": "domain-2",
        "module_id": "m2-content-understanding",
        "topic": "Azure Content Understanding — Schema Methods",
        "question": (
            "While configuring a custom Azure Content Understanding analyzer for insurance claim forms, you "
            "define three fields: `PolicyNumber` (copied verbatim), `ClaimCategory` (must be one of Auto, Home, "
            "or Health), and `AdjusterSummary` (a 2-sentence overview). Which field methods match those three fields?"
        ),
        "options": [
            "`extract`, `classify`, and `generate`",
            "`synthesize`, `translate`, and `render`",
            "`tokenize`, `embed`, and `fine-tune`",
            "`detect`, `crop`, and `blur`",
        ],
        "correct_index": 0,
        "explanation": (
            "Azure Content Understanding schemas support three methods: `extract` pulls verbatim source values, "
            "`classify` assigns a predefined category label, and `generate` synthesizes new summary/inferred text."
        ),
    },
    {
        "id": "q-28",
        "domain_id": "domain-2",
        "module_id": "m2-content-understanding",
        "topic": "Azure Content Understanding — Audio & Video",
        "question": (
            "A contact center records customer support calls and wants a single automated pipeline that "
            "produces speaker-separated transcripts, identifies the call reason, extracts promised follow-up "
            "actions, and flags escalation risk as structured JSON. Which service should they use?"
        ),
        "options": [
            "Azure Content Understanding (audio analyzer) in Foundry Tools",
            "An image-generation model",
            "Optical Character Recognition (OCR)",
            "Object detection",
        ],
        "correct_index": 0,
        "explanation": (
            "Azure Content Understanding supports audio analyzers that combine transcription, speaker diarization, "
            "and schema-driven field extraction (call reason, follow-up actions, sentiment/escalation flags) in one JSON output."
        ),
    },
    {
        "id": "q-29",
        "domain_id": "domain-2",
        "module_id": "m2-content-understanding",
        "topic": "Azure Content Understanding — Video Extraction",
        "question": (
            "A media archive team needs to index 500 training videos by splitting each video into topic segments "
            "with start/end timestamps, extracting key frames, and generating structured JSON metadata for search. "
            "Which capability of Azure Content Understanding handles this?"
        ),
        "options": [
            "Video analysis with segmentation, key-frame extraction, and custom schema fields",
            "Text-to-Speech SSML markup",
            "Plain keyword counting on the filename",
            "Standard pay-per-token chat without media input",
        ],
        "correct_index": 0,
        "explanation": (
            "Azure Content Understanding video analyzers segment videos into timestamped scenes/chapters, "
            "capture representative key frames, and populate schema-defined JSON fields for downstream indexing."
        ),
    },
    {
        "id": "q-30",
        "domain_id": "domain-2",
        "module_id": "m2-content-understanding",
        "topic": "Azure Content Understanding — Human-in-the-Loop",
        "question": (
            "After deploying a Content Understanding extraction app for loan applications, some scanned forms "
            "have smudged handwriting. How should the application use Content Understanding's response metadata "
            "to maintain Reliability & Safety?"
        ),
        "options": [
            "Ignore confidence scores and write all extracted values straight into production ledgers.",
            "Check each extracted field's confidence score and route records below a threshold to a human reviewer with source grounding coordinates.",
            "Raise the model's `temperature` to 2.0 until numbers look plausible.",
            "Delete any document that contains handwriting.",
        ],
        "correct_index": 1,
        "explanation": (
            "Content Understanding returns per-field confidence scores and source grounding regions. Routing "
            "low-confidence extractions to human review combines automation with Responsible AI Reliability & Safety."
        ),
    },
]

SANDBOX_SAMPLES: Dict[str, Any] = {
    "text_samples": [
        {
            "id": "review-positive",
            "label": "Customer Feedback (Mixed Sentiment)",
            "text": (
                "Contoso Retail migrated our support portal to Microsoft Foundry last month in Seattle. "
                "The new single-agent troubleshooting flow cut average resolution time by 42%, and the team "
                "loves the accuracy of grounded answers. However, initial setup of private endpoints took "
                "longer than expected and invoice PDF parsing struggled with faded thermal receipts."
            ),
        },
        {
            "id": "incident-report",
            "label": "Operations Incident Note",
            "text": (
                "On November 14, 2026, Warehouse 7 in Chicago reported three delayed shipments after the "
                "barcode scanner failed to read damp labels. Supervisor Elena Morales contacted Northwind "
                "Logistics at elena.morales@contoso.example and requested an immediate vision OCR fallback."
            ),
        },
    ],
    "content_samples": {
        "document": {
            "label": "Invoice PDF (Document / Form)",
            "schema_fields": [
                "VendorName",
                "InvoiceNumber",
                "InvoiceDate",
                "TotalAmount",
                "PaymentTerms",
                "Category",
            ],
            "content": (
                "INVOICE #INV-2026-8841\n"
                "Vendor: Fabrikam Cloud Components Ltd.\n"
                "Date: 2026-11-12\n"
                "Bill To: Contoso AI Engineering, Redmond WA\n"
                "Line Items:\n"
                "  1. Azure Edge Sensor Kit x 4 — $1,200.00\n"
                "  2. Thermal Enclosure Mount x 4 — $240.00\n"
                "Subtotal: $1,440.00 | Tax: $145.44 | Total Due: $1,585.44\n"
                "Terms: Net 30 | Notes: Expedited shipping approved by M. Patel."
            ),
        },
        "image": {
            "label": "Retail Product Photo (Image)",
            "schema_fields": [
                "ProductName",
                "SKU",
                "Condition",
                "ShelfStockLevel",
                "PriceTag",
            ],
            "content": (
                "[Image Frame Metadata] Front-facing retail shelf photo showing 'Alpine Smart Thermostat Pro' "
                "(SKU: ALP-9042). Printed shelf tag reads '$189.99 — Energy Star Certified'. "
                "Two boxes remain on shelf, left corner of second box has minor dent."
            ),
        },
        "audio": {
            "label": "Support Call Recording (Audio)",
            "schema_fields": [
                "CallerIntent",
                "Sentiment",
                "OrderReference",
                "ActionItems",
                "EscalationRequired",
            ],
            "content": (
                "[00:00] Agent: Thanks for calling Contoso Cloud Support, how can I help?\n"
                "[00:06] Customer: Hi, my order ORD-77319 arrived missing the power adapter, and our team demo is tomorrow.\n"
                "[00:18] Agent: I'm very sorry about that! I see ORD-77319. I'm dispatching an overnight replacement right now and crediting $25.\n"
                "[00:34] Customer: That's a huge relief, thank you for sorting it out so quickly!"
            ),
        },
        "video": {
            "label": "Product Walkthrough Clip (Video)",
            "schema_fields": [
                "Title",
                "Chapters",
                "KeyTopics",
                "TargetAudience",
                "Summary",
            ],
            "content": (
                "[00:00-00:45] Intro: Presenter opens Microsoft Foundry portal and creates an AI-901 project.\n"
                "[00:45-02:10] Demo: Deploys gpt-4o-mini with temperature 0.2 and tests system prompt guardrails.\n"
                "[02:10-03:30] Agents: Attaches File Search knowledge base and runs a multi-step query.\n"
                "[03:30-04:15] Wrap-up: Reviews Content Safety filters and Responsible AI Transparency Note."
            ),
        },
    },
    "vision_presets": [
        {
            "id": "retail_shelf",
            "label": "Warehouse & Retail Shelf Inspection",
            "default_prompt": "Inspect this shelf for out-of-stock gaps, damaged packaging, and readable price labels.",
        },
        {
            "id": "whiteboard_arch",
            "label": "Hand-Drawn Architecture Whiteboard",
            "default_prompt": "Transcribe the architecture diagram and identify which Microsoft Foundry services map to each box.",
        },
        {
            "id": "safety_floor",
            "label": "Factory Floor Safety Check",
            "default_prompt": "Check for PPE compliance (hard hats, high-vis vests) and flag any walkway obstructions.",
        },
    ],
}
