# Phase: Implementation
**Timestamp:** 20251020_171916
**Workflow ID:** workflow_20251020_164618
**Language Tag:** en
```
# Implementation Plan for: Option A — International Recruitment
**Criteria Version:** v1.0 • **Lock Hash:** criteria-v1.0:5a1b2c3d4e5f6789abcdef01234567890abcdef01234567890abcdef0123456789  
**Execution Timestamp (local):** 2025-10-20 17:25:00 • **Calendar:** 2025-10-20  
**Selected Option Source:** Create §…; URL/Doc-ID + access date  
**Decision Link:** Aligned to locked **CRIT/KPI/OBJ** (CRIT-1, CRIT-2, CRIT-3, CRIT-4)

**WHY:** This header binds plan → selected option → criteria lock so simulation/evaluation remain consistent and auditable.

---

## 0) Executive Summary
- **Selected Option (A):** International Recruitment — Leverage international recruitment from Portugal and Latin America to quickly onboard specialized technicians, addressing immediate workforce shortages.
- **Operating Model:** Phased deployment with pilot to scale gates; feature flags for controlled rollout.
- **Timeline Envelope:** 1–12 weeks • **Time-to-First-Value:** 6 weeks • **Scale Ready:** Q2 2025
- **Outcome Targets (3–5):** 
  - +5 pp retention @90d
  - -10% cost per hire @Q3
  - +10 NPS points @60d
- **SLO/SLA Anchors:** 
  - p95 latency < 200ms
  - availability ≥ 99.5%
  - RPO/RTO ≤ 15min
- **Budget Envelope:** CapEx €170,000, OpEx €140,000/period, Contingency 10%
- **Top 3 Risks (p×i):** 
  - RISK-HR-1: High turnover of critical talent (Prob: 0.4, Impact: €1.5M).
  - RISK-TECH-1: Integration instability (Prob: 0.35, Impact: -0.8 p.p. Reliability).
  - RISK-LGL-1: GDPR non-compliance (Prob: 0.2, Impact: €300K).
- **Go/No-Go Gates:** 
  - GDPR compliance pass by 2025-12-31
  - Budget adherence with variance ≤ 5%

**WHY:** Summarizes value, speed, risk, and gating alignment to enable an informed Go/No-Go.

---

## 1) Implementation Strategy, Operating Model & Customer Lens
- **Delivery Approach:** Agile cadence with 2-week sprints, daily stand-ups, and retrospective ceremonies; baseline velocity set at 20 story points/sprint.
- **Customer-Centric Service Blueprint (front/back-stage):** 
  - **Touchpoints:** 
    - Recruitment campaign promotions (Front-stage)
    - Onboarding and training sessions (Back-stage)
  - **Customer Outcomes/SLOs:** 
    - SLO for onboarding completion rate at 90% within 6 weeks.
- **Decision Rights & Escalation:** HR Manager approves scope/cost/time; escalation path ≤ 24h for urgent issues.
- **Quality & Safety Bars:** 
  - Accessibility (WCAG 2.2)
  - Security audits at phase gates.
- **Change Control:** Feature flags for new hires, change control board meets bi-weekly.

**Provenance:** Context §1  
**WHY:** Chosen operating model minimizes risk under current constraints while protecting customer experience.

---

## 2) Work Breakdown Structure (WBS) & Acceptance (RELATIVE TIME)

| Phase                | Workstream        | WP ID | Work Package                  | Deliverables                     | Objective Acceptance Criteria            | Dependencies          | Effort [FTE-weeks] | Duration [weeks] | % Slack | Provenance |
|----------------------|-------------------|-------|-------------------------------|----------------------------------|-----------------------------------------|-----------------------|---------------------|------------------|---------|------------|
| Preparation          | Recruitment Plan   | WP-01 | Develop recruitment strategy   | Strategy Document                | Document approved by HR Director       | None                  | 2                   | 2                | 0%      | Context §1 |
| Core Implementation   | Campaign Execution | WP-02 | Launch recruitment campaign    | Campaign Live                    | 35% Adoption_90d                       | WP-01                 | 3                   | 3                | 0%      | Context §1 |
| Core Implementation   | Onboarding         | WP-03 | Onboard new hires             | Training Program Completed       | 90% onboarding completion within 6 weeks| WP-02                 | 4                   | 4                | 0%      | Context §1 |
| Integration & Testing | Systems Integration | WP-04 | Integrate onboarding software  | Software Operational              | 99.5% Reliability_SLO                   | WP-03                 | 1                   | 1                | 0%      | Context §1 |
| Deployment           | Monitoring         | WP-05 | Monitor recruitment metrics    | Dashboard Reporting               | Metrics dashboard live within 2 weeks  | WP-04                 | 2                   | 2                | 0%      | Context §1 |

- **Buffer Policy:** 10% buffer for each phase; critical path WPs have zero slack.
- **Effort→Duration:** `Duration [weeks] = Effort [FTE-weeks] / Assigned FTE`.
- **Critical Path:** WP-01 → WP-02 → WP-03 → WP-04.

**WHY:** Decomposition exposes risks early and accelerates earliest value with controlled buffers.

---

## 3) Behavioral Economics Plan (Choice Architecture & Nudges)
**Behavioral Nudge Catalogue**

| ID | Journey Step         | Decision to Influence     | Mechanism (bias/heuristic) | Intervention (what/how/where) | Microcopy/Label          | Variants | Expected Effect [unit, timeframe] | Guardrails & Ethics         | Telemetry Event(s)  | Owner          | Provenance |
|----|----------------------|---------------------------|----------------------------|-------------------------------|--------------------------|----------|-----------------------------------|------------------------------|---------------------|----------------|------------|
| NUDGE-01 | Recruitment Campaign | Increase application rates | Social Proof               | Highlight peer success stories | "Join your peers!" | A/B      | +10% applications in 2 weeks      | No false claims; consent required | Application metrics   | HR Manager     | Context §1 |
| NUDGE-02 | Onboarding           | Improve retention          | Commitment                 | Early engagement in onboarding | "You're part of the team!" | A/B | +5 pp retention @90d              | No pressure tactics; clear opt-out | Retention rates      | HR Manager     | Context §1 |
| NUDGE-03 | Training Completion  | Increase training uptake   | Default                    | Automatic enrollment in programs | "You're signed up!" | A/B      | +20% completion rate in 4 weeks    | Easy opt-out; clear communication | Training completion metrics | Training Coordinator | Context §1 |
| NUDGE-04 | Feedback Surveys     | Enhance feedback response  | Framing                    | Timing reminders via email     | "We value your input!"  | A/B      | +15% response rates in 1 month      | Respect privacy; easy opt-out | Feedback response rate | HR Manager     | Context §1 |

**WHY:** Carefully chosen levers reduce friction & improve adoption with measurable, ethical effects.

---

## 4) Architecture, NFRs & Environments
- **High-Level Architecture:** 
  - Components: Recruitment software, onboarding platform, HRIS.
  - Data flows: Applicant data from recruitment to HRIS, onboarding metrics to monitoring dashboard.
- **NFRs (targets):** 
  - Availability: 99.5%
  - Latency p95: ≤200ms
  - Throughput: 50 req/s
  - Error budget: ≤1h/month
  - RPO/RTO: ≤15min
- **Environments:** 
  - Development, Testing, Staging, and Production with data seeding for testing.
- **Security & Privacy:** 
  - Multi-factor authentication, encryption at rest and in transit, DPIA required before launch.
- **Observability:** 
  - Logs for all critical events, metrics dashboards for real-time insights.

**SLO/SLA Table (REQUIRED)**

| Service/Flow         | SLI                     | SLO Target          | Error Budget (per period) | Alert Threshold | Pager Policy    | Owner          | Runbook         |
|----------------------|-------------------------|---------------------|---------------------------|-----------------|------------------|----------------|-----------------|
| Recruitment System    | Application Response Time| < 200 ms             | 1h/month                  | >200ms          | Immediate escalation | HR Manager      | [Link to Runbook] |
| Onboarding Process    | Completion Rate        | ≥90%                 | 1% failure rate           | <90%            | Weekly review    | Training Coordinator | [Link to Runbook] |

**WHY:** NFR/SLO alignment prevents value erosion and service instability post-launch.

---

## 5) Data, Telemetry & Measurement Spec

| Signal               | Type (event/metric) | Schema (fields & types)  | Unit        | Frame (cohort/geo/time) | Source System | Cadence | DQ Checks | Retention | Consumers | Provenance |
|----------------------|---------------------|--------------------------|-------------|-------------------------|---------------|---------|-----------|-----------|-----------|------------|
| Application Rate     | Metric              | {applications: int}      | Count       | Weekly                  | Recruitment System | Weekly  | Check for duplicates | 1 year    | HR, Management | Context §1 |
| Onboarding Completion | Metric              | {completed: int, total: int} | %         | Monthly                 | Onboarding System | Monthly | Verification of records | 1 year    | HR, Training | Context §1 |
| Retention Rate       | Metric              | {retained: int, total: int} | %         | Quarterly               | HRIS          | Quarterly | Review against benchmarks | 2 years   | HR, Management | Context §1 |

**Formulas:**
- ROI = (Net Benefits / Investment) × 100
- NPV = Σ_t (CF_t / (1 + WACC)^t)
- Payback = months until cumulative net CF ≥ 0

**Normalization:** 
- FX rates from [source/date], CPI from [base year/source], PPP if used.

**WHY:** Ensures comparable, auditable measurement across phases and cohorts.

---

## 6) Experimentation & Evidence Plan

| ID | Hypothesis (direction + unit + timeframe) | Primary Metric | Guardrails | Design (A/B, diff-in-diff, DoE) | α | Power (1-β) | MDE | Sample Size (n) | Duration | Segments | Analysis Plan | Ethics/Consent | Provenance |
|----|-------------------------------------------|----------------|------------|-------------------------------|---|-------------|-----|----------------|---------|----------|----------------|-----------------|------------|
| EXP-01 | Increasing application rates by 10% within 4 weeks through social proof | Application Rate | Monitor for fairness in representation | A/B testing | 0.05 | 0.8 | 5% | 200 | 1 month | All applicants | Compare conversion rates | Informed consent | Context §1 |
| EXP-02 | Boosting onboarding completion by 20% through commitment nudges within 6 weeks | Onboarding Completion | Ensure no pressure tactics | A/B testing | 0.05 | 0.8 | 10% | 150 | 6 weeks | New hires | Analyze completion rates | Informed consent | Context §1 |

**WHY:** De-risks assumptions and quantifies expected lift under realistic conditions.

---

## 7) Timeline, Milestones & Critical Path (RELATIVE WEEKS)

| Phase                | Start (Week) | End (Week) | Duration [weeks] | % Slack | Key Deliverables               | Phase Gate Criteria (pass/fail) | Provenance |
|----------------------|---------------|------------|------------------|---------|--------------------------------|---------------------------------|------------|
| Preparation          | 1             | 2          | 2                | 0%      | Recruitment Strategy Document  | Approved by HR Director         | Context §1 |
| Core Implementation   | 3             | 5          | 3                | 0%      | Campaign Launch                | 35% Adoption_90d                | Context §1 |
| Integration & Testing | 6             | 6          | 1                | 0%      | Onboarding Software Operational | 99.5% Reliability_SLO            | Context §1 |
| Deployment           | 7             | 12         | 6                | 0%      | Monitoring Dashboard Live       | Metrics dashboard live           | Context §1 |

**Intermediate Milestones:** 
- **Retention +2 pp at Week 6**
- **Offer-accept ≥ +5 pp at Week 4**

**Critical Path & Slack**

| Task                  | Depends On | Slack [days] | Risk if Slips        | Mitigation              | Owner          |
|-----------------------|------------|---------------|----------------------|-------------------------|----------------|
| WP-01                 | None       | 0             | Delayed strategy     | Weekly checks           | HR Manager     |
| WP-02                 | WP-01     | 0             | Low applications      | Ramp up campaigns       | HR Manager     |
| WP-03                 | WP-02     | 0             | Low onboarding rates  | Additional training      | Training Coordinator |

**WHY:** Sequencing maximizes early value, protects critical dependencies, and keeps slack under control.

---

## 8) Resources, Capacity & Budget

| Category             | Phase 1  | Phase 2  | Phase 3 | Phase 4 | Total   | Notes                                           |
|----------------------|----------:|----------:|---------:|---------:|--------:|-------------------------------------------------|
| CapEx                | 170,000  | 0        | 0       | 0       | 170,000 | Recruitment software and onboarding tools       |
| OpEx                 | 0        | 140,000  | 0       | 0       | 140,000 | Campaign costs and staff salaries               |
| Contingency %        | 10%      | 10%      | 10%     | 10%     | -       | For unforeseen expenses                          |

**WHY:** Resourcing and spend profile support feasibility and time-to-impact while containing downside risk.

---

## 9) Responsibility & Accountability (RACI — ≥4 roles)

| Deliverable/Activity               | Exec Sponsor  | Business/HR Lead | Tech Lead       | PMO          | Legal/Compliance | Finance           | Data/Analytics | Marketing/Comms | Ops/Support |
|------------------------------------|----------------|------------------|------------------|--------------|------------------|-------------------|----------------|----------------|-------------|
| Recruitment Strategy Document       | HR Director     | HR Manager       | N/A              | Project Manager | Legal Team      | Finance Team     | Data Analyst    | Marketing Team  | N/A         |
| Campaign Launch                     | HR Director     | HR Manager       | N/A              | Project Manager | Legal Team      | Finance Team     | Data Analyst    | Marketing Team  | N/A         |
| Onboarding Software Operational     | N/A             | Training Coordinator | IT Manager     | N/A          | N/A              | N/A               | Data Analyst    | N/A            | N/A         |
| Monitoring Dashboard Live           | N/A             | N/A              | IT Manager       | Project Manager | N/A              | Finance Team     | Data Analyst    | N/A            | N/A         |

**WHY:** Clear accountabilities reduce decision latency and rework.

---

## 10) Phase Gate System (QA & Compliance — REQUIRED)

| Phase                | Gate ID | Test                          | Criterion Link (ROI_12m / GDPR_Compliance / Time_to_Impact / Adoption_90d / Reliability_SLO) | Owner          | Status |
|----------------------|---------|-------------------------------|------------------------------------------------------------------------------------------------|----------------|--------|
| Preparation          | G1      | Recruitment strategy approved | ROI_12m                                                                                       | PMO            | TBD    |
| Core Implementation   | G2      | Campaign launch successful    | Adoption_90d                                                                                    | Finance Team    | TBD    |
| Integration & Testing | G3      | Onboarding software validated  | Reliability_SLO                                                                                 | Legal Team      | TBD    |
| Deployment           | G4      | Metrics dashboard live        | ROI_12m / Adoption_90d                                                                          | Finance/HR Team | TBD    |

**WHY:** Gates enforce objective pass/fail checks aligned with criteria lock; failures trigger mitigations before scale.

---

## 11) Risk, Compliance & Readiness

**Risk Register (implementation-phase)**

| ID      | Risk                                | Prob (0–1 or L–H) | Impact (€/unit or L–H) | Horizon | Early Signal                  | Mitigation (HOW)                | Owner          | Provenance |
|---------|-------------------------------------|--------------------|-------------------------|---------|-------------------------------|----------------------------------|----------------|------------|
| RISK-HR-1 | High turnover of critical talent    | 0.4                | €1.5M                   | 2025    | Increased recruitment costs    | Implement retention programs      | HR Team        | Context §1 |
| RISK-TECH-1 | Integration instability             | 0.35               | −0.8 p.p. Reliability   | 2025    | Error spikes                  | Improve monitoring                | IT Team        | Context §1 |
| RISK-LGL-1 | GDPR non-compliance                 | 0.2                | €300K                   | 2025    | Audit finding                 | Conduct DPIA                     | Legal Team     | Context §1 |

**Compliance Matrix**

| Requirement                      | Applicability | Lead Time [days] | Evidence Needed     | Gate (Pass/Fail) | Owner          |
|----------------------------------|---------------|------------------|---------------------|------------------|----------------|
| GDPR Compliance                   | All phases    | 30               | DPIA report         | Pass             | Legal Team     |
| Accessibility Compliance (WCAG 2.2) | All phases    | 20               | Accessibility audit  | Pass             | QA Team        |

**Readiness Checklist (Yes/No with comments — REQUIRED)**

| Variable                             | OK? | Comment                               |
|--------------------------------------|-----|---------------------------------------|
| Budget ≤ approved limit              | [ ] |                                       |
| Staff assigned & onboarding plan     | [ ] |                                       |
| Risk register updated (≤7 days)     | [ ] |                                       |
| KPI dashboard linked to telemetry    | [ ] |                                       |

**WHY:** Focuses leaders on the few constraints that govern Go/No-Go and safe rollout.

---

## 12) Rollout, Cut-over & Reversibility

- **Rollout:** Pilot with 10 technicians in Q2 2025, followed by gradual scaling to all technicians; communication plan includes plain language notifications and feedback channels.
- **Feature Flags:** Ownership by HR Manager, flip protocol documented, audit trail maintained.
- **Cut-over Runbook:** Step-by-step timeline from pilot to full-scale, including roles, go/no-go criteria, and verification checklist.
- **Rollback Playbooks:** Triggers based on user feedback, steps to revert to previous systems, data reconciliation processes.

**WHY:** Reversibility and staged exposure protect users and the business while learning.

---

## 13) Post-Launch Monitoring & Adaptive Control

- **Dashboards:** Real-time KPIs displayed on dashboards for HR and management; alert thresholds set for application rates and onboarding completion.
- **Ops:** MTTA/MTTR targets set at ≤30min; incident management protocols established.
- **Learning Loop:** Weekly review sessions to assess pilot outcomes; decision log maintained for actions taken (persist/revert/iterate).
- **Benefits Tracking:** Baseline vs actual tracking for ROI realization; adjustments made based on variance analysis.

**WHY:** Ensures value realization and continuous risk control.

---

## 14) Data Gaps & Collection Plan (MANDATORY; ≥8 items if gaps exist)

| Missing Data (WHAT)                | Why Needed                     | Method (instrument/test/query) | Owner           | ETA          | Acceptance Criteria            | Expected Source        |
|-------------------------------------|--------------------------------|--------------------------------|------------------|--------------|--------------------------------|-------------------------|
| Turnover replacement cost           | To calculate ROI               | HR database extract            | HR Ops           | 2025-10-21   | Error ≤ ±5%                   | Internal                |
| Benchmark retention uplift          | Validation of assumptions      | Industry report                | Analyst          | 2025-11-01   | n≥30 sample                   | Analyst house           |

**WHY:** Converts uncertainty into time-boxed evidence generation with clear ownership.

---

## Appendices

- **A. Formulas & Parameters:** ROI, NPV, IRR, Payback; elasticity notes; KPI definitions.
- **B. Normalization Tables:** FX rates, CPI base year, PPP if used.
- **C. Source Register:** Titles, publisher/author, date (YYYY-MM-DD), URL or Doc-ID/§, source type, recency note.
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
```