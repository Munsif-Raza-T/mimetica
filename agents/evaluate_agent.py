from crewai import Agent
# Using evaluation_framework_tool for KPI development
from tools.custom_tools import evaluation_framework_tool
from config import config
import streamlit as st

class EvaluateAgent:
    """Agent responsible for defining KPIs, success metrics, and monitoring recommendations"""
    
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
            role="Evaluation Framework and KPI Specialist",
            goal="Define comprehensive KPIs, success metrics, and create monitoring frameworks for measuring initiative success",
            backstory="""You are a senior performance measurement expert and evaluation specialist with extensive 
            experience in developing KPI frameworks, success metrics, and monitoring systems. You excel at creating 
            measurable success criteria, designing evaluation methodologies, and establishing monitoring frameworks 
            that enable continuous improvement. Your expertise includes performance measurement, data analytics, 
            and evaluation research methodologies.""",
            tools=[
                evaluation_framework_tool
            ],
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE,
            llm=llm
        )
    
    @staticmethod
    def create_task(implementation_plan: str, simulation_results: str):
        from crewai import Task
        return Task(
            description = f"""
            Create a comprehensive evaluation framework with KPIs, success metrics, and monitoring recommendations.
            
            Implementation Plan:
            {implementation_plan}
            
            Simulation Analysis Results:
            {simulation_results}
            
            Evaluation Framework Requirements:
            1. **KPI Development**
               - Define quantitative and qualitative KPIs aligned with objectives
               - Create leading and lagging indicators
               - Establish baseline measurements and target values
               - Design measurement methodologies and data collection processes
               
            2. **Success Metrics Framework**
               - Define success criteria at multiple levels (strategic, tactical, operational)
               - Create measurement timelines and milestones
               - Establish threshold values for success/failure determination
               - Design comparative benchmarking approaches
               
            3. **Monitoring and Evaluation System**
               - Design real-time monitoring dashboards and reporting
               - Create evaluation schedules and review processes
               - Establish data governance and quality assurance
               - Define corrective action triggers and response procedures
               
            4. **Performance Analytics**
               - Design data analysis frameworks for performance insights
               - Create predictive analytics for early warning systems
               - Establish trend analysis and pattern recognition
               - Design comparative analysis methodologies
               
            5. **Continuous Improvement Framework**
               - Create feedback loops for performance optimization
               - Design learning and adaptation mechanisms
               - Establish best practice identification and sharing
               - Create innovation and improvement recommendation processes
            
            Create a comprehensive evaluation document that enables effective performance measurement and continuous improvement.
            """,
            expected_output = """A comprehensive evaluation framework document in Markdown/PDF format containing:
            
            # Evaluation Framework and Success Measurement System
            
            ## Executive Summary
            - **Evaluation Scope**: [What will be measured and evaluated]
            - **Key Performance Areas**: [Primary domains of measurement]
            - **Success Definition**: [Overall success criteria and thresholds]
            - **Monitoring Approach**: [Real-time and periodic evaluation strategy]
            - **Continuous Improvement**: [How insights will drive improvements]
            
            ## Evaluation Philosophy and Approach
            
            ### Evaluation Principles
            - **Principle 1**: [Evidence-based decision making]
            - **Principle 2**: [Continuous learning and adaptation]
            - **Principle 3**: [Stakeholder-centric measurement]
            - **Principle 4**: [Balanced scorecard approach]
            - **Principle 5**: [Transparency and accountability]
            
            ### Measurement Philosophy
            - **Balanced Measurement**: [Quantitative and qualitative metrics]
            - **Multi-level Assessment**: [Strategic, tactical, and operational levels]
            - **Stakeholder Perspective**: [Multiple stakeholder viewpoints]
            - **Temporal Dimension**: [Short-term and long-term measurements]
            
            ## Key Performance Indicators (KPIs) Framework
            
            ### Strategic Level KPIs
            #### Financial Performance KPIs
            1. **Return on Investment (ROI)**
               - **Definition**: [Specific calculation methodology]
               - **Target Value**: [Specific target with timeframe]
               - **Measurement Frequency**: [How often measured]
               - **Data Sources**: [Where data comes from]
               - **Responsible Party**: [Who measures and reports]
               - **Threshold Values**: [Success/Warning/Failure levels]
            
            2. **Cost-Benefit Ratio**
               - **Definition**: [Total benefits divided by total costs]
               - **Target Value**: [Minimum acceptable ratio]
               - **Measurement Method**: [Calculation approach]
               - **Reporting Schedule**: [When and how reported]
            
            3. **Budget Performance Index**
               - **Definition**: [Actual costs vs. budgeted costs]
               - **Target Value**: [Variance tolerance levels]
               - **Alert Thresholds**: [When corrective action needed]
            
            #### Strategic Outcome KPIs
            1. **Objective Achievement Rate**
               - **Definition**: [Percentage of strategic objectives met]
               - **Target Value**: [Minimum success percentage]
               - **Assessment Method**: [How objectives are evaluated]
            
            2. **Stakeholder Satisfaction Index**
               - **Definition**: [Composite satisfaction score]
               - **Target Value**: [Minimum satisfaction level]
               - **Measurement Method**: [Survey and feedback approach]
            
            3. **Market Position Index**
               - **Definition**: [Competitive position measurement]
               - **Target Value**: [Desired market position]
               - **Benchmarking Approach**: [How position is determined]
            
            ### Tactical Level KPIs
            #### Operational Efficiency KPIs
            1. **Implementation Timeline Adherence**
               - **Definition**: [Schedule performance measurement]
               - **Target Value**: [Acceptable schedule variance]
               - **Measurement Method**: [Project management metrics]
               - **Reporting Frequency**: [Weekly/Monthly updates]
            
            2. **Resource Utilization Efficiency**
               - **Definition**: [Actual vs. planned resource usage]
               - **Target Value**: [Optimal utilization percentage]
               - **Monitoring Approach**: [Resource tracking methodology]
            
            3. **Quality Performance Index**
               - **Definition**: [Deliverable quality measurement]
               - **Target Value**: [Quality standards threshold]
               - **Assessment Method**: [Quality assurance process]
            
            #### Process Performance KPIs
            1. **Process Cycle Time**
               - **Definition**: [Time to complete key processes]
               - **Target Value**: [Maximum acceptable cycle time]
               - **Measurement Approach**: [Process timing methodology]
            
            2. **Error Rate and Quality**
               - **Definition**: [Defect rate in deliverables]
               - **Target Value**: [Maximum acceptable error rate]
               - **Quality Control**: [Error detection and correction process]
            
            3. **Stakeholder Engagement Level**
               - **Definition**: [Active stakeholder participation]
               - **Target Value**: [Minimum engagement threshold]
               - **Measurement Method**: [Engagement tracking approach]
            
            ### Operational Level KPIs
            #### Activity-Based KPIs
            1. **Task Completion Rate**
               - **Definition**: [Percentage of tasks completed on time]
               - **Target Value**: [Minimum completion rate]
               - **Tracking Method**: [Task management system]
            
            2. **Team Productivity Index**
               - **Definition**: [Output per unit of input]
               - **Target Value**: [Productivity benchmark]
               - **Measurement Approach**: [Productivity calculation method]
            
            3. **Communication Effectiveness**
               - **Definition**: [Information flow and clarity]
               - **Target Value**: [Communication quality standard]
               - **Assessment Method**: [Communication audit approach]
            
            ## Success Metrics and Criteria
            
            ### Multi-Dimensional Success Framework
            #### Quantitative Success Criteria
            **Financial Success:**
            - **Primary Criterion**: [ROI exceeds X% within Y timeframe]
            - **Secondary Criteria**: [Cost savings, revenue impact]
            - **Measurement Timeline**: [When success is evaluated]
            
            **Performance Success:**
            - **Primary Criterion**: [All strategic objectives achieved]
            - **Secondary Criteria**: [Quality standards, timeline adherence]
            - **Success Threshold**: [Minimum performance level]
            
            **Stakeholder Success:**
            - **Primary Criterion**: [Stakeholder satisfaction >X%]
            - **Secondary Criteria**: [Engagement levels, feedback quality]
            - **Measurement Method**: [Satisfaction survey approach]
            
            #### Qualitative Success Indicators
            **Strategic Alignment:**
            - **Criterion**: [Initiative aligns with organizational strategy]
            - **Assessment Method**: [Strategic fit evaluation]
            - **Evidence Requirements**: [Documentation and validation]
            
            **Innovation and Learning:**
            - **Criterion**: [New capabilities and knowledge gained]
            - **Assessment Method**: [Capability assessment framework]
            - **Success Indicators**: [Specific learning outcomes]
            
            **Sustainability:**
            - **Criterion**: [Results are sustainable long-term]
            - **Assessment Method**: [Sustainability analysis]
            - **Evidence Requirements**: [Long-term impact validation]
            
            ### Success Measurement Timeline
            #### Immediate Success (0-3 months)
            - **Launch Success**: [Successful initiative launch]
            - **Early Adoption**: [Initial stakeholder engagement]
            - **Process Establishment**: [Key processes operational]
            
            #### Short-term Success (3-12 months)
            - **Performance Trends**: [Positive performance indicators]
            - **Stakeholder Feedback**: [Positive stakeholder response]
            - **Milestone Achievement**: [Key milestones met]
            
            #### Medium-term Success (1-2 years)
            - **Objective Achievement**: [Strategic objectives realized]
            - **ROI Realization**: [Financial returns achieved]
            - **Capability Development**: [New capabilities established]
            
            #### Long-term Success (2+ years)
            - **Sustained Performance**: [Continued positive results]
            - **Market Impact**: [Measurable market position improvement]
            - **Organizational Learning**: [Knowledge and best practices established]
            
            ## Monitoring and Measurement System
            
            ### Real-Time Monitoring Framework
            #### Dashboard Design
            **Executive Dashboard:**
            - **Key Metrics**: [Top 5-7 strategic indicators]
            - **Visualization**: [Charts, graphs, and trend lines]
            - **Update Frequency**: [Real-time or daily updates]
            - **Alert System**: [Automated alerts for threshold breaches]
            
            **Operational Dashboard:**
            - **Detailed Metrics**: [Comprehensive operational indicators]
            - **Drill-Down Capability**: [Detailed analysis functionality]
            - **Comparative Analysis**: [Trend and benchmark comparisons]
            
            **Stakeholder Dashboard:**
            - **Relevant Metrics**: [Stakeholder-specific indicators]
            - **Communication Format**: [User-friendly presentations]
            - **Access Control**: [Role-based access to information]
            
            #### Data Collection and Management
            **Data Sources:**
            - **Internal Systems**: [ERP, CRM, project management tools]
            - **External Sources**: [Market data, benchmark information]
            - **Survey Data**: [Stakeholder feedback and satisfaction]
            - **Observational Data**: [Direct observation and assessment]
            
            **Data Quality Assurance:**
            - **Validation Rules**: [Data accuracy verification]
            - **Quality Controls**: [Error detection and correction]
            - **Audit Procedures**: [Data integrity verification]
            
            ### Periodic Evaluation Schedule
            #### Evaluation Frequency and Scope
            **Daily Monitoring:**
            - **Scope**: [Operational metrics and immediate indicators]
            - **Responsible Party**: [Operations team]
            - **Reporting**: [Dashboard updates and alerts]
            
            **Weekly Reviews:**
            - **Scope**: [Progress against plans and targets]
            - **Responsible Party**: [Project management team]
            - **Output**: [Weekly status reports]
            
            **Monthly Analysis:**
            - **Scope**: [Comprehensive performance assessment]
            - **Responsible Party**: [Management team]
            - **Output**: [Monthly performance reports]
            
            **Quarterly Evaluation:**
            - **Scope**: [Strategic objective assessment]
            - **Responsible Party**: [Executive team]
            - **Output**: [Quarterly strategic reviews]
            
            **Annual Assessment:**
            - **Scope**: [Comprehensive success evaluation]
            - **Responsible Party**: [Board and senior leadership]
            - **Output**: [Annual impact assessment]
            
            ## Performance Analytics and Insights
            
            ### Data Analysis Framework
            #### Descriptive Analytics
            - **Current State Analysis**: [What is happening now]
            - **Historical Trend Analysis**: [What has happened over time]
            - **Comparative Analysis**: [How performance compares to benchmarks]
            
            #### Predictive Analytics
            - **Trend Projection**: [Where performance is heading]
            - **Risk Prediction**: [What problems might emerge]
            - **Opportunity Identification**: [What opportunities exist]
            
            #### Prescriptive Analytics
            - **Optimization Recommendations**: [How to improve performance]
            - **Action Planning**: [What specific actions to take]
            - **Resource Allocation**: [How to allocate resources optimally]
            
            ### Early Warning System
            #### Alert Mechanisms
            **Performance Alerts:**
            - **Threshold Breaches**: [When KPIs fall below acceptable levels]
            - **Trend Alerts**: [When negative trends are detected]
            - **Variance Alerts**: [When actual performance deviates significantly from plan]
            
            **Risk Alerts:**
            - **Risk Materialization**: [When identified risks begin to occur]
            - **New Risk Detection**: [When new risks are identified]
            - **Risk Escalation**: [When risk levels increase]
            
            #### Response Procedures
            **Alert Response Process:**
            1. **Alert Generation**: [Automated alert creation]
            2. **Impact Assessment**: [Evaluation of alert significance]
            3. **Response Planning**: [Development of corrective actions]
            4. **Implementation**: [Execution of response measures]
            5. **Monitoring**: [Tracking response effectiveness]
            
            ## Continuous Improvement Framework
            
            ### Learning and Adaptation System
            #### Feedback Loops
            **Performance Feedback:**
            - **Regular Feedback Collection**: [Systematic feedback gathering]
            - **Feedback Analysis**: [Pattern identification and insights]
            - **Improvement Identification**: [Specific improvement opportunities]
            
            **Stakeholder Feedback:**
            - **Satisfaction Surveys**: [Regular stakeholder satisfaction measurement]
            - **Focus Groups**: [Detailed stakeholder input sessions]
            - **Advisory Committees**: [Ongoing stakeholder advisory input]
            
            #### Innovation and Enhancement
            **Best Practice Identification:**
            - **Success Factor Analysis**: [What works well and why]
            - **Best Practice Documentation**: [Capture and sharing of successful approaches]
            - **Knowledge Management**: [Organizational learning systems]
            
            **Continuous Enhancement:**
            - **Regular Process Review**: [Systematic process evaluation]
            - **Innovation Initiatives**: [Ongoing improvement projects]
            - **Technology Enhancement**: [Technology upgrade and optimization]
            
            ### Benchmarking and Comparative Analysis
            #### Internal Benchmarking
            - **Historical Performance**: [Comparison to past performance]
            - **Cross-Functional Comparison**: [Comparison across departments]
            - **Best-in-Class Internal**: [Learning from internal excellence]
            
            #### External Benchmarking
            - **Industry Benchmarks**: [Comparison to industry standards]
            - **Competitive Analysis**: [Performance relative to competitors]
            - **Best-in-Class External**: [Learning from external excellence]
            
            ## Implementation and Governance
            
            ### Measurement System Implementation
            #### Implementation Timeline
            **Phase 1: Foundation (Month 1-2)**
            - **System Setup**: [Monitoring infrastructure establishment]
            - **Data Integration**: [Data source connection and validation]
            - **Dashboard Development**: [Visualization tool creation]
            
            **Phase 2: Deployment (Month 3-4)**
            - **User Training**: [Stakeholder training on measurement system]
            - **Process Integration**: [Integration with existing processes]
            - **Initial Calibration**: [System testing and calibration]
            
            **Phase 3: Optimization (Month 5-6)**
            - **Performance Tuning**: [System optimization based on usage]
            - **Process Refinement**: [Measurement process improvement]
            - **Full Operation**: [Complete system deployment]
            
            #### Governance Structure
            **Measurement Governance Committee:**
            - **Charter**: [Committee purpose and authority]
            - **Membership**: [Committee composition and roles]
            - **Responsibilities**: [Oversight and decision-making duties]
            - **Meeting Schedule**: [Regular governance meetings]
            
            **Data Governance:**
            - **Data Ownership**: [Clear data ownership assignments]
            - **Quality Standards**: [Data quality requirements]
            - **Security Protocols**: [Data security and privacy measures]
            
            ## Success Enablers and Critical Factors
            
            ### Key Success Factors
            #### Leadership and Commitment
            - **Executive Sponsorship**: [Strong leadership support for measurement]
            - **Resource Commitment**: [Adequate resources for measurement system]
            - **Cultural Support**: [Organizational culture that values measurement]
            
            #### Technical Infrastructure
            - **System Capabilities**: [Robust measurement and reporting systems]
            - **Data Integration**: [Seamless data flow and integration]
            - **User Experience**: [Intuitive and user-friendly interfaces]
            
            #### Organizational Capabilities
            - **Analytical Skills**: [Capability to analyze and interpret data]
            - **Change Management**: [Ability to act on measurement insights]
            - **Communication**: [Effective communication of results and insights]
            
            ### Risk Mitigation for Measurement System
            #### Common Measurement Risks
            - **Data Quality Issues**: [Inaccurate or incomplete data]
            - **System Reliability**: [Technical failures and downtime]
            - **User Adoption**: [Resistance to using measurement system]
            
            #### Mitigation Strategies
            - **Quality Assurance**: [Robust data validation and verification]
            - **System Redundancy**: [Backup systems and procedures]
            - **Change Management**: [Comprehensive user adoption strategies]
            
            ## Conclusion and Next Steps
            
            ### Evaluation Framework Summary
            - **Comprehensive Coverage**: [Complete measurement of all critical aspects]
            - **Balanced Approach**: [Quantitative and qualitative measurement]
            - **Actionable Insights**: [Measurement that drives improvement]
            - **Sustainable System**: [Long-term measurement sustainability]
            
            ### Implementation Roadmap
            #### Immediate Actions (Next 30 days)
            1. **Finalize KPI Definitions**: [Complete KPI specification]
            2. **Establish Data Sources**: [Identify and secure data access]
            3. **Begin System Development**: [Start measurement system build]
            
            #### Short-term Actions (Next 90 days)
            1. **Deploy Measurement System**: [Implement monitoring infrastructure]
            2. **Train Stakeholders**: [Provide measurement system training]
            3. **Begin Data Collection**: [Start systematic data gathering]
            
            #### Long-term Actions (Next 12 months)
            1. **Optimize System Performance**: [Refine and improve measurement system]
            2. **Expand Analytics Capabilities**: [Enhance analytical functionality]
            3. **Institutionalize Learning**: [Embed continuous improvement culture]
            
            ### Expected Outcomes
            - **Informed Decision Making**: [Data-driven strategic decisions]
            - **Continuous Improvement**: [Ongoing performance enhancement]
            - **Stakeholder Confidence**: [Increased confidence through transparency]
            - **Organizational Learning**: [Enhanced organizational capabilities]
            """,
            markdown=True,
            agent = EvaluateAgent.create_agent(),
            output_file="evaluation_framework.md"
        )