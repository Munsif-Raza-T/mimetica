# -*- coding: utf-8 -*-

from crewai import Agent
from tools.custom_tools import CodeInterpreterTool
from config import config
import streamlit as st


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
            role="Multidisciplinary Feasibility, Criteria & Market Specialist",
            goal=(
                "Run DECIDE's Define/Establish stages as both a domain specialist and an overall decision architect. Commit to: "
                "1) Build and LOCK a weighted decision-criteria matrix before scoring any options; "
                "2) Execute deep feasibility across seven lenses (Technology, Legal/Regulatory, Finance, Market/Competition, "
                "Internal/Organizational, Communication, Behavioral) using domain-standard methods and quantitative outputs; "
                "3) Map cross-lens interdependencies and risks (prob×impact) with owners and due dates; "
                "4) Evaluate ≥2 decision frames to avoid single-track conclusions; "
                "5) Score Conservative / Balanced / Bold solution archetypes using ONLY the locked criteria, showing per-criterion contributions; "
                "6) Issue a defensible Go/No-Go/Conditional verdict with explicit conditions, thresholds, and a 0–14 / 15–30 day decision timeline; "
                "7) ALWAYS explain the WHY (evidence → inference → implication) behind every major claim."
            ),
            backstory=(
                "You are a senior structured-decision consultant who can become a domain specialist on demand and synthesize at the end. "
                "Your craft blends standards from each field:\n"
                "• Technology: architecture reviews, integration design, SRE golden signals, capacity & reliability planning, security (STRIDE cues);\n"
                "• Legal/Regulatory: GDPR/DPIA mindset, data residency, IP/contracting, sector obligations and approval timelines;\n"
                "• Finance: NPV/ROI across Optimistic/Base/Pessimistic scenarios, sensitivity to price/demand/cost drivers, payback/ROI guardrails;\n"
                "• Market/Competition: TAM–SAM–SOM (top-down & bottom-up), segmentation & JTBD, forecasting and price elasticity, "
                "supply constraints, competitor archetypes and positioning maps;\n"
                "• Internal/Organizational: capability/readiness diagnostics, governance patterns, RACI drafting, change impact mapping;\n"
                "• Communication: audience–message–channel mapping, change-comms milestones, outcome measurement;\n"
                "• Behavioral: friction/bias audits (status quo, present bias, loss aversion) and levers (social norms, defaults, salience). "
                "Principles: lock criteria before scoring; surface assumptions and gaps; quantify uncertainty; prefer reproducible reasoning; "
                "and narrate each decision with evidence → inference → recommendation."
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
        return Task(
            description=(
                f"""
Conduct a comprehensive **multidisciplinary feasibility analysis** based strictly on the processed inputs.
For **every** statement (finding, claim, metric, choice, recommendation), **explicitly explain the WHY**
as a short chain: **evidence → inference → implication**. Include **units** for all quantities and specify
**what the number is measured against** (period, cohort, baseline, benchmark). When data is missing, mark
**TBD** and create a **Data Gap & Collection Plan** entry (method, owner, ETA, acceptance criteria).
Do **not** invent facts. Do **not** omit material details.

Available Context (already processed; treat as ground truth):
{context_data}

NON-NEGOTIABLE PRINCIPLES
- **Evidence-first**: Use only what is present in the inputs. If something is not present, label it **TBD** and add a collection plan.
- **WHY for everything**: For each item (problem, cause, objective, scope, KPI, constraint, dependency, risk, frame, verdict),
  add one concise WHY explaining causal logic, trade-offs, and how the input evidence supports it.
- **Units & frames**: Every metric must include its **unit** (€, $, %, hours/week, points, units/day, etc.) and **frame** (per month, per quarter, cohort, vintage, region).
- **Provenance**: Add a short source cue for each claim, e.g., *(Source: Context §2)*. If exact sectioning is not available, use
  a clear pointer (document name / page / figure).
- **Alternatives considered**: When you set a target, choose a KPI, or set a scope boundary, mention at least one serious alternative
  and briefly explain **why it was rejected**.
- **Testable assumptions**: Any assumption must include a test plan (method, data needed, owner, ETA) and a note on **why the assumption is reasonable** now.
- **Executive-ready formatting**: Prefer compact lists and tables; keep language plain and unambiguous.
- **Reproducibility**: When you run calculations, include the **formula** and the **inputs** (with units) so downstream agents can recompute.

MISSION (DECIDE – Define/Establish)
1) Precisely define the problem (**Symptom → Likely Cause → Opportunity**) and surface assumptions, hard constraints, and knowledge gaps.
2) Build and **LOCK** a weighted decision-criteria matrix (Outcomes, Constraints, Preferences) **before** reviewing options or issuing any verdict.
3) Execute deep feasibility across **seven lenses** using domain-standard methods and quantitative tables:
   Technology, Legal/Regulatory, Finance, Market/Competition, Internal/Organizational, Communication, Behavioral.
4) Produce cross-lens **risk analysis** (probability × impact) with interdependencies, owners, and deadlines.
5) Evaluate **≥ 2 decision frames** (e.g., Value-at-Risk vs Speed-to-Learn; Share-Grab vs Profit-First) to avoid single-track conclusions.
6) Score **three solution archetypes** (Conservative / Balanced / Bold) using **only** the **LOCKED** criteria; disclose per-criterion contributions.
7) Issue a defendable **Go / No-Go / Conditional** verdict with **explicit thresholds, conditions**, and a **0–14 / 15–30 day** decision timeline.

GENERAL INSTRUCTIONS
- Call out **assumptions** explicitly when data is missing; list **knowledge_gaps** and how to validate them.
- Quantify ranges (**Optimistic/Base/Pessimistic**) and add **sensitivity** to key drivers (price, demand/volume, cost, capacity, timing).
- Use structured **tables** and **bullets** for clarity; make the output **printable** and **executive-ready**.
- If available, leverage specialist tools (JSONSchemaValidatorTool, CriteriaLockerTool, RiskRegisterTool, MarketSizingTool,
  ElasticityEstimatorTool, TimeSeriesForecastTool, PositioningMapTool, UnitEconomicsTool, MarkdownFormatterTool, CodeInterpreterTool)
  to validate structure, run calculations, and format tables. If a tool is not available, proceed with manual, clearly explained methods.

A) PROBLEM DEFINITION (DECIDE: Define)
- **Core Problem (3 levels):** Symptom, Likely Cause, Opportunity — each with a **WHY** and *(Source: …)*.
- **Business Impact (with units & formula):** quantify if possible; state time horizon and baseline; add *(Source: …)*.
- **Assumptions & Hard Constraints:** legal/tech/time/budget/quality windows — each with **WHY binding** and *(Source: …)*.
- **Knowledge Gaps & Validation Plan:** what data/experiment is needed, **by whom**, **when**, **method**, **acceptance criteria**.

B) DECISION CRITERIA CONSTRUCTOR (DECIDE: Establish) — **MUST BE LOCKED**
- **Groups:** Outcomes (ROI, NPS, OEE, Adoption, Time-to-Impact…), Constraints (GDPR/DPIA, security, compatibility, budget/window…),
  Preferences (stakeholder priorities).
- For each criterion: **name, group, weight (0–1), metric, unit, data source/system, cadence, thresholds (warn/alert), WHY it matters**.
- **Weights MUST sum to 1.** Explicitly **LOCK** the matrix (state that weights cannot change thereafter).
- (If available) Validate **lock** & **weights==1** with CriteriaLockerTool and JSONSchemaValidatorTool.

C) MULTIDISCIPLINARY FEASIBILITY — Seven Lenses (Deep, Evidence-First, Unit-Specified)

> **Instruction for all lenses:**  
> For every finding, include **evidence → inference → implication (WHY)**.  
> For every metric, include **unit**, **time frame** (per day/week/month/quarter/annual), **baseline date**, **formula**, and **source system/document**.  
> If data is missing, mark **TBD** and add it to the **Data Gap & Collection Plan** (method, owner, ETA, acceptance criteria).

---

### 1. Technology Feasibility (Architecture • Data • Reliability • Security • Cost)

**Scope & Core Questions**  
- Architecture fit to current stack? Data and API integration feasibility (latency budgets, throughput caps)?  
- Reliability targets (SLO/SLI/SLA), scalability headroom, capacity/cost envelopes?  
- Security posture (STRIDE/OWASP), identity, least privilege, data protection (PII/PHI), auditability?  
- Operability: observability, alerting (MTTD/MTTR), runbooks, SRE readiness?  
- Tech debt, migration strategy, environments (dev/test/stage/prod), rollback plans?

**Required Inputs (Examples)**  
- Current system diagrams, interface specs, API quotas, data catalogs, lineage; cloud accounts/cost reports; security policies; incident history.

**Methods & Quantification**  
- **Performance budgets:** end-to-end latency [ms], p95/p99; throughput [req/s]; error rates [%].  
- **Reliability math:** availability target SLA [%/year]; error budget hours [h/quarter]; SLI definitions.  
- **Scalability & capacity:** load-model assumptions, autoscaling rules; storage growth [GB/month]; retention [days].  
- **Security:** STRIDE checklist, authn/authz model, data-at-rest/in-transit encryption specs; secrets mgmt; vulnerability baseline (CVSS).  
- **Cloud FinOps:** unit cost [$/1k req], [$/GB stored/month], [$/GB egress]; cost-to-serve per user/event.  
- **Data quality:** freshness [min], completeness [%], accuracy [%], nulls per column [%].

**Deliverables (Tables)**  
**Tech Assessment Matrix**  
| Capability/Topic | Current State | Target/SLO (unit) | Fit/Gap | Integration Effort (S/M/L) | Key Risk | Mitigation | Owner | Due | Source | WHY |
|---|---|---|---|---|---|---|---|---|---|---|

**Interface & Data Contract Inventory**  
| System | API/Data Set | Fields | SLA (unit) | Volume (unit/period) | Latency (ms) | Errors (%) | Dependent Services | Source | WHY |

**Security & Privacy Map**  
| Asset | Data Class (PII/PHI/confidential) | Control (encryption, DLP, RBAC) | Threat (STRIDE) | Residual Risk (L/M/H) | Mitigation | Owner | Source | WHY |

**Acceptance Gates (Yes/No)**  
- SLOs defined & error budget computed; interfaces documented; cost-to-serve quantified; critical risks mitigated or conditionally gated.

---

### 2. Legal & Regulatory (Compliance • IP/Contracts • Approvals • Recordkeeping • Accessibility)

**Scope & Core Questions**  
- Which laws/regulations apply (GDPR/DPIA, HIPAA, PCI-DSS, SOC/ISO, sector rules)? Lawful basis?  
- Cross-border data flows; DPAs, SCCs; data residency?  
- IP ownership/licensing (including OSS licenses), indemnities, warranties, limitation of liability?  
- Consumer protection/advertising/competition law? Accessibility (WCAG 2.1 AA)? Retention & deletion SLAs?

**Required Inputs**  
- Data maps, processing purposes, vendor list & contracts, OSS bill of materials (SBOM), current certifications, prior DPIAs/LIAs.

**Methods & Quantification**  
- **Risk scoring:** probability × impact (impact in €/$ or L/M/H).  
- **Lead times:** expected approval durations [days/weeks]; review cycles.  
- **Accessibility metrics:** % components WCAG-compliant; defects per audit.  
- **Records:** retention windows [days/months/years], deletion SLAs [days].

**Deliverables (Tables)**  
**Compliance Register**  
| Requirement | Applicability | Current Gap | Risk (p×i) | Mitigation | Owner | Deadline | Evidence/Source | WHY |

**Data Transfer & Residency**  
| Data Category | Location(s) | Transfer Mechanism | DPA/SCC Status | Risk | Control | Source | WHY |

**IP/Contractual Terms**  
| Agreement | Scope | Key Clause (IP/Indemnity/LoL) | Risk | Mitigation | Counterparty | Renewal Date | Source | WHY |

**Acceptance Gates**  
- Lawful basis documented; DPIA completed (if required); DPAs/SCCs in place; accessibility plan with targets; retention/deletion documented.

---

### 3. Financial Feasibility (Model • Scenarios • Sensitivity • Unit Economics • Guardrails)

**Scope & Core Questions**  
- Investment & operating profile (CAPEX/OPEX) and timeline? Funding route?  
- Economics at unit and cohort level (gross/contribution margin %, LTV:CAC, payback [months])?  
- Scenario outcomes (Optimistic/Base/Pessimistic) for NPV, IRR, ROI [%], breakeven [months]?  
- Sensitivity to key drivers (price, volume, churn, COGS, CAC, FX, tax)? Working capital needs?

**Required Inputs**  
- Cost catalogs, staffing plans, pricing/discounts, funnel metrics, retention curves, tax rates, WACC/discount rate.

**Methods & Formulas**  
- **ROI [%]** = (Net Benefits / Investment) × 100.  
- **NPV [€/$]** = Σ (CashFlow_t / (1 + r)^t) − Initial CAPEX; **IRR [%]** solving NPV=0.  
- **Payback [months]** = months until cumulative cash flow ≥ 0.  
- **LTV [€/$]** = ARPU × Gross Margin % × Customer Lifetime [months].  
- **CAC [€/$]** = Acquisition Spend / New Customers; **LTV:CAC** ratio (unitless).  
- **Contribution Margin [%]** = (Revenue − Variable Costs) / Revenue × 100.

**Deliverables (Tables)**  
**Scenario Summary (O/B/P)**  
| KPI | Formula | Inputs (unit) | Base | Optimistic | Pessimistic | Source | WHY |
|---|---|---|---:|---:|---:|---|---|

**Unit Economics**  
| Segment/Channel | ARPU (€/period) | COGS (€/unit) | Gross Margin % | CAC (€/cust) | Payback (months) | LTV (€/cust) | LTV:CAC | Source | WHY |

**Sensitivity (Tornado-Style)**  
| Driver | Δ Assumption (unit) | Δ ROI (pp) | Δ NPV (€/k) | Δ Payback (months) | Source | WHY |

**Guardrails & Triggers**  
- **Min ROI** ≥ X %; **Max Payback** ≤ Y months; **Risk Budget** ≤ Z €/$; trigger actions if breached.

**Acceptance Gates**  
- Model ties to sources; units/time frames defined; O/B/P complete; sensitivity shows dominant drivers; guardrails set.

---

### 4. Market & Competition (Demand • Segmentation • Pricing • Supply • Rivalry • GTM)

**Scope & Core Questions**  
- Market size (TAM/SAM/SOM) with assumptions and reconciliation? Growth (CAGR %)?  
- Segments & JTBD; pains/gains; adoption barriers; behavioral signals?  
- Demand forecast (method fit to data), forecast horizon [months], O/B/P bands?  
- Pricing power & elasticity; competitive responses; channel economics (CAC/LTV/payback)?  
- Supply constraints & SLAs (capacity [units/period], lead times [days])?

**Required Inputs**  
- Market reports, CRM/funnel, cohort retention, win/loss, pricing experiments, supply/vendor SLAs.

**Methods & Quantification**  
- **TAM/SAM/SOM**: top-down (macro × penetration) & bottom-up (units × price × conversion). Report both with assumptions.  
- **Forecasting**: naive, moving average, ARIMA/ETS, prophet-like—justify method; report MAPE/MAE where historical data exists.  
- **Elasticity**: own-price ε = (%ΔQ / %ΔP); cross elasticity if relevant. If unknown, propose experiment (sample size, duration).  
- **Porter forces**: qualitative with any quant signals (share %, HHI).  
- **Channel economics**: CAC, LTV, payback, conversion rates per stage (%).

**Deliverables (Tables)**  
**TAM–SAM–SOM**  
| Method | TAM (€/year) | SAM (€/year) | SOM (€/year) | Assumptions | CAGR (%/period) | Source | WHY |

**Segmentation & JTBD**  
| Segment | Size (units/period) | JTBD | Pains/Gains | Behavioral Signals | Priority | Source | WHY |

**Demand & Pricing**  
| Model | Horizon (months) | Base | O | P | MAPE/MAE | Price ε (own/cross) | Source | WHY |

**Supply-Side Constraints**  
| Capacity (units/period) | Lead Time (days) | Bottleneck | SLA Target | Risk | Cost Driver | Source | WHY |

**Competition & Positioning**  
| Player | Price Level | Feature Coverage (%) | Channels | Strengths | Weaknesses | Likely Response | Source | WHY |

**GTM & Channels**  
| Channel | CAC (€/cust) | LTV (€/cust) | Payback (months) | Conv. Funnel (%) | KPI | Owner | Source | WHY |

**Acceptance Gates**  
- Both TAM/SAM/SOM methods present & reconciled; forecast + horizon + O/B/P; elasticity measured or test plan; channel economics quantified.

---

### 5. Communication Strategy (Stakeholders • Message House • Channels • Change-Comms • Measurement)

**Scope & Core Questions**  
- Who needs what info, when, and via which channel to drive adoption and alignment?  
- What are the key messages (value, risk, progress) per audience?  
- How do we measure comms effectiveness (reach, engagement, conversion, sentiment)?

**Required Inputs**  
- Stakeholder maps, previous comms performance, brand guidelines, risk register, change calendar.

**Methods & Metrics**  
- **Message House**: Core promise → three proof points → call-to-action.  
- **Channel mix**: email, in-app, webinars, town halls, PR, social; match to audience media habits.  
- **KPIs**: Open Rate [%], CTR [%], Conversion [%], Reach (#), Engagement rate [%], Sentiment (−1..+1), Time-to-Read [s].  
- **Cadence**: weekly/monthly/quarterly; milestones aligned to program phases.

**Deliverables (Tables)**  
**Audience–Message–Channel Matrix**  
| Audience | Goal | Message (value/risk/progress) | Channel | Frequency | KPI | Owner | Source | WHY |

**Change-Comms Milestones**  
| Milestone | Date | Audience | Artifact | KPI | Risk | Mitigation | Owner | Source | WHY |

**Acceptance Gates**  
- Each audience has tailored message + channel + KPI; milestones align with risks & decision gates; measurement plan defined.

---

### 6. Behavioral & Cultural Factors (Biases • Frictions • Interventions • Experiments • Ethics)

**Scope & Core Questions**  
- What frictions (time/complexity/uncertainty) and biases (status-quo, present bias, loss aversion) block adoption?  
- What interventions (defaults, social proof, salience, commitment devices) will lift adoption?  
- How will we test them ethically and measure lift?

**Required Inputs**  
- Usage/abandonment logs, survey/interview insights, prior experiments, culture diagnostics.

**Methods & Metrics**  
- **Experiment design**: A/B or stepped-wedge; power calculation (α, β); sample size [n].  
- **Outcome metrics**: Adoption rate [%], Time-to-First-Value [days], Task completion [%], Drop-off [%], Retention [% at day N], NPS [points].  
- **Instrumentation**: event tracking definitions with timestamp and user cohort.  
- **Ethics**: informed consent (where applicable), risk minimization, DEI impact assessment.

**Deliverables (Tables)**  
**Barrier → Lever Mapping**  
| Barrier/Bias | Hypothesized Mechanism | Intervention (nudge) | Expected Lift (pp) | Metric (unit) | Test Design | Owner | Due | Source | WHY |

**Experiment Plan**  
| Hypothesis | Variant(s) | Sample Size (n) | Duration (days) | Primary Metric | Guardrails | Analysis Plan | Source | WHY |

**Acceptance Gates**  
- At least one prioritized barrier per key segment; testable lever with power-aware plan; adoption metrics & guardrails defined.

---

### 7. Internal / Organizational (Capabilities • Governance • RACI • Change Impact • Capacity)

**Scope & Core Questions**  
- Do we have the skills, bandwidth, and governance to deliver on time/quality/budget?  
- What org/process changes are required; what is the change impact; what is the training plan?  
- What is the critical path and where are the resourcing bottlenecks?

**Required Inputs**  
- Org chart, skills inventory, hiring plans/lead times [days], vendor contracts, PMO roadmap, current OKRs.

**Methods & Metrics**  
- **Readiness scoring**: capability scores [0–5]; risk heatmap.  
- **Capacity**: FTEs available [FTE], utilization [%], hiring pipeline (time-to-fill [days]).  
- **Change impact**: processes affected; training hours per role [h/person]; adoption KPIs.  
- **Governance**: decision rights, escalation paths, cadence (steering committee frequency).

**Deliverables (Tables)**  
**Capability & Gap Analysis**  
| Capability | Current (0–5) | Target (0–5) | Gap | Action | Owner | Due | Source | WHY |

**RACI (Draft)**  
| Workstream | Responsible | Accountable | Consulted | Informed | Decision Rights | Escalation | Source | WHY |

**Capacity & Hiring**  
| Role | Needed (FTE) | Available (FTE) | Gap (FTE) | Time-to-Fill (days) | Interim Plan | Owner | Source | WHY |

**Acceptance Gates**  
- Critical gaps have actions/owners/dates; governance & RACI defined; capacity plan covers critical path with quantified buffers.

---

**Cross-Lens Consistency Check (Mandatory)**  
- All lens outputs use consistent definitions and units; no contradictions between tech limits, legal gates, financials, market pacing, comms cadence, behavior tests, and org capacity.  
- Each lens concludes with a **WHY** paragraph tying findings to **decision criteria** and **risk register** entries.

D) CROSS-DIMENSIONAL RISK & INTERDEPENDENCY ANALYSIS
- Integrated risk register with **probability [0–1 or L/M/H] × impact [€/$ or L/M/H]**; cascading paths across lenses (e.g., legal → finance; tech → comms).
- Prioritization by (**weighted impact × probability**); mitigations, owners, deadlines.
- Dependency map (what must precede; **critical path**).
- (If available) Validate structure with **RiskRegisterTool**.
- **WHY:** make hidden coupling visible; de-risk the decision path.

E) DECISION FRAMES & VARIABILITY
- Evaluate **at least two frames** (e.g., Value-at-Risk vs Speed-to-Learn; Share-Grab vs Profit-First); explain **WHY** each fits the context.
- Summarize divergent implications; apply a **diversity penalty** if recommended actions are >75% similar.
- **WHY:** counteract confirmation bias; stress-test feasibility under different executive priorities.

F) MULTI-CRITERIA SCORING (ONLY THE **LOCKED** CRITERIA)
- Score three solution archetypes: **Conservative / Balanced / Bold**.
- Show **per-criterion contributions** and the **total**; **DO NOT** change weights after seeing scores.
- **WHY:** transparent trade-offs and reproducibility.

G) VERDICT, THRESHOLDS & TIMELINE
- **Go / No-Go / Conditional**; list explicit **conditions** and **thresholds** for a Conditional.
- Provide **Evidence → Inference → Recommendation** chain (3 bullets per key lens).
- Decision timeline: **0–14 days / 15–30 days** with responsible owners.
- **WHY:** actionable next steps and clear risk gates prior to commitment.

MANDATORY ACCEPTANCE CHECKS (YES/NO)
- criteria_locked == true
- weights_sum_to_1 == true
- risk_matrix_present == true
- min_two_frames == true
- go_nogo_with_thresholds == true
- technology_table_present == true
- legal_compliance_map_present == true
- finance_scenarios_and_sensitivity_present == true
- market_tam_sam_som_present == true
- segmentation_with_jtbd == true
- demand_forecast_with_obp == true
- elasticity_estimated_or_flagged == true
- supply_constraints_and_sla == true
- competition_profiles_and_positioning_map == true
- gtm_channels_with_cac_ltv_payback == true
- pricing_with_range_and_rationale == true
- unit_economics_reported == true
- comms_audience_channel_table_present == true
- behavioral_levers_table_present == true
- internal_capability_gap_table_present == true

Deliver an integrated analysis with cross-dimensional risk assessment and **clear, defendable recommendations**. 
Every table/metric must include **units**, **time frame**, and **source**; every conclusion must include a **WHY**.
"""
            ),
        
          expected_output=(
              
    """
# Multidisciplinary Feasibility Analysis — Executive & Technical Report

> **Non-negotiables for this document**
> - Include **all** relevant facts from inputs or mark them **TBD** with a **Data Gap & Collection Plan** (method, owner, ETA).
> - Every **number** must carry **units** (%, €, $, hrs/week, ms, req/s, items/month, points, etc.).
> - Every **claim/decision** must include a **Why** line that explains evidence → inference → implication.
> - Prefer **tables** for criteria, KPIs, risks, scopes, dependencies, and plans to enable downstream automation.
> - Use **stable IDs** consistently: CRIT-#, KPI-#, TECH-#, LEG-#, FIN-#, MKT-#, ORG-#, COMMS-#, BEH-#, DEP-#, RISK-#.

---

## 0) Executive Summary (≤ 1 page)

**Core Problem (Symptom → Likely Cause → Opportunity)**  
- **Symptom:** _TBD_  
- **Likely Cause:** _TBD_  
- **Opportunity:** _TBD_  
**Why:** Link observed patterns (with units/dates) to causal drivers and the value lever they unlock.

**Locked Decision Criteria (Top 5 by weight)**  
| ID | Criterion | Group (Outcome/Constraint/Preference) | Weight (0–1) | Metric | Unit | Threshold (Warn/Alert) | Why |
|---|---|---|---:|---|---|---|---|
| CRIT-1 | ROI_12m | Outcome | 0.XX | ROI | % | 10 / 5 | Capital efficiency is a gating KPI for Go/No-Go |

**Overall Feasibility Verdict**: **Go / No-Go / Conditional (pick one)**  
**Conditions/Thresholds (if Conditional)**: _TBD (with units & dates)_  
**Why this verdict:** Concise rationale referencing locked criteria, top risks, and cross-lens implications.

**Decision Timeline & Next Steps**  
- **0–14 days:** _TBD (owners, effort in hrs/person, €)_  
- **15–30 days:** _TBD (owners, effort in hrs/person, €)_  
**Why:** Defers non-critical uncertainty; protects ROI and time-to-impact.

---

## 1) Problem Definition (DECIDE: Define)

### 1.1 Symptom → Likely Cause → Opportunity
- **Symptom (with units/timeframe):** _TBD_  
- **Likely Cause(s):** _TBD_  
- **Opportunity:** _TBD_  
**Why:** Show data trail (source/date), map mechanism from cause to effect, and quantify potential upside (%, €, pts).

### 1.2 Assumptions & Hard Constraints
| ID | Type (Legal/Tech/Time/Budget/Quality) | Statement | Unit/Limit | Source/Date | Why Binding |
|---|---|---|---|---|---|
| CONSTR-1 | Time | Launch window | YYYY-MM-DD | _TBD_ | Market seasonality dictates cut-off |

### 1.3 Knowledge Gaps & Validation Plan
| Gap | Why It Matters | Validation Method | Sample/Power | Owner | ETA | Accept Criteria |
|---|---|---|---|---|---|---|
| Price elasticity unknown | Influences margin/ROI | Price test (A/B) | n= _TBD_ | _TBD_ | _TBD_ | |ε| in [-1.2, -0.6] with p<0.05 |

---

## 2) Locked Decision Criteria (DECIDE: Establish) — **Must be locked**

> Weights **must sum to 1.0** and cannot change after this section.

| ID | Criterion | Group | Weight | Metric | Unit | Source | Cadence | Threshold (Warn/Alert) | Why |
|---|---|---|---:|---|---|---|---|---|---|
| CRIT-1 | ROI_12m | Outcome | 0.XX | ROI | % | Finance DW | Monthly | 10 / 5 | Directly linked to capital allocation |
| CRIT-2 | GDPR_Compliance | Constraint | 0.XX | Pass/Fail | bin | Legal | Milestone | Pass/Fail | Legal gate to operate |
| CRIT-3 | Time_to_Impact | Outcome | 0.XX | TTI | weeks | PMO | Bi-weekly | 8 / 12 | Urgency & opportunity window |
| CRIT-4 | Adoption_90d | Outcome | 0.XX | % active users | % | Product Analytics | Weekly | 30 / 20 | Predicts retention & revenue |
| CRIT-5 | Reliability_SLO | Outcome | 0.XX | Avail | % | SRE | Daily | 99.5 / 99.0 | SLA & churn risk |

**Weights Sum:** **1.00**  
**Why these weights:** Reflects executive priorities, feasibility gates, and risk appetite revealed in inputs.

---

## 3) Technology Feasibility

### 3.1 Architecture Fit & Integration
| ID | Capability/Topic | Current State | Required | Fit/Gap | Integration Effort (person-days) | Key Risk | Mitigation | Owner | Due |
|---|---|---|---|---|---:|---|---|---|---|
| TECH-1 | API availability | _TBD_ | REST + OAuth2 | Gap | _TBD_ | Auth drift | Centralized IdP | Eng Lead | YYYY-MM-DD |

**Why:** Integration latency (ms), throughput (req/s), and auth flows determine user experience and SLA.

### 3.2 Reliability, Scalability, Security
- **SRE Golden Signals:** latency (ms), traffic (req/s), errors (%), saturation (%).  
- **Capacity Plan:** headroom %, peak vs P95, autoscaling policy.  
- **Security Posture (STRIDE):** _TBD_  
**Why:** Reliability & security degrade adoption and increase cost of incidents (hrs, €).

### 3.3 Infrastructure & Technical Debt
| Area | Current | Debt/Gaps | Risk | Mitigation | Cost (€) | Owner | Due |
|---|---|---|---|---|---:|---|---|
| Observability | _TBD_ | Sparse traces | Incident MTTR↑ | OpenTelemetry rollout | _TBD_ | SRE | YYYY-MM-DD |

**Why:** Debt inflates MTTR (hrs), lowers availability (%), and jeopardizes SLOs.

---

## 4) Legal & Regulatory

### 4.1 Compliance Map & Liabilities
| ID | Requirement | Applicability | Risk (Prob×Impact) | Mitigation | Owner | Deadline |
|---|---|---|---|---|---|---|
| LEG-1 | GDPR DPIA | High | 0.4×0.7 | DPIA + DPA | Legal | YYYY-MM-DD |

**Why:** Non-compliance causes fines (€), delays (weeks), and reputational damage (NPS points).

### 4.2 Approvals & Data Residency
- **Approvals Needed:** _TBD_ (authority, lead time in weeks).  
- **Data Residency:** region constraints (EU/US), cross-border transfer basis.  
**Why:** Timelines and lawful basis define feasible launch dates and integration patterns.

---

## 5) Financial Feasibility

### 5.1 Investment, Costs & Unit Economics
| KPI | Formula | Inputs (with units) | Base | Optimistic | Pessimistic | Driver |
|---|---|---|---:|---:|---:|---|
| ROI_12m | (Net Gain / Invest)×100 | CAC €, LTV €, COGS € | 12% | 18% | 6% | Price ±5% |

- **CAPEX (€), OPEX (€/month), Payback (months), NPV (€ @ r%)**: _TBD_  
**Why:** Cash timing and sensitivity to price/volume/cost determine resilience.

### 5.2 Guardrails & Contingencies
- **Guardrails:** Payback ≤ _TBD_ months; ROI ≥ _TBD_%.  
- **Contingencies:** _TBD_ (buffer €, trigger thresholds).  
**Why:** Protects downside while preserving upside experiments.

---

## 6) Market & Competition (Deep Dive)

### 6.1 TAM–SAM–SOM (Top-down & Bottom-up)
| Model | TAM | SAM | SOM | Assumptions | CAGR (%/yr) | Why |
|---|---:|---:|---:|---|---:|---|
| Top-down | _TBD_ € | _TBD_ € | _TBD_ € | _TBD_ | _TBD_ | Macro ceiling; sanity check |
| Bottom-up | _TBD_ € | _TBD_ € | _TBD_ € | funnel conv %, capacity | _TBD_ | Execution-anchored |

**Reconciliation:** explain variances (%, reasons).

### 6.2 Segments, JTBD & Behavioral Signals
| Segment | Size (# / €) | JTBD | Pains | Gains | Signals (norms, friction, bias) | Why Priority |
|---|---:|---|---|---|---|---|
| SEG-1 | _TBD_ | _TBD_ | _TBD_ | _TBD_ | present-bias, loss aversion | Value × Access |

### 6.3 Demand Forecast & Elasticity
- **Method:** naive / MA / ARIMA / prophet-like — *justify choice*.  
- **O/B/P Forecast (units/month for 12 months):** _TBD_  
- **Own/Cross Price Elasticity:** ε = _TBD_ (unitless); **Plan** if unknown.  
**Why:** Guides pricing guardrails and inventory/capacity.

### 6.4 Supply-Side Constraints
| Capacity (units/month) | Lead Time (days) | Bottlenecks | SLA Target (%) | Risk | Cost Drivers |
|---:|---:|---|---:|---|---|
| _TBD_ | _TBD_ | _TBD_ | 99.0 | _TBD_ | _TBD_ |

### 6.5 Competitors & Positioning
| Player | Price Level | Channels | Strengths | Weaknesses | Likely Response (Δ€ / share %) |
|---|---|---|---|---|---|
| _TBD_ | Mid | Direct/Partner | _TBD_ | _TBD_ | _TBD_ |

**Positioning Map:** X=price, Y=perceived value (list plotted points).  
**Why:** Anticipate retaliation costs and differentiation needs.

### 6.6 GTM, Pricing & Unit Economics
| Channel | CAC (€) | LTV (€) | Payback (months) | KPI Target | Why |
|---|---:|---:|---:|---|---|
| _TBD_ | _TBD_ | _TBD_ | _TBD_ | CAC/LTV≥3 | Economically defensible |

- **Packaging:** good/better/best (features, €).  
- **Initial Price & Range (€):** _TBD_, with rationale vs elasticity/value.  
- **Cohorts:** GRR %, NRR %, Monthly Churn %.  
**Why:** Aligns acquisition, retention, and price power with guardrails.

---

## 7) Communication Strategy

### 7.1 Audience–Message–Channel Matrix
| Audience | Message | Channel | Objective | KPI/Measurement (unit) | Why |
|---|---|---|---|---|---|
| Internal Execs | ROI & risk | All-hands | Alignment | eNPS points | Governance & momentum |

### 7.2 Change-Comms Milestones & Measurement
- **Milestones:** _TBD_ (date, audience, artifact).  
- **Measurement:** uplift %, reach %, comprehension %.  
**Why:** Adoption and clarity correlate with activation/retention.

---

## 8) Behavioral & Cultural Factors

### 8.1 Frictions, Biases & Levers
| Barrier/Bias | Lever | Expected Effect (Δ%) | How to Measure | Owner | Why |
|---|---|---:|---|---|---|
| Status quo | Defaults + social proof | +8% adoption | Opt-in rate % | _TBD_ | Reduces choice burden |

### 8.2 Culture & Timing Cues
- **Cultural Blockers:** _TBD_  
- **Cues/Prompts:** _TBD_ (timing, salience).  
**Why:** Behavior is the bottleneck to ROI.

---

## 9) Internal / Organizational Readiness

### 9.1 Capability & Governance
| Capability | Current (0–5) | Gap (pts) | Action | Owner | Due | Why |
|---|---:|---:|---|---|---|---|
| Data Eng | 2 | 2 | Hire vendor | Ops | YYYY-MM-DD | Unlocks pipeline SLA |

### 9.2 RACI (Draft) & Change Impact
| Role | Responsible | Accountable | Consulted | Informed | Decision Rights | Escalation |
|---|---|---|---|---|---|---|
| _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

**Why:** Execution risk falls when ownership and paths are explicit.

---

## 10) Cross-Lens Risks & Interdependencies

### 10.1 Integrated Risk Register
| ID | Description | Lens | Prob (0–1) | Impact (0–1) | Score (w×p×i) | Interactions | Mitigation | Owner | Due | Why Critical |
|---|---|---|---:|---:|---:|---|---|---|---|
| RISK-1 | _TBD_ | Legal | 0.3 | 0.8 | 0.24 | RISK-3 | DPIA, DPA | Legal | YYYY-MM-DD | Blocks launch |

### 10.2 Dependency Map (Critical Path)
- **Predecessors → Successors:** _TBD_  
**Why:** Illuminates cascade paths (e.g., legal → finance; tech → comms).

---

## 11) Decision Frames & Multi-Criteria Scoring

### 11.1 Frames Considered
- **Value-at-Risk vs Speed-to-Learn** (and/or **Share-Grab vs Profit-First**)  
**Implications:** _TBD_  
**Why:** Reduces single-track bias; reveals trade-offs under different priorities.

### 11.2 Scoring (ONLY Locked Criteria)
| Solution Type | Total Score (0–1) | Top Contributors (criterion→contribution) | Why This Score |
|---|---:|---|---|
| Conservative | 0.XX | ROI_12m→0.18; GDPR→0.12 | Compliance strong; slower upside |
| Balanced | 0.XX | ROI_12m→0.20; Adoption→0.15 | Best trade-off |
| Bold | 0.XX | Time-to-Impact→0.17; ROI_12m→0.19 | Fast upside; higher exposure |

**Diversity Check:** Alternatives are not >75% similar.  
**Why:** Transparency and reproducibility—no weight changes post-hoc.

---

## 12) Strategic Recommendation, Conditions & Timeline

**Verdict:** **Go / No-Go / Conditional**  
**Why:** Best satisfies **locked criteria** under tested frames and manageable risk.

**Conditions & Thresholds (if Conditional)**  
- ROI ≥ _TBD_% ; Payback ≤ _TBD_ months ; Adoption ≥ _TBD_% ; SLO ≥ _TBD_% ; Compliance milestones met by YYYY-MM-DD.  
**Why:** Converts uncertainty into tractable checks.

**Rationale Chain (Evidence → Inference → Recommendation)**  
- **Finance:** _TBD → TBD → TBD_  
- **Technology:** _TBD → TBD → TBD_  
- **Market:** _TBD → TBD → TBD_

**Next Steps (with effort & cost)**  
- **0–14 days:** _TBD (owner, hrs, €)_  
- **15–30 days:** _TBD (owner, hrs, €)_

---

## 13) Acceptance Checks (Yes/No)

- criteria_locked == **true**  
- weights_sum_to_1 == **true**  
- risk_matrix_present == **true**  
- min_two_frames == **true**  
- go_nogo_with_thresholds == **true**  
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

---

## 14) Traceability & Provenance

**Sources (Doc IDs/Systems + Dates):** _TBD_  
**Tools Applied:** CriteriaLockerTool, RiskRegisterTool, MarketSizingTool, TimeSeriesForecastTool, ElasticityEstimatorTool, PositioningMapTool, UnitEconomicsTool, JSONSchemaValidatorTool, MarkdownFormatterTool, CodeInterpreterTool.  
**Assumptions (explicit):** _TBD_  
**Reproducibility Notes:** method choices, data snapshots, and seeds recorded.

---

## Appendices

- **A. Formulas & Definitions:** ROI, NPV, CAC, LTV, GRR/NRR, elasticity (units).  
- **B. Sensitivities:** driver ranges → KPI bands (include tornado summary if available).  
- **C. Full RACI & Governance.**  
- **D. Compliance Evidence/Checklists** (DPIA, DPA, ISO/SOC).  
- **E. Experiment Designs** (pricing/adoption/comms): hypothesis, metric, sample, duration, MDE.  
- **F. Data & Assumptions Snapshot** (dates, versions).  
- **G. Tool Artifacts** (validation logs, model summaries).

"""
),
            agent=DecisionMultidisciplinaryAgent.create_agent(),
            markdown=True,
            output_file="feasibility_report.md"
        )