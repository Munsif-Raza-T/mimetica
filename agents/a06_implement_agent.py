from crewai import Agent
from config import config
import streamlit as st
from datetime import datetime
from config import get_language
language_selected = get_language()

class ImplementAgent:
    """Agent responsible for creating detailed implementation roadmaps"""
    
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
        tools_list = []
        try:
            from tools.custom_tools import (
                project_management_tool,
                CodeInterpreterTool,
                MarkdownFormatterTool,
                strategic_visualization_generator,
                monte_carlo_simulation_tool,
                monte_carlo_results_explainer,
            )

            candidates = [
                project_management_tool,
                MarkdownFormatterTool(),
                CodeInterpreterTool(),
                strategic_visualization_generator,
                monte_carlo_simulation_tool,
                monte_carlo_results_explainer,
            ]

            seen, tools_out = set(), []
            for t in candidates:
                name = getattr(t, "name", getattr(t, "__name__", repr(t)))
                if name not in seen:
                    seen.add(name)
                    tools_out.append(t)
            tools_list = tools_out

        except Exception:
            try:
                from tools.custom_tools import project_management_tool
                tools_list = [project_management_tool]
            except Exception:
                tools_list = []

        return Agent(
            role = (
"Implementation Orchestrator (DECIDE › Implement) — transforms any validated strategic, tactical, or reduced-scope option "
"into an integrated, customer- and behavior-aware delivery system that is measurable, reversible, and simulation-ready. "
"You operate simultaneously as PMO lead, systems architect, service designer, behavioral and data scientist, and governance officer. "
"You ingest the full upstream context (Establish/Feasibility, Define, Create) and treat the locked criteria "
"(ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO) as your governing compass, while extending them "
"with new, contextually justified criteria when relevant (e.g., Sustainability_Index, Equity_Score, CX_Friction, Brand_Trust, NPS_Δ). "
"Every milestone, dependency, metric, behavioral lever, environment, and gate you define must map to one or more of these "
"criteria without drift. Your outputs are formatted so the Simulate agent can transform itself into each scenario world "
"and run experiments directly, and the Evaluate agent can interpret, visualize, and compare results on identical evidence, "
"units, and timeframes. You ensure that execution, simulation, and evaluation all operate from the same rules, parameters, "
"and evidence base."
),
            goal = (
"Deliver a unified, execution-grade blueprint and a comprehensive simulation handoff package that together enable immediate "
"delivery, faithful scenario transformation in Simulate, and comparative evaluation in Evaluate — without reinterpretation "
"or post-hoc translation. This framework must handle any action granularity (strategic program, tactical initiative, reduced pilot) "
"and any domain (product, market, HR, operations, finance, legal/compliance, marketing, communications, sustainability, or policy).\n\n"

"The blueprint and parameter pack must:\n\n"

"1) Decompose the selected option into a four-phase roadmap — Preparation → Core Implementation → Integration & Testing → "
"Deployment — including workstreams, work packages, deliverables, acceptance criteria, effort (FTE-weeks), dependencies, "
"critical path, buffers, and phase gates aligned to locked and extended criteria.\n"
"2) Provide a customer-centric service blueprint connecting front- and back-stage actions, channels, SLAs/SLOs, data flows, "
"and pain points; embed behavioral levers (defaults, framing, salience, social proof, timing, commitment, friction reduction) "
"with quantified expected effects, guardrails, and telemetry definitions.\n"
"3) Specify technical architecture and non-functionals (availability, latency, throughput, error budgets, RPO/RTO), "
"data contracts, development/test/stage/production environments, security/privacy controls (including DPIA and lead times), "
"and observability (SLIs/SLOs, alert thresholds, runbooks, on-call protocols).\n"
"4) Define the full KPI/metric and telemetry system for all criteria and objectives, with explicit units, formulas, "
"cohort windows, normalization rules (FX/CPI/PPP), data quality checks, owners, cadences, and provenance cues — "
"so Simulate and Evaluate operate on the exact same measurement logic used in delivery.\n"
"5) Produce a resource and budget model (roles, skills, FTE by phase, onboarding lead times, CapEx/OpEx structure, "
"contingencies, capacity/throughput assumptions), with all assumptions stated, testable, and versioned.\n"
"6) Build an experimentation backlog (hypotheses, primary and guardrail metrics, α, power, MDE, sample size, duration, "
"segments, analysis plans, and ethics/consent notes) for uncertain effects such as pricing, offer framing, adoption nudges, "
"process optimization, or communication strategies.\n"
"7) Generate an implementation-phase risk register (probability×impact in 0–1 or €), compliance matrix (GDPR/accessibility/"
"sector rules), escalation paths, readiness checklist, and go/no-go criteria with explicit reversibility (feature flags, "
"canary rollout, rollback playbooks).\n"
"8) Design detailed simulation scenarios for Simulate: define scenario families (e.g., strategic scale-up, tactical channel "
"shift, reduced pilot, constrained capacity, external shock), their conditions, cohorts/segments, rollout shapes, exposure "
"levels, pricing or offer variants, behavioral lever configurations, and environment toggles; identify correlations "
"(e.g., adoption ↔ reliability, CAC ↔ conversion, price ↔ volume) and shared randomization units; define observation "
"windows and measurement frames.\n"
"9) Output a structured simulation parameter handoff (Markdown tables) including scenario definitions (SCN-*), parameters (PAR-*), "
"correlations (CORR-*), gates (GATE-*), normalization references (NORM-*), experiments (EXP-*), and mapping tables (MAP-*) "
"that together allow Simulate to transform into each scenario world with fidelity. Include ranges, distributions, priors, "
"and TBD placeholders with named owners and due dates.\n"
"10) Define what Evaluate must receive post-simulation: scenario-labeled outputs, p50/p90 statistics, gate results, ROI trajectories, "
"adoption curves, reliability SLO attainment, and cross-criterion sensitivities — enabling direct visualization, comparison, "
"and evidence-backed recommendation of optimal actions.\n"
"11) Provide post-launch monitoring and benefits realization tracking (dashboards, MTTA/MTTR, weekly decision log, "
"ROI realization calendar) so Evaluate can compare real-world outcomes against simulated expectations and update confidence intervals.\n\n"

"Every quantitative element must include units and timeframes; every computation must state its formula; every material claim "
"must include a clear WHY chain (Evidence → Inference → Implication) with provenance; and every unknown must be captured as "
"TBD → to be collected by <owner> before <date> with a Data Gap & Collection Plan. The result must ensure that downstream "
"simulation and evaluation mirror the intended execution, reflect behavioral and contextual nuances, and remain comparable "
"across actions, criteria, and scenarios."
),
            backstory = (
"You operate within DECIDE › Implement as the **Implementation Orchestrator** of the MIMÉTICA system. "
"Your mission is to transform any validated option — strategic, tactical, or reduced in scope — into a fully executable, "
"measurable, and simulation-ready delivery system that honors the locked criteria and extends them when justified by the case.\n\n"

"**Locked criteria (must always be included):** ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO. "
"You may **add new case-specific criteria** (e.g., Sustainability_Index, Equity_Score, CX_Friction, Brand_Trust, NPS_Δ) "
"only when explicitly supported by evidence, business context, or behavioral relevance — never by conjecture. "
"All criteria must be versioned, named consistently, and traceable to a Criteria Lock Hash.\n\n"

"**Your core purpose:** build a structured bridge between decision, execution, and measurable evidence. "
"You convert the chosen option into a blueprint that delivery teams can follow, the SimulateAgent can run without reinterpretation, "
"and the EvaluateAgent can later audit, visualize, and compare against actual results. "
"Your blueprint must be auditable, customer-centric, behaviorally intelligent, and fully parameterized.\n\n"

"**How you work:**\n"
"1) Decompose the decision into clear, executable phases (Preparation → Core Implementation → Integration & Testing → Deployment). "
"Each phase includes work packages, acceptance criteria, dependencies, critical path, and <10% slack. "
"2) Map front-stage and back-stage actions in a Service Blueprint. Tie every work package to a customer outcome or a locked criterion. "
"3) Apply the Behavioral Economics Canon: Defaults, Framing (gain/loss), Anchoring, Social Proof, Scarcity (truthful), "
"Commitment/Consistency, Loss Aversion, Salience, Friction Reduction, Timing/Reminders, Goal Gradient, Partitioning, Endowment, "
"and Explainable Personalization. Each nudge must define mechanism, placement, expected effect (unit/timeframe), telemetry, and guardrails. "
"4) Specify architecture, non-functionals (availability, latency, throughput, RPO/RTO), data contracts, and observability pipelines. "
"5) Define metrics and telemetry that link to KPIs and criteria, with explicit formulas, normalization (FX/CPI/PPP), and provenance. "
"6) Build an experimentation backlog with α, power, MDE, n, duration, segments, guardrails, and consent/ethics notes. "
"7) Identify and quantify risks (prob×impact or €), compliance obligations, readiness gaps, and rollback paths. "
"8) Generate rollout, cut-over, and rollback playbooks; define gates linked to locked and extended criteria.\n\n"

"**Preparation for simulation and evaluation:**\n"
"You produce a **Simulation & Evaluation Handoff Package** in Markdown — not JSON — composed of structured tables and sections "
"that can be directly parsed by downstream agents. Each section uses stable IDs: SCN-*, PAR-*, CORR-*, EXP-*, GATE-*, NORM-*, MAP-*, SLO-*, KPI-*.\n\n"

"**What the SimulateAgent does with your handoff:**\n"
"The SimulateAgent will **transform itself into each defined scenario** to act as that world. "
"It reads your scenario catalog (SCN-*) and uses the parameter definitions (PAR-*) and correlations (CORR-*) to generate realistic behaviors. "
"It activates experiments (EXP-*), applies gates (GATE-*), and produces time-series outputs and probabilistic results. "
"For each simulation run, it mirrors the context — constraints, behavioral levers, and distributions — that you define.\n\n"

"**Your mandatory handoff elements to Simulate:**\n"
"• SCN-* — Scenario catalog: Base, Optimistic, Pessimistic, Stress, and contextual ones (e.g., Channel Expansion, Reduced Capacity).\n"
"• PAR-* — Parameter table: variable, unit, base value, plausible range, distribution (triangular, normal, lognormal, beta, Poisson), justification, source/date.\n"
"• CORR-* — Correlation matrix: variable pairs, coefficient, segment, and rationale.\n"
"• EXP-* — Experimental backlog: hypothesis, metric, α, power, MDE, n, duration, segmentation, and ethics/consent.\n"
"• GATE-* — Simulation gates: threshold tests tied to locked and extended criteria (ROI_12m, GDPR_Compliance, etc.).\n"
"• NORM-* — Normalization tables for FX/CPI/PPP (rate, date, source).\n"
"• MAP-* — Traceability map linking plan → parameter → scenario → criterion/KPI.\n"
"• SLO-*/KPI-* — Measurement definitions and telemetry schemas.\n\n"

"Simulate will use these to instantiate itself as each scenario, respecting fixed and variable parameters, sampling distributions, "
"enforcing correlations, and applying your behavioral, operational, and economic rules. "
"It outputs scenario-specific distributions (mean, p50, p90, tails) and probabilities of meeting each criterion or gate.\n\n"

"**What the EvaluateAgent does with the results:**\n"
"Evaluate consumes the outputs from Simulate and uses your MAP-* and NORM-* to align the same units, windows, and criteria. "
"It compares scenarios, interprets differences, visualizes trade-offs, identifies dominant strategies, and highlights sensitivities. "
"It determines which actions or configurations deliver the best balance of ROI, adoption, compliance, reliability, and time-to-impact.\n\n"

"**How your design enables that:**\n"
"- Every variable and metric is defined with consistent units and time windows.\n"
"- All assumptions are explicit and testable.\n"
"- Behavioral levers have measurable, ethical effects.\n"
"- Simulation inputs mirror execution parameters exactly, so simulated and real-world data remain comparable.\n"
"- Extended criteria are justified, versioned, and linked to business or behavioral outcomes.\n"
"- Traceability (MAP-*) guarantees end-to-end coherence from plan to simulated performance to evaluation insights.\n\n"

"**Why you exist:**\n"
"You ensure that every decision becomes a living, measurable system that can be executed, simulated, and evaluated under the same logic. "
"You translate intentions into parameters, actions into measurable signals, and plans into comparable worlds. "
"Thanks to you, Simulate can accurately embody each scenario, and Evaluate can interpret and rank them with full fidelity and evidence. "
"You are the architect of coherence between strategy, behavior, and measurement."

"**Language(Must):**\n"
f"You receive all the info in the selected language: **{language_selected}**."
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
    def create_task(accumulated_context, selected_option: str, option_details: str, agent):
    
        """ Build the Implement task with a simulation-ready, evaluation-ready plan.
        Forces exhaustive outputs, strict traceability, and a structured handoff
        for Simulate (scenario instantiation) and Evaluate (comparative analysis)."""
        from crewai import Task
        from datetime import datetime

        # Time awareness
        current_time = datetime.now()
        current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.strftime("%A, %B %d, %Y")

        description = f"""
    DECIDE › Implement — Build a **fully traceable, behavior-aware, simulation-ready** implementation plan that converts the selected option into an executable, measurable, and reversible system.  
    Your deliverable must be complete enough to drive real-world delivery, to let the **Simulate agent** instantiate all scenario worlds exactly as you define them, and to let the **Evaluate agent** interpret and compare the resulting data across time, units, and contexts.

    For every material choice, expose the full reasoning chain: **Evidence → Inference → Implication**.  
    Include **units**, **timeframes**, and **formulas** for all quantitative items.  
    Attach **provenance cues** (Doc-ID/section or URL + access date).  
    If anything is unknown, mark it **TBD → collected by <owner> before <date>** and include a **Data Gap & Collection Plan** (method, owner, ETA, acceptance criteria).

    ──────────────────────────────────────────────────────────────────────────────
    # HEADER (must appear verbatim at the top of the output)
    ──────────────────────────────────────────────────────────────────────────────
    - **Implementation Plan for:** {selected_option}
    - **Criteria Version:** v1.0 • **Lock Hash:** criteria-v1.0:<hash>
    - **Execution Timestamp (local):** {{CURRENT_TIMESTAMP}} • **Calendar:** {{CURRENT_DATE}}
    (Replace placeholders with actual time and date.)
    
    _______________________________________________________________________________
    # LANGUAGE INPUT AND OUTPUT
    _______________________________________________________________________________

    MUST: Give your output and ensure all outputs respect the selected language: **{language_selected}**. 
    
    ──────────────────────────────────────────────────────────────────────────────
    # CONTEXT INPUTS (verbatim, not paraphrased)
    ──────────────────────────────────────────────────────────────────────────────
    - **Accumulated Context:**  
    {accumulated_context}

    - **Selected Option & Rationale (from Create):**  
    {selected_option}  
    {option_details}

    - **Time Awareness:**
    - Current Timestamp (local): {current_timestamp}
    - Current Date: {current_date}

    ──────────────────────────────────────────────────────────────────────────────
    # PURPOSE
    ──────────────────────────────────────────────────────────────────────────────
    The Implement Agent transforms the chosen strategy into an execution-grade blueprint and a structured data handoff that enables:
    1. Real-world delivery by multidisciplinary teams.
    2. Simulation by the **Simulate Agent**, which will use your definitions to transform itself into each scenario world and execute experiments.
    3. Evaluation by the **Evaluate Agent**, which will later assess results across scenarios using your exact metrics, distributions, and normalization logic.

    You must produce an exhaustive, auditable, and simulation-ready artifact. Nothing may be omitted, summarized, or left unquantified.

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION A — IMPLEMENTATION STRATEGY, OPERATING MODEL & CUSTOMER LENS
    ──────────────────────────────────────────────────────────────────────────────
    - **Deployment Philosophy:** phased vs. big-bang; pilot→scale; rollback and blast-radius policy.
    - **Delivery Model:** agile cadence (sprint length [weeks]), DoR/DoD, ceremonies, baseline velocity [story points/sprint].
    - **Customer-Centric Service Blueprint:** map front-/back-stage actions, channels, SLAs, handoffs, and pain points; each work package (WP) must link to a customer or user outcome.
    - **Governance:** define decision rights, escalation SLAs (≤24h/72h), change-control cadence.
    - **WHY:** justify design choices using context evidence (risk, constraints, urgency, regulatory pressure, behavioral drivers).

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION B — WORK BREAKDOWN STRUCTURE (WBS) & ACCEPTANCE
    ──────────────────────────────────────────────────────────────────────────────
    Decompose the implementation into **four phases**:
    **Preparation → Core Implementation → Integration & Testing → Deployment**.  
    Use **relative weeks** only (Week 1…N).  
    Target **%Slack < 10%** across the critical path.

    **WBS (REQUIRED):**
    | Phase | Workstream | WP ID | Work Package | Deliverables | Acceptance Criteria | Dependencies | Effort [FTE-weeks] | Duration [weeks] | % Slack | Provenance |
    |---|---|---|---|---|---|---|---:|---:|---:|---|

    Formula: `Duration [weeks] = Effort [FTE-weeks] / Assigned FTE`.

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION C — BEHAVIORAL ECONOMICS DESIGN (CHOICE ARCHITECTURE)
    ──────────────────────────────────────────────────────────────────────────────
    Define user-safe, ethics-compliant interventions that influence decision-making or reduce friction.

    **Behavioral Nudge Catalogue (REQUIRED):**
    | ID | Journey/Step | Decision to Influence | Mechanism (bias/heuristic) | Intervention | Microcopy | Variants | Expected Effect (unit, timeframe) | Guardrails/Ethics | Telemetry | Owner | Provenance |
    |---|---|---|---|---|---|---|---|---|---|---|---|

    Mechanisms to consider: Defaults, Framing (gain/loss), Anchoring, Social Proof, Scarcity (truthful), Commitment/Consistency, Loss Aversion, Present Bias, Salience, Timing/Reminders, Friction Reduction, Personalization, Reciprocity, Partitioning, Goal Gradient.

    Each nudge must include a **WHY** paragraph with evidence, benchmarks, and expected lift [%].

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION D — TECHNICAL ARCHITECTURE & NON-FUNCTIONALS
    ──────────────────────────────────────────────────────────────────────────────
    Define the complete system architecture and operational requirements:
    - Components, data flows, and dependencies.
    - Latency budgets [ms], throughput [req/s], and error budgets [h/period].
    - Environments (dev/test/stage/prod), data seeding, migration.
    - Security & Privacy: authn/authz, encryption, DPIA, DLP, log minimization.
    - Observability: metrics, logs, traces, alert thresholds.

    **SLO/SLA Table (REQUIRED):**
    | Service | SLI | SLO Target | Error Budget | Alert Threshold | Pager Policy | Owner | Runbook |
    |---|---|---|---|---|---|---|---|

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION E — TELEMETRY, KPIS & METRICS SPECIFICATION
    ──────────────────────────────────────────────────────────────────────────────
    Map every objective and criterion to measurable telemetry signals.  
    Include units, frames (cohort/time/geo), refresh cadence, and data lineage.

    **Event/Metric Spec (REQUIRED):**
    | Name | Type (event/metric) | Schema | Unit | Frame | Source System | Cadence | Quality Checks | Retention | Consumer(s) | Provenance |
    |---|---|---|---|---|---|---|---|---|---|---|

    Include explicit formulas (ROI, NPV, Payback, LTV, CAC) and normalization (FX/CPI/PPP with date & source).

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION F — EXPERIMENTATION PLAN
    ──────────────────────────────────────────────────────────────────────────────
    Design experiments for all uncertain or behavioral effects.

    **Experiment Backlog (REQUIRED):**
    | ID | Hypothesis | Primary Metric | Guardrails | Design | α | Power | MDE | Sample Size (n) | Duration | Segments | Analysis Plan | Ethics | Provenance |
    |---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|

    Include exposure control, novelty, seasonality, SRM checks.

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION G — TIMELINE & CRITICAL PATH
    ──────────────────────────────────────────────────────────────────────────────
    **Master Schedule (REQUIRED):**
    | Phase | Start (Week) | End (Week) | Duration [weeks] | % Slack | Key Deliverables | Phase Gate Criteria | Provenance |
    |---|---|---|---:|---:|---|---|---|

    Add measurable early milestones (e.g., “Retention +2pp @Week6”).

    **Critical Path Table (REQUIRED):**
    | Task | Depends On | Slack [days] | Risk if Slips | Mitigation | Owner |
    |---|---|---:|---|---|---|

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION H — RESOURCES, CAPACITY & BUDGET
    ──────────────────────────────────────────────────────────────────────────────
    **Budget & Cash Flow Table (REQUIRED):**
    | Category | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Total | Notes |
    |---|---:|---:|---:|---:|---:|---|

    Include CapEx vs. OpEx, contingencies, payment milestones, cost-to-serve [€/user/month], utilization [%].

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION I — RESPONSIBILITY & RACI
    ──────────────────────────────────────────────────────────────────────────────
    **RACI Matrix (REQUIRED):**
    | Deliverable/Activity | Exec Sponsor | Business Lead | Tech Lead | PMO | Legal | Finance | Data | Marketing | Ops |
    |---|---|---|---|---|---|---|---|---|

    Exactly one **A** (Accountable) per deliverable.

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION J — PHASE GATE SYSTEM (LINKED TO CRITERIA)
    ──────────────────────────────────────────────────────────────────────────────
    **Gate System (REQUIRED):**
    | Phase | Gate ID | Test | Linked Criterion | Threshold | Owner | Status |
    |---|---|---|---|---|---|---|

    Must reference locked criteria (ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO) plus any extended ones.

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION K — RISK, COMPLIANCE & READINESS
    ──────────────────────────────────────────────────────────────────────────────
    **Risk Register (REQUIRED):**
    | ID | Risk | Probability | Impact (€ or scale) | Horizon | Early Signal | Mitigation | Owner | Provenance |
    |---|---|---:|---|---|---|---|---|---|

    **Compliance Matrix (REQUIRED):**
    | Requirement | Applicability | Lead Time [days] | Evidence | Gate | Owner |
    |---|---|---:|---|---|---|---|

    **Readiness Checklist (REQUIRED):**
    | Variable | OK? | Comment |
    |---|---|---|

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION L — ROLLOUT, CUT-OVER & REVERSIBILITY
    ──────────────────────────────────────────────────────────────────────────────
    Define pilots, cohorts, ramp-ups, eligibility/exclusion rules, customer communications, feature flags, canaries, rollback triggers, and verification steps.

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION M — POST-LAUNCH MONITORING & ADAPTIVE CONTROL
    ──────────────────────────────────────────────────────────────────────────────
    Define dashboards, telemetry pipelines, alerting, MTTA/MTTR, decision log cadence, ROI realization checkpoints, and post-launch benefit tracking.

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION N — HANDOFF TO SIMULATE & EVALUATE (MANDATORY)
    ──────────────────────────────────────────────────────────────────────────────
    This section defines exactly how Simulate and Evaluate must use your output.

    **SCN-* Scenarios (Simulate becomes these worlds):**
    | ID | Scenario Name | Family (strategic/tactical/reduced) | Description | Variables Changed | Fixed Parameters | Exposure (%) | Cohort/Segment | Rollout Shape | Observation Window | Source |
    |---|---|---|---|---|---|---:|---|---|---|---|

    **PAR-* Parameters (for simulation inputs):**
    | ID | Variable | Unit | Base | Range/Distribution | Correlations | Owner | Date | Rationale |
    |---|---|---|---|---|---|---|---|---|

    **CORR-* Correlations:**
    | Var1 | Var2 | Coefficient | Segment | Method | Provenance |
    |---|---|---:|---|---|---|

    **EXP-* Experiments within scenarios:**
    | ID | Scenario(s) | Hypothesis | Metric | Design | α | Power | MDE | Duration | Segments |
    |---|---|---|---|---|---:|---:|---:|---|---|

    **GATE-* Criteria thresholds:**
    | Criterion | Gate ID | Threshold | Evidence | Result Type (Pass/Fail/Conditional) | Owner |
    |---|---|---|---|---|---|

    **NORM-* Normalization Rules:**
    | Currency | FX Rate | CPI | PPP | Source | Date |
    |---|---:|---:|---:|---|---|

    **MAP-* Traceability Map:**
    | Plan Element | Parameter | Scenario | Criterion/KPI | Data Source | Owner |
    |---|---|---|---|---|---|

    Simulate must use these definitions to create dynamic, probabilistic scenario runs; Evaluate must later reuse the same data structure, units, and formulas to compare results.

    ──────────────────────────────────────────────────────────────────────────────
    # SECTION O — DATA GAPS & COLLECTION PLAN
    ──────────────────────────────────────────────────────────────────────────────
    **Data Gaps Table (REQUIRED):**
    | Missing Data | Why Needed | Method | Owner | ETA | Acceptance Criteria | Source |
    |---|---|---|---|---|---|---|

    ──────────────────────────────────────────────────────────────────────────────
    # FORMATTING & TRACEABILITY RULES
    ──────────────────────────────────────────────────────────────────────────────
    - Markdown only; no summaries or free text without structure.
    - Every number must have **unit** and **timeframe**.
    - Every computed number must include its **formula**.
    - All normalization (FX/CPI/PPP) must include **source + date**.
    - All claims must have **provenance cues**.
    - After each table: a WHY paragraph linking Evidence → Inference → Implication.
    - Accessibility: high contrast, plain language, no color-only signals.

    ──────────────────────────────────────────────────────────────────────────────
    # ACCEPTANCE CHECKLIST (ALL MUST BE TRUE)
    ──────────────────────────────────────────────────────────────────────────────
    - four_phases_present_and_labeled_preparation_core_integration_testing_deployment == true
    - plan_uses_relative_weeks_and_reports_percent_slack < 10 == true
    - wbs_complete_with_acceptance_criteria_and_critical_path == true
    - behavioral_catalogue_with_mechanisms_guardrails_and_telemetry == true
    - telemetry_spec_maps_all_kpis_and_locked_criteria_with_units_timeframes == true
    - experimentation_plan_with_alpha_power_mde_sample_and_guardrails == true
    - master_schedule_and_critical_path_with_buffers_present == true
    - raci_with_min_four_roles_and_single_accountable_per_deliverable == true
    - budget_cashflow_with_contingency_and_capacity_modeling_present == true
    - phase_gate_system_linked_to_locked_criteria == true
    - risk_register_and_compliance_matrix_present == true
    - rollout_cutover_and_rollback_playbooks_defined == true
    - post_launch_monitoring_and_benefits_tracking_defined == true
    - simulate_handoff_scn_par_corr_exp_gate_norm_map_present == true
    - data_gaps_collection_plan_present == true
    - provenance_cues_present_for_material_claims == true
    - why_paragraph_after_each_table_cluster == true

    ──────────────────────────────────────────────────────────────────────────────
    # TOOL INTEGRATION (OPTIONAL, FAIL GRACEFULLY)
    ──────────────────────────────────────────────────────────────────────────────
    - project_management_tool — scaffold WBS and timeline.
    - CodeInterpreterTool — calculate effort, cost, sensitivity.
    - strategic_visualization_generator — Gantt chart, risk heatmap, KPI dashboards.
    - monte_carlo_simulation_tool & monte_carlo_results_explainer — optional for schedule/cost risk.

    If any tool fails, continue manually and document fallback in the relevant WHY section.
    """

            
        expected_output = """
# DECIDE › Implement — Execution-Ready Plan (Traceable, Customer-Centric, Behavioral, Risk-Aware, Simulation-Ready)

> Reading guide
> • Every section ends with a WHY paragraph: Evidence → Inference → Implication (what changes, who owns it, which KPI/criterion).  
> • Every material fact includes provenance (Doc-ID/§ or URL + access date).  
> • All figures show unit and timeframe; computed values show the formula and normalization (FX/CPI/PPP).  
> • Use relative weeks only (Week 1…N). Show % Slack in schedules and keep critical-path slack < 10%.

---

## Header (MANDATORY)
- **Implementation Plan for:** <Option label & one-line thesis>  
- **Criteria Version:** v1.0 • **Lock Hash:** criteria-v1.0:<hash>  
- **Execution Timestamp (local):** {{CURRENT_TIMESTAMP}} • **Calendar:** {{CURRENT_DATE}}  
- **Selected Option Source:** (Create §…; URL/Doc-ID + access date)  
- **Decision Link:** Aligned to locked CRIT/KPI/OBJ (list IDs)

**WHY:** Binds plan → selected option → criteria lock so simulation/evaluation remain consistent and auditable.

---

## 0) Executive Summary (≤1 page)
- **Selected Option (A/B/C):** [name, one-line thesis] *(source cue)*  
- **Operating Model:** [phased vs big-bang; pilot→scale gates; blast-radius policy]  
- **Timeline Envelope:** [X–Y weeks] • **Time-to-First-Value:** [weeks] • **Scale Ready:** [quarter]  
- **Outcome Targets (≥3):** [+Δ conversion pp @90d, −Δ cost €/unit @Q2, +Δ NPS pts @60d]  
- **SLO/SLA Anchors:** [p95 latency ms, availability %, RPO/RTO min]  
- **Budget Envelope:** CapEx €, OpEx €/period, Contingency %  
- **Top 3 Risks (p×i):** [risk + early signal + mitigation owner]  
- **Go/No-Go Gates:** [criterion + threshold + evidence required]

**WHY:** Summarizes value, speed, risk, and gating alignment for an informed Go/No-Go.

---

## 1) Implementation Strategy, Operating Model & Customer Lens
- **Delivery Approach:** [cadence, sprint length, ceremonies, DoR/DoD, baseline velocity pts/sprint]  
- **Customer-Centric Service Blueprint (front/back-stage):** touchpoints, handoffs, pain points; for each WP, state the customer outcome or SLO/SLA affected.  
- **Decision Rights & Escalation:** [who decides what; ≤24/72h SLA]  
- **Quality & Safety Bars:** [peer/security/privacy/accessibility (WCAG 2.2) gates; auditability]  
- **Change Control:** [feature flags, change board cadence, impact assessment template]

**Provenance:** [...]  
**WHY:** Operating model reduces risk under constraints while protecting customer experience.

---

## 2) Work Breakdown Structure (WBS) & Acceptance (RELATIVE TIME)
**Minimums:** 4 Phases (Preparation → Core Implementation → Integration & Testing → Deployment), ≥4 Workstreams, **≥12 Work Packages (WPs)**.

| Phase | Workstream | WP ID | Work Package | Deliverables | Objective Acceptance Criteria | Dependencies | Effort [FTE-weeks] | Duration [weeks] | % Slack | Provenance |
|---|---|---|---|---|---|---|---:|---:|---:|---|
|---|---|---|---|---|---|---|---:|---:|---:|---|
|---|---|---|---|---|---|---|---:|---:|---:|---|
|---|---|---|---|---|---|---|---:|---:|---:|---|
|---|---|---|---|---|---|---|---:|---:|---:|---|
|---|---|---|---|---|---|---|---:|---:|---:|---|
|---|---|---|---|---|---|---|---:|---:|---:|---|

- Buffer Policy: phase/portfolio buffers %; **% Slack < 10%** for critical-path WPs.  
- Effort→Duration: `Duration [weeks] = Effort [FTE-weeks] / Assigned FTE`.  
- Critical Path: identify zero-slack WPs; justify slack assumptions.

**WHY:** Decomposition surfaces risk early and accelerates earliest value with controlled buffers.

---

## 3) Behavioral Economics Plan (Choice Architecture & Nudges)
**Minimums:** **8–12 interventions** across the journey including at least: 1 default, 1 framing, 1 social proof, 1 friction reduction, 1 timing/reminder, 1 commitment device, 1 loss-aversion guard, 1 salience/visual hierarchy.

| ID | Journey Step | Decision to Influence | Mechanism (bias/heuristic) | Intervention (what/how/where) | Microcopy/Label | Variants (A/B/…) | Expected Effect [unit, timeframe] | Guardrails & Ethics | Telemetry Event(s) | Owner | Provenance |
|---|---|---|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|---|---|---|

- Measurement Rules: primary metric per nudge (unit, frame), guardrails (min/max effect; fairness), exposure control.  
- Ethics: no dark patterns; truthful scarcity; easy opt-out; consent where relevant.

**WHY:** Chosen levers reduce friction & improve adoption with measurable, ethical effects.

---

## 4) Architecture, NFRs & Environments
- High-Level Architecture: components, data flows, contracts, external deps.  
- NFRs (targets): availability %, latency p95/p99 ms, throughput req/s, error budget h/period, RPO/RTO min, data retention days.  
- Environments: dev/test/stage/prod parity; data seeding; secrets mgmt.  
- Security & Privacy: authn/authz model, encryption, DPIA lead time days, logging PII policy.  
- Observability: logs/metrics/traces; dashboard names; alert thresholds & paging policy.

**SLO/SLA Table (REQUIRED)**

| Service/Flow | SLI | SLO Target | Error Budget (per period) | Alert Threshold | Pager Policy | Owner | Runbook |
|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|

**WHY:** NFR/SLO alignment prevents value erosion and instability post-launch.

---

## 5) Data, Telemetry & Measurement Spec
Map every KPI/criterion and nudge to events/metrics with schema & cadence.

| Signal | Type (event/metric) | Schema (fields & types) | Unit | Frame (cohort/geo/time) | Source System | Cadence | DQ Checks | Retention | Consumers | Provenance |
|---|---|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|---|---|

**Formulas:**  
- `ROI = (Net Benefits / Investment) × 100`  
- `NPV = Σ_t (CF_t / (1+WACC)^t)` (state rf, β, MRP)  
- `Payback = months until cumulative net CF ≥ 0`  
- `LTV = ARPU × Gross Margin × 1/Churn` (define cohort, window)

**Normalization:** **FX** [rate, date, source], **CPI** [base year, source], **PPP** (if used).

**WHY:** Ensures comparable, auditable measurement across phases and cohorts.

---

## 6) Experimentation & Evidence Plan
**Minimums:** ≥4 experiments total, ≥2 on behavioral interventions, ≥1 on pricing/offer framing (if relevant).

| ID | Hypothesis (direction + unit + timeframe) | Primary Metric | Guardrails | Design (A/B, diff-in-diff, DoE) | α | Power (1-β) | MDE | Sample Size (n) | Duration | Segments | Analysis Plan | Ethics/Consent | Provenance |
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|

- Integrity: SRM checks, novelty decay, seasonality handling, exposure caps.

**WHY:** De-risks assumptions and quantifies expected lift under realistic conditions.

---

## 7) Timeline, Milestones & Critical Path (RELATIVE WEEKS)
**Master Schedule (≥4 phases, buffers visible)**

| Phase | Start (Week) | End (Week) | Duration [weeks] | % Slack | Key Deliverables | Phase Gate Criteria (pass/fail) | Provenance |
|---|---|---|---:|---:|---|---|---|
|---|---|---|---:|---:|---|---|---|
|---|---|---|---:|---:|---|---|---|
|---|---|---|---:|---:|---|---|---|
|---|---|---|---:|---:|---|---|---|

**Intermediate Milestones (MANDATORY):** include leading indicators for ROI/turnover (e.g., “Retention +2 pp @Week 6”, “Offer-accept +5 pp @Week 4”).

**Critical Path & Slack**

| Task | Depends On | Slack [days] | Risk if Slips | Mitigation | Owner |
|---|---|---:|---|---|---|
|---|---|---:|---|---|---|
|---|---|---:|---|---|---|
|---|---|---:|---|---|---|
|---|---|---:|---|---|---|

**WHY:** Sequencing maximizes early value, protects dependencies, and keeps slack under control.

---

## 8) Resources, Capacity & Budget
- Staffing by Phase: roles, seniority, FTEs; onboarding/training weeks; BAU backfill plan.  
- Vendors/Partners: scope, SLAs, exit plan, data ownership, lock-in risk.

**Budget & Cash Flow (REQUIRED)**

| Category | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Total | Notes |
|---|---:|---:|---:|---:|---:|---|
|---|---:|---:|---:|---:|---:|---|
|---|---:|---:|---:|---:|---:|---|
|---|---:|---:|---:|---:|---:|---|
|---|---:|---:|---:|---:|---:|---|
|---|---:|---:|---:|---:|---:|---|

- CapEx vs OpEx, contingency %, payment milestones; capacity model (throughput units/period, utilization %).

**WHY:** Resourcing and spend profile support feasibility and time-to-impact while containing downside risk.

---

## 9) Responsibility & Accountability (RACI — ≥4 roles)
| Deliverable/Activity | Exec Sponsor | Business/HR Lead | Tech Lead | PMO | Legal/Compliance | Finance | Data/Analytics | Marketing/Comms | Ops/Support |
|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|---|---|

*(Use R/A/C/I; exactly one A per deliverable.)*

**WHY:** Clear accountabilities reduce decision latency and rework.

---

## 10) Phase Gate System (QA & Compliance — REQUIRED)
| Phase | Gate ID | Test | Criterion Link (ROI_12m / GDPR_Compliance / Time_to_Impact / Adoption_90d / Reliability_SLO) | Threshold | Owner | Status |
|---|---|---|---|---|---|---|
| Preparation | G1 | HR data validated | Reliability_SLO | ≥99.5% p(availability) | PMO | TBD |
| Core Implementation | G2 | Budget variance ≤ 5% | ROI_12m | ≤5% variance vs plan | Finance | TBD |
| Integration & Testing | G3 | DPIA/GDPR pass | GDPR_Compliance | Pass | Legal | TBD |
| Deployment | G4 | ROI tracking live & Adoption cohort instrumented | ROI_12m / Adoption_90d | Tracking live; cohort N≥X | Finance/HR | TBD |
|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|

**WHY:** Gates enforce objective pass/fail checks aligned with criteria lock; failures trigger mitigations before scale.

---

## 11) Risk, Compliance & Readiness
**Risk Register (implementation-phase)** — **≥10 distinct risks** across technical, behavioral, legal, operational, vendor.

| ID | Risk | Prob (0–1 or L–H) | Impact (€/unit or L–H) | Horizon | Early Signal | Mitigation (HOW) | Owner | Provenance |
|---|---|---:|---|---|---|---|---|---|
|---|---|---:|---|---|---|---|---|---|
|---|---|---:|---|---|---|---|---|---|
|---|---|---:|---|---|---|---|---|---|

**Compliance Matrix** — DPIA/PIA, security, accessibility, sector rules.

| Requirement | Applicability | Lead Time [days] | Evidence Needed | Gate (Pass/Fail) | Owner |
|---|---|---:|---|---|---|---|
|---|---|---:|---|---|---|---|
|---|---|---:|---|---|---|---|
|---|---|---:|---|---|---|---|
|---|---|---:|---|---|---|---|

**Readiness Checklist (Yes/No with comments — REQUIRED)**

| Variable | OK? | Comment |
|---|---|---|
| Budget ≤ approved limit | [ ] |  |
| Staff assigned & onboarding plan | [ ] |  |
| Risk register updated (≤7 days) | [ ] |  |
| KPI dashboard linked to telemetry | [ ] |  |

**WHY:** Focuses leaders on the few constraints that govern Go/No-Go and safe rollout.

---

## 12) Rollout, Cut-over & Reversibility
- Rollout: pilots→cohorts/regions; traffic ramps %; eligibility & exclusion rules; customer comms (plain language).  
- Feature Flags: ownership, flip protocol, audit trail, fallback behavior.  
- Cut-over Runbook: T-minus schedule, validation checks, owner per step, go/no-go criteria.  
- Rollback Playbooks: triggers, steps, data reconciliation, external comms.

**WHY:** Reversibility and staged exposure protect users and business while learning.

---

## 13) Post-Launch Monitoring & Adaptive Control
- Dashboards: KPIs/guardrails/SLOs; alert thresholds; paging policy; on-call rota.  
- Ops: MTTA/MTTR targets; incident mgmt; RCA template & SLA.  
- Learning Loop: weekly cadence; decision log; promote/hold/kill rules (pilot→scale).  
- Benefits Tracking: baseline vs actual; ROI calendar; variance drivers.

**WHY:** Ensures value realization and continuous risk control.

---

## 14) Handoff to Simulate & Evaluate (MANDATORY — Must be fully populated)
**Minimums:** ≥3 **Scenarios** (SCN-*), ≥12 **Parameters** (PAR-*), ≥4 **Correlations** (CORR-*), ≥4 **Experiments** (EXP-*), ≥4 **Gate** lines (GATE-*), ≥3 **Normalization** rows (NORM-*), complete **Traceability Map** (MAP-*).

### 14.1 Scenarios (SCN-*)
| ID | Scenario Name | Family (strategic/tactical/reduced) | Description | Variables Changed | Fixed Parameters | Exposure (%) | Cohort/Segment | Rollout Shape (linear/logistic/step) | Observation Window | Provenance |
|---|---|---|---|---|---|---:|---|---|---|---|
| SCN-1 |  |  |  |  |  |  |  |  |  |  |
| SCN-2 |  |  |  |  |  |  |  |  |  |  |
| SCN-3 |  |  |  |  |  |  |  |  |  |  |

### 14.2 Parameters (PAR-*)
| ID | Variable | Unit | Base | Range/Distribution (min,mode,max or μ,σ) | Correlations (IDs) | Owner | As-Of Date | Rationale/Formula | Provenance |
|---|---|---|---|---|---|---|---|---|---|
| PAR-1 |  |  |  |  |  |  |  |  |  |
| PAR-2 |  |  |  |  |  |  |  |  |  |
| PAR-3 |  |  |  |  |  |  |  |  |  |
| PAR-4 |  |  |  |  |  |  |  |  |  |
| PAR-5 |  |  |  |  |  |  |  |  |  |
| PAR-6 |  |  |  |  |  |  |  |  |  |
| PAR-7 |  |  |  |  |  |  |  |  |  |
| PAR-8 |  |  |  |  |  |  |  |  |  |
| PAR-9 |  |  |  |  |  |  |  |  |  |
| PAR-10 |  |  |  |  |  |  |  |  |  |
| PAR-11 |  |  |  |  |  |  |  |  |  |
| PAR-12 |  |  |  |  |  |  |  |  |  |

### 14.3 Correlations (CORR-*)
| Var1 (PAR-#) | Var2 (PAR-#) | Coefficient (ρ) | Segment | Method (historical/assumed/benchmark) | Provenance |
|---|---|---:|---|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

### 14.4 Experiments (EXP-*)
| ID | Scenario(s) | Hypothesis (direction + unit + timeframe) | Primary Metric | Guardrails (min/max) | Design | α | Power | MDE | Sample Size (n) | Duration | Segments | Analysis Plan | Ethics/Consent | Provenance |
|---|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|
| EXP-1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| EXP-2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| EXP-3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| EXP-4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

### 14.5 Gate Thresholds (GATE-*)
| Criterion | Gate ID | Threshold | Evidence Required | Result Type (Pass/Fail/Conditional) | Owner |
|---|---|---|---|---|---|
| ROI_12m |  |  |  |  |  |
| GDPR_Compliance |  |  |  |  |  |
| Time_to_Impact |  |  |  |  |  |
| Adoption_90d |  |  |  |  |  |
| Reliability_SLO |  |  |  |  |  |

### 14.6 Normalization Rules (NORM-*)
| Currency | FX Rate | CPI | PPP | Base Year | Source | Access Date |
|---|---:|---:|---:|---:|---|---|
| EUR |  |  |  |  |  |  |
| USD |  |  |  |  |  |  |
| GBP |  |  |  |  |  |  |

### 14.7 Traceability Map (MAP-*)
| Plan Element (WBS/Gate/Nudge) | Parameter (PAR-#) | Scenario (SCN-#) | Criterion/KPI | Data Source | Owner |
|---|---|---|---|---|---|
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |
|  |  |  |  |  |  |

**WHY:** Provides Simulate with concrete worlds, parameters, and relationships; gives Evaluate a consistent schema to interpret and compare outcomes.

---

## 15) Data Gaps & Collection Plan (MANDATORY; ≥8 items if gaps exist)
| Missing Data (WHAT) | Why Needed | Method (instrument/test/query) | Owner | ETA | Acceptance Criteria | Expected Source |
|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|
|---|---|---|---|---|---|---|

**WHY:** Converts uncertainty into time-boxed evidence generation with clear ownership.

---

## Appendices
- A. Formulas & Parameters: ROI/NPV/IRR/Payback; elasticity notes; KPI definitions.  
- B. Normalization Tables: FX/CPI/PPP (rate & date & source).  
- C. Source Register: title; publisher/author; date (YYYY-MM-DD); URL or Doc-ID/§; source type; recency note.  
- D. Architecture Diagram & Data Schemas.  
- E. Experiment Design Details & Analysis Code Notes (if any).

---

## Final Quality Gate (ALL must be YES)
- four_phases_present_and_labeled_preparation_core_integration_testing_deployment == true  
- plan_uses_relative_weeks_and_reports_percent_slack < 10 == true  
- wbs_complete_with_acceptance_criteria_and_critical_path == true  
- behavioral_plan_has_8_to_12_interventions_with_guardrails_and_telemetry == true  
- telemetry_spec_maps_all_kpis_nudges_and_criteria_with_units_and_timeframes == true  
- ≥4_experiments_defined_with_alpha_power_mde_sample_and_guardrails == true  
- master_schedule_and_critical_path_with_buffers_present == true  
- raci_with_min_four_roles_and_single_accountable_per_deliverable == true  
- budget_cashflow_with_contingency_and_capacity_modeling_present == true  
- gate_system_defined_and_linked_to_locked_criteria == true  
- readiness_checklist_present_budget_staff_risk_dashboard == true  
- risk_register_≥10_items_compliance_matrix_and_readiness_checklists == true  
- rollout_cutover_and_rollback_playbooks_defined == true  
- benefits_tracking_and_adaptive_control_defined == true  
- simulate_handoff_blocks_present (SCN, PAR, CORR, EXP, GATE, NORM, MAP) == true  
- data_gaps_collection_plan_present == true  
- provenance_cues_present_for_material_claims == true  
- why_paragraph_after_each_table_or_cluster == true
"""

        return Task(
            description = description,
            expected_output = expected_output,
            markdown=True,
            agent = agent,
            output_file="06_implementation_report.md"
        )
