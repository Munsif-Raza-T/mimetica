# -*- coding: utf-8 -*-
"""Public exports for MIMÉTICA tools (safe/optional imports)."""
from typing import List, Any

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
    markdown_editor_tool,
    monte_carlo_simulation_tool,
    monte_carlo_results_explainer,
    serper_search_tool,
    async_web_research_tool,

    # --- Simple pack (always present) ---
    get_simple_tools,
    get_simple_expected_output_template,

    # --- Simulation ---
    SimulationParamExtractorTool,
    CriteriaReferenceTool,
    TornadoSensitivityTool,
    PercentileSummaryTool,
    get_simulate_tools,   # convenience getter for SimulateAgent
    
    # --- Evaluation ---
    get_evaluate_tools,

    # --- Reporting ---
    #get_report_tools,
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
    "markdown_editor_tool",
    "monte_carlo_simulation_tool",
    "monte_carlo_results_explainer",
    "serper_search_tool",
    "async_web_research_tool",

    # Simple pack
    "get_simple_tools",
    "get_simple_expected_output_template",

    # Simulation
     "SimulationParamExtractorTool",
    "CriteriaReferenceTool",
    "TornadoSensitivityTool",
    "PercentileSummaryTool",
    "get_simulate_tools",

    # Evaluation
    "get_evaluate_tools",

    # Reporting
    #"get_report_tools"
]

# ----------------------------
# Safe optional exports
# ----------------------------
# Si en el futuro añades cualquiera de estas clases al custom_tools.py,
# se exportarán automáticamente sin romper la importación si aún no existen.

_OPTIONAL_NAMES = [
    # Content acquisition & parsing
    "WebPageReaderTool",
    "PDFTableExtractorTool",
    "HTML2TextTool",

    # Evidence hygiene & provenance
    "SourceCredibilityTool",
    "DeduplicateSnippetsTool",
    "CitationWeaverTool",

    # Data prep & formatting
    "DataCleanerTool",

    # Light analysis & structuring
    "EntityResolutionTool",
    "KPIExtractorTool",
    "TrendDetectorTool",
    "NewsTimelineTool",

    # Lean / extended (feature-flag capable)
    "GuardrailCheckerTool",
    "KPIConsistencyTool",
    "MonteCarloSimulatorTool",
    "FXRateTool",
    "CPIAdjusterTool",
    "PESTLEScorerTool",
    "FunnelMathTool",
    "BowTieRiskTool",
    "UnitNormalizerTool",
]

# --- Report (Agent 9) toolset getter -----------------------------------------

def get_report_tools(strict: bool = True) -> List[Any]:
    """
    Curated toolset for the ReportAgent (Agent 9).

    Execution intent:
      1) Session readers               -> build the cross-links map to prior phases
      2) Lightweight calculations      -> KPI sanity checks, deltas, quick math
      3) Strategic visualizations      -> MANDATORY (dashboards, timelines, distributions)
      4) Markdown assembly/edit        -> MANDATORY (compose the final report)
      5) Monte Carlo explainer         -> exec-friendly interpretation of P10/P50/P90 & probabilities

    If strict=True and any mandatory tool is missing, raise RuntimeError to avoid silent degradation.
    """
    tools: List[Any] = []

    # 1) Session readers
    if 'SessionDirectoryReadTool' in globals() and SessionDirectoryReadTool is not None:
        tools.append(SessionDirectoryReadTool())
    elif strict:
        raise RuntimeError("SessionDirectoryReadTool is required by ReportAgent.")

    if 'SessionFileReadTool' in globals() and SessionFileReadTool is not None:
        tools.append(SessionFileReadTool())
    elif strict:
        raise RuntimeError("SessionFileReadTool is required by ReportAgent.")

    # 2) Lightweight calculations
    if 'execute_python_code' in globals() and execute_python_code is not None:
        tools.append(execute_python_code)
    elif strict:
        raise RuntimeError("execute_python_code is required by ReportAgent.")

    # 3) Strategic visualizations (MANDATORY)
    if 'strategic_visualization_generator' in globals() and strategic_visualization_generator is not None:
        tools.append(strategic_visualization_generator)
    else:
        raise RuntimeError("strategic_visualization_generator is mandatory for ReportAgent.")

    # 4) Markdown assembly/editing (MANDATORY)
    if 'markdown_editor_tool' in globals() and markdown_editor_tool is not None:
        tools.append(markdown_editor_tool)
    else:
        raise RuntimeError("markdown_editor_tool is mandatory for ReportAgent.")

    # Optional: formatter class to polish headings/tables/lists
    if 'MarkdownFormatterTool' in globals() and MarkdownFormatterTool is not None:
        tools.append(MarkdownFormatterTool())

    # 5) Monte Carlo narrative (optional but recommended)
    if 'monte_carlo_results_explainer' in globals() and monte_carlo_results_explainer is not None:
        tools.append(monte_carlo_results_explainer)

    # Optional: CodeInterpreterTool class (heavier) for data munging
    if 'CodeInterpreterTool' in globals() and CodeInterpreterTool is not None:
        tools.append(CodeInterpreterTool())

    return tools

# Ensure it’s exported even if __all__ was defined earlier
try:
    __all__.append("get_report_tools")
except Exception:
    __all__ = list(set((globals().get("__all__", []) or []) + ["get_report_tools"]))


try:
    import importlib
    _ct = importlib.import_module("tools.custom_tools")
    for _name in _OPTIONAL_NAMES:
        _obj = getattr(_ct, _name, None)
        if _obj is not None:
            globals()[_name] = _obj
            __all__.append(_name)
except Exception:
    pass
