# MIMÉTICA MVP 1.0 — AI-Powered Strategic Decision Support System

## Overview

MIMÉTICA is a modular, agent-based decision-support system that guides organizations through complex strategic initiatives using an AI-powered workflow. It implements the DECIDE methodology (Define → Explore → Create → Implement → Decide/Simulate → Evaluate) through a sequential multi-agent architecture built with CrewAI.

Use it for campaign ROI optimization, digital transformation, customer experience improvement, and new service design—producing clear deliverables, visualizations, and exportable reports (PDF/DOCX).

## What’s New

- Model selection in-app with provider-aware rate limiting (OpenAI and Anthropic)
- Intelligent token batch management and progress stats per phase
- Pinecone-based vector store with session-aware clearing on login/logout
- Code Interpreter tool for safe Python execution during analysis
- Strategic visualization generator with embedded images in reports
- Report exports via ReportLab PDF and DOCX generator

## Architecture

### Frontend
- Streamlit web app with custom CSS and a sidebar
- Password-based auth (default password configurable)
- UI: document upload, workflow progress, interactive charts, results viewer
- File support: PDF, DOC/DOCX, CSV, XLS/XLSX up to 200MB

### Backend
- Multi-agent sequential workflow (CrewAI)
- Structured outputs passed between agents
- Document ingestion → cleaning → chunking → embeddings → Pinecone
- Simulation engine for Monte Carlo scenario analysis

### Workflow Phases
1. Collection (document processing and vectorization)
2. Analysis (multidisciplinary feasibility)
3. Definition (problem statements and objectives)
4. Exploration (context research and risk mapping)
5. Creation (strategic options)
6. Implementation (roadmap planning)
7. Simulation (Monte Carlo)
8. Evaluation (KPI framework)
9. Reporting (comprehensive report generation)

## Key Components

### Agents
- CollectorAgent, DecisionMultidisciplinaryAgent, DefineAgent, ExploreAgent,
  CreateAgent, ImplementAgent, SimulateAgent, EvaluateAgent, ReportAgent

### Custom Tools
- Pinecone Vector Search
- Project Management Planner
- Evaluation Framework Generator
- Markdown Editor
- Monte Carlo Simulator + Results Explainer
- Code Interpreter (safe Python execution)
- Strategic Visualization Generator (risk matrix, ROI projection, timelines, etc.)

### Utilities
- AuthManager (auth + session timeout)
- DocumentProcessor (multi-format ingestion)
- VectorStore (Pinecone + OpenAI embeddings)
- SessionManager (state + logs)
- PDFGenerator (ReportLab) and DocxGenerator
- Image Manager (saves images under `generated_images/<session>`)

## Data Flow
- Upload → validate → process → chunk → embed with OpenAI → store in Pinecone
- Phases consume prior outputs and write structured results to session state
- Visualizations generated and embedded via placeholder mechanism
- Outputs exported to PDF/DOCX and auxiliary Markdown files in workspace

## Dependencies

### Required APIs
- OpenAI API: LLMs + embeddings
- Pinecone: Vector database (serverless index)
- Anthropic API: Optional if selecting Anthropic models in-app
- SERPER API: Optional for web research

### Python Libraries (high level)
- Streamlit, CrewAI, OpenAI, Pinecone
- Pandas, Plotly, NumPy, Matplotlib/Seaborn
- ReportLab (PDF), python-docx (DOCX), python-dotenv

### File System
- `generated_images/` auto-created per session for charts and figures
- Uploaded files are processed in-memory during a session

## Security
- Password-based authentication (default `mimetica2025`, configurable via `APP_PASSWORD`)
- Session timeout (default 1 hour)
- Keys provided via `.env` (local) or Streamlit Cloud Secrets (deployment)

---

## Run it locally on macOS (zsh)

### 1) Prerequisites
- Python 3.10+ recommended
- pip installed
- Git (optional)

Verify Python:
```bash
python3 --version
```

### 2) Clone the repo
- Download or clone this repository to your machine.

### 3) Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4) Install dependencies
```bash
pip install -r requirements.txt
```

### 5) Configure environment variables
Create a `.env` file in the project root:
```env
# Required
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-east-1   # Pinecone region, e.g., us-east-1

# Optional but recommended if you plan to use Anthropic models
ANTHROPIC_API_KEY=your_anthropic_key

# Optional
SERPER_API_KEY=your_serper_key
APP_PASSWORD=mimetica2025
```
Notes:
- The app loads keys automatically via python-dotenv.
- Pinecone runs in serverless mode with `cloud="aws"` and your region.

### 6) Start the app
```bash
streamlit run app.py
```
- The app opens in your browser (default http://localhost:8501).
- To use a different port:
```bash
streamlit run app.py --server.port 8502
```

### 7) First login
- Default password is `mimetica2025` (or your `APP_PASSWORD`).
- Successful login clears the Pinecone collection for a fresh session.

### 8) Use the app
- Enter project info and upload documents (PDF, DOC/DOCX, CSV, XLS/XLSX).
- Click “Process Documents” to vectorize into Pinecone.
- Pick the model in the sidebar (OpenAI or Anthropic), then click “Update Model”.
- Run the full DECIDE workflow or view progress per phase.
- See results, charts, and download PDF/DOCX reports.

### 9) Stop the app
- Press Ctrl+C in the terminal running Streamlit.

---

## Deployment (Streamlit Cloud)
1) Push your code to GitHub (ensure `.env` is in `.gitignore`).
2) In Streamlit Cloud, create a new app from this repo.
3) Add Secrets (use top-level keys; do NOT nest under sections):
```toml
OPENAI_API_KEY = "your_openai_key"
ANTHROPIC_API_KEY = "your_anthropic_key"  # optional
PINECONE_API_KEY = "your_pinecone_key"
PINECONE_ENVIRONMENT = "us-east-1"        # your Pinecone region
SERPER_API_KEY = "your_serper_key"        # optional
APP_PASSWORD = "your_password"
```
4) Deploy. The app will pick up secrets via `st.secrets`.

---

## Troubleshooting
- Pinecone not configured: Ensure `PINECONE_API_KEY` and `PINECONE_ENVIRONMENT` are set.
- OpenAI auth error: Set `OPENAI_API_KEY` in `.env` or Streamlit Secrets.
- Anthropic models: Require `ANTHROPIC_API_KEY` and selecting an Anthropic model.
- “Vector store initialization failed”: Check network and your Pinecone region value.
- PDF export issues: ReportLab is bundled; if fonts/images don’t render, retry export.
- Large files: Max 200MB; very large PDFs may process slowly.
- Port busy: Use `--server.port` to run on a different port.

---

## Notes for Maintainers
- Default model: `gpt-4o-mini` (configurable from the sidebar)
- Embeddings via OpenAI (current model in code: `text-embedding-ada-002`)
- Vector index name: `mimetica` (cleared on login/logout via app controls)
- Images for visualizations saved under `generated_images/session_<timestamp>/`
- Exports: Comprehensive PDF (ReportLab) and DOCX are generated from phase outputs

Happy strategizing with MIMÉTICA!