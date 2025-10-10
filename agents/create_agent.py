# -*- coding: utf-8 -*-

from crewai import Agent
from config import config
import streamlit as st

# Optional import of custom tools
try:
    from tools.custom_tools import (
        MarkdownFormatterTool,
        CodeInterpreterTool,
        strategic_visualization_generator,
    )
    _TOOLS_IMPORT_OK = True
except Exception:
    _TOOLS_IMPORT_OK = False



class CreateAgent:
    """Agent responsible for creating high-quality, decision-ready strategic options
    with traceability (units, timeframes, sources) and business applicability.
    """

    @staticmethod
    def create_agent():
        # --- Model ---
        selected_model = config.validate_and_fix_selected_model()
        model_cfg = config.AVAILABLE_MODELS[selected_model]
        provider = model_cfg["provider"]

        # --- LLM ---
        llm = None
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
            raise ValueError(f"Unsupported provider: {provider}")


        # --- Tools: lean, local-only (formatter + calculations + charts) ---
        tools_list = []
        if _TOOLS_IMPORT_OK:
            candidates = [
                MarkdownFormatterTool(),          # salida markdown limpia
                CodeInterpreterTool(),            # cálculos/tablas rápidos
                strategic_visualization_generator # función-tool para gráficos
            ]
            # De-duplicado por nombre seguro
            seen, tools_out = set(), []
            for t in candidates:
                try:
                    name = getattr(t, "name", getattr(t, "__name__", repr(t)))
                except Exception:
                    name = repr(t)
                if name not in seen:
                    seen.add(name)
                    tools_out.append(t)
            tools_list = tools_out

        
        return Agent(
            role="Strategic Option Architect (DECIDE › Create) — turns messy context into three decision-ready, auditable alternatives aligned to the company’s realities.",

            goal=(
"Produce exactly three domain-appropriate strategic/tactical options that leadership can choose between now. "
"Each option must: frame scope and success conditions; quantify value mechanics with units/timeframes; "
"state explicit assumptions, constraints, and dependencies; detail resources, capabilities, and cost envelopes; "
"map risks with probability×impact, early signals, and mitigations; and outline a phased implementation path with indicative timings. "
"Define KPIs and monitoring cadence; show alignment to locked/target decision criteria; and include sensitivity hooks (what moves ROI/NPV/Payback). "
"Deliver artifacts usable by downstream agents without rework: option cards, a three-way criteria-fit table, risk-register slice, and a clear recommendation rule (when A vs. B vs. C should win) with evidence cues."
    ),
            backstory=(
"You operate in DECIDE › Create as the Strategic Option Architect. Your craft is turning messy, partial, "
"and cross-domain inputs into three auditable, business-realistic alternatives that executives can act on now. "
"You think like a strategist and a builder: you frame scope crisply, quantify value flows with units/timeframes, "
"and expose the trade-offs, constraints, and dependencies that actually govern feasibility.\n\n"
"You adapt to the problem’s dominant domain (Market, Customer Experience, Financial/ROI, Digital Transformation, "
"Operations), but never default to generic patterns. Instead, you assemble options that reflect the company’s "
"current capabilities, regulatory boundaries, tech stack, data reality, and budget. You always connect claims to "
"provenance cues (doc-ID/URL + access date), keep numbers normalized and comparable, and show how sensitive the "
"outcomes are to the few variables that really move ROI/NPV/Payback.\n\n"
"You insist on decision-grade clarity: explicit assumptions, early warning indicators, risk probability×impact with "
"mitigations, phase plans with indicative timings, and the minimal resources/FTEs/cost envelopes to get started. "
"You design measurable success (KPIs with cadence and owners) and write recommendation rules that make it obvious "
"when Option A vs. B vs. C should win. You collaborate upstream with Explore/Define agents (for evidence and criteria) "
"and downstream with Implement/Evaluate agents (for plans and monitoring) so your outputs can be used without rework."
            ),
            tools=tools_list,
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE,
            llm=llm,
        )
    
    @staticmethod
    def create_task(problem_definition: str, context_analysis: str):
        from crewai import Task
        description=f"""
DECIDE › Create — Build **three decision-ready alternatives** with explicit WHY-chains and hard data support.
Your job is to turn messy context into **auditable options** that executives can choose between today.

Inputs (verbatim)
- Problem Definition:
{problem_definition}

- Context & Risk Analysis (from Explore/Define):
{context_analysis}

Core Mandate
Produce **exactly three** options:
  • **Option A — Pragmatic / baseline**: high feasibility, leverages current capabilities.
  • **Option B — Ambitious / step-change**: higher upside with managed risk.
  • **Option C — Non-obvious / contrarian**: unconventional angle that could unlock asymmetric value
    (e.g., re-sequencing, make→buy→partner switch, pricing experiment, governance hack, capability trade).

Non-Negotiables (Evidence & WHY)
1) **WHY-chain for every material claim** → *Evidence → Inference → Implication* (who/what changes, KPI/criterion affected).
2) **Provenance for facts** → doc-ID/section or URL + access date; show **recency** and **source type** (operator, regulator, academic, vendor, analyst, news).
3) **Triangulate decision-critical numbers** with ≥2 credible sources or mark **TBD** with a **Data Gap & Collection Plan** (method, owner, ETA, acceptance criteria).
4) **Units & Frames everywhere** → €/month, %, days, req/s; cohort/geo/time window stated; show **normalization** (FX/CPI/PPP) and **formula** when computed.
5) **Comparability** → same definitions, periods, and units across options; declare adjustments and residual uncertainty.

Process (do in order; keep sections in output)
A) Context Squeeze & Domain Detection
   - Identify dominant domain(s): Market / Customer Experience / Financial-ROI / Digital Transformation / Operations (multi-domain allowed).
   - Write a **Scope Brief** (3–6 bullets): boundaries, success frame, decision gates, constraints (budget/capability/regulatory), non-goals.
   - **WHY paragraph**: why this framing fits, citing the 1–3 most determinative cues from inputs (with provenance).

B) Option Synthesis (exactly 3)
For **each** option include a compact **Option Card** with:
   1) **Name & One-line Thesis** — what it is, who benefits, why now.
   2) **Scope & Success Conditions** — what’s in/out; “done means”; guardrail gates.
   3) **Value Mechanics (with units/timeframes)** — revenue, cost, risk, CX, capacity; show formulas (ROI, NPV, Payback).
   4) **Assumptions / Constraints / Dependencies** — explicit; state confidence (H/M/L) and sensitivities.
   5) **Capabilities & Resources** — org/teams/FTE, skills, tooling/vendor needs; **cost envelope** by phase (order-of-magnitude).
   6) **Implementation Path (phased)** — phases with indicative timings; critical path; earliest value.
   7) **Risk Register Slice** — top 5 risks with Probability×Impact (0–1 or L/M/H × €/unit), early signals, mitigations, owner.
   8) **KPIs & Monitoring Cadence** — primary/secondary KPIs; unit, target/band, cadence, data source/owner.
   9) **Sensitivity Hooks (3–5 drivers)** — what moves ROI/NPV/Payback most; note elasticities or test required.
  10) **WHY paragraph** — connect evidence to inference to implication; include compact citations.

Special Requirements for Option C (Contrarian)
- Must be **plausible but non-traditional**, e.g.:
  • invert sequence (pilot → policy vs policy → pilot), 
  • monetize a by-product data exhaust, 
  • flip make/buy/partner, 
  • price experimentation (metered, outcome-based, risk-share),
  • governance or process redesign that collapses lead time.
- Provide **Premortem** (how it fails + leading indicators) and **Counterfactual** (what we learn even if it “fails”).

C) Comparable Economics & Normalization
- Present a **summary table** across options for: Investment [€], Opex [€/period], Net Benefit [€/period], ROI [%], Payback [months], NPV [€] @WACC, IRR [%], CX/Service KPIs, Compliance gates.
- State normalization rules (FX rate/date source; CPI base year; scope adjustments). Show formulas inline or in Appendix.

D) Criteria Fit (3-way)
- If Define already locked criteria, use them; else propose 6–10 **decision criteria** (Outcome/Constraint/Capability) with unit, target/threshold, weight (if known).
- Build a **3-way Criteria-Fit Table** with short WHY per row and citations where facts are used.

E) Recommendation Rule
- Write **“Choose A vs. B vs. C when …”** based on observable thresholds (e.g., ROI_12m ≥ X%, Payback ≤ Y months, DPIA pass, SLO p95 ≤ Z ms, budget window).
- Include **tie-breakers** and **early warning triggers** to revisit the choice.

F) Data Gaps & Collection Plan
- Consolidate all TBDs into a table: *What’s missing | Why needed | Method (instrument/test/query) | Owner | ETA | Acceptance | Expected source*.
- For tests: include **power assumptions** (α, β), sample size n (if estimable), and guardrails.

Deliverables (must appear in output)
1) **Three Option Cards** (A/B/C) with all 10 fields above.
2) **Comparable Economics Summary** (normalized) with formulas noted.
3) **3-way Criteria-Fit Table** (with short WHY per criterion).
4) **Risk Register Slice** per option + consolidated view of cross-cutting risks.
5) **Recommendation Rule** (A vs. B vs. C) + early triggers.
6) **Data Gap & Collection Plan**.
7) **Appendix**: formulas, normalization sources (FX/CPI/PPP), key citations (short form).

Tables — Minimum Structure
- **Comparable Economics**
  | Option | One-line Thesis | CapEx [€] | OpEx [€/period] | Net Benefit [€/period] | ROI [%] | Payback [months] | NPV [€] @WACC | IRR [%] | CX/SLA Key KPI | Provenance |
- **Criteria-Fit**
  | Criterion (unit) | Target/Threshold | Weight | A | B | C | WHY (1-line) | Source |
- **Risk Slice (per option)**
  | ID | Risk | Prob (0–1/L-H) | Impact (€/unit/L-H) | Horizon | Early Signal | Mitigation | Owner |
- **Data Gaps**
  | Missing Data | Why Needed | Method | Owner | ETA | Acceptance | Expected Source |

Formatting & Style
- Markdown, concise bullets, clear tables; after each table add a **WHY** paragraph (evidence → inference → implication).
- Every computed figure shows a **formula** and period/frame; every fact lists a compact **provenance cue**.

Acceptance Checklist (all must be YES)
- exactly_three_options == true
- each_option_has_units_and_timeframes == true
- each_option_has_assumptions_constraints_dependencies == true
- phased_implementation_path_present == true
- risk_register_slice_with_probability_times_impact == true
- kpis_with_targets_and_cadence_and_owner == true
- comparable_economics_normalized_with_formulas == true
- three_way_criteria_fit_table_present == true
- recommendation_rule_with_thresholds_and_triggers == true
- option_c_is_non_obvious_but_plausible_with_premortem == true
- data_gaps_with_collection_plan == true
- provenance_cues_present_for_material_claims == true
"""
        expected_output = """
# DECIDE › Create — Strategic Options Dossier (Decision-Ready, Auditable)

> **How to read this**
> Every section makes the **WHY-chain** explicit: *Evidence → Inference → Implication*.  
> All material facts include **provenance cues** (Doc-ID/§ or URL + access date).  
> All numbers have **unit** and **timeframe**, with any **normalization** (FX/CPI/PPP) stated.

---

## 0) Executive Summary (one page)
- **Problem Domain(s):** [Market / CX / Financial-ROI / Digital Transformation / Operations] — *why this framing* (1–2 lines + source cues).
- **Options Produced:** 3 (A=Pragmatic, B=Ambitious, C=Contrarian).  
- **Topline Economics (normalized):** ROI_12m [%], Payback [months], NPV @WACC [€], IRR [%] — *show base assumptions briefly + formula refs*.  
- **Key Risks:** top 3 cross-option risks with (p×i) and early signals.  
- **Recommendation Snapshot:** “Choose **[A|B|C]** if **[thresholds]**; otherwise **[tie-break]**.”  
- **Decision Horizon:** “[date/quarter]” with gating dependencies (e.g., DPIA, budget window).

**WHY (2–4 bullets):** Concise evidence→inference→implication justifying the shortlist & ranking.

---

## 1) Context Squeeze & Scope Brief
- **Scope & Boundaries:** in/out, cohorts/geo, time window, non-goals.  
- **Success Conditions:** what “good” means (units/targets).  
- **Constraints:** budget, capability, regulatory, tech stack/data reality.  
- **Decision Gates:** compliance, financing, partner commitments.  

**WHY:** Why this frame fits (quote the 1–3 determinative cues from inputs).  
**Provenance:** *(Doc-ID/§ or URL + access date)*

---

## 2) Three Option Cards (A/B/C) — *Complete each card below*
> A = **Pragmatic/baseline**; B = **Ambitious/step-change**; C = **Non-obvious/contrarian** (must be plausible + learning-rich).

### 2.A Option A — [Name]
1) **Thesis (one-liner):** [what, who benefits, why now]  
2) **Scope & Success:** [what’s in/out], “done means” [KPI targets with units/time]  
3) **Value Mechanics (unit/time):** revenue, cost, risk, CX/capacity drivers with **formulas** (ROI, NPV @WACC, Payback)  
4) **Assumptions / Constraints / Dependencies:** explicit; confidence H/M/L; cite data; list **sensitivity hooks** (top 3–5 drivers)  
5) **Capabilities & Resources:** teams/FTEs/skills, vendor/tooling, **cost envelope** by phase (CapEx/OpEx with unit/time)  
6) **Implementation Path (phased):** phases, indicative timings, critical path, earliest value  
7) **Risk Register Slice (top 5):** p×i, horizon, early signals, mitigations, owner  
8) **KPIs & Monitoring:** primary/secondary KPI (unit, target/band, cadence, data source/owner)  
9) **Provenance Cues:** compact list of sources that anchor the economics & constraints  
10) **WHY paragraph:** evidence → inference → implication (which decision criterion is affected)

### 2.B Option B — [Name]
(Repeat items 1–10; emphasize the step-change levers, added uncertainty, and risk-reduction design.)

### 2.C Option C — [Name] (Contrarian)
(Repeat items 1–10; **plus**:)
- **Premortem:** top 3 ways it fails + leading indicators  
- **Counterfactual Value:** what we learn even if outcomes underperform (option value, data, partner signals)

---

## 3) Comparable Economics (Normalized)
> Show base, and if used, O/B/P bands or a 10k-run Monte Carlo summary (mean, p5, p50, p95).

**Normalization Rules:** FX rate (source/date), CPI base year (source), any scope reconciliation/PPP.

| Option | One-line Thesis | CapEx [€] | OpEx [€/period] | Net Benefit [€/period] | ROI_12m [%] | Payback [months] | NPV @WACC [€] | IRR [%] | CX/SLA Anchor (unit) | Assumption Notes | Provenance |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|

**Formulas used:**  
- `ROI = (Net Benefits / Investment) × 100`  
- `NPV = Σ_t (CF_t / (1+WACC)^t)` — state WACC inputs (rf, β, MRP)  
- `Payback = months until cum. net CF >= 0`  
(If elasticities used, state model/link.)

**WHY (3–5 bullets):** what drives the differences; comparability caveats; uncertainty bands.

---

## 4) Criteria-Fit (Three-Way)
> If Define locked criteria, use them; otherwise propose 6–10 and mark (Proposed).

| Criterion (unit) | Type (Outcome/Constraint/Capability) | Target/Threshold | Weight | A | B | C | One-line WHY | Source |
|---|---|---|---:|---:|---:|---:|---|---|

**HOW:** scoring rule & scaling; **WHY:** which criteria dominate the choice and why.

---

## 5) Consolidated Risk View (Cross-Option)
> Summarize overlapping or cascading risks and their systemic effects.

| ID | Risk | Option(s) | Prob (0–1 or L-H) | Impact (€/unit or L-H) | Horizon | Early Signal | Mitigation (HOW) | Owner |
|---|---|---|---:|---|---|---|---|---|

**Interdependencies:** short map (e.g., “Reg delay → Launch slip [days] → CAC ↑ [€/cust] → ROI ↓ [pp]”).  
**WHY:** which risks materially shift the recommendation and under what signals.

---

## 6) Recommendation Rule (Operationalized)
- **Choose A if:** [observable thresholds; e.g., ROI_12m ≥ X%, Payback ≤ Y months, DPIA pass, SLO p95 ≤ Z ms].  
- **Choose B if:** [thresholds]  
- **Choose C if:** [specific contrarian conditions where asymmetric upside or learning value dominates]  
- **Tie-breakers:** [ranked]  
- **Early Triggers to Revisit:** conditions that nullify current choice.

**WHY:** connect thresholds to criteria weights and sensitivity drivers.

---

## 7) Data Gaps & Collection Plan (Mandatory for each TBD)
| Missing Data (WHAT) | Why Needed | Method (instrument/test/query) | Owner | ETA | Acceptance Criteria | Expected Source |
|---|---|---|---|---|---|---|

*(For experiments include α, β, power, MDE, guardrails; for instrumentation include SLO target & sampling plan.)*

---

## 8) Appendices (Reproducibility & Provenance)
- **A. Formulas & Parameterization:** ROI/NPV/IRR/Payback, elasticity models, KPI definitions.  
- **B. Normalization Tables:** FX/CPI/PPP (source + access date).  
- **C. Source Register:** title, publisher/author, date (YYYY-MM-DD), URL or Doc-ID/§, source type (operator/regulator/academic/vendor/analyst/news), recency note.  
- **D. Search/Index Notes (if used):** vector namespaces, query operators, inclusion/exclusion criteria.  
- **E. Assumption Log:** each assumption + sensitivity tag + how it will be tested (links to §7).

---

## Final Quality Gate (all must be YES)
- exactly_three_options == true  
- each_option_has_units_and_timeframes == true  
- assumptions_constraints_dependencies_explicit == true  
- phased_implementation_path_present == true  
- risk_slice_with_probability_times_impact_present == true  
- kpis_with_targets_cadence_owner_present == true  
- comparable_economics_normalized_with_formulas == true  
- three_way_criteria_fit_table_present == true  
- recommendation_rule_with_thresholds_and_triggers == true  
- option_c_is_contrarian_but_plausible_with_premortem == true  
- data_gaps_with_collection_plan_present == true  
- provenance_cues_present_for_material_claims == true

"""

        return Task(
            description=description,
            expected_output=expected_output,
            agent=CreateAgent.create_agent(),
            markdown=True,
            output_file="intervention_options.md"
        )