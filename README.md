
# MIMÉTICA MVP 1.0 - AI-Powered Strategic Decision Support System

## Overview

MIMÉTICA is a modular, agent-based decision-support system that guides organizations through complex strategic initiatives using an AI-powered workflow. The system implements the DECIDE methodology (Define → Explore → Create → Implement → Decide/Simulate → Evaluate) through a sequential multi-agent architecture built with CrewAI.

The application serves as a comprehensive strategic decision-making tool for various business scenarios including campaign ROI optimization, digital transformation, customer experience improvement, and new service design.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit-based web application
- **Authentication**: Password-based authentication with session management
- **UI Components**: Document upload interface, progress tracking dashboard, interactive charts, and report rendering
- **Styling**: Custom CSS with gradient headers and card-based layouts
- **File Support**: PDF, Word documents, CSV, and Excel files up to 200MB

### Backend Architecture
- **Multi-Agent System**: CrewAI-powered sequential agent workflow
- **Agent Communication**: Structured output passing between agents in Markdown/JSON format
- **Data Processing**: Document ingestion, cleaning, normalization, and vectorization pipeline
- **Simulation Engine**: Monte Carlo simulation capabilities for scenario analysis

### Core Workflow Structure
The system follows a strict sequential execution pattern:
1. **Collection**: Document processing and vectorization
2. **Analysis**: Multidisciplinary feasibility assessment
3. **Definition**: Problem statement and objective setting
4. **Exploration**: Contextual research and risk mapping
5. **Creation**: Strategic option development
6. **Implementation**: Detailed roadmap planning
7. **Simulation**: Monte Carlo scenario analysis
8. **Evaluation**: KPI framework and monitoring setup
9. **Reporting**: Comprehensive final report generation

## Key Components

### Agent System
- **CollectorAgent**: Handles document processing, cleaning, and vectorization
- **DecisionMultidisciplinaryAgent**: Conducts integrated feasibility analysis across multiple domains
- **DefineAgent**: Creates clear problem statements and SMART objectives
- **ExploreAgent**: Performs contextual research and risk assessment
- **CreateAgent**: Develops strategic intervention options
- **ImplementAgent**: Creates detailed implementation roadmaps
- **SimulateAgent**: Runs Monte Carlo simulations and scenario analysis
- **EvaluateAgent**: Defines KPIs and success metrics
- **ReportAgent**: Consolidates all outputs into final strategic reports

### Custom Tools
- **PineconeVectorSearchTool**: Semantic search across processed documents
- **ProjectManagementTool**: Project planning and timeline generation
- **EvaluationFrameworkTool**: KPI development and measurement frameworks  
- **MarkdownEditorTool**: Report formatting and documentation
- **MonteCarloSimulationTool**: Statistical modeling and scenario simulation

### Utility Modules
- **AuthManager**: User authentication and session security
- **DocumentProcessor**: Multi-format document ingestion and processing
- **VectorStore**: Pinecone integration for semantic search capabilities
- **SessionManager**: Workflow state management and progress tracking

## Data Flow

1. **Input Processing**: Users upload documents which are validated, processed, and vectorized
2. **Sequential Analysis**: Each agent processes outputs from the previous agent in the workflow
3. **Knowledge Persistence**: All intermediate results are stored in session state and vector database
4. **Output Generation**: Final reports are generated in both PDF and Markdown formats
5. **Progress Tracking**: Real-time workflow status updates and logging throughout execution

## External Dependencies

### Required APIs
- **OpenAI API**: For language model capabilities and text embeddings
- **Qdrant**: Vector database for semantic search and document retrieval
- **SERPER API**: Optional web search capabilities

### Python Libraries
- **CrewAI**: Multi-agent orchestration framework
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive visualization and charting
- **PyPDF2**: PDF document processing
- **python-docx**: Word document processing
- **Qdrant Client**: Vector database connectivity
- **OpenAI**: API client for language model access

### File System Requirements
- **Data Directory**: For storing processed documents
- **Outputs Directory**: For generated reports and results
- **Temp Directory**: For temporary file processing

## Deployment Strategy

### Environment Configuration
- Configuration managed through environment variables and config.py
- Support for local development and cloud deployment scenarios
- Configurable vector database endpoints (local Qdrant or cloud service)

### Security Considerations
- Password-based authentication with configurable credentials
- Session timeout management (default 1 hour)
- File upload validation and size limits
- Secure API key management through environment variables

### Scalability Design
- Modular agent architecture allows for easy extension
- Vector database provides efficient document retrieval at scale
- Session-based state management supports concurrent users
- Configurable simulation parameters for performance tuning

### Error Handling
- Comprehensive validation for file uploads and API responses
- Graceful degradation when external services are unavailable
- Detailed logging and error reporting throughout the workflow
- Session recovery capabilities for interrupted workflows

The system is designed to be both powerful for complex strategic analysis and accessible for business users, with a focus on providing actionable insights through structured multi-agent collaboration.

# MIMÉTICA Application - Step-by-Step Run Guide

## 1. Prerequisites

- **Python**: Version 3.8 or higher. Check with:
  ```powershell
  python --version
  ```
- **pip**: Python package manager should be available.
- **Git** (optional): For version control.

## 2. Clone or Download the Project

Clone the repository or download the project files to your local machine.

## 3. Set Up a Virtual Environment (Recommended)

Open PowerShell in your project directory (`e:\Project\MIMÉTICA`) and run:

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

## 4. Install Dependencies

Install all required Python packages using the provided `requirements.txt`:

```powershell
pip install -r requirements.txt
```

## 5. Configure Environment Variables

- If your app uses environment variables (it imports `load_dotenv`), create a `.env` file in the project root.
- Add any required variables (see `config.py` or documentation for specifics).

Example `.env`:
```
OPENAI_API_KEY=your_openai_key_here
OTHER_CONFIG=your_value
```

## 6. Run the Application

Start the Streamlit app with:

```powershell
streamlit run app.py
```

- This will launch the app in your default web browser.
- If not, copy the provided local URL (e.g., `http://localhost:8501`) and open it in your browser.

## 7. Using the Application

1. **Login**: If authentication is enabled, log in with your credentials.
2. **Project Setup**: Enter project information and upload documents (PDF, Word, CSV, Excel).
3. **Process Documents**: Click "Process Documents" to analyze and vectorize uploads.
4. **Start Workflow**: Once documents are processed, click "Start DECIDE Workflow".
5. **Navigate Phases**: Use the sidebar to track progress and move between workflow phases.
6. **View Results**: After completion, view and download results and reports.

## 8. Stopping the Application

- To stop the app, return to the PowerShell window and press `Ctrl+C`.

## 9. Troubleshooting

- **Missing Packages**: If you get import errors, ensure all dependencies are installed.
- **Port in Use**: If port 8501 is busy, Streamlit will suggest an alternative or you can specify one:
  ```powershell
  streamlit run app.py --server.port 8502
  ```
- **Environment Variables**: Double-check your `.env` file for required keys.

## 10. Optional: Updating Dependencies

If you add new packages, update `requirements.txt`:

```powershell
pip freeze > requirements.txt
```

---

You are now ready to use the MIMÉTICA application! For more help, check the code comments or project documentation.