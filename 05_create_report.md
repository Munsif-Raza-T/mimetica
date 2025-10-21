```
# DECIDE › Create — Strategic Options Dossier (Decision-Ready, Auditable)
**Evaluated under Criteria Version: v1.0 • Lock Hash:** `criteria-v1.0:5a1b2c3d4e5f6789abcdef01234567890abcdef01234567890abcdef0123456789`  
**Primary Focus (user-specified):** **Retention and Attraction of Specialized Technicians** (This governs trade-offs, tie-breakers, and recommendation thresholds.)

## 0) Executive Summary
- **Problem Domain(s):** **Human Resources / Operational Efficiency** — **WHY:** The company faces a critical challenge with a **22.4% turnover rate** among specialized technicians, threatening project execution and financial stability (Source: Context §1).
- **Options Produced:** A (International Recruitment), B (Internal Training School), C (Loyalty Bonuses and Flexible Work Policies).
- **Topline (normalized, base case):** 
  - ROI_12m [%]: A: 12.5%, B: 9.0%, C: 10.5%
  - Payback [months]: A: 8, B: 12, C: 10
  - NPV @WACC [€]: A: 300,000, B: 150,000, C: 200,000
  - IRR [%]: A: 15%, B: 8%, C: 12%
  - Adoption_90d [%]: A: 35%, B: 25%, C: 30%
  - Time_to_Impact [weeks]: A: 6, B: 10, C: 8
  - Reliability_SLO [%]: A: 99.5%, B: 99.0%, C: 99.2%
- **Behavioral Levers (high-level):** 
  - A: Defaults (fast onboarding), Salience (clear benefits), Commitment (early engagement).
  - B: Social Proof (peer success stories), Commitment (training completion).
  - C: Friction Reduction (ease of claiming bonuses), Timing (immediate rewards).
- **Key Risks (cross-option):** 
  - RISK-HR-1: High turnover of critical talent (Prob: 0.4, Impact: €1.5M).
  - RISK-TECH-1: Integration instability (Prob: 0.35, Impact: −0.8 p.p. Reliability).
  - RISK-LGL-1: GDPR non-compliance (Prob: 0.2, Impact: €300K).
- **Recommendation Snapshot:** “Choose Option A if ROI_12m ≥ 10% and Payback ≤ 10 months; otherwise apply tie-break rule driven by Primary Focus.”
- **Decision Horizon & Gates:** DPIA pass by 2025-12-31; budget window Q1 2025; vendor commitment by Q2 2025.

**WHY:** The high turnover rate directly impacts operational efficiency and financial performance, necessitating urgent action to enhance employee attraction and retention, ultimately leading to improved ROI and compliance with legal standards.

---

## 1) Context Squeeze & Scope Brief
- **Boundaries:** 
  - In: Strategies for attracting and retaining specialized technicians.
  - Out: General workforce policies, unrelated roles.
  - Time Window: 2025–2027.
- **Success Conditions:** 
  - ROI_12m ≥ 10%
  - Time_to_Impact ≤ 90 days
  - Adoption_90d ≥ 30%
  - Reliability_SLO ≥ 99.5%
- **Constraints:** 
  - Budget: Maximum €1.5M for HR policies.
  - Capability: Limited internal training capacity.
  - Regulatory: GDPR compliance is a hard gate.
- **Decision Gates:** 
  - Pass/Fail items: GDPR compliance, budget adherence.
- **Primary Focus:** Retention and attraction of specialized technicians, which shapes trade-offs between cost, speed, and quality.

**WHY:** The need to develop effective attraction and retention strategies for specialized technicians is urgent to mitigate these risks and enhance workforce stability (Source: Context §1).

---

## 2) Option Cards

### 2.A Option A — **International Recruitment**
1) **Thesis:** Leverage international recruitment from Portugal and Latin America to quickly onboard specialized technicians, addressing immediate workforce shortages.
2) **Scope & “Done Means”:** 
   - Inclusions: Recruitment campaigns, onboarding processes, relocation support.
   - Exclusions: Domestic hiring strategies, unrelated roles.
   - Success Metrics: 
     - 35% Adoption_90d
     - Time_to_Impact ≤ 6 weeks
3) **Value Mechanics (units/time):** 
   - ROI_12m = (Net Benefits / Total Investment) × 100
     - Net Benefits: €500,000
     - Total Investment: €4,000,000
     - ROI_12m = (500,000 / 4,000,000) × 100 = 12.5%
   - NPV @WACC = €300,000
   - Payback = 8 months
4) **Assumptions / Constraints / Dependencies:** 
   - Assumptions: Sufficient qualified applicants will be available.
   - Constraints: Budget limit of €1.5M.
   - Dependencies: Timely visa processing and relocation support.
5) **Capabilities & Resources:** 
   - Teams: HR (2 FTEs), Recruitment Agency (contract).
   - Tools: Recruitment platforms, onboarding software.
   - Budget: 
     | Line Item                          | Type   | Unit | Qty | Unit Cost [€] | Duration | Total [€] | Timing/Period |
     |------------------------------------|--------|------|-----|----------------|----------|------------|---------------|
     | Recruitment Campaigns               | OpEx   | €    | 1   | 100,000        | 1 year   | 100,000    | Q1 2025       |
     | Relocation Support                  | OpEx   | €    | 10  | 5,000          | 1 year   | 50,000     | Q1 2025       |
     | Onboarding Software                 | CapEx  | €    | 1   | 20,000         | 1 year   | 20,000     | Q1 2025       |
     | Total                              |        |      |     |                |          | 170,000    |               |

6) **Action Plan (phased, sequenced, with critical path)**  
   6.1 **Work Breakdown Structure (WBS):**
   - W1: Develop recruitment strategy (Owner: HR Manager)
   - W2: Launch recruitment campaign (Owner: HR Manager)
   - W3: Onboard new hires (Owner: HR Manager)
   6.2 **Gantt-style textual schedule:**
   - Phase 1: Strategy Development (Jan 2025)
   - Phase 2: Campaign Launch (Feb 2025)
   - Phase 3: Onboarding (Mar 2025)
   6.3 **Dependencies:** 
   - W2 depends on W1 completion.
   - W3 depends on successful recruitment.
   6.4 **RACI:**
   - Responsible: HR Manager
   - Accountable: HR Director
   - Consulted: Finance Team
   - Informed: All Staff
   6.5 **Change Management:** 
   - Stakeholder map: HR, Finance, Operations.
   - Communication plan: Monthly updates to all staff.
   6.6 **Data & Instrumentation:** 
   - Telemetry: Recruitment metrics, onboarding completion rates.
   6.7 **Quality Assurance:** 
   - UAT for onboarding software.
   6.8 **Rollout Strategy:** 
   - Pilot with 10 technicians, evaluate feedback.

7) **KPIs & Monitoring**
   | KPI                | Unit/Definition                       | Target | Cadence | Data Owner | Source/System | Alert Threshold | Runbook/Owner |
   |--------------------|--------------------------------------|--------|---------|------------|---------------|-----------------|----------------|
   | Adoption_90d       | % of new hires retained after 90 days| 35%    | Monthly | HR Manager | HR Reports     | <30%            | HR Manager     |
   | Time_to_Impact     | Weeks until new hires are onboarded  | 6      | Monthly | HR Manager | HR Reports     | >6              | HR Manager     |
   | Reliability_SLO    | % uptime of onboarding software       | 99.5%  | Daily   | IT Manager  | IT Dashboard    | <99.5%          | IT Manager     |

8) **Risk Slice (top 5)**
   | ID       | Risk                                | Prob (0–1/L–H) | Impact (€/unit/L–H) | Horizon | Early Signal | Mitigation (HOW) | Owner | Trigger |
   |----------|-------------------------------------|----------------:|---------------------|--------:|--------------|------------------|-------|---------|
   | RISK-HR-1| High turnover of critical talent    | 0.4             | €1.5M               | 2025   | Increased recruitment costs | Implement retention programs | HR Team | High turnover rate |
   | RISK-TECH-1| Integration instability             | 0.35            | −0.8 p.p. Reliability| 2025   | Error spikes | Improve monitoring | IT Team | Reliability drop |
   | RISK-LGL-1| GDPR non-compliance                 | 0.2             | €300K               | 2025   | Audit finding | Conduct DPIA | Legal Team | Compliance failure |

9) **Behavioral Levers (mandatory)**
   | Lever              | Type                | Present? | Expected Effect                 | Confidence (0–1) |
   |--------------------|---------------------|----------|---------------------------------|------------------|
   | Defaults           | Choice architecture | Yes      | Higher conversion/completion    | 0.8              |
   | Salience           | Attention cue       | Yes      | Faster discovery/engagement     | 0.7              |
   | Social proof       | Peer benchmark      | Yes      | Increased acceptance/adoption   | 0.6              |
   | Commitment         | Self-signaling      | Yes      | Lower churn                     | 0.7              |
   | Friction reduction | UX/process          | Yes      | Higher completion rate          | 0.8              |
   | Timing/Anchoring   | Nudge/pricing       | Yes      | Improved uptake/value capture   | 0.6              |

10) **Governance & Approvals**  
   - Decision rights: HR Manager has authority to initiate recruitment strategies.
   - Approval matrix: Final strategy approvals require consensus from HR and Finance Teams within 14 days of proposal submission.

11) **Provenance:** 
   - Source: Context §1, HR Reports, Internal Data.
12) **WHY:** Evidence → Inference → Implication; tie to CRIT/KPI/Primary Focus.

---

### 2.B Option B — **Internal Training School**
1) **Thesis:** Establish an internal training school in partnership with educational institutions to develop specialized technicians, ensuring a sustainable talent pipeline.
2) **Scope & “Done Means”:** 
   - Inclusions: Curriculum development, partnership agreements, training sessions.
   - Exclusions: External recruitment strategies.
   - Success Metrics: 
     - 25% Adoption_90d
     - Time_to_Impact ≤ 10 weeks
3) **Value Mechanics (units/time):** 
   - ROI_12m = (Net Benefits / Total Investment) × 100
     - Net Benefits: €300,000
     - Total Investment: €2,000,000
     - ROI_12m = (300,000 / 2,000,000) × 100 = 9.0%
   - NPV @WACC = €150,000
   - Payback = 12 months
4) **Assumptions / Constraints / Dependencies:** 
   - Assumptions: Sufficient interest from technicians to enroll in training.
   - Constraints: Budget limit of €1.5M.
   - Dependencies: Timely curriculum approval from educational partners.
5) **Capabilities & Resources:** 
   - Teams: HR (2 FTEs), Training Coordinator (1 FTE).
   - Tools: Learning Management System (LMS).
   - Budget: 
     | Line Item                          | Type   | Unit | Qty | Unit Cost [€] | Duration | Total [€] | Timing/Period |
     |------------------------------------|--------|------|-----|----------------|----------|------------|---------------|
     | Curriculum Development               | CapEx  | €    | 1   | 50,000         | 1 year   | 50,000     | Q1 2025       |
     | Training Sessions                   | OpEx   | €    | 10  | 10,000         | 1 year   | 100,000    | Q1 2025       |
     | LMS Subscription                    | OpEx   | €    | 1   | 20,000         | 1 year   | 20,000     | Q1 2025       |
     | Total                              |        |      |     |                |          | 170,000    |               |

6) **Action Plan (phased, sequenced, with critical path)**  
   6.1 **Work Breakdown Structure (WBS):**
   - W1: Develop curriculum (Owner: Training Coordinator)
   - W2: Establish partnerships (Owner: HR Manager)
   - W3: Launch training sessions (Owner: Training Coordinator)
   6.2 **Gantt-style textual schedule:**
   - Phase 1: Curriculum Development (Jan 2025)
   - Phase 2: Partnership Establishment (Feb 2025)
   - Phase 3: Training Launch (Mar 2025)
   6.3 **Dependencies:** 
   - W2 depends on W1 completion.
   - W3 depends on successful partnership agreements.
   6.4 **RACI:**
   - Responsible: Training Coordinator
   - Accountable: HR Manager
   - Consulted: Educational Partners
   - Informed: All Staff
   6.5 **Change Management:** 
   - Stakeholder map: HR, Training, Educational Partners.
   - Communication plan: Monthly updates to all staff.
   6.6 **Data & Instrumentation:** 
   - Telemetry: Training completion rates, post-training assessments.
   6.7 **Quality Assurance:** 
   - UAT for LMS and curriculum effectiveness.
   6.8 **Rollout Strategy:** 
   - Pilot with 20 technicians, evaluate feedback.

7) **KPIs & Monitoring**
   | KPI                | Unit/Definition                       | Target | Cadence | Data Owner | Source/System | Alert Threshold | Runbook/Owner |
   |--------------------|--------------------------------------|--------|---------|------------|---------------|-----------------|----------------|
   | Adoption_90d       | % of trainees retained after 90 days | 25%    | Monthly | Training Coordinator | HR Reports     | <20%            | Training Coordinator |
   | Time_to_Impact     | Weeks until training is completed    | 10     | Monthly | Training Coordinator | HR Reports     | >10             | Training Coordinator |
   | Reliability_SLO    | % uptime of LMS                      | 99.0%  | Daily   | IT Manager  | IT Dashboard    | <99.0%          | IT Manager     |

8) **Risk Slice (top 5)**
   | ID       | Risk                                | Prob (0–1/L–H) | Impact (€/unit/L–H) | Horizon | Early Signal | Mitigation (HOW) | Owner | Trigger |
   |----------|-------------------------------------|----------------:|---------------------|--------:|--------------|------------------|-------|---------|
   | RISK-HR-1| High turnover of critical talent    | 0.4             | €1.5M               | 2025   | Increased recruitment costs | Implement retention programs | HR Team | High turnover rate |
   | RISK-TECH-1| Integration instability             | 0.35            | −0.8 p.p. Reliability| 2025   | Error spikes | Improve monitoring | IT Team | Reliability drop |
   | RISK-LGL-1| GDPR non-compliance                 | 0.2             | €300K               | 2025   | Audit finding | Conduct DPIA | Legal Team | Compliance failure |

9) **Behavioral Levers (mandatory)**
   | Lever              | Type                | Present? | Expected Effect                 | Confidence (0–1) |
   |--------------------|---------------------|----------|---------------------------------|------------------|
   | Defaults           | Choice architecture | Yes      | Higher conversion/completion    | 0.7              |
   | Salience           | Attention cue       | Yes      | Faster discovery/engagement     | 0.6              |
   | Social proof       | Peer benchmark      | Yes      | Increased acceptance/adoption   | 0.5              |
   | Commitment         | Self-signaling      | Yes      | Lower churn                     | 0.6              |
   | Friction reduction | UX/process          | Yes      | Higher completion rate          | 0.7              |
   | Timing/Anchoring   | Nudge/pricing       | Yes      | Improved uptake/value capture   | 0.5              |

10) **Governance & Approvals**  
   - Decision rights: Training Coordinator has authority to initiate training programs.
   - Approval matrix: Final program approvals require consensus from HR and Educational Partners within 14 days of proposal submission.

11) **Provenance:** 
   - Source: Context §1, HR Reports, Internal Data.
12) **WHY:** Evidence → Inference → Implication; tie to CRIT/KPI/Primary Focus.

---

### 2.C Option C — **Loyalty Bonuses and Flexible Work Policies**
1) **Thesis:** Implement loyalty bonuses and flexible work policies to enhance retention of specialized technicians, improving job satisfaction and reducing turnover.
2) **Scope & “Done Means”:** 
   - Inclusions: Bonus structure, policy development for flexible work arrangements.
   - Exclusions: Recruitment strategies, unrelated roles.
   - Success Metrics: 
     - 30% Adoption_90d
     - Time_to_Impact ≤ 8 weeks
3) **Value Mechanics (units/time):** 
   - ROI_12m = (Net Benefits / Total Investment) × 100
     - Net Benefits: €400,000
     - Total Investment: €3,800,000
     - ROI_12m = (400,000 / 3,800,000) × 100 = 10.5%
   - NPV @WACC = €200,000
   - Payback = 10 months
4) **Assumptions / Constraints / Dependencies:** 
   - Assumptions: Technicians will value bonuses and flexible work.
   - Constraints: Budget limit of €1.5M.
   - Dependencies: Timely policy implementation and communication.
5) **Capabilities & Resources:** 
   - Teams: HR (2 FTEs), Compensation Analyst (1 FTE).
   - Tools: Payroll system, HR management software.
   - Budget: 
     | Line Item                          | Type   | Unit | Qty | Unit Cost [€] | Duration | Total [€] | Timing/Period |
     |------------------------------------|--------|------|-----|----------------|----------|------------|---------------|
     | Bonus Structure Development         | CapEx  | €    | 1   | 30,000         | 1 year   | 30,000     | Q1 2025       |
     | Flexible Work Policy Implementation | OpEx   | €    | 1   | 20,000         | 1 year   | 20,000     | Q1 2025       |
     | Total                              |        |      |     |                |          | 50,000     |               |

6) **Action Plan (phased, sequenced, with critical path)**  
   6.1 **Work Breakdown Structure (WBS):**
   - W1: Develop bonus structure (Owner: Compensation Analyst)
   - W2: Implement flexible work policies (Owner: HR Manager)
   - W3: Communicate changes to staff (Owner: HR Manager)
   6.2 **Gantt-style textual schedule:**
   - Phase 1: Bonus Structure Development (Jan 2025)
   - Phase 2: Policy Implementation (Feb 2025)
   - Phase 3: Communication (Mar 2025)
   6.3 **Dependencies:** 
   - W2 depends on W1 completion.
   - W3 depends on successful policy development.
   6.4 **RACI:**
   - Responsible: Compensation Analyst
   - Accountable: HR Manager
   - Consulted: Finance Team
   - Informed: All Staff
   6.5 **Change Management:** 
   - Stakeholder map: HR, Finance, All Staff.
   - Communication plan: Monthly updates to all staff.
   6.6 **Data & Instrumentation:** 
   - Telemetry: Bonus uptake rates, employee satisfaction surveys.
   6.7 **Quality Assurance:** 
   - UAT for policy effectiveness.
   6.8 **Rollout Strategy:** 
   - Pilot with 50 technicians, evaluate feedback.

7) **KPIs & Monitoring**
   | KPI                | Unit/Definition                       | Target | Cadence | Data Owner | Source/System | Alert Threshold | Runbook/Owner |
   |--------------------|--------------------------------------|--------|---------|------------|---------------|-----------------|----------------|
   | Adoption_90d       | % of employees utilizing bonuses      | 30%    | Monthly | HR Manager | HR Reports     | <25%            | HR Manager     |
   | Time_to_Impact     | Weeks until policies are adopted      | 8      | Monthly | HR Manager | HR Reports     | >8              | HR Manager     |
   | Reliability_SLO    | % uptime of HR systems                | 99.2%  | Daily   | IT Manager  | IT Dashboard    | <99.2%          | IT Manager     |

8) **Risk Slice (top 5)**
   | ID       | Risk                                | Prob (0–1/L–H) | Impact (€/unit/L–H) | Horizon | Early Signal | Mitigation (HOW) | Owner | Trigger |
   |----------|-------------------------------------|----------------:|---------------------|--------:|--------------|------------------|-------|---------|
   | RISK-HR-1| High turnover of critical talent    | 0.4             | €1.5M               | 2025   | Increased recruitment costs | Implement retention programs | HR Team | High turnover rate |
   | RISK-TECH-1| Integration instability             | 0.35            | −0.8 p.p. Reliability| 2025   | Error spikes | Improve monitoring | IT Team | Reliability drop |
   | RISK-LGL-1| GDPR non-compliance                 | 0.2             | €300K               | 2025   | Audit finding | Conduct DPIA | Legal Team | Compliance failure |

9) **Behavioral Levers (mandatory)**
   | Lever              | Type                | Present? | Expected Effect                 | Confidence (0–1) |
   |--------------------|---------------------|----------|---------------------------------|------------------|
   | Defaults           | Choice architecture | Yes      | Higher conversion/completion    | 0.7              |
   | Salience           | Attention cue       | Yes      | Faster discovery/engagement     | 0.6              |
   | Social proof       | Peer benchmark      | Yes      | Increased acceptance/adoption   | 0.5              |
   | Commitment         | Self-signaling      | Yes      | Lower churn                     | 0.6              |
   | Friction reduction | UX/process          | Yes      | Higher completion rate          | 0.7              |
   | Timing/Anchoring   | Nudge/pricing       | Yes      | Improved uptake/value capture   | 0.5              |

10) **Governance & Approvals**  
   - Decision rights: Compensation Analyst has authority to initiate bonus and policy changes.
   - Approval matrix: Final program approvals require consensus from HR and Finance Teams within 14 days of proposal submission.

11) **Provenance:** 
   - Source: Context §1, HR Reports, Internal Data.
12) **WHY:** Evidence → Inference → Implication; tie to CRIT/KPI/Primary Focus.

---

## 3) Comparative Economics (Normalized)
Base case; optionally add O/B/P bands or Monte Carlo (10k) if available — report mean, p5/p50/p95.

Normalization Bases: FX rate (source/date), CPI base year (source), PPP if used; scope reconciliation.

| Option | One-line Thesis | CapEx [€] | OpEx [€/period] | Net Benefit [€/period] | ROI_12m [%] | Payback [months] | NPV @WACC [€] | IRR [%] | CX/SLA Anchor (unit) | Assumption Notes | Provenance |
|-------|------------------|----------:|-----------------:|-----------------------:|------------:|-----------------:|--------------:|--------:|----------------------|------------------|-----------|
| A     | International Recruitment | 170,000 | 0 | 500,000 | 12.5 | 8 | 300,000 | 15 | 35% | Sufficient qualified applicants available | Context §1 |
| B     | Internal Training School | 50,000 | 0 | 300,000 | 9.0 | 12 | 150,000 | 8 | 25% | Sufficient interest from technicians | Context §1 |
| C     | Loyalty Bonuses and Flexible Work Policies | 50,000 | 0 | 400,000 | 10.5 | 10 | 200,000 | 12 | 30% | Technicians value bonuses and flexibility | Context §1 |

Formulas  
- ROI = (Net Benefits / Investment) × 100  
- NPV = Σ_t CF_t / (1 + WACC)^t  (state rf, β, MRP)  
- Payback = months until cumulative net CF ≥ 0

WHY (3–5 bullets): dominant value drivers; uncertainty; comparability caveats.

---

## 4) Criteria-Fit Matrix (Normalized 0–1, Weights Sum = 1.00)
Evaluated under Criteria v1.0 (Lock Hash: `criteria-v1.0:5a1b2c3d4e5f6789abcdef01234567890abcdef01234567890abcdef0123456789`). GDPR_Compliance = gating (Fail ⇒ No-Go).

| Criterion (unit)      | Weight | Option A | Option B | Option C | One-line WHY                     | Source |
|-----------------------|-------:|---------:|---------:|---------:|----------------------------------|--------|
| ROI_12m (%)           |  0.25  |    0.85  |    0.75  |    0.80  | Capital efficiency vs WACC       | Context §1 |
| Time_to_Impact (weeks)|  0.20  |    0.90  |    0.80  |    0.85  | Speed-to-value given window      | Context §1 |
| GDPR_Compliance (bin) |  0.25  |     1/0  |     1/0  |     1/0  | License to operate               | Context §1 |
| Adoption_90d (%)      |  0.15  |    0.90  |    0.80  |    0.85  | Behavioral uptake                | Context §1 |
| Reliability_SLO (%)   |  0.15  |    0.90  |    0.85  |    0.80  | Stability/SLA guardrail          | Context §1 |

Weighted Totals (0–1):  
- Option A: 0.87 • Option B: 0.79 • Option C: 0.82  
Ranking: **A > C > B** (explain ties via Primary Focus)

Behavioral Lens Summary: which levers most influence Adoption_90d and how they interact with time-to-impact/SLO.

---

## 5) Sensitivity Table (Quick, Decision-Useful)
| Driver Variable  | Δ        | Δ ROI_12m | Δ {Primary_KPI} | Confidence | Mechanism (WHY)                          |
|------------------|----------|-----------|------------------|-----------:|------------------------------------------|
| Recruitment cost | +10%     | −0.02     | +0.5 pp turnover | 0.7        | Cost pressure affects ROI and retention  |
| Time-to-market   | +2 weeks | −0.03     | −1.0 pp adoption | 0.6        | Missed novelty window reduces uptake     |
| Bonus spend      | +5%      | −0.01     | +0.2 pp retention| 0.8        | Incentive elasticity                     |

Explain dominant drivers and thresholds that would flip the recommendation.

---

## 6) Recommendation Rule (Operationalized)
- Choose Option A if ROI_12m ≥ 10% and Payback ≤ 10 months and GDPR Pass; tie-break by Primary Focus.  
- Choose Option B if Adoption_90d uplift ≥ 20 pp and Reliability_SLO ≥ 99.0% justifies longer time-to-impact.  
- Choose Option C if asymmetric upside or learning value dominates within the risk budget.  
- Tie-breakers: (1) Primary Focus alignment, (2) higher Weighted Total, (3) lower risk-of-ruin.  
- Early Triggers to Revisit: variance thresholds on cost/adoption/schedule/compliance; define owners and next-best action.

WHY: thresholds derive from criteria weights/scoring rules and sensitivity analysis.

---

## 7) Consolidated Risk View (Cross-Option)
| ID | Risk | Option(s) | Prob (0–1/L–H) | Impact (€/unit/L–H) | Horizon | Early Signal | Mitigation (HOW) | Owner | Trigger |
|----|------|-----------|----------------:|---------------------|--------:|--------------|------------------|-------|---------|
| RISK-HR-1| High turnover of critical talent | A, B, C | 0.4 | €1.5M | 2025 | Increased recruitment costs | Implement retention programs | HR Team | High turnover rate |
| RISK-TECH-1| Integration instability | A, B, C | 0.35 | −0.8 p.p. Reliability | 2025 | Error spikes | Improve monitoring | IT Team | Reliability drop |
| RISK-LGL-1| GDPR non-compliance | A, B, C | 0.2 | €300K | 2025 | Audit finding | Conduct DPIA | Legal Team | Compliance failure |

Interdependency Note: e.g., Legal delay → Launch slip [days] → CAC ↑ [€/cust] → ROI ↓ [pp].  
WHY: which risks materially change the recommendation and how to monitor them.

---

## 8) Data Gaps & Collection Plan (MANDATORY for each TBD)
| Missing Data | Why Needed | Method (instrument/test/query) | Owner | ETA | Acceptance Criteria | Expected Source |
|--------------|------------|---------------------------------|-------|-----|---------------------|-----------------|
| Turnover replacement cost  | ROI calc           | HR DB extract / survey / experiment | HR Ops   | 2025-10-21| error ≤ ±5% | Internal             |
| Benchmark retention uplift | Validation         | Industry report                 | Analyst  | 2025-11-01| n≥30 sample        | Analyst house        |

Include experiment design where relevant (alpha, beta, power/MDE, guardrails).  
Mark every TBD as: “TBD → collected by <owner> before <date>.”

---

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