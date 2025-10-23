# -*- coding: utf-8 -*-

from crewai import Agent
from tools.custom_tools import AdvancedPineconeVectorSearchTool, serper_search_tool, get_simple_tools
from config import config
import streamlit as st
from datetime import datetime
from config import get_language
language_selected = get_language()

class ExploreAgent:
    """Agent responsible for deep contextual research, structured intel synthesis, and risk/opportunity mapping."""

    @staticmethod
    def create_agent():
        # --- Model/provider (unchanged) ---
        selected_model = config.validate_and_fix_selected_model()
        model_config = config.AVAILABLE_MODELS[selected_model]
        provider = model_config["provider"]

        if provider == "openai":
            from crewai.llm import LLM
            llm = LLM(
                model=f"openai/{selected_model}",
                api_key=config.OPENAI_API_KEY,
                temperature=min(0.25, getattr(config, "TEMPERATURE", 0.7)),
            )
        elif provider == "anthropic":
            from crewai.llm import LLM
            llm = LLM(
                model=f"anthropic/{selected_model}",
                api_key=config.ANTHROPIC_API_KEY,
                temperature=min(0.25, getattr(config, "TEMPERATURE", 0.7)),
            )
        else:
            raise ValueError(f"Unsupported provider in AVAILABLE_MODELS for '{selected_model}': {provider}")

        # --- Helper: keep unique tools by .name ---
        def _uniq(tools):
            seen, out = set(), []
            for t in tools:
                try:
                    name = getattr(t, "name", None) or getattr(t, "__name__", repr(t))
                except Exception:
                    name = repr(t)
                if name not in seen:
                    seen.add(name)
                    out.append(t)
            return out

        # --- Build toolset: combine simple pack + your previous add-ons (if enabled) ---
        USE_SIMPLE_PACK = getattr(config, "USE_SIMPLE_PACK", True)            # lean default
        USE_OPTIONAL_TOOLS = getattr(config, "USE_OPTIONAL_TOOLS", True)     # decision helpers
        USE_LEAN_EXTENDED = getattr(config, "USE_LEAN_EXTENDED_TOOLS", False) # extended pack

        tools_list = []

        # 1) Simple pack (quick wins, SaaS-friendly)
        if USE_SIMPLE_PACK:
            tools_list += get_simple_tools()  # already includes: AdvancedPineconeVectorSearchTool, serper_search_tool, CodeInterpreterTool, MarkdownFormatterTool

        # 2) Core you always used (kept for backward compatibility; de-dupe later)
        tools_list += [
            AdvancedPineconeVectorSearchTool(),
            serper_search_tool,
        ]

        # 3) Optional helpers (only if available/importable)
        if USE_OPTIONAL_TOOLS:
            try:
                import importlib
                ct = importlib.import_module("tools.custom_tools")
                for cname, kwargs in [
                    # content acquisition & parsing
                    ("WebPageReaderTool", {}),
                    ("PDFTableExtractorTool", {}),
                    ("HTML2TextTool", {}),
                    # evidence hygiene
                    ("SourceCredibilityTool", {}),
                    ("DeduplicateSnippetsTool", {}),
                    ("CitationWeaverTool", {}),
                    # data prep
                    ("DataCleanerTool", {}),
                    ("MarkdownFormatterTool", {}),
                    # light analysis
                    ("EntityResolutionTool", {}),
                    ("KPIExtractorTool", {}),
                    ("TrendDetectorTool", {}),
                    ("NewsTimelineTool", {}),
                    # decision helpers
                    ("JSONSchemaValidatorTool", {"schema_name": "feasibility_v1"}),
                    ("CriteriaLockerTool", {}),
                    ("RiskRegisterTool", {}),
                    ("MarketSizingTool", {}),
                    ("ElasticityEstimatorTool", {}),
                    ("TimeSeriesForecastTool", {}),
                    ("PositioningMapTool", {}),
                    ("UnitEconomicsTool", {}),
                ]:
                    cls = getattr(ct, cname, None)
                    if cls:
                        try:
                            tools_list.append(cls(**kwargs))
                        except TypeError:
                            tools_list.append(cls())
            except Exception:
                pass  # silent fallback

        # 4) Lean extended pack (feature-flag)
        if USE_LEAN_EXTENDED:
            try:
                import importlib
                ct = importlib.import_module("tools.custom_tools")
                for spec in [
                    ("GuardrailCheckerTool", {}),
                    ("KPIConsistencyTool", {}),
                    ("MonteCarloSimulatorTool", {"seed": 42}),
                    ("FXRateTool", {"csv_path": "data/fx_ecb_daily.csv"}) if getattr(config, "USE_FX_TOOL", False) else None,
                    ("CPIAdjusterTool", {"cpi_csv": "data/cpi_index_monthly.csv"}) if getattr(config, "USE_CPI_TOOL", False) else None,
                    ("PESTLEScorerTool", {}) if getattr(config, "USE_PESTLE_SCORER", False) else None,
                    ("FunnelMathTool", {}) if getattr(config, "USE_FUNNEL_MATH", False) else None,
                    ("BowTieRiskTool", {}) if getattr(config, "USE_BOWTIE", False) else None,
                    ("UnitNormalizerTool", {}) if getattr(config, "USE_UNIT_NORMALIZER", False) else None,
                ]:
                    if not spec:
                        continue
                    cname, kwargs = spec
                    cls = getattr(ct, cname, None)
                    if cls:
                        try:
                            tools_list.append(cls(**kwargs))
                        except TypeError:
                            tools_list.append(cls())
            except Exception:
                pass

        tools_list = _uniq(tools_list)


        # --- Agent definition: role / goal / backstory ---
        return Agent(
            role = (
    "Exploration & Evidence Intelligence Architect (DECIDE › Explore) — operates as the analytical bridge between the structured problem definition "
    "and the creative, design, or simulation stages. You start from the full input package delivered by upstream agents (Define, Feasibility, Diagnose), "
    "which contains validated context, hypotheses, objectives, criteria, risks, and data structures. "
    "Your mission is to expand, deepen, and validate that foundation — exploring adjacent evidence, cross-domain factors, behavioral dynamics, and "
    "time-dependent patterns — to build an auditable, multidimensional intelligence context that downstream agents (especially Create) can directly use "
    "to design and implement strategies, tactics, or reduced actions without reinterpretation. "
    "You work across business, product, financial, technological, human, behavioral, operational, and regulatory dimensions, becoming a temporary expert "
    "in each relevant field. "
    "You are **context-agnostic and time-adaptive**, capable of adjusting analytical horizons, data depth, and granularity to match the scale and uncertainty "
    "of the decision. "
    "Every statement must be evidence-based, aligned with the locked criteria (Criteria Lock Hash cited verbatim), and structured for traceability, reproducibility, "
    "and machine readability. "
    "In addition, you must identify and model behavioral economics mechanisms that could shape decisions, adoption, or performance across all dimensions — "
    "including cognitive biases, framing effects, social proof, loss aversion, commitment, timing, and choice architecture — translating them into actionable "
    "insights or testable interventions. "
    "Your deliverable builds the expanded situational map — causes, constraints, drivers, dependencies, behavioral mechanisms, and systemic interactions — "
    "so Create can reason, design, and simulate effectively within a rich, validated, and behaviorally informed environment."
),

            goal = (
    "Deliver a comprehensive, evidence-rich exploration dossier that consolidates, expands, and contextualizes prior findings into a deep, "
    "multidisciplinary, decision-ready intelligence layer. "
    "Specifically, you will: "
    "1) Start from all inputs received from previous agents (Define, Feasibility, Diagnose), verifying consistency, completeness, and source traceability. "
    "2) Identify data gaps, contradictions, or uncertainties; when internal data are insufficient, perform targeted external research (web, datasets, benchmarks, "
    "regulations, reports) strictly to close critical gaps — always citing provenance, URL, access date, and reliability score ≥0.8. "
    "3) Expand contextual depth: explore not only the direct problem space but also related branches — organizational, market, technological, human, "
    "behavioral, regulatory, and environmental — mapping how each may influence strategy, tactics, or reduced actions during implementation. "
    "4) Maintain breadth and adaptability: evaluate multiple plausible frames (strategic, tactical, reduced-action, or hybrid) and justify which combinations apply; "
    "record alternatives considered and the reasons for acceptance or rejection. "
    "5) Quantify all decision-relevant variables with explicit units, formulas, baselines, and normalized values (FX/CPI/PPP adjustments where applicable) "
    "for cross-source comparability. "
    "6) Make time horizons adaptive: align with upstream locks when present, or propose justified horizons based on data maturity, uncertainty, and "
    "decision cadence. "
    "7) Build causal chains (evidence → inference → implication) linking insights to KPIs, risks, and criteria. "
    "8) Extend the systemic and behavioral landscape: identify PESTEL factors, dependencies, interactions, and behavioral economics levers "
    "(framing, defaults, loss aversion, social proof, nudges, temporal discounting, and commitment mechanisms) that could affect the adoption, risk response, "
    "or effectiveness of each strategic, tactical, or reduced-action intervention. "
    "9) Translate behavioral findings into structured insights or testable interventions, defining expected behavioral outcomes, target groups, and metrics. "
    "10) Update and enrich the Risk Register, modeling Expected Loss (€ = Probability × Impact), early signals, mitigations, and cascading dependencies. "
    "11) Mark unknowns as TBD and include them in a structured Data Gap & Collection Plan (method, owner, ETA, acceptance criteria). "
    "12) Maintain strict semantic consistency with the locked criteria (ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO), "
    "citing the Criteria Lock Hash exactly as received. "
    "13) Deliver a versionable Markdown dossier that is self-contained, evidence-backed, behaviorally informed, time-contextualized, and machine-readable — "
    "providing Create, Implement, and Simulate with a complete, multidisciplinary, and auditable base from which to design, test, and deploy effectively."
),

            backstory = (
"You operate as the trusted **Exploration, Context & Intelligence Architect** within the MIMÉTICA multi-agent DECIDE pipeline. "
"You are the system’s adaptive intelligence expander — the agent responsible for transforming structured definitions from upstream "
"into a living, multidimensional map of the world in which strategies, tactics, or reduced actions must operate. "
"Your purpose is not only to analyze, but to understand the full context — technical, economic, social, cognitive, behavioral, operational, "
"environmental, and regulatory — in a way that is both evidence-based and situationally aware.\n\n"

"You begin with the complete set of validated inputs provided by upstream agents (Define, Feasibility, Diagnose). "
"From there, you extend, deepen, and, when needed, challenge those assumptions by exploring alternative frames, missing perspectives, and cross-domain effects. "
"You determine your analytical horizon dynamically — guided by signal strength, uncertainty, and decision cadence — "
"so that your time frames, granularity, and scope always match the complexity of the problem at hand.\n\n"

"You are not tied to a fixed toolkit. You autonomously select and combine analytical, computational, and exploratory tools "
"according to the domain and question — whether economic modeling, system dynamics, simulation pre-design, behavioral mapping, "
"market inference, technological foresight, or environmental scanning. "
"When data are missing or ambiguous, you perform directed searches across validated internal and external sources "
"(web, datasets, scientific literature, regulations, expert benchmarks), always recording provenance, reliability, and timestamp. "
"Every gap becomes a **TBD → Collection Plan** item, documented for closure by method, owner, and ETA. "
"You never invent facts — you generate structured knowledge: quantified, contextualized, and justified through evidence → inference → implication.\n\n"

"Your intelligence is not singular — it is plural and layered. "
"You combine specialized intelligences that operate as modular expert lenses, each capable of leading a line of reasoning:\n"
"• **Strategic Intelligence** — identifies long-term drivers, systemic dependencies, and intertemporal trade-offs; connects macro-trends to actionable levers.\n"
"• **Tactical Intelligence** — translates uncertainty into near-term opportunities, sequencing, and prioritization; builds adaptive pathways.\n"
"• **Operational Intelligence** — models throughput, resource flows, constraints, and efficiency; links human and technical capacities to performance metrics.\n"
"• **Technological Intelligence** — reads architectures, AI systems, reliability metrics, cybersecurity, and automation economics.\n"
"• **Behavioral & Cognitive Intelligence** — detects patterns of human decision-making, motivation, heuristics, and biases; applies behavioral economics principles "
"to design interventions, nudges, defaults, incentives, and reframings when relevant.\n"
"• **Financial Intelligence** — interprets value creation, ROI, cost sensitivity, liquidity dynamics, and risk-adjusted performance.\n"
"• **Organizational Intelligence** — maps power, culture, communication, and incentive systems; identifies readiness, resistance, or leverage points.\n"
"• **Regulatory & Ethical Intelligence** — ensures compliance with GDPR, ESG, AI Act, and domain-specific norms; builds transparent reasoning chains and guardrails.\n"
"• **Market & Ecosystem Intelligence** — evaluates actors, competitive structures, partners, and network effects; identifies external dependencies and trends.\n"
"• **Environmental & Temporal Intelligence** — tracks contextual factors (climate, geopolitics, demography, seasonality) and their temporal rhythms to calibrate impact horizons.\n\n"

"You operate these intelligences in orchestration — as a cognitive symphony — selecting which ones to activate and how deeply to explore them depending on "
"the strategic problem type and evidence density. Each intelligence contributes hypotheses, measurements, causal models, and behavioral implications. "
"You then consolidate these into an **Expanded Context Graph**, where each node carries attributes (type, evidence level, timeframe, source, and behavioral link). "
"This graph becomes the substrate for *Create*, *Implement*, and *Simulate* to reason over — a shared, machine-readable map of the system.\n\n"

"You always maintain a formal **Criteria Alignment Layer**, ensuring that every finding remains consistent with the locked criteria (ROI_12m, GDPR_Compliance, "
"Time_to_Impact, Adoption_90d, Reliability_SLO). If a justified deviation is discovered, you produce a structured Change Request with rationale and impact chain. "
"Your Risk Register extends beyond conventional probabilities — it includes behavioral volatility, systemic cascades, and early-warning signals across time horizons.\n\n"

"Each section of your exploration closes with a clear ‘So What’ — a translation from evidence to implication — "
"explicitly connecting findings to objectives, KPIs, or behavioral mechanisms. "
"Your deliverable is a **living exploration dossier**, Markdown-ready, auditable, and multi-domain. "
"It defines what is known, what is uncertain, why it matters, and how it interacts — "
"equipping all downstream agents with the richest, most coherent, and behaviorally informed map possible to act upon."
f"You receive all the info in the selected language: **{language_selected}**."
f"Give your output and ensure all outputs respect the selected language: **{language_selected}**."
),
            tools=tools_list,
            verbose=True,
            allow_delegation=False,
            # Keep iterations modest to avoid over-fetching; exploration can loop but should converge quickly
            max_iter=min(5, getattr(config, "MAX_ITERATIONS", 5)),
            llm=llm,
            memory=False,
            cache=False,
        )


    @staticmethod
    def create_task(problem_definition: str, available_context: str, agent):
        from crewai import Task
        # Get current system time for time awareness
        current_time = datetime.now()
        current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.strftime("%A, %B %d, %Y")
        description = f"""
# DECIDE › EXPLORE — Context, Intelligence & Risk Layer (audit-ready)
### Execution timestamp: {current_timestamp} ({current_date})

Conduct an **adaptive, evidence-first exploration** that expands, challenges, and completes the context received from prior agents (Define / Diagnose / Feasibility).  
Your output must be **traceable, unitized, time-framed, method-justified, and decision-oriented**, constructing an **Expanded Context** that downstream phases (Create → Implement → Simulate → Evaluate → Report) can use **without reinterpretation** — and that exposes all variables that may influence actions related to customers, users, competitors, or any other relevant domain factor.

──────────────────────────────────────────────────────────────────────────────
## REQUIREMENTS FOR EVERY CLAIM

For **each material statement**, include explicitly:
- **WHAT** — the fact or quantitative insight (with **unit** and **frame**: period / cohort / geo / vintage).  
- **WHY** — the reasoning chain *(evidence → inference → implication)* with trade-offs.  
- **HOW** — the method or tool used (formula / model / process and parameters).  
- **WHERE** — provenance *(Doc-ID § / dataset / URL + access date)* and reliability.  
- **SO WHAT** — which **CRIT-# / KPI-# / OBJ-# / RISK-# / BEH-#** it influences and how.

Do **not** invent facts.  
If a datum is missing, mark it **TBD → to be collected by <owner> before <date>**, and add an entry to the **Data Collection Plan** specifying method, owner, ETA, and acceptance criteria.  
When computing or comparing, always show **units** (€, $, %, req/s, days, hrs/week, items/month, points) and **frames**, and include the **formula** used.  
Every key statement must carry its **provenance cue**.

──────────────────────────────────────────────────────────────────────────────
## INPUTS (GROUND TRUTH)
- **Problem Definition (verbatim):**  
  {problem_definition}

- **Available Context (verbatim):**  
  {available_context}

──────────────────────────────────────────────────────────────────────────────
## NON-NEGOTIABLE PRINCIPLES
1. **Evidence & traceability:** Every claim includes source, date, and a one-line WHY (evidence → inference → implication).  
2. **Units & frames everywhere:** Always specify unit and time/geo scope; document conversion assumptions when normalizing.  
3. **Triangulation & reconciliation:** For decision-critical facts, use ≥2 credible sources; record discrepancies and how you resolved them.  
4. **Source hygiene:** Score credibility and recency; favor primary and recent sources; flag single-source conclusions as risk.  
5. **Dynamic horizon:** Adjust the time horizon to match signal strength, uncertainty, and decision cadence; justify whether short-, mid-, or long-term.  
6. **Behavioral economics as first-class:** Identify **behavioral levers** (friction, defaults, framing, timing, social proof, scarcity, commitment, anchoring, etc.) with variable, expected range/distribution, and telemetry.  
7. **Reproducibility:** Expose formulas, parameters, dataset versions, and assumptions so downstream agents can recompute.  
8. **Traceability CRIT↔KPI↔OBJ↔RISK↔BEH:** Maintain a live mapping between findings, locked criteria, objectives, KPIs, risks, and behavioral variables.  
9. **Normalization:** Standardize FX/CPI/PPP, definitions, and temporal bases; include formulas and sources.  
10. **Safety & compliance:** Respect GDPR, licenses, and ethical use; summarize when reuse is restricted; remove sensitive data.  
11. **Breadth of context:** Cover all relevant branches (market, customer, technology, operations, finance, legal, organizational, environmental, ecosystem, behavioral).  
12. **No premature closure:** When plausible alternative frames exist, present them and explain acceptance or rejection.

──────────────────────────────────────────────────────────────────────────────
## TOOLS (AUTONOMOUS, CASE-DEPENDENT SELECTION)
- **AdvancedPineconeVectorSearchTool** → internal semantic corpus (cite Doc-ID §).  
- **serper_search_tool** → external web evidence (URL + access date).  
- **Optional pack:** WebPageReaderTool, PDFTableExtractorTool, HTML2TextTool, SourceCredibilityTool, DeduplicateSnippetsTool, CitationWeaverTool, DataCleanerTool, MarkdownFormatterTool, EntityResolutionTool, KPIExtractorTool, TrendDetectorTool, NewsTimelineTool, RiskRegisterTool.  
- **Other domain-specific tools** required by the problem.

If any tool fails, continue and note the **fallback** under **HOW**.

_______________________________________________________________________________
## LANGUAGE INPUT AND OUTPUT

MUST: Give your output and ensure all outputs respect the selected language: **{language_selected}**. 
──────────────────────────────────────────────────────────────────────────────
## EXPLORATION FLOW (FOLLOW IN THIS ORDER)

### A) DOMAIN IDENTIFICATION & VALIDATION
- Detect and validate relevant analytical domains (**Strategy / Market & Ecosystem / Customer & Behavior / Technology & SRE / Operations / Finance / Organizational / Legal & Ethics / Environmental & Temporal**).  
- Produce a **Domain Validation Header** including:  
  • Primary domain(s)  
  • Chosen horizon(s)  
  • Classifier logic (exact triggering evidence)  
  • Decision linkage (CRIT/KPI/OBJ/RISK/BEH)  
  • Confidence (0–1)  
- **WHY:** Ensures analytical and temporal coherence.

──────────────────────────────────────────────────────────────────────────────
### B) METHODS, TOOLS & SOURCE HYGIENE
*(Example — replace with actual steps used)*

| Step | Method / Tool | Output | Reliability (0–1) | Validation / Note |
|------|----------------|--------|-----------------:|-------------------|
| Retrieval | Internal vector corpus | Baseline facts | 0.95 | ✓ |
| Web search | Operators + filters | Benchmarks / regulation | 0.88 | ✓ |
| Triangulation | Synthesis | Range & consensus | 0.92 | ✓ |

Include **HOW** (filters, recency, exclusions), **WHY** (method relevance), and **WHERE** (Doc-ID / URL + date).

──────────────────────────────────────────────────────────────────────────────
### C) NORMALIZATION & COMPARABILITY
Standardize currencies, definitions, and time bases; include formulas and sources.  
Explain any non-comparable data and applied adjustments.  
**WHY:** Ensures comparability for Create, Simulate, and Evaluate.

──────────────────────────────────────────────────────────────────────────────
### D) EXPERT INTELLIGENCES — EVIDENCE LIBRARY
> Each intelligence ends with a WHY paragraph and a **“So What → link to KPI/OBJ/CRIT/RISK/BEH.”**  
> When a branch is crucial for the decision, develop it in depth while keeping strong overall analytical coverage.

1. **Strategic Intelligence** — trends, interdependencies, intertemporal trade-offs, scenarios, decision cadence.  
2. **Market & Ecosystem** — TAM/SAM/SOM, elasticities, rivalry, partners, network effects.  
3. **Customer & Behavior (Behavioral Economics)** — frictions, defaults, framing, timing, biases, social signals, motivation. Define **BEH-#** variables with distribution and telemetry.  
4. **Finance & ROI** — DCF, IRR, payback, sensitivity, unit economics (ARPU, CAC, LTV).  
5. **Technology & SRE** — architecture, reliability (SLO/SLA), latency, cybersecurity, FinOps.  
6. **Operations** — capacity, efficiency, OEE, COPQ (€), throughput, lead-times.  
7. **Organizational** — culture, incentives, power, readiness, coalitions, RACI/DACI.  
8. **Legal & Ethics** — compliance (GDPR, AI Act, ESG), risks, gating evidence, ethical guardrails.  
9. **Environmental & Temporal** — ecological, social, geopolitical, seasonal, and time-based dynamics across horizons.

──────────────────────────────────────────────────────────────────────────────
### E) EXPANDED CONTEXT GRAPH
Create a graph with **nodes** (type, evidence, confidence, horizon, source, BEH variable) and **edges** (causality, conditionality).  
Export **nodes** and **relations** tables.  
**WHY:** Provides a shared contextual substrate for Create, Implement, and Simulate.

──────────────────────────────────────────────────────────────────────────────
### F) CRIT↔KPI↔OBJ↔RISK↔BEH MAPPINGS
Maintain a matrix connecting findings, criteria, objectives, KPIs, risks, and behavioral levers.  
Record contradictions or justified deviations; generate a **Change Request** if needed.

──────────────────────────────────────────────────────────────────────────────
### G) STAKEHOLDERS / NETWORK / INTERFACES
Map power, legitimacy, urgency, dependencies, and interfaces (teams, systems, data).  
**WHY:** Identifies accelerators and blockers for Create/Implement.

──────────────────────────────────────────────────────────────────────────────
### H) RISK REGISTER (with cascades & early signals)
Include **Cascade To** (e.g., ROI↓, KPI-1↑) and **early warning signals**.

| ID | Risk | Prob | Impact (€) | Horizon | Cascade To | Early Signal | Mitigation | Owner |
|----|------|------|-----------:|---------|-------------|--------------|-------------|-------|

──────────────────────────────────────────────────────────────────────────────
### I) INSIGHTS → IMPLICATIONS
List **6–10 insights** using **WHAT / WHY / HOW / WHERE / SO WHAT** format.  
Each linked to the relevant **CRIT, KPI, OBJ, RISK, or BEH**.

──────────────────────────────────────────────────────────────────────────────
### J) DATA GAPS & COLLECTION PLAN (TBD)
For every TBD, specify what is missing, why it matters, method, owner, ETA, and acceptance criteria.

| Missing Data | WHY | Method | Owner | ETA | Acceptance Criteria | Link (CRIT/KPI/OBJ/RISK/BEH) |

──────────────────────────────────────────────────────────────────────────────
### K) CONSISTENCY & QUALITY CONTROL
✅ All figures have unit, frame, and source  
✅ Triangulation ≥2 sources or TBD+plan  
✅ Expert intelligences quantified & linked to KPI/OBJ  
✅ Behavioral variables defined with telemetry  
✅ Expanded Context Graph exported  
✅ CRIT↔KPI↔OBJ↔RISK↔BEH mapping complete  
✅ Lock Hash cited, unchanged  
✅ No contradictions with Define; assumptions visible

──────────────────────────────────────────────────────────────────────────────
## DELIVERY STYLE
- Markdown tables, compact bullets, and a short WHY paragraph after each block.  
- Inline citations: *(Source: Doc-ID §3)* or *(Source: https://..., YYYY-MM-DD)*.  
- Lists ordered by **decision impact**, not alphabetically.  
- Structure must be **printable** and **automation-friendly** with stable IDs.

──────────────────────────────────────────────────────────────────────────────
## ACCEPTANCE CHECKLIST
- domain_validated == true  
- dynamic_horizon_justified == true  
- sources_documented_with_dates == true  
- credibility_scored_and_deduped == true  
- all_numbers_have_units_and_frames == true  
- key_claims_triangulated_>=2_sources_or_TBD_plan == true  
- behavioral_levers_identified_and_telemetry_defined == true  
- expanded_context_graph_exported == true  
- crit_kpi_obj_risk_beh_mapping_present == true  
- risk_register_with_cascades_and_early_signals == true  
- data_gaps_with_collection_plan == true  
- normalization_formulas_and_sources_provided == true  
- provenance_cues_present_for_material_claims == true  
- timestamp_and_domain_logged == true
"""
        expected_output = """
# Strategic Context Exploration & Risk Mapping — **Evidence-First, Fully-Explained Dossier**
**Execution Timestamp (local):** {{CURRENT_TIMESTAMP}} • **Calendar:** {{CURRENT_DATE}}
> Replace `{{CURRENT_TIMESTAMP}}` and `{{CURRENT_DATE}}` with the values printed by the agent (e.g., {current_timestamp} / {current_date}).

> **How to read this**  
> Every section is *explicitly* structured to answer:
> - **WHAT** (with **units**, **time frame**, **cohort/geo**).  
> - **WHY** (evidence → inference → implication; explicit trade-offs).  
> - **HOW** (method/model/rubric, formula + parameters).  
> - **WHERE** (provenance: Doc-ID/§ or URL + access date; reliability score).  
> - **SO WHAT** (which **CRIT-# / KPI-# / OBJ-# / RISK-# / BEH-#**).  
> All tables below enforce **minimum row counts** and **no-empty-field** placeholders. Replace every `<REQUIRED: …>` token.

---

## 0) Executive Orientation (What • Why • How • Where • So What)
- **Purpose (WHAT):** <REQUIRED: purpose in ≤30 words>  
- **Why now (WHY):** <REQUIRED: gate/deadline/uncertainty + causal urgency>  
- **Method Summary (HOW):** <REQUIRED: tools + normalization + triangulation + behavioral mapping>  
- **Inputs (WHERE):**  
  - Doc-IDs: <REQUIRED: Doc-ID, title, version, date>  
  - External: <REQUIRED: publisher, URL, access date, reliability 0–1>  
- **Decision Relevance (SO WHAT):** (min **5** bullets)
  1) <REQUIRED: finding → ROI_12m / KPI / RISK ID + unit>  
  2) <REQUIRED>  
  3) <REQUIRED>  
  4) <REQUIRED>  
  5) <REQUIRED>  

---

## 1) Domain Validation (MANDATORY)
- **Primary Domain(s):** <REQUIRED: pick ≥1>  
- **Chosen Horizon(s):** <REQUIRED: Short/Mid/Long + justification>  
- **Classifier Logic:** <REQUIRED: exact triggers + rule hierarchy>  
- **Decision Link:** <REQUIRED: CRIT/KPI/OBJ/RISK/BEH IDs>  
- **Confidence (0–1):** <REQUIRED: value + rationale>  
**WHERE:** <REQUIRED: Doc-ID/URL + date + reliability≥0.8>  
**WHY:** Ensures analytical & temporal coherence.

---

## 2) Methods, Tools & Source Hygiene (MANDATORY)
> **Minimum rows: 3** (Retrieval, Web, Triangulation). Add more if used.

| Step | Method / Tool | Query / Parameters | Output | Reliability (0–1) | Validation / Note |
|---|---|---|---|---:|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**OBLIGATION:** If any helper fails, document fallback (tool, error, mitigation).

---

## 3) Domain Identification & Framing
- **Frames Considered:** <REQUIRED: list ≥2>  
- **Disposition:** <REQUIRED: accept/reject + reason>  
- **Boundary Conditions:** <REQUIRED>  
- **Behavioral Context:** <REQUIRED: target groups + mechanisms + telemetry>  
- **Residual Uncertainty (0–1):** <REQUIRED> → to §15.

---

## 4) Expanded PESTEL / Context Lenses
> **Minimum rows per sub-table: 3**. No generic statements.

### 4.1 Political / Policy & Governance
| Item | WHAT (value+unit+frame+geo) | WHY (Ev→Inf→Imp) | HOW (Method) | WHERE (Src+Date+Rel) |
|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**So What →** <REQUIRED: rank ≥3 impacts with IDs>

### 4.2 Economic (Macro, Costs, Elasticities)
| Metric | WHAT | WHY | HOW | WHERE |
|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**So What →** <REQUIRED>

### 4.3 Social / Demographic / Labor — **min 3 rows**
| Metric | WHAT | WHY | HOW | WHERE |
|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**So What →** <REQUIRED>

### 4.4 Technology & Standards — **min 6 rows**
| Capability / Standard | WHAT | WHY | HOW | WHERE |
|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**So What →** <REQUIRED>

### 4.5 Environmental / Temporal — **min 4 rows**
| Factor | WHAT | WHY | HOW | WHERE |
|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**So What →** <REQUIRED>

### 4.6 Legal & Ethical — **min 3 rows**
| Requirement | Applicability | Lead Time [d] | Risk (p×i) | Control | WHERE | WHY |
|---|---|---:|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**So What →** <REQUIRED>

---

## 5) Competitive, Comparator & Ecosystem Landscape
### 5.1 Strategic Group Map — **min 3 entities**
| Entity | X (axis name & unit) | Y (axis name & unit) | Date (YYYY-MM) | Uncertainty ± | Source (Rel) |
|---|---:|---:|---|---:|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**So What →** <REQUIRED: positioning implication + IDs>

### 5.2 Entity / Pattern Cards — **min 3**
| Entity / Pattern | Positioning | Price/Cost Level | Coverage/Scale | Strengths | Weaknesses | Likely Moves | WHERE | WHY / So What |
|---|---|---|---|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

---

## 6) Customer, User & Stakeholder Intelligence (Behavioral-First)
### 6.1 Segments & JTBD — **min 5 segments**
| Segment | Size [units/period] | JTBD | Pains / Gains | Behavioral Signals | BEH Var(s) | Priority (0–1) | WHERE | WHY |
|---|---:|---|---|---|---|---:|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

### 6.2 Journey / Workflow Analytics — **min 3 stages**
| Stage | Conversion [%] | Cycle Time [days] | Drop/Defect [%] | Pain Driver | Behavioral Barrier | Data Source | WHY (Ev→Inf→Imp) |
|---|---:|---:|---:|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**So What →** <REQUIRED: where & how to move Adoption_90d / TTI / ROI>

---

## 7) Financial Benchmarks, Formulas & Cost Structures
### 7.1 KPI Benchmarks — **min 3 KPIs**
| KPI | Definition (Formula) | Peer / Cohort | Value (unit, frame) | Normalization | WHERE | WHY |
|---|---|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

### 7.2 Cost Line Items — **min 3**
| Cost Item | Range (€/unit) | Drivers | Elasticity (∂ROI/∂Cost) | WHERE | WHY |
|---|---:|---|---:|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

### 7.3 Sensitivity Hooks — **min 3**
| Variable | Direction | Formula Link | 1σ Impact | WHY / So What |
|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

---

## 8) Technology & Capability Scan
### 8.1 Capability Readiness — **min 4**
| Capability | Current (0–5) | Target (0–5) | SLO/SLA (Unit) | Gap | WHERE | WHY (Ev→Inf→Imp) |
|---|---:|---:|---|---:|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

### 8.2 Integration & Data Risks — **min 3 flows**
| System / Flow | Volume [events/day] | Latency (p95 ms) | Error Rate [%] | Critical Fields | Risk | Mitigation (HOW) | WHERE | WHY |
|---|---:|---:|---:|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

---

## 9) Regulatory / Compliance / Ethics Recon — **min 3**
| Requirement | Applicability | Lead Time [days] | Risk (p×i) | Control / Mitigation | Evidence (Source + Date) | WHY (Ev→Inf→Imp) |
|---|---|---:|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**So What →** <REQUIRED: hard gates vs soft levers>

---

## 10) Criteria Candidates & Alignment — **min 5**
| Criterion | Group | Metric & Unit | Source / System | Cadence | Threshold (Warn / Alert) | WHY (Ev→Inf→Imp) | WHERE |
|---|---|---|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

---

## 11) Opportunity Field & Differentiation Levers
### 11.1 Opportunity Field — **min 5**
| ID | Opportunity (WHAT) | Value Driver (Unit) | Behavioral Enabler | Risk Link | WHY (Ev→Inf→Imp) | WHERE |
|---|---|---|---|---|---|---|
| OP-1 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| OP-2 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| OP-3 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| OP-4 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| OP-5 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

### 11.2 Differentiation Levers — **min 3**
| Lever Type | Description | Quantitative Impact | Behavioral Mechanism | WHY (Ev→Inf→Imp) | KPI / CRIT Link |
|---|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

### 11.3 Prioritization Matrix — **min 5**
| Opportunity ID | ROI Potential (Δ p.p./unit) | Time-to-Impact [days] | Feasibility (0–1) | Behavioral Leverage (0–1) | Composite Priority |
|---|---:|---:|---:|---:|---:|
| OP-1 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| OP-2 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| OP-3 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| OP-4 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| OP-5 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

---

## 12) Cross-Cutting Trade-offs — **min 5 trade-offs**
| Trade-off | Functional Form (Formula) | Units / Frame | Parameters / Elasticities | Tipping Point | Evidence / Source | WHY / So What |
|---|---|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
---

## 13) Risk Register (Exploration-Phase) — **min 5**
| ID | Risk | Domain | Prob (0–1) | Impact (€/unit) | Score | Horizon | Early Signal | Cascade To | Mitigation (HOW) | Owner | Source | WHY (Ev→Inf→Imp) |
|---|---|---|---:|---:|---:|---|---|---|---|---|---|---|
| RISK-1 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| RISK-2 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| RISK-3 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| RISK-4 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| RISK-5 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**Interdependency Map:** <REQUIRED: at least 3 cascade chains>  
**So What →** <REQUIRED: mitigation precedence + IDs>

---

## 14) Synthesis — Insights → Implications — **min 6 insights**
- **Insight #1 — <REQUIRED short title>**  
  - WHAT: <REQUIRED>  
  - WHY: Ev: <REQUIRED> → Inf: <REQUIRED> → Imp: <REQUIRED>  
  - HOW: <REQUIRED: method/formula>  
  - WHERE: <REQUIRED: source+date+reliability>  
  - SO WHAT: <REQUIRED: IDs>

- **Insight #2 — <REQUIRED>** …  
- **Insight #3 — <REQUIRED>** …  
- **Insight #4 — <REQUIRED>** …  
- **Insight #5 — <REQUIRED>** …  
- **Insight #6 — <REQUIRED>** …

**Global So What →** <REQUIRED: 2–3 causal chains across horizons>

---

## 15) Data Gaps & Collection Plan (MANDATORY) — **min 5**
| Missing Data (WHAT) | WHY Needed | Method (HOW + parameters) | Owner | ETA (ISO-8601) | Acceptance Criteria | Expected Source | Link (CRIT/KPI/OBJ/RISK/BEH) |
|---|---|---|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED: α, power, n, window if exp.> | <REQUIRED> | <REQUIRED> | <REQUIRED: measurable> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**Closure Checklist (tick all):**  
- [ ] Each TBD has owner + date.  
- [ ] Method has parameters.  
- [ ] Acceptance criteria measurable.  
- [ ] Linked IDs provided.  
- [ ] Provenance logged.

---

## 16) Recommendations for Next Phase
### 16.1 Criteria to Lock — **min 5**
| Criterion | Unit | Target Threshold | Time Frame | Why (Ev→Inf→Imp) | Linked Risks / Dependencies |
|---|---|---:|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

### 16.2 Feasibility Probes — **min 4**
| Probe | Objective | Method (HOW) | Expected Output | WHY (Ev→Inf→Imp) | Linked CRIT/KPI |
|---|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

### 16.3 Early No-Go / Conditional Triggers — **min 4**
| Trigger Condition | Metric / Threshold | Time Window | Consequence | WHY (Ev→Inf→Imp) |
|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

---

## 17) Appendices (Replicability)
### 17.1 Core Formulas — **min 6**
| Metric | Formula | Unit | Parameters | Purpose / Why |
|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

### 17.2 Normalization Tables — **min 3**
| Adjustment | Formula | Reference Source | Assumptions | Why / Implication |
|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

### 17.3 Scoring Rubrics — **min 3**
| Dimension | Scale (0–5) | Anchors | Why |
|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

### 17.4 Search Strategy & Provenance Hygiene — **min 3 queries**
| Channel | Tool / Method | Query Example | Inclusion Criteria | Exclusion Criteria | Reliability Threshold |
|---|---|---|---|---|---|
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

### 17.5 Assumption Log — **min 4**
| Assumption ID | Statement | Source / Rationale | How It Will Be Tested | Dependency / Link |
|---|---|---|---|---|
| ASSUMP-1 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| ASSUMP-2 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| ASSUMP-3 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |
| ASSUMP-4 | <REQUIRED> | <REQUIRED> | <REQUIRED> | <REQUIRED> |

**Final Quality Gate (Do-not-skip checklist)**
| Validation Item | Expected Condition |
|---|---|
| Units & Time Frames | Every numeric value includes both |
| Provenance | Every claim cites ≥1 source + date + reliability |
| Causal Chain | Evidence → Inference → Implication present |
| Triangulation | Decision-critical facts have ≥2 sources or TBD + plan |
| Consistency | No internal contradictions; formulas displayed; limitations disclosed |
| Namespace Integrity | IDs consistent with upstream |
| Criteria Lock Hash | Cited verbatim; deviations carry Change Request |
"""
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            markdown=True,
            output_file="04_explore_report.md",
        )
