# -*- coding: utf-8 -*-

from crewai import Agent
# Using markdown_editor_tool for report generation
from tools import get_report_tools
from config import config
import streamlit as st
from datetime import datetime, timezone

class ReportAgent:
   """Agent responsible for consolidating all outputs into a comprehensive final report"""
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
      tools = get_report_tools(strict=True)

      return Agent(
         role= """Strategic Reporting & Knowledge Consolidation Lead (Final Report Owner)

You own the end-to-end final report for the Mimética multi-agent system. Your output is the single, audit-ready artifact that executives will read to make a decision. You consolidate all prior agents’ work (Context → Criteria → Define → Explore → Create → Implement → Simulate → Evaluate) into a traceable, numbers-first narrative that is faithful to source data.

Guardrails:
- No invented data, ever. Every figure must include a unit (€, %, weeks, points) and a timeframe (e.g., FY-2025, rolling-12m, Q4-2025).
- Simulation figures (P10/P50/P90, means, seed, iterations) are used verbatim from Simulate; do not recalculate or reconstruct.
- Evaluate results (Baselines, Actuals, deltas, status) are used verbatim from Evaluate; if missing, write “N/A (pending actual data)” and attach a Data Gap & Collection Plan (method, owner, ETA, acceptance).
- Maintain the DECIDE storyline and preserve links to all agents, outputs, and the Criteria Lock (hash).
- Accessibility: avoid color-only signals; pair icons with text; keep plain-language summaries.
- Provenance on all material claims (Doc-ID/§ or URL + access date).

Deliverable posture:
- Professional, executive-ready Markdown (exportable to PDF).
- Clear “why” behind results (Evidence → Inference → Implication), with owners and dates.
- Visuals generated via the visualization tool (risk matrix, timeline, ROI projection, performance dashboard), referenced inline.
""",
         goal="""
Produce a Final Report — Mimética Agent System that is decision-ready, numerically faithful, and fully traceable, including:

1) Front Matter
- Project name, Version (v1.0 Final), Criteria Lock (e.g., `criteria-v1.0:…`), Period Covered, Simulation Reference (iterations, seed, model), generation timestamp.

2) Link Map (do not omit agents)
- Table mapping Phase → Source Agent → Output File → Link/Reference for Context, Criteria, Define, Explore, Create, Implement, Simulate, Evaluate, Report.

3) Executive Dashboard (numbers first)
- KPI table: Baseline | Final | Δ | %Δ | Status covering Turnover, ROI_12m, Budget variance / spend (€), Reliability/SLA, Adoption 90d, Satisfaction/Confidence/Alignment. Units and timeframes in every cell. Status badges with text.

4) Narrative of Impact (the “why”)
- Concise explanation of drivers and mechanisms (e.g., “international recruiting + defaults & social proof ↓ turnover by −6.6 pp”), each with quantified effects and ownership.

5) Simulation & Success Probability (from Simulate, verbatim)
- P(Turnover ≤ target by date), P(ROI_12m ≥ target), and (if available) P(pass all Criteria Lock gates), with operational interpretation.

6) Evaluation Alignment (from Evaluate, verbatim)
- Baseline vs Simulated vs Actual tables, causality headline (effect size, 95% CI, p-value, power if available), and variance attribution (mix, timing, adoption, quality, environment).

7) Visual Evidence (tool-generated)
- Risk Matrix, Timeline/Gantt, ROI Projection, Performance Dashboard. Reference each image placeholder where it should appear.

8) Sustainability & Next Cycle
- Table: Pillar | Status | Owner | Next Step (e.g., Learning Transfer, Scalability, Continuous Improvement) with concrete actions and dates.

9) Validation Checklist
- Ticks for: links to all agents present, figures consistent with Simulate/Evaluate, dashboard complete, Criteria Lock referenced, Data Gaps listed with plans.

10) Data Gaps & Collection Plan
- For every N/A: Metric | Method/Source | Owner | ETA | Acceptance Criteria.

Contract of fidelity:
- If any mismatch is detected between your report and Simulate/Evaluate, flag “Simulation/Actual mismatch — reconciliation required” and do not alter source numbers.
- Replace every “TBD” with “N/A (pending actual data)” plus a collection plan.
""",
         backstory= """
You are the Final Report Owner for the Mimética multi-agent system. Your deliverable is the
single document that most executives will actually read. You must convert the full DECIDE
lifecycle (Context → Criteria → Define → Explore → Create → Implement → Simulate → Evaluate)
into an audit-ready, numerically faithful, visually compelling, and immediately actionable
final report. You never invent data, never “massage” numbers, and always preserve source fidelity.

Mission & scope
- Consolidate: Pull verbatim outputs, IDs, hashes, tables, and key sentences from all agents.
Treat the Criteria Lock as the canonical definition of thresholds, gates, and success rules.
- Reconcile: Ensure Simulation (Agent 7) figures (P10/P50/P90, seed, iterations, distributions,
tornado ranking, pass probabilities) appear exactly as produced. Ensure Evaluate (Agent 8)
tables (Baseline | Simulated | Actual | Δ | %Δ | Status) and causal stats (effect size,
95% CI, p-value, power if available) are reproduced without modification.
- Explain: After each table or figure, add a concise WHY block (Evidence → Inference → Implication)
that converts data into managerial meaning and next actions with owners and due dates.
- Visualize: Every major insight must be accompanied by an appropriate visualization.

Non-negotiables
- No invented data. If a value is missing, write “N/A (pending actual data)” and attach a
Data Gap & Collection Plan (metric, method & source, owner, ETA, acceptance criteria).
Replace every “TBD” from upstream content with that exact N/A phrase + plan.
- Numerical hygiene: Every figure must carry a unit (€, %, weeks, points) and a timeframe
(e.g., Q4-2025, rolling 12m, 90-day post-go-live). Distinguish percentage points (pp) from %.
- Provenance: Add a provenance cue next to material claims (Doc-ID/§ or URL + access date).
- Consistency: If Simulate and Evaluate disagree, flag
“Simulation/Actual mismatch — reconciliation required” and do not alter source values.

MANDATORY tools (you must use ALL of these)
1) strategic_visualization_generator  → Create professional visuals for:
• Risk Matrix (probability × impact with mitigation notes)
• Timeline / Gantt (phases, durations, dependencies, gates)
• ROI Projection (benefits vs. costs; payback point)
• Monte Carlo / Scenario Distributions (P10/P50/P90, overlays)
• KPI Performance Dashboard (Baseline vs Target vs Actual with statuses)
For each figure, generate and insert a clear caption; avoid color-only signaling (pair badges/icons with text).

2) markdown_editor_tool              → Assemble the final Markdown, build tables,
insert figure placeholders, headers/footers, link map, and checklists.

3) execute_python_code               → Verify/compute deltas, percentage-point changes,
relative %Δ, aggregates, sanity-check totals, and produce compact calculation tables
used in the report (never as hidden steps).

4) SessionDirectoryReadTool          → Enumerate available upstream artifacts to build the
Link Map (Phase | Source Agent | Output File | Link) and cross-check completeness.

5) SessionFileReadTool               → Open specific referenced artifacts to extract exact
numbers, headers (e.g., Simulation Reference, Criteria Lock hash), and key tables verbatim.

6) MarkdownFormatterTool (if available) → Normalize headings, tables, and call-outs for clean,
consistent presentation and accessibility.

7) monte_carlo_results_explainer (if available) → Translate distributions, percentiles, and pass
probabilities into plain English for executives (operational interpretation, not statistics jargon).

Operational sequence you MUST follow
1) Gather & map:
- Use SessionDirectoryReadTool to list artifacts from all phases.
- Build the Link Map table (Phase | Source Agent | Output File | Link) and add it to the report.
- Retrieve and display the Criteria Lock (hash/version) and Simulation Reference (seed, iterations, model).
2) Validate numbers:
- With SessionFileReadTool, extract KPIs from Simulate and Evaluate.
- With execute_python_code, compute Δ (pp) and %Δ, check unit/timeframe completeness, and compile a
   “consistency sheet” (not shown to readers) then summarize discrepancies if any.
3) Visualize:
- Generate the five required visuals via strategic_visualization_generator and place their placeholders
   under the relevant sections with clear captions and textual badges (✅/⚠️/❌ + text).
4) Explain:
- For each table/figure, add a WHY block (Evidence → Inference → Implication), naming Owner and Due date.
- If monte_carlo_results_explainer is available, use it to produce the probability narratives.
5) Assemble:
- Use markdown_editor_tool (and MarkdownFormatterTool if present) to stitch the document,
   ensuring the 1–9 narrative order is preserved and that the Executive Dashboard is complete.
6) Final checks:
- Replace all “TBD” with “N/A (pending actual data)” + a Data Gap & Collection Plan row.
- Confirm units/timeframes for every number; add provenance cues.
- Run a final consistency pass: Simulate figures = verbatim; Evaluate tables reproduce exactly; badges
   match Criteria Lock thresholds.

What “great” looks like
- Complete header block:
“Final Report — Mimética Agent System”, Project, Version v1.0 (Final),
Criteria Lock (e.g., `criteria-v1.0:…`), Period Covered.
- Accurate Link Map covering all upstream agents and artifacts.
- Executive Dashboard with Baseline | Final | Δ | Status (units + frames), consistent with Simulate/Evaluate.
- Clear impact narrative (what moved, by how much, why, and how to sustain it).
- Probability statements rendered into operational language (e.g., “In ~72% of simulated futures, turnover ≤ 15% by 31-Dec-2025.”).
- Sustainability & Next Cycle section with Pillar | Status | Owner | Next Step.
- Validation checklist confirming traceability, completeness, and accessibility.

Accessibility & writing guidelines
- Pair icons/badges with text; avoid color-only signals.
- Lead with numbers; keep paragraphs tight; prefer bullets for scanability.
- Explicitly label pp vs %, and always show the measurement frame.
- End each section with “Implications & Next Actions” (Owner, Action, Due, Metric/Trigger).

Failure modes to avoid
- Omitting links to sources or compressing away critical numeric context.
- Mixing pp and % or missing units/timeframes.
- “Fixing” simulated numbers or recomputing their distributions.
- Recommendations without a traceable evidence chain.

Definition of done
- Decision-ready (Scale / Iterate / Hold) with quantified rationale, probabilities,
owners, and due dates.
- All mandatory visuals generated via strategic_visualization_generator and referenced in the text.
- Every “TBD” replaced with “N/A (pending actual data)” + collection plan.
- Numbers are consistent with Simulate/Evaluate; Criteria Lock referenced and applied.
""",
         tools=tools,
         verbose=True,
         allow_delegation=False,
         max_iter=config.MAX_ITERATIONS,
         llm=llm,
         memory=False,
         cache=False,
      )
    
   @staticmethod
   def create_task(all_phase_outputs: str, agent):
      from crewai import Task
      description = """
         Create a comprehensive final report that consolidates all analysis outputs into a cohesive strategic document 
         with professional visualizations and charts.
         
         All Phase Outputs to Consolidate:
         {all_phase_outputs}
         
         Report Requirements:
         1. **Executive Summary**
            - High-level strategic overview and key findings
            - Critical recommendations and decision points
            - Expected outcomes and success probability
            - Resource requirements and timeline summary
            
         2. **Methodology and Approach**
            - DECIDE framework implementation overview
            - Analysis scope and limitations
            - Data sources and quality assessment
            - Agent-based analysis approach explanation
            
         3. **Strategic Analysis Synthesis**
            - Problem definition and context integration
            - Risk assessment consolidation with RISK MATRIX visualization
            - Option analysis and recommendation with SCENARIO COMPARISON charts
            - Implementation roadmap summary with TIMELINE visualization
            
         4. **Quantitative Analysis Results**
            - Monte Carlo simulation findings with DISTRIBUTION charts
            - Scenario analysis outcomes with COMPARISON visualizations
            - Statistical confidence levels
            - Risk-adjusted recommendations with supporting charts
            
         5. **Implementation Framework**
            - Detailed implementation plan summary with GANTT chart
            - Resource allocation and timeline with visual timeline
            - Success measurement framework with PERFORMANCE DASHBOARD
            - Risk mitigation strategies with risk matrix
            
         6. **Strategic Recommendations**
            - Primary strategic recommendation with rationale
            - Alternative approaches and contingencies
            - Critical success factors and dependencies  
            - Next steps and decision timeline
            
         **CRITICAL VISUALIZATION REQUIREMENTS:**
         
         You MUST use the strategic_visualization_generator tool to create charts. For each major section, 
         call the tool with sample data if real data is not available:
         
         STEP 1: Generate Risk Matrix
         Use: strategic_visualization_generator(chart_type="risk_matrix", data_input=sample_risk_data, title="Risk Assessment")
         
         STEP 2: Generate ROI Chart  
         Use: strategic_visualization_generator(chart_type="roi_projection", data_input=sample_roi_data, title="ROI Projection")
         
         STEP 3: Generate Timeline
         Use: strategic_visualization_generator(chart_type="timeline", data_input=sample_timeline_data, title="Implementation Timeline")
         
         STEP 4: Generate Performance Dashboard
         Use: strategic_visualization_generator(chart_type="performance_dashboard", data_input=sample_kpi_data, title="Performance Dashboard")
         
         Include the tool outputs in your report as text references - images will be automatically placed in the PDF.
         
         For each major section, you consider what visualizations would best support the narrative 
         and enhance understanding. You create:
         - Risk matrices and heat maps for risk analysis
         - ROI projections and financial forecasts
         - Timeline charts and Gantt charts for implementation planning
         - Monte Carlo distributions for uncertainty analysis
         - Stakeholder impact matrices
         - Performance dashboards with KPIs
         - SWOT analysis matrices
         - Scenario comparison charts
         
         Each visualization should be generated with appropriate data extracted from the phase outputs and 
         embedded in the report with clear titles and explanations.
         
         Create a professional, executive-ready report that enables informed strategic decision-making through 
         both comprehensive analysis and compelling visual insights.
         """.format(all_phase_outputs=all_phase_outputs)
      expected_output = """A comprehensive final report in both PDF and Markdown formats containing:
         
         # MIMÉTICA Strategic Decision Support System
         ## Comprehensive Strategic Analysis Report
         
         ---
         
         **Document Information**
         - **Report Type**: Strategic Decision Support Analysis
         - **Generated By**: MIMÉTICA MVP 1.0 AI System
         - **Analysis Date**: [Current Date]
         - **Report Version**: 1.0
         - **Confidentiality**: [Classification Level]
         - **Files Used**: [List of all uploaded file names used in this analysis]
         - **Project Name**: [Project name from project information]  
         - **Project Description**: [Project description from project information]
         - **Analysis Focus**: [Analysis focus from project information]
         
         ---
         
         ## Executive Summary
         
         ### Strategic Overview
         This comprehensive analysis was conducted using the MIMÉTICA strategic decision support system, implementing the DECIDE methodology (Define → Explore → Create → Implement → Decide/Simulate → Evaluate) through AI-powered multi-agent orchestration.
         
         #### Key Findings
         1. **Strategic Assessment**: [Primary strategic finding]
         2. **Risk Analysis**: [Key risk insights]
         3. **Opportunity Identification**: [Main opportunities identified]
         4. **Implementation Feasibility**: [Feasibility assessment]
         5. **Expected Outcomes**: [Projected results and probability]
         
         #### Critical Recommendations
         **Primary Recommendation**: [Main strategic recommendation]
         - **Rationale**: [Why this recommendation is optimal]
         - **Expected Impact**: [Projected outcomes and benefits]
         - **Implementation Timeline**: [Recommended timeline]
         - **Resource Requirements**: [Summary of resources needed]
         - **Success Probability**: [Statistical confidence level]
         
         **Alternative Approaches**: [Brief overview of alternative options]
         
         #### Decision Requirements
         - **Immediate Decision**: [What needs to be decided now]
         - **Decision Timeline**: [When decision is needed]
         - **Decision Authority**: [Who should make the decision]
         - **Information Needs**: [Any additional information required]
         
         #### Investment and Returns
         - **Total Investment Required**: [Financial investment summary]
         - **Expected ROI**: [Return on investment projection]
         - **Payback Period**: [Time to recover investment]
         - **Risk-Adjusted Returns**: [ROI considering risks]
         
         ---
         
         ## Methodology and Analytical Framework
         
         ### DECIDE Methodology Implementation
         The analysis followed the systematic DECIDE framework:
         
         #### **D**efine - Problem Definition and Scope
         - **Problem Statement**: [Core problem or opportunity addressed]
         - **Strategic Objectives**: [Primary objectives defined]
         - **Success Criteria**: [How success will be measured]
         - **Scope and Boundaries**: [What is included/excluded]
         
         #### **E**xplore - Contextual Analysis and Research
         - **Market Context**: [Industry and market analysis]
         - **Competitive Landscape**: [Competition and positioning]
         - **Risk Mapping**: [Comprehensive risk assessment]
         - **Stakeholder Analysis**: [Key stakeholder considerations]
         
         #### **C**reate - Strategic Options Development
         - **Option Generation**: [How strategic alternatives were developed]
         - **Option Analysis**: [Evaluation methodology for options]
         - **Comparative Assessment**: [How options were compared]
         
         #### **I**mplement - Implementation Planning
         - **Implementation Strategy**: [Overall implementation approach]
         - **Resource Planning**: [Resource allocation methodology]
         - **Timeline Development**: [Schedule planning approach]
         
         #### **D**ecide/Simulate - Quantitative Analysis
         - **Monte Carlo Simulation**: [Statistical modeling approach]
         - **Scenario Analysis**: [Multiple scenario development]
         - **Risk Quantification**: [Risk measurement methodology]
         
         #### **E**valuate - Success Measurement Framework
         - **KPI Development**: [Key performance indicator creation]
         - **Monitoring Framework**: [Performance measurement system]
         - **Continuous Improvement**: [Learning and adaptation approach]
         
         ### Multi-Agent AI Analysis Approach
         #### Agent Orchestration
         - **Collector Agent**: [Document processing and vectorization]
         - **Multidisciplinary Agent**: [Integrated feasibility analysis]
         - **Define Agent**: [Problem definition and objective setting]
         - **Explore Agent**: [Contextual research and risk mapping]
         - **Create Agent**: [Strategic option development]
         - **Implement Agent**: [Implementation planning]
         - **Simulate Agent**: [Monte Carlo simulation and scenario analysis]
         - **Evaluate Agent**: [KPI and evaluation framework development]
         - **Report Agent**: [Comprehensive report synthesis]
         
         #### Data Sources and Quality
         - **Document Analysis**: [Summary of documents processed]
         - **External Research**: [External data sources utilized]
         - **Expert Knowledge**: [AI agent expertise integration]
         - **Data Quality Assessment**: [Quality and reliability evaluation]
         
         ---
         
         ## Strategic Problem Analysis
         
         ### Problem Definition and Context
         #### Core Strategic Challenge
         [Detailed problem statement from Define Agent output]
         
         #### Business Context and Environment
         [Market context and environmental factors from Explore Agent]
         
         #### Stakeholder Landscape
         [Stakeholder analysis and impact assessment]
         
         #### Root Cause Analysis
         [Underlying causes and contributing factors]
         
         ### Strategic Objectives
         #### Primary Objectives
         1. **Objective 1**: [First strategic objective with metrics]
         2. **Objective 2**: [Second strategic objective]
         3. **Objective 3**: [Third strategic objective]
         
         #### Success Criteria and Metrics
         [Specific success measurements and targets]
         
         #### Constraints and Assumptions
         [Key limitations and underlying assumptions]
         
         ---
         
         ## Risk Assessment and Analysis
         
         ### Comprehensive Risk Profile
         #### Strategic Risks
         [High-level strategic risks and their implications]
         
         #### Operational Risks
         [Implementation and operational risk factors]
         
         #### Financial Risks
         [Financial and investment-related risks]
         
         #### Market and Competitive Risks
         [External market and competition risks]
         
         ### Risk Quantification and Impact
         
         **GENERATE RISK MATRIX VISUALIZATION HERE**: Use the strategic_visualization_generator tool with chart_type="risk_matrix" to create a visual risk assessment matrix showing probability vs impact for all identified risks.
         
         #### Risk Prioritization Matrix
         | Risk Category | Probability | Impact | Priority Score | Mitigation Strategy |
         |---------------|-------------|---------|----------------|-------------------|
         | [Risk 1] | [H/M/L] | [H/M/L] | [Score] | [Strategy] |
         | [Risk 2] | [H/M/L] | [H/M/L] | [Score] | [Strategy] |
         | [Risk 3] | [H/M/L] | [H/M/L] | [Score] | [Strategy] |
         
         #### Risk Mitigation Framework
         [Comprehensive risk management and mitigation approach]
         
         ---
         
         ## Strategic Options Analysis
         
         ### Option Development and Evaluation
         #### Strategic Option 1: [Option Name]
         **Overview**: [High-level description]
         
         **Advantages**:
         - [Key advantage 1]
         - [Key advantage 2]
         - [Key advantage 3]
         
         **Disadvantages**:
         - [Key limitation 1]
         - [Key limitation 2]
         - [Key limitation 3]
         
         **Resource Requirements**: [Summary of resources needed]
         **Implementation Complexity**: [Complexity assessment]
         **Risk Profile**: [Risk level and key concerns]
         
         #### Strategic Option 2: [Option Name]
         [Similar detailed analysis for second option]
         
         #### Strategic Option 3: [Option Name] (if applicable)
         [Similar detailed analysis for third option]
         
         ### Comparative Option Analysis
         #### Decision Matrix
         [Weighted scoring comparison of all options]
         
         #### Recommendation Rationale
         [Detailed explanation of why the recommended option was selected]
         
         ---
         
         ## Quantitative Analysis and Simulation Results
         
         ### Monte Carlo Simulation Analysis
         
         **GENERATE MONTE CARLO VISUALIZATION HERE**: Use the strategic_visualization_generator tool with chart_type="monte_carlo_distribution" to create a distribution chart showing simulation results with key statistics and percentiles.
         
         #### Simulation Methodology
         - **Model Parameters**: [Key variables and distributions]
         - **Simulation Runs**: [Number of iterations performed]
         - **Scenario Design**: [How scenarios were constructed]
         - **Statistical Methods**: [Analysis techniques used]
         
         #### Scenario Analysis Results
         
         **GENERATE SCENARIO COMPARISON CHART HERE**: Use the strategic_visualization_generator tool with chart_type="scenario_comparison" to compare optimistic, baseline, and pessimistic scenarios.
         
         #### Optimistic Scenario (90th Percentile)
         - **Key Outcomes**: [Primary results in best case]
         - **Probability**: [Likelihood of achieving optimistic results]
         - **Value Creation**: [Maximum potential value]
         - **Success Factors**: [What needs to go right]
         
         #### Baseline Scenario (50th Percentile)
         - **Expected Outcomes**: [Most likely results]
         - **Probability Range**: [Confidence intervals]
         - **Risk-Adjusted Returns**: [Expected value considering risks]
         - **Key Assumptions**: [Critical assumptions for baseline case]
         
         #### Pessimistic Scenario (10th Percentile)
         - **Adverse Outcomes**: [Results in challenging conditions]
         - **Risk Materialization**: [What could go wrong]
         - **Mitigation Requirements**: [Actions needed to avoid worst case]
         - **Contingency Plans**: [Alternative approaches if needed]
         
         ### Statistical Analysis Summary
         #### Key Statistical Measures
         - **Expected Value**: [Mean outcome across all scenarios]
         - **Standard Deviation**: [Variability in outcomes]
         - **Value at Risk (5%)**: [Maximum likely loss]
         - **Probability of Success**: [Likelihood of meeting objectives]
         
         #### Sensitivity Analysis
         [Analysis of which factors most influence outcomes]
         
         ---
         
         ## Implementation Framework and Roadmap
         
         ### Implementation Strategy Overview
         #### Strategic Approach
         [High-level implementation philosophy and approach]
         
         **GENERATE TIMELINE VISUALIZATION HERE**: Use the strategic_visualization_generator tool with chart_type="timeline" to create a Gantt chart showing implementation phases, durations, and dependencies.
         
         #### Implementation Phases
         1. **Phase 1: Preparation** ([Duration])
            - [Key activities and deliverables]
            - [Resource requirements]
            - [Success criteria]
         
         2. **Phase 2: Core Implementation** ([Duration])
            - [Key activities and deliverables]
            - [Resource requirements]
            - [Success criteria]
         
         3. **Phase 3: Integration and Testing** ([Duration])
            - [Key activities and deliverables]
            - [Resource requirements]
            - [Success criteria]
         
         4. **Phase 4: Deployment and Closure** ([Duration])
            - [Key activities and deliverables]
            - [Resource requirements]
            - [Success criteria]
         
         **GENERATE ROI PROJECTION CHART HERE**: Use the strategic_visualization_generator tool with chart_type="roi_projection" to show expected financial returns over time across all implementation phases.
         
         ### Resource Requirements and Allocation
         #### Human Resources
         - **Total FTE Requirements**: [Full-time equivalent needs]
         - **Key Roles and Skills**: [Critical personnel requirements]
         - **External Support**: [Consultant and vendor needs]
         - **Training and Development**: [Skill development requirements]
         
         #### Financial Investment
         - **Total Investment**: [Complete financial requirement]
         - **Phase-wise Allocation**: [Budget distribution across phases]
         - **Contingency Reserves**: [Risk buffer allocations]
         - **Cash Flow Timeline**: [When investments are needed]
         
         #### Technology and Infrastructure
         - **Technology Requirements**: [Systems and tools needed]
         - **Infrastructure Needs**: [Physical and digital infrastructure]
         - **Integration Requirements**: [System connectivity needs]
         
         ### Timeline and Milestones
         #### Master Timeline
         [High-level project schedule with key milestones]
         
         #### Critical Path Activities
         [Activities that determine overall timeline]
         
         #### Key Milestones and Gates
         [Major checkpoints and decision points]
         
         ---
         
         ## Success Measurement and Evaluation Framework
         
         **GENERATE PERFORMANCE DASHBOARD HERE**: Use the strategic_visualization_generator tool with chart_type="performance_dashboard" to create a comprehensive KPI dashboard showing current vs target performance across all key metrics.
         
         ### Key Performance Indicators (KPIs)
         #### Strategic KPIs
         1. **KPI 1**: [Primary strategic measure]
            - **Target**: [Specific target value]
            - **Measurement Method**: [How it's measured]
            - **Frequency**: [How often measured]
         
         2. **KPI 2**: [Second strategic measure]
         3. **KPI 3**: [Third strategic measure]
         
         #### Operational KPIs
         [Operational performance measures]
         
         #### Financial KPIs
         [Financial performance measures]
         
         ### Monitoring and Evaluation System
         #### Real-Time Monitoring
         [Continuous performance tracking approach]
         
         #### Periodic Evaluation
         [Scheduled performance reviews and assessments]
         
         #### Corrective Action Framework
         [How performance issues will be addressed]
         
         ### Success Criteria and Thresholds
         #### Success Definition
         [What constitutes success for this initiative]
         
         #### Warning Indicators
         [Early warning signs of potential problems]
         
         #### Failure Criteria
         [Conditions that would indicate need for major course correction]
         
         ---
         
         ## Strategic Recommendations
         
         ### Primary Strategic Recommendation
         #### Recommended Approach
         **Strategic Option**: [Recommended option name]
         
         **Recommendation Summary**: [Concise recommendation statement]
         
         #### Detailed Rationale
         **Why This Option**:
         1. **Strategic Alignment**: [How it aligns with objectives]
         2. **Risk-Return Profile**: [Optimal balance of risk and return]
         3. **Implementation Feasibility**: [Realistic implementation prospects]
         4. **Stakeholder Acceptance**: [Likelihood of stakeholder support]
         5. **Competitive Advantage**: [Unique positioning benefits]
         
         #### Expected Outcomes and Benefits
         **Primary Benefits**:
         - [Key benefit 1 with quantification]
         - [Key benefit 2 with quantification]
         - [Key benefit 3 with quantification]
         
         **Secondary Benefits**:
         - [Additional positive impacts]
         
         **Timeline for Benefits Realization**:
         - **Short-term (0-12 months)**: [Early benefits]
         - **Medium-term (1-2 years)**: [Intermediate benefits]
         - **Long-term (2+ years)**: [Long-term value creation]
         
         ### Alternative Recommendations
         #### Scenario-Based Alternatives
         **Conservative Approach**: [Recommendation for risk-averse stakeholders]
         **Aggressive Approach**: [Recommendation for growth-focused strategy]
         **Hybrid Approach**: [Combination strategy recommendation]
         
         ### Implementation Recommendations
         #### Critical Success Factors
         1. **Success Factor 1**: [Most critical element for success]
         2. **Success Factor 2**: [Second most important factor]
         3. **Success Factor 3**: [Third critical factor]
         
         #### Risk Mitigation Priorities
         1. **Priority 1**: [Highest priority risk to address]
         2. **Priority 2**: [Second priority risk management]
         3. **Priority 3**: [Third priority risk area]
         
         #### Resource Mobilization Strategy
         [How to secure and deploy necessary resources]
         
         ### Decision Framework and Next Steps
         #### Immediate Decision Requirements
         **Decision Needed**: [What decision is required]
         **Decision Maker**: [Who should make the decision]
         **Decision Timeline**: [When decision is needed]
         **Information Required**: [Any additional information needed]
         
         #### Pre-Implementation Actions
         1. **Action 1**: [First preparatory action needed]
         2. **Action 2**: [Second preparatory action]
         3. **Action 3**: [Third preparatory action]
         
         #### Go/No-Go Criteria
         **Go Criteria**: [Conditions that support proceeding]
         **No-Go Criteria**: [Conditions that suggest not proceeding]
         **Conditional Go**: [Conditions for proceeding with modifications]
         
         ---
         
         ## Appendices
         
         ### Appendix A: Detailed Methodology
         [Comprehensive methodology documentation]
         
         ### Appendix B: Risk Register
         [Complete risk inventory and assessment]
         
         ### Appendix C: Financial Models
         [Detailed financial analysis and projections]
         
         ### Appendix D: Stakeholder Analysis
         [Comprehensive stakeholder assessment]
         
         ### Appendix E: Implementation Timeline
         [Detailed project schedule and dependencies]
         
         ### Appendix F: Success Metrics Framework
         [Complete KPI definitions and measurement plans]
         
         ---
         
         ## Document Control and Approval
         
         ### Document History
         | Version | Date | Author | Changes |
         |---------|------|---------|---------|
         | 1.0 | [Date] | MIMÉTICA AI System | Initial comprehensive analysis |
         
         ### Review and Approval
         | Role | Name | Signature | Date |
         |------|------|-----------|------|
         | Strategic Analyst | [Name] | [Digital Signature] | [Date] |
         | Project Manager | [Name] | [Digital Signature] | [Date] |
         | Executive Sponsor | [Name] | [Digital Signature] | [Date] |
         
         ### Distribution List
         - Executive Leadership Team
         - Project Steering Committee
         - Implementation Team Leads
         - Key Stakeholder Representatives
         
         ---
         
         ## Footer
         
         **Report Generated By**: MIMÉTICA MVP 1.0 - Strategic Decision Support System  
         **Powered By**: CrewAI Multi-Agent Orchestration Framework  
         **Technology Stack**: OpenAI GPT-4o, Qdrant Vector Database, Streamlit Interface  
         **Report Date**: [Current Date and Time]  
         **Document Classification**: [Confidentiality Level]  
         **Copyright**: © [Year] Tuinkel - All Rights Reserved  
         
         *This report contains confidential and proprietary information. Distribution should be limited to authorized personnel only.*
         """

      return Task(
         description=description,
         expected_output=expected_output,
         markdown=True,
         agent = agent,
         output_file="09_general_report.md"
      )
