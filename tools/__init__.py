# -*- coding: utf-8 -*-
"""Public exports for MIMÉTICA tools (safe/optional imports)."""

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

    # --- Simple pack (always present) ---
    get_simple_tools,
    get_simple_expected_output_template,
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

    # Simple pack
    "get_simple_tools",
    "get_simple_expected_output_template",
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

# Intentamos añadirlos si existen en custom_tools
try:
    import importlib
    _ct = importlib.import_module("tools.custom_tools")
    for _name in _OPTIONAL_NAMES:
        _obj = getattr(_ct, _name, None)
        if _obj is not None:
            globals()[_name] = _obj
            __all__.append(_name)
except Exception:
    # Silencioso: si falla algo aquí, no rompemos la importación del paquete
    pass
