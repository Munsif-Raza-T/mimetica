from crewai import Agent
from tools.custom_tools import AdvancedPineconeVectorSearchTool, SessionDirectoryReadTool, SessionFileReadTool
from config import config
import streamlit as st

class CollectorAgent:
    """Agent responsible for data collection, cleaning, and vectorization"""
    @staticmethod
    def create_agent():
        # Get current model configuration with validation
        selected_model = config.validate_and_fix_selected_model()
        model_config = config.AVAILABLE_MODELS[selected_model]
        provider = model_config['provider']
        
        # Set up LLM based on provider
        llm = None
        if provider == 'openai':
            from crewai.llm import LLM
            llm = LLM(
                model=f"openai/{selected_model}",
                api_key=config.OPENAI_API_KEY,
                temperature=config.TEMPERATURE
            )
        elif provider == 'anthropic':
            from crewai.llm import LLM
            llm = LLM(
                model=f"anthropic/{selected_model}",
                api_key=config.ANTHROPIC_API_KEY,
                temperature=config.TEMPERATURE
            )
        
        return Agent(
            role="Data Collection and Processing Specialist",
            goal="Efficiently collect, clean, normalize, and vectorize uploaded documents for analysis",
            backstory="""You are an expert data engineer with deep experience in document processing,
            data cleaning, and vector database management. Your role is to ensure that all uploaded
            documents are properly processed, cleaned, and made searchable through vectorization.
            You work with various document types (PDF, Word, CSV, Excel) and ensure data quality
            and consistency across all inputs. You only process documents that have been uploaded
            in the current Streamlit session.""",
            tools=[
                SessionDirectoryReadTool(),
                SessionFileReadTool(),
                AdvancedPineconeVectorSearchTool()
            ],
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE,
            llm=llm
        )

    @staticmethod
    def create_task(documents_info: str):
        from crewai import Task
        return Task(
            description=f"""
Process and vectorize uploaded documents for the MIMÉTICA analysis workflow.

Documents to process:
{documents_info}

Your tasks:
1. Analyze document structure and content quality
2. Clean and normalize text data
3. Extract key information and metadata
4. Create vector embeddings for semantic search
5. Validate data integrity and completeness
6. Generate a comprehensive data processing report

Deliverables:
- Cleaned and structured dataset summary (CSV/JSON format)
- Document processing report with statistics
- Vector database status and search capabilities confirmation
- Data quality assessment and recommendations

Ensure all documents are properly indexed and searchable for subsequent analysis phases.
""",
            expected_output="""
A comprehensive document processing report in markdown format containing:

# Document Processing Report

## Processing Summary
- Total documents processed: [number]
- Document types: [list of file types]
- Processing time: [duration]
- Data quality issues: [summary]

## Data Cleaning and Normalization
- Cleaning steps performed
- Issues encountered and resolutions
- Data normalization approach

## Key Information Extracted
- Metadata summary
- Key topics and entities
- Document relationships

## Vectorization and Searchability
- Vector database status
- Search test results
- Indexing completeness

## Data Quality Assessment
- Data integrity checks
- Completeness and consistency
- Recommendations for improvement

## Appendix
- List of processed files
- Processing logs
""",
            agent=CollectorAgent.create_agent(),
            markdown=True,
            output_file="document_processing_report.md"
        )
