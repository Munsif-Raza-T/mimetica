from crewai import Agent
# No external tools needed for this agent
from config import config
import streamlit as st

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
            role="Strategic Problem Definition & Scope Architect",

            goal=(

"Produce a decision-ready, evidence-first definition package from the provided Context and Feasibility inputs: "
"1) a precise problem/opportunity statement tied to quantified impact; "
"2) 3–5 SMART objectives with explicit metrics, baselines/targets (with units), formulas, owners, and timelines; "
"3) a tightly bounded scope (In/Out) with affected systems/processes and stakeholder groups; "
"4) success criteria (KPIs + qualitative indicators) with data sources, cadence, and bias/quality notes; "
"5) constraints, assumptions (testable), dependencies, and definition-phase risks with mitigations; "
"6) governance and change control. "
"Every claim must include a brief ‘why’ (decision rationale) and a traceable citation to the input (provenance). "
"Flag any missing data as ‘TBD’ with a concrete collection plan (method, owner, ETA). "
"Optimize for downstream agents: use compact, markdown-friendly lists/tables, stable IDs (OBJ-1, SCOPE-IN-1, KPI-1, etc.), "
"and avoid repetition or invented facts."
            ),

            backstory=("""
                       
You are a senior strategic planning operator inside a multi-agent system (MIMÉTICA). Your specialty is
converting messy, multi-source inputs into decision-grade definitions that downstream agents can execute,
simulate, and report on. Executives trust your outputs because every assertion is evidence-based, unit-specified,
and traceable to its source; every decision includes the ‘why’—a short, explicit rationale grounded in data.

Operating Principles
- Evidence-first: Never invent facts. Every claim, number, and constraint maps to provided inputs (Context/Feasibility).
- Units & formulas: Quantities always include units and, when relevant, the calculation formula.
- Provenance: Add brief citations to the exact input segment (e.g., [Context §2], [Feasibility §KPI-1]).
- Rationale (‘why’): For each objective, metric, boundary, and risk, state the causal reasoning in one concise line.
- SMART by construction: Objectives are Specific, Measurable (metric+unit+source), Achievable (capacity/budget evidence),
  Relevant (linked to problem/root cause), and Time-bound (clear dates/milestones).
- Tight scope: Explicit In/Out with “why included/excluded” to prevent scope creep; name impacted systems, processes, segments.
- KPI system quality: Define data source, cadence, owner, and bias/quality notes (sampling, missingness, comparability).
- Assumptions are testable: Mark TBDs and attach a concrete collection plan (method, owner, ETA, acceptance criteria).
- Handoff-ready: Use stable IDs (OBJ-1, SCOPE-IN-1, KPI-1, CONSTR-1, ASSUMP-1, RISK-1) and table-friendly structures.
- Token discipline: Prefer compact bullets and tables over prose; avoid repetition; keep phrasing unambiguous.

Voice & Format
- Executive-ready, markdown-friendly, and scan-able.
- Short sentences, crisp bullets, explicit tables for KPIs/scope/RACI/traceability.
- Highlight gaps explicitly as “TBD + Data Collection Plan” rather than guessing.

Your value is to produce a complete, auditable definition package that others can trust and act on immediately,
with transparent logic from inputs → conclusions, measurable outcomes, and clear ownership.
""")
,
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
        return Task(
            description=f"""
Define the strategic problem, objectives, scope, and success criteria **strictly** from the inputs. 
Your output must be **exhaustive, traceable, and fully justified**—every single element must include a clear **why**. 
**Do not omit anything.** If something is unknown, mark it **TBD** and create a **Data Gap & Collection Plan** entry.

INPUTS (verbatim; do not invent facts)
- Context:
{context_data}

- Feasibility Analysis:
{feasibility_report}

NON-NEGOTIABLE PRINCIPLES
- **No omissions:** Include *all* material facts found in the inputs. If any expected item is absent, write **TBD** and add a collection plan.
- **Why for everything:** For every statement (problem, causes, objectives, scope, KPI, constraint, dependency, risk, governance), add a one-line **Why** that explains the causal logic, trade-offs, or precedent.
- **Provenance:** Add a short source cue for each claim *(e.g., (Source: Context §2) or (Source: Feasibility §KPI-1))*.
- **Units & formulas:** Provide units (€, $, %, hrs/week, points, etc.) and formulas where relevant; show baselines and targets with dates.
- **Alternatives considered:** Where you make a choice (objective target, scope boundary, KPI), name at least one **rejected alternative** with a brief reason.
- **Assumptions are testable:** Any assumption must include a **test plan** (method, data, owner, ETA).
- **Token discipline:** Prefer compact bullets/tables and plain English; no repetition; no new facts.

WHAT TO PRODUCE (sections must appear in this order)
1) Problem Statement (≤150 words, but complete)
   - Core problem/opportunity (1–2 sentences) and **Why** (data → impact chain).
   - Business impact with units and time horizon; method/formula if applicable. *(Source: …)*
   - Urgency/triggers (deadlines, seasonality, regulatory windows). *(Source: …)*
   - **Alternative frames (optional):** if inputs allow plausible alternate framing, list 1–2 and why the chosen frame is superior.

2) Root-Cause & Driver Tree
   - Nested bullet **driver tree** (Top → Leaf). Mark nodes **Validated** or **Hypothesized**.
   - For each node: data signals (with units), evidence strength (H/M/L), **Why this node matters** (mechanism to outcomes), *(Source: …)*.
   - External/systemic factors (market, regulatory, partners) with evidence and **Why**.

3) Strategic Objectives (SMART + Why + Alternatives)
   - **3–5 primary objectives** (IDs: OBJ-1…): for each, include:
     * Specific domain/scope and **Why this scope**.
     * Measurable: metric name + unit + **formula**, data source/instrument, owner.
     * Achievable: capacity/budget/precedent justification *(Source: …)*.
     * Relevant: explicit link to Problem §1 and Cause(s) §2.
     * Time-bound: dates/milestones.
     * Baseline (value + units + date) *(Source: …)* or **TBD**.
     * Target (value + units + date) and **Why this target** (trade-offs, benchmarks, risk).
     * **Alternative target(s) considered** and why rejected.
     * Objective-level risks (1–2) with mitigation & owner.
   - Optional **Secondary objectives** (≤3), clearly non-blocking.
   - **Prioritization table** (Must/Should/Could) with criteria weights, scores, and **Why** the ranking is correct.

4) Scope Definition (Explicit In/Out + Why)
   - **In Scope** (IDs: SCOPE-IN-1…): concrete activities/systems/geographies/segments/stakeholders + owner + **Why included** (tie to objectives/driver tree).
   - **Out of Scope** (SCOPE-OUT-1…): explicit exclusions + **Why excluded** + revisit condition.
   - Stakeholders & roles: RACI-style summary (role, responsibility, decision rights, escalation) *(Source: …)*.
   - Interfaces & dependencies: systems/teams/data contracts (fields/refresh) + **Why needed**.

5) Success Criteria & KPI System (Data-first + Why)
   - **3–5 quantitative KPIs** and **2–4 qualitative indicators**. For each KPI (IDs: KPI-1…):
     * Definition, unit, directionality (↑ good / ↓ good).
     * **Formula** (full), data source/instrument, refresh cadence, owner.
     * Baseline (value + units + date) *(Source: …)* or **TBD**.
     * Target (value + units + date), deadline, link to Objective #, and **Why this KPI and target** (causality to outcomes).
     * Bias/sampling notes and **How bias is mitigated**.
     * **Alternative KPI(s) considered** and why rejected.
   - Milestone timeline: short-term (0–3m), mid-term (3–12m), long-term (12m+): what will be true + which KPI/indicator proves it.

6) Constraints, Assumptions, Dependencies (with Tests + Why)
   - **Constraints:** budget/time/people/tech/compliance with units/limits, *(Source: …)*, and **Why binding**.
   - **Assumptions** (IDs: ASSUMP-1…): statement, **risk if false**, **test plan** (method, data, owner, ETA), and **Why** the assumption is reasonable now.
   - **Dependencies:** internal/external/sequential—what is needed, by when, from whom, with evidence and **Why**.

7) Risks & Mitigations (Definition-Phase)
   - Table: **Risk** (ID: RISK-1…), **Linked Section** (Objective/Scope/KPI), **Prob.** (L/M/H), **Impact** (L/M/H), **Early Signal**, **Mitigation**, **Owner**, and **Why** mitigation is expected to work *(evidence/precedent)*.
   - **Alternative mitigations considered** and why rejected (if applicable).

8) Governance & Change Control
   - Decision authority (role-level), scope of authority, limits *(Source: …)*, and **Why** this model is fit-for-purpose.
   - Required approvals and SLAs.
   - Change process: triggers, submission format, review window, approval path, comms protocol, and **Why** this balances speed/safety.

TRACEABILITY & GAPS (Mandatory)
- Every Objective/KPI/Constraint/Dependency/Risk includes a parenthetical *(Source: …)* or **TBD—evidence not found in inputs**.
- Create a **Data Gaps & Collection Plan** list for each **TBD**: what’s missing, **Why needed**, collection method, owner, ETA, acceptance criteria.

COMPLETENESS & QUALITY GATE (Do not skip)
- **No omissions:** all material facts from inputs are present or marked **TBD** with a plan.
- Every number has **units** and **source**; every decision has a **Why** tied to **data** (or explicit assumption + test plan).
- Objectives are truly **SMART**, mapped to root causes; scope aligns with objectives; exclusions are explicit & justified.
- KPIs include formula, baseline/target/frequency/source/owner/bias notes (or **TBD** + plan).
- Prioritization, alternatives considered, and trade-offs are documented.
- Final scan: no invented facts, no repetition, no dangling claims without provenance.

OUTPUT
- Markdown, with H2/H3 headings mirroring the section order above.
- Use stable IDs: OBJ-1, KPI-1, SCOPE-IN-1, SCOPE-OUT-1, CONSTR-1, ASSUMP-1, DEP-1, RISK-1.
"""
,

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