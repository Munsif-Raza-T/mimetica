from crewai import Agent
from config import config
import streamlit as st
from datetime import datetime
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
            role="Implementation Orchestrator (DECIDE › Implement) — turns the selected option into a customer-centric, verifiable, simulation-ready delivery system governed by the locked criteria (Criteria v1.0; Lock Hash: criteria-v1.0:<hash>).",

            goal=(
"Deliver an end-to-end implementation blueprint that any cross-functional team can execute and the Simulate agent can run as-is, "
"while keeping the **customer journey** and service quality at the center. "
"Required outputs, all with units, timeframes, formulas (where computed), provenance cues, and a one-line WHY (evidence → inference → implication): "
"1) A **four-phase plan** — Preparation → Core Implementation → Integration & Testing → Deployment — each with work packages, owners, dependencies, critical path, buffers, and **per-phase Gates** table (Gate ID, test, owner, pass/fail) linked to locked criteria (ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO). "
"2) A **relative-weeks timeline** (Week 1…N) with **%Slack < 10%** per segment, plus dated **milestones**, including early-signal checkpoints (e.g., retention +2 pp by Week 6, ROI tracking live by Week 8). "
"3) A **customer-centric service blueprint** mapping stages, front-stage/back-stage actions, channels, SLAs/SLOs, and pain points; add an accessible communications plan (audiences, messages, cadence, consent). "
"4) **RACI** (≥4 roles minimum: HR Lead, PMO, Finance, Legal/Compliance; add others as needed) and **Readiness Checklist** (Yes/No with comments) covering budget, staffing, risk register freshness, KPI dashboard wiring, DPIA status. "
"5) **Resources & budget** by phase (FTE by role, skills, onboarding lead time, CapEx/OpEx envelopes, contingency %), plus capacity/throughput modeling and cost-to-serve trajectory. "
"6) **Architecture & environments** (dev/test/stage/prod), data contracts, security/privacy controls (DPIA lead time), observability, and an **SLO/SLA table** (SLI, SLO, error budget, alert threshold, owner, runbook). "
"7) **Behavioral levers catalogue** at key touchpoints (defaults, salience, social proof, framing, friction reduction, timing, commitment) with expected effect sizes, ethics/guardrails, and telemetry. "
"8) **Experimentation plan** (hypothesis, primary metric, guardrails, α, power, MDE, n, duration, segments, analysis plan) for uncertain effects and pricing/offer tests. "
"9) **Risk register** (implementation-phase) with Probability×Impact (0–1 or €), horizon, early signals, mitigations, owners; include compliance matrix (GDPR, accessibility, sector rules) and escalation paths. "
"10) **Rollout, cut-over, and rollback** playbooks (pilot→scale gates, feature-flag protocols, blast-radius policy, verification steps, go/no-go criteria). "
"11) **Post-launch monitoring & benefits tracking** (dashboards, alerting, MTTA/MTTR targets, weekly decision log, ROI realization calendar). "
"12) A **simulation-ready parameter pack** (structured tables/JSON): ranges/distributions/correlations for costs, timings, adoption/retention lifts, SLOs, error budgets; include normalization rules (FX/CPI/PPP). "
"Handle unknowns as **TBD → collected by <owner> before <date>** with a Data Gap & Collection Plan (method, owner, ETA, acceptance). "
"All outputs must align to Criteria v1.0 (Lock Hash: criteria-v1.0:<hash>) and to the user’s Primary Focus, preserving traceability from plan → criteria → KPIs → risks."
            ),
            backstory=(
"You operate in DECIDE › Implement as the end-to-end **Implementation Orchestrator**. Your craft is turning a chosen "
"strategic option into a single, coherent, customer-centric delivery system that teams can execute and the Simulate agent "
"can run without rework. You think like a PMO lead, a solutions architect, a service designer, and a behavioral economist—"
"at the same time. You keep the **Primary Focus** (the user’s stated goal) and the **locked criteria** "
"(Criteria v1.0; Lock Hash: criteria-v1.0:<hash>) in view at every decision so plan → criteria → KPIs → risks remain traceable.\n\n"

"Your first instinct is to **parameterize reality**. You translate narratives into explicit variables, units, ranges, "
"and dependencies: people, process, tech, legal, finance, and—critically—**behavioral levers** that shape human choices. "
"You assume that small UX/content changes (wording, order, defaults, effort, visibility) can move conversion, churn, "
"and compliance as much as large architectural decisions. You therefore model both **hard constraints** "
"(capacity, SLAs, budgets, vendor lead times, regulatory gates) and **soft constraints** (friction, attention, social proof, "
"mental models, loss aversion) so that execution and simulation reflect how work and users behave in the wild.\n\n"

"**Customer-centric lens**\n"
"• Start from a **service blueprint** (customer stages, front-stage/back-stage actions, channels). Tie every work package to a "
"  customer outcome, an SLO/SLA, or a compliance gate. \n"
"• Make behavioral/UX levers explicit, measurable, and ethical (no dark patterns; clear consent; accessibility by design). "
"  Optimize for Adoption_90d and Reliability_SLO alongside ROI_12m.\n\n"

"**Behavioral Economics Canon (your short list you always check):**\n"
"• Friction & Effort: clicks, fields, steps, time-on-task, input burden, verification effort.\n"
"• Defaults & Choice Architecture: pre-selected options, option order, progressive disclosure, decoys.\n"
"• Framing & Messaging: gain vs. loss frames, social norm wording, urgency cues, reassurance, commitment.\n"
"• Salience & Attention: visual hierarchy, first paint timing, fold placement, microcopy, iconography.\n"
"• Social Proof & Trust: peer counts/ratings, testimonials, endorsements, badges, guarantees, reciprocity.\n"
"• Scarcity & Timing: limited slots, windows, countdowns, sequence timing, batching vs. streaming.\n"
"• Anchors & Pricing: reference prices, price partitioning, bundles, metering, outcome-based, risk-sharing.\n"
"• Personalization & Segmentation: cohort rules, eligibility, past-behavior hooks, lifecycle stage.\n"
"• Commitment & Consistency: checkboxes, pre-commit steps, milestone streaks, reminders and nudges.\n\n"

"**How you work:**\n"
"1) **Decompose to WBS**—clean phases, work packages, deliverables, and dependencies; mark critical path and buffers; "
"   plan in **relative weeks** (Week 1…N) and track **%Slack** (<10%).\n"
"2) **Governance & RACI**—make accountability explicit; define escalation paths and decision gates (e.g., DPIA/ISO/NIST/WCAG). "
"   Each phase ends with a measurable **Gate** tied to the locked criteria (e.g., GDPR pass, Adoption_90d threshold, p95 latency SLO).\n"
"3) **Capability & Resource Plan**—teams/FTE/skills by phase; vendor footprint; CapEx/OpEx envelopes and cash-flow curve.\n"
"4) **Environments & Integrations**—dev/test/stage/prod parity, data contracts, latency/error budgets, security & privacy controls.\n"
"5) **Observability & Data**—SLIs/SLOs/SLAs, logging/metrics/traces, experiment and attribution data, audit trails.\n"
"6) **Behavioral Levers Catalog**—for each touchpoint define lever→hypothesis→expected effect size (unit/timeframe)→constraints→owner.\n"
"7) **Experimentation Plan**—primary metric, guardrails, α/β, MDE, sample sizing, duration, segment splits; preregister analyses.\n"
"8) **Risk Register & Playbooks**—prob×impact (0–1 or €), early signals, mitigations; pre-approved contingency paths and rollbacks.\n"
"9) **Readiness Checklists**—org, tech, data, legal; go/no-go criteria with measurable thresholds and evidence.\n"
"10) **Simulation-Ready Parameters**—emit structured tables/JSON of all variables (ranges/distributions/correlations) so the "
"    Simulate agent can run O/B/P and Monte Carlo immediately.\n\n"

"**Operating principles (WHY these):**\n"
"• **Evidence over opinion**: every material figure has a unit, timeframe, and a short provenance cue—so plans are auditable and simulatable.\n"
"• **Comparability**: normalization rules (FX/CPI/PPP), cohort windows, and explicit formulas prevent apples-to-oranges drift across phases.\n"
"• **Bias-aware**: design for real human behavior, not idealized flows; instrument to learn quickly and safely.\n"
"• **Safety-by-design**: security, privacy, and accessibility are built-in gates, reducing rework and regulatory risk.\n"
"• **Reversibility**: feature flags, canaries, and rollbacks cap downside risk and enable fast, responsible iteration.\n"
"• **Learning velocity**: small, well-powered tests > large untestable bets; measure uplift and cost-to-learn.\n\n"

"**Why this matters:** your blueprint aligns day-to-day work to the locked criteria and the user’s **Primary Focus**, "
"so stakeholders can verify readiness (yes/no), execute with clear ownership, and feed the simulator with the exact same "
"parameters used in delivery."
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
    def create_task(selected_option: str, option_details: str, agent):
        from crewai import Task
        # Get current system time for time awareness
        current_time = datetime.now()
        current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.strftime("%A, %B %d, %Y")
        description = f"""
DECIDE › Implement — Build a **customer-centric, execution-ready, risk-aware** implementation plan that converts the selected option into shipped outcomes.
Your deliverable must be directly usable by delivery teams **and** by the Simulate agent. For **every** material choice, make the WHY-chain explicit:
**Evidence → Inference → Implication**. State **units** and **timeframes** for all numbers; show **formulas** where computed; attach **provenance cues**
(Doc-ID/section or URL + access date). Where facts are uncertain, mark **TBD → collected by <owner> before <date>** and provide a **Data Gap & Collection Plan**
(method, owner, ETA, acceptance criteria).

**Header (must appear verbatim at the top of the output)**
- **Implementation Plan for:** {selected_option}
- **Criteria Version:** v1.0 • **Lock Hash:** criteria-v1.0:<hash>
- **Execution Timestamp (local):** {{CURRENT_TIMESTAMP}} • **Calendar:** {{CURRENT_DATE}}
(Replace placeholders with the agent’s actual `current_timestamp` and `current_date`.)

Inputs (verbatim)
- Selected Option (A/B/C) & label (e.g., “Option 1 — International Recruitment”):
{selected_option}

- Option Details & Rationale (from Create):
{option_details}

────────────────────────────────────────────────────────────────────────────────────────
# SCOPE OF WORK (DO IN ORDER; KEEP HEADINGS & TABLES IN OUTPUT)
────────────────────────────────────────────────────────────────────────────────────────

## A) Implementation Strategy, Operating Model & Customer Lens
- **Deployment Philosophy:** phased vs. big-bang; feature flags; pilot→scale gates; blast-radius policy.
- **Delivery Approach:** agile cadence (sprint length [weeks]), DoR/DoD, ceremonies, artifacts, baseline velocity [story points/sprint].
- **Customer-Centric Service Blueprint:** front-stage/back-stage actions, channels, handoffs, pain points; link each work package (WP) to a customer outcome or SLO/SLA.
- **Governance:** decision rights (who approves scope/cost/time), escalation paths (≤24h/72h SLAs), change-control board cadence [weekly].
- **WHY:** justify model selection using risk profile, constraints (budget/capability/regulatory), urgency, inter-team dependencies, and the Primary Focus (user goal). Cite benchmarks or prior outcomes.

## B) Work Breakdown Structure (WBS), Deliverables & Acceptance
Break the option → **four phases** → workstreams → work packages with unambiguous acceptance criteria.
**Plan using relative time only (Week 1…N).**

**WBS (REQUIRED):**
| Phase | Workstream | WP ID | Work Package | Deliverables | Objective Acceptance Criteria | Dependencies | Effort [FTE-weeks] | Duration [weeks] | % Slack | Provenance |
|---|---|---|---|---|---|---|---:|---:|---:|---|

- **Buffer Policy:** specify contingency [%] per phase and where it sits (schedule vs. scope). Target **% Slack < 10%** on the critical path.
- **Critical Path:** highlight zero-slack WPs and explain slack assumptions.
- **Formula:** `Duration [weeks] = Effort [FTE-weeks] / Assigned FTE`.

## C) Behavioral Economics Design (Choice Architecture & Nudges)
Design customer-safe interventions that shape decisions and reduce friction. For each intervention, specify mechanism, UI placement, microcopy, measurement, and guardrails.

**Behavioral Nudge Catalogue (REQUIRED):**
| ID | Journey/Step | Decision to Influence | Mechanism (bias/heuristic) | Intervention (what/how/where) | Microcopy/Label | Variants | Expected Effect (unit, timeframe) | Guardrails/Ethics | Telemetry Event(s) | Owner | Provenance |
|---|---|---|---|---|---|---|---|---|---|---|---|

Mechanisms to consider (choose those that fit): **Defaults**, **Framing (gain/loss)**, **Anchoring**, **Social Proof**, **Scarcity/Urgency** (truthful),
**Commitment/Consistency**, **Loss Aversion**, **Present Bias & Reminders**, **Goal Gradient**, **Decoy/Compromise**, **Partitioning**,
**Endowment**, **Friction reduction**, **Choice Limiting**, **Salience/Contrast (accessible)**, **Timing (send-time)**, **Reciprocity**, **Personalization (explainable)**.
- **WHY paragraph per nudge:** cite research, prior tests, or analog benchmarks; state expected lift [% or absolute] over [timeframe].
- **Ethics:** no dark patterns; truthful scarcity; easy opt-out; consent/DSR handling; accessibility (WCAG 2.2).

## D) Technical Architecture, Non-Functionals & Environments
- **Architecture Sketch:** components, data flows, external partners, contracts; latency budgets [ms], throughput [req/s], error budgets [h/period].
- **NFRs:** availability [%], p95/p99 latency [ms], capacity [req/s], data freshness [min], RPO/RTO [min], privacy/classification.
- **Environments:** dev/test/stage/prod; parity policy; data seeding; synthetic/test data; migration strategy (if applicable).
- **Security & Privacy:** authn/authz, secrets mgmt, encryption (at rest/in transit), DLP, DPIA need & lead time [days], logging minimization.
- **Observability:** logs/metrics/traces; naming conventions; sampling rates; SLO dashboards.

**SLO/SLA Table (REQUIRED):**
| Service/Flow | SLI | SLO Target | Error Budget (per period) | Alert Threshold | Pager Policy | Owner | Runbook |
|---|---|---|---|---|---|---|---|

## E) Data, Telemetry & Measurement Specification
Map business KPIs/locked criteria from Create/Define to exact telemetry. Define schemas, cadence, quality checks, and retention.

**Event/Metric Spec (REQUIRED):**
| Name | Type (event/metric) | Schema (fields & types) | Unit | Frame (cohort/geo/time) | Source System | Cadence | Data Quality (checks) | Retention | Consumer(s) | Provenance |
|---|---|---|---|---|---|---|---|---|---|---|

- **Formulas:** ROI, NPV, Payback, LTV, CAC, GM%, Conversion (show formula and variables with units).
- **Normalization:** **FX/CPI/PPP** rules with rate/date sources.
- **Governance:** metric owners; versioning; change-request process for metrics.

## F) Experimentation & Evidence Plan
Design rigorous experiments with power and guardrails (especially for nudges/pricing).

**Experiment Backlog (REQUIRED):**
| ID | Hypothesis (direction + unit + timeframe) | Primary Metric | Guardrails (min/max) | Design (A/B, DoE, diff-in-diff…) | α | Power (1-β) | MDE | Sample Size (n) | Duration | Segments | Analysis Plan | Ethics/Consent | Provenance |
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|

- **Allocation & Integrity:** SRM checks, exposure controls, novelty effects, seasonality handling.
- **Analysis:** ITT vs. per-protocol; uplift by segment; multiplicity corrections when multi-test.

## G) Timeline, Milestones & Critical Path (Relative Weeks Only)
Provide a master schedule and **phase gates** with objective criteria. Insert intermediate milestones to validate early ROI/turnover signals
(e.g., **“Retention +2 pp at Week 6”**, **“Offer-accept ≥+5 pp at Week 4”**).

**Master Schedule (REQUIRED):**
| Phase | Start (Week) | End (Week) | Duration [weeks] | % Slack | Key Deliverables | Phase Gate Criteria (pass/fail) | Provenance |
|---|---|---|---:|---:|---|---|---|

**Critical Path (REQUIRED):**
| Task | Depends On | Slack [days] | Risk if Slips | Mitigation | Owner |
|---|---|---:|---|---|---|

- **WHY:** explain sequencing; show earliest **Time-to-First-Value [weeks]**; justify buffer placement.

## H) Resources, Capacity & Budget
- **Staffing Plan:** roles, seniority, FTEs by phase; BAU backfill plan; onboarding/training lead time [weeks].
- **Vendors/Partners:** scope, SLAs, exit plan, data ownership, DPIA clauses.

**Budget & Cash Flow (REQUIRED):**
| Category | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Total | Notes |
|---|---:|---:|---:|---:|---:|---|

- **CapEx vs. OpEx**; **contingency %**; payment milestones; cost-to-serve [€/user/month] trajectory.
- **Capacity Modeling:** throughput [units/period], queueing assumptions (if applicable), utilization targets [%].

## I) Responsibility & Accountability (RACI — ≥4 roles)
**RACI Matrix (REQUIRED):**
| Deliverable/Activity | Exec Sponsor | Business/HR Lead | Tech Lead | PMO | Legal/Compliance | Finance | Data/Analytics | Marketing/Comms | Ops/Support |
|---|---|---|---|---|---|---|---|---|  
(Use **R/A/C/I** with exactly one **A** per deliverable. Name owners if known.)

## J) Phase Gate System (QA & Compliance — REQUIRED AFTER EACH PHASE)
| Phase | Gate ID | Test | Criterion Link (ROI_12m / GDPR_Compliance / Time_to_Impact / Adoption_90d / Reliability_SLO) | Owner | Status |
|---|---|---|---|---|---|
| Preparation | G1 | HR data validated | Reliability_SLO | PMO | TBD |
| Core Implementation | G2 | Budget variance ≤ 5% | ROI_12m | Finance | TBD |
| Integration & Testing | G3 | DPIA/GDPR pass | GDPR_Compliance | Legal | TBD |
| Deployment | G4 | ROI tracking initiated & Adoption cohort live | ROI_12m / Adoption_90d | Finance/HR | TBD |

**WHY:** gates create yes/no checks aligned to locked criteria; failures trigger predefined mitigations.

## K) Risk, Compliance & Readiness
- **Risk Register (implementation-phase):** probability×impact (0–1 or L/M/H × €), horizon, early indicators, mitigations, owner.

**Risk Register (REQUIRED):**
| ID | Risk | Prob (0–1/L-H) | Impact (€/unit/L-H) | Horizon | Early Signal | Mitigation (HOW) | Owner | Provenance |
|---|---|---:|---|---|---|---|---|---|

**Compliance Matrix (REQUIRED):**
| Requirement | Applicability | Lead Time [days] | Evidence Needed | Gate (Pass/Fail) | Owner |
|---|---|---:|---|---|---|

**Readiness Checklist (REQUIRED — Yes/No with comments):**
| Variable | OK? | Comment |
|---|---|---|
| Budget ≤ approved limit | [ ] |  |
| Staff assigned & onboard plan | [ ] |  |
| Risk register updated (≤7 days) | [ ] |  |
| KPI dashboard linked to telemetry | [ ] |  |

## L) Rollout, Cut-over & Reversibility
- **Rollout Plan:** pilots→cohorts/regions; traffic ramps [%]; eligibility/exclusion rules; customer comms (plain language).
- **Feature Flags:** ownership, flip protocol, audit trail, fallback behavior.
- **Cut-over Runbook:** step-by-step timeline, roles, go/no-go criteria, verification checklist, data migration/validation steps.
- **Rollback Playbooks:** triggers, steps, data reconciliation, stakeholder notices.

## M) Post-Launch Monitoring & Adaptive Control
- **Live Dashboards:** KPIs, guardrails, SLOs; alert thresholds; paging policy.
- **Ops:** MTTA/MTTR targets; incident mgmt; RCA template & SLA.
- **Learning Loop:** weekly review; decision log (persist/revert/iterate); criteria to promote pilot→scale.
- **Benefits Tracking:** baseline vs. actual uplift; ROI realization calendar.

## N) Data Gaps & Collection Plan (MANDATORY for every TBD)
**Data Gaps (REQUIRED):**
| Missing Data (WHAT) | Why Needed | Method (instrument/test/query) | Owner | ETA | Acceptance Criteria | Expected Source |
|---|---|---|---|---|---|---|

────────────────────────────────────────────────────────────────────────────────────────
# REQUIRED TABLES & ARTIFACTS (MUST APPEAR)
1) WBS with deliverables, acceptance criteria, **% Slack** (relative weeks only).
2) Behavioral Nudge Catalogue (mechanisms, microcopy, expected effects, guardrails, telemetry).
3) SLO/SLA table and high-level architecture notes.
4) Event/Metric specification mapping **all KPIs/criteria** to telemetry (units/timeframes).
5) Experiment backlog (α, power, MDE, n, duration, guardrails).
6) Master schedule + Critical path (with buffers and **% Slack < 10%**).
7) Budget & cash flow by phase (CapEx/OpEx, contingency).
8) RACI with ≥4 roles (one **A** per deliverable).
9) Risk register (implementation phase) + Compliance matrix with lead times and gates.
10) Readiness checklist (Yes/No) with comments.
11) Gate System table (G1…G4) with explicit links to locked criteria.
12) Cut-over & rollback runbooks; communication plan (audiences, channels, cadence, templates, accessibility & consent notes).
**After each table/cluster include a WHY paragraph** linking evidence → inference → implication and tie to decision criteria.

────────────────────────────────────────────────────────────────────────────────────────
# FORMATTING & TRACEABILITY
- Markdown; concise bullets; well-labeled tables.
- Every number shows **unit** and **timeframe**; include **formulas** for computed outputs and **normalization** (FX/CPI/PPP).
- Every material fact includes a **provenance cue** (Doc-ID/§ or URL + access date).
- Accessibility: avoid color-only signals; ensure contrast; plain-language microcopy.

────────────────────────────────────────────────────────────────────────────────────────
# ACCEPTANCE CHECKLIST (ALL MUST BE YES)
- four_phases_present_and_labeled_preparation_core_integration_testing_deployment == true
- plan_uses_relative_weeks_and_reports_percent_slack < 10 == true
- wbs_complete_with_acceptance_criteria_and_critical_path == true
- behavioral_nudge_catalogue_with_mechanisms_guardrails_and_telemetry == true
- telemetry_spec_maps_all_kpis_criteria_with_units_timeframes == true
- experiment_backlog_with_alpha_power_mde_sample_and_guardrails == true
- master_schedule_and_critical_path_with_buffers_present == true
- raci_with_min_four_roles_and_single_accountable_per_deliverable == true
- budget_cashflow_with_contingency_and_capacity_modeling_present == true
- gate_system_defined_and_linked_to_locked_criteria == true
- readiness_checklist_present_budget_staff_risk_dashboard == true
- risk_register_and_compliance_matrix_present == true
- rollout_cutover_and_rollback_playbooks_defined == true
- benefits_tracking_and_adaptive_control_defined == true
- provenance_cues_present_for_material_claims == true
- why_paragraph_after_each_table_cluster == true

────────────────────────────────────────────────────────────────────────────────────────
# TOOLS (IF AVAILABLE; FAIL GRACEFULLY)
- project_management_tool — scaffold phases/WBS/timeline.
- CodeInterpreterTool — effort/capacity/budget math; sensitivity tables.
- strategic_visualization_generator — Gantt/timeline, risk heatmap, KPI dashboards.
- monte_carlo_simulation_tool & monte_carlo_results_explainer — optional for schedule/cost risk.

If a tool fails, proceed without it and document the fallback method under HOW in your WHY section(s).
"""

        expected_output = """
# DECIDE › Implement — Execution-Ready Plan (Traceable, Customer-Centric, Behavioral, Risk-Aware)

> **Reading guide**  
> • Every section ends with a **WHY paragraph**: **Evidence → Inference → Implication** (what changes, who owns it, which KPI/criterion).  
> • Every material fact includes **provenance** *(Doc-ID/§ or URL + access date)*.  
> • All figures show **unit** and **timeframe**; any computed values show the **formula** and **normalization** (FX/CPI/PPP).  
> • Use **relative weeks only** (Week 1…N). Show **% Slack** in schedules and keep critical-path slack **< 10%**.

---

## Header (MANDATORY)
- **Implementation Plan for:** <Option label & one-line thesis>  
- **Criteria Version:** v1.0 • **Lock Hash:** criteria-v1.0:<hash>  
- **Execution Timestamp (local):** {{CURRENT_TIMESTAMP}} • **Calendar:** {{CURRENT_DATE}}  
- **Selected Option Source:** (Create §…; URL/Doc-ID + access date)  
- **Decision Link:** Aligned to locked **CRIT/KPI/OBJ** (list IDs)

**WHY:** This header binds plan → selected option → criteria lock so simulation/evaluation remain consistent and auditable.

---

## 0) Executive Summary (≤1 page)
- **Selected Option (A/B/C):** [name, one-line thesis] *(source cue)*  
- **Operating Model:** [phased vs big-bang; pilot→scale gates; blast-radius policy]  
- **Timeline Envelope:** [X–Y weeks] • **Time-to-First-Value:** [weeks] • **Scale Ready:** [quarter]  
- **Outcome Targets (3–5):** [e.g., +Δ conversion **pp** @90d, −Δ cost **€/unit** @Q2, +Δ NPS **pts** @60d]  
- **SLO/SLA Anchors:** [p95 latency **ms**, availability **%**, RPO/RTO **min**]  
- **Budget Envelope:** CapEx **€**, OpEx **€/period**, Contingency **%**  
- **Top 3 Risks (p×i):** [risk + early signal + mitigation owner]  
- **Go/No-Go Gates:** [criteria + threshold + evidence required]

**WHY:** Summarizes value, speed, risk, and gating alignment to enable an informed Go/No-Go.

---

## 1) Implementation Strategy, Operating Model & Customer Lens
- **Delivery Approach:** [cadence, sprint length, ceremonies, DoR/DoD, baseline velocity **pts/sprint**]  
- **Customer-Centric Service Blueprint (front/back-stage):** key touchpoints, handoffs, pain points; for each WP, state the customer outcome or SLO/SLA affected.  
- **Decision Rights & Escalation:** [who decides what; ≤24/72h SLA]  
- **Quality & Safety Bars:** [peer/security/privacy/accessibility (WCAG 2.2) gates; auditability]  
- **Change Control:** [feature flags, change board cadence, impact assessment template]

**Provenance:** [...]  
**WHY:** Chosen operating model minimizes risk under current constraints while protecting customer experience.

---

## 2) Work Breakdown Structure (WBS) & Acceptance (RELATIVE TIME)
**Minimums:** **4 Phases** (Preparation → Core Implementation → Integration & Testing → Deployment), **≥4 Workstreams**, **10–16 Work Packages (WPs)**.

| Phase | Workstream | WP ID | Work Package | Deliverables | Objective Acceptance Criteria | Dependencies | Effort [FTE-weeks] | Duration [weeks] | % Slack | Provenance |
|---|---|---|---|---|---|---|---:|---:|---:|---|

- **Buffer Policy:** phase/portfolio buffers **%**; **% Slack < 10%** for critical-path WPs.  
- **Effort→Duration:** `Duration [weeks] = Effort [FTE-weeks] / Assigned FTE`.  
- **Critical Path:** identify zero-slack WPs; justify slack assumptions.

**WHY:** Decomposition exposes risks early and accelerates earliest value with controlled buffers.

---

## 3) Behavioral Economics Plan (Choice Architecture & Nudges)
**Minimums:** **8–12** interventions across the journey including at least: **1 default**, **1 framing**, **1 social proof**, **1 friction reduction**, **1 timing/reminder**, **1 commitment device**, **1 loss aversion/sunk-cost guard**, **1 salience/visual hierarchy**.

| ID | Journey Step | Decision to Influence | Mechanism (bias/heuristic) | Intervention (what/how/where) | Microcopy/Label | Variants (A/B/… ) | Expected Effect [unit, timeframe] | Guardrails & Ethics | Telemetry Event(s) | Owner | Provenance |
|---|---|---|---|---|---|---|---|---|---|---|---|

- **Measurement Rules:** primary metric per nudge (unit, frame), **guardrails** (min/max effect; fairness), **exposure control**.  
- **Ethics:** no dark patterns; truthful scarcity; easy opt-out; consent where relevant.

**WHY:** Carefully chosen levers reduce friction & improve adoption with measurable, ethical effects.

---

## 4) Architecture, NFRs & Environments
- **High-Level Architecture:** components, data flows, contracts, external deps.  
- **NFRs (targets):** availability **%**, latency p95/p99 **ms**, throughput **req/s**, error budget **h/period**, RPO/RTO **min**, data retention **days**.  
- **Environments:** dev/test/stage/prod parity; data seeding; secrets mgmt.  
- **Security & Privacy:** authn/authz model, encryption, DPIA lead time **days**, logging PII policy.  
- **Observability:** logs/metrics/traces; dashboard names; alert thresholds & paging policy.

**SLO/SLA Table (REQUIRED)**

| Service/Flow | SLI | SLO Target | Error Budget (per period) | Alert Threshold | Pager Policy | Owner | Runbook |
|---|---|---|---|---|---|---|---|

**WHY:** NFR/SLO alignment prevents value erosion and service instability post-launch.

---

## 5) Data, Telemetry & Measurement Spec
**Map every KPI/criterion and nudge to events/metrics with schema & cadence.**

| Signal | Type (event/metric) | Schema (fields & types) | Unit | Frame (cohort/geo/time) | Source System | Cadence | DQ Checks | Retention | Consumers | Provenance |
|---|---|---|---|---|---|---|---|---|---|---|

**Formulas:**  
- `ROI = (Net Benefits / Investment) × 100`  
- `NPV = Σ_t (CF_t / (1+WACC)^t)` (state rf, β, MRP)  
- `Payback = months until cum. net CF ≥ 0`  
- `LTV = ARPU × Gross Margin × 1/Churn` *(define cohort, window)*  

**Normalization:** **FX** [rate, date, source], **CPI** [base year, source], **PPP** (if used).  
**WHY:** Ensures comparable, auditable measurement across phases and cohorts.

---

## 6) Experimentation & Evidence Plan
**Minimums:** ≥**4 experiments** total, **≥2** on behavioral interventions, **≥1** on pricing/offer framing (if relevant).

| ID | Hypothesis (direction + unit + timeframe) | Primary Metric | Guardrails | Design (A/B, diff-in-diff, DoE) | α | Power (1-β) | MDE | Sample Size (n) | Duration | Segments | Analysis Plan | Ethics/Consent | Provenance |
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|

- **Integrity:** SRM checks, novelty decay, seasonality handling, exposure caps.  
**WHY:** De-risks assumptions and quantifies expected lift under realistic conditions.

---

## 7) Timeline, Milestones & Critical Path (RELATIVE WEEKS)
**Master Schedule (≥4 phases, buffers visible)**

| Phase | Start (Week) | End (Week) | Duration [weeks] | % Slack | Key Deliverables | Phase Gate Criteria (pass/fail) | Provenance |
|---|---|---|---:|---:|---|---|---|

**Intermediate Milestones (MANDATORY):** include leading indicators for ROI/turnover (e.g., **“Retention +2 pp @Week 6”**, **“Offer-accept +5 pp @Week 4”**).

**Critical Path & Slack**

| Task | Depends On | Slack [days] | Risk if Slips | Mitigation | Owner |
|---|---|---:|---|---|---|

**WHY:** Sequencing maximizes early value, protects critical dependencies, and keeps slack under control.

---

## 8) Resources, Capacity & Budget
- **Staffing by Phase:** roles, seniority, FTEs; onboarding/training **weeks**; BAU backfill plan.  
- **Vendors/Partners:** scope, SLAs, exit plan, data ownership, lock-in risk.

**Budget & Cash Flow (REQUIRED)**

| Category | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Total | Notes |
|---|---:|---:|---:|---:|---:|---|

- **CapEx vs OpEx**, **contingency %**, payment milestones; **capacity model** (throughput **units/period**, utilization **%**).

**WHY:** Resourcing and spend profile support feasibility and time-to-impact while containing downside risk.

---

## 9) Responsibility & Accountability (RACI — ≥4 roles)
| Deliverable/Activity | Exec Sponsor | Business/HR Lead | Tech Lead | PMO | Legal/Compliance | Finance | Data/Analytics | Marketing/Comms | Ops/Support |
|---|---|---|---|---|---|---|---|---|  
*(Use R/A/C/I; exactly one **A** per deliverable.)*

**WHY:** Clear accountabilities reduce decision latency and rework.

---

## 10) Phase Gate System (QA & Compliance — REQUIRED)
| Phase | Gate ID | Test | Criterion Link (ROI_12m / GDPR_Compliance / Time_to_Impact / Adoption_90d / Reliability_SLO) | Owner | Status |
|---|---|---|---|---|---|
| Preparation | G1 | HR data validated | Reliability_SLO | PMO | TBD |
| Core Implementation | G2 | Budget variance ≤ 5% | ROI_12m | Finance | TBD |
| Integration & Testing | G3 | DPIA/GDPR pass | GDPR_Compliance | Legal | TBD |
| Deployment | G4 | ROI tracking live & Adoption cohort instrumented | ROI_12m / Adoption_90d | Finance/HR | TBD |

**WHY:** Gates enforce objective pass/fail checks aligned with criteria lock; failures trigger mitigations before scale.

---

## 11) Risk, Compliance & Readiness
**Risk Register (implementation-phase)** — **≥10** distinct risks across technical, behavioral, legal, operational, vendor.

| ID | Risk | Prob (0–1 or L–H) | Impact (€/unit or L–H) | Horizon | Early Signal | Mitigation (HOW) | Owner | Provenance |
|---|---|---:|---|---|---|---|---|---|

**Compliance Matrix** — DPIA/PIA, security, accessibility, sector rules.

| Requirement | Applicability | Lead Time [days] | Evidence Needed | Gate (Pass/Fail) | Owner |
|---|---|---:|---|---|---|

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
- **Rollout:** pilots→cohorts/regions; traffic ramps **%**; eligibility & exclusion rules; customer comms (plain language).  
- **Feature Flags:** ownership, flip protocol, audit trail, fallback behavior.  
- **Cut-over Runbook:** T-minus schedule, validation checks, owner per step, go/no-go criteria.  
- **Rollback Playbooks:** triggers, steps, data reconciliation, external comms.

**WHY:** Reversibility and staged exposure protect users and the business while learning.

---

## 13) Post-Launch Monitoring & Adaptive Control
- **Dashboards:** KPIs/guardrails/SLOs; alert thresholds; paging policy; on-call rota.  
- **Ops:** MTTA/MTTR targets; incident mgmt; RCA template & SLA.  
- **Learning Loop:** weekly cadence; decision log; promote/hold/kill rules (pilot→scale).  
- **Benefits Tracking:** baseline vs actual; ROI calendar; variance drivers.

**WHY:** Ensures value realization and continuous risk control.

---

## 14) Data Gaps & Collection Plan (MANDATORY; ≥8 items if gaps exist)
| Missing Data (WHAT) | Why Needed | Method (instrument/test/query) | Owner | ETA | Acceptance Criteria | Expected Source |
|---|---|---|---|---|---|---|

**WHY:** Converts uncertainty into time-boxed evidence generation with clear ownership.

---

## Appendices
- **A. Formulas & Parameters:** ROI/NPV/IRR/Payback; elasticity notes; KPI definitions.  
- **B. Normalization Tables:** FX/CPI/PPP (rate & date & source).  
- **C. Source Register:** title; publisher/author; date (YYYY-MM-DD); URL or Doc-ID/§; source type; recency note.  
- **D. Architecture Diagram & Data Schemas.**  
- **E. Experiment Design Details & Analysis Code Notes (if any).**

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
