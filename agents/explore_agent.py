from crewai import Agent
# Using AdvancedPineconeVectorSearchTool for document search and serper_search_tool for web research
from tools.custom_tools import AdvancedPineconeVectorSearchTool, serper_search_tool
from config import config

class ExploreAgent:
    """Agent responsible for contextual research and risk mapping"""
    
    @staticmethod
    def create_agent():
        return Agent(
            role="Strategic Research and Risk Analysis Specialist",
            goal="Conduct comprehensive contextual research and create detailed risk mapping for strategic initiatives",
            backstory="""You are a senior research analyst and risk management expert with deep experience 
            in strategic intelligence gathering, market research, and comprehensive risk assessment. You excel 
            at synthesizing information from multiple sources to create actionable insights and developing 
            sophisticated risk mapping frameworks. Your expertise includes competitive analysis, trend analysis, 
            and predictive risk modeling.""",
            tools=[
                AdvancedPineconeVectorSearchTool(),
                serper_search_tool
            ],
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE
        )
    
    @staticmethod
    def create_task(problem_definition: str, available_context: str):
        from crewai import Task
        return Task(
            description = f"""
            Conduct comprehensive contextual research and risk mapping based on the defined problem and objectives.
            
            Problem Definition:
            {problem_definition}
            
            Available Context:
            {available_context}
            
            Research Areas:
            1. **Contextual Analysis**
               - Industry trends and market dynamics
               - Competitive landscape assessment
               - Best practices and case studies
               - Regulatory and environmental factors
               
            2. **Stakeholder Research**
               - Stakeholder behavior patterns
               - Influence networks and relationships
               - Communication preferences
               - Resistance and adoption factors
               
            3. **Risk Identification and Mapping**
               - Strategic risks and business risks
               - Operational and technical risks
               - Financial and market risks
               - Reputational and compliance risks
               
            4. **Opportunity Analysis**
               - Market opportunities and gaps
               - Technology advancement opportunities
               - Partnership and collaboration possibilities
               - Innovation and differentiation potential
               
            5. **Environmental Scanning**
               - Economic factors and projections
               - Social and cultural trends
               - Technology disruption potential
               - Political and regulatory changes
            
            Create comprehensive research findings with detailed risk mapping and strategic insights.
            """,
         expected_output = """A comprehensive context analysis and risk mapping report containing:
            
            # Strategic Context Analysis and Risk Mapping
            
            ## Executive Summary
            - **Research Scope**: [Overview of research conducted]
            - **Key Findings**: [Top 5 strategic insights]
            - **Critical Risk Areas**: [Highest priority risks identified]
            - **Strategic Opportunities**: [Most promising opportunities]
            - **Recommended Focus Areas**: [Priority areas for intervention]
            
            ## Contextual Research Findings
            
            ### Industry and Market Context
            #### Industry Overview
            - **Market Size and Growth**: [Current market characteristics]
            - **Industry Trends**: [Key trends affecting the sector]
            - **Market Dynamics**: [Supply/demand factors, pricing trends]
            - **Growth Drivers**: [Factors driving industry expansion]
            - **Market Challenges**: [Industry-wide obstacles and constraints]
            
            #### Competitive Landscape
            - **Key Competitors**: [Major players and their positioning]
            - **Competitive Advantages**: [Differentiating factors in market]
            - **Market Share Distribution**: [Competitive positioning analysis]
            - **Competitive Threats**: [Emerging competition and disruptions]
            - **White Space Opportunities**: [Underserved market segments]
            
            #### Best Practices and Case Studies
            - **Successful Implementations**: [Relevant success stories]
            - **Lessons Learned**: [Key insights from similar initiatives]
            - **Innovation Examples**: [Creative approaches and solutions]
            - **Failure Analysis**: [Common pitfalls and how to avoid them]
            
            ### Stakeholder Context Analysis
            #### Stakeholder Behavior Patterns
            - **Decision-Making Processes**: [How stakeholders make decisions]
            - **Communication Preferences**: [Preferred channels and formats]
            - **Influence Networks**: [Key relationships and dependencies]
            - **Motivation Factors**: [What drives stakeholder behavior]
            
            #### Adoption and Resistance Factors
            - **Adoption Drivers**: [Factors encouraging acceptance]
            - **Resistance Sources**: [Common objections and concerns]
            - **Change Readiness**: [Stakeholder preparedness for change]
            - **Influence Strategies**: [Effective persuasion approaches]
            
            ### Regulatory and Environmental Context
            #### Regulatory Environment
            - **Current Regulations**: [Applicable laws and standards]
            - **Regulatory Trends**: [Anticipated changes and updates]
            - **Compliance Requirements**: [Mandatory obligations]
            - **Regulatory Risks**: [Potential compliance challenges]
            
            #### Environmental Factors
            - **Economic Environment**: [Economic conditions and projections]
            - **Social Trends**: [Demographic and cultural shifts]
            - **Technology Environment**: [Technical capabilities and trends]
            - **Political Context**: [Political stability and policy directions]
            
            ## Comprehensive Risk Mapping
            
            ### Risk Identification Framework
            #### Strategic Risks
            1. **Market Risk**: [Market condition changes, competitive threats]
               - **Risk Level**: [High/Medium/Low]
               - **Probability**: [Likelihood of occurrence]
               - **Impact**: [Severity of consequences]
               - **Time Horizon**: [When risk might materialize]
            
            2. **Strategic Misalignment Risk**: [Objective conflicts, priority changes]
            3. **Resource Allocation Risk**: [Inadequate or misdirected resources]
            4. **Stakeholder Risk**: [Stakeholder opposition or disengagement]
            
            #### Operational Risks
            1. **Execution Risk**: [Implementation challenges and delays]
            2. **Quality Risk**: [Deliverable quality and standards]
            3. **Process Risk**: [Workflow and operational disruptions]
            4. **Integration Risk**: [System and process integration challenges]
            
            #### Financial Risks
            1. **Budget Overrun Risk**: [Cost escalation scenarios]
            2. **Revenue Risk**: [Revenue shortfall possibilities]
            3. **ROI Risk**: [Return on investment uncertainty]
            4. **Funding Risk**: [Resource availability challenges]
            
            #### Technology Risks
            1. **Technical Feasibility Risk**: [Technology capability limitations]
            2. **Security Risk**: [Cybersecurity and data protection]
            3. **Scalability Risk**: [System performance under load]
            4. **Integration Risk**: [Technology compatibility issues]
            
            #### Compliance and Legal Risks
            1. **Regulatory Compliance Risk**: [Regulatory violation potential]
            2. **Legal Liability Risk**: [Legal exposure and litigation]
            3. **Privacy Risk**: [Data privacy and protection issues]
            4. **Intellectual Property Risk**: [IP infringement concerns]
            
            #### Reputational Risks
            1. **Brand Risk**: [Brand image and reputation impact]
            2. **Stakeholder Confidence Risk**: [Trust and credibility issues]
            3. **Public Relations Risk**: [Negative publicity potential]
            4. **Market Perception Risk**: [Market reaction and sentiment]
            
            ### Risk Interaction Analysis
            #### Risk Dependencies
            - **Cascading Risks**: [How risks trigger other risks]
            - **Compound Risks**: [Risks that amplify each other]
            - **Risk Clusters**: [Related risk groups]
            
            #### Risk Scenarios
            - **Best Case Scenario**: [Minimal risk materialization]
            - **Moderate Risk Scenario**: [Typical risk environment]
            - **High Risk Scenario**: [Multiple risk materialization]
            - **Crisis Scenario**: [Extreme risk conditions]
            
            ### Risk Prioritization Matrix
            | Risk Category | Probability | Impact | Priority Score | Mitigation Urgency |
            |---------------|-------------|---------|----------------|-------------------|
            | [Risk 1] | [H/M/L] | [H/M/L] | [1-10] | [High/Medium/Low] |
            | [Risk 2] | [H/M/L] | [H/M/L] | [1-10] | [High/Medium/Low] |
            
            ## Strategic Opportunities Analysis
            
            ### Market Opportunities
            - **Market Gaps**: [Unserved or underserved segments]
            - **Emerging Markets**: [New market development potential]
            - **Technology Opportunities**: [Technology-enabled advantages]
            - **Partnership Opportunities**: [Strategic collaboration potential]
            
            ### Innovation Opportunities
            - **Process Innovation**: [Operational improvement possibilities]
            - **Product/Service Innovation**: [New offering development]
            - **Business Model Innovation**: [Revenue model opportunities]
            - **Technology Innovation**: [Technical advancement applications]
            
            ### Competitive Opportunities
            - **Competitive Gaps**: [Competitor weaknesses to exploit]
            - **First Mover Advantages**: [Early market entry benefits]
            - **Differentiation Opportunities**: [Unique positioning potential]
            - **Market Share Opportunities**: [Share capture possibilities]
            
            ## Strategic Insights and Recommendations
            
            ### Key Strategic Insights
            1. **Market Insight**: [Critical market understanding]
            2. **Competitive Insight**: [Competitive advantage opportunities]
            3. **Risk Insight**: [Critical risk management priorities]
            4. **Stakeholder Insight**: [Key stakeholder management needs]
            5. **Opportunity Insight**: [Highest value opportunities]
            
            ### Research-Based Recommendations
            #### Immediate Actions (0-3 months)
            - [Urgent risk mitigation actions]
            - [Quick opportunity capture initiatives]
            - [Stakeholder engagement priorities]
            
            #### Short-term Actions (3-12 months)
            - [Strategic positioning moves]
            - [Risk management implementation]
            - [Market preparation activities]
            
            #### Long-term Considerations (12+ months)
            - [Strategic positioning for future]
            - [Long-term risk management]
            - [Market evolution preparation]
            
            ### Success Factors for Next Phase
            - **Critical Requirements**: [Must-have elements for success]
            - **Key Dependencies**: [Important relationships to manage]
            - **Risk Monitoring Needs**: [Ongoing risk surveillance requirements]
            - **Opportunity Watch Areas**: [Emerging opportunities to track]
            """,
            agent = ExploreAgent.create_agent(),
            markdown=True,
            output_file="context_analysis_and_risk_mapping_report.md"
        
        )
