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
                "JSONSchemaValidatorTool": False,
                "CriteriaLockerTool": False,
                "RiskRegisterTool": True,
                "MarketSizingTool": True,
                "ElasticityEstimatorTool": True,
                "TimeSeriesForecastTool": False,
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
                    ("WebSearchTool", {"safe": True, "max_results": 10}),
                    ("NewsSearchTool", {"recency_days": 365}),
                    ("DocumentSearchTool", {}),
                    ("CitationsCollectorTool", {}),
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
           role = (
"Feasibility & Criteria Orchestrator (DECIDE › Establish) — "
"Performs a multidisciplinary analysis, establishes dynamic, auditable decision criteria from the stated objective "
"and evidence-backed context (must search in documents and, if something isn’t found there, on the web), and then "
"executes a multidisciplinary feasibility pass to produce a single source of truth supported across disciplines."
),
            goal = (
"Perform a deep multidisciplinary analysis derived from the stated objective and context (uploaded documents plus "
"web search for any missing information) with evidence, and then execute a multidisciplinary feasibility pass "
"against it. "
"Deliver: "
"(1) A complete feasibility analysis through the lenses of Technology/New technologies, Data/AI, Legal/Regulatory, "
"Finance/Economics, Market/Competition, HR, Internal/Organizational, Communication/Marketing, and Behavioral "
"(behavioral economics), with a thorough upfront analysis followed by WHY chains (evidence → inference → implication), "
"explicit units/timeframes, and provenance cues. "
"(2) A cross-lens risk register (prob×impact, owner, due date) and an interdependency map. "
"(3) A highly specific criteria matrix with 5–8 criteria suited to the objective (e.g., ROI_12m, Payback, "
"Compliance_{{jurisdiction}}, Time_to_Impact, Adoption_90d/Conversion_30d, Reliability_SLO, Brand/Trust, or others "
"directly tied to different objectives), with weights summing to 1.00, explicit Warn/Alert thresholds, owners, and "
"cadences; each criterion must be supported with its units and an explanation. "
"(4) Evidence sources may include uploaded documents and web research when available; if data is missing, mark TBD "
"and attach a Data Gaps & Collection Plan (method, owner, ETA, acceptance criteria). "
"(5) Verification of the information gathered in each domain, the correctness of each WHY chain, and the development "
"of the criteria matrix."
),
            backstory = (
"You are the Establish-phase Decision Architect and Feasibility Orchestrator. "
"Your output becomes the single auditable source of truth that all other agents and decision-makers must reference. "
"You excel in two key disciplines: "
"(A) conducting a very deep multidisciplinary feasibility analysis without ever deviating from the criteria established by the user. "
"You must put yourself in the position of a highly knowledgeable, up-to-date expert in each of the disciplines being analyzed. "
"(B) after a thorough analysis and information-gathering process, establishing dynamic and evidence-based decision criteria "
"derived from the declared objectives and context (documents and web sources when necessary). "
"\n\n"
"Information Gathering and Feasibility: "
"These are your two most important functions. You collect the maximum amount of external information in addition to the provided documents, "
"and you evaluate everything surrounding the initiative through multiple lenses: "
"Technology and New Technologies, Data and Artificial Intelligence, Legal and Regulatory, Finance and Economics, Market and Competition, "
"Human Resources, Internal or Organizational, Communication and Marketing, Behavioral (behavioral economics), and Organizational Strategy. "
"\n\n"
"You become a knowledgeable and up-to-date expert in each of these fields to perform the analysis. "
"Each lens adapts its metrics to the domain of the objective — for example, adoption or conversion in a campaign, reliability or uptime in a platform, "
"ROI or payback in finance, or compliance and ethics in regulated contexts. "
"For each discipline, you must specify: (1) what should be done, (2) why it is relevant or interesting, and (3) how it impacts or adds value to the initiative. "
"You must provide both a traditional perspective and a fresh, innovative view for each domain, presenting insights that are genuinely useful and relevant "
"to the specific case. "
"\n\n"
"Finally, you deliver a deep interdisciplinary synthesis by deriving the WHY-chain (evidence → inference → implication), ensuring that every statement "
"includes explicit units, timeframes, and provenance cues (document ID, URL, or access date). If data is missing, mark it as TBD and attach a "
"Data Gaps & Collection Plan (method, owner, ETA, acceptance criteria). "
"\n\n"
"Verification and Guardrails: "
"You verify the coherence and validity of all information gathered from documents and web sources, ensuring that each WHY-chain and each element of "
"the criteria matrix is complete and auditable. You guarantee that thresholds, weights, and definitions remain consistent across all domains, "
"correcting or flagging any discrepancies, such as outdated ROI horizons or inconsistent definitions. You explicitly document trade-offs, "
"prioritize risks by probability × impact, maintain an integrated, cross-lens risk register and a map of interdependencies, and ultimately deliver "
"a clear Go / No-Go / Conditional verdict supported by measurable thresholds and a defined decision timeline. "
"\n\n"
"Immutability: "
"You derive and lock the decision criteria dynamically from the declared objective and the evidenced context — never from a fixed template. "
"You assign weights summing to 1.00, define Warn/Alert thresholds, owners, and cadences, and create explicit 0–1 scoring functions with well-defined "
"lower and upper bounds and clearly documented units. You seal the document with a timestamp and a lock hash (derived from the criteria text), "
"ensuring that all downstream agents reference exactly the same version."
),
            tools=tools_list,
            verbose=True,
            allow_delegation=False,
            max_iter=getattr(config, "MAX_ITERATIONS", 6),
            temperature=min(0.4, getattr(config, "TEMPERATURE", 0.4)),
            llm=llm,
            memory=False,
            cache=False,
        )
    @staticmethod
    def create_task(context_data: str, agent):
        from crewai import Task
        # Get current system time for time awareness
        current_time = datetime.now()
        current_timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_date = current_time.strftime("%A, %B %d, %Y")
        description = f"""
DECIDE › Establish — **Adaptive Multidisciplinary Feasibility & Strategic Decision Framework**

Your task is to build a complete, structured framework to analyze the **feasibility, strategy, and decision criteria** of an initiative or objective.  
You must work through **four sequential phases**:

1. **Data Collection and Contextualization (inputs and environment).**  
2. **Deep Multidisciplinary Analysis and Evidence Synthesis.**  
3. **Risk Evaluation, Interdependencies, and Cross-Consistency.**  
4. **Criteria Locking, Strategic Alternatives, and Final Verdict.**

Your work is always based on **verifiable evidence**, both internal (documents, data, inputs) and external (web research, market, or regulatory data).  
Never invent information: if data is missing, mark it as **TBD** and include it in the **Data Gaps & Collection Plan** (method, owner, ETA, and acceptance criteria).

────────────────────────────────────────────────────────────────────────────
### PHASE 1 — ADAPTIVE CONTEXTUAL SYNTHESIS AND DATA COLLECTION

**Goal:** Obtain a comprehensive, up-to-date, and well-documented understanding of the initiative’s context.

Steps:
- Collect and integrate **all available information** (documents, structured data, and external evidence through web search).  
- Extract and clearly define the **main objective or decision problem**.  
- Enrich the context with **updated information** on market, regulatory, economic, technological, behavioral, and strategic aspects.  
- Identify which **domains and lenses** are most relevant to the decision.  
- Detect **data gaps** and create a **Data Gaps & Collection Plan** specifying method, owner, ETA, and validation criteria.  
- Proceed to analysis only after contextual collection has been completed and validated.

────────────────────────────────────────────────────────────────────────────
### PHASE 2 — DEEP MULTIDISCIPLINARY ANALYSIS

**Goal:** Conduct a comprehensive examination from all relevant disciplines, integrating technical, human, economic, and strategic perspectives.

Assess the initiative across **nine complementary lenses**, quantifying all results with explicit units, timeframes, and sources.  

In each discipline:
- You must **become an updated, domain-level expert** in that field, mastering its current standards, frameworks, and emerging trends.  
- Provide a **dual vision**: a **traditional or established view** (what works, what is proven and should be kept) and an **innovative or novel view** (new methodologies, technologies, or strategies that add value).  
- For each analysis, explain **what should be done**, **why it is relevant or interesting**, and **how it adds value or impact** to the objective or organization.

#### Lenses of Analysis:
1. **Technology / Operations** — Architecture, scalability, reliability, security, automation.  
2. **Data & Artificial Intelligence** — Governance, accuracy, ethics, cost, interpretability.  
3. **Legal & Regulatory** — Compliance, licensing, privacy, accessibility, approval timelines.  
4. **Finance & Economics** — ROI, Payback, NPV, IRR, unit economics, elasticity, sensitivity.  
5. **Market & Competition** — TAM/SAM/SOM, pricing, segmentation, demand and supply, adoption.  
6. **Communication & Marketing** — Message, channels, audience, perception, performance.  
7. **Behavioral & Human Factors** — Frictions, biases, nudges, ethics, experimentation.  
8. **Internal / Organizational** — Resources, governance, maturity, capabilities, hiring times.  
9. **Organizational Strategy** — Long-term alignment, coherence, adaptability, sustainability, leadership.

Each lens must conclude with a **WHY-chain (evidence → inference → implication)** justifying the findings.  
Always include explicit units, timeframes, and provenance cues (document ID, URL, or access date).

The outcome of this phase must be a **deep interdisciplinary synthesis**, combining all findings into a coherent and balanced framework that merges both traditional and innovative views.

────────────────────────────────────────────────────────────────────────────
### PHASE 3 — RISKS, INTERDEPENDENCIES & CROSS-CONSISTENCY

**Goal:** Identify risks, dependencies, and contradictions that may affect feasibility or decision integrity.

**Tasks:**
- Maintain an **Integrated Risk Register** including probability × impact, category, owner, due date, and mitigation measures.  
- Classify risks by **lens or domain**, level of criticality, and urgency.  
- Build a **Dependency Map** illustrating how domains influence each other (e.g., Technology ↔ Finance ↔ Market).  
- Check for **cross-lens consistency** — ensure no contradictions between metrics or assumptions.  
- Prioritize risks and dependencies based on their influence on time, cost, adoption, or compliance.  

The result of this phase is a **consolidated risk profile** with evidence-based dependencies and clear mitigation recommendations.

────────────────────────────────────────────────────────────────────────────
### PHASE 4 — CRITERIA, STRATEGIC ALTERNATIVES & VERDICT

**Goal:** Lock decision criteria, evaluate strategic alternatives, and issue an evidence-based verdict.

#### 4.1 Criteria Lock
- Derive **5–8 dynamic criteria** aligned with the contextual evidence.  
- Define for each: **weight (Σ=1.00)**, **Warn/Alert thresholds**, **owner**, **cadence**, and a clear **WHY justification**.  
- Document **normalization rules (0–1)**, lower and upper bounds, units, and at least **one worked example**.  
- Seal the lock with **timestamp, version, and SHA256 hash** of the criteria text, ensuring reproducibility and citation by downstream agents.  
- Any change requires a **formal Change Request**, governance review, and version bump.

#### 4.2 Strategic Alternatives
- Define and compare at least **three alternatives** (e.g., Growth vs Compliance, Expansion vs Focus, Digital vs Human-led).  
- For each, describe the **core hypothesis**, **expected impacts**, and the **WHY-chain** (evidence → inference → implication).  
- Score each option using the **locked criteria** (no weight edits).  
- Explain differences in scoring and strategic implications.  
- Highlight both **traditional/established options** that work and **innovative or experimental ones** that could create future value.

#### 4.3 Final Verdict
- Deliver a **Go / No-Go / Conditional** verdict with **quantified thresholds** (time, cost, performance).  
- Set a **decision horizon** (0–14 / 15–30 days) with owners, resources, and budget.  
- Summarize the overall rationale in **three WHY-chains**, reflecting the major lenses.

────────────────────────────────────────────────────────────────────────────
### DATA GAPS & COLLECTION PLAN

Record any missing information systematically:

| Gap | Why It Matters | Method | Owner | ETA | Acceptance Criteria | Expected Source |
|-----|----------------|---------|--------|------|----------------------|-----------------|

────────────────────────────────────────────────────────────────────────────
### FINAL ACCEPTANCE CHECKLIST (ALL MUST BE TRUE)

- Contextual data collection completed and validated.  
- Nine lenses analyzed and documented with both traditional and innovative views.  
- Integrated Risk Register and Dependency Map created.  
- 5–8 criteria locked (Σ=1.00).  
- Thresholds, normalization, and worked example included.  
- Minimum of three strategic alternatives evaluated.  
- Final verdict issued with quantified thresholds and timeline.  
- Data Gaps Plan present and complete.  
- WHY-chains coherent and complete across all phases.  
- No invented data.  
"""
        expected_output = f"""
# Deep Multidisciplinary Feasibility & Strategy — Locked, Auditable Report

> **Non-negotiables**
> • Every claim includes a **WHY** (evidence → inference → implication).  
> • Every metric has an explicit **unit** and **timeframe**.  
> • **Provenance** (Doc-ID/§ or URL + access date) accompanies all material facts.  
> • Minimum content rules are enforced (row counts noted per section).  
> • Tables use stable IDs (COLLECT-#, TECH-#, DATA-#, LEG-#, FIN-#, MKT-#, COMMS-#, BEH-#, ORG-#, STRATORG-#, RISK-#, CRIT-#).  
> • Each discipline provides: **what should be done**, **why it’s relevant/interesting**, and **how it adds value/impact**.  
> • Each discipline contains **Traditional (proven) view** and **Innovative (novel) view**; keep proven practices when they work, and also propose valuable new approaches.  
> • The analyst **becomes an updated expert** in each field at analysis time.

---

## 0) Executive Summary (≤1 page; REQUIRED)
- **Objective & Context (1–2 lines):** [problem/goal; source cue]  
- **Top5 quantified drivers:**  
  1) [metric + value + timeframe] — [provenance]  
  2) [metric + value + timeframe] — [provenance]  
  3) [metric + value + timeframe] — [provenance]
  4) [metric + value + timeframe] — [provenance]
  5) [metric + value + timeframe] — [provenance]  
- **Verdict (preview):** Go / Conditional / No-Go — with measurable conditions (threshold + date + evidence).  
- **Decision timeline (preview):** 0–14d / 15–30d (owners, effort [hours], budget [€]).  
**WHY:** evidence → inference → implication.

---

## 1) Phase 1 — Adaptive Contextual Synthesis & Data Collection (REQUIRED)
**Goal:** Build a complete, up-to-date, evidenced context before any scoring.

### 1.1 Inputs & Sources
- **Documents/Systems ingested:** [list with Doc-ID/System + access date]  
- **External web research topics & findings:** [bullets with URLs + access dates]  
- **Objective/Decision statement:** [1–2 sentences; cite source]

### 1.2 Domain Relevance Map
| Domain/Lens | Relevance (H/M/L) | Why Relevant | Evidence (provenance) |
|-------------|-------------------|--------------|-----------------------|
| [Tech/Ops] | [..] | [..] | [..] |
| [Data/AI] | [..] | [..] | [..] |
| ... | ... | ... | ... |

### 1.3 Assumptions & Hard Constraints (≥4)
| ID | Type (Legal/Tech/Time/Budget/Quality) | Statement | Unit/Limit | Source/Date | WHY binding |
|----|---------------------------------------|-----------|------------|-------------|-------------|
| CONSTR-1 | [..] | [..] | [..] | [..] | [..] |
| CONSTR-2 | [..] | [..] | [..] | [..] | [..] |
| CONSTR-3 | [..] | [..] | [..] | [..] | [..] |
| CONSTR-4 | [..] | [..] | [..] | [..] | [..] |

### 1.4 Data Gaps & Collection Plan (initial)
| Gap | Why It Matters | Method (instrument/test/query) | Owner | ETA | Acceptance Criteria | Expected Source |
|-----|----------------|---------------------------------|-------|-----|---------------------|-----------------|
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |

**Proceed only when contextual collection is validated.**

---

## 2) Phase 2 — Deep Multidisciplinary Analysis (Nine Lenses; REQUIRED)
**Goal:** Exhaustive cross-domain analysis with explicit units/timeframes and provenance.  
**For each lens include:** (A) **What to do**, (B) **Why relevant/interesting**, (C) **How it adds value/impact**, (D) **Traditional (proven)** view, (E) **Innovative (novel)** view, (F) **WHY-chain**.

> The analyst becomes an **updated expert** in each lens at analysis time.

### 2.1 Technology / Operations (≥5 rows)
**Tech Assessment Matrix**  
| ID | Capability/Topic | Current | Target/SLO (unit) | Fit/Gap | Effort (S/M/L) | Key Risk | Mitigation | Owner | Due | Source | WHY |
|----|------------------|--------|--------------------|--------|----------------|----------|-----------|-------|-----|--------|-----|
| TECH-1 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| TECH-2 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| TECH-3 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| TECH-4 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| TECH-5 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |

**Interfaces & Data Contracts (≥5)**  
| System | API/Data | Schema fields | SLA (unit) | Volume (unit/period) | Latency (ms) | Error (%) | Dependencies | Source | WHY |
|--------|----------|---------------|------------|----------------------|--------------|----------:|--------------|--------|-----|
| [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |

**Security & Privacy (≥5)**  
| Asset | Data Class | Control | STRIDE Threat | Residual Risk | Mitigation | Owner | Source | WHY |
|-------|-----------|---------|---------------|---------------|-----------|-------|--------|-----|
| [..]  | [..]      | [..]    | [..]          | [..]          | [..]      | [..]  | [..]   | [..] |
| [..]  | [..]      | [..]    | [..]          | [..]          | [..]      | [..]  | [..]   | [..] |
| [..]  | [..]      | [..]    | [..]          | [..]          | [..]      | [..]  | [..]   | [..] |
| [..]  | [..]      | [..]    | [..]          | [..]          | [..]      | [..]  | [..]   | [..] |
| [..]  | [..]      | [..]    | [..]          | [..]          | [..]      | [..]  | [..]   | [..] |


**Traditional vs Innovative (narrative bullets).**

---

### 2.2 Data & Artificial Intelligence (≥5 rows)
| ID | Data/Model Topic | Current | Target (unit) | Gaps | Risk | Mitigation | Owner | Due | Source | WHY |
|----|------------------|--------|---------------|------|------|-----------|-------|-----|--------|-----|
| DATA-1 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| DATA-2 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| DATA-3 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| DATA-4 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| DATA-5 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |

**Traditional vs Innovative (narrative bullets).**

---

### 2.3 Legal & Regulatory (≥5 items)
**Compliance Register**  
| ID | Requirement | Applicability | Gap | Risk (p×i) | Mitigation | Owner | Deadline | Evidence | WHY |
|----|------------|--------------|-----|------------|-----------|-------|----------|---------|-----|
| LEG-1 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| LEG-2 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| LEG-3 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| LEG-4 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| LEG-5 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |

**Traditional vs Innovative (narrative bullets).**

---

### 2.4 Finance & Economics (formulas & units REQUIRED)
**Scenario Summary (Optimistic / Base / Pessimistic)**  
| KPI | Formula | Inputs (unit) | Base | O | P | Source | WHY |
|-----|---------|----------------|-----:|---:|---:|-------|-----|
| ROI % | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| Payback (months) | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| NPV (€ @ WACC=..) | [..] | [WACC inputs] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | 
| [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |

**Unit Economics (≥5 segments)**  
| Segment | ARPU (€/period) | COGS (€/unit) | GM % | CAC (€/cust) | Payback (months) | LTV (€/cust) | LTV:CAC | Source | WHY |
|---------|------------------:|---------------:|-----:|--------------:|------------------:|--------------:|--------:|--------|-----|
| [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |

**Sensitivity (Tornado) — top 5 drivers**  
| Driver | Δ Assumption (unit) | Impact on KPI | Method | Source | WHY |
|--------|----------------------|---------------|--------|--------|-----|
| [..] | [±..] | [±..] | [Spearman/one-at-a-time] | [..] | [..] |
| [..] | [±..] | [±..] | [..] | [..] | [..] |
| [..] | [±..] | [±..] | [..] | [..] | [..] |
| [..] | [±..] | [±..] | [..] | [..] | [..] |
| [..] | [±..] | [±..] | [..] | [..] | [..] |

**Traditional vs Innovative (narrative bullets).**

---

### 2.5 Market & Competition (≥10 rows across tables)
- **TAM–SAM–SOM** (top-down & bottom-up) with reconciliation and CAGR.  
- **Pricing & Elasticity** (own/cross ε) with method and horizon.  
- **Competition & Positioning** (table + map).  
- **GTM/Channels** (CAC/LTV/Payback; funnel).  
- **Supply Constraints** (capacity [units/period], lead time [days], SLAs).  
**Traditional vs Innovative (narrative bullets) + WHY-chains.**

---

### 2.6 Communication & Marketing (≥7 rows)
**Audience–Message–Channel Matrix**  
| Audience | Message | Channel | Cadence | KPI (open/CTR/conv/sentiment) | Owner | WHY |
|----------|---------|---------|---------|--------------------------------|------|-----|
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |

**Traditional vs Innovative (narrative bullets).**

---

### 2.7 Behavioral & Human Factors (≥7 interventions)
**Barrier → Lever Mapping & Experiments**  
| ID | Barrier | Lever (bias/heuristic) | Intervention (what/where) | Expected Lift (unit, timeframe) | Guardrails/Ethics | Experiment (α, power, MDE, n, duration) | Telemetry | Owner | WHY |
|----|---------|------------------------|---------------------------|---------------------------------|-------------------|-------------------------------------------|----------|-------|-----|
| BEH-1 | [..] | [defaults/friction/etc.] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| BEH-2 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| BEH-3 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| BEH-4 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| BEH-5 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| BEH-6 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| BEH-7 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |

**Traditional vs Innovative (narrative bullets).**

---

### 2.8 Internal / Organizational (≥5 items)
**Capability & Gap Analysis / RACI (draft) / Capacity & Hiring**  
| ID | Capability/Role | Current FTE | Need (FTE) | Time-to-Fill (days) | Gap/Risk | Mitigation | Owner | WHY |
|----|-----------------|------------:|-----------:|--------------------:|---------|-----------|-------|-----|
| ORG-1 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| ORG-2 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| ORG-3 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| ORG-4 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| ORG-5 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |

**Traditional vs Innovative (narrative bullets).**

---

### 2.9 Organizational Strategy (≥4 items)
| ID | Strategic Theme | Current Fit | Target Fit | Gap | Dependency Risk | Action | Owner | Due | Source | WHY |
|----|-----------------|------------:|-----------:|----:|-----------------|--------|-------|-----|--------|-----|
| STRATORG-1 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| STRATORG-2 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| STRATORG-3 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| STRATORG-4 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |

**Traditional vs Innovative (narrative bullets).**

---

## 3) Phase 3 — Cross-Lens Risks & Interdependencies (≥8 risks)
**Integrated Risk Register**  
| ID | Description | Lens | Prob (0–1) | Impact (€/k or 0–1) | Score | Early Signal | Mitigation | Owner | Due | Provenance | WHY |
|----|-------------|------|-----------:|---------------------:|------:|-------------|-----------|-------|-----|-----------|-----|
| RISK-1 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| RISK-2 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| RISK-3 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| RISK-4 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| RISK-5 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| RISK-6 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| RISK-7 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| RISK-8 | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] | [..] |

**Dependency Map (Critical Path)** — predecessors → successors; note effects on time/cost/adoption.  
**Cross-Consistency Check** — list any contradictions found; resolutions.

---

## 4) Phase 4 — Criteria Lock, Strategic Alternatives & Final Verdict

### 4.1 Criteria — Version & Lock (5–8 criteria REQUIRED)
**Criteria Version:** v1.0  
**Locked At:** {current_timestamp}  
**Lock Hash (SHA256 of criteria text):** criteria-v1.0:<computed-lock-hash>  
*(Cite this hash in ALL downstream agents.)*

> **Requirement:** 5–8 context-derived criteria. Weights must sum to **1.00**.  
> Each criterion must specify metric, unit, cadence, owner, thresholds (Warn/Alert), normalization rule (0–1), and a one-line WHY.

**Locked Decision Criteria (Σ weights = 1.00)**  
| ID | Criterion | Group (Outcome/Constraint) | Weight | Metric | Unit | Source/System | Cadence | Threshold (Warn/Alert) | Owner | WHY |
|----|-----------|----------------------------|------:|--------|------|---------------|---------|------------------------|-------|-----|
| CRIT-1 | [Derived] | [..] | 0.XX | [e.g., ROI_12m, Conv%] | [..] | [System/Doc] | [..] | [Warn/Alert] | [Role/Name] | [1-line] |
| CRIT-2 | [Derived] | [..] | 0.XX | [e.g., Time_to_Impact] | [..] | [System/Doc] | [..] | [Warn/Alert] | [Role/Name] | [1-line] |
| CRIT-3 | [Derived] | [..] | 0.XX | [e.g., Compliance_{{reg}}] | [..] | [System/Doc] | [..] | [Warn/Alert] | [Role/Name] | [1-line] |
| CRIT-4 | [Derived] | [..] | 0.XX | [e.g., Reliability_SLO] | [..] | [System/Doc] | [..] | [Warn/Alert] | [Role/Name] | [1-line] |
| CRIT-5 | [Optional] | [..] | 0.XX | [...] | [..] | [System/Doc] | [..] | [Warn/Alert] | [Role/Name] | [1-line] |
| CRIT-6 | [Optional] | [..] | 0.XX | [...] | [..] | [System/Doc] | [..] | [Warn/Alert] | [Role/Name] | [1-line] |
| CRIT-7 | [Optional] | [..] | 0.XX | [...] | [..] | [System/Doc] | [..] | [Warn/Alert] | [Role/Name] | [1-line] |
| CRIT-8 | [Optional] | [..] | 0.XX | [...] | [..] | [System/Doc] | [..] | [Warn/Alert] | [Role/Name] | [1-line] |

**Weights (sum):** **1.00**

#### Normalization Rules (0–1; floors/caps REQUIRED)
| Criterion | Rule (math) | Floor → Cap (unit) | Example Input (unit) | Normalized Score | Provenance |
|-----------|-------------|--------------------|----------------------|------------------:|------------|
| [CRIT-#]  | [f(x)=…]    | [min → max]        | [value]              | [0.00–1.00]       | [Doc/URL+date] |

**Worked Example (Scoring) — REQUIRED**  
| Criterion | Measured Value | Unit | Normalized (0–1) | Weight | Contribution (=Norm×W) | WHY |
|-----------|----------------|------|------------------:|-------:|-----------------------:|-----|
| [CRIT-1]  | [..]           | [..] | 0.XX              | 0.XX   | 0.XX                   | [reason + provenance] |
| [CRIT-2]  | [..]           | [..] | 0.XX              | 0.XX   | 0.XX                   | [reason + provenance] |
| **Total** | —              | —    | —                 | **1.00** | **0.XX**             | **Decision threshold rationale** |

**Governance (immutable once locked)**  
- Changes require **Change Request**, quorum ≥ **2/3**, **version bump**, and a **new lock hash**.  
- Any conflicting numbers elsewhere → record under **Corrections & Consistency** and align to this lock.

---

### 4.2 Strategic Alternatives (≥5 options; scored with the locked criteria)
| Strategy Option | Total (0–1) | Per-Criterion Scores (CRIT-1..n) | Strengths | Risks | Dependencies | Recommendation | WHY Summary (1–2 lines) |
|-----------------|-------------:|----------------------------------|-----------|-------|--------------|----------------|--------------------------|
| Option 1 | 0.XX | [..] | [..] | [..] | [..] | [..] | [..] |
| Option 2 | 0.XX | [..] | [..] | [..] | [..] | [..] | [..] |
| Option 3 | 0.XX | [..] | [..] | [..] | [..] | [..] | [..] |
| Option 4 | 0.XX | [..] | [..] | [..] | [..] | [..] | [..] |
| Option 5 | 0.XX | [..] | [..] | [..] | [..] | [..] | [..] |

**Diversity check:** options should not be >75% similar; note penalties if they are.  
Include **Traditional vs Innovative** considerations per option.

---

### 4.3 Strategic Verdict, Conditions & Timeline (REQUIRED)
**Verdict:** **Go / Conditional / No-Go**  
**Conditions (if Conditional):** measurable thresholds by date with evidence source.  
**Rationale (3 WHY bullets):**  
- **Finance/Economics:** evidence → inference → implication  
- **Technology/Delivery:** evidence → inference → implication  
- **Market/Behavior/Strategy:** evidence → inference → implication  

**Decision Timeline**  
- **0–14 days:** tasks, owners, hours, € (measurable)  
- **15–30 days:** tasks, owners, hours, € (measurable)

---

## 5) Corrections & Consistency (REQUIRED when mismatches exist)
| Item Found | Where | Conflict | Resolution (align to this Lock) | Owner | Due |
|------------|-------|----------|----------------------------------|-------|-----|
| [..] | [..] | [..] | [..] | [..] | [..] |

---

## 6) Data Gaps & Collection Plan (MANDATORY for each TBD; ≥5 rows if gaps exist)
| Gap | Why It Matters | Method (instrument/test/query) | Owner | ETA | Acceptance Criteria | Expected Source |
|-----|----------------|---------------------------------|-------|-----|---------------------|-----------------|
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |
| [..] | [..] | [..] | [..] | [..] | [..] | [..] |

---

## 7) Acceptance Checklist (ALL must be TRUE)
- contextual_data_collection_completed_and_validated == **true**  
- nine_lenses_analyzed_with_traditional_and_innovative_views == **true**  
- integrated_risk_register_and_dependency_map_present == **true**  
- dynamic_criteria_count_between_5_and_8 == **true**  
- weights_sum_to_1_00 == **true**  
- normalization_rules_and_worked_example_present == **true**  
- governance_change_request_and_quorum_defined == **true**  
- ≥3_strategic_alternatives_scored_with_locked_criteria == **true**  
- strategic_verdict_with_quantified_thresholds_and_timeline == **true**  
- data_gaps_collection_plan_present == **true**  
- provenance_present_for_all_material_claims == **true**  
- why_chain_present_after_each_table_or_block == **true**

---

## 8) Traceability & Provenance
- **Sources (Doc IDs/Systems + dates):** [list all key items with access dates]  
- **Web references (if used):** [URL + access date]  
- **Tools Used:** CriteriaLockerTool, JSONSchemaValidatorTool, RiskRegisterTool, MarketSizingTool, ElasticityEstimatorTool, TimeSeriesForecastTool, PositioningMapTool, UnitEconomicsTool, MarkdownFormatterTool, CodeInterpreterTool.  
- **Reproducibility:** normalization rules, data snapshots, seeds, versions.

## Appendices
- **A. Formulas & Definitions:** ROI, NPV (WACC inputs), IRR, Payback, LTV, CAC, GRR/NRR, elasticity.  
- **B. Sensitivity (tornado):** driver deltas → KPI deltas.  
- **C. Draft RACI & Governance details.**  
- **D. Compliance evidence (DPIA, DPA/SCC, ISO/SOC, WCAG).**  
- **E. Experiment designs (metrics, α/power/MDE, analysis plans).**
"""


        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            markdown=True,
            output_file="02_feasibility_report.md"
        )