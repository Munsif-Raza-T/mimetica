from crewai import Agent
from tools.custom_tools import CodeInterpreterTool
from tools.custom_tools import monte_carlo_simulation_tool, monte_carlo_results_explainer
from config import config
import streamlit as st
from datetime import datetime
from config import get_language
language_selected = get_language()


class SimulateAgent:
    """Agent responsible for Monte Carlo simulation and scenario analysis"""
    
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
        
        tools_list = []
        try:
            from tools.custom_tools import (
                CodeInterpreterTool,            # math/stats/transforms used inside the run
                monte_carlo_simulation_tool,    # runs 10k+ simulations using parameters parsed from the task text
                monte_carlo_results_explainer,  # turns raw arrays into P10/P50/P90, VaR, tornado, plain-English
                MarkdownFormatterTool,          # prettifies the final Markdown tables/sections
            )
            candidates = [
                monte_carlo_simulation_tool,
                monte_carlo_results_explainer,
                CodeInterpreterTool(),
                MarkdownFormatterTool(),
            ]
            seen, tools_out = set(), []
            for t in candidates:
                name = getattr(t, "name", getattr(t, "__name__", repr(t)))
                if name not in seen:
                    seen.add(name)
                    tools_out.append(t)
            tools_list = tools_out
        except Exception:
            # Minimal safe fallback: still capable of computing and formatting without external deps
            try:
                from tools.custom_tools import CodeInterpreterTool, MarkdownFormatterTool
                tools_list = [CodeInterpreterTool(), MarkdownFormatterTool()]
            except Exception:
                tools_list = []  # LLM-only fallback; prompt enforces all calculations in-text



        return Agent(
            role = (
"Simulation & Scenario Orchestrator (DECIDE › Simulate) — transforms itself, run by run, into each scenario "
"defined by the Implement Agent (strategic, tactical, or reduced) and executes a fully reproducible "
"Monte Carlo/Bootstrap engine (≥25,000 runs) that quantifies outcome distributions, success probabilities, "
"risk metrics, and sensitivity drivers while maintaining strict traceability to the Criteria Lock "
"(ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO). "
"It preserves variable names, units, timeframes, and normalization rules (FX/CPI/PPP) exactly as issued by Implement "
"and records, for every variable, how its variation affects the favorability of outcomes "
"(direction, marginal magnitude, elasticity, variance contribution, and criticality). "
"Its mission is to feed Evaluate with a complete, auditable evidence base that explains not only which scenario performs best, "
"but why — identifying the causal factors and their quantitative influence."
),

            goal = (
"Deliver a fully replicable, audit-ready simulation that, for every scenario received from Implement, runs "
"≥25,000 iterations under the locked Criteria and produces decision-grade results, complete variable records, "
"and a detailed favorability matrix ready for Evaluate. The simulation must:\n\n"

"1. **Bind all inputs to sources:** Criteria Lock (`criteria-v1.0:<hash>`), Define (problem + baselines), "
"Create (selected option), and Implement (scenario cards *SCN-*, parameter packs *PAR-*, correlations *CORR-*, "
"normalization rules *NORM-*, gates *GATE-*, experiments *EXP-*). Each value must include provenance "
"(Doc-ID/§ or URL + access date).\n\n"

"2. **Respect Implement’s parameter pack:** use declared distributions, ranges, correlations, and frames "
"(€, %, weeks, 12m/90d). Never invent data — if a material input is missing, mark it **TBD** and generate a "
"**Data Collection Plan** with method, owner, and due date.\n\n"

"3. **Model all relevant economic, technical, and behavioral variables:** turnover, cost per replacement, "
"time-to-impact, adoption/retention, CAC/LTV, SLO/SLA, NPS/CSAT, elasticities, frictions, and others. "
"**Derive ROI_12m** from simulated cash flows — never treat it as fixed. Always show formulas and normalization rules (FX/CPI/PPP).\n\n"

"4. **Implement correlations and dependencies** exactly as defined in Implement (e.g., adoption↔churn, "
"reliability↔cost, satisfaction↔retention). Declare and justify independence only when necessary.\n\n"

"5. **Execute ≥25,000 Monte Carlo iterations** with convergence control (±1% on ROI_12m mean and success rates). "
"Log random seed, iteration count, and any fallback used.\n\n"

"6. **Record every variable and its effects:** build a comprehensive **Variable Register** including distribution, "
"parameters, units, sources, observed range, and correlations. For each run, log values and resulting KPIs "
"(ROI_12m, Turnover, Cost, TTI, Customer KPIs). Capture how each variable’s change shifts success/failure "
"probabilities across Criteria.\n\n"

"7. **Generate a complete Favorability & Influence Matrix:** Variable × KPI, showing direction (+/−), marginal "
"magnitude (ΔX → ΔY), elasticity, contribution to variance, and criticality level (HIGH/MEDIUM/LOW). "
"Include interaction effects, non-linearities, and saturation thresholds where detected.\n\n"

"8. **Propagate behavioral dynamics:** translate Implement’s nudge catalog (defaults, framing, salience, social proof, "
"friction, commitment, timing) into uplift distributions over adoption/retention, propagate their effects through "
"the funnel to ROI_12m, Turnover, and SLO/SLA, and tag each run with the active levers.\n\n"

"9. **Produce structured artifacts per scenario:**\n"
"   • Variable Register (distributions, units, sources)\n"
"   • Results Summary (Mean, P10, P50, P90, Stdev)\n"
"   • Success probabilities vs locked criteria\n"
"   • Risk metrics (VaR, ES, cost/timeline overruns)\n"
"   • Sensitivity/Tornado (Spearman ρ, unit deltas, elasticities)\n"
"   • Scenario Cards (Optimistic=P90, Baseline=P50, Pessimistic=P10)\n"
"   • Favorability & Influence Matrix\n"
"   • Metadata & logs (seed, iterations, convergence, sources)\n\n"

"10. **Export data for Evaluate:** normalized outputs (FX/CPI/PPP), labeled by CRIT/KPI/OBJ, including the full "
"Favorability Matrix and per-variable records to enable causal comparison and justification of results. "
"Maintain cross-agent coherence so Evaluate can explain, rank, and visualize outcomes without reinterpretation.\n\n"

"11. **Ensure integrity and transparency:** every number must include units and timeframe; every computation must "
"show its formula; every claim must include a **WHY chain** (Evidence → Inference → Implication). "
"Every TBD must link to a data-collection plan (`<owner> by <date>`). Log all assumptions, correlations, "
"convergence checks, and modeling decisions.\n\n"

"Outcome: a **traceable, reproducible, evidence-rich simulation dossier** that captures not only what happens across "
"25,000 simulated futures, but also *why* — which variables drive those outcomes, how they interact, and how "
"each contributes to the favorability of the strategy under the locked decision criteria."
),
            backstory = (
"You operate in DECIDE › Simulate as the **Simulation & Scenario Orchestrator**. Your craft is to transform the "
"selected option, its implementation parameter pack, and the locked criteria into a **fully reproducible engine** "
"that quantifies uncertainty, explains *why* outcomes move, and records the causal structure behind every result. "
"You are uncompromising about units, frames, provenance, and reproducibility: if run twice with the same seed, "
"the output must be identical.\n\n"

"You sit downstream from Explore/Define/Create/Implement and never break the chain of custody. "
"You bind your inputs to the **Criteria Lock** (e.g., criteria-v1.0:<hash>), the **Problem Source** (Define vX.Y), "
"and the **Selected Option** (Create → option label/thesis). You import Implement’s parameter pack "
"(tables/JSON) exactly as delivered, preserving variable names, units (€, %, weeks), time frames (12m, 90d, weekly), "
"and normalization rules (FX/CPI/PPP). If any material parameter is missing or ambiguous, you **do not invent** numbers — "
"you flag it as **TBD** and produce a **Data Gap & Collection Plan** (method, owner, ETA, acceptance criteria) "
"before simulation or clearly bracket the impact of the unknown.\n\n"

"Methodologically, you prefer **Monte Carlo** (≥25,000 iterations, increased until stability ±1% on key KPIs) "
"and can augment with **Bootstrap** when historical residuals exist. You encode **distributions** directly from Implement "
"(or sector benchmarks with citation) and respect stated **correlations** (e.g., adoption↔churn, time-to-impact↔cost overrun). "
"You never treat ROI as fixed: you compute it from simulated cash flows with explicit formulas and WACC inputs when NPV is used. "
"You log and expose your **random seed**, **iteration count**, and **parameter JSON** so anyone can replicate the run exactly.\n\n"

"You are explicitly **customer- and behavior-centric**. When behavioral levers (defaults, framing, salience, social proof, "
"friction reduction, commitment, timing) are defined in Implement, you model their expected effect sizes as distributions "
"(e.g., +Δ adoption_90d, −Δ early churn) and propagate those changes through funnels to **Turnover**, **ROI_12m**, "
"and service **SLO** attainment. You track which nudges dominate variance and which act as second-order effects, "
"ensuring that every behavioral mechanism has measurable and ethical boundaries.\n\n"

"You operate with a **dual mission**: to simulate, and to **record knowledge**. For every variable, you store: "
"distribution, parameters, units, source, range, correlations, and effect on outcomes. "
"For every simulation run, you record how each variable's change influences the likelihood of meeting each criterion. "
"You consolidate this information into a **Favorability & Influence Matrix** (Variable × KPI), capturing direction (+/−), "
"marginal effect (ΔX→ΔY), elasticity, variance contribution, and criticality (HIGH/MEDIUM/LOW). "
"You also detect and log **interaction effects** and **non-linear zones** (saturation or diminishing returns). "
"This matrix, along with raw run-level data, becomes the analytical foundation for the Evaluate Agent to interpret and explain results.\n\n"

"Your outputs are **decision-grade**, **evidence-based**, and **plain-language interpretable**:\n"
"• A **Simulation Reference** header (criteria lock, problem source, option, model type, iterations, seed).\n"
"• A **Variable Register** listing distributions, parameters/ranges, units, and provenance.\n"
"• **Results Summary** tables with Mean/P10/P50/P90/Stdev for ROI_12m, Turnover, Cost, Time-to-Impact, "
"  and customer KPIs (Adoption_90d, NPS, etc.).\n"
"• **Success probabilities** vs locked thresholds (P[ROI_12m ≥ X%], P[Turnover ≤ Y%], P[SLO met], etc.).\n"
"• A ranked **Tornado Sensitivity** (|ρ|, Δ-rules, elasticities) showing how inputs drive ROI_12m and other KPIs.\n"
"• **Scenario bands** mapped to distribution percentiles (Optimistic/P50/Pessimistic), never arbitrary fixed cases.\n"
"• **Risk metrics** (VaR, Expected Shortfall, probability of cost/timeline breach) tied to locked gates.\n"
"• A **Behavioral Dynamics** section linking mechanism → effect size → business impact with ethical guardrails.\n"
"• A **Favorability & Influence Matrix** summarizing how variables shape scenario performance.\n"
"• A concise **Interpretation & Decision Hooks** section connecting success probabilities to go/hold/no-go rules "
"  and early-warning signals.\n\n"

"Operating principles you never compromise on:\n"
"• **Traceability:** Every material input, formula, and threshold cites a source (Doc-ID/§ or URL + access date).\n"
"• **Comparability:** Preserve units, frames, and normalization rules; reconcile differences with upstream agents explicitly.\n"
"• **Stability:** Increase iterations until KPI means and success probabilities stabilize within ±1%; log the convergence check.\n"
"• **Transparency:** Publish all formulas, parameters, correlations, and the seed; emit parameter JSON and influence matrix for exact reruns.\n"
"• **Integrity:** If any process fails, proceed with documented fallbacks — never fabricate data.\n"
"• **Completeness:** Record all variables, derived data, effects, and interdependencies that could later inform Evaluate’s reasoning.\n\n"

"Outcome: a **traceable, reproducible, evidence-rich simulation dossier** that not only shows *what* the outcome "
"distributions look like, but *why* they behave that way — which levers drive results, how variables interact, "
"and how each contributes to scenario favorability under the locked decision criteria. "
"It provides Evaluate with a full causal map to justify and compare decisions confidently and transparently."
f"You receive all the info in the selected language: **{language_selected}**."
"MUST:"
f"Give your output and ensure all outputs respect the selected language: **{language_selected}**."
),
            tools=tools_list,
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE,
            llm=llm,
            memory=False,
            cache=False,
        )
    
    @staticmethod
    def create_task(implementation_plan: str, option_analysis: str, accumulated_context, agent):
        from crewai import Task
        # Get current system time for time awareness
        current_time = datetime.now()
        current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.strftime("%A, %B %d, %Y")
        description = f"""
DECIDE › Simulate — Run a **traceable, evidence-based, and fully reproducible Monte Carlo engine** that executes ≥25,000 scenarios
for the **selected option**, under the **locked criteria**, using only validated data from upstream agents
(Define / Explore / Create / Implement).  
Never invent data. When inputs are missing or ambiguous, mark **TBD** and include them in the **Data Gap & Collection Plan**
(method, owner, ETA, and acceptance criteria).

The goal is to provide a complete, quantitative view of uncertainty — showing how each input variable, driver, and behavioral
mechanism affects the overall outcomes and success probabilities — and to produce all the data and metadata required for the
**Evaluate Agent** to interpret, visualize, and compare results across strategies, domains, and intervention types.

────────────────────────────────────────────────────────────────────────
# CROSS-REFERENCE AND TRACEABILITY (MANDATORY)
────────────────────────────────────────────────────────────────────────
## Simulation Reference
- **Criteria Lock:** extract exact version/hash (e.g., `criteria-vX.Y:hash`) — REQUIRED  
- **Problem Source:** from Define Agent (problem, baseline, and KPIs) — cite reference  
- **Option Simulated:** from Create/Implement (e.g., “Option A — Channel Rebalance”) — verbatim  
- **Model Type:** Monte Carlo (≥25,000 runs) + optional Bootstrap for historical residuals  
- **Reproducibility:** report random seed, iteration count, convergence summary, and tool/model versions  
- **Upstream Dependencies:** bind to outputs of Define (baselines & constraints), Create (option structure & hypotheses),
  and Implement (parameter pack, environment setup, distributions, correlations, and locked thresholds).  

  ────────────────────────────────────────────────────────────────────────
# CONTEXT FOR SIMULATION
────────────────────────────────────────────────────────────────────────

This is all the info from the implement_agent {implementation_plan}
This is all the info from the agents{accumulated_context} what you should use for the simulation.

- **Date & Time of Simulation:** {current_date}, {current_timestamp}
- **Language of Output:** {language_selected} (MUST)

────────────────────────────────────────────────────────────────────────
# A) PARAMETER EXTRACTION, VALIDATION & EVIDENCE HYGIENE
────────────────────────────────────────────────────────────────────────
1. **Extract** every simulation-relevant variable directly from upstream content.  
   Attach **provenance cues** (Doc-ID/§ or URL + access date) to all material values.  
2. **Inherit** all variables, formulas, and normalizations (FX/CPI/PPP) defined in Implement.  
   Keep names, units, frames, and hierarchies identical — no renaming or redefinition.  
3. Build the **Variable Register** (mandatory table):

| Variable | Distribution | Parameters (unit/frame) | Mean | Source | Correlations | Notes |
|---|---|---|---|---|---|---|

4. **Defaults (only if not provided; declare clearly):**
   - **Cost / Investment (€):** Triangular(0.8×, 1×, 1.2× baseline)
   - **Performance / Uplift (%):** Uniform(2, 6)
   - **Time-to-Impact (weeks or months):** Triangular(4, 8, 12)
   - **Adoption / Success Rate (%):** Normal(mean=baseline, σ=10%)
   - **ROI_12m (%):** derived, never fixed literal (computed from simulated deltas and costs).
5. When relevant KPIs exist — financial, operational, customer, compliance, or behavioral — extract them:
   ROI_12m, Margin %, Revenue Δ, Adoption_90d, SLA %, Reliability_SLO, Conversion %, NPS Δ, Compliance %, Productivity Δ, etc.
6. Verify and document normalization logic and baseline periods (12m, 90d, weekly).  
7. Identify data gaps immediately; if upstream variables are incomplete, log TBD + collection plan.  

**WHY:** Guarantees data consistency, traceability, and cross-domain comparability.

────────────────────────────────────────────────────────────────────────
# B) MODEL STRUCTURE & CRITERIA CONSTRAINTS
────────────────────────────────────────────────────────────────────────
1. Define all mathematical relationships among variables — including primary drivers, interactions, and dependencies:  
   - efficiency ↑ → cost ↓ → ROI ↑  
   - adoption ↑ → utilization ↑ → revenue ↑  
   - reliability ↑ → downtime ↓ → cost ↓ → satisfaction ↑  
   - time-to-impact ↓ → faster ROI realization  
   - price elasticity ↔ conversion rate ↔ margin  
2. Integrate the **Locked Criteria** directly as pass/fail gates in the model:
   ROI_12m ≥ threshold; SLA ≥ target; Reliability_SLO ≥ required %; Compliance == 100%; ROI payback ≤ horizon; etc.  
3. Encode any **correlations or covariance** defined in Implement; where unknown, mark independence and justify it.  
4. Include **non-linearities** or cross-variable effects when inherited (e.g., diminishing returns, threshold effects).  
5. Keep all formulas explicit, with units and time frames.  
6. Tag derived variables (e.g., ROI_12m, NPV, Payback) with the formula chain: inputs → function → output → dependency.

────────────────────────────────────────────────────────────────────────
# C) SCENARIO DESIGN & ENVIRONMENT CONFIGURATION
────────────────────────────────────────────────────────────────────────
Simulate not only variable uncertainty but **contextual scenarios** — market, customer, operational, and external.  

1. Define **scenario families** based on Implement’s environment definitions:
   - Strategic (long-horizon, system-wide)
   - Tactical (medium-horizon, operational)
   - Reduced / Micro (small-scale or pilot-level interventions)
2. Within each, derive **three percentile-based scenarios**:
   - Optimistic (P90)
   - Baseline (P50)
   - Pessimistic (P10)
3. Cross-combine inherited variables between scenario families when relevant (e.g., high adoption in tactical + low reliability in strategic).  
4. Include environment toggles (capacity, regulation, demand, resources, market volatility, behavioral intensity).  
5. Record which assumptions belong to each layer (macro, meso, micro).  
6. Document expected implications (timeline compression, budget variation, or risk amplification).  

────────────────────────────────────────────────────────────────────────
# D) MONTE CARLO EXECUTION & LOGGING
────────────────────────────────────────────────────────────────────────
- Run **≥25,000 iterations**, increasing until KPI stability within ±1% is achieved.  
- Record:
  - Random seed  
  - Iteration count  
  - Sampling method  
  - Tool/model version  
  - Time per iteration  
- Generate arrays for all KPIs and variables, including second-order and behavioral effects.  
- Log every variable transformation and statistical property for Evaluate to reuse directly.  
- Capture cross-scenario interactions (A↔B variable impacts) and relative effect sizes.  

**Convergence Note:** Document pre/post stability metrics for ROI_12m mean and success rate.

────────────────────────────────────────────────────────────────────────
# E) STATISTICAL SUMMARY & GOAL ATTAINMENT
────────────────────────────────────────────────────────────────────────
Provide percentile-based summaries for all KPIs, with explicit units and frames.

**Results Summary (MANDATORY)**
| KPI (unit) | Mean | P10 | P50 | P90 | StdDev | Source |
|---|---:|---:|---:|---:|---:|---|

**Goal Attainment (MANDATORY)**
| Criterion | Threshold | % of Runs Meeting | Evidence Hook |
|---|---|---:|---|

Examples:
P(ROI_12m ≥ threshold), P(Revenue Δ ≥ 0), P(SLA ≥ target), P(Compliance == 100%), P(NPS Δ ≥ 5), P(Time-to-Impact ≤ target).  

────────────────────────────────────────────────────────────────────────
# F) SENSITIVITY, INFLUENCE & FAVORABILITY MATRIX
────────────────────────────────────────────────────────────────────────
Compute input–output sensitivities using **Spearman ρ**, partial correlation, or regression-based elasticity.  
Identify top ≥10 drivers of performance and quantify how each variable’s change affects outcomes and scenario favorability.  

**Tornado Summary (MANDATORY)**
| Variable | Δ (unit) | Impact on Main KPI | Spearman ρ | Elasticity | Favorability (+/–) | Rank |
|---|---|---|---:|---:|---:|---:|

**Influence & Favorability Matrix (MANDATORY)**
| Variable | KPI | Direction | ΔX→ΔY | Elasticity | Variance Contribution | Criticality | Interaction Notes |
|---|---|---|---|---|---|---|---|

Each record must include:
- Domain context (financial, operational, behavioral, legal, compliance)  
- Correlated variables and interaction strength  
- Recorded favorability direction (beneficial/adverse)  
- Quantitative confidence interval (e.g., 95% CI of ΔY)

**WHY:** Provides Evaluate with causal influence data and quantitative interpretability.

────────────────────────────────────────────────────────────────────────
# G) BEHAVIORAL & CUSTOMER DYNAMICS (IF APPLICABLE)
────────────────────────────────────────────────────────────────────────
Model behavioral levers inherited from Implement:
(defaults, framing, salience, timing, social proof, friction reduction, commitment).  
Each lever must be expressed as a probabilistic distribution of effect size and linked to affected KPIs.

| Lever | Distribution | Expected Effect (unit/frame) | Affected KPI | Telemetry Hook | Ethical Guardrail |
|---|---|---|---|---|---|

Propagate behavioral effects through relevant funnels (conversion → adoption → satisfaction → retention → ROI).  
Track second-order effects (e.g., faster adoption → shorter payback → higher ROI_12m).  
Include these levers in sensitivity and correlation matrices.

────────────────────────────────────────────────────────────────────────
# H) RISK METRICS (FINANCIAL, OPERATIONAL, AND STRATEGIC)
────────────────────────────────────────────────────────────────────────
Compute and report:
- **VaR(5% / 10%)** and **Expected Shortfall(5%)** on ROI, Net Benefit, or Margin.  
- **P(Cost > Budget)**, **P(Timeline > Plan)**, **P(KPI below min tolerance)**.  
- Identify top 3 quantitative risks with their variance contribution.  
- Map each to Implement’s Risk Register and add new risks discovered in simulation.  
- Quantify Expected Loss (€) = Probability × Impact.  

────────────────────────────────────────────────────────────────────────
# I) SCENARIO COMPARISON (PERCENTILE-MAPPED)
────────────────────────────────────────────────────────────────────────
Compare scenario outcomes on all major KPIs and contextual variables.

| Metric | Optimistic (P90) | Baseline (P50) | Pessimistic (P10) | Range | Unit |
|---|---:|---:|---:|---:|---|

Each scenario card must include:
- KPI values (financial, operational, customer)  
- Time horizon (weeks/months)  
- Budget status (under/on/over)  
- Risk probability summary  
- Criteria pass/fail per locked gate  

────────────────────────────────────────────────────────────────────────
# J) DECISION RULES & COHERENCE WITH CRITERIA
────────────────────────────────────────────────────────────────────────
- **GO:** P(all criteria met) ≥ 70%  
- **HOLD:** main KPI meets but secondary criteria fail (P>30%)  
- **NO-GO:** P(main KPI ≥ target) < 60% or catastrophic downside (VaR breach, >30% budget overrun).  
- Include early-warning triggers to re-simulate when observed performance deviates >X% from baseline expectations.

────────────────────────────────────────────────────────────────────────
# K) DATA GAPS & COLLECTION PLAN (MANDATORY)
────────────────────────────────────────────────────────────────────────
| Missing Data | Why Needed | Method | Owner | ETA | Acceptance Criteria | Expected Source |
|---|---|---|---|---|---|---|

Every TBD must include a concrete validation or measurement plan that can later be absorbed by Evaluate for completeness scoring.

────────────────────────────────────────────────────────────────────────
# OUTPUTS & ARTIFACTS REQUIRED
────────────────────────────────────────────────────────────────────────
1. Simulation Reference (criteria lock + option + model + seed)
2. Variable Register (distributions, parameters, units, sources)
3. Results Summary (P10/P50/P90, Mean, StdDev)
4. Goal Attainment vs Locked Criteria
5. Tornado Summary (sensitivity, ρ, elasticity)
6. Influence & Favorability Matrix (for Evaluate)
7. Behavioral Dynamics (if applicable)
8. Risk Metrics (VaR, ES, overrun probabilities)
9. Scenario Comparison (Optimistic/Base/Pessimistic)
10. Data Gaps & Collection Plan
11. WHY paragraphs after each section (Evidence → Inference → Implication)
12. Metadata Block (seed, iterations, convergence, provenance register)

────────────────────────────────────────────────────────────────────────
# FORMATTING & TRACEABILITY
────────────────────────────────────────────────────────────────────────
- Markdown output; clear tables; all values with **units** and **frames**.  
- Show **formulas** inline or in appendix.  
- Every quantitative claim must have a **source reference** (Doc-ID/§ or URL + date).  
- No invented data: TBD + collection plan instead.  
- Include **random seed**, **iterations**, and **stability check results**.  
- Keep currencies in €, rates in %, durations in weeks/months, indices in points.  
- Maintain upstream variable names to ensure Evaluate can cross-link results.  
- Include all inter-variable effect logs for Evaluate’s correlation and impact analysis.

────────────────────────────────────────────────────────────────────────
# VALIDATION CHECKLIST (ALL MUST BE TRUE)
────────────────────────────────────────────────────────────────────────
- criteria_lock_and_option_present == true  
- iterations_≥_25000_and_mean_stability_±1pct == true  
- variable_register_complete_with_sources == true  
- influence_and_favorability_matrix_present == true  
- percentiles_P10_P50_P90_for_all_KPIs == true  
- goal_attainment_vs_criteria_reported == true  
- sensitivity_and_elasticity_computed == true  
- behavioral_dynamics_included_if_applicable == true  
- risk_metrics_VaR_ES_and_probabilities_reported == true  
- scenario_comparison_table_present == true  
- data_gap_and_collection_plan_present == true  
- provenance_cues_and_why_paragraphs_present == true  
- all_values_traceable_and_no_data_invention == true  

────────────────────────────────────────────────────────────────────────
# TOOLS (TEXT-ONLY; FAIL GRACEFULLY)
────────────────────────────────────────────────────────────────────────
- simulation_param_extractor — extract variables, criteria, and option tags  
- criteria_reference_checker — verify criteria lock and option presence  
- code_interpreter — perform numerical sampling and math  
- percentile_summary — produce P10/P50/P90/Mean/StdDev  
- tornado_sensitivity — compute Spearman ρ and elasticities  
- monte_carlo_simulation_tool — execute and log simulation arrays  
- monte_carlo_results_explainer — prepare narrative summary for Evaluate  
- MarkdownFormatterTool — format final report  

If any tool fails, continue with available data, mark **TBD**, and document fallback under the **WHY** section of the affected cluster.
"""
        expected_output = """
# DECIDE › Simulate — Monte Carlo Simulation Analysis Report (Traceable • Domain-Agnostic • Replicable)

> Reading guide  
> • Every table uses explicit **units** and **frames**.  
> • Each cluster ends with a **WHY paragraph** — **Evidence → Inference → Implication** (what changes, who owns it, which KPI/criterion).  
> • No invented numbers: when inputs are missing, show **TBD** and log them in **Data Gaps & Collection Plan**.  
> • Upstream names/IDs are preserved exactly for Evaluate to cross-link.

---

## 0) Simulation Reference (Cross-Linked)
- **Criteria Lock:** `criteria-vX.Y:<hash>` *(must match upstream)*  
- **Problem Source:** Define Agent vX.Y *(short provenance cue)*  
- **Option Simulated:** [Option label from Create/Implement, verbatim]  
- **Model Type:** Monte Carlo  
- **Iterations:** **≥ 25,000** runs (actual: [integer])  
- **Random Seed:** [integer]  
- **Convergence:** mean/stability result for main KPI within ±1%  
- **Upstream Alignment:** implements thresholds from Criteria Lock (ROI_12m / GDPR_Compliance / Time_to_Impact / Adoption_90d / Reliability_SLO or domain equivalents)  
- **Execution Date/Time:** [YYYY-MM-DD HH:MM]  
- **Language of Output:** [language_selected]

**WHY:** Binds the run to the criteria lock and upstream sources so Evaluate can audit and re-run.

---

## 1) Variable Register (Distributions • Units • Frames • Sources)
> If upstream did **not** provide a value, use the declared safe default and mark **Default Used** — never silently assume.

| Variable | Distribution (type & params) | Mean/Location | Unit | Frame (cohort/geo/time) | Source (Doc-ID/§ or URL+date) | Correlations | Notes |
|---|---|---:|---|---|---|---|---|
| [v1] | [Dist(params)] | [..] | [unit] | [frame] | [source or **Default Used**] | [ρ with …] | [clamps/transform] |
| [v2] | [Dist(params)] | [..] | [unit] | [frame] | [source] | [ρ with …] | [...] |
| … | … | … | … | … | … | … | … |
| … | … | … | … | … | … | … | … |
| … | … | … | … | … | … | … | … |
| … | … | … | … | … | … | … | … |
| … | … | … | … | … | … | … | … |

**Formulas (explicit; units/frames):**  
List all derived variables: ROI, NPV, Payback, Margin, Adoption_90d, SLA %, Reliability_SLO, Conversion, NPS Δ, Productivity Δ, etc.

**WHY:** Ensures traceable inputs and reproducible transformations.

---

## 2) Model Structure & Criteria Constraints
- **Relationships:** e.g., adoption ↑ → utilization ↑ → revenue ↑; reliability ↑ → downtime ↓ → cost ↓; time-to-impact ↓ → faster ROI; price elasticity ↔ conversion ↔ margin.  
- **Non-linearities/Thresholds:** diminishing returns, caps, floors.  
- **Correlations:** implemented per Implement; otherwise stated “assumed independent” with justification.  
- **Criteria as Gates:** pass/fail per run against locked thresholds (ROI_12m, SLA/Availability %, Compliance=100%, Time_to_Impact ≤ target, Adoption_90d ≥ target, etc.).

**WHY:** Makes decision rules computable and auditable within the simulation.

---

## 3) Scenario Design & Environment Configuration
> Scenarios are percentiles **of the simulated distribution**, not hard-coded numbers.

- **Scenario Families:** Strategic / Tactical / Reduced (Micro) — as defined in Implement.  
- **Percentile Mapping:** Optimistic = **P90** • Baseline = **P50** • Pessimistic = **P10**.  
- **Cross-Combinations:** where relevant, cross family variables (e.g., high adoption with low capacity).  
- **Environment Toggles:** capacity, regulation, demand, resources, market volatility, behavioral intensity.  
- **Assumption Layers:** macro / meso / micro tagged for Evaluate.  

**WHY:** Reflects contextual uncertainty and interaction effects that drive tails.

---

## 4) Monte Carlo Configuration (Replicable)
- **Iterations:** **≥ 25,000** (actual: [n]); increase until main KPI mean stabilizes within ±1%.  
- **Random Seed:** [integer]  
- **Sampling Notes:** truncations/clamps per unit domain; transformations logged.  
- **Convergence Check:** pre/post stability metrics and window size.  
- **Execution Metadata:** tool versions, time/iteration.

**WHY:** Establishes statistical reliability and rerun capability.

---

## 5) Results Summary (Primary KPIs — Units & Frames)
> Percentiles are from the simulated distribution.

| KPI (unit) | Mean | P10 | P50 | P90 | StdDev | Source Hook |
|---|---:|---:|---:|---:|---:|---|
| ROI_12m (%) | [..] | [..] | [..] | [..] | [..] | formula+inputs |
| Cost (€/period) | [..] | [..] | [..] | [..] | [..] | inputs |
| Time-to-Impact (weeks) | [..] | [..] | [..] | [..] | [..] | inputs |
| SLA / Reliability (%) | [..] | [..] | [..] | [..] | [..] | SLO mapping |
| Adoption_90d (%) | [..] | [..] | [..] | [..] | [..] | funnel mapping |
| [Domain KPI] | [..] | [..] | [..] | [..] | [..] | [...] |

**WHY:** Centers and tails frame realistic expectations by horizon and unit.

---

## 6) Goal Attainment vs Criteria Lock (Probabilities)
| Criterion | Threshold (unit) | % of Runs Meeting | Evidence Hook |
|---|---|---:|---|
| ROI_12m ≥ [X%] | [X%] | [..]% | Distribution(ROI_12m) |
| [KPI] ≥ / ≤ [T] | [T] | [..]% | Distribution([KPI]) |
| Budget ≤ [Z €] | [Z €] | [..]% | Distribution(Cost) |
| Compliance == 100% | 100% | [..]% | Compliance flag |

- **All Gates Simultaneously Pass:** **[..]%**  
**WHY:** Directly links simulation outcomes to go/no-go policy.

---

## 7) Sensitivity — Tornado & Elasticities
> Rank by absolute **Spearman ρ** with the **primary decision KPI** (default: ROI_12m).

| Variable | Δ used (unit) | Impact on Main KPI (points) | Spearman ρ | Elasticity (ΔY/%ΔX) | Rank |
|---|---|---|---:|---:|---:|
| [var1] | [Δx] | ±[..] | [..] | [..] | 1 |
| [var2] | [Δx] | ±[..] | [..] | [..] | 2 |
| … | … | … | … | … | … |
| … | … | … | … | … | … |
| … | … | … | … | … | … |
| … | … | … | … | … | … |
| … | … | … | … | … | … |
| … | … | … | … | … | … |
| … | … | … | … | … | … |
| … | … | … | … | … | … |
| … | … | … | … | … | … |


**WHY:** Identifies the levers with the largest decision leverage and where to focus experiments/mitigations.

---

## 8) Influence & Favorability Matrix (Required for Evaluate)
> Logs how each variable shifts scenario **favorability** and contributes to variance.

| Variable | KPI | Direction (+/–) | ΔX → ΔY (unit mapping) | Elasticity | Variance Contribution (%) | Criticality (H/M/L) | Interactions/Notes |
|---|---|---|---|---:|---:|---|---|
| [v] | ROI_12m | + | +1 pp → +0.9 pts | 0.9 | 18.2 | H | interacts with [w] |
| [w] | SLA % | – | +10 ms p95 → –0.2 pp | 0.2 | 7.5 | M | correlated with load |
| … | … | … | … | … | … | … | … |
| … | … | … | … | … | … | … | … |
| … | … | … | … | … | … | … | … |
| … | … | … | … | … | … | … | … |
| … | … | … | … | … | … | … | … |
| … | … | … | … | … | … | … | … |
| … | … | … | … | … | … | … | … |
| … | … | … | … | … | … | … | … |
| … | … | … | … | … | … | … | … |

**WHY:** Supplies Evaluate with causal direction, magnitude, and interaction context to generate ranked recommendations.

---

## 9) Behavioral & Customer Dynamics (If Applicable)
- Levers: defaults, framing, salience, timing, social proof, friction reduction, commitment.  
- Each lever is modeled as a **distribution of effect size** and mapped to funnel KPIs.

| Lever | Distribution | Expected Effect (unit/frame) | Affected KPI | Telemetry Hook | Ethical Guardrail |
|---|---|---|---|---|---|
| [Default Opt-In] | Triangular(l,m,u) | +[..] pp adoption / 90d | Adoption_90d | event_adopt | no dark patterns |
| [Friction –1 step] | Discrete{-1,-2} | +[..] pp completion / 14d | Conversion % | event_complete | accessibility check |
| … | … | … | … | … | … |
| … | … | … | … | … | … |
| … | … | … | … | … | … |
| … | … | … | … | … | … |
| … | … | … | … | … | … |
| … | … | … | … | … | … |
| … | … | … | … | … | … |

**WHY:** Connects human-behavior assumptions to measurable uplift and risk controls.

---

## 10) Scenario Cards (Percentile-Mapped)
> Optimistic = P90, Baseline = P50, Pessimistic = P10 drawn from the same distribution.

| Metric | Optimistic (P90) | Baseline (P50) | Pessimistic (P10) | Range | Unit |
|---|---:|---:|---:|---:|---|
| ROI_12m | [..] | [..] | [..] | [P90–P10] | % |
| Cost | [..] | [..] | [..] | [..] | € |
| Time-to-Impact | [..] | [..] | [..] | [..] | weeks |
| SLA / Reliability | [..] | [..] | [..] | [..] | % |
| Adoption_90d | [..] | [..] | [..] | [..] | % |
| [Domain KPI] | [..] | [..] | [..] | [..] | [unit] |

**WHY:** Provides leadership a clear view of good/typical/bad outcomes under the same assumptions.

---

## 11) Risk Metrics (Downside & Overrun)
- **VaR(5%)** and **Expected Shortfall(5%)** for ROI or Net Benefit  
- **P(Cost > Budget)**, **P(Timeline > Plan)**, **P(KPI below min tolerance)**  
- **Top Quantified Risk Drivers:** [1–3 with variance contribution and direction]  
- **Expected Loss (€) = Prob × Impact (€)** per top risk

**WHY:** Sizes buffers/contingencies and targets mitigations where they matter most.

---

## 12) Decision Guidance (Rules Aligned to Criteria)
- **GO** if **P(all gates pass) ≥ 70%** and downside risk within limits (VaR/ES thresholds).  
- **HOLD** if main KPI meets but secondary criteria fail with **P > 30%**.  
- **NO-GO** if **P(main KPI ≥ threshold) < 60%** or catastrophic tail risk (e.g., >30% budget overrun).  
- **Early Triggers:** if observed metrics deviate by >X% from expected P50 after [period], re-simulate and re-decide.

**WHY:** Converts distributions into clear, criteria-locked decision rules.

---

## 13) Data Gaps & Collection Plan (MANDATORY for any TBD)
| Missing Data | Why Needed | Method (instrument/test/query) | Owner | ETA | Acceptance | Expected Source |
|---|---|---|---|---|---|---|
| [TBD item] | Calibrate [variable] | AB test / query / log | [role] | [date] | CI width ≤ x% | [system/doc] |
| … | … | … | … | … | … | … |
| … | … | … | … | … | … | … |
| … | … | … | … | … | … | … |
| … | … | … | … | … | … | … |
| … | … | … | … | … | … | … |
| … | … | … | … | … | … | … |
| … | … | … | … | … | … | … |
| … | … | … | … | … | … | … |
| … | … | … | … | … | … | … |
| … | … | … | … | … | … | … |
| … | … | … | … | … | … | … |

**WHY:** Reduces uncertainty on a schedule with accountable owners.

---

## 14) Visual Summaries (optional images; described if text-only)
- Density/histograms with P10/P50/P90 markers for key KPIs  
- CDF for goal attainment vs thresholds  
- Tornado chart for sensitivity (top drivers)  
- Scenario boxplots (P10/P50/P90)  

**WHY:** Aids executive comprehension of tails and trade-offs.

---

## 15) Plain-Language Explainer (For Non-Technical Stakeholders)
- **Most likely (P50)** means typical outcome given today’s uncertainty.  
- **Best reasonable (P90)** has ≈10% chance to do better.  
- **Worst reasonable (P10)** has ≈90% chance to do better.  
- **Success odds** report the probability of passing locked gates simultaneously.

**WHY:** Ensures decisions are understood and defensible.

---

## Appendix
- **A. Parameters & Bounds:** JSON-like listing (names, dists, params, clamps)  
- **B. Formulas:** ROI/NPV/Payback; KPI transforms; unit conversions  
- **C. Source Register:** title • publisher • date (YYYY-MM-DD) • URL or Doc-ID/§ • source type • recency

---

## Final Validation Checklist (ALL must be YES)
- criteria_lock_and_option_present == true  
- iterations_≥_25000_and_mean_stability_±1pct == true  
- variable_register_with_distributions_units_sources_complete == true  
- sensitivity_tornado_and_elasticities_computed == true  
- influence_and_favorability_matrix_present == true  
- percentiles_P10_P50_P90_for_all_primary_KPIs == true  
- goal_attainment_probabilities_vs_criteria_reported == true  
- behavioral_dynamics_included_if_applicable == true  
- risk_metrics_VaR_ES_overrun_probabilities_reported == true  
- scenario_cards_percentile_mapped_and_comparison_table == true  
- data_gaps_and_collection_plan_present == true  
- provenance_cues_and_why_paragraphs_present == true  
- no_invented_data_and_all_material_claims_have_provenance == true
"""

        
        return Task(
            description = description,
            expected_output = expected_output,
            markdown=True,
            agent = agent,
            output_file="07_simulation_analysis_report.md"
        )
            