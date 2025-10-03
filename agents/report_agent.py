from crewai import Agent
# Using markdown_editor_tool for report generation
from tools.custom_tools import markdown_editor_tool, strategic_visualization_generator, execute_python_code
from config import config
import streamlit as st

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
        
        return Agent(
            role="Strategic Report Analyst and Visualization Specialist",
            goal="Synthesize all phase outputs into a comprehensive, visually enhanced strategic report with professional charts and graphs. You MUST use the strategic_visualization_generator tool to create charts for each major section.",
            backstory="""You are a senior strategic analyst with expertise in business intelligence and data visualization. 
            Your specialty is creating comprehensive strategic reports that combine rigorous analysis with compelling 
            visual representations. You excel at:
            
            1. **Strategic Synthesis**: Integrating complex analysis from multiple sources into coherent insights
            2. **Data Visualization**: Creating professional charts, graphs, and diagrams that enhance understanding
            3. **Executive Communication**: Translating technical analysis into executive-ready recommendations
            4. **Visual Storytelling**: Using charts and graphs to tell a compelling strategic narrative
            
            CRITICAL: You ALWAYS use the strategic_visualization_generator tool to create charts for every report section.
            
            Charts will be saved as image files and integrated into the final PDF. You should include image placeholder
            references in your report text where charts should appear. Do NOT expect or include base64 image data 
            in your report content - the system will handle image placement automatically.
            You understand that executives and stakeholders make better decisions when complex data is presented 
            visually and that a well-visualized report significantly increases comprehension and buy-in.
            
            You are required to generate visualizations for every major section of your reports.""",
            tools=[
                markdown_editor_tool,
                strategic_visualization_generator,
                execute_python_code
            ],
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE,
            llm=llm
        )
    
    @staticmethod
    def create_task(all_phase_outputs: str):
        from crewai import Task
        return Task(
            description = f"""
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
            """,
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
            """,
            markdown=True,
            agent = ReportAgent.create_agent(),
            output_file="comprehensive_strategic_analysis_report.md"
        )
