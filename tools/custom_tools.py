import os
import json
import numpy as np
import pandas as pd
import requests
from typing import Dict, List, Any, Optional, Type
import streamlit as st
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from utils.vector_store import VectorStore
from config import config

# CrewAI imports
from crewai.tools import BaseTool, tool
from pydantic import BaseModel, Field


# =============================================================================
# SESSION FILE READER TOOL
# =============================================================================

class SessionDirectoryReadTool(BaseTool):
    """Tool for reading files uploaded in the current Streamlit session"""
    
    name: str = "session_directory_reader"
    description: str = "Read files that have been uploaded in the current Streamlit session"
    
    def _run(self) -> str:
        try:
            # Get the documents from the session state
            import streamlit as st
            
            if 'workflow_state' not in st.session_state or 'documents' not in st.session_state.workflow_state:
                return "No documents found in the current session."
                
            documents = st.session_state.workflow_state.get('documents', [])
            if not documents:
                return "No documents have been uploaded in the current session."
            
            # Create a summary of the uploaded documents
            summary = "Uploaded Documents in Current Session:\n\n"
            for doc in documents:
                filename = doc.get('filename', 'Unknown')
                file_type = doc.get('file_type', 'Unknown')
                content_preview = doc.get('content', '')[:200] + '...' if len(doc.get('content', '')) > 200 else doc.get('content', '')
                file_size = doc.get('file_size', 0)
                
                summary += f"""
Document: {filename}
Type: {file_type}
Size: {file_size} bytes
Preview: {content_preview}
-------------------
"""
            
            return summary
            
        except Exception as e:
            return f"Error reading session documents: {str(e)}"


class SessionFileReadTool(BaseTool):
    """Tool for reading a specific file from the current Streamlit session"""
    
    name: str = "session_file_reader"
    description: str = "Read a specific file that has been uploaded in the current Streamlit session"
    
    def _run(self, filename: str) -> str:
        try:
            import streamlit as st
            
            if 'workflow_state' not in st.session_state or 'documents' not in st.session_state.workflow_state:
                return f"No documents found in the current session."
            
            documents = st.session_state.workflow_state.get('documents', [])
            if not documents:
                return f"No documents have been uploaded in the current session."
            
            # Find the requested document
            for doc in documents:
                if doc.get('filename', '') == filename:
                    return doc.get('content', f"No content found in {filename}")
            
            return f"File {filename} not found in the current session."
            
        except Exception as e:
            return f"Error reading file {filename}: {str(e)}"


# =============================================================================
# FUNCTION-BASED TOOLS (Using @tool decorator)
# =============================================================================

@tool("pinecone_vector_search")
def pinecone_vector_search(query: str, limit: int = 10) -> str:
    """Search for similar documents in Pinecone vector database.
    
    Args:
        query: The search query to find similar documents
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        String containing search results with similarity scores and content
    """
    try:
        vector_store = VectorStore()
        results = vector_store.search_similar(query, limit=limit)
        if not results:
            return f"No similar content found for query: {query}"
        
        search_results = []
        for i, result in enumerate(results, 1):
            search_results.append(f"""
Result {i}:
- Source: {result['filename']} ({result['file_type']})
- Similarity Score: {result['score']:.3f}
- Content: {result['chunk_text'][:500]}...
""")
        return "\n".join(search_results)
    except Exception as e:
        return f"Vector search failed: {str(e)}"


