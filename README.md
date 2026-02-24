# 📊 Financial Document Analyzer - AI Intelligence Engine

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.3-009688.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-0.130.0-FF4B4B.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red.svg)

## 🚀 Project Overview
A production-ready, asynchronous Financial Document Analysis system built to process dense corporate reports, financial statements, and investment documents. Powered by **FastAPI** and **CrewAI**, this intelligence engine orchestrates a team of specialized AI agents (Verifier, Financial Analyst, Risk Assessor, and Investment Advisor) to extract hard data, identify operational risks, and synthesize conservative, data-backed investment insights.

This project was engineered with the philosophy that document auditing engines must be deterministic. AI hallucinations in financial analysis are unacceptable, so the multi-agent orchestration is strictly engineered for SEC-style compliance and factual extraction.

---

## 🎯 Debug Mission Accomplished

This project was originally provided with severe deterministic bugs and hallucination-prone prompts. The architecture has been completely refactored to professional standards.

### 1. Squashed Deterministic Bugs (The Crashers)
* **LLM Instantiation:** Fixed a fatal `llm = llm` circular reference. The LLM is now properly initialized with `temperature=0.0` to enforce deterministic, factual outputs.
* **Tool Registration:** Refactored standard class methods into standalone functions using the correct `@tool` decorator, allowing the CrewAI agents to actually utilize them.
* **Dynamic File Routing:** Replaced hardcoded `data/sample.pdf` references with dynamic, UUID-based file handling to support concurrent API uploads.
* **Pipeline Orchestration:** Wired up the orphaned agents in `main.py` so the full pipeline executes in sequence. Removed `pypdf` import errors by integrating a robust document loader.

### 2. Fixed Inefficient Prompts (The Hallucination Engine)
* **Persona Engineering:** Overhauled all agent `roles`, `goals`, and `backstories`. Removed active instructions to hallucinate (e.g., requests for "fake URLs" and "made-up connections"). Agents now act as strict compliance officers and quantitative strategists.
* **Context Piping:** Implemented CrewAI `context` arrays. Downstream agents (Risk Assessor, Investment Advisor) are now programmatically forced to base their analysis *strictly* on the hard numbers extracted by the upstream agents.

---

## 🌟 Bonus Features Implemented

To make this system production-ready and provide a seamless Developer Experience (DX), both bonus requirements were implemented natively:

1. **Queue Worker Model (Asynchronous Execution):**
   FastAPI's synchronous threads would normally time out waiting for CrewAI to process a dense PDF. This system implements an async queue using FastAPI's `BackgroundTasks` to handle concurrent requests. The API instantly returns a `task_id` upon upload, offloading the LLM execution to a non-blocking background worker.

2. **Database Integration (State Tracking):**
   Instead of relying on volatile memory, the system uses a lightweight, zero-config **SQLite + SQLAlchemy** database for storing analysis results and user data. Every uploaded document is assigned a UUID and tracked in an `analyses` table, allowing users to reliably poll the state of their task (`QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED`).

---

## 💻 Setup & Installation

### 1. Clone & Install Dependencies
Ensure you have Python 3.10+ installed.
```bash
git clone <your-repo-url>
cd financial-document-analyzer
pip install -r requirements.txt
pip install pypdf sqlalchemy
```

### 2. Environment Variables
Create a `.env` file in the root directory and add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```
*(Note: Ensure your OpenAI account has sufficient quota/billing enabled, or swap the LLM engine to Google Gemini in `agents.py` if preferred).*

### 3. Run the Server
Launch the FastAPI application:
```bash
python main.py
```
The server will start at `http://localhost:8000`. You can access the interactive Swagger UI at `http://localhost:8000/docs`.

---

## 📡 API Documentation

### `POST /analyze`
Uploads a financial PDF and queues it for asynchronous multi-agent analysis.
* **Payload:** `multipart/form-data`
  * `file`: The PDF document to analyze. (e.g., `TSLA-Q2-2025-Update.pdf`)
  * `query`: (Optional) The specific financial question to answer.
* **Response:**
  ```json
  {
      "status": "success",
      "message": "Document queued for analysis.",
      "task_id": "72750f64-0ba6-4892-838d-3bd8b9e2cbc3",
      "check_status_url": "/status/72750f64-0ba6-4892-838d-3bd8b9e2cbc3"
  }
  ```

### `GET /status/{task_id}`
Retrieves the current status and final markdown results of the analysis.
* **Response (Processing):**
  ```json
  {
      "task_id": "72750f64-0ba6-4892-838d-3bd8b9e2cbc3",
      "filename": "TSLA-Q2-2025-Update.pdf",
      "status": "PROCESSING",
      "result": "Analysis in progress..."
  }
  ```
* **Response (Completed):** Returns the exact task details along with the full, factual Markdown report synthesized by the AI Crew in the `result` field.
* **Response (Failed):** Safely catches LLM quota errors or parsing failures and returns the exact error trace in the `result` field without crashing the server.

---
*Built for precision, compliance, and scalability.*
