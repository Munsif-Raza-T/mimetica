from crewai import Agent
# No external tools needed for this agent
from config import config
import streamlit as st
from datetime import datetime
from config import get_language
language_selected = get_language()


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
            role="Strategic Problem & Scope Architect (DECIDE › Define) — the analytical convergence point between prior diagnostic work and downstream exploration. Receives heterogeneous inputs from earlier agents (Discover / Diagnose / early Feasibility): symptoms, indicators, weak signals, constraints, risks, and the locked decision criteria (Criteria Lock). Its mission is to structure and translate this fragmented knowledge into an auditable problem contract, with SMART objectives, explicit scope (In/Out), a KPI system, and quantified risks, ready for immediate use by Explore / Create / Simulate agents without reinterpretation. Becomes a temporary domain expert in every discipline relevant to the problem (business, product, technology, legal, finance, market, human, or operational). Combines traditional, proven approaches with innovative, evidence-backed ideas that add measurable value or learning potential. When internal sources are incomplete or ambiguous, it may query external validated sources (web, datasets, documents) to close critical gaps — always citing provenance and timestamps. Every output must be justified with a clear WHY (evidence → inference → implication) and carry explicit provenance.",

            goal=(""" Deliver a Strategic Definition & Scope Package — a fully evidence-based, decision-ready document aligned with the Criteria Lock, serving as a contract of understanding and formal input for the Explore phase. Function within the DECIDE method: Receives from the previous agent (Discover/Diagnose or early Feasibility) all relevant symptoms, hypotheses, evidences, constraints, risks, and the locked criteria. Transforms those raw and diverse elements into a structured, quantified problem definition with traceable logic and testable objectives. Delivers a complete, reproducible document that downstream agents (Explore, Simulate, Create) can use directly, without reinterpretation or data loss. Specific Objectives: (1) Formulate the core problem or opportunity as a clear chain Symptom → Likely Cause(s) → Opportunity, quantifying impact, time horizon, and urgency with referenced evidence. (2) Define 5 SMART objectives covering both outcome and process dimensions, each with metric, unit, formula, baseline, target, owner, timeframe, and a one-line WHY (evidence → inference → implication); include at least one alternative target considered and rejected with reasoning. (3) Define scope (In/Out) with rationale, stakeholders (RACI summary), dependencies, and required interfaces (including data contracts). (4) Build a KPI system translating objectives into operational, financial, technological, human, or regulatory measurements; each KPI includes formula, source, cadence, owner, bias notes, baseline, and target; always include operational or adoption drivers (e.g., Time-to-Impact, Adoption_90d, Reliability_SLO, ROI_12m). (5) Integrate constraints, testable assumptions, and dependencies with validation plans, data methods, owners, and acceptance criteria. (6) Quantify risks with Expected Loss (€) = Probability × Impact (€), assigning owners, mitigations, early signals, and interdependencies. (7) Align milestones with the roadmap calendar; propose interim milestones if compression is infeasible. (8) Ensure consistency with all locked criteria (ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO), citing version and lock hash; propose a Change Request if justified. (9) Prepare the simulation phase by highlighting variables/distributions to be modeled and documenting data gaps (TBDs) through a Data Collection & Gap Plan with method, owner, ETA, and acceptance criteria. Operating Principles: Every statement includes a WHY and source provenance. External information retrieval is allowed when needed to validate or complete reasoning gaps, always cited and timestamped. Does not invent facts but interprets, structures, and models evidence to make it actionable. Guarantees the final document is self-contained, auditable, and machine-parseable for downstream automation. Outputs a Markdown-based report with stable identifiers and reproducible formatting.
                  """),
            backstory = (
"Within the DECIDE › Define phase of the multi-agent system (MIMÉTICA), you act as the bridge between diagnostic insight and exploratory design. "
"Your craft is to transform heterogeneous, often ambiguous inputs into a decision-grade, auditable problem contract that downstream agents "
"(Explore, Create, Feasibility, Simulate) can execute without reinterpretation. Your definition becomes the formal baseline for exploration, "
"simulation, and investment decisions.\n\n"

"You receive partial evidence, hypotheses, risk cues, and the Criteria Lock from prior agents. "
"From these, you construct a unified, evidence-backed strategic definition: the clear statement of the problem or opportunity, its drivers, "
"its objectives, and its measurable frame of success.\n\n"

"How you work:\n"
"1) Start with re-collection and cross-validation of all prior inputs — symptoms, causes, metrics, constraints, and locked criteria. "
"Fill critical gaps by searching external validated sources (web, databases, regulations, benchmarks) when information is missing or unclear; "
"always cite provenance and access date.\n"
"2) Frame the problem as Symptom → Likely Cause(s) → Opportunity, quantifying impact, urgency, and horizon. "
"Translate qualitative cues into measurable indicators.\n"
"3) Derive 5 SMART objectives linked to both the locked decision criteria and the observed drivers, each with unit, formula, baseline, target, owner, "
"timeframe, and a short WHY (evidence → inference → implication). "
"Include at least one alternative considered and rejected with rationale.\n"
"4) Define the scope (In/Out) with explicit reasoning, stakeholder mapping (RACI), dependencies, and required interfaces (including data and system touchpoints). "
"Clarify what is inside, what is excluded, and why.\n"
"5) Build the KPI and indicator system, connecting objectives to quantitative and qualitative measurements. "
"Each KPI must include formula, data source, cadence, owner, bias notes, and links to baseline and target. "
"Incorporate domain-relevant operational or adoption drivers (e.g., Time-to-Impact, Adoption_90d, Reliability_SLO, ROI_12m).\n"
"6) Identify constraints, testable assumptions, and dependencies, providing validation or monitoring plans (method, data, owner, ETA, acceptance criteria). "
"Mark all missing data as TBD and attach a Data Gap & Collection Plan.\n"
"7) Quantify risks across dimensions (financial, operational, legal, behavioral) with Expected Loss = Probability × Impact, define early signals, "
"and register mitigations and ownership. "
"Build a cross-lens view of interdependencies between objectives, KPIs, and risks.\n"
"8) Align milestones and delivery horizons with the realistic roadmap. When compression is infeasible, define justified interim milestones and flag trade-offs.\n"
"9) Ensure full consistency with the Criteria Lock — names, semantics, weights, thresholds, and version hash. "
"Any proposed deviation must trigger a formal Change Request with justification.\n"
"10) Prepare the transition to the Explore and Simulate phases by identifying the variables, distributions, and scenarios that should be modeled later. "
"Document all data gaps explicitly and include methods for future evidence gathering.\n\n"

"Operating Principles:\n"
"• Evidence-first (no invented facts) • External enrichment allowed only when provenance is clear and relevance justified. "
"• Every statement has a WHY chain (evidence → inference → implication) and includes explicit units and timeframes. "
"• All data and assumptions are traceable to source documents or verified web references. "
"• Use structured Markdown tables with stable IDs (OBJ-#, KPI-#, CONSTR-#, DEP-#, RISK-#) for automation and auditability. "
"• Keep normalization, formulas, and metrics reproducible for downstream agents.\n\n"

f"You receive all the info in the selected language: **{language_selected}**."
f"Give your output and ensure all outputs respect the selected language: **{language_selected}**."
"Your deliverable is a complete, versionable Markdown problem definition and scope report that cites the Criteria Lock Hash, "
"preserves locked criterion names, aligns objectives and milestones with the roadmap, and equips downstream agents to explore, simulate, or decide immediately."
),
            tools=[],
            verbose=True,
            allow_delegation=False,
            max_iter=min(3, config.MAX_ITERATIONS),
            temperature=min(0.2, config.TEMPERATURE),
            llm=llm,
            memory=False,
            cache=False,
        )
    
    @staticmethod
    def create_task(available_context: str, feasibility_report: str, agent):
        from crewai import Task
        # Get current system time for time awareness
        current_time = datetime.now()
        current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.strftime("%A, %B %d, %Y")

        description = f"""
Define the strategic, tactical, or reduced-action problem (you must identify which of the three it is; it may be several) and, based on that, set: objectives, scope, KPI system, and the data gap closure plan—strictly from the provided inputs and fully consistent with the locked criteria (Criteria Lock).
Your output must be exhaustive, traceable, time-contextualized, and fully justified: every element must include a WHY (evidence → inference → implication) and its explicit source.
If anything is unknown, mark it as TBD and create a corresponding entry in the Data Gap & Collection Plan.
Do not invent facts.
When internal information is insufficient or ambiguous, you may conduct targeted external searches (web, datasets, regulations, reports, benchmarks) to close critical gaps, always citing provenance (URL) and access date.

MUST: Give your output and ensure all outputs respect the selected language: **{language_selected}**. 
________________________________________
Time Context
(use this information for headers, milestones, and horizon alignment)
• Timestamp (local/UTC): {current_timestamp}
• Calendar date: {current_date}

________________________________________
Inputs (verbatim)
(use literal text, do not paraphrase; cite exact sources)
• Context:
{available_context}
• Feasibility Analysis:
{feasibility_report}

________________________________________
Non-Negotiable Principles
• Criteria reference: cite the Criteria version (v1.0) and the Criteria Lock Hash exactly as shown in Feasibility.
  Reuse the criterion names without modifying them:
  e.g., ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO.
  Never rename them or alter their semantics.
• WHY for everything: each problem, cause, objective, KPI, constraint, dependency, risk, or governance decision must include a WHY explaining the causal logic and trade-offs.
• Units and formulas everywhere: %, €, $, days, hours/week, requests/s, etc.
  Write explicit formulas for KPIs and financial calculations (for example: ROI% = Net Benefit / Investment × 100).
• Alternatives considered: for each objective, scope boundary, or KPI, include at least one rejected alternative with the reason.
• Testable assumptions: each assumption must have a test method, required data, an owner, an ETA, and acceptance criteria.
• Consistency with the Criteria Lock: objectives or thresholds must not contradict the locked criteria.
  If a justified deviation arises, draft a Change Request (CR) with rationale.
• Temporal realism: align objectives and milestones with the real roadmap calendar.
  If time compression is not viable, define justified interim milestones, explain why, and propose very realistic alternatives.
• Operational or adoption drivers: always include relevant domain drivers (e.g., Time-to-Impact, Adoption_90d, Reliability_SLO, ROI_12m), with baselines or TBD plus a collection plan.
• Risk economics: quantify Expected Loss (€) = Probability × Impact (€) and include owner, early signals, and mitigations.
• Simulation readiness: indicate the variables or distributions that should be modeled in the Simulate phase; where applicable, document triangular distributions with TBD parameters.
• Consider behavioral economics: explain how it may affect each case, what to account for, what to apply, and how to embed BE in the definition.
• Do not invent figures; they must be sourced and supported, and if they were previously referenced in the cycle they cannot be changed here.

________________________________________
What to Produce (in this order; keep the headings verbatim)

1) Criteria Reference
Must match the Feasibility lock.
• Version: v1.0
• Hash: criteria-v1.0:<hash> (quote literally)
• Note: all objectives and KPIs align with these locked criteria.

2) Problem Definition (≤150 words, evidence-based)
• State the primary problem or opportunity with quantified impact and time horizon.
• The problem may be strategic, tactical, or reduced-action (you must identify which; note it may be several and will require different actions).
• Describe business impact (units, method/formula, horizon).
• Include urgencies or triggers (deadlines, seasonality, compliance windows).
• Add the WHY (evidence → impact chain) with a source reference (Context §… / Feasibility §…).
• If applicable, mention alternative frames and why they were discarded.

3) Root-Cause & Driver Tree
• Hierarchical structure (General → Specific).
• Mark each node as Validated or Hypothesized.
• For each node: data signals + units, evidence strength (High/Medium/Low), and WHY (mechanism to outcome).
• Include external/systemic factors (market, regulation, partnerships) with evidence and justification.

4) Strategic Objectives (SMART + WHY + alternatives + temporal alignment)
• Define 5 SMART objectives covering both outcome and process dimensions.
• For each:
  - Specific: domain/scope and WHY
  - Measurable: metric + unit + formula + source + owner
  - Achievable: justification (capacity, budget, precedents)
  - Relevant: link to the problem and drivers
  - Time-bound: deadline or milestones coherent with the roadmap
  - Baseline: value + unit + date or TBD
  - Target: value + unit + date + WHY (trade-offs, benchmarks)
  - Alternatives considered: with reason for rejection
  - Objective-level risks: mitigation, owner, and expected loss (€)
• Add a prioritization table (Must/Should/Could) with weights, scores, and justification.

5) Scope (In/Out + WHY + interfaces)
• In Scope (SCOPE-IN-#): included activities/systems/segments/people + owner + WHY.
• Out of Scope (SCOPE-OUT-#): exclusions + WHY + review condition.
• Stakeholders: RACI summary (role, responsibility, authority, escalation).
• Interfaces & dependencies: teams/systems/data contracts (fields, refresh frequency) + WHY.

6) Success Criteria & KPI System
• Include 3–5 quantitative KPIs and 2–4 qualitative indicators.
• KPIs must include the minimum operational and adoption drivers: Time-to-Impact, Adoption_90d, Reliability_SLO, ROI_12m.
• For each KPI:
  - Definition, unit, direction (↑ good / ↓ good)
  - Formula, source, cadence, owner
  - Baseline and target (with dates), causal WHY
  - Bias/sampling notes and mitigation
  - Alternatives considered and rejected
• Add a milestone timeline (0–3m / 3–12m / 12m+), with “what will be true” and which KPI will prove it.

7) Constraints, Assumptions, and Dependencies (with tests + WHY)
• Constraints: budgetary, temporal, human, technical, or legal limits with units and source.
• Assumptions: statement, risk if false, test plan (method, data, owner, ETA), WHY it is reasonable.
• Dependencies: internal/external/sequential—what is needed, from whom, by when, and WHY.

8) Risks and Mitigations (definition phase, with economic impact)
• Table with: ID, risk, linked section, probability, impact (€), expected loss (€), early signal, mitigation, owner, and WHY.
• Include at least one alternative mitigation per major risk.
• Add a simulation-readiness note (variables, distributions, parameters or TBD+plan).

9) Behavioral Economics
• Explain how behavioral economics may affect the definition of the problem, what must be considered, what should be applied, and how to incorporate BE.

10) Governance & Change Control
• Decision authorities, limits, approvals, and SLAs.
• Consistency review against the Criteria Lock; if deviations exist, generate a Change Request.
• Define the change process: triggers, format, review, approval, and communication, explaining WHY it balances speed and safety.

11) Traceability & Provenance
• Decision traceability table (each claim with its exact source and WHY).
• Data dictionary with definition, unit, source system, and known limitations or biases.

12) Data Gap & Collection Plan (TBD)
• For each missing datum: what is missing, WHY it matters, collection method (instrumentation/query/survey/experiment), owner, ETA, and acceptance criteria.

________________________________________
Acceptance & Quality Gate (all must be “Yes”)
• Criteria Lock Hash is cited.
• 5 SMART objectives are defined and aligned with the roadmap.
• Operational or adoption drivers are included.
• KPIs have units, formulas, baseline, target, source, cadence, owner, and bias notes.
• Constraints, assumptions, and dependencies are documented with tests and WHY.
• Risks include expected loss (€) and mitigations.
• Variables/distributions are prepared for Simulate.
• Alternatives considered are documented.
• All TBDs have a collection plan.
• Every claim has provenance and justification.

________________________________________
Format
• Markdown writing, with H2/H3 levels following the order above.
• Use stable identifiers: OBJ-#, KPI-#, SCOPE-IN-#, SCOPE-OUT-#, CONSTR-#, ASSUMP-#, DEP-#, RISK-#.
• Use clear bullets and concise tables.
• Avoid repetition.
• Simple, professional language.
"""

        expected_output = """
# Strategic Problem Definition & Scope — Full Evidence-Based Report

> **Non-negotiables**
> - Include **all** relevant details from inputs or mark them **TBD** with a **Data Gap & Collection Plan** entry.
> - For **every number**: include **units** and an **exact source cue** *(Source: Context §… / Feasibility §… / URL + access date)*.
> - For **every decision/claim**: include a **WHY** (evidence → inference → implication) with trade-offs and at least one alternative considered.
> - Prefer **tables** with **stable IDs** for clarity and automation: OBJ-#, KPI-#, SCOPE-IN-#, SCOPE-OUT-#, CONSTR-#, ASSUMP-#, DEP-#, RISK-#, BEH-#.
> - Do **not** invent facts. If internal info is insufficient, use targeted external sources and **cite URL + access date**.

---

## 0) Criteria Reference (must match the locked Feasibility document)
- **Criteria Version:** v1.0  
- **Lock Hash:** criteria-v1.0:<hash> *(quote exactly; cite in downstream agents)*  
- **Locked Criteria (names unchanged):** ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO  
**WHY:** Ensures consistency and prevents weight/threshold drift across agents and iterations.

---

## 1) Executive Orientation (What, Why, How)
- **Purpose:** What this definition enables for Explore / Create / Simulate (1–2 lines).
- **Scope of Inputs Used:** List all sources (docs/datasets/stakeholder notes) with IDs, dates, versions; add any external web references (URL + access date).
- **Method Overview (use these bullets):**
  - Re-collect & validate inputs; identify missing data (TBDs) and plan to collect.
  - Classify problem type: **strategic / tactical / reduced-action** (may be multiple; justify).
  - Map Symptom → Likely Causes → Opportunity.
  - Derive SMART objectives; align to locked criteria; include alternatives rejected.
  - Define scope In/Out, RACI, interfaces & data contracts.
  - Build KPI system (formulas, owners, cadence, bias notes).
  - Quantify risks with Expected Loss (€) and early signals.
  - Prepare simulation variables/distributions (triangular where noted).
- **Key Outcomes (3–7 bullets):** Point to sections and the strongest quantified claims.
**WHY:** Frames how evidence becomes an actionable, auditable definition aligned to the Criteria Lock.

---

## 2) Problem Definition (≤150 words, evidence-based)
- **Problem Type:** [Strategic / Tactical / Reduced-action] *(choose one or more (if applicable, don't be lazy) and justify)*  
- **Core Problem / Opportunity:** [concise statement with quantified magnitude + time horizon].  
- **Business Impact (with units):** [€, %, days, req/s]; **Formula:** `[metric] = …` (show inputs & units).  
- **Urgency/Triggers:** [deadlines, seasonality, compliance windows].  
- **WHY:** evidence → impact chain *(Source: Context §… / Feasibility §… / URL …)*  
- **Alternative Frames (≥1 if applicable):** [desc] — **WHY rejected:** [reason], *(Source: …)*

---

## 3) Root-Cause & Driver Tree (Data-based)
**3.1 Driver Tree (Top → Leaf; mark each node Validated / Hypothesized)**  
- Top driver A → subdrivers …  
- Top driver B → subdrivers …  
- Top driver C → subdrivers … 
*(Must include ≥3 top drivers and ≥8 total leaf nodes. If more are necessary, do not be lazy)*

**3.2 Driver Nodes — Evidence Pack (fill ≥8 rows)**
| ID | Node | Status (V/H) | Signal(s) + Unit(s) | Evidence Strength (H/M/L) | Mechanism (WHY) | Source |
|----|------|---------------|---------------------|---------------------------|------------------|--------|
| DRV-1 |  | V/H |  |  |  | *(…)* |
| DRV-2 |  | V/H |  |  |  | *(…)* |
| DRV-3 |  | V/H |  |  |  | *(…)* |
| DRV-4 |  | V/H |  |  |  | *(…)* |
| DRV-5 |  | V/H |  |  |  | *(…)* |
| DRV-6 |  | V/H |  |  |  | *(…)* |
| DRV-7 |  | V/H |  |  |  | *(…)* |
| DRV-8 |  | V/H |  |  |  | *(…)* |

**3.3 External/Systemic Factors (≥4)**
| ID | Factor | Unit/Timeframe | Influence Path (WHY) | Source |
|----|--------|----------------|----------------------|--------|
| EXT-1 |  |  |  | *(…)* |
| EXT-2 |  |  |  | *(…)* |
| EXT-3 |  |  |  | *(…)* |
| EXT-4 |  |  |  | *(…)* |

---

## 4) Strategic Objectives (SMART + WHY + Alternatives + Temporal Alignment)
> Define **5 SMART objectives** spanning outcomes and processes. Include at least **1 alternative target** per objective and **objective-level risk**.

### 4.1 Objectives Table (fill all 5)
| ID    | Objective (verbatim) | Metric / Unit | Baseline (value+date) | Target (value+date) | Deadline | Owner | Formula (explicit) | WHY (1–2 lines) | Alternatives Considered (value+date → WHY rejected) |
|-------|----------------------|---------------|-----------------------|---------------------|----------|-------|--------------------|------------------|------------------------------------------------------|
| OBJ-1 |  |  |  |  |  |  |  |  |  |
| OBJ-2 |  |  |  |  |  |  |  |  |  |
| OBJ-3 |  |  |  |  |  |  |  |  |  |
| OBJ-4 |  |  |  |  |  |  |  |  |  |
| OBJ-5 |  |  |  |  |  |  |  |  |  |

**4.2 Objective-level Risks & Expected Loss (≥5)**
| ID | Linked OBJ | Probability (0–1) | Impact (€) | **Expected Loss (€)** | Early Signal | Mitigation | Owner | WHY |
|----|------------|------------------:|-----------:|----------------------:|--------------|------------|-------|-----|
| RISK-O1 | OBJ-1 |  |  |  |  |  |  |  |
| RISK-O2 | OBJ-2 |  |  |  |  |  |  |  |
| RISK-O3 | OBJ-3 |  |  |  |  |  |  |  |
| RISK-O4 | OBJ-4 |  |  |  |  |  |  |  |
| RISK-O5 | OBJ-5 |  |  |  |  |  |  |  |

**4.3 Prioritization (Must/Should/Could)**
- **Criteria & Weights (sum=1.00):** Impact [ ], Effort [ ], Time [ ], Risk [ ], Strategic Fit [ ] → Σ=1.00  
- **Scoring Table**
| Objective ID | Impact (0–5) | Effort (0–5) | Time (0–5) | Risk (0–5) | Strategic Fit (0–5) | Weighted Score | Rank | WHY |
|--------------|--------------:|--------------:|-----------:|-----------:|---------------------:|---------------:|-----:|-----|
| OBJ-1 |  |  |  |  |  |  |  |  |
| OBJ-2 |  |  |  |  |  |  |  |  |
| OBJ-3 |  |  |  |  |  |  |  |  |
| OBJ-4 |  |  |  |  |  |  |  |  |
| OBJ-5 |  |  |  |  |  |  |  |  |

---

## 5) Scope Definition (Explicit In/Out + WHY + Interfaces)
**5.1 In Scope (≥6)**
| ID | Item (activity/system/segment) | Owner/Role | Linked Objective(s) | WHY Included (mechanism) | Source |
|----|-------------------------------|------------|---------------------|--------------------------|--------|
| SCOPE-IN-1 |  |  |  |  | *(…)* |
| SCOPE-IN-2 |  |  |  |  | *(…)* |
| SCOPE-IN-3 |  |  |  |  | *(…)* |
| SCOPE-IN-4 |  |  |  |  | *(…)* |
| SCOPE-IN-5 |  |  |  |  | *(…)* |
| SCOPE-IN-6 |  |  |  |  | *(…)* |

**5.2 Out of Scope (≥4)**
| ID | Item | WHY Excluded | Revisit Condition & Date | Source |
|----|------|--------------|--------------------------|--------|
| SCOPE-OUT-1 |  |  |  | *(…)* |
| SCOPE-OUT-2 |  |  |  | *(…)* |
| SCOPE-OUT-3 |  |  |  | *(…)* |
| SCOPE-OUT-4 |  |  |  | *(…)* |

**5.3 Stakeholders & Roles (RACI Summary)**
| Role/Group | Responsible | Accountable | Consulted | Informed | Decision Rights | Escalation Path | Source |
|------------|-------------|-------------|-----------|---------|-----------------|-----------------|--------|
|  |  |  |  |  |  |  | *(…)* |
|  |  |  |  |  |  |  | *(…)* |
|  |  |  |  |  |  |  | *(…)* |

**5.4 Interfaces & Data Contracts (≥6)**
| ID | System/Team | What’s Needed | Data Contract (fields & refresh cadence) | By When | WHY Needed | Source |
|----|-------------|---------------|-------------------------------------------|--------|------------|--------|
| INT-1 |  |  |  |  |  | *(…)* |
| INT-2 |  |  |  |  |  | *(…)* |
| INT-3 |  |  |  |  |  | *(…)* |
| INT-4 |  |  |  |  |  | *(…)* |
| INT-5 |  |  |  |  |  | *(…)* |
| INT-6 |  |  |  |  |  | *(…)* |

---

## 6) Success Criteria & KPI System (Data-first + Drivers + Bias Notes)
**6.1 Quantitative KPIs (≥5)**
| KPI-ID | Definition | Unit | Direction (↑/↓ good) | **Formula (explicit)** | Data Source | Cadence | Owner | Baseline (value+date) | Target (value+date) | Linked OBJ | Bias/Sampling Notes | WHY |
|--------|------------|------|----------------------|------------------------|-------------|---------|-------|----------------------|---------------------|------------|---------------------|-----|
| KPI-1 |  |  |  |  |  |  |  |  |  |  |  |  |
| KPI-2 |  |  |  |  |  |  |  |  |  |  |  |  |
| KPI-3 |  |  |  |  |  |  |  |  |  |  |  |  |
| KPI-4 |  |  |  |  |  |  |  |  |  |  |  |  |
| KPI-5 |  |  |  |  |  |  |  |  |  |  |  |  |

**6.2 Required Operational & Adoption Drivers (must include all 4)**
| Driver | Unit | Baseline | Target | Cadence | Owner | **Formula** | Source | WHY |
|--------|------|---------:|-------:|---------|-------|-------------|--------|-----|
| Time-to-Impact | days |  |  |  |  |  | *(…)* |  |
| Adoption_90d | % |  |  |  |  |  | *(…)* |  |
| Reliability_SLO | % / ms |  |  |  |  |  | *(…)* |  |
| ROI_12m | % |  |  |  |  | `ROI% = Net Benefit / Investment × 100` | *(…)* |  |

**6.3 Qualitative Indicators (≥3)**
| ID | Indicator | Method (survey/interviews/reviews) | Sample/Frame | Threshold | Cadence | Owner | WHY | Source |
|----|----------|-------------------------------------|--------------|----------:|---------|-------|-----|--------|
| QUAL-1 |  |  |  |  |  |  |  | *(…)* |
| QUAL-2 |  |  |  |  |  |  |  | *(…)* |
| QUAL-3 |  |  |  |  |  |  |  | *(…)* |

**6.4 Milestone Timeline**
| Horizon | What Will Be True | Evidence (KPI/Indicator) | Owner | Date |
|---------|-------------------|---------------------------|-------|------|
| 0–3m |  |  |  |  |
| 3–12m |  |  |  |  |
| 12m+ |  |  |  |  |

---

## 7) Constraints, Assumptions, Dependencies (with Tests + WHY)
**7.1 Constraints (≥5)**
| ID | Type (Budget/Time/People/Tech/Legal) | Limit (unit) | WHY Binding | Source |
|----|--------------------------------------|--------------|-------------|--------|
| CONSTR-1 |  |  |  | *(…)* |
| CONSTR-2 |  |  |  | *(…)* |
| CONSTR-3 |  |  |  | *(…)* |
| CONSTR-4 |  |  |  | *(…)* |
| CONSTR-5 |  |  |  | *(…)* |

**7.2 Assumptions (Testable; ≥5)**
| ID | Statement | Risk if False | Test Plan (method/data/owner/ETA) | Acceptance Criteria | WHY Reasonable Now | Source |
|----|-----------|---------------|-----------------------------------|--------------------|--------------------|--------|
| ASSUMP-1 |  |  |  |  |  | *(…)* |
| ASSUMP-2 |  |  |  |  |  | *(…)* |
| ASSUMP-3 |  |  |  |  |  | *(…)* |
| ASSUMP-4 |  |  |  |  |  | *(…)* |
| ASSUMP-5 |  |  |  |  |  | *(…)* |

**7.3 Dependencies (≥6)**
| ID | Type (Int/Ext/Seq) | What’s Needed | From Whom | By When | WHY | Source |
|----|---------------------|---------------|-----------|--------|-----|--------|
| DEP-1 |  |  |  |  |  | *(…)* |
| DEP-2 |  |  |  |  |  | *(…)* |
| DEP-3 |  |  |  |  |  | *(…)* |
| DEP-4 |  |  |  |  |  | *(…)* |
| DEP-5 |  |  |  |  |  | *(…)* |
| DEP-6 |  |  |  |  |  | *(…)* |

---

## 8) Risks & Mitigations (Definition-Phase, with €)
> Include **≥10 risks** with Expected Loss and at least **1 alternative mitigation** for the top 5.

| ID | Risk | Linked Section (OBJ/Scope/KPI/Constraint) | Prob. (0–1) | Impact (€) | **Expected Loss (€)** | Early Signal | Primary Mitigation | Alt. Mitigation (why rejected) | Owner | WHY Mitigation Works | Source |
|----|------|-------------------------------------------|------------:|-----------:|----------------------:|--------------|--------------------|-------------------------------|-------|----------------------|--------|
| RISK-1 |  |  |  |  |  |  |  |  |  |  | *(…)* |
| RISK-2 |  |  |  |  |  |  |  |  |  |  | *(…)* |
| RISK-3 |  |  |  |  |  |  |  |  |  |  | *(…)* |
| RISK-4 |  |  |  |  |  |  |  |  |  |  | *(…)* |
| RISK-5 |  |  |  |  |  |  |  |  |  |  | *(…)* |
| RISK-6 |  |  |  |  |  |  |  |  |  |  | *(…)* |
| RISK-7 |  |  |  |  |  |  |  |  |  |  | *(…)* |
| RISK-8 |  |  |  |  |  |  |  |  |  |  | *(…)* |
| RISK-9 |  |  |  |  |  |  |  |  |  |  | *(…)* |
| RISK-10|  |  |  |  |  |  |  |  |  |  | *(…)* |

> **Simulation readiness:** List variables / distributions to be modeled; if using triangular distributions, indicate **min/mode/max** or mark **TBD** with a collection plan.

---

## 9) Behavioral Economics (definition-phase lens)
**9.1 BE Assessment (≥6 interventions)**
| ID | Journey/Step | Target Behavior | Mechanism (bias/heuristic) | Intervention (what/where/how) | Microcopy | Primary Metric (unit, timeframe) | Telemetry | Owner | WHY |
|----|--------------|-----------------|-----------------------------|-------------------------------|-----------|-------------------------------|----------|-------|-----|
| BEH-1 |  |  |  |  |  |  |  |  |  |
| BEH-2 |  |  |  |  |  |  |  |  |  |
| BEH-3 |  |  |  |  |  |  |  |  |  |
| BEH-4 |  |  |  |  |  |  |  |  |  |
| BEH-5 |  |  |  |  |  |  |  |  |  |
| BEH-6 |  |  |  |  |  |  |  |  |  |

**9.2 Guardrails & Ethics (≥3)**
| ID | Risk | Guardrail | Owner | Monitoring | Source |
|----|------|----------|-------|------------|--------|
| BEG-1 |  |  |  |  | *(…)* |
| BEG-2 |  |  |  |  | *(…)* |
| BEG-3 |  |  |  |  | *(…)* |

---

## 10) Governance & Change Control
- **Decision Authority (role-level):** scope, limits, approvals & SLAs.  
- **Criteria alignment:** confirm no contradictions vs locked criteria; if any, propose a **Change Request (CR)** with rationale.  
- **Change process:** triggers, submission format, review cycle, approval path, comms protocol.  
**WHY:** Balances speed and safety; preserves traceability to the Criteria Lock.

---

## 11) Traceability & Provenance (Inputs → Outputs)
**11.1 Decision Traceability Table (≥10 rows)**  
| Output Decision/Claim | Exact Source Snippet (quote/figure) | Section Referenced | WHY This Source is Sufficient |
|-----------------------|--------------------------------------|--------------------|-------------------------------|
| “[…]” | “[…]” | Context §… / Feasibility §… / URL… | [reasoning] |
| “[…]” | “[…]” | Context §… / Feasibility §… / URL… | [reasoning] |
| “[…]” | “[…]” | Context §… / Feasibility §… / URL… | [reasoning] |
| “[…]” | “[…]” | Context §… / Feasibility §… / URL… | [reasoning] |
| “[…]” | “[…]” | Context §… / Feasibility §… / URL… | [reasoning] |
| “[…]” | “[…]” | Context §… / Feasibility §… / URL… | [reasoning] |
| “[…]” | “[…]” | Context §… / Feasibility §… / URL… | [reasoning] |
| “[…]” | “[…]” | Context §… / Feasibility §… / URL… | [reasoning] |
| “[…]” | “[…]” | Context §… / Feasibility §… / URL… | [reasoning] |
| “[…]” | “[…]” | Context §… / Feasibility §… / URL… | [reasoning] |


**11.2 Data Dictionary (≥12 fields)**
| Metric/Field | Definition | Unit | Source System | Known Limitations/Bias |
|--------------|------------|------|--------------|------------------------|
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |
|  |  |  |  |  |

---

## 12) Data Gap & Collection Plan (for every **TBD**; ≥8 rows if gaps exist)
| Missing Data | WHY Needed | Collection Method (instrumentation/query/survey/experiment) | Owner | ETA | Acceptance Criteria | Source (if any) |
|--------------|-----------|--------------------------------------------------------------|-------|-----|---------------------|-----------------|
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

---

## 13) Temporal Alignment & Roadmap Consistency
- **Roadmap window:** [start date] → [end date] (weeks).  
- **Interim milestones (if compression infeasible):** define realistic interim targets, dates, and trade-offs; justify with capacity/throughput limits.  
**WHY:** Preserves realism while aligning to locked criteria and program gates.

---

## 14) Appendix (Calculations, Benchmarks, Sensitivities)
- **Formulas & Derivations:** ROI, conversion/adoption, latency/SLO, cost drivers (with units).  
- **Benchmarks / Comparables:** sources, adjustments, and WHY applicable; include URL + access date.  
- **Sensitivity Notes:** how results shift under plausible ranges; WHY this informs targets/risk setting.

---

## Final Quality Gate (Do-Not-Skip Checklist)
- criteria_lock_hash_cited == **true**  
- five_smart_objectives_defined_and_time_aligned == **true**  
- operational_or_adoption_drivers_included (Time-to-Impact, Adoption_90d, Reliability_SLO, ROI_12m) == **true**  
- kpis_have_units_formulas_baseline_target_source_cadence_owner_bias_notes == **true**  
- scope_in_out_raci_and_interfaces_with_data_contracts == **true**  
- constraints_assumptions_dependencies_with_tests_and_whys == **true**  
- ≥10_risks_with_expected_loss_and_mitigations (top5_alt_mitigations) == **true**  
- behavioral_economics_section_with_≥6_interventions_and_guardrails == **true**  
- simulation_variables_distributions_prepared_or_tbd_with_plan == **true**  
- alternatives_considered_for_objectives_scope_kpis == **true**  
- all_tbds_have_collection_plan_entries == **true**  
- provenance_present_for_all_material_claims == **true**
"""

        return Task(
            description=description,
            expected_output = expected_output,
            agent=agent,
            markdown=True,
            output_file="03_define_report.md",
        )