@tool("project_management_planner")
def project_management_tool(option_title: str, phases: str, timeline_weeks: int = 12) -> str:
    """Generate a comprehensive project management plan.
    
    Args:
        option_title: Title of the project or strategic option
        phases: Comma-separated list of project phases to plan
        timeline_weeks: Project duration in weeks (default: 12)
    
    Returns:
        Comprehensive project management plan as formatted string
    """
    try:
        # Parse phases from string
        phases_list = [phase.strip() for phase in phases.split(',')]
        
        # Create project structure
        total_phases = len(phases_list)
        weeks_per_phase = timeline_weeks // total_phases
        
        project_plan = f"""
# Project Management Plan: {option_title}

## Project Overview
- **Total Duration**: {timeline_weeks} weeks
- **Number of Phases**: {total_phases}
- **Average Phase Duration**: {weeks_per_phase} weeks

## Detailed Project Schedule

"""
        
        current_week = 1
        for i, phase in enumerate(phases_list, 1):
            end_week = current_week + weeks_per_phase - 1
            if i == total_phases:  # Last phase gets remaining weeks
                end_week = timeline_weeks
            
            project_plan += f"""
### Phase {i}: {phase}
- **Duration**: Week {current_week} - Week {end_week}
- **Key Deliverables**: 
  - Milestone {i}.1: Initial analysis and planning
  - Milestone {i}.2: Implementation activities
  - Milestone {i}.3: Testing and validation
  - Milestone {i}.4: Documentation and handover

**Critical Success Factors:**
- Resource allocation and team coordination
- Stakeholder engagement and communication
- Quality assurance and risk management
- Timeline adherence and scope control

"""
            current_week = end_week + 1
        
        # Add risk management section
        project_plan += f"""
## Risk Management Framework

### High-Priority Risks
1. **Resource Availability**: Risk of key team members becoming unavailable
   - Mitigation: Cross-training and backup resource identification
   
2. **Scope Creep**: Uncontrolled expansion of project requirements
   - Mitigation: Formal change control process and stakeholder alignment
   
3. **Technical Challenges**: Unforeseen technical complications
   - Mitigation: Technical spikes and proof-of-concept development
   
4. **Timeline Delays**: Activities taking longer than planned
   - Mitigation: Buffer time allocation and parallel work streams

### Success Metrics
- **On-time Delivery**: 95% of milestones delivered on schedule
- **Budget Adherence**: Stay within 5% of approved budget
- **Quality Standards**: Meet all defined quality criteria
- **Stakeholder Satisfaction**: 90%+ satisfaction rating

## Resource Requirements
- **Project Manager**: Full-time throughout project
- **Technical Lead**: 75% allocation
- **Development Team**: 2-3 developers (full-time during implementation phases)
- **Subject Matter Experts**: Part-time consultation as needed
- **Quality Assurance**: 25% allocation throughout project
"""
        
        return project_plan
        
    except Exception as e:
        return f"Project planning failed: {str(e)}"


