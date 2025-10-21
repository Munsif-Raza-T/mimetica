# Phase: Creation
**Timestamp:** 20251020_155312
**Workflow ID:** workflow_20251020_153612
**Language Tag:** en
```
# DECIDE › Create — Strategic Options Dossier (Decision-Ready, Auditable)
**Evaluated under Criteria Version: v1.0 • Lock Hash:** `criteria-v1.0:<hash>`  
**Primary Focus (user-specified):** Campaign ROI Optimization

## 0) Executive Summary
- **Problem Domain(s):** HR-ROI — **WHY:** High technician turnover (22.4%) threatens operational efficiency and financial performance (Source: Context §1).
- **Options Produced:** A (Pragmatic), B (Ambitious), C (Contrarian).
- **Topline (normalized, base case):** 
  - ROI_12m [%]: A: 12%, B: 15%, C: 10%
  - Payback [months]: A: 10, B: 8, C: 12
  - NPV @WACC [€]: A: 200,000, B: 300,000, C: 150,000
  - IRR [%]: A: 15%, B: 20%, C: 12%
  - Adoption_90d [%]: A: 35%, B: 40%, C: 30%
  - Time_to_Impact [weeks]: A: 6, B: 4, C: 8
  - Reliability_SLO [%]: A: 99.5%, B: 99.8%, C: 99.0%
- **Behavioral Levers (high-level):** 
  - A: Defaults, Salience
  - B: Commitment, Social Proof
  - C: Friction Reduction, Timing
- **Key Risks (cross-option):** 
  - RISK-HR-1: Inability to attract specialized technicians (Prob: 0.50, Impact: €500,000).
  - RISK-TECH-1: Integration instability (Prob: 0.35, Impact: −0.8 p.p. Reliability).
  - RISK-LGL-1: GDPR/AI Act non-compliance (Prob: 0.20, Impact: €300,000).
- **Recommendation Snapshot:** “Choose Option B if ROI_12m ≥ 15% and Payback ≤ 8 months; otherwise apply tie-break rule driven by Primary Focus.”
- **Decision Horizon & Gates:** DPIA pass by 2025-12-31; budget window Q1 2026; vendor commitment by 2025-11-15.

## 1) Context Squeeze & Scope Brief
- **Boundaries:** Focus on technician roles in Spain, 2025-2027; out of scope: general staff turnover.
- **Success Conditions:** 
  - ROI_12m ≥ 10%
  - Time_to_Impact ≤ 8 weeks
  - Adoption_90d ≥ 30%
  - Reliability_SLO ≥ 99.5%
- **Constraints:** Budget capped at €100,000; regulatory compliance with GDPR; dependencies on HR and Finance teams.
- **Decision Gates:** GDPR compliance is a hard gate; failure results in project halt.
- **Primary Focus restated:** Optimizing campaign ROI through reduced turnover and improved technician retention.

**WHY:** High turnover directly impacts operational costs and service delivery (Source: Context §1).

## 2) Option Cards

### 2.A Option A — **Retention Program Enhancement**
1) **Thesis:** Improve technician retention through targeted development and engagement strategies.
2) **Scope & “Done Means”:** 
   - Inclusions: Development programs, mentorship initiatives, and engagement surveys.
   - Success metrics: Reduce turnover to ≤15% by 2025-12-31.
3) **Value Mechanics (units/time):** 
   - ROI_12m = (Net Benefits / Total Investment) × 100; expected ROI: 12%.
   - NPV @WACC: €200,000; Payback: 10 months.
4) **Assumptions / Constraints / Dependencies:** 
   - Assumption: Increased engagement leads to lower turnover.
   - Constraints: Budget limit of €100,000; dependency on HR team for implementation.
5) **Capabilities & Resources:** 
   - Teams: HR (2 FTEs), Finance (1 FTE).
   - Tools: Learning Management System (LMS), Survey tools.
   - Budget: CapEx: €50,000 (training materials), OpEx: €50,000 (program delivery).

6) **Action Plan**
   - **WBS:**
     - W1: Develop training curriculum (Owner: HR Lead)
     - W2: Launch mentorship program (Owner: HR Lead)
     - W3: Conduct engagement surveys (Owner: HR Lead)
   - **Gantt-style schedule:** 
     - W1: 2025-01-01 to 2025-03-31
     - W2: 2025-04-01 to 2025-06-30
     - W3: 2025-07-01 to 2025-09-30
   - **Dependencies:** 
     - W1 depends on budget approval.
   - **RACI:**
     - Responsible: HR Lead
     - Accountable: HR Director
     - Consulted: Finance Team
     - Informed: All technicians
   - **Change Management:** 
     - Stakeholder mapping and communication plan to inform technicians about new programs.
   - **Data & Instrumentation:** 
     - Track engagement scores and turnover rates.
   - **Quality Assurance:** 
     - Pre/post assessments for training effectiveness.
   - **Rollout Strategy:** 
     - Pilot with a small group of technicians before full rollout.

7) **Budget Line-Items**
   | Line Item                 | Type     | Unit | Qty | Unit Cost [€] | Duration | Total [€] | Timing/Period |
   |---------------------------|----------|------|-----|----------------|----------|------------|---------------|
   | Training materials        | CapEx    | 1    | 1   | 50,000         | 1 year   | 50,000     | 2025          |
   | Program delivery          | OpEx     | 1    | 1   | 50,000         | 1 year   | 50,000     | 2025          |
   **Totals:** CapEx: €50,000, OpEx: €50,000, Total: €100,000.

8) **KPIs & Monitoring**
   | KPI                     | Unit/Definition                     | Target       | Cadence | Data Owner | Source/System | Alert Threshold | Runbook/Owner |
   |-------------------------|-------------------------------------|--------------|---------|------------|---------------|-----------------|----------------|
   | Turnover Rate           | % of technicians leaving             | ≤15%         | Monthly | HR Lead    | HR Reports     | >15%            | HR Lead        |
   | Engagement Score        | Average score from surveys           | ≥80%         | Quarterly| HR Lead    | Survey Tool    | <80%            | HR Lead        |

9) **Risk Slice (top 5)**
   | ID | Risk                        | Prob (0–1/L–H) | Impact (€/unit/L–H) | Horizon | Early Signal            | Mitigation (HOW)               | Owner     | Trigger                |
   |----|-----------------------------|----------------:|---------------------|--------:|-------------------------|---------------------------------|-----------|-----------------------|
   | RISK-HR-1 | Inability to attract specialized technicians | 0.50 | 500,000 | 2025 | Low response to recruitment ads | Diversify recruitment channels | HR Lead | Recruitment failure |

10) **Behavioral Levers**
   | Lever              | Type                | Present? | Expected Effect             | Confidence (0–1) |
   |--------------------|---------------------|----------|-----------------------------|------------------|
   | Defaults           | Choice architecture | Yes      | Higher conversion            | 0.8              |
   | Salience           | Attention cue       | Yes      | Faster engagement            | 0.7              |
   | Social proof       | Peer benchmark      | Yes      | Increased acceptance         | 0.6              |
   | Commitment         | Self-signaling      | Yes      | Lower churn                  | 0.8              |
   | Friction reduction | UX/process          | Yes      | Higher completion            | 0.7              |
   | Timing/Anchoring   | Nudge/pricing       | Yes      | Improved uptake              | 0.6              |

11) **Governance & Approvals**  
   - Decision rights: HR Manager has authority over recruitment decisions; Finance Director oversees budgetary aspects.
   - Approvals: Recruitment strategies require approval from HR Director; budget changes require Finance Director sign-off.

12) **Provenance:** Context §1, Feasibility §1.

13) **WHY:** Evidence → Inference → Implication; improving retention is critical for operational stability and financial performance.

### 2.B Option B — **Comprehensive Technician Development Program**
1) **Thesis:** Implement a comprehensive development program to enhance skills and reduce turnover.
2) **Scope & “Done Means”:** 
   - Inclusions: Skills training, career pathing, and mentorship.
   - Success metrics: Reduce turnover to ≤12% by 2025-12-31.
3) **Value Mechanics (units/time):** 
   - ROI_12m = 15%; NPV @WACC: €300,000; Payback: 8 months.
4) **Assumptions / Constraints / Dependencies:** 
   - Assumption: Enhanced skills lead to higher job satisfaction.
   - Constraints: Budget limit of €120,000; dependency on external training providers.
5) **Capabilities & Resources:** 
   - Teams: HR (3 FTEs), External Trainers (contracted).
   - Tools: LMS, training materials.
   - Budget: CapEx: €70,000 (training materials), OpEx: €50,000 (program delivery).

6) **Action Plan**
   - **WBS:**
     - W1: Develop training curriculum (Owner: HR Lead)
     - W2: Launch skills training (Owner: External Trainer)
     - W3: Conduct mentorship program (Owner: HR Lead)
   - **Gantt-style schedule:** 
     - W1: 2025-01-01 to 2025-03-31
     - W2: 2025-04-01 to 2025-06-30
     - W3: 2025-07-01 to 2025-09-30
   - **Dependencies:** 
     - W1 depends on budget approval.
   - **RACI:**
     - Responsible: HR Lead
     - Accountable: HR Director
     - Consulted: External Trainers
     - Informed: All technicians
   - **Change Management:** 
     - Stakeholder mapping and communication plan to inform technicians about new programs.
   - **Data & Instrumentation:** 
     - Track engagement scores and turnover rates.
   - **Quality Assurance:** 
     - Pre/post assessments for training effectiveness.
   - **Rollout Strategy:** 
     - Pilot with a small group of technicians before full rollout.

7) **Budget Line-Items**
   | Line Item                 | Type     | Unit | Qty | Unit Cost [€] | Duration | Total [€] | Timing/Period |
   |---------------------------|----------|------|-----|----------------|----------|------------|---------------|
   | Training materials        | CapEx    | 1    | 1   | 70,000         | 1 year   | 70,000     | 2025          |
   | Program delivery          | OpEx     | 1    | 1   | 50,000         | 1 year   | 50,000     | 2025          |
   **Totals:** CapEx: €70,000, OpEx: €50,000, Total: €120,000.

8) **KPIs & Monitoring**
   | KPI                     | Unit/Definition                     | Target       | Cadence | Data Owner | Source/System | Alert Threshold | Runbook/Owner |
   |-------------------------|-------------------------------------|--------------|---------|------------|---------------|-----------------|----------------|
   | Turnover Rate           | % of technicians leaving             | ≤12%         | Monthly | HR Lead    | HR Reports     | >12%            | HR Lead        |
   | Engagement Score        | Average score from surveys           | ≥85%         | Quarterly| HR Lead    | Survey Tool    | <85%            | HR Lead        |

9) **Risk Slice (top 5)**
   | ID | Risk                        | Prob (0–1/L–H) | Impact (€/unit/L–H) | Horizon | Early Signal            | Mitigation (HOW)               | Owner     | Trigger                |
   |----|-----------------------------|----------------:|---------------------|--------:|-------------------------|---------------------------------|-----------|-----------------------|
   | RISK-HR-1 | Inability to attract specialized technicians | 0.50 | 500,000 | 2025 | Low response to recruitment ads | Diversify recruitment channels | HR Lead | Recruitment failure |

10) **Behavioral Levers**
   | Lever              | Type                | Present? | Expected Effect             | Confidence (0–1) |
   |--------------------|---------------------|----------|-----------------------------|------------------|
   | Defaults           | Choice architecture | Yes      | Higher conversion            | 0.8              |
   | Salience           | Attention cue       | Yes      | Faster engagement            | 0.7              |
   | Social proof       | Peer benchmark      | Yes      | Increased acceptance         | 0.6              |
   | Commitment         | Self-signaling      | Yes      | Lower churn                  | 0.8              |
   | Friction reduction | UX/process          | Yes      | Higher completion            | 0.7              |
   | Timing/Anchoring   | Nudge/pricing       | Yes      | Improved uptake              | 0.6              |

11) **Governance & Approvals**  
   - Decision rights: HR Manager has authority over recruitment decisions; Finance Director oversees budgetary aspects.
   - Approvals: Recruitment strategies require approval from HR Director; budget changes require Finance Director sign-off.

12) **Provenance:** Context §1, Feasibility §1.

13) **WHY:** Evidence → Inference → Implication; implementing a comprehensive development program is essential for reducing turnover and improving technician satisfaction.

### 2.C Option C — **AI-Driven Recruitment and Retention System**
1) **Thesis:** Leverage AI to optimize recruitment and retention strategies for specialized technicians.
2) **Scope & “Done Means”:** 
   - Inclusions: AI algorithms for candidate matching, predictive analytics for retention.
   - Success metrics: Reduce turnover to ≤10% by 2025-12-31.
3) **Value Mechanics (units/time):** 
   - ROI_12m = 10%; NPV @WACC: €150,000; Payback: 12 months.
4) **Assumptions / Constraints / Dependencies:** 
   - Assumption: AI will improve hiring accuracy and retention predictions.
   - Constraints: Budget limit of €150,000; dependency on IT for implementation.
5) **Capabilities & Resources:** 
   - Teams: IT (2 FTEs), HR (1 FTE).
   - Tools: AI software, data analytics platforms.
   - Budget: CapEx: €100,000 (software), OpEx: €50,000 (maintenance).

6) **Action Plan**
   - **WBS:**
     - W1: Develop AI algorithms (Owner: IT Lead)
     - W2: Integrate with HR systems (Owner: IT Lead)
     - W3: Train HR staff on new tools (Owner: HR Lead)
   - **Gantt-style schedule:** 
     - W1: 2025-01-01 to 2025-04-30
     - W2: 2025-05-01 to 2025-08-31
     - W3: 2025-09-01 to 2025-12-31
   - **Dependencies:** 
     - W1 depends on budget approval.
   - **RACI:**
     - Responsible: IT Lead
     - Accountable: HR Director
     - Consulted: HR Team
     - Informed: All technicians
   - **Change Management:** 
     - Stakeholder mapping and communication plan to inform technicians about new programs.
   - **Data & Instrumentation:** 
     - Track AI performance metrics and turnover rates.
   - **Quality Assurance:** 
     - Pre/post assessments for algorithm effectiveness.
   - **Rollout Strategy:** 
     - Pilot with a small group of technicians before full rollout.

7) **Budget Line-Items**
   | Line Item                 | Type     | Unit | Qty | Unit Cost [€] | Duration | Total [€] | Timing/Period |
   |---------------------------|----------|------|-----|----------------|----------|------------|---------------|
   | AI software               | CapEx    | 1    | 1   | 100,000        | 1 year   | 100,000    | 2025          |
   | Maintenance               | OpEx     | 1    | 1   | 50,000         | 1 year   | 50,000     | 2025          |
   **Totals:** CapEx: €100,000, OpEx: €50,000, Total: €150,000.

8) **KPIs & Monitoring**
   | KPI                     | Unit/Definition                     | Target       | Cadence | Data Owner | Source/System | Alert Threshold | Runbook/Owner |
   |-------------------------|-------------------------------------|--------------|---------|------------|---------------|-----------------|----------------|
   | Turnover Rate           | % of technicians leaving             | ≤10%         | Monthly | HR Lead    | HR Reports     | >10%            | HR Lead        |
   | AI Prediction Accuracy   | % of correct matches                 | ≥85%         | Quarterly| IT Lead    | AI System      | <85%            | IT Lead        |

9) **Risk Slice (top 5)**
   | ID | Risk                        | Prob (0–1/L–H) | Impact (€/unit/L–H) | Horizon | Early Signal            | Mitigation (HOW)               | Owner     | Trigger                |
   |----|-----------------------------|----------------:|---------------------|--------:|-------------------------|---------------------------------|-----------|-----------------------|
   | RISK-TECH-1 | Integration instability | 0.35 | −0.8 p.p. Reliability | 2025 | Error budget > threshold | Observability + retry + circuit-breaker | IT Lead | Integration failure |

10) **Behavioral Levers**
   | Lever              | Type                | Present? | Expected Effect             | Confidence (0–1) |
   |--------------------|---------------------|----------|-----------------------------|------------------|
   | Defaults           | Choice architecture | Yes      | Higher conversion            | 0.8              |
   | Salience           | Attention cue       | Yes      | Faster engagement            | 0.7              |
   | Social proof       | Peer benchmark      | Yes      | Increased acceptance         | 0.6              |
   | Commitment         | Self-signaling      | Yes      | Lower churn                  | 0.8              |
   | Friction reduction | UX/process          | Yes      | Higher completion            | 0.7              |
   | Timing/Anchoring   | Nudge/pricing       | Yes      | Improved uptake              | 0.6              |

11) **Governance & Approvals**  
   - Decision rights: IT Manager has authority over system decisions; HR Director oversees budgetary aspects.
   - Approvals: AI system integration requires approval from IT Director; budget changes require Finance Director sign-off.

12) **Provenance:** Context §1, Feasibility §1.

13) **WHY:** Evidence → Inference → Implication; leveraging AI technology is essential for optimizing recruitment and retention processes.

## 3) Comparative Economics (Normalized)
Base case; optionally add O/B/P bands or Monte Carlo (10k) if available — report mean, p5/p50/p95.

Normalization Bases: FX rate (source/date), CPI base year (source), PPP if used; scope reconciliation.

| Option | One-line Thesis | CapEx [€] | OpEx [€/period] | Net Benefit [€/period] | ROI_12m [%] | Payback [months] | NPV @WACC [€] | IRR [%] | CX/SLA Anchor (unit) | Assumption Notes | Provenance |
|-------|------------------|----------:|-----------------:|-----------------------:|------------:|-----------------:|--------------:|--------:|----------------------|------------------|-----------|
| A     | Improve technician retention through targeted development and engagement strategies. | 50,000 | 50,000 | 100,000 | 12% | 10 | 200,000 | 15% | Turnover Rate (%) | Assumes engagement leads to lower turnover. | Context §1 |
| B     | Implement a comprehensive development program to enhance skills and reduce turnover. | 70,000 | 50,000 | 120,000 | 15% | 8 | 300,000 | 20% | Engagement Score (%) | Assumes enhanced skills lead to higher job satisfaction. | Context §1 |
| C     | Leverage AI to optimize recruitment and retention strategies for specialized technicians. | 100,000 | 50,000 | 150,000 | 10% | 12 | 150,000 | 12% | AI Prediction Accuracy (%) | Assumes AI improves hiring accuracy. | Context §1 |

**WHY:** Each option presents a different approach to addressing the high turnover rate, with varying levels of investment and expected returns.

## 4) Criteria-Fit Matrix (Normalized 0–1, Weights Sum = 1.00)
Evaluated under Criteria v1.0 (Lock Hash: `criteria-v1.0:<hash>`). GDPR_Compliance = gating (Fail ⇒ No-Go).

| Criterion (unit)      | Weight | Option A | Option B | Option C | One-line WHY                     | Source |
|-----------------------|-------:|---------:|---------:|---------:|----------------------------------|--------|
| ROI_12m (%)           |  0.25  |    0.80  |    0.90  |    0.70  | Capital efficiency vs WACC       | Context §1 |
| Time_to_Impact (weeks)|  0.25  |    0.75  |    0.85  |    0.65  | Speed-to-value given window      | Context §1 |
| GDPR_Compliance (bin) |  0.25  |     1/0  |     1/0  |     1/0  | License to operate               | Context §1 |
| Adoption_90d (%)      |  0.25  |    0.70  |    0.80  |    0.60  | Behavioral uptake                | Context §1 |

Weighted Totals (0–1):  
- Option A: 0.77 • Option B: 0.83 • Option C: 0.66  
Ranking: B (highest) > A > C.

**Behavioral Lens Summary:** 
- Option B leverages commitment and social proof effectively, enhancing adoption rates.

## 5) Sensitivity Table (Quick, Decision-Useful)
| Driver Variable  | Δ        | Δ ROI_12m | Δ Adoption_90d | Confidence | Mechanism (WHY)                          |
|------------------|----------|-----------|------------------|-----------:|------------------------------------------|
| Recruitment cost | +10%     | −0.02     | +0.5 pp turnover | 0.7        | Cost pressure affects ROI and retention  |
| Time-to-market   | +2 weeks | −0.03     | −1.0 pp adoption | 0.6        | Missed novelty window reduces uptake     |
| Bonus spend      | +5%      | −0.01     | +0.2 pp retention| 0.8        | Incentive elasticity                     |

**WHY:** Understanding these sensitivities aids in risk management and strategy adjustments.

## 6) Recommendation Rule (Operationalized)
- Choose Option B if ROI_12m ≥ 15% and Payback ≤ 8 months and GDPR Pass; tie-break by Primary Focus.
- Choose Option A if ROI_12m ≥ 12% and Payback ≤ 10 months; otherwise apply tie-break rule driven by Primary Focus.
- Choose Option C if asymmetric upside or learning value dominates within the risk budget.
- Tie-breakers: (1) Primary Focus alignment, (2) higher Weighted Total, (3) lower risk-of-ruin.
- Early Triggers to Revisit: variance thresholds on cost/adoption/schedule/compliance; define owners and next-best action.

**WHY:** These thresholds derive from criteria weights/scoring rules and sensitivity analysis.

## 7) Consolidated Risk View (Cross-Option)
| ID | Risk | Option(s) | Prob (0–1/L–H) | Impact (€/unit/L–H) | Horizon | Early Signal | Mitigation (HOW) | Owner | Trigger |
|----|------|-----------|----------------:|---------------------|--------:|--------------|------------------|-------|---------|
| RISK-HR-1 | Inability to attract specialized technicians | A, B, C | 0.50 | 500,000 | 2025 | Low response to recruitment ads | Diversify recruitment channels | HR Lead | Recruitment failure |
| RISK-TECH-1 | Integration instability | A, B, C | 0.35 | −0.8 p.p. Reliability | 2025 | Error budget > threshold | Observability + retry + circuit-breaker | IT Lead | Integration failure |
| RISK-LGL-1 | GDPR/AI Act non-compliance | A, B, C | 0.20 | 300,000 | 2025 | Audit finding | DPIA + DPA + Explainability pack | DPO | Non-compliance |

**Interdependency Note:** e.g., Legal delay → Launch slip [days] → CAC ↑ [€/cust] → ROI ↓ [pp].  
**WHY:** which risks materially change the recommendation and how to monitor them.

## 8) Data Gaps & Collection Plan (MANDATORY for each TBD)
| Missing Data | Why Needed | Method (instrument/test/query) | Owner | ETA | Acceptance Criteria | Expected Source |
|--------------|------------|---------------------------------|-------|-----|---------------------|-----------------|
| Turnover replacement cost  | ROI calc           | HR DB extract / survey | HR Ops   | 2025-10-21| error ≤ ±5%        | Internal             |
| Benchmark retention uplift | Validation         | Industry report                 | Analyst  | 2025-11-01| n≥30 sample        | Analyst house        |

**Include experiment design where relevant (alpha, beta, power/MDE, guardrails).**  
**Mark every TBD as:** “TBD → collected by <owner> before <date>.”

## 9) Appendices (Reproducibility & Provenance)
- A. Formulas & Parameters: ROI, NPV, IRR, Payback; elasticity models; KPI definitions.  
- B. Normalization Bases: FX rate (source/date), CPI base year (source), PPP if used; scope reconciliation.  
- C. Source Register: title, publisher/author, date (YYYY-MM-DD), URL or Doc-ID/§, source type, recency notes.  
- D. Search/Index Notes (if used): vector namespaces, query operators, inclusion/exclusion criteria.  
- E. Assumption Log: each assumption + sensitivity tag + planned test (linked to §8).  
- F. Governance Artifacts: approval matrix templates; audit checklist; DPIA template (if relevant).

---

## Final Quality Gate (all must be YES)
- between_three_and_four_options == true  
- each_option_has_units_and_timeframes == true  
- option_includes_sequenced_action_plan_with_wbs_gantt_dependencies_and_critical_path == true  
- raci_defined_per_work_package == true  
- resources_and_fte_by_skill_and_seniority_declared == true  
- budget_line_items_capex_opex_with_unit_x_volume_x_duration_and_spend_calendar == true  
- behavioral_levers_subtable_present == true  
- assumptions_constraints_dependencies_explicit == true  
- phased_implementation_path_present == true  
- risk_register_with_probability_times_impact_and_triggers == true  
- kpis_with_targets_cadence_owner_alert_thresholds_and_runbook == true  
- governance_and_approvals_matrix_with_controls_and_audit == true  
- comparable_economics_normalized_with_formulas == true  
- criteria_fit_matrix_weights_sum_to_1_00 == true  
- recommendation_rule_references_primary_focus == true  
- sensitivity_table_present == true  
- option_c_or_4_contrarian_with_premortem_and_counterfactual == true  
- data_gaps_with_collection_plan_present == true  
- provenance_cues_present_for_material_claims == true  
- if_training_then_curriculum_hours_modality_schedule_cohorts_coverage_budget_kpis_dependencies_comms == true  
- if_compensation_then_amount_timing_eligibility_governance_payroll_impact_comms_budget_monitoring == true  
```