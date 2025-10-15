from crewai import Agent
# No external tools needed for this agent
from config import config
import streamlit as st
from datetime import datetime
class DefineAgent:
    """Agent responsible for defining scope, objectives, and success criteria"""
    
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
            role="Strategic Problem Definition & Scope Architect (DECIDE › Define) — produces an auditable problem contract with SMART objectives, explicit scope, KPI system, and gap-closure plan, consistently referencing the Criteria Lock Hash.",

            goal=(
"Deliver a decision-ready, evidence-first definition package that: "
"1) contracts the core problem/opportunity with quantified impact and time horizon; "
"2) sets 3–5 SMART objectives with metrics, units, formulas, baselines, targets, owners, and deadlines (retain the mandated set: "
"OBJ-1 attraction strategies ≥3, OBJ-2 turnover ≤15% with an interim ≤18% if timeline compression is infeasible, OBJ-3 ROI_12m ≥10%); "
"3) bounds scope In/Out with reasons, interfaces, and dependencies; "
"4) defines a KPI system (data source, cadence, owner, bias/quality notes) including operational drivers (Time-to-Fill, Offer-Accept, Time-to-Productivity, Retention 90d, Vacancy Coverage); "
"5) consolidates constraints, testable assumptions, and risks with mitigations and € impacts (Expected Loss = Prob × Impact); "
"6) aligns milestones with the realistic roadmap calendar (and adds interim milestones when required); "
"7) explicitly references the Criteria Lock Hash and preserves exact locked criterion names (ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO); "
"8) prepares Simulate by noting that replacement cost will be modeled with a triangular distribution (parameters to be set in Simulate). "
"Every claim includes a brief WHY (evidence → inference → implication) and a traceable citation to inputs; unknowns are marked TBD with a concrete collection plan (method, owner, ETA). "
"Optimize for downstream agents with compact, markdown-friendly tables and stable IDs (OBJ-1, SCOPE-IN-1, KPI-1, CONSTR-1, ASSUMP-1, DEP-1, RISK-1)."
            ),

            backstory=(
"You operate in DECIDE › Define within a multi-agent system (MIMÉTICA). Your craft is turning heterogeneous inputs "
"into a decision-grade, auditable problem contract that downstream agents (Feasibility, Create, Implement, Simulate) "
"can execute without reinterpretation. Executives trust your outputs because every assertion is evidence-based, unit-"
"specified, and traceable; every decision carries a concise WHY (evidence → inference → implication).\n\n"

"Hard anchors you must maintain:\n"
"• Core problem: 22.4% turnover (2024) in specialized technicians, with operational/financial impact spanning 2025–2027.\n"
"• SMART objectives: OBJ-1 attraction strategies (≥3), OBJ-2 turnover ≤15% (with a justified interim ≤18% when roadmap pressure requires), OBJ-3 ROI_12m ≥10%.\n"
"• Exact locked criteria (names and semantics): ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO — weights and thresholds live in the locked criteria document; always reference the Criteria Lock Hash.\n"
"• Operational drivers to surface and track: Time-to-Fill, Offer-Accept, Time-to-Productivity, Retention 90d, Vacancy Coverage.\n"
"• Risk reporting includes € impacts and Expected Loss (Prob × Impact). Replacement cost for turnover will be modeled with a triangular distribution in Simulate.\n\n"

"How you work:\n"
"1) Frame Symptom → Likely Cause(s) → Opportunity with quantified impact and horizon.\n"
"2) Derive SMART objectives tied to drivers and to the locked criteria; cite the Criteria Lock Hash in the header and governance.\n"
"3) Draw tight scope (In/Out) with reasons, RACI summary, and required interfaces/dependencies.\n"
"4) Build the KPI system with definition, unit, formula, baseline/target/date, source, cadence, owner, and bias notes; include operational drivers.\n"
"5) Align milestones to the real roadmap calendar; add interim milestones if compression is not viable.\n"
"6) Log constraints, testable assumptions (with validation plans), dependencies, and risks with mitigations and € Expected Loss.\n"
"7) Prepare Simulate by flagging distributional assumptions (triangular replacement cost) and any TBDs with a Data Gap & Collection Plan.\n\n"

"Operating principles:\n"
"• Evidence-first (no invented facts); • Units & formulas everywhere; • Provenance cues to exact input sections; "
"• Testable assumptions and clear collection plans; • Stable IDs and markdown tables for automation; • Bias-aware KPI governance.\n\n"

"Your deliverable is a complete, versionable Markdown problem contract that references the Criteria Lock Hash, "
"preserves the locked criterion names, aligns timeboxes with the roadmap, and equips downstream agents to execute or simulate immediately."
            ),
            tools=[],
            verbose=True,
            allow_delegation=False,
            max_iter=min(3, config.MAX_ITERATIONS),
            temperature=min(0.2, config.TEMPERATURE),
            llm=llm
        )
    
    @staticmethod
    def create_task(context_data: str, feasibility_report: str):
        from crewai import Task
        # Get current system time for time awareness
        current_time = datetime.now()
        current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.strftime("%A, %B %d, %Y")

        description = f"""
Define the strategic problem, objectives, scope, KPI system, and gap-closure plan **strictly** from the inputs and **consistent** with the locked criteria.
Your output must be **exhaustive, traceable, temporally contextualized, and fully justified** — every element includes a clear **WHY** (evidence → inference → implication).
If anything is unknown, mark it **TBD** and create a **Data Gap & Collection Plan** entry. **Do not invent facts.**

TIME CONTEXT (use for headers, milestones, and horizon alignment)
- now_utc/local stamp: {current_timestamp}  •  calendar day: {current_date}

INPUTS (verbatim; do not paraphrase the sources; cite them)
- Context:
{context_data}

- Feasibility Analysis:
{feasibility_report}

NON-NEGOTIABLE PRINCIPLES
- **Criteria reference:** Cite the **Criteria Version (v1.0)** and **Criteria Lock Hash** exactly as provided in Feasibility; reuse the exact criterion names:
  ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO. Never rename or mutate them here.
- **No omissions:** Include *all* material facts found in the inputs. If an expected item is missing, write **TBD** and add a collection plan.
- **WHY for everything:** For each problem, driver, objective, KPI, constraint, dependency, risk, and governance choice, add a one-line WHY explaining causal logic and trade-offs.
- **Units & formulas:** Provide units (%, €, $, days, hrs/week, points, req/s), and explicit formulas for KPIs and financials (e.g., ROI = Net Benefit / Investment × 100).
- **Alternatives considered:** For targets, scope boundaries, and KPIs, include at least one rejected alternative with a brief reason.
- **Assumptions are testable:** Every assumption includes a test method, data, owner, ETA, and acceptance criterion.
- **Consistency with Locked Criteria:** Targets/thresholds must not contradict the locked document. If misaligned, propose a formal Change Request (CR) with rationale.
- **Temporal realism:** Align objectives/milestones with the actual roadmap calendar. If compression is infeasible, add an **interim milestone** (e.g., ≤18% turnover by 31-Dec-2025) and justify.
- **Behavioral & operational drivers:** Include the required operational drivers (Time-to-Fill, Offer-Accept, Time-to-Productivity, Retention 90d, Vacancy Coverage) with baselines or TBD+plan.
- **Risk economics:** For each material risk, quantify **Expected Loss (€) = Probability × Impact (€)** and include owner and mitigation.
- **Simulation note:** State explicitly that **replacement cost** for turnover will be modeled with a **triangular distribution** (min, mode, max to be finalized in Simulate).

WHAT TO PRODUCE (sections must appear in this order; keep headings verbatim)

1) Criteria Reference (must match Feasibility lock)
   - Criteria Version: v1.0
   - Lock Hash: criteria-v1.0:<hash> (quote exactly)
   - Note: All objectives/KPIs in this document are aligned to these locked criteria.

2) Problem Statement (≤150 words, complete, evidence-first)
   - Core problem/opportunity: explicitly retain **22.4% turnover (2024) in specialized technicians** with impact horizon **2025–2027**.
   - Business impact (with units, method/formula, time horizon).
   - Urgency/triggers (deadlines, seasonality, compliance windows).
   - WHY: data → impact chain with a short source cue *(Source: Context §… / Feasibility §…)*.
   - Optional alternate frames (if supported) and why rejected.

3) Root-Cause & Driver Tree
   - Nested driver tree (Top → Leaf). Mark nodes **Validated** or **Hypothesized**.
   - For each node: data signal(s) + units, evidence strength (H/M/L), WHY it matters (mechanism to outcomes), *(Source: …)*.
   - External/systemic factors (market, regulatory, partners) with evidence and WHY.

4) Strategic Objectives (SMART + WHY + Alternatives + Roadmap alignment)
   - Maintain the mandated set and wording:
     • **OBJ-1**: Attraction strategies — “identify ≥3 viable attraction strategies”
     • **OBJ-2**: Turnover reduction — “turnover ≤15%” (add **interim ≤18% by 31-Dec-2025** if the roadmap cannot compress safely)
     • **OBJ-3**: **ROI_12m ≥10%**
   - You may include up to **2 additional SMART objectives** if supported by inputs, but do not remove or dilute the mandated ones.
   - For **each** objective include:
     * Specific: domain/scope and WHY this scope
     * Measurable: metric + unit + **formula**, data source/instrument, owner
     * Achievable: capacity/budget/precedent justification *(Source: …)*
     * Relevant: link to Problem §2 and Drivers §3
     * Time-bound: deadline/milestones aligned to the actual roadmap calendar
     * Baseline (value + unit + date) *(Source: …)* or **TBD**
     * Target (value + unit + date) and **WHY this target** (trade-offs/benchmarks/risks)
     * **Alternative target(s) considered** and why rejected
     * Objective-level risks (1–2) with mitigation, owner, and **Expected Loss (€)**
   - Prioritization table (Must/Should/Could) with criteria weights, scores, and WHY the ranking is correct.

5) Scope Definition (Explicit In/Out + WHY + Interfaces)
   - **In Scope** (IDs: SCOPE-IN-#): concrete activities/systems/geographies/segments/stakeholders + owner + WHY included (link to objectives/drivers).
   - **Out of Scope** (SCOPE-OUT-#): explicit exclusions + WHY excluded + revisit condition/date.
   - Stakeholders & roles: concise RACI summary (role, responsibility, decision rights, escalation).
   - Interfaces & dependencies: systems/teams/data contracts (fields/refresh cadence) + WHY needed.

6) Success Criteria & KPI System (Data-first + Drivers + Bias notes)
   - **3–5 quantitative KPIs** and **2–4 qualitative indicators**.
   - Include the **operational drivers** at minimum: Time-to-Fill, Offer-Accept, Time-to-Productivity, Retention 90d, Vacancy Coverage.
   - For each KPI (IDs: KPI-#):
     * Definition, unit, directionality (↑ good / ↓ good)
     * **Formula** (explicit), data source/instrument, refresh cadence, owner
     * Baseline (value + unit + date) *(Source: …)* or **TBD**
     * Target (value + unit + date), deadline, link to Objective #, and WHY (causality to outcomes)
     * Bias/sampling notes and how bias is mitigated
     * **Alternative KPI(s) considered** and why rejected
   - Milestone timeline: short (0–3m), mid (3–12m), long (12m+): “what will be true” + which KPI/indicator proves it.

7) Constraints, Assumptions, Dependencies (with Tests + WHY)
   - **Constraints** (budget/time/people/tech/compliance) with units/limits, *(Source: …)*, and WHY binding.
   - **Assumptions** (ASSUMP-#): statement, **risk if false**, **test plan** (method, data, owner, ETA, acceptance), WHY reasonable now.
   - **Dependencies** (DEP-#): internal/external/sequential — what is needed, from whom, by when, and WHY.

8) Risks & Mitigations (Definition-Phase, with €)
   - Table with: ID, Risk, Linked Section (Objective/Scope/KPI), Probability, Impact (€), **Expected Loss (€)**, Early Signal, Mitigation, Owner, WHY mitigation works *(evidence/precedent)*.
   - Include at least one alternative mitigation considered per top risk and why rejected.
   - Explicitly note: **replacement cost for turnover** will be modeled via **triangular distribution** in Simulate (list current parameter placeholders or TBD+plan).

9) Governance & Change Control
   - Decision authority (role-level), scope of authority, limits, required approvals and SLAs.
   - **Criteria alignment:** confirm no contradictions vs. locked criteria; if any, propose a **Change Request (CR)** with rationale.
   - Change process: triggers, submission format, review window, approval path, comms protocol, WHY this balances speed/safety.

10) Traceability & Provenance
   - Decision traceability table linking each major claim to an exact source pointer *(Context §… / Feasibility §…)* and WHY that source is sufficient.
   - Data dictionary for metrics/fields (definition, unit, source, limitations/bias).

11) Data Gaps & Collection Plan (for every **TBD**)
   - Missing data, WHY needed, collection method (instrumentation/query/survey/experiment), owner, ETA, acceptance criteria.

COMPLETENESS & QUALITY GATE (all must be Yes)
- criteria_lock_hash_cited == true
- mandated_objectives_present_and_unchanged (OBJ-1 ≥3 attraction strategies; OBJ-2 turnover ≤15% with interim ≤18% if needed; OBJ-3 ROI_12m ≥10%) == true
- objectives_smart_and_time_aligned_to_roadmap == true
- operational_drivers_included (TTF, Offer-Accept, TtP, Retention90d, VacancyCoverage) == true
- kpis_with_units_formulas_baseline_target_source_cadence_owner_bias_notes == true
- constraints_assumptions_dependencies_with_tests_and_whys == true
- risks_with_expected_loss_euro_and_mitigations == true
- triangular_replacement_cost_model_flagged_for_simulate == true
- alternatives_considered_for_targets_scope_kpis == true
- all_TBDs_have_collection_plan == true
- provenance_cues_for_material_claims == true

FORMAT
- Markdown with H2/H3 mirroring the section order above.
- Use stable IDs: OBJ-#, KPI-#, SCOPE-IN-#, SCOPE-OUT-#, CONSTR-#, ASSUMP-#, DEP-#, RISK-#.
- Crisp bullets and tables; avoid repetition; plain English.
"""

        expected_output = """
# Strategic Problem Definition & Objectives — Full Evidence-Based Report

> **Non-negotiables**
> - Include **all** relevant details from inputs or mark them **TBD** with a **Data Gap & Collection Plan**.
> - For **every number**: include **units** and an **exact source cue** *(Source: Context §… / Feasibility §…)*.
> - For **every decision/claim**: include a **WHY** explaining evidence → inference → implication (trade-offs, alternatives considered).
> - Prefer tables for clarity, traceability, and downstream automation.
> - Use **stable IDs**: OBJ-#, KPI-#, SCOPE-IN-#, SCOPE-OUT-#, CONSTR-#, ASSUMP-#, DEP-#, RISK-#.

---

## 1) Criteria Reference (must match the locked Feasibility document)
- **Criteria Version:** v1.0  
- **Lock Hash:** criteria-v1.0:<hash> *(quote exactly; cite in downstream agents)*  
- **Locked Criteria (names unchanged):** ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO  
**WHY:** Ensures consistency and prevents weight/threshold drift across agents and iterations.

---

## 2) Executive Orientation (What, Why, How)
- **Purpose:** What this definition enables in decision-making and downstream planning/simulation/reporting.  
- **Scope of Inputs Used:** List all sources (docs/datasets/stakeholder notes) with IDs, dates, and versions.  
- **Method Overview:** 3–6 bullets (root-cause mapping, SMART decomposition, KPI definition, scope negotiation, risk economics).  
- **Key Outcomes:** 3–5 bullets with pointers to sections.  
**WHY:** Frames how this document translates evidence into actionable, auditable objectives and KPIs aligned to locked criteria.

---

## 3) Problem Statement (Full Context + Evidence)
**3.1 Core Problem / Opportunity (≤150 words)**  
- **Core problem (2024):** Turnover **22.4%** in specialized technicians → execution risk **2025–2027**.  
- **Opportunity:** Reduce talent loss, accelerate delivery, and unlock ROI through attraction/retention levers.  
**WHY:** Recurrent replacement costs and operational delays degrade reliability and ROI. *(Source: …)*

**3.2 Business Impact (with units)**  
- Impact level: **[value] [€ or $] per [period]**; **[value] [weeks]** delay per vacancy; **[pp]** hit to SLO.  
- **Formula example:** `Cost_of_Turnover_per_period = Exits × Replacement_Cost (€) + Output_Delay_Cost (€)`  
- **Baseline date:** [YYYY-MM-DD].  
**Source & Provenance:** *(Source: …)*

**3.3 Urgency & Timing**  
- Triggers/deadlines: [seasonality / compliance / contract windows] with dates.  
**WHY now:** Delaying increases expected loss and pushes risk across 2025–2027. *(Source: …)*

**3.4 Alternative Frames (if supported)**  
- Alt-Frame-1: [description] — **WHY rejected:** [reason], *(Source: …)*  
- Alt-Frame-2: [description] — **WHY rejected:** [reason], *(Source: …)*

---

## 4) Root-Cause & Driver Tree (Data-based)
**4.1 Driver Tree (Top → Leaf)**  
- Nested bullets; mark each node **Validated** or **Hypothesized**.  
For each node: **Signal(s)** (+ units) • **Evidence Strength** (H/M/L) • **WHY it matters** (mechanism to outcome) • *(Source: …)*

**4.2 Primary Causes (3–6) — Evidence Packs**  
For each cause: description & mechanism • quant signal (value + units + date) • qual signal (quote/theme) • counter-evidence/resolution • **WHY we believe it**.

**4.3 External/Systemic Factors**  
Market/regulatory/partner constraints with units/dates and **WHY**. *(Source: …)*

---

## 5) Strategic Objectives (SMART + WHY + Alternatives + Roadmap Alignment)
> **Mandated (do not rename/remove):**  
> **OBJ-1** Attraction strategies (≥3 viable) • **OBJ-2** Turnover ≤15% (with interim **≤18% by 31-Dec-2025** if roadmap cannot compress safely) • **OBJ-3** **ROI_12m ≥10%**.

### 5.1 Objectives Table (Primary, 3–5 total)
| ID    | Objective (verbatim)                           | Metric/Unit            | Baseline | Target                        | Deadline      | Owner    | Formula / Source | WHY | Alternatives Considered |
|-------|------------------------------------------------|------------------------|----------|-------------------------------|---------------|----------|------------------|-----|-------------------------|
| OBJ-1 | Identify attraction strategies (≥3 viable)     | # strategies           | 0        | ≥3                            | 2025-12-31    | HR Lead | — / *(Source: …)* | Diversify funnel & reach | [Alt target X] — rejected: [reason] |
| OBJ-2 | Reduce turnover                                | %                      | 22.4     | ≤15.0 (**interim ≤18% 2025-12-31**) | 2025-12-31 / 2026-03-31 | HR Lead | `Turnover% = Exits / Avg Headcount × 100` / *(Source: …)* | Execution stability & cost | [Alt ≤16%] — rejected: [reason] |
| OBJ-3 | Achieve ROI_12m                                | %                      | 0        | ≥10.0                         | 2025-12-31    | Finance | `ROI% = Net Benefit / Investment × 100` / *(Source: …)* | Sustainability | [Alt ≥8%] — rejected: [reason] |

> You may add up to **2** additional SMART objectives if supported by inputs. Do not alter the mandated ones.

**5.2 Objective-level Risks & Expected Loss**
| ID | Linked OBJ | Probability | Impact (€) | Expected Loss (€) | Early Signal | Mitigation | Owner | WHY |
|----|------------|------------:|-----------:|------------------:|--------------|------------|-------|-----|
| RISK-O1 | OBJ-2 | 0.5 | 500,000 | 250,000 | offer acceptance ↓ | add channels/branding | HR | Largest sensitivity driver |

**5.3 Prioritization (Must/Should/Could)**
| Objective ID | Impact (0–5) | Effort (0–5) | Time (0–5) | Risk (0–5) | Weighted Score | Rank | WHY |
|--------------|--------------:|--------------:|-----------:|-----------:|---------------:|-----:|-----|
| OBJ-2 | 5 | 3 | 3 | 4 |  — | — | Largest ROI path; criteria alignment |

---

## 6) Scope Definition (Explicit In/Out + WHY + Interfaces)
**6.1 In Scope**  
| ID | Item | Owner/Role | Ties to Objective(s) | WHY Included | Source |
|----|------|------------|----------------------|--------------|--------|
| SCOPE-IN-1 | [activity/system/segment] | [role] | OBJ-2 | [mechanism] | *(Source: …)* |

**6.2 Out of Scope**  
| ID | Item | WHY Excluded | Revisit Condition | Source |
|----|------|--------------|-------------------|--------|
| SCOPE-OUT-1 | [item] | [lack of ROI / sequence] | [date/event] | *(Source: …)* |

**6.3 Stakeholders & Roles (RACI-style)**  
| Role/Group | Responsible | Accountable | Consulted | Informed | Decision Rights | Escalation Path | Source |
|------------|-------------|-------------|-----------|---------|-----------------|-----------------|--------|

**6.4 Interfaces & Dependencies**  
| ID | System/Team | What’s Needed | Data Contract (fields/refresh) | By When | WHY Needed | Source |
|----|-------------|---------------|---------------------------------|--------|------------|--------|

---

## 7) Success Criteria & KPI System (Data-first + Operational Drivers + Bias Notes)
**7.1 Quantitative KPIs (3–5)**  
For each KPI-#: Definition & unit; **Formula**; data source/instrument; refresh cadence; owner; Baseline (value + date) or **TBD**; Target (value + date) with deadline & linked OBJ-#; Bias/sampling notes; **WHY**; Alternatives considered/rejected.

**7.2 Required Operational Drivers (include even if Baseline = TBD)**
| Driver                 | Unit  | Baseline | Target | Cadence  | Owner    | Formula / Source                      | WHY |
|------------------------|-------|---------:|-------:|----------|----------|----------------------------------------|-----|
| Time-to-Fill           | days  |   TBD    | ≤45    | Weekly   | HR Ops   | `CloseDate − OpenDate` / ATS *(…)*     | Hiring latency driver |
| Offer-Accept           | %     |   TBD    | ≥35    | Weekly   | HR Ops   | `Accepted / Offers × 100` *(…)*        | Funnel efficiency |
| Time-to-Productivity   | days  |   TBD    | ≤60    | Monthly  | L&D      | `TTV milestone date − Start date`      | Speed to value |
| Retention 90d          | %     |   TBD    | ≥80    | Monthly  | HR Lead  | `Active at 90d / Hires × 100`          | Early stickiness |
| Vacancy Coverage       | %     |   TBD    | ≥90    | Weekly   | HR Ops   | `Filled FTE / Required FTE × 100`      | Delivery capacity |

**7.3 Qualitative Indicators (2–4)**  
Method (survey/interviews), sample, threshold, cadence, **WHY meaningful**, *(Source: …)*

**7.4 Milestone Timeline**  
| Horizon | What Will Be True | Evidence (KPI/Indicator) | Owner | Date |
|---------|-------------------|---------------------------|-------|------|
| 0–3m    |                   |                           |       |      |
| 3–12m   |                   |                           |       |      |
| 12m+    |                   |                           |       |      |

---

## 8) Constraints, Assumptions, Dependencies (with Tests + WHY)
**8.1 Constraints**  
| ID | Type     | Limit/Unit | WHY Binding | Source |
|----|----------|------------|-------------|--------|
| CONSTR-1 | Budget | [€ amount] | governance/contract/compliance | *(Source: …)* |
| CONSTR-2 | Legal  | GDPR: Pass | gating (no trade-off)          | *(Source: …)* |

**8.2 Assumptions (Testable)**  
| ID | Statement | Risk if False | Test Plan (method/data/owner/ETA) | WHY Reasonable Now | Source |
|----|-----------|---------------|-----------------------------------|--------------------|--------|
| ASSUMP-1 | [text] | [impact] | [A/B, query, survey] / [owner] / [ETA] | [precedent/logic] | *(Source: …)* |

**8.3 Dependencies**  
| ID  | Type (Int/Ext/Seq) | What’s Needed | From Whom | By When | WHY | Source |
|-----|---------------------|---------------|-----------|--------|-----|--------|
| DEP-1 | Int               | [artifact]    | [team]    | [date] | [reason] | *(Source: …)* |

---

## 9) Risk & Mitigation (Definition-Phase, with €)
| ID    | Risk                                | Linked Section | Prob. | Impact (€) | **Expected Loss (€)** | Early Signal           | Mitigation                  | Owner | WHY Mitigation Works | Source |
|-------|-------------------------------------|----------------|------:|-----------:|----------------------:|------------------------|-----------------------------|------|----------------------|--------|
| RISK-1| Talent scarcity in key roles        | OBJ-2          | 0.5   | 500,000    | 250,000               | offer acceptance ↓     | channel mix + EVP uplift    | HR   | precedent [ref]      | *(…)* |
| RISK-2| GDPR non-compliance                 | CONSTR-2       | 0.2   | 300,000    | 60,000                | audit finding          | DPIA + controls             | Legal| regulatory evidence  | *(…)* |

> **Simulation flag:** Replacement cost for turnover will be modeled with a **triangular distribution** *(min, mode, max TBD in Simulate)*.

---

## 10) Governance & Change Control
- **Decision Authority (role-level):** scope, limits, approvals & SLAs.  
- **Criteria alignment:** confirm no contradictions vs locked criteria; if any, propose a **Change Request (CR)** with rationale.  
- **Change process:** triggers, submission format, review cycle, approval path, comms protocol.  
**WHY:** Balances speed and safety; preserves traceability to the lock.

---

## 11) Traceability & Provenance (Inputs → Outputs)
**11.1 Decision Traceability Table**  
| Output Decision/Claim | Exact Source Snippet (quote/figure) | Section Referenced | WHY This Source is Sufficient |
|---|---|---|---|
| “[…]” | “[…]” | Context §… / Feasibility §… | [reasoning] |

**11.2 Data Dictionary**  
| Metric/Field | Definition | Unit | Source System | Known Limitations/Bias |
|---|---|---|---|---|

---

## 12) Data Gaps & Collection Plan (for every **TBD**)
| Missing Data | WHY Needed | Collection Method | Owner | ETA | Acceptance Criteria |
|---|---|---|---|---|---|
|  |  | instrumentation/query/survey/experiment |  |  |  |

---

## 13) Temporal Alignment & Roadmap Consistency
- **Roadmap window:** [start date] → [end date] (weeks).  
- **If infeasible to hit ≤15% by 31-Dec-2025:** insert **interim milestone ≤18% by 31-Dec-2025**, final **≤15% by 31-Mar-2026**; justify sequencing and capacity implications.  
**WHY:** Maintains realism while preserving alignment to locked criteria and program gates.

---

## 14) Appendix (Calculations, Benchmarks, Sensitivities)
- **Formulas & Derivations:** ROI, turnover, driver conversions (with units).  
- **Benchmarks/Comparables:** sources, adjustments, and **WHY** applicable.  
- **Sensitivity Notes:** How results shift under plausible ranges; **WHY** this informs risk/target setting.

---

## Final Quality Gate (Do-Not-Skip Checklist)
- criteria_lock_hash_cited == **true**  
- mandated_objectives_present_and_unchanged (OBJ-1 ≥3 strategies; OBJ-2 ≤15% with interim ≤18%; OBJ-3 ROI_12m ≥10%) == **true**  
- objectives_smart_and_time_aligned_to_roadmap == **true**  
- operational_drivers_included (TTF, Offer-Accept, TtP, Retention90d, VacancyCoverage) == **true**  
- kpis_with_units_formulas_baseline_target_source_cadence_owner_bias_notes == **true**  
- constraints_assumptions_dependencies_with_tests_and_whys == **true**  
- risks_with_expected_loss_euro_and_mitigations == **true**  
- triangular_replacement_cost_model_flagged_for_simulate == **true**  
- alternatives_considered_for_targets_scope_kpis == **true**  
- all_TBDs_have_collection_plan == **true**  
- provenance_cues_for_material_claims == **true**
"""

        return Task(
            description=description,

            expected_output = """
            
# Strategic Problem Definition & Objectives — Full Evidence-Based Report

> **Non-negotiables**
> - Include **all** relevant details from inputs or mark them **TBD** with a **Data Gap & Collection Plan**.
> - For **every** number: include **units** and **exact source** *(Source: Context §… / Feasibility §…)*.
> - For **every** decision/claim: include a **Why** explaining the causal logic, trade-offs, and alternatives considered.
> - Prefer tables for clarity, traceability, and downstream automation.
> - Use **stable IDs**: OBJ-#, KPI-#, SCOPE-IN-#, SCOPE-OUT-#, CONSTR-#, ASSUMP-#, DEP-#, RISK-#.

---

## 0) Executive Orientation (What, Why, How)
- **Purpose:** What this document enables in decision-making and downstream planning/simulation/reporting.
- **Scope of Inputs Used:** List all sources (docs/datasets/stakeholder notes) with IDs, dates, and versions.
- **Method Overview:** 3–6 bullets (root-cause mapping, SMART decomposition, KPI definition, scope negotiation, risk surfacing).
- **Key Outcomes:** The most material findings (1–5 bullets) with pointers to sections.
- **Why This Matters:** One paragraph linking problem → impact → objectives → KPIs → governance.

---

## 1) Problem Statement (Full Context + Evidence)
**1.1 Core Problem / Opportunity (≤150 words)**  
Plain statement (no jargon).  
- **Why:** Short chain from observations → impact.  
- **Source:** *(Source: …)*

**1.2 Business Impact (with units)**  
- Current impact level: **[value] [units]** over **[period]**.  
- **Formula:** `[metric] = [var A] × [var B] − [var C]` (show input variables and units).  
- **Baseline date:** [YYYY-MM-DD].  
- **Source & Provenance:** *(Source: …)*

**1.3 Urgency & Timing**  
- Triggers/deadlines (seasonality, compliance, contract, etc.).  
- **Why now:** concise causal argument.  
- **Source:** *(Source: …)*

**1.4 Alternative Frames (if supported by inputs)**  
- Alt-Frame-1: [description] — **Why rejected:** [reason], *(Source: …)*  
- Alt-Frame-2: [description] — **Why rejected:** [reason], *(Source: …)*

---

## 2) Root-Cause & Driver Tree (Data-based)
**2.1 Driver Tree (Top → Leaf)**  
Nested bullets; mark each node **Validated** or **Hypothesized**. For each node:
- **Signal(s):** metric/observation + units *(Source: …)*  
- **Evidence Strength:** High / Medium / Low (justify briefly)  
- **Why It Matters:** mechanism from cause → outcome

**2.2 Primary Causes (3–6) — Evidence Packs**  
For each cause:
- Description & mechanism  
- **Quant signal:** [value + units + date] *(Source: …)*  
- **Qual signal:** short quote/theme *(Source: …)*  
- **Counter-evidence (if any):** [summary] and resolution  
- **Why we believe it:** brief reasoning path

**2.3 External/Systemic Factors**  
Market/regulatory/partner constraints with units, dates, and **Why** *(Source: …)*

---

## 3) Strategic Objectives (SMART + Why + Alternatives)
> Create **3–5 primary objectives**. Each must tie to drivers in §2 and be fully SMART.

### OBJ-1 — [Title]
- **Specific:** [domain, population, boundary] — **Why this scope:** [causal link to §2 / feasibility constraints] *(Source: …)*
- **Measurable:** **Metric name + unit + full formula**; **instrument/data source**; **owner/role**
- **Achievable:** capacity/budget/precedent *(Source: …)*
- **Relevant:** link to **Problem §1** and **Causes §2**
- **Time-bound:** [deadline/milestones with dates]
- **Baseline:** [value + units + date] *(Source: …)* or **TBD**
- **Target:** [value + units + date]  
  - **Why this target:** trade-offs (speed vs. risk vs. ROI), benchmarks *(Source: …)*
  - **Alternatives considered:** [target A/B] — **Why rejected:** [reason]

(Repeat for **OBJ-2… OBJ-N**)

**Secondary Objectives (optional; non-blocking):** OBJ-S-1… (shortened SMART, with **Why**)

**Prioritization Table (Must/Should/Could)**  
| Objective ID | Impact (0-5) | Effort (0-5) | Time (0-5) | Risk (0-5) | Weighted Score | Rank | Why |
|---|---:|---:|---:|---:|---:|---:|---|
| OBJ-1 |  |  |  |  |  |  | [brief rationale + Source] |
| OBJ-2 |  |  |  |  |  |  |  |
*(State **criteria weights** and the **Why** for the final ranking)*

---

## 4) Scope Definition (Explicit In/Out + Why)
**4.1 In Scope**  
| ID | Item | Owner/Role | Ties to Objective(s) | Why Included | Source |
|---|---|---|---|---|---|
| SCOPE-IN-1 |  |  |  | [mechanism or dependency] | *(Source: …)* |
| SCOPE-IN-2 |  |  |  |  |  |

**4.2 Out of Scope**  
| ID | Item | Why Excluded | Revisit Condition | Source |
|---|---|---|---|---|
| SCOPE-OUT-1 |  | [lack of ROI / dependency / sequence] | [date/event] | *(Source: …)* |

**4.3 Stakeholders & Roles (RACI-style)**  
| Role/Group | Responsible | Accountable | Consulted | Informed | Decision Rights | Escalation Path | Source |
|---|---|---|---|---|---|---|---|

**4.4 Interfaces & Dependencies**  
| ID | System/Team | What’s Needed | Data Contract (fields/refresh) | By When | Why Needed | Source |
|---|---|---|---|---|---|---|

---

## 5) Success Criteria & KPI System (Data-first + Why)
**5.1 Quantitative KPIs (3–5)**  
For each **KPI-#**:
- **Definition & Unit:** [metric] ([unit]); directionality (↑ good / ↓ good)
- **Formula:** `[metric] = …` (full; name all fields)
- **Data Source & Instrumentation:** [system/table/dashboard], refresh cadence, owner/role
- **Baseline:** [value + units + date] *(Source: …)* or **TBD**
- **Target & Deadline:** [value + units + date]; linked **OBJ-#**
- **Bias/Sampling Notes:** [risk + mitigation]
- **Why this KPI:** causal link to drivers/outcomes *(Source: …)*
- **Alternatives considered:** [metric A/B] — **Why rejected**

**5.2 Qualitative Indicators (2–4)**  
Method (survey/interviews/reviews), sample, threshold, cadence, **Why meaningful**, *(Source: …)*

**5.3 Milestone Timeline**  
| Horizon | What Will Be True | Evidence (KPI/Indicator) | Owner | Date |
|---|---|---|---|---|
| 0–3m |  |  |  |  |
| 3–12m |  |  |  |  |
| 12m+ |  |  |  |  |

---

## 6) Constraints, Assumptions, Dependencies (with Tests + Why)
**6.1 Constraints**  
| ID | Type | Limit/Unit | Why Binding | Source |
|---|---|---|---|---|
| CONSTR-1 | Budget | [€/$ amount] | [governance/contract/compliance] | *(Source: …)* |

**6.2 Assumptions (Testable)**  
| ID | Statement | Risk if False | Test Plan (method/data/owner/ETA) | Why Reasonable Now | Source |
|---|---|---|---|---|---|
| ASSUMP-1 |  |  |  |  | *(Source: …)* |

**6.3 Dependencies**  
| ID | Internal/External/Sequential | What’s Needed | From Whom | By When | Why | Source |
|---|---|---|---|---|---|---|
| DEP-1 |  |  |  |  |  |  |

---

## 7) Risks & Mitigations (Definition-Phase)
| ID | Risk | Linked Section (OBJ/Scope/KPI) | Prob. | Impact | Early Signal | Mitigation | Owner | Why Mitigation Works | Source |
|---|---|---|---|---|---|---|---|---|---|
| RISK-1 |  |  | L/M/H | L/M/H |  |  |  | [precedent/evidence] | *(Source: …)* |

*(List alternative mitigations considered, if applicable, with brief **Why rejected**.)*

---

## 8) Governance & Change Control
- **Decision Authority (Role-level):** scope of authority, limits *(Source: …)* — **Why fit-for-purpose**
- **Approvals & SLAs:** committees/roles, response windows
- **Change Process:** triggers, submission format, review cycle, approval path, comms protocol — **Why this balances speed/safety**

---

## 9) Traceability & Provenance (Inputs → Outputs)
**9.1 Decision Traceability Table**  
| Output Decision/Claim | Exact Source Snippet (quote or figure) | Section Referenced | Why This Source is Sufficient |
|---|---|---|---|
| “[…]” | “[…]” | Context §… / Feasibility §… | [reasoning] |

**9.2 Data Dictionary**  
| Metric/Field | Definition | Unit | Source System | Known Limitations/Bias |
|---|---|---|---|---|

---

## 10) Data Gaps & Collection Plan (for **every** TBD)
| Missing Data | Why Needed | Collection Method | Owner | ETA | Acceptance Criteria |
|---|---|---|---|---|---|
|  |  | Instrumentation/query/survey |  |  |  |

---

## 11) Appendix (Calculations, Benchmarks, Sensitivities)
- **Formulas & Derivations:** Show the math (ROI, targets, conversions) with units.
- **Benchmarks/Comparables:** Sources, adjustments, and **Why** applicable.
- **Sensitivity Notes:** How results shift under plausible ranges; **Why** this informs risk/target setting.

---

### Final Quality Gate (Do-Not-Skip Checklist)
- Every number has **units** and **source**; every decision has a **Why** tied to **data** (or explicit assumption + test plan).
- Objectives are **fully SMART**, mapped to **root causes**, with **baselines/targets/dates**.
- Scope inclusions/exclusions are explicit and justified; interfaces & dependencies are clear and necessary.
- KPIs have **formula, source, owner, cadence, bias notes** (or **TBD** + collection plan).
- Prioritization and **alternatives considered** are documented with rationale.
- All **TBDs** appear in §10 with owner, ETA, and acceptance criteria.
- No invented facts. No repetition. No dangling claims without provenance.

"""

,
            agent=DefineAgent.create_agent(),
            markdown=True,
            output_file="problem_definition.md",
        )