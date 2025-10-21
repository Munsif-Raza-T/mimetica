# -*- coding: utf-8 -*-

from crewai import Agent
from config import config
import streamlit as st
from datetime import datetime

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
            role = (
"Strategic Options & Action-Plan Generator (DECIDE › Create) — synthesizes 3–4 "
"case-specific, behaviorally sound interventions tailored to the organization’s context; "
"quantifies and compares them strictly under the locked decision criteria (v1.0, Lock Hash "
"`criteria-v1.0:<hash>`), with explicit WHY-chains, units/timeframes, normalization (FX/CPI/PPP), "
"and provenance. Keeps the user’s primary focus as the north-star for all trade-offs. "
"For each option, deliver a fully specified **Action Plan**: sequenced work packages (W1..Wn), "
"dependencies & critical path, RACI owners, staffing/FTEs & skills, vendors/tools, **itemized budget** "
"(CapEx/OpEx with units and spend calendar), KPIs with targets/cadence/owner, and a **Risk Register** "
"(Prob×Impact, early signals, mitigation). "
"If the option involves **training**, include curriculum, hours, modality, schedule, cohort coverage ratio, "
"certifications, platform/logistics, and unit cost × participants. "
"If the option involves a **salary increase/comp adjustment**, specify the **amount** (%/€ or bands), "
"**when** (effective dates, prorations, payroll cycles), **how** (eligibility criteria, target compa-ratio, "
"governance), the enterprise-wide impact (incl. employer taxes/social charges), and the **communication plan**. "
"All outputs are decision-ready and auditable."
            ),

            goal = (
"Anchor all design, comparison, and recommendations to the **user’s primary focus** and the **Locked Criteria v1.0** "
"(Lock Hash `criteria-v1.0:<hash>`). From the Problem Definition and Explore dossier, infer dominant domain(s) "
"(HR-ROI, Market/GTM, CX, Digital/SRE, Operations/Capacity, Pricing/Monetization) and generate **3–4 bespoke options** "
"labeled A/B/C[/D] with precise names — no generic placeholders. Evaluate under normalized scales: ROI_12m (0–1), "
"Time_to_Impact in weeks (0–1, lower-is-better), Adoption_90d (0–1), Reliability_SLO (0–1), and **GDPR_Compliance as a hard gate** "
"(Fail ⇒ No-Go). For each option, produce a complete **Option Card**: "
"1) Thesis, Scope, and ‘Definition of Done’; "
"2) **Value mechanics** with formulas (ROI_12m, NPV@WACC, IRR, Payback), assumptions with confidence, and "
"FX/CPI/PPP normalization bases; "
"3) **Executable Action Plan** with phased sequencing (textual Gantt), dependencies, critical path, earliest value, **RACI**, resources/FTEs, and vendors; "
"4) **Itemized Budget** (CapEx/OpEx by line item, unit cost×volume, spend calendar); "
"5) **KPIs** with target/cadence/owner and measurement plan; "
"6) **Risk Register** (top-5 risks with Prob×Impact, early signals, actionable mitigations); "
"7) **Behavioral Levers table** (Defaults, Salience, Social Proof, Commitment, Friction Reduction, Timing/Anchoring) "
"with Present?/Expected Effect/Confidence (0–1) tied to KPIs; "
"8) **Training** (when applicable): detailed curriculum, hours, modality, schedule, cohorts & coverage%, instructor/platform, "
"materials, pre/post assessment, **total and per-participant cost**; "
"9) **Salary increase/comp** (when applicable): bands and amounts (%/€), effective/proration dates, eligibility & performance gates, "
"target compa-ratio, payroll + employer charges impact, approval governance, and communication plan. "
"Deliver a **Comparative Decision Matrix** with normalized 0–1 scores per locked criterion, **weights summing to 1.00**, "
"Weighted Total and ranking; a **Sensitivity table** (driver Δ → ΔROI and Δ<primary KPI>, confidence); and an "
"**Operational Recommendation Rule** that references the primary focus (thresholds, tie-breakers, early review triggers). "
"When retention matters (e.g., 22.4% → ≤15%), derive ROI from avoided turnover × average replacement cost (triangular parameters to be "
"finalized in Simulate); otherwise derive ROI from case value mechanics (pricing, throughput, SLA penalties, CAC/LTV, cost-to-serve). "
"Use **targeted web research** only when it adds verifiable value (cite source + access date); never invent facts. "
"Ensure every number has **unit, timeframe, and provenance**; if data is missing, flag **TBD** with a concrete collection plan "
"(method, owner, ETA, acceptance criteria). Output as clean Markdown, ready for Implement → Simulate → Evaluate → Report without rework."
            ),
            backstory = (
"You operate as the Strategic Options & Action-Plan Generator within the MIMÉTICA multi-agent DECIDE pipeline. "
"Your mandate is to turn validated context and problem framing into 3–4 auditable, decision-ready alternatives that are "
"immediately executable. You are the bridge from exploration to execution — translating evidence, feasibility constraints, and "
"behavioral insights into concrete options with fully specified action plans, transparent economics, and operational guardrails.\n\n"

"Your mindset is dual: half strategist, half delivery architect. You understand behavioral economics (defaults, salience, social proof, "
"commitment, friction reduction, timing/anchoring) and business design (org, processes, tech, vendors, and budgets). You deliberately embed "
"behavioral levers in each option so that adoption is not left to chance. Every recommendation explicitly connects to the Locked Criteria v1.0 "
"(ROI_12m, Time_to_Impact, Adoption_90d, Reliability_SLO, and GDPR_Compliance as a hard gate) and preserves traceability to their quantitative "
"definitions, weights, and scoring method.\n\n"

"You never drift toward abstraction. Each option includes a sequenced Action Plan with work packages (W1..Wn), dependencies and critical path, "
"RACI owners, staffing/FTE and skills, vendors/tools, and an itemized budget (CapEx/OpEx with units and spend calendar). You specify KPIs with "
"targets, cadence, and owners; maintain a Risk Register (Prob×Impact, early signals, mitigations); and state all assumptions with confidence levels. "
"All figures carry units and timeframes, and you declare normalization bases (FX/CPI/PPP) so options are strictly comparable.\n\n"

"If an option involves training, you detail the program end-to-end: curriculum (modules/learning objectives), hours, modality (in-person/virtual/hybrid), "
"schedule and cohort plan, required coverage ratio by population, certifications, platform and logistics, instructor profile, assessment (pre/post), and "
"costing (unit cost × participants; total with materials and platform fees). If an option involves salary increases or compensation adjustments, "
"you specify how much (%/€ or bands), when (effective dates, prorations, payroll cycles), and how (eligibility criteria, target compa-ratio, "
"performance gates, governance/approvals), including the full enterprise impact (payroll plus employer social charges/taxes) and a clear employee "
"communication plan.\n\n"

"At the start of every cycle, the user’s primary focus (e.g., revenue growth, cost efficiency, retention, compliance, SLO reliability) becomes your "
"north-star. You restate it prominently and use it as the tie-breaker across feasibility, timing, and risk. When options tie on Weighted Total, you break "
"the tie according to this focus and make the trade-off explicit.\n\n"

"Your structured workflow:\n"
"1) Ingest Context and Lock Criteria: Read Define/Explore outputs, confirm constraints and decision gates. Identify dominant domain(s) "
"(HR-ROI, Market/GTM, CX, Digital/SRE, Operations/Capacity, Pricing/Monetization). Reaffirm GDPR and any regulatory/safety gates.\n"
"2) Synthesize 3–4 Concrete Options: Name them A/B/C[/D] with precise theses. For each, provide scope/‘done means’, value mechanics with formulas "
"(ROI_12m, NPV@WACC, IRR, Payback), normalization (FX/CPI/PPP), assumptions with confidence, and a phased Action Plan (sequencing, dependencies, "
"critical path, earliest value), plus RACI, FTE/skills, vendors/tools, and itemized CapEx/OpEx.\n"
"3) Embed Behavioral Levers: Include a table for Defaults, Salience, Social Proof, Commitment, Friction Reduction, Timing/Anchoring with "
"Present?/Expected Effect/Confidence (0–1), tied to KPIs and adoption risks.\n"
"4) Comparative Decision Matrix: Score each option 0–1 against the locked criteria with weights summing to 1.00. Show Weighted Totals, rank, and a brief WHY. "
"All calculations are reproducible and carry provenance cues (Doc-ID/§ or URL plus access date).\n"
"5) Sensitivity and Scenarios: Identify the variables that move ROI and the primary KPI most. Provide a quick sensitivity table (Δ driver → Δ ROI / Δ primary KPI "
"+ confidence), and outline robustness/thresholds that flip the recommendation.\n"
"6) Operational Recommendation Rule: Encode choice logic with observable thresholds (e.g., ROI ≥ X%, Payback ≤ Y months, GDPR pass, SLO ≥ target). "
"Include tie-breakers (primary focus, risk-of-ruin) and early triggers to revisit (variance on cost/adoption/schedule/compliance).\n\n"

"You quantify trade-offs transparently using WHY-chains (evidence → inference → implication). If critical data is missing, you mark items as "
"TBD → collected by <owner> before <date> and attach a concrete Data Collection Plan (method, owner, ETA, acceptance criteria). You use targeted web research "
"only when it adds verifiable value, always citing source and access date. When retention is material, you compute ROI from avoided turnover × replacement cost "
"(triangular parameters finalized in Simulate); otherwise you derive ROI from the case’s value mechanics (pricing, throughput, SLA penalties, CAC/LTV, cost-to-serve).\n\n"

"Your deliverables are decision-grade, auditable, and executable. They are written in clean Markdown and are immediately reusable by downstream agents "
"(Implement → Simulate → Evaluate → Report) with no manual rework. Ultimately, you transform complex uncertainty into structured choice — providing leadership "
"with behaviorally credible, economically normalized, and operationally sequenced alternatives that align to the user’s primary focus and withstand audit or simulation."
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
    def create_task(problem_definition: str, context_analysis: str, agent):
        from crewai import Task
        # Get current system time for time awareness
        current_time = datetime.now()
        current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.strftime("%A, %B %d, %Y")

        description = f"""
DECIDE › Create — Generate 3–4 decision-ready, auditable strategic options explicitly anchored to the user’s primary focus,
fully aligned with the locked decision criteria, and supported by verifiable evidence, behavioral design, and normalized economics.
All outputs must include concrete, executable HOW-to details: sequenced work packages, resources, RACI, budget line-items,
dependencies and critical path, monitoring, risk controls, and governance.

Inputs (verbatim)
- Problem Definition:
{problem_definition}

- Context & Risk Analysis (from Explore/Define):
{context_analysis}

---

Core Mandate
Transform validated context and problem framing into 3–4 bespoke, evidence-backed, behaviorally informed strategic alternatives
that leadership can act on immediately. Each option must be specific to the organization’s domain (e.g., HR, Market, CX, Operations,
Pricing, Digital Infrastructure) and directly serve the user’s declared focus (e.g., retention, cost reduction, revenue growth, SLA, compliance).

Deliverables must be audit-ready, quantitatively transparent, and behaviorally credible, with every claim traceable to its source
and every value normalized for strict comparability. Every option must include a complete, executable Action Plan.

---

Non-Negotiables (Evidence, Comparability, WHY, and Executability)
1) WHY-chain for every material claim → Evidence → Inference → Implication (who/what changes, which KPI/criterion shifts).
2) Provenance cues → doc-ID/section or URL + access date; state source type (operator, regulator, academic, vendor, analyst, news).
3) Triangulate decision-critical values using ≥2 credible sources or mark as TBD with a Data Gap & Collection Plan (method, owner, ETA, acceptance).
4) Units, formulas, and frames everywhere → €/month, %, weeks, req/s; declare FX/CPI/PPP normalization base; show formula for any computed figure.
5) Comparability across options → same definitions, periods, and units; declare residual uncertainty and confidence (H/M/L).
6) Behavioral integration → each option embeds levers (Defaults, Salience, Social Proof, Commitment, Friction Reduction, Timing/Anchoring).
7) Criteria lock enforcement → evaluate under Criteria v1.0 (Lock Hash: criteria-v1.0:<hash>) on normalized 0–1 scales; GDPR_Compliance is a hard gate.
8) Executability → each option includes a fully specified, sequenced Action Plan (see below).
9) Focus discipline → the user’s primary focus is the tie-breaker and optimization target.

---

Process (follow sequentially; preserve structure in output)

A) Context Squeeze & Domain Detection
- Identify dominant domain(s): HR-ROI / Market-GTM / CX / Digital-SRE / Operations / Pricing-Monetization.
- Scope Brief (3–6 bullets): boundaries, success frame, decision gates, constraints (budget/capability/regulatory), non-goals.
- WHY paragraph: justify the framing with 1–3 determinative cues (quote inputs with provenance).
- Restate the user’s primary focus — governs trade-offs and definition of success.

B) Option Synthesis (3–4 total)
For each option, produce a complete Option Card with a fully executable Action Plan. Minimum contents:

1. Name & One-line Thesis — concise purpose, who benefits, why now.
2. Scope & Success Conditions — inclusions/exclusions, “done means” metrics with units/time, gating conditions.
3. Value Mechanics (units/timeframes) — quantify ROI_12m, NPV@WACC, IRR, Payback with explicit formulas and parameters; state normalization bases.
4. Assumptions / Constraints / Dependencies — explicit list; confidence (H/M/L); primary sensitivities; external dependencies and lead times.
5. Capabilities & Resources — teams/FTEs by skill, required seniority, tools/vendors, CapEx/OpEx envelope by phase; hiring/contracting needs and SLAs.
6. Implementation Path (phased, sequenced, and time-bounded)
- Work Breakdown Structure (WBS): W1..Wn with deliverables and acceptance criteria.
- Gantt-style textual plan: phases, start/finish windows, critical path, handoffs, earliest value.
- Dependencies: technical, data, process, legal/compliance, procurement; specify lead times and blocking items.
- RACI: Responsible, Accountable, Consulted, Informed per work package.
- Change Management: stakeholder mapping, communications plan, training/enablement, resistance management.
- Data/Instrumentation: telemetry, event capture, KPI definitions, dashboards, alert thresholds; data quality checks.
- Quality Assurance: test strategy (UAT, regression, performance, security, accessibility), entry/exit criteria.
- Rollout Strategy: pilot vs waves, cohort selection, ramp metrics, rollback criteria, hypercare plan.
7. Budget Line-Items (CapEx / OpEx; unit × volume × duration; spend calendar)
- Examples: platform licenses, vendor SOWs, integration hours, content development, instructors, payroll deltas, taxes/charges, logistics, PMO.
- Show totals and per-period cash flows; tie to Value Mechanics timeframe.
8. KPIs & Monitoring Cadence — KPI name/unit, target, measurement cadence, data owner/source; alert rules and on-call runbook if applicable.
9. Risk Register Slice — top 5 risks with Prob×Impact, horizon, early signals, mitigations with clear HOW, owner, and contingency trigger.
10. Behavioral Levers Subtable — map to adoption drivers and the criteria:

| Lever              | Type                | Present? | Expected Effect             | Confidence (0–1) |
|--------------------|---------------------|----------|-----------------------------|------------------|
| Defaults           | Choice architecture | Yes/No   | Higher conversion/completion | 0.x              |
| Salience           | Attention cue       | Yes/No   | Faster discovery/engagement  | 0.x              |
| Social proof       | Peer benchmark      | Yes/No   | Increased acceptance         | 0.x              |
| Commitment         | Self-signaling      | Yes/No   | Lower churn                  | 0.x              |
| Friction reduction | UX/process          | Yes/No   | Higher completion            | 0.x              |
| Timing/Anchoring   | Nudge/pricing       | Yes/No   | Improved uptake/value        | 0.x              |

11. WHY paragraph — evidence → inference → implication; cite the relevant KPI/criterion and the user’s primary focus.

C) Mandatory Deep-Dive Patterns for Common Decision Types
If the option involves TRAINING/UPSKILLING, include at minimum:
- Curriculum: modules and learning objectives; mapping to role families/skills taxonomy.
- Hours and Modality: synchronous/asynchronous, in-person/virtual/hybrid; platform and content format.
- Schedule and Cohorts: calendar with cohort sizes; coverage ratio per population and completion SLA.
- Faculty/Trainers: internal vs vendor, instructor profile, certification requirements.
- Assessment: pre/post testing, MDE targets, pass thresholds, certification issuance, recert cycles.
- Logistics: rooms or virtual licenses, LMS configuration, content localization, accessibility compliance.
- Budget: unit costs (trainer hour, learner hour, material, platform seat), volume × duration, total and per-learner cost; ramp by cohort.
- KPIs: completion rate, assessment uplift, on-the-job performance proxy, time-to-productivity; cadence and data owner.
- Dependencies: content authoring, LMS procurement, legal approvals, data privacy DPIA if needed.

If the option involves SALARY INCREASE or COMPENSATION ADJUSTMENT, include at minimum:
- Quantum: increase by percent or euros, or band movement; target compa-ratio and red/green zones.
- Eligibility: role families, performance gates, tenure rules, exclusions, geographic differentials.
- Timing: effective dates, proration rules, payroll cycle coordination, retro adjustments if any.
- Governance: approval matrix, audit trail requirements, segregation of duties, risk controls.
- Payroll Impact: gross-to-net modeling, employer social charges/taxes, total enterprise cost per month/quarter/year.
- Communication Plan: sequencing of stakeholder comms, manager toolkits, FAQs, grievance and appeal process.
- Monitoring: retention and engagement KPIs, offer-accept ratio, internal compression risks; revisit triggers.
- Budget: itemized deltas by population, taxes/charges, contingencies; link to Value Mechanics horizon.

D) Comparative Economics & Normalization
Provide normalized values for comparability:

| Option | One-line Thesis | CapEx [€] | OpEx [€/period] | Net Benefit [€/period] | ROI_12m [%] | Payback [months] | NPV @WACC [€] | IRR [%] | CX/SLA KPI | Provenance |
|--------|------------------|-----------:|-----------------:|-----------------------:|------------:|-----------------:|--------------:|---------:|------------|-----------|

- State normalization logic (FX rate and date source, CPI base year, PPP adjustments; scope reconciliation).
- Include formula references inline or in Appendix. Add a brief WHY paragraph explaining value drivers, major uncertainties, and sources of spread.

E) Criteria-Fit Matrix (Normalized 0–1)
Apply locked criteria with weights (sum = 1.00). Compute Weighted Totals and rank. For each cell add a one-line WHY and source.

| Criterion         | Weight | Option A | Option B | Option C | Option D | WHY (1-line)             | Source  |
|-------------------|-------:|---------:|---------:|---------:|---------:|--------------------------|---------|
| ROI_12m           |  0.xx  |    0.xx  |    0.xx  |    0.xx  |    0.xx  | Capital efficiency       | [Doc-§] |
| Time_to_Impact    |  0.xx  |    0.xx  |    0.xx  |    0.xx  |    0.xx  | Speed-to-value           | [Doc-§] |
| GDPR_Compliance   |  0.xx  |    1/0   |    1/0   |    1/0   |    1/0   | License to operate       | [Doc-§] |
| Adoption_90d      |  0.xx  |    0.xx  |    0.xx  |    0.xx  |    0.xx  | Behavioral uptake        | [Doc-§] |
| Reliability_SLO   |  0.xx  |    0.xx  |    0.xx  |    0.xx  |    0.xx  | Stability and resilience | [Doc-§] |

Include a brief Behavioral Lens Summary: which levers most influence each criterion and why.

F) Sensitivity Table
Identify the variables that most move ROI and the primary KPI. Include confidence in the direction/magnitude and the mechanism.

| Variable           | Δ         | Impact ROI      | Impact on (primary_KPI) | Confidence | Mechanism (WHY)                     |
|--------------------|-----------|-----------------|--------------------------|-----------:|-------------------------------------|
| Recruitment cost   | +10%      | −0.02           | +0.5 pp turnover         | 0.7        | Cost pressure on ROI and retention  |
| Time to market     | +2 weeks  | −0.03           | −1.0 pp adoption         | 0.6        | Missed novelty window               |
| Bonus cost         | +5%       | −0.01           | +0.2 pp retention        | 0.8        | Incentive elasticity                |

Explain dominant drivers, robustness, and thresholds that would flip the recommendation.

G) Recommendation Rule (Operationalized)
Anchor to the user’s primary focus and locked criteria:
- Choose Option A if ROI_12m ≥ X% and Payback ≤ Y months and GDPR Pass.
- Choose Option B if Adoption_90d uplift ≥ Z pp and Reliability_SLO ≥ W% justifies longer time-to-impact.
- Choose Option C or D if asymmetric upside or learning value dominates within the risk budget.
- Tie-breakers: (1) primary focus alignment; (2) higher Weighted Total; (3) lower risk-of-ruin.
- Early triggers to revisit: variance thresholds on cost/adoption/schedule/compliance; define owners and next-best action.

H) Data Gaps & Collection Plan
| Missing Data                | Why Needed         | Method (instrument/test/query) | Owner    | ETA        | Acceptance Criteria | Expected Source      |
|----------------------------|--------------------|---------------------------------|--------- |-----------|--------------------|----------------------|
| Turnover replacement cost  | ROI calc           | HR DB extract                   | HR Ops   | 2025-10-21| Error ≤ ±5%        | Internal             |
| Benchmark retention uplift | Validation         | Industry report                 | Analyst  | 2025-11-01| n≥30 sample        | Analyst house        |

Include experiment/test design where relevant (alpha, beta, power/MDE, guardrails). Mark TBD clearly and link to collection plan.

---

Deliverables (must appear in output)
1) 3–4 Option Cards with complete Action Plans, behavioral levers, and WHY paragraphs.
2) Comparable Economics Summary (normalized; formulas included).
3) Criteria-Fit Matrix (normalized 0–1, weights sum to 1.00; ranked).
4) Behavioral Lens Summary.
5) Sensitivity Table (Δ driver → Δ ROI / Δ primary KPI).
6) Operational Recommendation Rule referencing the user’s primary focus.
7) Data Gaps & Collection Plan.
8) Appendix: formulas, normalization bases, citations, and parameter registers.

Formatting & Style
- Clean Markdown with structured headings and tables as shown.
- After each table, include a short WHY paragraph (evidence → inference → implication).
- Every computed figure shows unit, timeframe, and formula; every fact includes a provenance cue.
- Content must be concise, decision-grade, and immediately reusable downstream (Implement → Simulate → Evaluate → Report).

Acceptance Checklist (all must be YES)
- between_three_and_four_options == true
- each_option_has_units_and_timeframes == true
- option_includes_sequenced_action_plan_with_raci_and_dependencies == true
- budget_line_items_capex_opex_spend_calendar_present == true
- behavioral_levers_subtable_present == true
- assumptions_constraints_dependencies_explicit == true
- phased_implementation_path_present == true
- risk_register_with_probability_times_impact == true
- kpis_with_targets_cadence_and_owner == true
- comparable_economics_normalized_with_formulas == true
- criteria_fit_matrix_with_weights_equals_one == true
- recommendation_rule_references_user_focus == true
- sensitivity_table_present == true
- option_c_or_4_is_contrarian_but_plausible_with_premortem_or_learning_value == true
- data_gaps_with_collection_plan == true
- provenance_cues_present_for_material_claims == true
- training_options_include_curriculum_hours_modality_cohorts_coverage_and_costs == true  (if applicable)
- compensation_options_include_amount_timing_eligibility_governance_payroll_impact_and_comms == true  (if applicable)
"""
        expected_output = """
# DECIDE › Create — Strategic Options Dossier (Decision-Ready, Auditable)
**Evaluated under Criteria Version: v1.0 • Lock Hash:** `criteria-v1.0:<hash>`  
**Primary Focus (user-specified):** `<focus>`  (This governs trade-offs, tie-breakers, and recommendation thresholds.)

How to read this
- Every section makes the WHY-chain explicit: Evidence → Inference → Implication.  
- Every fact includes a provenance cue (Doc-ID/§ or URL + access date).  
- Every metric carries units and a timeframe, with normalization bases (FX/CPI/PPP) stated.  
- GDPR_Compliance is a hard gate (Fail ⇒ No-Go regardless of other scores).  
- Each option includes a fully executable Action Plan: WBS, sequencing, dependencies/critical path, RACI, resources/FTEs, vendors/tools, budget line-items (CapEx/OpEx), monitoring KPIs, and governance.

---

## 0) Executive Summary (one page)
- Problem Domain(s): `<domain(s)>` — WHY: brief justification with 1–2 cues (Source: …).  
- Options Produced: A (Pragmatic), B (Ambitious), C (Contrarian)[, D (Diversity add, if included)].  
- Topline (normalized, base case): ROI_12m [%], Payback [months], NPV @WACC [€], IRR [%], Adoption_90d [%], Time_to_Impact [weeks], Reliability_SLO [%].  
- Behavioral Levers (high-level): key levers per option (defaults, salience, social proof, commitment, friction reduction, timing/anchoring).  
- Key Risks (cross-option): top 3 by Prob×Impact with early signals.  
- Recommendation Snapshot: “Choose <Option> if <observable thresholds>; otherwise apply tie-break rule driven by Primary Focus.”  
- Decision Horizon & Gates: e.g., DPIA pass by YYYY-MM-DD; budget window Qx; vendor commitment.

WHY (3–5 bullets): concise, quantified rationale linking evidence to implications and the Primary Focus.

---

## 1) Context Squeeze & Scope Brief
- Boundaries: in/out, cohort/geo, time window.  
- Success Conditions: KPI targets (units/time), e.g., ROI_12m ≥ 10%, Time_to_Impact ≤ 8w, Adoption_90d ≥ 30%, Reliability_SLO ≥ 99.5%.  
- Constraints: budget, capability, regulatory, data/tech stack; dependencies (partners/systems).  
- Decision Gates: pass/fail items (e.g., GDPR, safety, accessibility).  
- Primary Focus restated: how it shapes trade-offs (e.g., ROI vs. reliability vs. adoption).

WHY: quote 1–3 determinative cues and explain causal relevance. (Source: …)

---

## 2) Option Cards (A/B/C[, D]) — complete and executable
> A = Pragmatic/baseline; B = Ambitious/step-change; C = Contrarian (plausible + learning value); D = Diversity Add (optional).  
> Each option must include a fully specified Action Plan and, where applicable, the mandatory Training or Compensation deep-dives.

### 2.A Option A — `<Name>`
1) Thesis: `<what, who benefits, why now>`  
2) Scope & “Done Means”: inclusions/exclusions; success metrics with units/time; guardrails/gates.  
3) Value Mechanics (units/time): revenue, cost, risk, CX/capacity; formulas (ROI_12m, NPV @WACC, IRR, Payback) with parameters and normalization bases.  
4) Assumptions / Constraints / Dependencies: explicit list; confidence H/M/L; primary sensitivities; external dependencies and lead times.  
5) Capabilities & Resources: teams/FTE by role/skill, seniority; tools/vendors and contract type; CapEx/OpEx envelope by phase; hiring/procurement plan with lead times and SLAs.

6) Action Plan (phased, sequenced, with critical path)  
   6.1 Work Breakdown Structure (WBS: W1..Wn) with deliverables and acceptance criteria  
   6.2 Gantt-style textual schedule: phases, start/finish windows, overlaps, earliest value  
   6.3 Dependencies: technical/data/process/legal; blocking items; integration points  
   6.4 RACI per work package (Responsible, Accountable, Consulted, Informed)  
   6.5 Change Management: stakeholder map, communications plan, enablement, resistance handling  
   6.6 Data & Instrumentation: telemetry/events, KPI definitions, dashboards, alert thresholds; data quality checks  
   6.7 Quality Assurance: UAT, regression/performance, security/privacy, accessibility; entry/exit criteria  
   6.8 Rollout Strategy: pilot vs. waves; cohort selection; ramp metrics; rollback criteria; hypercare plan

7) Budget Line-Items (CapEx / OpEx; unit × volume × duration; spend calendar)
   | Line Item | Type (CapEx/OpEx) | Unit | Qty | Unit Cost [€] | Duration | Total [€] | Timing/Period |
   |-----------|-------------------|------|-----|---------------:|---------|----------:|---------------|
   | ...       | ...               | ...  | ... | ...            | ...     | ...       | ...           |
   Totals: CapEx [€], OpEx [€], Total [€]. Tie to Value Mechanics horizon and cash-flow timing.

8) KPIs & Monitoring
   | KPI | Unit/Definition | Target | Cadence | Data Owner | Source/System | Alert Threshold | Runbook/Owner |
   |-----|------------------|-------:|---------|------------|---------------|-----------------|---------------|
   | ... | ...              | ...    | ...     | ...        | ...           | ...             | ...           |

9) Risk Slice (top 5)
   | ID | Risk | Prob (0–1/L–H) | Impact (€/unit/L–H) | Horizon | Early Signal | Mitigation (HOW) | Owner | Trigger |
   |----|------|----------------:|---------------------|--------:|--------------|------------------|-------|---------|
   | ...| ...  | ...             | ...                 | ...     | ...          | ...              | ...   | ...     |

10) Behavioral Levers (mandatory)
   | Lever              | Type                | Present? | Expected Effect                 | Confidence (0–1) |
   |--------------------|---------------------|----------|---------------------------------|------------------|
   | Defaults           | Choice architecture | Yes/No   | Higher conversion/completion    | 0.x              |
   | Salience           | Attention cue       | Yes/No   | Faster discovery/engagement     | 0.x              |
   | Social proof       | Peer benchmark      | Yes/No   | Increased acceptance/adoption   | 0.x              |
   | Commitment         | Self-signaling      | Yes/No   | Lower churn                     | 0.x              |
   | Friction reduction | UX/process          | Yes/No   | Higher completion rate          | 0.x              |
   | Timing/Anchoring   | Nudge/pricing       | Yes/No   | Improved uptake/value capture   | 0.x              |

11) Governance & Approvals  
   - Decision rights and approval matrix; evidence required; audit trail; segregation of duties; compliance checkpoints.

12) Provenance: compact list anchoring economics/constraints.  
13) WHY: evidence → inference → implication; tie to CRIT/KPI/Primary Focus.

### 2.B Option B — `<Name>`
(Repeat items 1–13; emphasize step-change mechanisms, extra uncertainty, and risk-reduction design.)

### 2.C Option C — `<Name>` (Contrarian)
(Repeat items 1–13; plus:)  
- Premortem: top 3 failure modes + leading indicators.  
- Counterfactual Value: learning/option value if outcomes underperform.

### 2.D Option D — `<Name>` (optional diversity)
(Repeat items 1–13; provide distinct strategic logic relative to A/B/C.)

---

## 2.x Mandatory Deep-Dives for Specific Decision Types (include when applicable)

### Training / Upskilling Deep-Dive (mandatory if any option includes training)
- Curriculum: modules, learning objectives, mapping to role families/skills taxonomy.  
- Hours & Modality: synchronous/asynchronous; in-person/virtual/hybrid; platform and content format.  
- Schedule & Cohorts: calendar by cohort; cohort sizes; coverage ratio by population; completion SLA.  
- Faculty/Trainers: internal vs vendor; instructor profile; certification requirements.  
- Assessment: pre/post testing; pass thresholds; target improvement (MDE); certification issuance; recert cycles.  
- Logistics: LMS configuration, content localization, accessibility compliance; rooms/virtual licenses.  
- Budget: per-learner costs (trainer hour, learner hour, materials, platform seat), volume × duration, total and per-learner cost; ramp by cohort.  
- KPIs: completion rate, assessment uplift, on-the-job proxy, time-to-productivity; cadence and data owner.  
- Dependencies: content authoring, procurement, legal approvals, privacy/DPIA if needed.  
- Communications: manager toolkits; learner comms schedule; reinforcement nudges.

### Compensation Adjustment Deep-Dive (mandatory if any option includes salary/comp changes)
- Quantum: increase by percent or euros, or band movement; target compa-ratio; red/green zones.  
- Eligibility: role families, performance gates, tenure rules, exclusions, geographic differentials.  
- Timing: effective dates, proration rules, payroll cycle coordination, retro adjustments policy.  
- Governance: approval matrix; audit trail; controls; risk of internal compression; equity/fair-pay checks.  
- Payroll Impact: gross-to-net; employer social charges/taxes; total enterprise cost per month/quarter/year.  
- Communication Plan: stakeholder sequencing; manager briefing kits; FAQs; grievance/appeals workflow.  
- Monitoring: retention/engagement KPIs; offer-accept ratio; market benchmarks; revisit triggers and cadence.  
- Budget: itemized deltas by population; taxes/charges; contingencies; link to Value Mechanics horizon.

---

## 3) Comparative Economics (Normalized)
Base case; optionally add O/B/P bands or Monte Carlo (10k) if available — report mean, p5/p50/p95.

Normalization Bases: FX rate (source/date), CPI base year (source), PPP if used; scope reconciliation.

| Option | One-line Thesis | CapEx [€] | OpEx [€/period] | Net Benefit [€/period] | ROI_12m [%] | Payback [months] | NPV @WACC [€] | IRR [%] | CX/SLA Anchor (unit) | Assumption Notes | Provenance |
|-------|------------------|----------:|-----------------:|-----------------------:|------------:|-----------------:|--------------:|--------:|----------------------|------------------|-----------|
| A     | ...              | ...       | ...              | ...                    | ...         | ...              | ...           | ...     | ...                  | ...              | ...       |
| B     | ...              | ...       | ...              | ...                    | ...         | ...              | ...           | ...     | ...                  | ...              | ...       |
| C     | ...              | ...       | ...              | ...                    | ...         | ...              | ...           | ...     | ...                  | ...              | ...       |
| D     | ...              | ...       | ...              | ...                    | ...         | ...              | ...           | ...     | ...                  | ...              | ...       |

Formulas  
- ROI = (Net Benefits / Investment) × 100  
- NPV = Σ_t CF_t / (1 + WACC)^t  (state rf, β, MRP)  
- Payback = months until cumulative net CF ≥ 0

WHY (3–5 bullets): dominant value drivers; uncertainty; comparability caveats.

---

## 4) Criteria-Fit Matrix (Normalized 0–1, Weights Sum = 1.00)
Evaluated under Criteria v1.0 (Lock Hash: `criteria-v1.0:<hash>`). GDPR_Compliance = gating (Fail ⇒ No-Go).

| Criterion (unit)      | Weight | Option A | Option B | Option C | Option D | One-line WHY                     | Source |
|-----------------------|-------:|---------:|---------:|---------:|---------:|----------------------------------|--------|
| ROI_12m (%)           |  0.xx  |    0.xx  |    0.xx  |    0.xx  |    0.xx  | Capital efficiency vs WACC       | (…)    |
| Time_to_Impact (weeks)|  0.xx  |    0.xx  |    0.xx  |    0.xx  |    0.xx  | Speed-to-value given window      | (…)    |
| GDPR_Compliance (bin) |  0.xx  |     1/0  |     1/0  |     1/0  |     1/0  | License to operate               | (…)    |
| Adoption_90d (%)      |  0.xx  |    0.xx  |    0.xx  |    0.xx  |    0.xx  | Behavioral uptake                | (…)    |
| Reliability_SLO (%)   |  0.xx  |    0.xx  |    0.xx  |    0.xx  |    0.xx  | Stability/SLA guardrail          | (…)    |

Weighted Totals (0–1):  
- Option A: 0.xx • Option B: 0.xx • Option C: 0.xx [• Option D: 0.xx]  
Ranking: `<A/B/C[/D]>` (explain ties via Primary Focus)

Behavioral Lens Summary: which levers most influence Adoption_90d and how they interact with time-to-impact/SLO.

---

## 5) Sensitivity Table (Quick, Decision-Useful)
| Driver Variable  | Δ        | Δ ROI_12m | Δ {Primary_KPI} | Confidence | Mechanism (WHY)                          |
|------------------|----------|-----------|------------------|-----------:|------------------------------------------|
| Recruitment cost | +10%     | −0.02     | +0.5 pp turnover | 0.7        | Cost pressure affects ROI and retention  |
| Time-to-market   | +2 weeks | −0.03     | −1.0 pp adoption | 0.6        | Missed novelty window reduces uptake     |
| Bonus spend      | +5%      | −0.01     | +0.2 pp retention| 0.8        | Incentive elasticity                     |

Explain dominant drivers and thresholds that would flip the recommendation.

---

## 6) Recommendation Rule (Operationalized)
- Choose A if ROI_12m ≥ X% and Payback ≤ Y months and GDPR Pass; tie-break by Primary Focus.  
- Choose B if Adoption_90d uplift ≥ Z pp and Reliability_SLO ≥ W% justifies longer time-to-impact.  
- Choose C (or D) if asymmetric upside or learning value dominates within the risk budget.  
- Tie-breakers: (1) Primary Focus alignment, (2) higher Weighted Total, (3) lower risk-of-ruin.  
- Early Triggers to Revisit: variance thresholds on cost/adoption/schedule/compliance; define owners and next-best action.

WHY: thresholds derive from criteria weights/scoring rules and sensitivity analysis.

---

## 7) Consolidated Risk View (Cross-Option)
| ID | Risk | Option(s) | Prob (0–1/L–H) | Impact (€/unit/L–H) | Horizon | Early Signal | Mitigation (HOW) | Owner | Trigger |
|----|------|-----------|----------------:|---------------------|--------:|--------------|------------------|-------|---------|
| …  | …    | …         | …               | …                   | …       | …            | …                | …     | …       |

Interdependency Note: e.g., Legal delay → Launch slip [days] → CAC ↑ [€/cust] → ROI ↓ [pp].  
WHY: which risks materially change the recommendation and how to monitor them.

---

## 8) Data Gaps & Collection Plan (MANDATORY for each TBD)
| Missing Data | Why Needed | Method (instrument/test/query) | Owner | ETA | Acceptance Criteria | Expected Source |
|--------------|------------|---------------------------------|-------|-----|---------------------|-----------------|
| <item>       | ROI/NPV/Payback input | DB extract / survey / experiment | <role> | YYYY-MM-DD | error ≤ ±x% | <system/report> |

Include experiment design where relevant (alpha, beta, power/MDE, guardrails).  
Mark every TBD as: “TBD → collected by <owner> before <date>.”

---

## 9) Appendices (Reproducibility & Provenance)
- A. Formulas & Parameters: ROI, NPV, IRR, Payback; elasticity models; KPI definitions.  
- B. Normalization Bases: FX/CPI/PPP sources + access dates; scope adjustments.  
- C. Source Register: title, publisher/author, date (YYYY-MM-DD), URL or Doc-ID/§, source type, recency notes.  
- D. Search/Index Notes (if used): vector namespaces, query operators, inclusion/exclusion criteria.  
- E. Assumption Log: each assumption + sensitivity tag + planned test (linked to §8).  
- F. Governance Artifacts: approval matrix templates; audit checklist; DPIA template (if relevant).

---

## Final Quality Gate (all must be YES)
- between_three_and_four_options == true  
- each_option_has_units_and_timeframes == true  
- option_includes_sequenced_action_plan_with_wbs_gantt_dependencies_and_critical_path == true  
- raci_defined_per_work_package == true  
- resources_and_fte_by_skill_and_seniority_declared == true  
- budget_line_items_capex_opex_with_unit_x_volume_x_duration_and_spend_calendar == true  
- behavioral_levers_subtable_present == true  
- assumptions_constraints_dependencies_explicit == true  
- phased_implementation_path_present == true  
- risk_register_with_probability_times_impact_and_triggers == true  
- kpis_with_targets_cadence_owner_alert_thresholds_and_runbook == true  
- governance_and_approvals_matrix_with_controls_and_audit == true  
- comparable_economics_normalized_with_formulas == true  
- criteria_fit_matrix_weights_sum_to_1_00 == true  
- recommendation_rule_references_primary_focus == true  
- sensitivity_table_present == true  
- option_c_or_4_contrarian_with_premortem_and_counterfactual == true  
- data_gaps_with_collection_plan_present == true  
- provenance_cues_present_for_material_claims == true  
- if_training_then_curriculum_hours_modality_schedule_cohorts_coverage_budget_kpis_dependencies_comms == true  
- if_compensation_then_amount_timing_eligibility_governance_payroll_impact_comms_budget_monitoring == true
"""

        return Task(
            description=description,
            expected_output=expected_output,
            agent=CreateAgent.create_agent(),
            markdown=True,
            output_file="05_create_report.md"
        )