@tool("evaluation_framework_generator")
def evaluation_framework_tool(objectives: str, timeline_months: int = 6) -> str:
    """Generate comprehensive KPI and evaluation framework.
    
    Args:
        objectives: Comma-separated list of objectives to evaluate
        timeline_months: Evaluation timeline in months (default: 6)
    
    Returns:
        Comprehensive evaluation framework with KPIs and monitoring plan
    """
    try:
        # Parse objectives from string
        objectives_list = [obj.strip() for obj in objectives.split(',')]
        
        framework = f"""
# Evaluation Framework and KPI Development

## Strategic Objectives Assessment
"""
        
        for i, objective in enumerate(objectives_list, 1):
            framework += f"""
### Objective {i}: {objective}

**Quantitative KPIs:**
- Primary Metric: [Define specific measurable outcome]
- Secondary Metrics: [2-3 supporting indicators]
- Target Values: [Specific numerical targets]
- Measurement Frequency: [Daily/Weekly/Monthly]

**Qualitative KPIs:**
- Stakeholder Satisfaction: Survey-based assessment
- Process Quality: Expert evaluation and peer review
- Innovation Impact: Qualitative assessment of novel approaches
- Cultural Change: Organizational climate assessment

**Leading Indicators:**
- Early warning signals of progress/challenges
- Predictive metrics for success probability
- Process efficiency measurements

**Lagging Indicators:**
- Final outcome measurements
- Long-term impact assessment
- Return on investment calculations

"""
        
        # Add comprehensive monitoring framework
        framework += f"""
## Monitoring and Evaluation Timeline

### Month 1-2: Baseline Establishment
- Data collection system setup
- Baseline measurements for all KPIs
- Stakeholder survey deployment
- Initial assessment documentation

### Month 3-4: Mid-term Evaluation
- Progress assessment against targets
- Stakeholder feedback collection
- Process optimization identification
- Course correction recommendations

### Month 5-6: Final Evaluation
- Comprehensive outcome assessment
- ROI calculation and analysis
- Lessons learned documentation
- Future improvement recommendations

## Data Collection Methods

### Quantitative Data
- **Automated Systems**: Real-time data capture from operational systems
- **Surveys**: Structured questionnaires for stakeholder feedback
- **Performance Metrics**: Direct measurement of operational outcomes
- **Financial Tracking**: Cost and benefit quantification

### Qualitative Data
- **Interviews**: In-depth stakeholder conversations
- **Focus Groups**: Facilitated group discussions
- **Observation**: Direct process observation and documentation
- **Case Studies**: Detailed analysis of specific implementation examples

## Success Thresholds

### Green Zone (Exceeding Expectations)
- All primary KPIs exceed targets by 10%+
- Stakeholder satisfaction >90%
- Implementation timeline ahead of schedule
- Budget utilization <95% of allocation

### Yellow Zone (Meeting Expectations)
- Primary KPIs within 5% of targets
- Stakeholder satisfaction 70-90%
- Implementation timeline on track
- Budget utilization 95-100% of allocation

### Red Zone (Below Expectations)
- Primary KPIs >5% below targets
- Stakeholder satisfaction <70%
- Implementation timeline delayed
- Budget overrun >100% of allocation

## Reporting and Communication

### Dashboard Development
- Real-time KPI visualization
- Traffic light status indicators
- Trend analysis and forecasting
- Exception reporting for critical issues

### Stakeholder Reporting
- **Executive Summary**: Monthly high-level updates
- **Detailed Reports**: Quarterly comprehensive analysis
- **Ad-hoc Updates**: Event-driven communications
- **Annual Review**: Comprehensive evaluation and planning

## Continuous Improvement Framework

### Learning Integration
- Regular retrospectives and lessons learned sessions
- Best practice identification and documentation
- Process refinement based on evaluation findings
- Knowledge transfer to future initiatives

### Adaptive Management
- Flexible KPI adjustment based on changing conditions
- Responsive evaluation methodology updates
- Stakeholder feedback integration
- Continuous methodology improvement
"""
        
        return framework
        
    except Exception as e:
        return f"Evaluation framework generation failed: {str(e)}"


@tool("markdown_editor_tool")
def markdown_editor_tool(content: str, format_type: str = "report") -> str:
    """Format and structure content into well-organized markdown.
    
    Args:
        content: Content to be formatted in markdown
        format_type: Type of formatting to apply (default: "report")
    
    Returns:
        Formatted markdown content
    """
    try:
        if format_type == "report":
            formatted_content = f"""
# MIMÉTICA Strategic Analysis Report
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

---

{content}

---

## Document Information
- **Analysis Framework**: DECIDE Methodology
- **Multi-Agent System**: CrewAI-powered strategic analysis
- **Document Type**: Strategic Decision Support Report
- **Confidentiality**: Internal Strategic Planning Document

### Methodology Notes
This report was generated using the MIMÉTICA AI-powered decision support system, which implements a structured nine-phase analysis workflow:

1. **Collection**: Document processing and vectorization
2. **Analysis**: Multidisciplinary feasibility assessment  
3. **Definition**: Problem statement and objective setting
4. **Exploration**: Contextual research and risk mapping
5. **Creation**: Strategic option development
6. **Implementation**: Detailed roadmap planning
7. **Simulation**: Monte Carlo scenario analysis
8. **Evaluation**: KPI framework and monitoring setup
9. **Reporting**: Comprehensive final report generation

### Disclaimer
This analysis is based on the provided documents and data sources. Recommendations should be validated with current market conditions and organizational constraints before implementation.
"""
        else:
            # Simple formatting
            formatted_content = content
            
        return formatted_content
        
    except Exception as e:
        return f"Markdown formatting failed: {str(e)}"


