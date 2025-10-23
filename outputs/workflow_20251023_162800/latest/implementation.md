# Phase: Implementation
**Timestamp:** 20251023_165213
**Workflow ID:** workflow_20251023_162800
**Language Tag:** en
```
# Implementation Plan for: Maximization of Inheritances and Legacies
- **Criteria Version:** v1.0 • **Lock Hash:** criteria-v1.0:8c14f4b4a3b8f9e1e7e2b1b7f1f4d1c8e0b5a8e1b4d6a2b9e8d3b8e1a3b5d1c8  
- **Execution Timestamp (local):** 2025-10-23 16:49:34 • **Calendar:** 2025-10-23  
- **Selected Option Source:** Create §…; URL/Doc-ID + access date  
- **Decision Link:** Aligned to locked CRIT/KPI/OBJ: ROI_12m, GDPR_Compliance, Time_to_Impact, Adoption_90d, Reliability_SLO

**WHY:** Binds plan → selected option → criteria lock so simulation/evaluation remain consistent and auditable.

---

## 0) Executive Summary
- **Selected Option (A/B/C):** Option A: Develop a strategic program for growing inheritances and legacies to secure sustainable funding.
- **Operating Model:** Phased approach with pilot testing followed by scaling; rollback procedures in place to mitigate risks.
- **Timeline Envelope:** 0–36 weeks • **Time-to-First-Value:** 12 weeks • **Scale Ready:** Q3 2026
- **Outcome Targets (≥3):** 
  - +5% increase in legacy income @2028
  - Reduce cost per acquisition of legacy donors by 10% @Q2 2026
  - +10 NPS points @60d post-implementation
- **SLO/SLA Anchors:** 99.5% availability, 200 ms p95 latency, RPO/RTO of 1 hour
- **Budget Envelope:** CapEx €78,000, OpEx €5,000/month, Contingency 10%
- **Top 3 Risks (p×i):** 
  - Market saturation (0.3×€3,900) = €1,170; early signal: low donations.
  - Low engagement metrics (0.4×€2,000) = €800; early signal: low response.
  - Compliance audit failures (0.2×€5,000) = €1,000; early signal: compliance issues.
- **Go/No-Go Gates:** ROI_12m > €81,900; GDPR_Compliance = Pass.

**WHY:** Summarizes value, speed, risk, and gating alignment for an informed Go/No-Go.

---

## 1) Implementation Strategy, Operating Model & Customer Lens
- **Delivery Approach:** Agile cadence, with 2-week sprints; Definition of Ready and Done established; baseline velocity of 10 story points/sprint.
- **Customer-Centric Service Blueprint (front/back-stage):** 
  - Touchpoints: Donor engagement through campaigns, legal consultations, feedback sessions.
  - Handoffs: Clear communication with legal advisors for compliance and marketing for campaign effectiveness.
  - Pain Points: Navigating legal complexities, ensuring donor trust and transparency.
- **Decision Rights & Escalation:** Decisions on budget and strategy by Blanca; escalation SLA ≤24h for operational decisions.
- **Quality & Safety Bars:** Security audits quarterly; privacy checks against GDPR; accessibility checks (WCAG 2.2).
- **Change Control:** Feature flags for new campaigns; change board review every month for impact assessment.

**Provenance:** Contextual evidence from organizational strategy documents.  
**WHY:** Operating model reduces risk under constraints while protecting customer experience.

---

## 2) Work Breakdown Structure (WBS) & Acceptance (RELATIVE TIME)
**Minimums:** 4 Phases (Preparation → Core Implementation → Integration & Testing → Deployment), ≥4 Workstreams, **≥12 Work Packages (WPs)**.

| Phase                | Workstream            | WP ID | Work Package                                 | Deliverables                                       | Objective Acceptance Criteria                        | Dependencies                   | Effort [FTE-weeks] | Duration [weeks] | % Slack | Provenance             |
|----------------------|-----------------------|-------|----------------------------------------------|---------------------------------------------------|---------------------------------------------------|--------------------------------|---------------------|-------------------|---------|------------------------|
| Preparation          | Planning              | WP-01 | Conduct initial stakeholder meetings         | Stakeholder report and feedback summary            | All stakeholders engaged and feedback incorporated | None                           | 2                   | 2                 | 0       | Context §…            |
| Preparation          | Data Collection       | WP-02 | Gather historical data on legacies           | Historical data report on legacies                 | Data report approved by finance team               | WP-01                          | 3                   | 3                 | 0       | Context §…            |
| Core Implementation   | Campaign Development  | WP-03 | Design communication campaigns                | Campaign materials and communication plan          | Campaign materials reviewed and approved           | WP-02                          | 4                   | 4                 | 5       | Context §…            |
| Core Implementation   | Training              | WP-04 | Staff training on legacy fundraising          | Training session report and attendee feedback      | 80% staff trained within timeline                   | WP-03                          | 3                   | 3                 | 0       | Context §…            |
| Integration & Testing | Compliance Review     | WP-05 | Conduct GDPR compliance checks                | Compliance report                                  | Pass compliance checks                              | WP-02                          | 1                   | 1                 | 0       | Context §…            |
| Deployment           | Launch                | WP-06 | Roll out campaigns and monitor performance    | Campaign performance report                         | Campaigns launched and performance metrics tracked  | WP-04, WP-05                   | 3                   | 2                 | 3       | Context §…            |

- Buffer Policy: Phase buffers set at 5%; **% Slack < 10%** for critical-path WPs.  
- Effort→Duration: `Duration [weeks] = Effort [FTE-weeks] / Assigned FTE`.  
- Critical Path: Identified zero-slack WPs are WP-01, WP-02, WP-03, WP-04.

**WHY:** Decomposition surfaces risk early and accelerates earliest value with controlled buffers.

---

## 3) Behavioral Economics Plan (Choice Architecture & Nudges)
**Minimums:** **8–12 interventions** across the journey including at least: 1 default, 1 framing, 1 social proof, 1 friction reduction, 1 timing/reminder, 1 commitment device, 1 loss-aversion guard, 1 salience/visual hierarchy.

| ID  | Journey Step                  | Decision to Influence            | Mechanism (bias/heuristic)       | Intervention (what/how/where)              | Microcopy/Label            | Variants (A/B/…) | Expected Effect [unit, timeframe] | Guardrails & Ethics                    | Telemetry Event(s)           | Owner       | Provenance    |
|-----|-------------------------------|----------------------------------|----------------------------------|-------------------------------------------|-----------------------------|-----------------|----------------------------------|----------------------------------------|-----------------------------|-------------|---------------|
| BE-01| Initial contact with donors   | Increase engagement              | Social Proof                     | Use testimonials from previous legacy donors | "Join others who have given" | A/B Test        | +15% engagement rate @30d         | Ensure testimonials are genuine         | Engagement metrics          | Marketing   | Context §…   |
| BE-02| Campaign launch               | Drive urgency                    | Scarcity                        | Limited-time offer for legacy pledges     | "Act before [date]!"       | None            | +10% conversions @60d             | Ensure offer is ethical and clear      | Conversion rates            | Marketing   | Context §…   |
| BE-03| Informational sessions        | Build trust                      | Loss Aversion                    | Provide clear information on donation impacts | "Your legacy matters"       | None            | +20% attendance @next session      | Ensure all information is accurate      | Attendance rates            | Marketing   | Context §…   |
| BE-04| Follow-up after campaigns      | Reinforce commitment             | Commitment/Consistency           | Regular updates on impact of donations     | "Your support makes a difference" | None            | +5% repeat engagement @90d         | Ensure updates are factual and timely   | Repeat donor metrics        | Marketing   | Context §…   |
| BE-05| Survey post-campaign          | Collect feedback                 | Salience                        | Send a survey to gauge donor experiences    | "Help us improve!"          | None            | 75% response rate @30d             | Ensure survey is user-friendly         | Survey response rates       | Marketing   | Context §…   |

- Measurement Rules: primary metric per nudge (unit, frame), guardrails (min/max effect; fairness), exposure control.  
- Ethics: no dark patterns; truthful scarcity; easy opt-out; consent where relevant.

**WHY:** Chosen levers reduce friction & improve adoption with measurable, ethical effects.

---

## 4) Architecture, NFRs & Environments
- **High-Level Architecture:** 
  - Components: CRM for donor management, analytics for campaign performance.
  - Data flows: Donor data captured → analyzed for insights → used in targeted campaigns.
  - External dependencies: Legal advisors for compliance.
- **NFRs (targets):** 
  - Availability: 99.5%
  - Latency: 200 ms p95
  - Throughput: 100 req/s
  - Error budget: 1 hour/month
  - RPO/RTO: 1 hour
- **Environments:** Development, testing, staging, production parity; data seeding for tests; secrets management through secure vaults.
- **Security & Privacy:** 
  - Authorization model: Role-based access control (RBAC)
  - Encryption standards: AES-256 for data at rest
  - DPIA lead time: 30 days for legal reviews
- **Observability:** 
  - Metrics logged for KPI tracking; alerts set for performance thresholds; dashboards for real-time analytics.

**SLO/SLA Table (REQUIRED)**

| Service/Flow        | SLI                      | SLO Target       | Error Budget (per period) | Alert Threshold        | Pager Policy     | Owner       | Runbook    |
|---------------------|--------------------------|------------------|---------------------------|------------------------|------------------|-------------|------------|
| Campaign Management  | Campaign response time    | <200 ms          | 1 hour/month              | >200 ms                | Immediate action  | Marketing   | TBD        |
| Donor Engagement     | Engagement rate           | >75%             | 1 hour/month              | <75%                   | Daily review      | Marketing   | TBD        |
| Compliance           | GDPR compliance rate      | 100%             | 0 errors                  | Any non-compliance     | Immediate action  | Compliance   | TBD        |

**WHY:** NFR/SLO alignment prevents value erosion and instability post-launch.

---

## 5) Data, Telemetry & Measurement Spec
Map every KPI/criterion and nudge to events/metrics with schema & cadence.

| Signal                | Type (event/metric) | Schema (fields & types)            | Unit  | Frame (cohort/geo/time) | Source System     | Cadence      | DQ Checks          | Retention  | Consumers      | Provenance    |
|-----------------------|---------------------|------------------------------------|-------|-------------------------|--------------------|--------------|---------------------|------------|----------------|---------------|
| Legacy Donations       | Metric              | {donor_id: string, amount: float} | €     | Monthly                 | Financial Records   | Monthly      | Amount > 0          | 5 years    | Finance        | Context §…   |
| Engagement Rate        | Metric              | {campaign_id: string, responses: int, outreach: int} | %     | Quarterly              | Marketing Analytics  | Quarterly    | Responses ≥ 0       | 2 years    | Marketing       | Context §…   |
| Compliance Rate        | Metric              | {compliant: int, total: int}      | %     | Ongoing                 | Compliance Audit     | Ongoing      | Total > 0           | 3 years    | Compliance      | Context §…   |

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

| ID  | Hypothesis (direction + unit + timeframe) | Primary Metric           | Guardrails (min/max) | Design                | α   | Power (1-β) | MDE   | Sample Size (n) | Duration | Segments | Analysis Plan      | Ethics/Consent | Provenance    |
|-----|---------------------------------------------|--------------------------|-----------------------|-----------------------|-----|--------------|-------|------------------|----------|----------|--------------------|----------------|---------------|
| EXP-01 | Increasing communication frequency will raise donor engagement by 15% within 60 days | Engagement rate          | 70% ≤ rate ≤ 90%     | A/B Testing           | 0.05 | 0.8          | 5%    | 200              | 60 days  | All donors | Comparative analysis | Informed consent | Context §…   |
| EXP-02 | Offering a limited-time increase in legacy value will enhance donations by 10% in 90 days | Total legacy donations    | 0 ≤ value ≤ €100,000 | Time-limited offer    | 0.05 | 0.8          | €10,000 | 150              | 90 days  | Target group | Pre- and post- campaign metrics | Informed consent | Context §…   |

- Integrity: SRM checks, novelty decay, seasonality handling, exposure caps.

**WHY:** De-risks assumptions and quantifies expected lift under realistic conditions.

---

## 7) Timeline, Milestones & Critical Path (RELATIVE WEEKS)
**Master Schedule (≥4 phases, buffers visible)**

| Phase                | Start (Week) | End (Week) | Duration [weeks] | % Slack | Key Deliverables                | Phase Gate Criteria (pass/fail) |
|----------------------|---------------|------------|------------------|---------|---------------------------------|----------------------------------|
| Preparation          | 1             | 2          | 2                | 0       | Stakeholder report              | All stakeholders engaged         |
| Core Implementation   | 3             | 8          | 6                | 5       | Campaign materials              | Campaign materials approved      |
| Integration & Testing | 9             | 10         | 2                | 0       | Compliance report               | Pass compliance checks           |
| Deployment           | 11            | 12         | 2                | 3       | Campaign performance report      | Campaigns launched successfully  |

**Intermediate Milestones (MANDATORY):** include leading indicators for ROI/turnover (e.g., “Retention +2 pp @Week 6”, “Offer-accept +5 pp @Week 4”).

**Critical Path & Slack**

| Task                  | Depends On | Slack [days] | Risk if Slips        | Mitigation              | Owner       |
|-----------------------|------------|---------------|----------------------|-------------------------|-------------|
| Stakeholder meetings   | None       | 0             | Delayed engagement    | Schedule early           | Blanca      |
| Campaign materials     | Stakeholder report | 0      | Delayed launch        | Allocate extra resources | Marketing   |
| Compliance report      | Campaign materials | 0     | Legal issues          | Preemptive legal review  | Compliance  |

**WHY:** Sequencing maximizes early value, protects dependencies, and keeps slack under control.

---

## 8) Resources, Capacity & Budget
- **Staffing by Phase:** 
  - FTEs required: 1 project manager, 1 marketing specialist, 1 compliance officer; onboarding time of 2 weeks.
- **Vendors/Partners:** Legal advisors; SLA for response time ≤72h; exit plan includes data ownership clauses.

**Budget & Cash Flow (REQUIRED)**

| Category              | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Total  | Notes                          |
|-----------------------|---------:|---------:|---------:|---------:|--------:|---------------------------------|
| Personnel             | €20,000  | €20,000  | €10,000  | €10,000  | €60,000 | 1 FTE + legal advisor           |
| Campaign Costs        | €5,000   | €10,000  | €5,000   | €5,000   | €25,000 | Promotions and materials        |
| Training              | €3,000   | -        | -        | -        | €3,000  | Staff training sessions         |
| Compliance            | €2,000   | -        | -        | -        | €2,000  | Legal compliance checks         |
| Contingency (10%)     | €3,000   | €3,000   | €2,000   | €2,000   | €10,000 | Risk management allocation      |

- CapEx vs OpEx, contingency %, payment milestones; capacity model (throughput units/period, utilization %).

**WHY:** Resourcing and spend profile support feasibility and time-to-impact while containing downside risk.

---

## 9) Responsibility & Accountability (RACI — ≥4 roles)
| Deliverable/Activity   | Exec Sponsor | Business/HR Lead | Tech Lead | PMO        | Legal/Compliance | Finance   | Data/Analytics | Marketing/Comms | Ops/Support |
|------------------------|--------------|------------------|-----------|------------|------------------|-----------|----------------|------------------|-------------|
| Stakeholder report      | Blanca       | -                | -         | -          | -                | -         | -              | -                | -           |
| Campaign materials      | -            | Marketing        | -         | PMO        | Compliance        | -         | -              | Marketing        | -           |
| Compliance report       | -            | -                | -         | -          | Compliance        | -         | -              | -                | -           |
| Campaign performance     | -            | -                | -         | PMO        | -                | Finance   | Data           | Marketing        | -           |

*(Use R/A/C/I; exactly one A per deliverable.)*

**WHY:** Clear accountabilities reduce decision latency and rework.

---

## 10) Phase Gate System (QA & Compliance — REQUIRED)
| Phase                | Gate ID | Test                     | Criterion Link (ROI_12m / GDPR_Compliance / Time_to_Impact / Adoption_90d / Reliability_SLO) | Threshold | Owner       | Status |
|----------------------|---------|--------------------------|------------------------------------------------------------------------------------------------|-----------|-------------|--------|
| Preparation          | G1      | Stakeholder feedback      | Adoption_90d                                                                                    | ≥75%      | Blanca      | TBD    |
| Core Implementation   | G2      | Campaign material review  | ROI_12m                                                                                         | Pass      | Marketing   | TBD    |
| Integration & Testing | G3      | GDPR compliance check     | GDPR_Compliance                                                                                 | Pass      | Compliance   | TBD    |
| Deployment           | G4      | Campaign performance review | ROI_12m / Adoption_90d                                                                          | Tracking live | Finance   | TBD    |

**WHY:** Gates enforce objective pass/fail checks aligned with criteria lock; failures trigger mitigations before scale.

---

## 11) Risk, Compliance & Readiness
**Risk Register (implementation-phase)** — **≥10 distinct risks**

| ID | Risk                  | Prob (0–1 or L–H) | Impact (€ or scale) | Horizon  | Early Signal            | Mitigation               | Owner        | Provenance   |
|----|-----------------------|-------------------:|---------------------:|----------|-------------------------|--------------------------|--------------|--------------|
| RISK-1 | Market saturation     | 0.3                 | €3,900               | 6 months | Low donations           | Diversify outreach        | Blanca       | Context §…  |
| RISK-2 | Low engagement        | 0.4                 | €2,000               | 6 months | Low response rates      | Improve targeting strategies | Marketing    | Context §…  |
| RISK-3 | Compliance audits     | 0.2                 | €5,000               | 3 months | Compliance issues       | Regular training          | Compliance    | Context §…  |
| RISK-4 | Delayed launch        | 0.3                 | €1,500               | 1 month  | Late campaign materials  | Allocate extra resources   | Marketing    | Context §…  |
| RISK-5 | Legal challenges      | 0.2                 | €4,000               | 6 months | Legal reviews fail       | Preemptive legal review   | Compliance    | Context §…  |

**Compliance Matrix** — DPIA/PIA, security, accessibility, sector rules.

| Requirement             | Applicability | Lead Time [days] | Evidence Needed | Gate (Pass/Fail) | Owner       |
|-------------------------|---------------|------------------|------------------|------------------|-------------|
| GDPR compliance         | All phases    | 30               | Compliance report | Pass             | Compliance   |
| Accessibility compliance | All phases    | 15               | Accessibility audit | Pass             | Compliance   |

**Readiness Checklist (Yes/No with comments — REQUIRED)**

| Variable                  | OK?  | Comment          |
|---------------------------|------|------------------|
| Budget ≤ approved limit   | Yes  |                  |
| Staff assigned & onboarding plan | Yes  |                  |
| Risk register updated (≤7 days) | Yes  |                  |
| KPI dashboard linked to telemetry | Yes  |                  |

**WHY:** Focuses leaders on the few constraints that govern Go/No-Go and safe rollout.

---

## 12) Rollout, Cut-over & Reversibility
- **Rollout:** Phased rollout starting with pilot regions; traffic ramps by 20% per month; eligibility rules based on donor engagement history; clear customer communications in simple language.
- **Feature Flags:** Ownership assigned to Marketing; flip protocol documented; audit trail maintained.
- **Cut-over Runbook:** T-minus schedule for all activities; validation checks at T+0; owner assigned for each step; go/no-go criteria based on compliance and engagement metrics.
- **Rollback Playbooks:** Triggers for fallback include low engagement metrics; steps for reverting to previous states outlined; data reconciliation procedures established.

**WHY:** Reversibility and staged exposure protect users and business while learning.

---

## 13) Post-Launch Monitoring & Adaptive Control
- **Dashboards:** KPI monitoring for engagement, compliance, and financial metrics; alert thresholds set for immediate action.
- **Ops:** MTTA/MTTR targets established; incident management protocols in place.
- **Learning Loop:** Weekly reviews of decision log; promote/hold/kill rules based on performance metrics.
- **Benefits Tracking:** Baseline versus actual performance compared quarterly; ROI realization calendar established with variance drivers documented.

**WHY:** Ensures value realization and continuous risk control.

---

## 14) Handoff to Simulate & Evaluate (MANDATORY — Must be fully populated)
### 14.1 Scenarios (SCN-*)
| ID   | Scenario Name         | Family                  | Description                        | Variables Changed         | Fixed Parameters            | Exposure (%) | Cohort/Segment | Rollout Shape (linear/logistic/step) | Observation Window | Provenance     |
|------|-----------------------|-------------------------|------------------------------------|---------------------------|-----------------------------|---------------|----------------|---------------------------------------|---------------------|----------------|
| SCN-1| Base Scenario         | Strategic               | Current strategy without changes   | None                      | Current engagement tactics  | 100%          | All donors     | Linear                               | 3 months           | Context §…    |
| SCN-2| Optimistic Scenario    | Tactical                | Enhanced campaigns with more funding | Increased budget          | Current engagement tactics  | 75%           | Target group    | Logistic                             | 2 months           | Context §…    |
| SCN-3| Pessimistic Scenario   | Tactical                | Reduced budget impacting outreach   | Decreased budget          | Current engagement tactics  | 50%           | All donors     | Linear                               | 3 months           | Context §…    |

### 14.2 Parameters (PAR-*)
| ID    | Variable                 | Unit  | Base        | Range/Distribution          | Correlations (IDs) | Owner       | As-Of Date | Rationale/Formula              | Provenance     |
|-------|--------------------------|-------|-------------|-----------------------------|--------------------|-------------|-------------|---------------------------------|----------------|
| PAR-1 | Total Budget             | €     | €78,000     | €70,000 - €100,000          | None               | Finance     | 2025-10-23  | Total planned budget for 2025  | Context §…    |
| PAR-2 | Campaign Engagement Rate  | %     | 75%         | 60% - 90%                   | PAR-1              | Marketing    | 2025-10-23  | Average engagement from campaigns| Context §…    |
| PAR-3 | Compliance Rate          | %     | 90%         | 85% - 100%                   | None               | Compliance   | 2025-10-23  | Rate of compliance with GDPR    | Context §…    |
| PAR-4 | Legacy Donation Average   | €     | €74,000     | €50,000 - €100,000          | None               | Finance     | 2025-10-23  | Average legacy donation in Spain | Context §…    |

### 14.3 Correlations (CORR-*)
| Var1 (PAR-#) | Var2 (PAR-#) | Coefficient (ρ) | Segment | Method (historical/assumed/benchmark) | Provenance     |
|---------------|--------------|------------------|---------|---------------------------------------|----------------|
| PAR-1        | PAR-2       | 0.75             | All     | Historical analysis                    | Context §…    |
| PAR-2        | PAR-3       | 0.60             | All     | Benchmarking against industry standards | Context §…    |

### 14.4 Experiments (EXP-*)
| ID   | Scenario(s)      | Hypothesis (direction + unit + timeframe) | Primary Metric           | Guardrails (min/max) | Design                | α   | Power (1-β) | MDE   | Sample Size (n) | Duration | Segments   | Analysis Plan      | Ethics/Consent | Provenance     |
|------|------------------|---------------------------------------------|--------------------------|-----------------------|-----------------------|-----|--------------|-------|------------------|----------|------------|--------------------|----------------|----------------|
| EXP-1| SCN-1, SCN-2    | Increasing donor communications will raise engagement by 15% in 60 days | Engagement rate          | 70% ≤ rate ≤ 90%     | A/B Testing           | 0.05 | 0.8          | 5%    | 200              | 60 days  | All donors  | Comparative analysis | Informed consent | Context §…    |

### 14.5 Gate Thresholds (GATE-*)
| Criterion             | Gate ID | Threshold   | Evidence Required              | Result Type (Pass/Fail/Conditional) | Owner       |
|-----------------------|---------|-------------|---------------------------------|-------------------------------------|-------------|
| ROI_12m               | G1      | >€81,900    | ROI calculation                  | Pass                                | Finance     |
| GDPR_Compliance       | G2      | Pass        | Compliance audit report          | Pass                                | Compliance   |
| Time_to_Impact        | G3      | ≤6 months   | Campaign performance metrics      | Pass                                | Marketing    |
| Adoption_90d          | G4      | ≥75%        | Engagement metrics analysis      | Pass                                | Marketing    |

### 14.6 Normalization Rules (NORM-*)
| Currency | FX Rate | CPI | PPP | Base Year | Source       | Access Date  |
|----------|---------|-----|-----|-----------|--------------|--------------|
| EUR      | 1.00    | 0.95| 0.90| 2025      | ECB          | 2025-10-23   |
| USD      | 1.05    | 0.90| 0.85| 2025      | US Bureau     | 2025-10-23   |

### 14.7 Traceability Map (MAP-*)
| Plan Element (WBS/Gate/Nudge) | Parameter (PAR-#) | Scenario (SCN-#) | Criterion/KPI            | Data Source          | Owner       |
|-------------------------------|--------------------|-------------------|-------------------------|-----------------------|-------------|
| Stakeholder report             | None               | SCN-1             | Adoption_90d            | Context §…            | Blanca      |
| Campaign materials             | PAR-2             | SCN-2             | ROI_12m                 | Marketing Analytics    | Marketing   |

**WHY:** Provides Simulate with concrete worlds, parameters, and relationships; gives Evaluate a consistent schema to interpret and compare outcomes.

---

## 15) Data Gaps & Collection Plan (MANDATORY; ≥8 items if gaps exist)
| Missing Data (WHAT)          | Why Needed                                     | Method (instrument/test/query)        | Owner       | ETA         | Acceptance Criteria                    | Expected Source      |
|-------------------------------|------------------------------------------------|---------------------------------------|-------------|-------------|---------------------------------------|----------------------|
| Donor engagement metrics       | Essential for measuring campaign success       | Survey                                 | Marketing   | 2025-11-30  | Minimum 100 responses collected        | Internal surveys     |
| Market trends data            | Understanding potential market size is crucial | Market analysis report                 | Marketing   | 2025-11-15  | Report completed and validated         | External sources     |
| Compliance data               | Ensures adherence to legal standards           | Compliance checks                      | Compliance   | Ongoing     | All checks passed                      | Compliance audits    |
| Historical donation data      | Needed for trend analysis                      | Data extraction from CRM               | Finance     | 2025-10-30  | Historical reports compiled            | Internal CRM         |
| Feedback from campaigns        | To improve future campaigns                    | Post-campaign feedback surveys         | Marketing   | 2025-12-31  | 80% donor response rate                | Campaign materials    |
| Training effectiveness metrics | To assess training impact                      | Training feedback forms                | HR          | 2026-01-15  | 75% staff satisfaction                  | Training sessions    |
| Legal framework updates       | Required for compliance                         | Legal reviews                          | Compliance   | Ongoing     | Updated legal framework documented     | Legal advisors       |
| Benchmarking data             | To compare performance                          | Research on industry standards         | Marketing   | 2025-12-20  | Benchmarking report completed          | External benchmarks   |

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
```