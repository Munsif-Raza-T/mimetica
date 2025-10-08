"""Custom tools for MIMÉTICA agents"""

from .custom_tools import (
    # Session readers
    SessionDirectoryReadTool,
    SessionFileReadTool,

    # Code interpreter (class + function)
    CodeInterpreterTool,
    execute_python_code,

    # Visualization generator
    strategic_visualization_generator,

    # DECIDE optional tools (safe stubs / validators)
    JSONSchemaValidatorTool,
    CriteriaLockerTool,
    RiskRegisterTool,
    MarketSizingTool,
    ElasticityEstimatorTool,
    TimeSeriesForecastTool,
    PositioningMapTool,
    UnitEconomicsTool,
    MarkdownFormatterTool,

    # Vector search & planning/eval/reporting tools
    AdvancedPineconeVectorSearchTool,
    project_management_tool,
    evaluation_framework_tool,
    markdown_editor_tool,
    monte_carlo_simulation_tool,
    serper_search_tool,
    async_web_research_tool,

    # Aggregated lists
    FUNCTION_TOOLS,
    CLASS_TOOLS,
    ALL_TOOLS,
    get_strategic_analysis_tools,
    get_content_tools,
    get_advanced_tools,
    get_code_interpreter_tools,
)

__all__ = [
    # Session readers
    "SessionDirectoryReadTool",
    "SessionFileReadTool",

    # Code interpreter (class + function)
    "CodeInterpreterTool",
    "execute_python_code",

    # Visualization generator
    "strategic_visualization_generator",

    # DECIDE optional tools
    "JSONSchemaValidatorTool",
    "CriteriaLockerTool",
    "RiskRegisterTool",
    "MarketSizingTool",
    "ElasticityEstimatorTool",
    "TimeSeriesForecastTool",
    "PositioningMapTool",
    "UnitEconomicsTool",
    "MarkdownFormatterTool",

    # Vector/search/planning/evaluation
    "AdvancedPineconeVectorSearchTool",
    "project_management_tool",
    "evaluation_framework_tool",
    "markdown_editor_tool",
    "monte_carlo_simulation_tool",
    "serper_search_tool",
    "async_web_research_tool",

    # Aggregated lists & getters
    "FUNCTION_TOOLS",
    "CLASS_TOOLS",
    "ALL_TOOLS",
    "get_strategic_analysis_tools",
    "get_content_tools",
    "get_advanced_tools",
    "get_code_interpreter_tools",
]