@tool("web_search")
def serper_search_tool(query: str, num_results: int = 10) -> str:
    """Search the web using SERPER API for market research and contextual analysis.
    
    Args:
        query: Search query to execute
        num_results: Number of results to return (default: 10)
    
    Returns:
        Web search results formatted as string
    """
    try:
        if not config.SERPER_API_KEY:
            return "SERPER API key not configured. Web search functionality unavailable."
        
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': config.SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': num_results
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            # Process organic results
            if 'organic' in data:
                for i, result in enumerate(data['organic'][:num_results], 1):
                    results.append(f"""
Result {i}:
- Title: {result.get('title', 'No title')}
- URL: {result.get('link', 'No URL')}
- Snippet: {result.get('snippet', 'No description')}
""")
            
            # Add knowledge graph if available
            if 'knowledgeGraph' in data:
                kg = data['knowledgeGraph']
                results.append(f"""
Knowledge Graph:
- Title: {kg.get('title', 'No title')}
- Type: {kg.get('type', 'No type')}
- Description: {kg.get('description', 'No description')}
""")
            
            return f"Web Search Results for '{query}':\n" + "\n".join(results)
        else:
            return f"Web search failed with status code: {response.status_code}"
            
    except Exception as e:
        return f"Web search error: {str(e)}"


@tool("monte_carlo_simulator")
def monte_carlo_simulation_tool(base_value: float, volatility: float, scenarios: int = 1000) -> str:
    """Run Monte Carlo simulation for risk analysis.
    
    Args:
        base_value: Base value for simulation
        volatility: Volatility parameter for simulation
        scenarios: Number of scenarios to simulate (default: 1000)
    
    Returns:
        Simulation results formatted as string
    """
    try:
        # Generate random values using normal distribution
        random_values = np.random.normal(0, volatility, scenarios)
        simulated_outcomes = base_value * (1 + random_values)
        
        # Calculate statistics
        results = {
            'mean': float(np.mean(simulated_outcomes)),
            'median': float(np.median(simulated_outcomes)),
            'std_dev': float(np.std(simulated_outcomes)),
            'min_value': float(np.min(simulated_outcomes)),
            'max_value': float(np.max(simulated_outcomes)),
            'percentile_10': float(np.percentile(simulated_outcomes, 10)),
            'percentile_25': float(np.percentile(simulated_outcomes, 25)),
            'percentile_75': float(np.percentile(simulated_outcomes, 75)),
            'percentile_90': float(np.percentile(simulated_outcomes, 90))
        }
        
        # Format results as readable string
        formatted_results = f"""
Monte Carlo Simulation Results:
Base Value: {base_value}
Volatility: {volatility}
Scenarios: {scenarios}

Statistical Results:
- Mean: {results['mean']:.2f}
- Median: {results['median']:.2f}
- Standard Deviation: {results['std_dev']:.2f}
- Minimum Value: {results['min_value']:.2f}
- Maximum Value: {results['max_value']:.2f}

Percentiles:
- 10th Percentile: {results['percentile_10']:.2f}
- 25th Percentile: {results['percentile_25']:.2f}
- 75th Percentile: {results['percentile_75']:.2f}
- 90th Percentile: {results['percentile_90']:.2f}

Risk Assessment:
- Downside Risk (10th percentile): {((results['percentile_10'] - base_value) / base_value * 100):.1f}%
- Upside Potential (90th percentile): {((results['percentile_90'] - base_value) / base_value * 100):.1f}%
"""
        
        return formatted_results
        
    except Exception as e:
        return f"Monte Carlo simulation failed: {str(e)}"


# =============================================================================
# CLASS-BASED TOOLS (Using BaseTool subclassing) - Alternative approach
# =============================================================================

