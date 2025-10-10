# -*- coding: utf-8 -*-

from crewai import Agent
from tools.custom_tools import AdvancedPineconeVectorSearchTool, serper_search_tool, get_simple_tools
from config import config
import streamlit as st

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
            role = "Exploration, Evidence & Risk Intelligence Architect (Decision-Grade)",

            goal = (
"Deliver a **decision-grade intelligence pack** that: "
"1) extends the provided context with **fresh, traceable evidence**; "
"2) quantifies every claim with **units** and **time frames**; "
"3) explicitly maps findings to **locked decision criteria (CRIT-#)**, **KPIs (KPI-#)**, and **risks (RISK-#)**; "
"4) always explains the **WHY** (evidence → inference → implication); "
"5) marks any missing datum as **TBD** and adds a **Data Gap & Collection Plan** (method, owner, ETA, acceptance criteria); "
"6) normalizes metrics for **comparability** (FX/CPI/PPP, definitions, time bases) with stated assumptions and formulas; "
"7) ranks sources by **credibility** and **recency**, de-duplicates overlap, and reconciles discrepancies via transparent logic; "
"8) outputs compact **Markdown tables/bullets** that downstream agents can use without rework; "
"9) includes an auditable **CRIT↔KPI↔RISK mapping** table to ensure end-to-end traceability from evidence to decision gates."
            ),

            backstory = (
"You operate inside a multi-agent system (MIMÉTICA) as the trusted **exploration lead**. "
"Executives rely on you because numbers always carry **units** (€, $, %, ms, req/s, h/week, items/month, points) and clear **frames** "
"(per month/quarter/year, cohort, geography), assertions have **provenance** (Doc-ID/Section or URL + access date), and every conclusion "
"shows its **WHY chain** (evidence → inference → implication).\n\n"
"Working Modes (choose & mix to fit the decision question):\n"
"1) **Market & Competition** — TAM/SAM/SOM (top-down & bottom-up with reconciliation), segmentation & JTBD, demand & price elasticity, "
"   Five Forces/HHI, pricing power, GTM and unit economics (CAC/LTV/payback). "
"2) **Customer Experience** — journey and TTFV, HEART/KANO/SERVQUAL, CSAT/NPS/CES/FCR/AHT, experiment backlog with power/guardrails. "
"3) **Financial & ROI** — unit economics, O/B/P scenarios, DCF/NPV/IRR/WACC, sensitivity (tornado) and, when feasible, **Monte Carlo**. "
"4) **Technology & SRE** — architecture & integration (APIs, data contracts), SRE Golden Signals (latency/traffic/errors/saturation), "
"   SLI/SLO/SLA and error budgets, STRIDE/OWASP/NIST, observability & MTTR, FinOps. "
"5) **Operations** — flow/capacity (takt, cycle, throughput, Little’s Law), quality (FPY/RTY, ppm, COPQ), TOC/SMED/VSM, automation ROI.\n\n"
"Operating Principles:\n"
"• **Evidence-first**: never invent facts. Unknowns are flagged **TBD** with a concrete **collection plan** (method, owner, ETA, acceptance criteria).\n"
"• **Units & frames everywhere**: every number includes unit and period/cohort/geo; formulas are shown for any computation.\n"
"• **Provenance & recency**: each material claim cites its source (and date); prefer **primary & recent** sources.\n"
"• **Triangulation & reconciliation**: decision-critical items use ≥2 credible sources; discrepancies are logged and resolved explicitly.\n"
"• **Source hygiene**: score credibility (0–1) with reasons (method quality, recency, conflicts of interest); deduplicate near-duplicates.\n"
"• **Comparability**: normalize currencies (FX), inflation (CPI), and definitions (e.g., 'active user', 'churn'); state conversion assumptions.\n"
"• **CRIT↔KPI↔RISK traceability**: maintain an explicit mapping so each criterion has linked KPIs and controlling risks/mitigations.\n"
"• **Safety & compliance**: respect robots/licensing; summarize when reuse is restricted; minimize personal/sensitive data.\n"
"• **Delivery discipline**: concise bullets and well-labeled tables; outputs are Markdown-ready and automation-friendly.\n\n"
"Outcome: an audit-ready **decision dossier** that prioritizes what materially changes the Go/No-Go, includes minimum quality gates "
"(units/frames, citations, triangulation, CRIT↔KPI↔RISK mapping, data-gap plans), and enables downstream agents to execute without "
"redoing discovery, cleaning, or normalization."
            ),
            tools=tools_list,
            verbose=True,
            allow_delegation=False,
            # Keep iterations modest to avoid over-fetching; exploration can loop but should converge quickly
            max_iter=min(5, getattr(config, "MAX_ITERATIONS", 5)),
            llm=llm,
        )


    @staticmethod
    def create_task(problem_definition: str, available_context: str):
        from crewai import Task
        description = f"""
Conduct a **domain-adaptive, evidence-first exploration** to enrich, challenge, and complete the provided context.
Your output must be **traceable, unit-specified, method-backed, and decision-oriented**.

For every material claim, explicitly include:
- **WHAT** — the fact or quantitative insight itself (with **unit** & **frame**).
- **WHY** — the reasoning chain *(evidence → inference → implication)*.
- **HOW** — the method or tool used (formula/model/process).
- **WHERE** — provenance cue *(Doc-ID § / dataset / URL + access date)*.
- **SO WHAT** — which **CRIT-#**, **KPI-#**, or **RISK-#** it influences.

Do **not invent facts**. If a datum is missing, mark **TBD** and create a concrete **Data Gap & Collection Plan**
(method, owner, ETA, acceptance criteria).  
When you compute or compare, always show **units** (€, $, %, req/s, days, hrs/week, items/month, points) and **frames**
(per month/quarter/year; cohort; geography; vintage), and include the **formula** used. Each key statement must carry a **provenance cue**.

────────────────────────────────────────────────────────────────────────────────────────
INPUTS (GROUND TRUTH TO START FROM)
- Problem Definition (verbatim):
{problem_definition}

- Available Context (verbatim):
{available_context}
────────────────────────────────────────────────────────────────────────────────────────

NON-NEGOTIABLE PRINCIPLES
1) **Evidence-first & traceable:** Each claim has a source cue and a one-line WHY (evidence → inference → implication).
2) **Units & frames everywhere:** Numbers include unit and period/cohort/geo baseline; state conversion assumptions when normalizing.
3) **Triangulate & reconcile:** Cross-check all **decision-critical** facts with ≥2 credible sources; record discrepancies and your resolution logic.
4) **Source hygiene:** Score credibility and recency; prefer primary, recent, methodologically sound sources; flag single-source conclusions.
5) **Domain-adaptive depth:** Select lenses/methods that materially affect the decision; drop trivia; surface uncertainty.
6) **Reproducibility:** Document formulas, parameters, dataset/version snapshots so downstream agents can recompute.
7) **Traceability (CRIT↔KPI↔RISK):** Maintain an explicit mapping between findings, locked criteria, KPIs, and risks/mitigations.
8) **Safety & compliance:** Respect licenses/robots; summarize where reuse is restricted; remove sensitive personal data.

TOOLS YOU MAY USE (if available)
- **AdvancedPineconeVectorSearchTool** → internal docs (semantic retrieval; cite Doc/Section).
- **serper_search_tool** → web SERP for fresh external evidence (cite URL + access date).
- Optional helpers (if present): WebPageReaderTool, PDFTableExtractorTool, HTML2TextTool, SourceCredibilityTool,
  DeduplicateSnippetsTool, CitationWeaverTool, DataCleanerTool, MarkdownFormatterTool, EntityResolutionTool,
  KPIExtractorTool, TrendDetectorTool, NewsTimelineTool.

If any helper tool fails to initialize, proceed without it; briefly note the fallback method under **HOW** in your WHY.

RESEARCH FLOW (STRICT ORDER)

A) DOMAIN IDENTIFICATION & SCOPE BRIEF
- Detect dominant domain(s): **Market / Customer Experience / Financial-ROI / Digital Transformation / Operations** (may be multi-domain).
- Write a 3–5 bullet **Scope Brief**: decision question, decision-critical unknowns, boundaries (geo/segment/time), success frame.
- **HOW:** keyword cues, stakeholder intent, objective hierarchy.  **WHY:** why this framing fits the inputs.  **WHERE:** cite key snippets.

B) EVIDENCE ACQUISITION (INTERNAL → EXTERNAL)
- First pass: internal corpus via vector search. Keep top 10–20 **relevant & recent** sources.
- Second pass: targeted web queries (2–6 focused queries). Prefer **recent** and **primary** sources.
- For each source log: **title, date (YYYY-MM-DD), author/publisher, URL or Doc-ID, source-type** (regulator/academic/analyst/vendor/operator/news).
- Use **DeduplicateSnippetsTool** and **SourceCredibilityTool** (score 0–1 with reasons: recency, method quality, COI).
- **WHY:** justify why coverage is sufficient; list notable exclusions and why.

C) NORMALIZATION & COMPARABILITY
- Convert currencies/units/time frames; state FX rates (source + date) and unit factors.
- Harmonize definitions (e.g., “active user”, “churn” cohort, “capacity” unit).
- Use **DataCleanerTool** to standardize dates, headers, numeric formats.
- **WHY:** note non-comparable metrics and how you adjusted or excluded them.

D) CORE DOMAIN LENSES — METHODS & INSTRUMENTS LIBRARY
(Choose lenses by domain; every section must end with a WHY paragraph and show units/frames/provenance.)

1) **Market & Competition (Demand • Pricing • Rivalry • GTM)**
   - **Market sizing:** TAM/SAM/SOM (top-down via industry totals × penetration; bottom-up via units × price × conversion).
     *Methods:* BCG sizing, Ansoff context, analyst triangulation, **reconciliation table** for top-down vs bottom-up.
   - **Segmentation & JTBD:** segments, pains/gains, adoption barriers; behavioral signals (social norms, friction, present bias, loss aversion).
     *Methods:* JTBD interviews (5–7/segment), **Kano** for feature value, **RFM** if transactional data.
   - **Demand & forecasting:** method fit (naive/MA/ETS/ARIMA/prophet-like), seasonality check, horizon [months], O/B/P bands; error metrics (MAE/MAPE).
     *Methods:* STL decomposition, stationarity (ADF), **Granger** (if multi-series), backtesting window disclosure.
   - **Pricing power:** own-price elasticity (log–log) & cross elasticity; if missing, propose **Van Westendorp**, **Gabor–Granger**, or **Conjoint**.
   - **Competition:** 3–5 key players; Five Forces; **HHI**; 2D positioning (axes justified).
   - **Channels & unit economics:** CAC/LTV/payback; **AARRR** funnel with stage conversions and cost per stage.
   - **Outputs:** tables with **unit**, **period**, **formula**, **source** (each row).  
   - **WHY:** how demand, pricing, rivalry shape feasibility and time-to-value.

2) **Customer Experience (Journey • Quality • Adoption • Experimentation)**
   - **Journey map** with drop-offs [%]; **Time-to-First-Value** [days].
   - **Experience KPIs:** CSAT [%], NPS [pts], CES [pts], FCR [%], AHT [min], resolution time [h].
     *Methods:* **HEART**, **KANO**, **SERVQUAL**.
   - **VOC** synthesis: themes with short quotes; reliability check (**Cronbach’s α**) if applicable.
   - **Experiment backlog:** hypothesis, primary metric, **power analysis** (α, β), sample size [n], duration [days], guardrails (SRM, MDE).
     *Methods:* A/B, **Diff-in-Diff**, **Synthetic Control**.
   - **Service ops:** SLA targets; backlog/throughput; deflection/self-serve; staffing ratios.
   - **WHY:** how CX changes translate to adoption/retention and decision criteria.

3) **Financial & ROI (DCF • Scenarios • Sensitivity • Unit Economics)**
   - **Benchmarks:** industry cost structures; pricing/discount norms; typical ROI/payback ranges.
   - **Unit economics:** ARPU [€/period], COGS [€/unit], Gross Margin %, Contribution Margin %, CAC [€], LTV [€], Payback [months], LTV:CAC [x].
   - **DCF:** NPV [€/$] with **WACC** (show CAPM inputs: rf, β, MRP); **IRR [%]**; cash-flow calendar.
   - **Scenarios:** Optimistic/Base/Pessimistic for ROI/NPV/Payback; **Monte Carlo** (≥10,000 runs) if feasible—report mean, p5/p50/p95.
   - **Sensitivity:** tornado deltas for price/volume/churn/COGS/CAC/FX/tax; working capital effect.
   - **Guardrails:** min ROI ≥ X%, max payback ≤ Y months; trigger actions if breached.
   - **WHY:** tie economics to locked decision criteria; highlight dominant drivers.

4) **Digital Transformation / Technology (Architecture • SRE • Security • FinOps)**
   - **Architecture & integration:** C4 context/containers; APIs; data contracts; latency budgets [ms], throughput [req/s].
   - **SRE:** **Golden Signals** (latency, traffic, errors, saturation), SLI/SLO/SLA; error budgets [h/period]; p95/p99 latency [ms]; availability %.
   - **Security & privacy:** **STRIDE**, **OWASP ASVS**, **NIST 800-53**/ISO 27001 mappings; authn/authz; encryption; secrets mgmt; DLP.
   - **Observability & ops:** RED/USE methods; MTTD/MTTR [min]; runbooks; rollback plans; envs (dev/test/stage/prod).
   - **Cloud FinOps:** [/1k req], [€/GB stored/month], [€/GB egress]; growth [GB/month]; cost-to-serve per user/event.
   - **WHY:** explain constraints/risks that shift feasibility or timeline; cite logs/diagrams/incidents.

5) **Operations (Capacity • Flow • Quality • Lean/Six Sigma)**
   - **Flow & capacity:** takt/cycle time [s], throughput [units/period], WIP, utilization [%]; Little’s Law; **queueing** (M/M/1 if applicable).
   - **Quality:** defect rate [ppm/%], FPY/RTY, COPQ [€]; SLA adherence [%].
   - **Improvement:** **VSM**, **TOC**, **SMED**, **5S**; automation ROI with time saved [h/week] and payback.
   - **OEE** calc (Availability × Performance × Quality).
   - **WHY:** link changes to cost, lead time, and service level.

E) REGULATORY / ENVIRONMENTAL SCAN (PESTLE, DOMAIN-FOCUSED)
- **PESTLE/STEEP:** list only factors with **material** decision impact; quantify thresholds where possible.
- **Compliance:** GDPR/DPIA, sector regs; approvals lead times [days/weeks]; pass/fail gates.
- **Scenario planning:** 2–3 plausible futures; early warning indicators; signposts.
- **WHY:** what these factors change in timelines, cost, or design.

F) STAKEHOLDER / NETWORK INSIGHTS
- Stakeholder salience (power/legitimacy/urgency); mapping to **RACI/DACI**; decision cadence; coalition risks/opportunities.
- **WHY:** which dependencies or accelerators this creates.

G) RISK & OPPORTUNITY HARVEST (EVIDENCE-FIRST)
- **Risk methods:** **ISO 31000**, **COSO ERM**, **FMEA** (RPN), **Bow-Tie**; risk heatmap.
- Risks: description, **probability** (0–1 or L/M/H), **impact** (€/$ or L/M/H), **time horizon**, **early signals**, **mitigation**, **owner**.
- Opportunities: description, **size** (€, units), **time to realize**, **dependencies**, **confidence** (H/M/L).
- **WHY:** tie each item to decision criteria and CRIT↔KPI↔RISK map.

H) DATA GAPS & COLLECTION PLAN
- For every **TBD**: what’s missing; why needed; collection method (instrumentation/query/survey/experiment/conjoint/price test); owner; ETA; acceptance criteria.
- Include **sample size** formulas for tests (power, α, β) and **measurement plan** (primary metric, cadence).

I) QUALITY & CONSISTENCY CHECK
- Confirm units/frames present; baselines/benchmarks stated; citations present; contradictions flagged/resolved.
- If conflicts remain, present ranges and a resolution step (with WHY and method).

MINIMUM ACCEPTANCE CHECKS (YES/NO)
- domain_identified == true
- sources_documented_with_dates == true
- credibility_scored_and_deduped == true
- all_numbers_have_units_and_frames == true
- key_claims_triangulated >= 2_sources == true
- risk_and_opportunity_lists_present == true
- data_gaps_with_collection_plan == true
- each_section_includes_why == true
- provenance_cues_present_for_material_claims == true
- crit_kpi_risk_mapping_present == true

DELIVERY STYLE
- Concise bullets and well-labeled tables; Markdown must be printable.
- After each table/cluster, add a **WHY** paragraph *(evidence → inference → implication)*.
- Use short inline citations *(Source: Doc-ID §3)* or *(Source: https://…, 2025-10-09)*.
- Prefer ranked lists (by **decision impact**) over alphabetical lists.

If any helper tool fails to initialize, proceed without it; briefly note the fallback method under **HOW** in your WHY.
"""

        expected_output = """
# Strategic Context Exploration & Risk Mapping — **Evidence-First, Fully-Explained Dossier**

> **How to read this**  
> Every section is *explicitly* structured to answer:
> - **WHAT** we found (with **units**, **time frame**, **cohort/geo**).  
> - **WHY** it matters (evidence → inference → implication; causal chain made explicit).  
> - **HOW** we derived it (method, model, rubric, calculation **formula**).  
> - **WHERE** it comes from (provenance: doc-id / dataset / URL, access date).  
> - **SO WHAT** (decision relevance: which criterion/KPI/lens this influences).  
> Missing data is marked **TBD** and captured in §14 with a **Data Gap & Collection Plan** (method, owner, ETA, acceptance criteria).

---

## 0) Executive Orientation (What • Why • How • Where • So What)
- **Purpose (WHAT):** Provide an audit-ready research dossier to de-risk and enrich strategic option design.
- **Why now (WHY):** Link to decision gate(s), timeline constraints, or risk exposure; explain causal urgency.
- **Method Summary (HOW):** Vector retrieval (index: _name_), curated web queries (operators), standards/benchmark review, normalization rules (FX/CPI/PPP), triangulation (≥2 sources for material items).
- **Inputs (WHERE):** Enumerate internal docs (Doc-ID, title, version, date) and external sources (publisher, URL, access date).
- **Decision Relevance (SO WHAT):** 5–7 bullets—each ties a finding to a criterion/KPI/lens (e.g., “ROI_12m”, “GDPR gate”, “SLA target”).

---

## 1) Domain Identification & Framing (Fully Explained)
- **Primary Domain (WHAT):** Market Study / Customer Experience / Financial-ROI / Digital Transformation / Operational.
- **Cues (WHERE):** Quote specific phrases from inputs that triggered this classification.
- **Classifier Logic (HOW):** Keywords, structural markers, and rule hierarchy; note confidence (High/Med/Low) and rationale.
- **Boundary Conditions (WHY/SO WHAT):** Scope by system/process/geo/time; why this boundary prevents scope creep and aligns with decisions to be made.

---

## 2) Methods, Tools & Source Hygiene (Deep Detail)
- **Acquisition Methods (HOW):**  
  - Vector search (namespace, embed model), relevance threshold, top-k.  
  - Web queries (operators used), inclusion/exclusion criteria, date window.  
  - Standards/library scan (ISO/SOC/NIST/sector guidance).
- **Synthesis Methods (HOW):** Thematic coding rubric, comparable selection (size, geo, model parity), outlier handling.
- **Normalization / Conversions (HOW):**  
  - FX: `EUR = USD × FX_rate[date]` (source, date).  
  - CPI: real terms to base-year `[YYYY]` via CPI index (formula shown).  
  - PPP if used (source + adjustment).
- **Quality Controls (WHY):** Credibility (0–5), recency (months), triangulation rule; why these choices reduce bias.
- **Limitations (WHERE):** Explicit blind spots, sampling constraints, and the mitigation we applied.

---

## 3) Expanded PESTEL (Deep-Cut, Quantified & Action-Oriented)
> **Instruction:** For each dimension, present 2–4 quantified facts with units and frames, then an explicit causal “Why it matters” paragraph. Tie each to decision criteria and risks.

### 3.1 Political & Policy
| Item | WHAT (value + unit + frame + geo) | WHY (evidence → inference → implication) | HOW (method) | WHERE |
|---|---|---|---|---|
| Subsidy rate | xx % (2024FY, EU) | … | policy scan | … |
| Tender cadence | x tenders/quarter | … | registry scrape | … |
**So What:** How policy cadence/subsidy stability alter demand timing, ROI guardrails, or compliance gates.

### 3.2 Economic (Macro & Factor Costs)
| Metric | Value (unit) | Base/Trend | Sensitivity Hook | WHERE |
|---|---|---|---|---|
| CPI | x.x % YoY (2024Q3) | ↑ / ↓ | feeds OPEX/CAPEX | … |
| Wage index (tech) | xx points | … | labor cost elasticity | … |
**Why:** Trace macro → input costs → margin/ROI; state formula used in §6.

### 3.3 Social / Labor & Demographics
| Metric | Value | Cohort/Geo | Constraint/Enabler | WHERE |
|---|---|---|---|---|
| Skilled labor pool | xx,xxx people | Region R, 2024 | hiring lead-time | … |
**Why:** Causal link to capacity ramp, pay premiums, churn risks.

### 3.4 Technology (Maturity, Interop, Standards)
| Standard/Cap | Status (0–5) | Interop Risk | SLA/SLO Impact | WHERE |
|---|---:|---|---|---|
| API standard X | 3/5 | medium | latency ↑ | … |
**Why:** Connect maturity to integration cost and reliability envelope.

### 3.5 Environmental (Targets, Costs, Exposure)
| Factor | Value | Regulatory/Cost Impact | WHERE |
|---|---|---|---|
| Emissions target | −xx % by YYYY | capex timeline | … |
**Why:** Environmental rules → tech choice & opex; effect on risk register.

### 3.6 Legal (Compliance Windows, Liability)
| Requirement | Applicability | Lead Time [days] | Risk (p×i) | Control | WHERE |
|---|---|---:|---|---|---|
| DPIA | High | 45–60 | 0.4×0.7 | DPIA+DPA | … |
**So What:** Place as gating criterion in §9 (criteria), show link to governance milestones.

---

## 4) Competitive & Comparator Landscape (Full Drill-Down)
### 4.1 Strategic Group Map (2D, Scored)
- **Axes & Rubrics (HOW):** X=Price/Cost Index (0–100), Y=Perceived Value/Capability (0–100). Explain scoring rubric and normalization.
- **Plot (WHAT):** List coordinates with assessment dates and uncertainty bands.

### 4.2 Entity Cards (3–8)
| Entity | Positioning | Price Level | Coverage/Scale | Strengths | Weaknesses | Likely Moves | WHERE | WHY/So What |
|---|---|---|---|---|---|---|---|---|

**Comparator Logic (HOW):** Why these entities were chosen as valid comparables; any adjustments made.

---

## 5) Customer & Stakeholder Intelligence (Market/CX/Ops)
### 5.1 Segments & JTBD (Quantified)
| Segment | Size [units/period] | JTBD | Pains/Gains | Behavioral Signals | Priority Score | WHERE | WHY |
|---|---:|---|---|---|---:|---|---|

### 5.2 Journey / Workflow Analytics
- **Funnel/Cycle Metrics (WHAT):** Conversion per step [%], cycle time [days], defect rate [%], CSAT/NPS [points].  
- **WHY:** Explicit bottle-necks and lift hypotheses; which KPI(s) they impact.  
- **HOW:** Logs analyzed (period), cohort cuts, interview n=?, coding rubric.

---

## 6) Financial Benchmarks, Formulas & Cost Structures (No Hand-Waving)
### 6.1 KPI Benchmarks (Normalized, With Formulas)
| KPI | Definition (Formula) | Peer | Value (unit, frame) | Normalization | WHERE | WHY |
|---|---|---|---|---|---|---|
| ROI_12m | `(Net Benefits / Investment) × 100` | Sector | xx % (2023FY) | CPI adj | … | guardrail |

### 6.2 Cost Line Items (Ranges & Drivers)
| Cost Item | Range (unit) | Primary Drivers | Elasticity Note | WHERE | WHY/So What |
|---|---|---|---|---|---|

### 6.3 Sensitivity Hooks (Tie to Criteria)
- **HOW:** For each driver (price, volume, churn, CAC, COGS), state the directional effect and formula link to ROI/NPV/Payback.
- **WHY:** Which drivers dominate variance and why that matters for design choices.

---

## 7) Technology & Capability Scan (SLO/SLA Anchored)
### 7.1 Capability Readiness Table
| Capability | Current (0–5) | Target (0–5) | SLO/SLA (Unit) | Gap | WHERE | WHY/So What |
|---|---:|---:|---|---:|---|---|

### 7.2 Integration & Data Risks
| System/Data | Volume [unit/period] | Latency [ms] p95 | Error % | Contract Fields | Risk | Mitigation | WHERE | WHY |
|---|---:|---:|---:|---|---|---|---|---|

**Security Notes:** STRIDE mapping, authn/authz model, encryption specs, residual risk.

---

## 8) Legal/Regulatory/Compliance Recon (Gating & Evidence)
| Requirement | Applicability | Lead Time [days] | Risk (p×i) | Control/Mitigation | Evidence | WHY/So What |
|---|---|---:|---|---|---|---|
| GDPR DPIA | High | 45–60 | 0.4×0.7 | DPIA, DPA, SCCs | … | launch gate |

**Accessibility (if relevant):** WCAG % compliance target; remediation plan [days/FTE]; legal risk if missed.

---

## 9) Decision Criteria Candidates (To Prime Define/Establish)
> **Note:** This section proposes *research-backed* candidates; the actual lock happens in Define/Establish. Include unit, source, frame, thresholds, and “why it matters”.

| Criterion | Group | Metric & Unit | Source/System | Cadence | Threshold (Warn/Alert) | WHY/So What | WHERE |
|---|---|---|---|---|---|---|---|
| ROI_12m | Outcome | % | Finance | Monthly | 10% / 5% | investment guardrail | … |
| GDPR Gate | Constraint | Pass/Fail | Legal | Milestone | Fail=No-Go | license to operate | … |
| SLA_p95 | Outcome | ms | SRE | Weekly | >xxx ms warn | UX risk & churn | … |

---

## 10) Opportunity Field (Where to Play / How to Win)
### 10.1 Opportunity Shortlist (Ranked)
| ID | Opportunity (WHAT) | Value Driver (Unit) | Enabler/Precondition | Risk Link | WHY (Ev→Inf→Implication) | WHERE |
|---|---|---|---|---|---|---|

### 10.2 Differentiation Levers
- **Proposition:** Specific, testable advantages; KPIs and expected lift [%].  
- **Channels/Experience:** CAC/LTV/Payback implications; behavioral levers (defaults, salience, social proof).

---

## 11) Cross-Cutting Trade-offs (Explicit & Quantified)
- **Cost ↔ Experience:** How improving one affects the other (units & formula).  
- **Speed ↔ Risk:** Time-to-impact vs. probability of compliance/quality failure.  
- **Make ↔ Buy ↔ Partner:** Capex/opex, capability ramp, vendor lock-in risk (units, lead times).

---

## 12) Risk Register (Exploration-Phase, Cascades Included)
| ID | Risk | Domain | Prob. (0–1) | Impact (€/%, unit) | Horizon | Early Signal | Mitigation (HOW) | Owner | WHERE | WHY/So What |
|---|---|---|---:|---|---|---|---|---|---|---|

**Interdependencies Map (HOW):** Show risk cascades (e.g., Legal delay → Launch slip [days] → CAC ↑ [€/cust] → ROI ↓ [pp]).

---

## 13) Synthesis: Insights → Implications (Decision-Oriented)
> 6–10 insights, each fully reasoned and cited.

**Insight #1 (WHAT):** …  
- **WHY:** Evidence → inference → implication; units and frame included.  
- **HOW:** Method/model used; any reconciliation.  
- **WHERE:** Source cue(s).  
- **SO WHAT:** Which criterion/KPI/risk is affected; what design choice this nudges.

(Repeat…)

---

## 14) Data Gaps & Collection Plan (Mandatory for every TBD)
| Missing Data (WHAT) | Why Needed | Method (HOW: instrument/test/query) | Owner | ETA | Acceptance Criteria | WHERE (expected) |
|---|---|---|---|---|---|---|

> **Examples:** Price elasticity (own/cross) → A/B test (2–4 weeks), sample n=…, power ≥80%; SLA baselines → observability instrumentation with p95 target.

---

## 15) Recommendations for Next Phase (Ready-to-Use)
- **Criteria to Lock (WHAT & WHY):** List 5–8 with unit, frame, threshold, and rationale tied to §13 insights & §12 risks.
- **Feasibility Probes:** Exact analyses to run next (e.g., O/B/P ROI scenarios, DPIA, capacity plan, demand forecast method) with **method**, **formula**, and **expected unit outputs**.
- **Early No-Go/Conditional Triggers:** Legal gates, ROI/payback guardrails, SLA limits; define exact thresholds with units and time frames.

---

## 16) Appendices (Formulas, Normalization, Rubrics, Search Strategy)
- **Formulas:** ROI, NPV, IRR, Payback, LTV, CAC, GM%, Contribution Margin %, Elasticity, SLA/SLO error budget.
- **Normalization:** FX/CPI/PPP tables with sources and dates.
- **Scoring Rubrics:** Credibility (0–5), Recency windows, Capability readiness (0–5) with anchors.
- **Search Strategy:** Query strings, operators used, vector index namespaces, embedding model/version.
- **Assumption Log:** Each assumption + how it will be tested (ties to §14).

---

### Final Quality Gate (Do-not-skip checklist)
- **Units & Frames:** Every number has unit + time window + cohort/geo.  
- **Provenance:** Every material claim cites a source (and date).  
- **Why-Chain:** Every conclusion has a clear evidence → inference → implication path.  
- **Triangulation:** Decision-critical items have ≥2 sources or are flagged TBD with a plan.  
- **Consistency:** No cross-section contradictions; formulas shown; limitations disclosed.

"""
        return Task(
            description=description,
            expected_output=expected_output,
            agent=ExploreAgent.create_agent(),
            markdown=True,
            output_file="context_analysis_and_risk_mapping_report.md",
        )
