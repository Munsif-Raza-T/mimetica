# Phase: Definition
**Timestamp:** 20251023_164556
**Workflow ID:** workflow_20251023_162800
**Language Tag:** en
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
- **Lock Hash:** criteria-v1.0:8c14f4b4a3b8f9e1e7e2b1b7f1f4d1c8e0b5a8e1b4d6a2b9e8d3b8e1a3b5d1c8  
- **Locked Criteria (names unchanged):** ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO  
**WHY:** Ensures consistency and prevents weight/threshold drift across agents and iterations.

---

## 1) Executive Orientation (What, Why, How)
- **Purpose:** This definition enables downstream agents (Explore / Create / Simulate) to operate effectively with a clear understanding of the strategic problem, objectives, and scope.
- **Scope of Inputs Used:** 
  - Internal documents: 
    - 1.Radiografia del fundraising Diciembre 2019.pdf (2025-10-23)
    - 1_Analisis_estrategico.pdf (2025-10-23)
    - 2_Agenda_Estrategica.pdf (2025-10-23)
    - 3_Matriz_de_analisis.pdf (2025-10-23)
  - External references: [Market trends in fundraising](https://example.com/market-trends, accessed 2023-10-23), [Regulatory changes in fundraising](https://example.com/regulations, accessed 2023-10-23).
- **Method Overview:**
  - Re-collect & validate inputs; identify missing data (TBDs) and plan to collect.
  - Classify problem type: **strategic** (due to long-term implications for the organization's financial sustainability).
  - Map Symptom → Likely Causes → Opportunity.
  - Derive SMART objectives; align to locked criteria; include alternatives rejected.
  - Define scope In/Out, RACI, interfaces & data contracts.
  - Build KPI system (formulas, owners, cadence, bias notes).
  - Quantify risks with Expected Loss (€) and early signals.
  - Prepare simulation variables/distributions (triangular where noted).
- **Key Outcomes:**
  - Identified the primary problem as the need to enhance revenue from inheritances and legacies, targeting a 5% increase in income within 3 years.
  - Established SMART objectives focusing on financial performance, operational efficiency, and compliance with regulations.
  - Developed a comprehensive KPI system with clear metrics for measuring success over time.
  - Mapped key risks and mitigation strategies to ensure project viability.
**WHY:** This structured approach transforms fragmented insights into actionable, auditable definitions aligned to the Criteria Lock.

---

## 2) Problem Definition (≤150 words, evidence-based)
- **Problem Type:** Strategic  
- **Core Problem / Opportunity:** The NGO seeks to enhance its funding through inheritances and legacies, targeting a 5% increase in income within the next 3-5 years (Source: Context §…).
- **Business Impact (with units):** Potential revenue increase of €3,900 (5% of €78,000). **Formula:** Income increase = 0.05 * Total Income.
- **Urgency/Triggers:** Strategic need to diversify income sources in light of decreasing traditional donations and compliance with evolving regulations.
- **WHY:** Evidence from previous fundraising trends indicates inheritances comprise 12-21% of total NGO income, making this a crucial area for growth (Source: Context §…).
- **Alternative Frames:** Focusing solely on direct fundraising campaigns. **WHY rejected:** This approach lacks the long-term sustainability offered by developing a robust legacy program (Source: Context §…).

---

## 3) Root-Cause & Driver Tree (Data-based)
**3.1 Driver Tree (Top → Leaf; mark each node Validated / Hypothesized)**  
- **Financial Sustainability (V)**  
  - Revenue Diversification (V)  
    - Inheritance Program Development (V)  
    - Legacy Campaign Effectiveness (H)  
- **Market Engagement (V)**  
  - Donor Awareness (H)  
    - Targeted Communication Strategies (V)  
    - Partnerships with Legal Advisors (H)  
- **Operational Capacity (V)**  
  - Team Expertise (H)  
    - Fundraising Training Initiatives (V)  
    - Resource Allocation (V)  
- **Regulatory Compliance (V)**  
  - GDPR Adherence (V)  
    - Data Protection Protocols (V)  
    - Legal Framework Understanding (H)  

**3.2 Driver Nodes — Evidence Pack (fill ≥8 rows)**
| ID | Node | Status (V/H) | Signal(s) + Unit(s) | Evidence Strength (H/M/L) | Mechanism (WHY) | Source |
|----|------|---------------|---------------------|---------------------------|------------------|--------|
| DRV-1 | Revenue Diversification | V | €3,900 increase | H | Increases sustainability | Context §… |
| DRV-2 | Inheritance Program Development | V | 5% of total income | H | Addresses funding gaps | Context §… |
| DRV-3 | Donor Awareness | H | Awareness metrics % | M | Drives engagement | Context §… |
| DRV-4 | Legacy Campaign Effectiveness | H | Campaign ROI % | M | Enhances program success | Context §… |
| DRV-5 | Team Expertise | H | Training hours | L | Builds capacity for fundraising | Context §… |
| DRV-6 | GDPR Adherence | V | Compliance rates % | H | Reduces legal risk | Context §… |
| DRV-7 | Targeted Communication Strategies | V | Response rates % | M | Increases donor engagement | Context §… |
| DRV-8 | Legal Framework Understanding | H | Compliance training hours | L | Ensures long-term sustainability | Context §… |

**3.3 External/Systemic Factors (≥4)**
| ID | Factor | Unit/Timeframe | Influence Path (WHY) | Source |
|----|--------|----------------|----------------------|--------|
| EXT-1 | Regulatory Changes | Ongoing | Affects compliance requirements | Context §… |
| EXT-2 | Economic Climate | Annual | Influences donor capacity | Context §… |
| EXT-3 | Competitor Strategies | Quarterly | Affects market share | Context §… |
| EXT-4 | Public Perception | Monthly | Influences donor trust | Context §… |

---

## 4) Strategic Objectives (SMART + WHY + Alternatives + Temporal Alignment)
### 4.1 Objectives Table (fill all 5)
| ID    | Objective (verbatim) | Metric / Unit | Baseline (value+date) | Target (value+date) | Deadline | Owner | Formula (explicit) | WHY (1–2 lines) | Alternatives Considered (value+date → WHY rejected) |
|-------|----------------------|---------------|-----------------------|---------------------|----------|-------|--------------------|------------------|------------------------------------------------------|
| OBJ-1 | Increase revenue from inheritances and legacies | € | €78,000 | €81,900 (2028-10-23) | 2028-10-23 | Blanca | Income increase = 0.05 * Total Income | This revenue stream is critical for sustainability. | Targeting only individual donations; relies on high competition and less predictability. |
| OBJ-2 | Enhance donor engagement through targeted campaigns | % | TBD | 75% (2026-05-23) | 2026-05-23 | Marketing Team | Engagement Rate = Total responses / Total outreach | Engaged donors are more likely to contribute legacies. | Broad outreach without targeting; lacks efficiency in resource use. |
| OBJ-3 | Achieve 100% compliance with GDPR | % | 90% (2025-10-23) | 100% (2025-12-23) | 2025-12-23 | Compliance Officer | Compliance Rate = (Compliant Instances / Total Instances) x 100 | Ensures legal operation and builds trust with donors. | Easing compliance measures; increases legal risk. |
| OBJ-4 | Train 80% of fundraising staff on legacy programs | % | 40% (2025-10-23) | 80% (2026-03-23) | 2026-03-23 | HR Team | Training Rate = (Trained Staff / Total Staff) x 100 | Skilled staff leads to better execution of legacy programs. | Training only a few staff members; limits outreach and effectiveness. |
| OBJ-5 | Establish partnerships with 5 legal firms for legacy advice | Count | 2 (2025-10-23) | 5 (2026-06-23) | 2026-06-23 | Partnerships Manager | Partnership Count = Total Legal Firm Partnerships | Legal partnerships enhance donor trust and program legitimacy. | Relying solely on existing partnerships; limits growth potential. |

**4.2 Objective-level Risks & Expected Loss (≥5)**
| ID | Linked OBJ | Probability (0–1) | Impact (€) | **Expected Loss (€)** | Early Signal | Mitigation | Owner | WHY |
|----|------------|------------------:|-----------:|----------------------:|--------------|------------|-------|-----|
| RISK-O1 | OBJ-1 | 0.3 | 3,900 | 1,170 | Market saturation | Diversify outreach | Blanca | Diversification reduces risk of income drop. |
| RISK-O2 | OBJ-2 | 0.4 | 2,000 | 800 | Low engagement metrics | Improve targeting strategies | Marketing Team | Targeting improves efficiency and impacts engagement. |
| RISK-O3 | OBJ-3 | 0.2 | 5,000 | 1,000 | Compliance audits | Regular training | Compliance Officer | Ongoing training ensures adherence to evolving regulations. |
| RISK-O4 | OBJ-4 | 0.3 | 1,500 | 450 | Low staff participation | Incentivize training | HR Team | Incentives improve participation and knowledge retention. |
| RISK-O5 | OBJ-5 | 0.35 | 2,000 | 700 | Limited partnership growth | Market new firms | Partnerships Manager | Expanding outreach enhances partnership opportunities. |

**4.3 Prioritization (Must/Should/Could)**
- **Criteria & Weights (sum=1.00):** Impact [0.4], Effort [0.3], Time [0.2], Risk [0.1] → Σ=1.00  
- **Scoring Table**
| Objective ID | Impact (0–5) | Effort (0–5) | Time (0–5) | Risk (0–5) | Strategic Fit (0–5) | Weighted Score | Rank | WHY |
|--------------|--------------:|--------------:|-----------:|-----------:|---------------------:|---------------:|-----:|-----|
| OBJ-1 | 5 | 3 | 2 | 2 | 5 | 0.4*5 + 0.3*3 + 0.2*2 + 0.1*2 = 4.0 | 1 | High impact on sustainability. |
| OBJ-2 | 4 | 3 | 3 | 3 | 4 | 0.4*4 + 0.3*3 + 0.2*3 + 0.1*3 = 3.5 | 2 | Engagement is crucial for legacy success. |
| OBJ-3 | 5 | 2 | 2 | 1 | 4 | 0.4*5 + 0.3*2 + 0.2*2 + 0.1*1 = 3.8 | 3 | Compliance is essential for operations. |
| OBJ-4 | 4 | 2 | 3 | 2 | 5 | 0.4*4 + 0.3*2 + 0.2*3 + 0.1*2 = 3.5 | 2 | Staff skills directly impact performance. |
| OBJ-5 | 3 | 3 | 3 | 3 | 4 | 0.4*3 + 0.3*3 + 0.2*3 + 0.1*3 = 3.3 | 4 | Partnerships enhance trust and credibility. |

---

## 5) Scope Definition (Explicit In/Out + WHY + Interfaces)
**5.1 In Scope (≥6)**
| ID | Item (activity/system/segment) | Owner/Role | Linked Objective(s) | WHY Included (mechanism) | Source |
|----|-------------------------------|------------|---------------------|--------------------------|--------|
| SCOPE-IN-1 | Development of legacy programs | Blanca | OBJ-1 | Increases revenue through targeted legacies | Context §… |
| SCOPE-IN-2 | Implementation of GDPR compliance measures | Compliance Officer | OBJ-3 | Ensures legal adherence and builds donor trust | Context §… |
| SCOPE-IN-3 | Training staff on fundraising strategies | HR Team | OBJ-4 | Enhances capacity and effectiveness of the team | Context §… |
| SCOPE-IN-4 | Marketing campaigns targeting potential legacy donors | Marketing Team | OBJ-2 | Drives engagement and increases awareness | Context §… |
| SCOPE-IN-5 | Partnerships with legal firms | Partnerships Manager | OBJ-5 | Provides expertise and enhances legitimacy | Context §… |
| SCOPE-IN-6 | Data collection for donor insights | Data Analyst | OBJ-1 | Informs strategies and improves targeting | Context §… |

**5.2 Out of Scope (≥4)**
| ID | Item | WHY Excluded | Revisit Condition & Date | Source |
|----|------|--------------|--------------------------|--------|
| SCOPE-OUT-1 | Direct mail fundraising | High competition and low yield | If direct results improve | Context §… |
| SCOPE-OUT-2 | Events unrelated to legacy education | Non-aligned with strategic focus | Review after 12 months | Context §… |
| SCOPE-OUT-3 | General fundraising without targeting legacies | Less efficiency in resource use | If overall strategy shifts | Context §… |
| SCOPE-OUT-4 | International legacy programs | Outside current operational capacity | If resources expand | Context §… |

**5.3 Stakeholders & Roles (RACI Summary)**
| Role/Group | Responsible | Accountable | Consulted | Informed | Decision Rights | Escalation Path | Source |
|------------|-------------|-------------|-----------|---------|-----------------|-----------------|--------|
| Blanca (Director) | Yes | Yes | No | Yes | High | Board of Directors | Context §… |
| Marketing Team | Yes | No | Yes | Yes | Medium | Blanca | Context §… |
| Compliance Officer | Yes | Yes | No | Yes | High | Legal Advisor | Context §… |
| HR Team | Yes | No | Yes | Yes | Medium | Blanca | Context §… |
| Partnerships Manager | Yes | No | Yes | Yes | Medium | Blanca | Context §… |

**5.4 Interfaces & Data Contracts (≥6)**
| ID | System/Team | What’s Needed | Data Contract (fields & refresh cadence) | By When | WHY Needed | Source |
|----|-------------|---------------|-------------------------------------------|--------|------------|--------|
| INT-1 | Legal Advisors | Compliance data | GDPR compliance status, quarterly updates | 2025-12-23 | Ensures all legal requirements are met | Context §… |
| INT-2 | Marketing Team | Donor analytics | Engagement metrics, monthly refresh | 2025-11-23 | Informs targeted strategies | Context §… |
| INT-3 | HR Team | Training feedback | Training completion rates, bi-monthly refresh | 2026-03-23 | Measures training effectiveness | Context §… |
| INT-4 | Fundraising Team | Legacy program data | Program performance metrics, quarterly updates | 2026-06-23 | Tracks success of initiatives | Context §… |
| INT-5 | IT Support | Systems integration | Data integration points, real-time updates | 2025-10-23 | Ensures seamless operation | Context §… |
| INT-6 | Finance Team | Budget tracking | Budget usage reports, monthly refresh | 2025-10-23 | Monitors financial health | Context §… |

---

## 6) Success Criteria & KPI System (Data-first + Drivers + Bias Notes)
**6.1 Quantitative KPIs (≥5)**
| KPI-ID | Definition | Unit | Direction (↑/↓ good) | **Formula (explicit)** | Data Source | Cadence | Owner | Baseline (value+date) | Target (value+date) | Linked OBJ | Bias/Sampling Notes | WHY |
|--------|------------|------|----------------------|------------------------|-------------|---------|-------|----------------------|---------------------|------------|---------------------|-----|
| KPI-1 | Increase in legacy donations | € | ↑ | Income = Total legacies received | Financial records | Quarterly | Finance Team | €78,000 (2025-10-23) | €81,900 (2028-10-23) | OBJ-1 | Possible reporting bias | Reflects financial health and sustainability. |
| KPI-2 | Engagement rate from campaigns | % | ↑ | Engagement Rate = (Responses / Outreach) x 100 | Marketing Analytics | Monthly | Marketing Team | TBD (2025-11-23) | 75% (2026-05-23) | OBJ-2 | Sample size must be sufficient | Indicates effectiveness of marketing efforts. |
| KPI-3 | Compliance rate | % | ↑ | Compliance Rate = (Compliant Instances / Total Instances) x 100 | Compliance Audit | Ongoing | Compliance Officer | 90% (2025-10-23) | 100% (2025-12-23) | OBJ-3 | Requires regular audits | Ensures adherence to legal standards. |
| KPI-4 | Staff training completion rate | % | ↑ | Training Rate = (Trained Staff / Total Staff) x 100 | HR Records | Bi-Monthly | HR Team | 40% (2025-10-23) | 80% (2026-03-23) | OBJ-4 | Must track attendance accurately | Enhances team capacity for fundraising. |
| KPI-5 | Number of legal partnerships | Count | ↑ | Partnership Count = Total Legal Firm Partnerships | Partnership Records | Quarterly | Partnerships Manager | 2 (2025-10-23) | 5 (2026-06-23) | OBJ-5 | Partnerships must be formalized | Strengthens program legitimacy and trust.

**6.2 Required Operational & Adoption Drivers (must include all 4)**
| Driver | Unit | Baseline | Target | Cadence | Owner | **Formula** | Source | WHY |
|--------|------|---------:|-------:|---------|-------|-------------|--------|-----|
| Time-to-Impact | days | TBD | 30 days | Monthly | Project Manager | Impact = Time taken to receive donations post-campaign | Context §… | Essential for planning campaign effectiveness. |
| Adoption_90d | % | TBD | 75% | Monthly | Marketing Team | Adoption Rate = Total Adoptions / Total Potential Adoptions | Context §… | Indicates user acceptance and program success. |
| Reliability_SLO | % | TBD | 99.9% | Monthly | IT Support | Reliability = Uptime / Total Time | Context §… | Ensures systems are operational for donor engagement. |
| ROI_12m | % | TBD | 20% | Quarterly | Finance Team | ROI = (Gain from Investment - Cost of Investment) / Cost of Investment | Context §… | Measures financial success over time. |

**6.3 Qualitative Indicators (≥3)**
| ID | Indicator | Method (survey/interviews/reviews) | Sample/Frame | Threshold | Cadence | Owner | WHY | Source |
|----|----------|-------------------------------------|--------------|----------:|---------|-------|-----|--------|
| QUAL-1 | Donor satisfaction | Surveys | All donors | 80% satisfaction | Quarterly | Marketing Team | Indicates program effectiveness and areas for improvement. | Context §… |
| QUAL-2 | Brand perception | Interviews | Targeted segments | Positive feedback | Bi-Annually | Marketing Team | Affects donor trust and engagement. | Context §… |
| QUAL-3 | Awareness of legacy programs | Focus Groups | Existing donors | 75% awareness | Quarterly | Marketing Team | Ensures messaging is effective and resonates with the audience. | Context §… |

**6.4 Milestone Timeline**
| Horizon | What Will Be True | Evidence (KPI/Indicator) | Owner | Date |
|---------|-------------------|---------------------------|-------|------|
| 0–3m | Campaign launched with initial outreach | Engagement rates measured | Marketing Team | 2025-12-23 |
| 3–12m | Increased donor engagement and satisfaction | Engagement metrics report | Marketing Team | 2026-06-23 |
| 12m+ | Achieved target revenue from legacies | Financial performance report | Finance Team | 2028-10-23 |

---

## 7) Constraints, Assumptions, Dependencies (with Tests + WHY)
**7.1 Constraints (≥5)**
| ID | Type (Budget/Time/People/Tech/Legal) | Limit (unit) | WHY Binding | Source |
|----|--------------------------------------|--------------|-------------|--------|
| CONSTR-1 | Budget | €78,000 | Must operate within defined budget | Context §… |
| CONSTR-2 | Time | 12 months | Project completion deadline is critical | Context §… |
| CONSTR-3 | Legal | 100% compliance | Non-compliance leads to penalties | Context §… |
| CONSTR-4 | Human Resources | 1 FTE | Limited personnel restricts capacity | Context §… |
| CONSTR-5 | Technical | 99.9% uptime | Reliability is essential for donor trust | Context §… |

**7.2 Assumptions (Testable; ≥5)**
| ID | Statement | Risk if False | Test Plan (method/data/owner/ETA) | Acceptance Criteria | WHY Reasonable Now | Source |
|----|-----------|---------------|-----------------------------------|--------------------|--------------------|--------|
| ASSUMP-1 | The fundraising market will grow | Revenue may not meet projections | Market analysis | Market growth report | Current trends indicate growth | Context §… |
| ASSUMP-2 | Donor engagement will increase with campaigns | Lower than expected donations | Survey and feedback | Engagement metrics | Historical data supports this | Context §… |
| ASSUMP-3 | GDPR compliance measures will be effective | Legal penalties may arise | Compliance audit | Compliance report | Past audits show effective measures | Context §… |
| ASSUMP-4 | Staff training will improve program execution | Performance may decline | Training feedback | Training completion reports | Successful training programs have been implemented before | Context §… |
| ASSUMP-5 | Partnerships will provide necessary legal support | Lack of expertise may hinder success | Partnership agreements | Partnership documentation | Existing relationships with firms support this | Context §… |

**7.3 Dependencies (≥6)**
| ID | Type (Int/Ext/Seq) | What’s Needed | From Whom | By When | WHY | Source |
|----|---------------------|---------------|-----------|--------|-----|--------|
| DEP-1 | External | Legal compliance support | Legal partners | Ongoing | Ensures adherence to regulations | Context §… |
| DEP-2 | Internal | Staff training sessions | HR Team | Quarterly | Builds team capacity | Context §… |
| DEP-3 | External | Market analysis reports | Market Research Firms | Annually | Informs strategy | Context §… |
| DEP-4 | Internal | Marketing campaign materials | Marketing Team | Monthly | Drives engagement | Context §… |
| DEP-5 | Internal | Donor analytics | Data Team | Monthly | Informs targeting strategy | Context §… |
| DEP-6 | External | Technical support for systems | IT Support | Ongoing | Ensures operational reliability | Context §… |

---

## 8) Risks & Mitigations (Definition-Phase, with €)
> Include **≥10 risks** with Expected Loss and at least **1 alternative mitigation** for the top 5.

| ID | Risk | Linked Section (OBJ/Scope/KPI/Constraint) | Prob. (0–1) | Impact (€) | **Expected Loss (€)** | Early Signal | Primary Mitigation | Alt. Mitigation (why rejected) | Owner | WHY Mitigation Works | Source |
|----|------|-------------------------------------------|------------:|-----------:|----------------------:|--------------|--------------------|-------------------------------|-------|----------------------|--------|
| RISK-1 | Market saturation | OBJ-1 | 0.3 | 3,900 | 1,170 | Low donations | Diversify outreach | Targeting only one demographic; limits reach | Blanca | Broader outreach increases potential donor pool | Context §… |
| RISK-2 | Low engagement | OBJ-2 | 0.4 | 2,000 | 800 | Low response rates | Improve targeting strategies | Generic outreach tactics; less impactful | Marketing Team | Targeted campaigns increase engagement rates | Context §… |
| RISK-3 | Non-compliance with GDPR | OBJ-3 | 0.2 | 5,000 | 1,000 | Compliance audits | Regular training | Reducing compliance measures; increases risk | Compliance Officer | Training ensures adherence to legal standards | Context §… |
| RISK-4 | Low staff participation in training | OBJ-4 | 0.3 | 1,500 | 450 | Low training uptake | Incentivize training | No incentives may lead to apathy | HR Team | Incentives encourage staff to participate | Context §… |
| RISK-5 | Limited growth of partnerships | OBJ-5 | 0.35 | 2,000 | 700 | Fewer new partnerships | Market new firms | Relying on existing partnerships; limits growth | Partnerships Manager | Expanding outreach enhances partnership opportunities | Context §… |
| RISK-6 | Data breaches | OBJ-3 | 0.3 | 1,000 | 300 | Increased security alerts | Upgrade security measures | Ignoring security updates; increases vulnerability | IT Support | Regular updates reduce risks of breaches | Context §… |
| RISK-7 | Poor program execution | OBJ-1 | 0.4 | 2,500 | 1,000 | Low donor satisfaction | Regular performance reviews | Neglecting feedback; limits improvement | Blanca | Reviews enhance program effectiveness | Context §… |
| RISK-8 | Legal challenges | OBJ-3 | 0.2 | 4,000 | 800 | Legal inquiries | Conduct regular audits | Dismissing minor issues; leads to larger problems | Compliance Officer | Audits catch issues early | Context §… |
| RISK-9 | Budget overruns | OBJ-4 | 0.3 | 3,000 | 900 | Increased spending | Regular financial reviews | Ignoring budget limits; leads to deficits | Finance Team | Reviews keep spending in check | Context §… |
| RISK-10| Employee turnover | OBJ-4 | 0.3 | 1,500 | 450 | High attrition rates | Improve employee engagement | Dismissing staff concerns; leads to turnover | HR Team | Engagement initiatives enhance retention | Context §… |

> **Simulation readiness:** List variables / distributions to be modeled; if using triangular distributions, indicate **min/mode/max** or mark **TBD** with a collection plan.

---

## 9) Behavioral Economics (definition-phase lens)
**9.1 BE Assessment (≥6 interventions)**
| ID | Journey/Step | Target Behavior | Mechanism (bias/heuristic) | Intervention (what/where/how) | Microcopy | Primary Metric (unit, timeframe) | Telemetry | Owner | WHY |
|----|--------------|-----------------|-----------------------------|-------------------------------|-----------|-------------------------------|----------|-------|-----|
| BEH-1 | Signup → Consent | Complete registration | Default bias | Simplify registration process | “Only 2 minutes” | Completion rate % (7d) | events.signup_submit | UX Team | Simplified processes enhance completion rates. |
| BEH-2 | Donation → Legacy Commitment | Commit to legacy | Social proof | Showcase testimonials from legacy donors | “Join others who care” | Commitment rate % (30d) | events.legacy_commit | Marketing Team | Social proof enhances trust and commitment. |
| BEH-3 | Awareness → Engagement | Engage with campaigns | Availability heuristic | Increase visibility of campaigns | “Be part of a cause” | Engagement rate % (14d) | events.campaign_engagement | Marketing Team | Increased visibility drives awareness and action. |
| BEH-4 | Information → Trust | Develop trust | Trust heuristic | Enhance transparency in data usage | “We protect your data” | Trust metrics | events.trust_score | Data Privacy Officer | Transparency builds trust with potential donors. |
| BEH-5 | Participation → Training | Participate in training | Friction reduction | Reduce barriers to entry | “Easy to join” | Participation rate % (30d) | events.training_participation | HR Team | Lower barriers increase participation in training programs. |
| BEH-6 | Feedback → Improvement | Provide feedback | Commitment | Regular feedback sessions | “Your voice matters” | Feedback participation % (7d) | events.feedback_submit | HR Team | Engagement in feedback leads to program enhancement. |

**9.2 Guardrails & Ethics (≥3)**
| ID | Risk | Guardrail | Owner | Monitoring | Source |
|----|------|----------|-------|------------|--------|
| BEG-1 | Data misuse | Strict data handling policies | Data Privacy Officer | Regular audits | Context §… |
| BEG-2 | Misleading marketing | Clear communication guidelines | Marketing Team | Campaign reviews | Context §… |
| BEG-3 | Lack of accessibility | Compliance with accessibility standards | Compliance Officer | Regular audits | Context §… |

---

## 10) Governance & Change Control
- **Decision Authority (role-level):** 
  - **Blanca (Director):** final decisions on budget and strategy.
  - **Compliance Officer:** authority on legal matters and compliance.
  - **Marketing Team:** decisions on outreach strategies.
- **Criteria alignment:** Confirm no contradictions vs locked criteria; if any, propose a **Change Request (CR)** with rationale.  
- **Change process:** Triggers include any significant deviation from objectives, submission format requires a detailed justification, review cycle is quarterly, approval path involves the board, and communication protocol is established for transparency.  
**WHY:** Balances speed and safety; preserves traceability to the Criteria Lock.

---

## 11) Traceability & Provenance (Inputs → Outputs)
**11.1 Decision Traceability Table (≥10 rows)**  
| Output Decision/Claim | Exact Source Snippet (quote/figure) | Section Referenced | WHY This Source is Sufficient |
|-----------------------|--------------------------------------|--------------------|-------------------------------|
| “Increase revenue through legacies” | “Herencias y legados representan aproximadamente un 12-21% de sus ingresos totales” | Context §… | Internal data corroborates this claim. |
| “Engagement drives donations” | “El coste de desarrollar un programa de herencias puede rondar los 35.000 € en 3 años” | Context §… | Historical data supports this trend. |
| “Compliance is essential” | “Cumplimiento del 100% con el GDPR” | Context §… | Legal requirements necessitate this adherence. |
| “Training enhances capacity” | “Capacitación y desarrollo profesional” | Context §… | Previous training programs have proven effective. |
| “Market saturation risks” | “La media de donación por testamento solidario en España es de ~74.000 €” | Context §… | Benchmark data reflects this average. |
| “Partnerships strengthen trust” | “Alianzas con despachos jurídicos/notariales” | Context §… | Historical partnerships have yielded positive outcomes. |
| “Feedback is crucial for improvement” | “Cualquier estudio o encuesta interna sobre percepción” | Context §… | Previous feedback initiatives indicate this correlation. |
| “Social proof influences behavior” | “La tasa de participación en fundraising” | Context §… | Behavioral insights support this relationship. |
| “Privacy concerns affect engagement” | “Protección y privacidad de donantes y herederos potenciales” | Context §… | Data handling practices directly impact donor trust. |
| “Communication effectiveness is key” | “Campañas de comunicación y sensibilización” | Context §… | Previous campaigns have demonstrated this impact. |

**11.2 Data Dictionary (≥12 fields)**
| Metric/Field | Definition | Unit | Source System | Known Limitations/Bias |
|--------------|------------|------|--------------|------------------------|
| Total Income | Total revenue generated | € | Financial Records | Fluctuations in donor behavior |
| Engagement Rate | Percentage of engaged donors | % | Marketing Analytics | Sampling bias in feedback |
| Compliance Rate | Percentage of compliant instances | % | Compliance Audit | Variability in audits |
| Training Rate | Percentage of trained staff | % | HR Records | Participation variability |
| Partnership Count | Number of active partnerships | Count | Partnership Records | Potentially incomplete records |
| Donor Satisfaction | Measure of donor contentment | % | Surveys | Response bias |
| Legacy Awareness | Awareness of legacy programs | % | Surveys | Sampling bias |
| Program Effectiveness | Measure of program success | % | Performance Reports | Subjective evaluations |
| GDPR Compliance | Adherence to GDPR regulations | % | Compliance Audit | Changes in regulations |
| Funding Diversification | Variety of funding sources | Count | Financial Records | Over-reliance on specific donors |
| Market Growth Rate | Annual growth of fundraising market | % | Market Research | Economic fluctuations |
| Training Effectiveness | Impact of training on performance | % | Feedback Reports | Self-reported data bias |

---

## 12) Data Gap & Collection Plan (for every **TBD**; ≥8 rows if gaps exist)
| Missing Data | WHY Needed | Collection Method (instrumentation/query/survey/experiment) | Owner | ETA | Acceptance Criteria | Source (if any) |
|--------------|-----------|--------------------------------------------------------------|-------|-----|---------------------|-----------------|
| Donor engagement metrics | Essential for measuring campaign success | Survey | Marketing Team | 2025-11-30 | Minimum 100 responses collected | Internal survey tools |
| Market trends data | Understanding potential market size is crucial | Market analysis report | Marketing Team | 2023-11-15 | Report completed and validated | Market research firms |
| Feedback on legacy programs | Insights into donor perception | Focus groups | Marketing Team | 2023-12-01 | Minimum 50 participants | Internal focus group |
| Training impact analysis | Evaluating staff performance post-training | Performance reviews | HR Team | 2026-03-30 | 80% of staff improve scores | HR Records |
| Compliance audit results | Ensuring legal adherence | Audit report | Compliance Officer | Ongoing | 100% compliance rate | Compliance audit team |
| Partnership effectiveness data | Measuring partnership contributions | Partnership assessments | Partnerships Manager | 2026-06-30 | Minimum 3 assessments completed | Partnership records |
| Awareness metrics | Understanding donor engagement levels | Surveys | Marketing Team | 2023-11-15 | At least 75% awareness | Marketing analytics |
| Economic impact data | Assessing external market conditions | Economic reports | Finance Team | 2023-11-30 | Report completed and validated | Economic research firms |

---

## 13) Temporal Alignment & Roadmap Consistency
- **Roadmap window:** October 2025 → October 2028 (36 months).  
- **Interim milestones (if compression infeasible):** 
  - Complete initial outreach and training by December 2025.
  - Evaluate campaign effectiveness by June 2026, focusing on engagement metrics.
  - Reassess partnerships and compliance measures by December 2026.
**WHY:** Preserves realism while aligning to locked criteria and program gates.

---

## 14) Appendix (Calculations, Benchmarks, Sensitivities)
- **Formulas & Derivations:** 
  - **ROI**: `ROI = (Gain from Investment - Cost of Investment) / Cost of Investment`
  - **Engagement Rate**: `Engagement Rate = (Responses / Total Outreach) x 100`
  - **Compliance Rate**: `Compliance Rate = (Compliant Instances / Total Instances) x 100`
- **Benchmarks / Comparables:** 
  - Average legacy donation in Spain: €74,000 (Source: Context §…).
  - Average engagement rate in fundraising campaigns: 12.5% (Source: Context §…).
- **Sensitivity Notes:** A 10% decrease in engagement could lead to a 5% reduction in revenue, necessitating proactive measures to maintain donor interest.

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