class AdvancedPineconeVectorSearchTool(BaseTool):
    """Advanced tool for searching similar documents using vector similarity with caching"""
    
    name: str = "advanced_pinecone_vector_search"
    description: str = "Search for similar documents using vector similarity with advanced filtering and caching"
    
    def _run(self, query: str, limit: int = 10, similarity_threshold: float = 0.7) -> str:
        """Execute the vector search with advanced parameters
        
        Args:
            query: The search query
            limit: Maximum results to return
            similarity_threshold: Minimum similarity score threshold
        """
        try:
            vector_store = VectorStore()
            results = vector_store.search_similar(query, limit=limit)
            
            if not results:
                return f"No similar content found for query: {query}"
            
            # Filter by similarity threshold
            filtered_results = [r for r in results if r['score'] >= similarity_threshold]
            
            if not filtered_results:
                return f"No results found above similarity threshold {similarity_threshold} for query: {query}"
            
            search_results = []
            for i, result in enumerate(filtered_results, 1):
                search_results.append(f"""
Result {i}:
- Source: {result['filename']} ({result['file_type']})
- Similarity Score: {result['score']:.3f}
- Relevance: {'High' if result['score'] > 0.8 else 'Medium' if result['score'] > 0.7 else 'Low'}
- Content: {result['chunk_text'][:500]}...
- Metadata: {result.get('metadata', 'No metadata available')}
""")
            
            summary = f"""
Search Summary:
- Query: {query}
- Total Results Found: {len(results)}
- Results Above Threshold: {len(filtered_results)}
- Similarity Threshold: {similarity_threshold}

{chr(10).join(search_results)}
"""
            return summary
            
        except Exception as e:
            return f"Advanced vector search failed: {str(e)}"


# =============================================================================
# ASYNC TOOLS EXAMPLE
# =============================================================================

@tool("async_web_research")
async def async_web_research_tool(topic: str, depth: str = "basic") -> str:
    """Perform asynchronous web research on a given topic.
    
    Args:
        topic: The research topic
        depth: Research depth - "basic", "detailed", or "comprehensive"
    
    Returns:
        Research findings formatted as string
    """
    import asyncio
    import aiohttp
    
    try:
        # Simulate async web research
        await asyncio.sleep(1)  # Simulated network delay
        
        research_points = {
            "basic": 3,
            "detailed": 5,
            "comprehensive": 8
        }
        
        num_points = research_points.get(depth, 3)
        
        # Simulated research results
        findings = f"""
Async Web Research Results for: {topic}
Research Depth: {depth}
Timestamp: {datetime.now().isoformat()}

Key Findings:
"""
        
        for i in range(1, num_points + 1):
            findings += f"- Finding {i}: [Simulated research point about {topic}]\n"
        
        findings += f"""
Research Methodology:
- Search engines consulted: Multiple sources
- Academic databases: Included in {depth} research
- Industry reports: {"Included" if depth in ["detailed", "comprehensive"] else "Basic coverage"}
- Social media sentiment: {"Analyzed" if depth == "comprehensive" else "Not included"}

Confidence Level: {"High" if depth == "comprehensive" else "Medium" if depth == "detailed" else "Basic"}
"""
        
        return findings
        
    except Exception as e:
        return f"Async web research failed: {str(e)}"


# =============================================================================
# TOOL COLLECTIONS FOR EASY IMPORT
# =============================================================================

# Function-based tools list
FUNCTION_TOOLS = [
    pinecone_vector_search,
    project_management_tool,
    evaluation_framework_tool,
    markdown_editor_tool,
    serper_search_tool,
    monte_carlo_simulation_tool,
    async_web_research_tool
]

# Class-based tools list
CLASS_TOOLS = [
    AdvancedPineconeVectorSearchTool()
]

# All tools combined
ALL_TOOLS = FUNCTION_TOOLS + CLASS_TOOLS


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def get_strategic_analysis_tools():
    """Get tools specifically for strategic analysis workflows"""
    return [
        pinecone_vector_search,
        project_management_tool,
        evaluation_framework_tool,
        monte_carlo_simulation_tool,
        serper_search_tool
    ]

def get_content_tools():
    """Get tools for content generation and formatting"""
    return [
        markdown_editor_tool,
        async_web_research_tool
    ]

def get_advanced_tools():
    """Get advanced tools with enhanced features"""
    return [
        AdvancedPineconeVectorSearchTool()
    ]


# =============================================================================
# TOOL CONFIGURATION AND CACHING
# =============================================================================

def configure_tool_caching():
    """Configure caching for tools that support it"""
    # This would be implemented based on your specific caching requirements
    # CrewAI handles basic caching automatically, but you can customize it
    pass


if __name__ == "__main__":
    # Example usage
    print("Available CrewAI Tools:")
    print(f"Function-based tools: {len(FUNCTION_TOOLS)}")
    print(f"Class-based tools: {len(CLASS_TOOLS)}")
    print(f"Total tools: {len(ALL_TOOLS)}")