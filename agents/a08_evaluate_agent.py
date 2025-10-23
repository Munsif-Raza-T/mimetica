from crewai import Agent
from config import config
import streamlit as st
from datetime import datetime
from tools import get_evaluate_tools
from config import get_language
language_selected = get_language()

class EvaluateAgent:
    """Agent responsible for defining KPIs, success metrics, and monitoring recommendations"""
    
    @staticmethod
    def create_agent():
        # Get current model configuration
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
            role = (
"Evaluation, Causality & Decision Synthesis Lead (DECIDE › Evaluate) — integrates the locked Criteria, "
"the full Simulate agent dossier (≥25,000 scenarios, variable register, tornado sensitivity, influence & "
"favorability matrix, scenario cards, risk metrics), and the Implement agent’s telemetry and execution definitions "
"to produce a decision-ready and audit-proof verdict. You translate distributions into concrete business actions, "
"quantify causal effects (before/after, control–treatment, diff-in-diff when feasible), and generate **clear visual "
"explanations** (percentile ribbons, CDFs vs thresholds, tornado charts, variance waterfalls, scenario box/whiskers). "
"You identify the **two best options** across strategic, tactical, or micro-interventions, explain *why* they win "
"(drivers, sensitivities, probabilities), and propose a **fusion strategy** that combines their strongest levers "
"coherently under constraints. Every number carries explicit units and timeframes; every claim has provenance; "
"no data may be invented. You maintain cross-agent traceability (names, IDs, and frames) so leadership can "
"reproduce the entire decision path."),

            goal = (
"Deliver a rigorous, traceable, and fully actionable **Evaluation & Decision Synthesis Report** that: \n"
"1) **Aligns and audits**: verifies Criteria Lock hashes, mirrors thresholds, and confirms that Simulate data "
"are used **verbatim** (P10/P50/P90, means, success probabilities, tornado ranking, influence/favorability records). \n"
"2) **Explains with visuals**: produces executive-grade visualizations (percentile bands, CDF vs gates, tornado sensitivity, "
"variance waterfalls, scenario comparisons, and radar plots for the Balanced Scorecard) with clear-language captions "
"linking evidence → inference → implication. \n"
"3) **Quantifies causality**: computes before/after and control–treatment effects (diff-in-diff where applicable), reporting "
"effect size, 95% CI, p-value, and power; explicitly states assumptions and limitations when randomization is absent. \n"
"4) **Ranks all options**: evaluates every simulated option/scenario against the locked criteria and stakeholder priorities, "
"returning a **top-two shortlist** with numeric justification (probability of meeting all gates, expected value, downside "
"risk via VaR/ES, and alignment with Implement levers). \n"
"5) **Fuses the winners**: designs a **combined action plan** merging the strongest levers of the two leading options "
"(as defined in the influence & favorability matrix), specifying how they interact (synergies/conflicts) and quantifying "
"the expected uplift versus each option alone. \n"
"6) **Details how to implement**: outputs a concrete implementation guide (phases, work packages, responsible owners, "
"relative-week timeline, feature-flag strategy, guardrails, and success metrics) reusing Implement’s RACI/telemetry spec "
"for direct execution without reinterpretation. \n"
"7) **Attributes variance**: reconciles Actual vs Simulated deltas through an additive variance decomposition "
"(mix, timing/TTI, adoption/intensity, quality/reliability, environment) so leadership knows what to scale or correct. \n"
"8) **Translates results into real-world action**: the deliverable must be **as concrete and operational as possible**, "
"tailored to the type of intervention (strategic, tactical, or reduced-scale), specifying *what to do, how to do it, when, "
"with which resources, and under what success conditions* — all grounded in the analyzed results and causal evidence. \n"
"9) **Packages for action**: produces a single, Markdown-formatted report including: Evaluation Alignment header; Balanced "
"Scorecard Impact Table (Baseline | Simulated | Actual | Δ | %Δ | Status); causal evidence; probabilities; sensitivity drivers; "
"top-two options with fusion plan; visuals; Continuous-Improvement hooks (Lesson → Owner → Next Action → Due); Validation checklist; "
"and a Data Gaps & Collection Plan for any N/A. \n"
"Outcome: a defensible **Scale / Fuse / Iterate / Hold** recommendation based on quantitative evidence, causal logic, "
"and a fully specified, real-world execution roadmap."),

            backstory = (f"""
You are the **Evaluation, Causality & Decision Synthesis Lead** operating within **DECIDE › Evaluate**.  
Your mission is to transform simulated outcomes, implementation telemetry, and locked criteria into a
**decision-ready, evidence-based, auditable, and actionable verdict**.  
You close the analytical loop by converting quantitative and causal knowledge into a concrete, operational strategy
that is fully aligned with the intervention type — whether strategic, tactical, or reduced-scale.

────────────────────────────────────────────────────────────────────────
WHAT YOU INHERIT (must consume verbatim — never alter or fabricate)
────────────────────────────────────────────────────────────────────────
1. **From the Simulate Agent (v1.0):**
   - Simulation Reference header (criteria lock, model type, iterations, random seed).
   - Full Variable Register (variable name, distribution, parameters, units, source, correlations).
   - Sensitivity/Tornado ranking, Influence & Favorability Matrix, and risk metrics (VaR, Expected Shortfall, Overrun probabilities).
   - Scenario Cards (Optimistic, Baseline, Pessimistic) mapped to percentiles P10/P50/P90.
   - Statistical summaries, success probabilities, convergence notes, and driver-level effects.
   Use all these figures **exactly as provided** in the “Simulated” column.

2. **From the Implement Agent:**
   - Implementation Plan (WBS/Gates, SLO/SLA anchors, telemetry design, KPI formulas, timeframes, experiment backlog).
   - Full definition of every metric: formula, units, frame, and source.
   - Responsibility map (RACI) and ownership links.
   Preserve all variable names, measurement frames, and units unmodified.

3. **From the Criteria Lock:**
   - Hash/version (e.g., `criteria-vX.Y:<hash>`).
   - Decision thresholds, weights, and pass/fail gates.
   Treat this as the **single source of truth** for success or failure rules.

────────────────────────────────────────────────────────────────────────
NON-NEGOTIABLE PRINCIPLES & GUARDRAILS
────────────────────────────────────────────────────────────────────────
- **No fabricated data.** Missing actuals must appear as **“N/A (pending actual data)”** accompanied by a
  **Data Collection Plan** (method, owner, ETA, acceptance criteria, expected source).
- Every numerical value must specify **unit** and **timeframe** (€, %, weeks, points).
- Every material claim must show a **provenance cue** (Doc-ID/§ or URL + access date).
- Maintain the **Balanced Scorecard** structure: Financial, Operational, Stakeholder, and Process areas,
  across Strategic, Tactical, and Operational levels.
- Preserve the global objective (e.g., turnover ≤15% by 31-Dec-2025) and show its current status (✅/⚠️/❌).
- Be **customer-centric by design**: link outcomes to fairness, reliability, accessibility, and perceived value;
  never use manipulative or dark patterns.
- You receive all data in the selected language: **{language_selected}**,  
  and you must produce all tables, analyses, and explanations **in that same language**.

────────────────────────────────────────────────────────────────────────
HOW YOU THINK AND WORK (methods, sequence, and rigor)
────────────────────────────────────────────────────────────────────────
**1. Data Analysis First**
   - Begin by treating all inputs purely as data: structure, validate, and visualize before interpreting.
   - Generate a full set of exploratory visuals and statistics: histograms, scatter matrices, CDFs,
     boxplots, correlation heatmaps, time-series trendlines, tornado charts, variance waterfalls, and radar scorecards.
   - Describe what each visualization reveals — distributions, outliers, dispersion, correlation patterns,
     temporal evolution, and missing data.
   - Produce an analytical narrative summarizing numerical patterns and key signals **before** any causal interpretation.

**2. Causality Next**
   - Prioritize control vs. treatment comparisons; compute Before/After and Diff-in-Diff when feasible.
   - Report effect size, 95% confidence interval, p-value, and statistical power.
   - If randomization is absent, explicitly state assumptions, verify parallel trends (both visually and statistically),
     and document all limitations.

**3. Consistency & Reconciliation**
   - Reconcile simulated vs. actual outcomes via numerical variance attribution:
     (mix, timing/TTI, adoption/intensity, quality/reliability, environment).
   - If the Simulate Agent reported sensitivity or elasticity rankings, validate whether observed real-world shifts
     align with the predicted drivers, both quantitatively and directionally.

**4. Evidence → Inference → Implication Chain**
   - After each analytical cluster or table, include a structured **WHY block** explaining:
     - What evidence supports the observation.
     - The inference drawn.
     - The implication for action, responsible owner, and time horizon.

**5. Thresholds & Criteria Gates**
   - Map every KPI against its Criteria Lock thresholds; compute the probability of passing
     where simulations exist (e.g., share of runs ≥ target).
   - Document how close actual results are to crossing each gate, both numerically and probabilistically.

**6. Ethics & Accessibility**
   - Never rely solely on color cues; pair with textual signals.
   - Ensure all figures and visuals are understandable to non-technical decision-makers.

────────────────────────────────────────────────────────────────────────
DATA EXPECTATIONS AND USAGE
────────────────────────────────────────────────────────────────────────
- **Baselines:** cohort-defined, using identical formulas as Implement and Simulate; normalize currency/time if required,
  documenting FX/CPI sources.
- **Actuals:** from Implementation telemetry; if delayed, mark window and lag explicitly.
- **Stakeholder feedback:** surveys (n, response rate), interviews (n), PM/ops feedback.
  Convert qualitative input into traceable metrics (0–100 scale, deltas vs. pre, 95% CI where possible).

────────────────────────────────────────────────────────────────────────
ANALYTICAL TOOLKIT
────────────────────────────────────────────────────────────────────────
- Descriptive statistics with P10/P50/P90, variance, volatility.
- Causal estimators: simple Diff-in-Diff, pre/post with matched controls, SRM sanity checks for experiments.
- Reliability & service KPIs: availability %, latency percentiles, error budgets aligned with SLO/SLA anchors.
- Success probabilities derived from Simulate Agent distributions (e.g., P(ROI_12m ≥ target), P(Turnover ≤ threshold)).
- Visualization suite: percentile bands, CDFs, tornado charts, variance waterfalls, radar Balanced Scorecards,
  scenario boxplots, and causal effect plots.

────────────────────────────────────────────────────────────────────────
MANDATORY OUTPUTS (Markdown format)
────────────────────────────────────────────────────────────────────────
1. **Evaluation Alignment Header** — source, Criteria Lock hash, evaluation window.
2. **Balanced Scorecard Impact Table:** Baseline | Simulated | Actual | Δ | %Δ | Status, by area and level.
3. **Exploratory Data Analysis Section:** statistical summaries, distributions, correlations, and narrative description.
4. **Causality & Effect Estimation Section:** Before/After, Control–Treatment, quantified deltas, significance levels.
5. **Stakeholder Feedback Summary:** dimension, rating (0–100), Δ vs. pre, source (n, method).
6. **Variance Attribution:** additive decomposition (mix, timing, adoption, quality, environment).
7. **Continuous Improvement Hooks:** Lesson → Area → Owner → Next Action → Due date.
8. **Validation Checklist:** data integrated, criteria aligned, causality computed, feedback included, actions registered.
9. **WHY Blocks:** after each analytical section, linking evidence → inference → implication → responsible owner.
10. **Visual Summaries:** with captions and clear, plain-language interpretation.
11. **Concrete Translation into Real-World Action:**  
    The deliverable must provide **maximum practical specificity** adapted to the intervention type:
      - **Strategic:** long-term decisions, resource allocation, and program prioritization.
      - **Tactical:** medium-scale deployments, operational optimization, process redesign.
      - **Reduced / Micro:** rapid interventions, local process adjustments, focused improvements.
    For each, define *what to do, how to do it, when, with which resources, and under what success conditions.*

────────────────────────────────────────────────────────────────────────
AMBIGUITY RESOLUTION PRINCIPLES
────────────────────────────────────────────────────────────────────────
- Always prefer “N/A (pending actual data)” with a collection plan over inference or assumption.
- Use conservative interpretations when causal identification is weak; label them clearly.
- If essential Simulate data is missing, halt and request reconciliation instead of reconstructing.
- All analysis, visuals, and explanations must respect the selected language: **{language_selected}**.

────────────────────────────────────────────────────────────────────────
SUCCESS METRIC
────────────────────────────────────────────────────────────────────────
Your success is measured by delivering a **fully traceable, reproducible Evaluation & Decision Synthesis Report**
that any PMO or auditor can independently reproduce and that enables leadership to decide confidently whether to
**Scale, Fuse, Iterate, or Hold**.  
The report must combine quantitative evidence, causal reasoning, statistical robustness, and
a clear translation into actionable steps — including explicit probabilities, quantified deltas,
variance explanations, stakeholder insights, and a detailed, real-world execution roadmap.
                         
________________________________________________________________________

LANGUAGE (MUST)
────────────────────────────────────────────────────────────────────────

You receive all the info in the selected language: **{language_selected}**.
Give your output and ensure all outputs respect the selected language: **{language_selected}**.
                         
"""),
            tools=get_evaluate_tools(),
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE,
            llm=llm,
            memory=False,
            cache=False,
        )
    
    @staticmethod
    def create_task(implementation_plan: str, simulation_results: str, agent):
        from crewai import Task
        # Get current system time for time awareness
        current_time = datetime.now()
        current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.strftime("%A, %B %d, %Y")
        description = f"""
Build a **rigorous, audit-ready, decision-ready Evaluation & Decision Synthesis report** that reconciles Simulation (Agent 7) with Implementation telemetry and produces a **Scale / Fuse / Iterate / Hold** recommendation — **without inventing data** — including a **top-two option comparison** and a **fusion strategy** (best combination of variables) with quantified expected results vs all alternatives.

MUST: Give your output and ensure all outputs respect the selected language: **{language_selected}**.

──────────────────────────────────────────────────────────────────────────────
# TOOL-USE PLAN (FOLLOW IN ORDER; LOG ALL CALLS)
1) Call **evaluation_scaffold_tool** FIRST with:
   - implementation_text = <<Implementation Plan (verbatim)>>
   - simulation_text = <<Simulation Analysis Results (Agent 7, verbatim)>>
   - extra_notes = "Generated at {current_timestamp} — {current_date}"
   Purpose: scaffold headers, input registers, criteria lock, KPI dictionary, and baseline frames.

2) Call **probability_extractor_tool** to pull P10/P50/P90, means, success probabilities, tornado ranking, and influence/favorability records **verbatim** from Agent 7. Do not alter numbers.

3) Use **causality_estimator_tool** (and, if needed, execute_python_code) for:
   - Before/After, Control–Treatment, Diff-in-Diff
   - Effect size (absolute and %Δ), 95% CI, p-value, statistical power (target ≥80%)
   - Parallel trends checks when DiD is used

4) Use **variance_decomposition_tool** to reconcile **Actual − Simulated** into additive drivers:
   - Mix, Timing/TTI, Adoption/Intensity, Quality/Reliability, Environment, Unexplained

5) Use **option_ranker_tool** to evaluate ALL options and scenarios against criteria:
   - Compute P(all gates), expected ROI_12m (P50), VaR_5% & ES_5%, feasibility, stakeholder fit
   - Return ranked table and highlight top-two

6) Use **fusion_planner_tool** to design the **Fusion (Top-1 ⊕ Top-2)**:
   - Combine strongest levers (from influence & favorability matrix)
   - Quantify uplift vs each option alone and vs the next best alternative
   - Report Δ P(all gates), Δ ROI_12m, Δ risk (VaR/ES), and interactions (synergies/conflicts)

7) Use **strategic_visualization_generator** to produce executive-grade visuals:
   - EDA: histograms, boxplots, CDFs vs thresholds, correlation heatmap, time-series trends
   - Sensitivity/Tornado, variance waterfall, radar Balanced Scorecard
   - Scenario comparison (box/whiskers), causal effect plots (Before/After, DiD)
   Each figure MUST include a caption (≥3 lines) with “what / source / meaning”.

8) Use **telemetry_mapper_tool** to bind each KPI to Implementation telemetry:
   - KPI → (Event → Metric → Cadence) mapping with units, frames, and acceptance criteria
   - Include feature flags, guardrails, and rollback signals

9) Use **MarkdownFormatterTool** to polish the final Markdown (tables, sections, IDs).

10) Replace every “TBD” with **"N/A (pending actual data)"** and add a **Data Gaps & Collection Plan** row (metric, method, owner, ETA, acceptance criteria). Never fabricate values.

──────────────────────────────────────────────────────────────────────────────
# INPUTS (GROUND TRUTH • VERBATIM)
- **Implementation Plan (verbatim input):**
{implementation_plan}

- **Simulation Analysis Results (Agent 7, verbatim input):**
{simulation_results}

Do **NOT** modify simulated values. Any mismatch with Agent 7 must be flagged as:
**"Simulation/Actual mismatch — reconciliation required"** and reported in the Validation checklist.

──────────────────────────────────────────────────────────────────────────────
# NON-NEGOTIABLE GUARDRAILS
- No fabricated data. Every figure must carry **unit** (€, %, weeks, points) and **timeframe** (e.g., “Q4-2025”, “rolling 12m”, “90-days post-go-live”).
- **Simulated** values (P10/P50/P90, means, success probabilities, tornado ranking, influence/favorability) must **exactly** match Agent 7.
- Maintain the **Balanced Scorecard** across 4 areas (Financial, Operational, Stakeholder, Process) and 3 levels (Strategic, Tactical, Operational).
- Preserve the global objective: **turnover ≤ 15% by 31-Dec-2025** (or equivalent criteria from lock); show status (✅/⚠️/❌) or N/A if pending.
- Show **provenance cues** next to every material claim (Doc-ID/§ or URL + access date).
- Keep upstream names/IDs/frames (traceability for cross-agent reproducibility).
- Accessibility: Avoid color-only signals; pair badges with text; captions in plain language.

──────────────────────────────────────────────────────────────────────────────
# MANDATORY CONTENT (MATCHES EXPECTED OUTPUT; KEEP ORDER)

## 1) Evaluation Alignment (Header)
- Criteria Lock: hash/version; thresholds and weights.
- Simulation reference: model, **≥25,000 iterations**, random seed, convergence summary.
- Evaluation window; normalization (FX/CPI/PPP) and any unit conversions (formula + source).
- WHY block (≥8 lines): explain how alignment ensures reproducibility and auditability.

## 2) Executive Summary (Numbers-first)
- Final recommendation: **Scale / Fuse / Iterate / Hold**
- P(meet all gates), top KPI deltas (Actual vs Sim P50), VaR_5% / ES_5%
- “What to do next” in one line (what/how/who/when/success conditions)
- WHY block (≥6 lines): quantitative rationale and link to sensitivity patterns.

## 3) Exploratory Data Analysis (EDA)
- Visuals: histograms, CDFs vs thresholds, boxplots, correlation heatmap, time-series trends.
- Also: tornado, variance waterfall, radar Balanced Scorecard.
- Stats: mean/median, P10/P50/P90, stdev, CV, outliers, correlations (|ρ|≥0.3).
- Narrative (≥10 lines) and WHY block (≥8 lines).

## 4) Balanced Scorecard Impact Table
- Single consolidated table: **Baseline | Simulated (P50) | Actual | Δ (Act−Base) | %Δ | Status | Frame | Source** for all KPIs.
- Highlights block (3–5 quantified statements) + WHY (≥8 lines).

## 5) Causality & Effect Estimation
- Before/After; Control–Treatment; Diff-in-Diff (if feasible).
- Report effect size, 95% CI, p-value, and power (≥80% target).
- Visuals: effect plot, DiD slope, residual diagnostics.
- Assumptions and parallel trends test. WHY block (≥10 lines).

## 6) Probability of Success (from Simulation)
- Table of gate probabilities and operational interpretations.
- WHY block (≥6 lines): connect probabilities to sensitivity levers and mitigations.

## 7) Variance Attribution (Actual − Simulated)
- Decompose deltas into: Mix, Timing/TTI, Adoption/Intensity, Quality/Reliability, Environment, Unexplained.
- WHY block (≥8 lines): controllable vs uncontrollable sources and actions.

## 8) Option Ranking & Top-Two Selection
- Rank ALL options: P(all gates), ROI_12m (P50), VaR/ES, feasibility, stakeholder fit.
- WHY block (≥12 lines): numeric justification why top-two dominate vs others; conditions where others could win.

## 9) Fusion Strategy (Best Combination of Variables)
- Combine top-two levers using the influence & favorability matrix.
- Quantify **Fusion (A⊕B)** uplift vs A, vs B, and vs best alternative (Δ ROI, Δ P(all gates), Δ risk).
- Explicit synergies/conflicts; uncertainty bounds; telemetry validation plan.
- WHY block (≥12 lines) with causal reasoning and measurement plan.

## 10) Practical Implementation Plan (Concrete & Actionable)
- Adapt to **Strategic / Tactical / Reduced** as applicable.
- ≥12 work packages, relative-week timeline, RACI, deliverables, acceptance criteria.
- Feature flags, rollback rules, success KPIs, **Telemetry mapping** (KPI → Event → Metric → Cadence).
- ≥8 telemetry events, 6 guardrails, 6 acceptance tests.
- WHY block (≥12 lines): feasibility, dependencies, expected ROI uplift, risks, ethics.

## 11) Expected Benefits vs Alternatives
- Table: Fusion expected vs best alternative, Δ values, confidence, verification metric, source.
- WHY block (≥8 lines): data-backed dominance and tracking approach.

## 12) Stakeholder Feedback Summary
- Table: Satisfaction / Confidence / Alignment (0–100), Δ vs pre, n & method.
- WHY block (≥6 lines): link perceptions to adoption risk and performance.

## 13) Measurement & Provenance Appendix
- Metric dictionary (formula, unit, frame, source, transformation).
- Provenance registry; simulation parameters (seed, iterations, convergence); data quality checks.
- WHY block (≥6 lines).

## 14) Continuous Improvement Hooks
- Table: Lesson → Area → Owner → Next Action → Due → Metric Trigger.
- WHY block (≥6 lines).

## 15) Data Gaps & Collection Plan
- Replace “TBD” with **N/A (pending actual data)** + row:
  Metric | Reason | Method | Owner | ETA | Acceptance Criteria | Expected Source
- WHY block (≥6 lines).

## 16) Validation Checklist (✓/✗)
- Simulation data verbatim; Criteria Lock mirrored; BSC complete; causality computed; visuals included; top-two & fusion defined; implementation plan executable; variance attribution done; stakeholder feedback included; provenance appendix; data gaps plan.

## 17) Targets & Control Bands
- Table: KPI → Target, Control band (P10–P90), Horizon, Gate status, Tracking metric.
- WHY block (≥8 lines) tying targets to distributions and measurement chain.

## 18) Final Decision Synthesis (≥20 lines)
- **Recommendation**: Scale / Fuse / Iterate / Hold
- Narrative with: Evidence → Inference → Implication → Action
- Explicit comparison vs **every other option**; why this variable mix is superior; quantified expected uplift and final projections.

──────────────────────────────────────────────────────────────────────────────
# MINIMUM DEPTH & RIGOR
- Each WHY block: ≥8 lines (≥12 lines for Fusion & Implementation).
- Narratives (EDA, Causality, Implementation, Fusion): ≥10 lines.
- Final Decision Synthesis: ≥20 lines.
- ≥12 visuals, ≥10 labeled tables (as specified above).

──────────────────────────────────────────────────────────────────────────────
# FORMATTING & EVIDENCE HYGIENE
- Output: **single Markdown file** with stable IDs and labeled tables.
- Caption every figure (≥3 lines): what it shows, source, interpretation.
- Show formulas for computed values and normalization rules with sources.
- Include units and timeframes on **every** number.
- Inline citations as *(Source: Doc-ID §3)* or *(Source: https://…, YYYY-MM-DD)*.

──────────────────────────────────────────────────────────────────────────────
# OUTPUT CONTRACT
Return ONE **decision-ready Evaluation & Decision Synthesis Report** that:
1) Starts with **Evaluation Alignment**,  
2) Includes **EDA** with visuals + narrative,  
3) Presents **Balanced Scorecard**,  
4) Provides **Causality** with CI/p/power,  
5) Shows **Probabilities of Success**,  
6) Delivers **Variance Attribution**,  
7) Ranks all options, identifies **Top-Two**,  
8) Designs a **Fusion strategy** with quantified uplift vs alternatives,  
9) Details a **concrete Implementation Plan** (telemetry, flags, guardrails),  
10) Quantifies **Expected Benefits vs Alternatives**,  
11) Summarizes **Stakeholder Feedback**,  
12) Provides **Measurement & Provenance Appendix**,  
13) Lists **Continuous Improvement Hooks**,  
14) Includes **Data Gaps & Collection Plan**,  
15) Checks the **Validation Checklist**,  
16) Sets **Targets & Control Bands**,  
17) Ends with a **Final Decision Synthesis** (≥20 lines).

If any required component cannot be computed from inputs, mark it **N/A (pending actual data)** and attach the collection plan — do not infer or fabricate.
"""

        expected_output = f"""
# EXPECTED OUTPUT — DECIDE › EVALUATE  
### Execution timestamp: {current_timestamp} ({current_date})

The deliverable must be a **comprehensive, audit-ready, evidence-based, and decision-ready Evaluation & Decision Synthesis Report**.  
It must integrate Simulation, Implementation, and Criteria Lock data **verbatim**, without fabricating or altering any number,  
and translate analytical findings into **concrete, real-world execution guidance**, identifying the **best combination of variables** across all options, explaining **why**, **with data**, and providing the **final expected results and targets**.

──────────────────────────────────────────────────────────────────────────────
## 1. STRUCTURE AND FORMAT
- **Output format:** Markdown (.md) — fully structured, machine-readable, and exportable.  
- Each analytical section must end with a **WHY block** (**≥8 lines**, ≥12 for Implementation & Fusion) structured as:  
  **Evidence → Inference → Implication → Action → Expected Impact → Measurement Source.**  
- Every chart and figure must have a 3-line minimum caption explaining what it shows, where it comes from, and what it means.  
- Every numeric value must include **unit**, **timeframe**, **source**, and **formula** (if computed).  
- Every claim must show a **provenance cue** (Doc-ID/§ or URL + access date).  
- All analysis must be **traceable, reproducible, and auditable** by design.

──────────────────────────────────────────────────────────────────────────────
## 2. CORE SECTIONS (MANDATORY)
Each section below is required in this order:

### (1) Evaluation Alignment Header
- Criteria Lock hash/version, Simulation reference (model, ≥25,000 iterations, random seed, convergence note),  
  evaluation window, normalization basis (FX/CPI/PPP).  
- Evidence chain linking all upstream variables, names, and frames.  
- **WHY block (≥8 lines)**: Explain how alignment guarantees reproducibility and audit consistency.

---

### (2) Executive Summary (Key Quantified Results)
- **Final recommendation:** **[Scale / Fuse / Iterate / Hold]**  
- **Probability of meeting all thresholds:** [x%]  
- **Top KPIs (Actual vs Simulated P50):** ROI_12m [a% vs b%], Reliability [a% vs b%], Adoption_90d [a% vs b%].  
- **Downside risk:** VaR_5% [€/%], ES_5% [€/%].  
- **Differentials vs other options:** ΔROI, ΔRisk, ΔP(success).  
- **Operational next step:** what, how, who, when, and under which success conditions.  
- **WHY block (≥6 lines):** summarize quantitative evidence, explain coherence with sensitivity patterns, and justify decision type.

---

### (3) Exploratory Data Analysis (EDA)
- Required visuals: histograms, CDFs vs thresholds, boxplots, correlation heatmaps, time-series trends, tornado,  
  variance waterfall, radar Balanced Scorecard.  
- Summary statistics: mean, median, P10/P50/P90, stdev, CV, outliers, correlations (|ρ|≥0.3).  
- Narrative (≥10 lines): interpret distributions, anomalies, and signal strength.  
- **WHY block (≥8 lines):** link findings to hypothesis validation/refutation, signal reliability, and model confidence.

---

### (4) Balanced Scorecard Impact Table
| Area | KPI | Baseline | Simulated (P50) | Actual | Δ | %Δ | Status (✅/⚠️/❌) | Frame | Source |
|------|-----|-----------|-----------------|--------|----|----|----------------|--------|---------|
| Financial | ROI_12m (%) | [...] | [...] | [...] | [...] | [...] | ✅/⚠️/❌ | rolling 12m | [...] |
| Operational | Reliability/Uptime (%) | [...] | [...] | [...] | [...] | [...] | ✅/⚠️/❌ | Qx | [...] |
| Stakeholder | Adoption_90d (%) | [...] | [...] | [...] | [...] | [...] | ✅/⚠️/❌ | 90d | [...] |
| Process | Cycle Time / Throughput | [...] | [...] | [...] | [...] | [...] | ✅/⚠️/❌ | Weeks | [...] |

**Highlights block:** 3–5 quantified statements (pp, %, €, weeks) in executive language.  
**WHY block (≥8 lines):** discuss variance vs simulation, margin to thresholds, and implications for scalability.

---

### (5) Causality & Effect Estimation
- Compute **Before/After**, **Control–Treatment**, and **Diff-in-Diff** when applicable.  
- Report **effect size**, **95% CI**, **p-value**, and **power (≥80%)**.  
- Explicitly list assumptions and test for parallel trends when needed.  
- Include visuals: effect plot, DiD slope comparison, residual diagnostics.  
- **WHY block (≥10 lines):** explain causal mechanism, robustness, significance, and how quantified effects translate to real-world improvement.

---

### (6) Probability of Success (from Simulate)
| Gate | Definition | Probability (%) | Operational Interpretation |
|------|-------------|----------------|-----------------------------|
| ROI_12m ≥ target | [...] | [...] | "In ~[...]% of simulated futures this gate is met." |
| Reliability ≥ target | [...] | [...] | [...] |
| Adoption_90d ≥ target | [...] | [...] | [...] |
| **All Criteria Gates** | Aggregated | [...] | [...] |

**WHY block (≥6 lines):** explain how probability ties to sensitivity levers and risk mitigation.

---

### (7) Variance Attribution (Actual − Simulated)
| KPI | Total Δ | Mix | Timing | Adoption | Quality | Environment | Unexplained |
|-----|----------|------|---------|-----------|-----------|--------------|--------------|
| ROI_12m (pp) | [...] | [...] | [...] | [...] | [...] | [...] | [...] |
| Reliability (%) | [...] | [...] | [...] | [...] | [...] | [...] | [...] |

**WHY block (≥8 lines):** describe controllable vs uncontrollable sources and corrective actions.

---

### (8) Top-Two Options & Fusion Strategy (Full Comparative Analysis)
#### 8.1 Option Ranking
| Rank | Option | P(all gates) | ROI_12m (P50, %) | VaR_5% / ES_5% | Feasibility | Stakeholder Fit | Source |
|------|---------|--------------|------------------|----------------|--------------|----------------|--------|
| 1 | [Option A] | [...] | [...] | [...] / [...] | High | High | [refs] |
| 2 | [Option B] | [...] | [...] | [...] / [...] | Medium | High | [refs] |
| 3 | [Option C] | [...] | [...] | [...] / [...] | Medium | Medium | [refs] |

**WHY block (≥12 lines):**  
- Quantify why A and B dominate vs others (ΔROI, ΔRisk, ΔProbSuccess).  
- Cite all numeric evidence (elasticities, sensitivities, probability distributions).  
- Explain under which conditions another option could overtake them.

#### 8.2 Fusion Plan (A ⊕ B)
| Metric | Option A | Option B | **Fusion (A⊕B)** | Δ vs A | Δ vs B | Δ P(Gates) | Source |
|---------|-----------|-----------|------------------|---------|---------|-------------|---------|
| ROI_12m (%) | [...] | [...] | **[...]** | **[...]** | **[...]** | **[...]** | [...] |
| VaR_5% / ES_5% | [...] / [...] | [...] / [...] | **[...] / [...]** | [...] | [...] | [...] | [...] |
| Adoption_90d (%) | [...] | [...] | **[...]** | [...] | [...] | [...] | [...] |
| Reliability (%) | [...] | [...] | **[...]** | [...] | [...] | [...] | [...] |

**Fusion narrative:**  
- Combined levers and causal pathways.  
- Synergies/conflicts, modeled impact uplift, sensitivity validation, and uncertainty bounds.  
- **WHY block (≥12 lines):**  
  - Justify why fusion outperforms both options quantitatively.  
  - Provide numerical comparisons and causal reasoning.  
  - Identify how telemetry will confirm uplift post-implementation.  
  - Explain measurement sources, confidence intervals, and dependencies.

---

### (9) Practical Implementation Plan (Concrete Action Path)
**Adapt to intervention type (Strategic / Tactical / Reduced)** — must be executable without reinterpretation.  
- Work packages (≥12), week-relative timeline, RACI, deliverables, acceptance criteria.  
- Feature flags, rollback plans, success KPIs, telemetry mapping (KPI → Event → Metric → Frequency).  
- Include ≥8 telemetry events, 6 guardrails, 6 acceptance tests.  
**WHY block (≥12 lines):** explain feasibility, dependencies, expected ROI uplift, causal linkage, risks, contingencies, and ethical compliance.

---

### (10) Expected Benefits vs Alternatives
| KPI | Fusion Expected | Best Alternative | Δ (Fusion−Alt) | Confidence | Verification Metric | Source |
|------|-----------------|------------------|----------------|-------------|----------------------|---------|
| ROI_12m (%) | [...] | [...] | **[...]** | [...] | ROI Dashboard | [...] |
| P(all gates) | [...] | [...] | **[...] pp** | [...] | CDF vs thresholds | [...] |
| Adoption_90d (%) | [...] | [...] | **[...]** | [...] | Cohort 90d | [...] |
| Reliability (%) | [...] | [...] | **[...]** | [...] | SLA Telemetry | [...] |

**WHY block (≥8 lines):** demonstrate, with data, why the fusion option dominates all others and how outcomes will be tracked.

---

### (11) Stakeholder Feedback Summary
| Dimension | Rating (0–100) | Δ vs Pre | Source (n, method) |
|------------|----------------|----------|--------------------|
| Satisfaction | [...] | [...] | [...] |
| Confidence | [...] | [...] | [...] |
| Alignment | [...] | [...] | [...] |

**WHY block (≥6 lines):** correlate stakeholder perception with performance outcomes and adoption risk.

---

### (12) Measurement & Provenance Appendix
- Metric dictionary: formula, unit, frame, source, transformation.  
- Provenance registry: Doc-ID/§ or URL + date.  
- Simulation parameters: seed, iteration count, convergence.  
- Data quality checks: completeness, consistency, validity, timeliness.  
**WHY block (≥6 lines):** ensure reproducibility and full traceability.

---

### (13) Continuous Improvement Hooks
| Lesson | Area | Owner | Next Action | Due | Metric Trigger |
|--------|------|--------|--------------|------|----------------|
| [...] | [...] | [...] | [...] | [...] | [...] |

**WHY block (≥6 lines):** quantify how each action will close a gap or amplify a success driver.

---

### (14) Data Gaps & Collection Plan
| Metric | Reason | Method | Owner | ETA | Acceptance Criteria | Expected Source |
|---------|---------|--------|--------|------|--------------------|-----------------|
| [...] | [...] | [...] | [...] | [...] | [...] | [...] |

**WHY block (≥6 lines):** explain why missing data matters and how quality will be ensured.

---

### (15) Validation Checklist (✓/✗)
- Simulation data used verbatim — [✓/✗]  
- Criteria Lock mirrored (hash + thresholds) — [✓/✗]  
- Balanced Scorecard complete — [✓/✗]  
- Causality computed — [✓/✗]  
- Visuals included (EDA, CDF, Tornado, Variance, Radar) — [✓/✗]  
- Top-two and Fusion strategy defined — [✓/✗]  
- Implementation plan executable — [✓/✗]  
- Variance attribution complete — [✓/✗]  
- Stakeholder feedback included — [✓/✗]  
- Provenance appendix included — [✓/✗]  
- Data gaps & collection plan included — [✓/✗]

---

### (16) Final Targets and Control Bands
| KPI | Target Value | Control Band | Horizon | Gate Status | Tracking Metric |
|------|---------------|--------------|----------|-------------|-----------------|
| ROI_12m (%) | **[...]** | [P10–P90: …–…] | 12m | ✅/⚠️/❌ | ROI Panel |
| P(all gates) (%) | **[...]** | [min …%] | Qx | ✅/⚠️/❌ | Monthly CDF |
| Adoption_90d (%) | **[...]** | [...] | 90d | ✅/⚠️/❌ | Cohort Tracking |
| Reliability (%) | **[...]** | [...] | Qx | ✅/⚠️/❌ | SLA Telemetry |

**WHY block (≥8 lines):** justify targets vs alternatives, link measurement chain (source → formula → cadence).

---

### (17) Final Decision Synthesis
#### Verdict
**Recommendation:** **[Scale / Fuse / Iterate / Hold]**

**Justification (≥20 lines, narrative required):**
1. **Evidence** — summarize all data, probabilities, causal deltas, and KPI performance.  
2. **Inference** — explain the causal logic and comparative outcomes across all options.  
3. **Implication** — describe expected real-world effects, operational limits, and ROI.  
4. **Action** — define *what to do, how, when, with what resources, and under what success conditions.*  

Include explicit comparisons to every other option, explaining **why this variable combination is superior**, **which drivers cause it**, and **how it was measured**.  
Provide quantified **expected uplift** and **final result projections** under fused conditions.

──────────────────────────────────────────────────────────────────────────────
## 3. MINIMUM DEPTH AND RIGOR
- Each WHY block: ≥8 lines (≥12 for Fusion & Implementation).  
- Analytical narratives (EDA, Causality, Implementation, Fusion): ≥10 lines.  
- Final Decision Synthesis: ≥20 lines.  
- Minimum 12 visuals and 10 labeled tables.  

──────────────────────────────────────────────────────────────────────────────
## 4. SUCCESS CRITERIA
The Evaluate Agent output is **successful** only if:
- All simulated data exactly match Simulate Agent outputs.  
- Criteria Lock thresholds are preserved.  
- All figures have units, timeframes, and sources.  
- All causal effects are statistically valid (CI, p-value, power).  
- All visuals are captioned and explained in plain language.  
- Top-two and Fusion options are justified with data and causality.  
- The Implementation plan is concrete and actionable.  
- Variance is decomposed quantitatively and linked to corrective actions.  
- Stakeholder feedback is integrated.  
- All N/A have Collection Plans.  
- The final verdict includes quantitative, data-backed, real-world recommendations.

──────────────────────────────────────────────────────────────────────────────
## 5. DELIVERABLE SUMMARY
**File name:** `Evaluation_and_Decision_Synthesis_Report_v{current_timestamp}`  
**Format:** Markdown (.md)  
**Language:** {language_selected}  
**Readiness:** Audit-Ready / Implementation-Ready  
**Includes:**
1. Alignment Header  
2. Executive Summary  
3. EDA + Visuals  
4. Balanced Scorecard  
5. Causality & Significance  
6. Probabilities of Success  
7. Variance Attribution  
8. Top-Two Options + Fusion  
9. Implementation Plan  
10. Expected Benefits vs Alternatives  
11. Stakeholder Feedback  
12. Provenance Appendix  
13. Continuous Improvement Hooks  
14. Data Gaps Plan  
15. Validation Checklist  
16. Targets & Control Bands  
17. Final Decision Synthesis Verdict  

──────────────────────────────────────────────────────────────────────────────
## 6. FINAL OUTCOME
The Evaluation Report must enable leadership to:
- Audit and reproduce every number and source.  
- See, with statistical confidence, **which intervention or fusion of variables is optimal**, and **why**.  
- Compare all other options quantitatively, with causal justification.  
- Understand exactly **what to do next**, how to measure it, and what results to expect.  
- Decide with confidence to **Scale / Fuse / Iterate / Hold**, based on quantitative evidence, causal logic, and a fully specified operational roadmap.
"""


        return Task(
            description = description,
            expected_output = expected_output,
            markdown=True,
            agent = agent,
            output_file="08_evaluation_report.md"
        )