# -*- coding: utf-8 -*-

from crewai import Agent
from tools.custom_tools import CodeInterpreterTool
from config import config
import streamlit as st
from datetime import datetime

class DecisionMultidisciplinaryAgent:
    """Agent for integrated multidisciplinary feasibility analysis"""

    @staticmethod
    def create_agent():
        # Get current model configuration
        selected_model = config.validate_and_fix_selected_model()
        model_config = config.AVAILABLE_MODELS[selected_model]
        provider = model_config["provider"]

        # Set up LLM based on provider
        llm = None
        if provider == "openai":
            from crewai.llm import LLM

            llm = LLM(
                model=f"openai/{selected_model}",
                api_key=config.OPENAI_API_KEY,
                temperature=min(0.4, getattr(config, "TEMPERATURE", 0.4)),
            )
        elif provider == "anthropic":
            from crewai.llm import LLM

            llm = LLM(
                model=f"anthropic/{selected_model}",
                api_key=config.ANTHROPIC_API_KEY,
                temperature=min(0.4, getattr(config, "TEMPERATURE", 0.4)),
            )

       # --- Tools: baseline + optional tools (silent, failure-tolerant) ---
        tools_list = [CodeInterpreterTool()]

        # Feature flags (override in config.py if needed)
        USE_OPTIONAL_TOOLS = getattr(config, "USE_OPTIONAL_TOOLS", True)
        TOOLS_ENABLED = getattr(
            config,
            "TOOLS_ENABLED",
            {
                "JSONSchemaValidatorTool": True,
                "CriteriaLockerTool": True,
                "RiskRegisterTool": True,
                "MarketSizingTool": True,
                "ElasticityEstimatorTool": True,
                "TimeSeriesForecastTool": True,
                "PositioningMapTool": True,
                "UnitEconomicsTool": True,
                "MarkdownFormatterTool": True,
            },
        )

        if USE_OPTIONAL_TOOLS:
            try:
                import importlib
                ct = importlib.import_module("tools.custom_tools")

                optional_tools = [
                    ("JSONSchemaValidatorTool", {"schema_name": "feasibility_v1"}),
                    ("CriteriaLockerTool", {}),
                    ("RiskRegisterTool", {}),
                    ("MarketSizingTool", {}),
                    ("ElasticityEstimatorTool", {}),
                    ("TimeSeriesForecastTool", {}),
                    ("PositioningMapTool", {}),
                    ("UnitEconomicsTool", {}),
                    ("MarkdownFormatterTool", {}),
                ]

                for class_name, kwargs in optional_tools:
                    # Respect per-tool enable flags without emitting UI logs
                    if not TOOLS_ENABLED.get(class_name, True):
                        continue

                    try:
                        cls = getattr(ct, class_name, None)
                        if cls is None:
                            # Tool class not found in custom_tools; skip silently
                            continue

                        # Some tools may not accept kwargs (or signature may differ).
                        # Try kwargs first, then no-arg fallback.
                        try:
                            tool_instance = cls(**kwargs)
                        except TypeError:
                            tool_instance = cls()

                        tools_list.append(tool_instance)

                    except Exception:
                        # Any initialization error: skip silently to avoid breaking agent startup
                        continue

            except Exception:
                # custom_tools module not available; proceed with baseline tool only
                pass


        # --- Agent profile (role/goal/backstory) ---
        return Agent(
            role = "Feasibility & Criteria Orchestrator (DECIDE › Establish) — locks normalized, auditable decision criteria and runs cross-discipline feasibility to a single source of truth.",
            goal = (
"Publish a single, immutable Criteria Lock and execute a multidisciplinary feasibility pass against it. "
"Deliver: (1) a LOCKED criteria matrix that names EXACTLY these five criteria — ROI_12m, GDPR_Compliance, "
"Time_to_Impact, Adoption_90d, Reliability_SLO — with weights that sum to 1.00, explicit Warn/Alert thresholds, "
"owners and cadences; (2) a version header with timestamp and a human-readable lock hash (text hash) that downstream "
"agents must cite; (3) 0–1 normalization/scoring rules per criterion and a worked scoring example; (4) governance rules "
"for how changes can be requested/approved (Change Request, approver quorum, version bump); (5) a feasibility analysis "
"across Technology, Legal/Regulatory, Finance, Market/Competition, Internal/Organizational, Communication, and Behavioral lenses, "
"with evidence → inference → implication WHY-chains, units/timeframes, and provenance cues; (6) a cross-lens risk register "
"(prob×impact, owner, due) and interdependency map; (7) scoring of Conservative/Balanced/Bold archetypes using ONLY the locked "
"criteria (no weight edits post hoc) and a Go/No-Go/Conditional verdict with thresholds and a 0–14 / 15–30 day decision timeline; "
"and (8) validation that all thresholds/weights elsewhere in the flow match this lock (fix or flag any ambiguity)."
            ),
            backstory = (
"You are the Establish-phase decision architect. Your output becomes the reference standard everyone cites. "
"You do two things exceptionally well: (A) you freeze decision rules into a versioned, auditable artifact; "
"and (B) you test feasibility across multiple disciplines without drifting from those rules.\n\n"
"Immutability: You name and lock the five criteria exactly — ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, "
"Reliability_SLO — set weights that sum to 1.00, define Warn/Alert thresholds, owners, cadences, and write explicit 0–1 "
"scoring functions (including caps and floors). You stamp the document with a timestamp and a lock hash (derived from the "
"criteria text), and you propagate that hash so all downstream agents cite the same version. No synonym drift, no silent edits; "
"changes require a formal Change Request with governance and version bump.\n\n"
"Feasibility: You examine Technology (architecture, SLOs, security), Legal/Regulatory (GDPR/DPIA, contracts, accessibility), "
"Finance (ROI/NPV/IRR, payback, unit economics, sensitivity), Market/Competition (TAM/SAM/SOM, elasticity, GTM), "
"Internal/Organizational (capabilities, RACI, capacity), Communication (audience–message–channel, measurement), and "
"Behavioral (frictions, biases, nudges, ethics). Every claim carries units and timeframes, and every conclusion includes a "
"compact WHY-chain (evidence → inference → implication) with provenance cues. Where data is missing, you mark TBD and attach "
"a data-gap collection plan (method, owner, ETA, acceptance criteria).\n\n"
"Guardrails: You never score with criteria that are not locked. You never adjust weights after seeing scores. You ensure thresholds "
"and nomenclature are consistent across the program (fix or flag any mismatch such as outdated ROI horizons). You make trade-offs explicit, "
"prioritize risks by probability×impact, and issue a clear Go/No-Go/Conditional verdict tied to observable thresholds and a short decision timeline."
            ),
            tools=tools_list,
            verbose=True,
            allow_delegation=False,
            max_iter=getattr(config, "MAX_ITERATIONS", 6),
            temperature=min(0.4, getattr(config, "TEMPERATURE", 0.4)),
            llm=llm,
        )
    @staticmethod
    def create_task(context_data: str):
        from crewai import Task
        # Get current system time for time awareness
        current_time = datetime.now()
        current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.strftime("%A, %B %d, %Y")
        description = f"""
DECIDE › Establish — **Feasibility & Criteria (Multidisciplinary / Establish)**

Create ONE immutable, versioned **Criteria Lock** and run a cross-discipline feasibility pass strictly against it.
Everything downstream must cite this lock’s **version** and **lock hash**. If any other document uses variants, **flag and correct**.

Time Context
- **Locked At (local)**: {current_timestamp}
- **Calendar Date**: {current_date}

────────────────────────────────────────────────────────────────────────────────────────
NON-NEGOTIABLES (from feedback; must all appear)
1) **Lock EXACTLY these five criteria** (names verbatim): ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO.
2) **Weights sum to 1.00** (Σ=1.00) with a compact **Why** per weight.
3) **Warn/Alert thresholds** per criterion + **cadence** and **owner**.
4) **Version header** with **Criteria Version** (e.g., v1.0), **Locked At** timestamp, and **Lock Hash** (SHA256 of the criteria section text).
5) **0–1 normalization rules** per criterion and **one worked example** (scoring table).
6) **Governance**: who can change, how (Change Request), quorum, version bump rule.
7) **Consistency checks**: fix/flag any threshold/weight/label that conflicts with this lock (no synonym drift).
8) Feasibility across **7 lenses** with **WHY-chains** (evidence → inference → implication), **units/timeframes**, and **provenance**.

────────────────────────────────────────────────────────────────────────────────────────
INPUTS (verbatim / already processed context)
{context_data}

Use only the evidence present above. If something is missing, mark **TBD** and add a **Data Gap & Collection Plan** (method, owner, ETA, acceptance criteria).
Do **not** invent facts. Every computed number shows **unit**, **timeframe**, and **formula**.

────────────────────────────────────────────────────────────────────────────────────────
A) CRITERIA — VERSION & LOCK (Paste this header verbatim with your filled values)

Criteria — Version & Lock
- **Criteria Version:** v1.0
- **Locked At:** {current_timestamp}
- **Lock Hash (SHA256 text):** criteria-v1.0:<short-hash>  ← *Downstream agents must cite this exact string*

Locked Decision Criteria (Σ pesos = 1.00)
| ID     | Criterion         | Group       | Weight | Metric            | Unit | Source/System | Cadence   | Threshold (Warn/Alert) | Owner        | Why |
|--------|-------------------|-------------|-------:|-------------------|------|---------------|-----------|------------------------|--------------|-----|
| CRIT-1 | ROI_12m           | Outcome     | 0.20   | ROI               |  %   | Finance DW    | Monthly   | 10 / 5                 | Finance Lead | Capital efficiency gate |
| CRIT-2 | GDPR_Compliance   | Constraint  | 0.15   | Pass/Fail         | bin  | Legal         | Milestone | Pass / Fail            | Legal        | Legal gating criterion |
| CRIT-3 | Time_to_Impact    | Outcome     | 0.25   | TTI               | weeks| PMO           | Bi-weekly | 8 / 12                 | PMO          | Urgency window |
| CRIT-4 | Adoption_90d      | Outcome     | 0.25   | % active users    |  %   | Analytics     | Weekly    | 30 / 20                | Product      | Revenue predictor |
| CRIT-5 | Reliability_SLO   | Outcome     | 0.15   | Availability      |  %   | SRE           | Daily     | 99.5 / 99.0            | SRE          | SLA/churn risk |

**Weights Sum:** 1.00  • **Validation:** use CodeInterpreterTool or JSONSchemaValidatorTool if available.
**Normalization (0–1) Rules (must state floors/caps):**
- ROI_12m (%): score=0 at 0%; 0.5 at 10% (warn); 1 at ≥20% (cap).
- Time_to_Impact (weeks): score=1 at ≤4; 0.5 at 8 (warn); 0 at ≥12 (alert).
- Adoption_90d (%): score=0 at 0; 0.5 at 30 (warn); 1 at ≥50.
- Reliability_SLO (%): score=0 at ≤99.0 (alert); 0.5 at 99.5 (warn); 1 at ≥99.9.
- GDPR_Compliance (bin): Pass=1; Fail=0 (gating: Fail ⇒ overall score=0 and **No-Go** regardless of others).

**Worked Example (Scoring)**
| Criterion       | Measured Value | Unit | Normalized (0–1) | Weight | Contribution (=Norm×W) | Why |
|-----------------|----------------|------|------------------:|-------:|-----------------------:|-----|
| ROI_12m         | 12             |  %   | 0.60              | 0.20   | 0.12                   | Above warn, below cap |
| Time_to_Impact  | 6              | weeks| 0.75              | 0.25   | 0.19                   | Early impact vs window |
| Adoption_90d    | 35             |  %   | 0.58              | 0.25   | 0.15                   | Near warn→acceptable  |
| Reliability_SLO | 99.6           |  %   | 0.60              | 0.15   | 0.09                   | Above warn            |
| GDPR_Compliance | Pass           | bin  | 1.00              | 0.15   | 0.15                   | Gating passed         |
| **Total**       | —              | —    | —                 | **1.00**| **0.70**              | **Go if ≥ threshold** |

**Governance (changes)**
- Change Request required, approver: Steering Committee, quorum: **2/3**, action: **version bump** (e.g., v1.1) and new lock hash.
- Any thresholds/weights elsewhere must match this lock or be corrected/flagged in “Corrections & Consistency” below.

────────────────────────────────────────────────────────────────────────────────────────
B) CORRECTIONS & CONSISTENCY
List and fix any mismatches found across inputs/agents (examples: “ROI 20%/18m” variants). This document is the single source of truth.

| Item Found | Where | Conflict | Resolution (align to this Lock) | Owner | Due |
|------------|-------|----------|----------------------------------|-------|-----|

────────────────────────────────────────────────────────────────────────────────────────
C) MULTIDISCIPLINARY FEASIBILITY — **Seven Lenses with WHY-chains**

Instruction for all lenses:
- Every metric shows **unit** and **frame** (per month/quarter, cohort/geo, baseline date).
- Every finding includes a **WHY** line: **evidence → inference → implication** with a short provenance cue *(Doc-ID/§ or URL+date)*.
- If missing, mark **TBD** and add to **Data Gap & Collection Plan** (method, owner, ETA, acceptance).

1) Technology (Architecture • Data • Reliability • Security • Cost)
- Deliver: **Tech Assessment Matrix**, **Interface/Data Contracts**, **Security & Privacy Map**, **Acceptance Gates** (SLOs, error budget, cost-to-serve).
- Quantify: latency p95/p99 [ms], throughput [req/s], availability [%], error budget [h/period], RPO/RTO [min], unit costs [€/1k req], data freshness [min].

2) Legal & Regulatory (GDPR/DPIA • IP/Contracts • Approvals • Accessibility)
- Deliver: **Compliance Register**, **Data Transfer & Residency**, **IP/Contractual Terms**, **Acceptance Gates** (lawful basis, DPIA, DPAs/SCCs, WCAG).
- Quantify: risk (prob×impact), approval lead times [days], accessibility defect rates.

3) Finance (Model • Scenarios O/B/P • Sensitivity • Unit Economics • Guardrails)
- Deliver: **Scenario Summary**, **Unit Economics**, **Sensitivity (tornado)**, **Guardrails & Triggers**.
- Formulas: ROI, NPV (state WACC inputs), IRR, Payback, LTV, CAC; normalization rules (FX/CPI/PPP) + sources & dates.

4) Market & Competition (TAM/SAM/SOM • Segmentation/JTBD • Demand/Elasticity • Supply • GTM)
- Deliver: **TAM–SAM–SOM** (top-down & bottom-up), **Segmentation & JTBD**, **Demand & Pricing**, **Supply Constraints**, **Competition & Positioning**, **GTM & Channels**.
- Quantify: CAGR, forecast horizon, O/B/P bands, elasticity ε, capacity [units/period], lead times [days], CAC/LTV/payback.

5) Communication (Stakeholders • Message House • Channels • Change-Comms • Measurement)
- Deliver: **Audience–Message–Channel Matrix**, **Change-Comms Milestones** with KPIs (open %, CTR %, conversion %, sentiment).

6) Behavioral (Frictions • Biases • Nudges • Experiments • Ethics)
- Deliver: **Barrier → Lever Mapping**, **Experiment Plan** (α, power, MDE, n, duration, guardrails, analysis).
- Include: defaults, framing, social proof, scarcity/urgency (truthful), commitment/consistency, friction reduction, salience; ethics & consent.

7) Internal/Organizational (Capabilities • Governance • RACI • Capacity • Change Impact)
- Deliver: **Capability & Gap Analysis**, **RACI (draft)**, **Capacity & Hiring** with time-to-fill [days] and buffers.

**Cross-Lens Consistency Check (Mandatory)**
- No contradictions across tech/legal/finance/market/comms/behavioral/org. Note any interdependencies affecting criteria or risk.

────────────────────────────────────────────────────────────────────────────────────────
D) CROSS-LENS RISK & INTERDEPENDENCY
- Integrated **Risk Register**: probability [0–1 or L/M/H] × impact [€/unit or L/M/H], interactions, mitigations, owners, due.
- **Dependency Map** and **critical path** across lenses; note impacts on Time_to_Impact and Reliability_SLO.

────────────────────────────────────────────────────────────────────────────────────────
E) DECISION FRAMES & SCORING (ONLY the **LOCKED** criteria)
- Evaluate **≥2 frames** (e.g., Value-at-Risk vs Speed-to-Learn; Share-Grab vs Profit-First) — explain **WHY** each fits.
- Score **Conservative / Balanced / Bold** archetypes using the normalization rules above; show per-criterion contributions.
- **No** weight changes post hoc.

────────────────────────────────────────────────────────────────────────────────────────
F) VERDICT & TIMELINE
- **Go / No-Go / Conditional** with explicit **thresholds** (units/timeframes) aligned to the Lock.
- **Decision Horizon:** 0–14 days / 15–30 days, named owners, effort (hrs/person) and budget (€).
- **WHY**: 3 bullets (evidence → inference → recommendation) across key lenses.

────────────────────────────────────────────────────────────────────────────────────────
G) DATA GAPS & COLLECTION PLAN (MANDATORY for each TBD)
| Gap | Why It Matters | Method (instrument/test/query) | Owner | ETA | Acceptance Criteria | Expected Source |
|-----|----------------|---------------------------------|-------|-----|---------------------|-----------------|

────────────────────────────────────────────────────────────────────────────────────────
ACCEPTANCE CHECKLIST (ALL MUST BE YES)
- five_criteria_present_verbatim == true
- weights_sum_to_1_00 == true
- warn_alert_defined_per_criterion == true
- owners_and_cadences_present == true
- version_and_lock_hash_present == true
- normalization_rules_and_worked_example_present == true
- governance_change_request_and_quorum_defined == true
- corrections_consistency_section_completed == true
- seven_feasibility_lenses_with_units_and_provenance == true
- cross_lens_risk_and_dependency_map_present == true
- ≥2_decision_frames_and_three_archetypes_scored == true
- verdict_with_explicit_thresholds_and_timeline == true
- data_gaps_collection_plan_present == true
- why_chain_for_every_major_claim_present == true

TOOLS (if available; fail gracefully)
- CriteriaLockerTool, JSONSchemaValidatorTool, RiskRegisterTool, MarketSizingTool, ElasticityEstimatorTool,
  TimeSeriesForecastTool, PositioningMapTool, UnitEconomicsTool, MarkdownFormatterTool, CodeInterpreterTool.
If a tool fails, proceed manually and note the fallback in the WHY of the affected section.
"""
        expected_output = """
# Multidisciplinary Feasibility & Criteria — Locked, Auditable Report

> Non-negotiables:
> • Every claim includes a **WHY** (evidence → inference → implication).  
> • Every metric carries a **unit** and a **time frame** (cohort/geo/period).  
> • Compact **provenance** cues (Doc-ID/§ or URL + access date) for material facts.  
> • Tables use stable IDs (CRIT-#, TECH-#, LEG-#, FIN-#, MKT-#, ORG-#, COMMS-#, BEH-#, RISK-#).  

---

## 0) Criteria — Version & Lock

**Criteria Version:** v1.0  
**Locked At:** {current_timestamp}  
**Lock Hash (SHA256 of criteria text):** criteria-v1.0:<computed-lock-hash>  
*(Cite this hash in ALL downstream agents.)*

### Locked Decision Criteria (Σ weights = **1.00**, EXACT names)
| ID     | Criterion          | Group       | Weight | Metric           | Unit | Source        | Cadence   | Threshold (Warn / Alert) | Owner    | WHY |
|--------|--------------------|-------------|-------:|------------------|------|---------------|-----------|---------------------------|----------|-----|
| CRIT-1 | ROI_12m            | Outcome     | 0.20   | ROI              | %    | Finance DW    | Monthly   | 10 / 5                    | Finance  | Capital allocation gate; links value to cost of capital |
| CRIT-2 | GDPR_Compliance    | Constraint  | 0.15   | Pass/Fail        | bin  | Legal         | Milestone | Pass / Fail               | Legal    | Legal gating condition to operate |
| CRIT-3 | Time_to_Impact     | Outcome     | 0.25   | TTI              | weeks| PMO           | Bi-weekly | 8 / 12                    | PMO      | Urgency window; when value appears |
| CRIT-4 | Adoption_90d       | Outcome     | 0.25   | % active users   | %    | Analytics     | Weekly    | 30 / 20                   | Product  | Leading indicator for retention & revenue |
| CRIT-5 | Reliability_SLO    | Outcome     | 0.15   | Availability     | %    | SRE           | Daily     | 99.5 / 99.0               | SRE      | SLA/churn risk; platform stability |

**Weights (sum):** **1.00**  
**WHY (criteria & weights):** Reflect executive priorities and enabling risks (legal/operational) evidenced in inputs.

#### Scoring Rules (0–1 normalization; monotonic, capped)
- **ROI_12m (%)**: 0 at 0%; 0.5 at 10% (warn); 1.0 at ≥20% (cap).  
- **Time_to_Impact (weeks)**: 1.0 at ≤4; 0.5 at 8 (warn); 0 at ≥12 (alert). *(lower is better)*  
- **Adoption_90d (%)**: 0 at 0; 0.5 at 30 (warn); 1.0 at ≥50.  
- **Reliability_SLO (%)**: 0 at ≤99.0 (alert); 0.5 at 99.5 (warn); 1.0 at ≥99.9.  
- **GDPR_Compliance**: Pass=1, Fail=0 (gating; if 0, total score is **blocked**).

*Normalization note:* document the mapping function (linear/piecewise), bounds, and historical references if available.

#### Governance (changes)
- This section is **immutable** once locked.  
- Any change requires a **Change Request**, approved by the **Steering Committee** (2/3 rule), and creates a **new version** (v1.1, v2.0) with a **new lock hash**.  
- Any duplicated/ambiguous thresholds outside this document are **void** and must be corrected to match this lock.

---

## 1) Executive Summary (≤1 page)
- **Core Problem (symptom → likely cause → opportunity):** _TBD_  
- **Feasibility outlook (high/medium/low)** with 3 quantified reasons (unit/frame) + provenance.  
- **Verdict:** **Go / No-Go / Conditional** with **measurable conditions** (threshold + date + evidence).  
- **Decision timeline:** 0–14 days / 15–30 days (owners, effort, €).  
**WHY:** tie locked criteria to key drivers (finance, tech, legal, adoption, reliability).

---

## 2) Problem Definition (Define)
### 2.1 Symptom → Likely Cause → Opportunity
- **Symptom (unit/frame):** _TBD_  
- **Likely Cause(s):** _TBD_  
- **Opportunity:** _TBD_  
**WHY:** evidence → inference → implication with source and dates.

### 2.2 Assumptions & Hard Constraints
| ID | Type (Legal/Tech/Time/Budget/Quality) | Statement | Unit/Limit | Source/Date | WHY binding |
|----|---------------------------------------|-----------|------------|-------------|-------------|
| CONSTR-1 | Time | Launch window | YYYY-MM-DD | _TBD_ | Seasonality/lead time |

### 2.3 Knowledge Gaps & Validation Plan
| Gap | Why It Matters | Method | Sample/Power | Owner | ETA | Acceptance |
|-----|-----------------|--------|--------------|-------|-----|-----------|
| Price elasticity | Drives ROI/Payback | Price A/B | n=TBD | _TBD_ | _TBD_ | |ε|∈[0.6,1.2], p<0.05 |

---

## 3) Seven-Lens Feasibility (deep, evidence-first)

### 3.1 Technology (Architecture • Data • SRE • Security • Cost)
**Tech Assessment Matrix**  
| Capability/Topic | Current | Target/SLO (unit) | Fit/Gap | Effort (S/M/L) | Key Risk | Mitigation | Owner | Due | Source | WHY |
|---|---|---|---|---|---|---|---|---|---|---|

**Interfaces & Data Contracts**  
| System | API/Data | Fields | SLA (unit) | Volume (unit/period) | Latency (ms) | Errors (%) | Dependencies | Source | WHY |

**Security & Privacy**  
| Asset | Data Class | Control | STRIDE Threat | Residual Risk | Mitigation | Owner | Source | WHY |

**Acceptance gates:** SLOs defined, error budget computed, data contracts documented, cost-to-serve quantified (€/1k req, €/GB/month).

### 3.2 Legal & Regulatory
**Compliance Register**  
| Requirement | Applicability | Gap | Risk (p×i) | Mitigation | Owner | Deadline | Evidence | WHY |

**Data Transfer/Residency & IP/Contracts**  
Tables for mechanisms (DPA/SCC), risks, and key clauses (IP/indemnity/LoL).  
**Acceptance gates:** Lawful basis / DPIA as required; WCAG plan; retention/deletion SLAs.

### 3.3 Financial
**Scenario Summary (O/B/P)**  
| KPI | Formula | Inputs (unit) | Base | O | P | Source | WHY |
|-----|---------|----------------|-----:|---:|---:|-------|-----|
Include ROI [%], NPV [€ @ WACC], IRR [%], Payback [months]; **sensitivities** (tornado) for price/volume/churn/COGS/CAC/FX.

**Unit Economics**  
| Segment | ARPU (€/period) | COGS (€/unit) | GM % | CAC (€/cust) | Payback (months) | LTV (€/cust) | LTV:CAC | Source | WHY |

### 3.4 Market & Competition
**TAM–SAM–SOM (top-down & bottom-up)** with reconciliation.  
**Forecast & Elasticity** (method, horizon, O/B/P; own/cross ε).  
**Competition & Positioning** (table + map).  
**GTM/Channels** (CAC/LTV/payback; funnel).  
**Supply Constraints** (capacity [units/period], lead time [days], SLAs).

### 3.5 Communication Strategy
**Audience–Message–Channel Matrix** with KPIs (open/CTR/conv/sentiment) and cadences.

### 3.6 Behavioral & Cultural Factors
**Barrier → Lever Mapping** with nudges (defaults, framing, social proof, salience, commitment, timing), **expected lift** (pp) and **primary metric**.  
**Experiment Plan** (α, power, MDE, n, duration, guardrails, ethics).

### 3.7 Internal / Organizational
**Capability & Gap Analysis**, **RACI (draft)**, **Capacity & Hiring** (FTE, time-to-fill), governance/escalations.

---

## 4) Cross-Lens Risks & Interdependencies
**Integrated Risk Register**  
| ID | Description | Lens | Prob (0–1) | Impact (€/k or 0–1) | Score | Interactions | Mitigation | Owner | Due | WHY |
|----|-------------|------|-----------:|---------------------:|------:|-------------|-----------|-------|-----|-----|

**Dependency Map (Critical Path)** with predecessors→successors and coupling points.

---

## 5) Decision Frames & Multi-Criteria Scoring

### 5.1 Frames Considered (≥2)
- **Value-at-Risk vs Speed-to-Learn** (and/or **Share-Grab vs Profit-First**) — summarize implications.

### 5.2 Scoring (ONLY the **Locked Criteria**)
**Example (archetypes: Conservative / Balanced / Bold)**  
| Solution Type | Total (0–1) | ROI_12m | GDPR | TTI | Adoption_90d | Reliability_SLO | WHY |
|---------------|------------:|--------:|-----:|----:|-------------:|-----------------:|-----|
| Conservative  | 0.68        | 0.22    | 0.15 |0.08| 0.12         | 0.11            | Strong compliance & reliability; slower upside |
| Balanced      | 0.74        | 0.24    | 0.15 |0.10| 0.15         | 0.10            | Best trade-off across adoption and TTI |
| Bold          | 0.69        | 0.26    | 0.15 |0.06| 0.17         | 0.05            | Higher adoption upside; more TTI/SLO exposure |

**Diversity check:** alternatives are not >75% similar (apply diversity penalty if they are).  
**Note:** **Do NOT** change weights after seeing scores.

---

## 6) Strategic Verdict, Conditions & Timeline
**Verdict:** **Go / No-Go / Conditional**  
**Conditions (if Conditional):** measurable thresholds (e.g., ROI_12m ≥ X%, Payback ≤ Y months, Adoption_90d ≥ Z%, Reliability_SLO ≥ W%, DPIA=Pass by YYYY-MM-DD).  
**Rationale (3× WHY):**  
- **Finance:** evidence → inference → implication  
- **Technology:** evidence → inference → implication  
- **Market/Behavior:** evidence → inference → implication  

**Decision Timeline**  
- **0–14 days:** tasks, owners, hours, € (measurable)  
- **15–30 days:** tasks, owners, hours, € (measurable)

---

## 7) Example Scoring Table (0–1 rules shown)
> Include at least **one** fully worked example per criterion with formula, inputs, and result.

| Criterion        | Raw Value (unit) | Rule (to 0–1)                        | Score | WHY |
|------------------|------------------|--------------------------------------|------:|-----|
| ROI_12m (%)      | 14               | 0 at 0; 0.5 at 10; 1 at ≥20 (cap)    | 0.60  | Above warn, below cap; acceptable if other gates pass |
| Time_to_Impact   | 9 weeks          | 1 at ≤4; 0.5 at 8; 0 at ≥12          | 0.40  | Near alert; mitigable with pilot phasing |
| Adoption_90d (%) | 32               | 0 at 0; 0.5 at 30; 1 at ≥50          | 0.53  | Slightly above warn; depends on behavioral levers |
| Reliability_SLO  | 99.6             | 0 at ≤99.0; 0.5 at 99.5; 1 at ≥99.9  | 0.67  | Above warn; some headroom |
| GDPR             | Pass             | Pass=1; Fail=0 (gating)              | 1.00  | Gate satisfied |

---

## 8) Acceptance Checklist (YES/NO)
- weights_sum_to_1 == **true**  
- warn_and_alert_thresholds_defined_per_criterion == **true**  
- owners_and_cadences_assigned == **true**  
- criteria_locked_and_lock_hash_present == **true**  
- technology_table_present == **true**  
- legal_compliance_map_present == **true**  
- finance_scenarios_and_sensitivity_present == **true**  
- market_tam_sam_som_present == **true**  
- segmentation_with_jtbd == **true**  
- demand_forecast_with_obp == **true**  
- elasticity_estimated_or_flagged == **true**  
- supply_constraints_and_sla == **true**  
- competition_profiles_and_positioning_map == **true**  
- gtm_channels_with_cac_ltv_payback == **true**  
- pricing_with_range_and_rationale == **true**  
- unit_economics_reported == **true**  
- comms_audience_channel_table_present == **true**  
- behavioral_levers_table_present == **true**  
- internal_capability_gap_table_present == **true**  
- cross_lens_risk_matrix_and_dependencies_present == **true**  
- go_nogo_or_conditional_with_thresholds_and_timeline == **true**

---

## 9) Traceability & Provenance
- **Sources (Doc IDs/Systems + dates):** _TBD_  
- **Tools Used:** CriteriaLockerTool, JSONSchemaValidatorTool, RiskRegisterTool, MarketSizingTool, ElasticityEstimatorTool, TimeSeriesForecastTool, PositioningMapTool, UnitEconomicsTool, MarkdownFormatterTool, CodeInterpreterTool.  
- **Assumptions (explicit):** _TBD_  
- **Reproducibility Notes:** normalization rules, data snapshots, seeds, versions.

## Appendices
- **A. Formulas & Definitions:** ROI, NPV, IRR, Payback, LTV, CAC, GRR/NRR, elasticity (own/cross).  
- **B. Sensitivity (tornado):** driver deltas → KPI deltas.  
- **C. Full RACI & Governance.**  
- **D. Compliance Evidence** (DPIA, DPA, ISO/SOC, WCAG).  
- **E. Experiment Designs** (pricing/adoption/comms).

"""


        return Task(
            description=description,
            expected_output=expected_output,
            agent=DecisionMultidisciplinaryAgent.create_agent(),
            markdown=True,
            output_file="feasibility_report.md"
        )