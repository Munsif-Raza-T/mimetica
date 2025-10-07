from crewai import Agent
# Using AdvancedPineconeVectorSearchTool for document search and serper_search_tool for web research
from tools.custom_tools import AdvancedPineconeVectorSearchTool, serper_search_tool
from config import config
import streamlit as st

class ExploreAgent:
    """Agent responsible for contextual research and risk mapping"""
    
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
            role="Strategic Research and Risk Analysis Specialist",
            goal="Conduct comprehensive contextual research and create detailed risk mapping for strategic initiatives, adapting research focus based on problem domain",
            backstory="""You are a senior research analyst and risk management expert with deep experience 
            in strategic intelligence gathering, market research, and comprehensive risk assessment. You excel 
            at synthesizing information from multiple sources to create actionable insights and developing 
            sophisticated risk mapping frameworks. Your expertise includes competitive analysis, trend analysis, 
            and predictive risk modeling.
            
            CRITICAL: You must tailor your research approach based on the problem context:
            For market studies: emphasize competitive intelligence, industry analysis, customer behavior research.
            For customer experience: focus on journey analysis, touchpoint research, service delivery patterns.
            For ROI/financial optimization: prioritize financial benchmarking, cost analysis, revenue model research.
            For digital transformation: emphasize technology trends, capability gaps, digital maturity assessments.
            For operational challenges: focus on process benchmarking, efficiency studies, workflow analysis.
            
            Your research should provide domain-specific insights that directly inform strategic options rather than
            generic market overviews. Adapt your analysis depth and focus areas to match the problem domain.""",
            tools=[
                AdvancedPineconeVectorSearchTool(),
                serper_search_tool
            ],
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE,
            llm=llm
        )
    
    @staticmethod
    def create_task(problem_definition: str, available_context: str):
        from crewai import Task
        return Task(
            description = f"""
CRITICAL INSTRUCTION: Analyze the problem context to determine the appropriate research focus and adapt your analysis accordingly.

Problem Definition:
{problem_definition}

Available Context:
{available_context}

CONTEXT ANALYSIS REQUIREMENT:
First, identify the problem domain by analyzing the problem definition and context:
- MARKET STUDY indicators: "market research", "competitive analysis", "market positioning", "customer segments", "market entry"
- CUSTOMER EXPERIENCE indicators: "customer journey", "user experience", "customer satisfaction", "service quality", "touchpoints"  
- FINANCIAL/ROI indicators: "ROI", "cost reduction", "revenue optimization", "profitability", "financial performance"
- DIGITAL TRANSFORMATION indicators: "digital adoption", "technology implementation", "automation", "digital capabilities"
- OPERATIONAL indicators: "process improvement", "efficiency", "workflow", "operational excellence", "productivity"

Based on the identified domain, conduct targeted research in the following areas:

FOR MARKET STUDIES - Focus on:
1. **Competitive Intelligence**: Deep analysis of 3-5 key competitors, their strategies, positioning, and market share
2. **Customer Segmentation Research**: Detailed customer behavior patterns, preferences, and segment opportunities  
3. **Industry Dynamics**: Market size, growth trends, disruption factors, and emerging opportunities
4. **Positioning Analysis**: Value proposition gaps, differentiation opportunities, and competitive advantages

FOR CUSTOMER EXPERIENCE - Focus on:
1. **Journey Mapping Research**: Customer touchpoint analysis, pain point identification, and experience gaps
2. **Service Delivery Patterns**: Service quality benchmarks, delivery channel effectiveness, and improvement opportunities
3. **Customer Behavior Analysis**: Satisfaction drivers, loyalty factors, and experience expectations
4. **Experience Innovation**: Best practices in experience design and emerging experience trends

FOR FINANCIAL/ROI - Focus on:
1. **Financial Benchmarking**: Industry cost structures, profitability patterns, and performance metrics
2. **Revenue Model Analysis**: Revenue stream opportunities, pricing strategies, and monetization approaches
3. **Cost Structure Research**: Cost reduction opportunities, efficiency improvements, and resource optimization
4. **Investment Analysis**: ROI patterns, investment requirements, and financial risk assessment

FOR DIGITAL TRANSFORMATION - Focus on:
1. **Technology Landscape**: Digital trends, platform capabilities, and technology adoption patterns
2. **Digital Maturity Assessment**: Capability gaps, digital readiness, and transformation requirements
3. **Implementation Patterns**: Successful transformation strategies, common pitfalls, and best practices
4. **Change Management Research**: Digital adoption factors, resistance patterns, and engagement strategies

FOR OPERATIONAL IMPROVEMENTS - Focus on:
1. **Process Benchmarking**: Industry best practices, efficiency standards, and optimization opportunities
2. **Workflow Analysis**: Process bottlenecks, automation opportunities, and improvement potential
3. **Resource Optimization**: Capacity utilization, resource allocation, and productivity enhancement
4. **Performance Management**: KPI frameworks, measurement systems, and continuous improvement approaches

Research Areas (Adapted to Context):
1. **Domain-Specific Contextual Analysis**
   - Industry trends and dynamics relevant to the identified domain
   - Competitive landscape specific to the problem context
   - Best practices and case studies from the relevant domain
   - Regulatory and environmental factors affecting the specific context

2. **Targeted Stakeholder Research**
   - Stakeholder behavior patterns specific to the domain
   - Influence networks relevant to the problem context
   - Communication preferences typical for the domain
   - Resistance and adoption factors specific to the context

3. **Context-Specific Risk Identification**
   - Domain-relevant strategic and business risks
   - Context-specific operational and technical risks
   - Financial and market risks pertinent to the domain
   - Reputational and compliance risks relevant to the context

4. **Domain-Focused Opportunity Analysis**
   - Market opportunities specific to the identified context
   - Technology opportunities relevant to the domain
   - Partnership possibilities within the problem space
   - Innovation potential specific to the context

5. **Contextual Environmental Scanning**
   - Economic factors affecting the specific domain
   - Social and cultural trends relevant to the context
   - Technology disruption potential in the problem space
   - Political and regulatory changes affecting the domain

Create domain-specific research findings with detailed risk mapping and strategic insights tailored to the problem context.
""",
         expected_output = """A comprehensive context analysis and risk mapping report tailored to the identified problem domain:
            
            # Strategic Context Analysis and Risk Mapping

            ## Executive Summary
            - **Problem Domain Identified**: [Market Study/Customer Experience/Financial-ROI/Digital Transformation/Operational]
            - **Research Scope**: [Domain-specific research conducted]
            - **Key Findings**: [Top 5 strategic insights relevant to the domain]
            - **Critical Risk Areas**: [Highest priority risks specific to the context]
            - **Strategic Opportunities**: [Most promising opportunities within the domain]
            - **Recommended Focus Areas**: [Priority areas for intervention based on domain analysis]

            ## Domain-Specific Research Findings

            ### Problem Context Assessment
            #### Domain Identification
            - **Primary Domain**: [Identified problem domain with justification]
            - **Key Indicators**: [Specific elements that led to domain classification]
            - **Context Characteristics**: [Unique aspects of this problem space]
            - **Domain Boundaries**: [Scope and limitations of the identified context]

            #### Contextual Research Approach
            - **Research Framework**: [Domain-appropriate research methodology]
            - **Information Sources**: [Domain-relevant sources consulted]
            - **Analysis Methodology**: [Context-specific analysis approach]
            - **Validation Methods**: [How findings were validated for this domain]

            ### Industry and Market Context (Adapted to Domain)

            FOR MARKET STUDIES:
            #### Competitive Intelligence Analysis
            - **Competitor 1**: [Company name, market position, key strategies, strengths/weaknesses]
            - **Competitor 2**: [Company name, market position, key strategies, strengths/weaknesses]  
            - **Competitor 3**: [Company name, market position, key strategies, strengths/weaknesses]
            - **Competitive Gaps**: [Unserved market spaces and opportunities]
            - **Differentiation Opportunities**: [How to position uniquely in the market]

            #### Customer Segmentation Insights
            - **Primary Segments**: [Key customer groups with behaviors and preferences]
            - **Segment Opportunities**: [Underserved or emerging segments]
            - **Customer Journey Patterns**: [How customers navigate the market]
            - **Value Drivers**: [What customers prioritize in this market]

            FOR CUSTOMER EXPERIENCE:
            #### Experience Landscape Analysis
            - **Current Journey State**: [Existing customer journey characteristics]
            - **Experience Benchmarks**: [Industry standards for customer experience]
            - **Pain Point Analysis**: [Critical friction points in customer interactions]
            - **Experience Innovation**: [Emerging trends in customer experience design]

            #### Service Delivery Research
            - **Delivery Channel Analysis**: [Effectiveness of different service channels]
            - **Service Quality Standards**: [Industry benchmarks and expectations]
            - **Experience Gaps**: [Areas where current delivery falls short]
            - **Improvement Opportunities**: [Specific areas for experience enhancement]

            FOR FINANCIAL/ROI:
            #### Financial Landscape Analysis
            - **Industry Cost Structures**: [Typical cost patterns and benchmarks]
            - **Revenue Model Patterns**: [Common monetization approaches]
            - **Profitability Factors**: [Key drivers of financial performance]
            - **Investment Requirements**: [Typical investment levels and returns]

            #### Performance Benchmarking
            - **Financial Metrics**: [Key performance indicators and industry standards]
            - **Cost Optimization**: [Areas where costs can be reduced]
            - **Revenue Enhancement**: [Opportunities to increase revenue]
            - **ROI Patterns**: [Expected return profiles for similar initiatives]

            FOR DIGITAL TRANSFORMATION:
            #### Digital Maturity Landscape
            - **Technology Adoption**: [Current digital adoption patterns in relevant context]
            - **Digital Capabilities**: [Required capabilities and current gaps]
            - **Implementation Patterns**: [Successful digital transformation approaches]
            - **Technology Trends**: [Emerging technologies relevant to the context]

            #### Change Management Research
            - **Adoption Factors**: [What drives successful digital adoption]
            - **Resistance Patterns**: [Common barriers to digital transformation]
            - **Success Strategies**: [Proven approaches for digital change management]
            - **Capability Building**: [Skills and capabilities needed for success]

            FOR OPERATIONAL IMPROVEMENTS:
            #### Process Excellence Research
            - **Best Practice Analysis**: [Industry leading operational practices]
            - **Efficiency Benchmarks**: [Performance standards and metrics]
            - **Process Innovation**: [Emerging approaches to operational excellence]
            - **Optimization Opportunities**: [Specific areas for improvement]

            #### Resource Optimization Analysis
            - **Resource Utilization**: [Current patterns and optimization opportunities]
            - **Capacity Management**: [Approaches to capacity optimization]
            - **Productivity Enhancement**: [Methods to improve operational productivity]
            - **Performance Management**: [Systems for monitoring and improving performance]

            ### Domain-Specific Stakeholder Analysis
            #### Key Stakeholder Groups (Context-Relevant)
            - **Primary Stakeholders**: [Most important stakeholders for this domain]
            - **Influence Patterns**: [How stakeholders exert influence in this context]
            - **Decision Dynamics**: [How decisions are made in this domain]
            - **Engagement Requirements**: [What stakeholders expect and need]

            #### Stakeholder Behavior Patterns (Domain-Specific)
            - **Decision Processes**: [How stakeholders make decisions in this context]
            - **Communication Preferences**: [Preferred channels and formats for this domain]
            - **Motivation Factors**: [What drives stakeholder behavior in this context]
            - **Resistance Factors**: [Common sources of resistance in this domain]

            ### Regulatory and Environmental Context (Domain-Focused)
            #### Domain-Specific Regulatory Environment
            - **Relevant Regulations**: [Laws and standards applicable to this domain]
            - **Compliance Requirements**: [Specific obligations for this context]
            - **Regulatory Trends**: [Anticipated changes affecting this domain]
            - **Compliance Risks**: [Potential regulatory challenges]

            #### Environmental Factors (Context-Relevant)
            - **Economic Conditions**: [Economic factors affecting this domain]
            - **Social Trends**: [Demographic and cultural factors relevant to context]
            - **Technology Environment**: [Technical factors specific to this domain]
            - **Political Context**: [Political factors affecting this problem space]

            ## Context-Specific Risk Mapping

            ### Risk Framework (Adapted to Domain)
            #### Domain-Relevant Strategic Risks
            1. **[Domain-Specific Risk 1]**: [Description, probability, impact, time horizon]
            2. **[Domain-Specific Risk 2]**: [Description, probability, impact, time horizon]
            3. **[Domain-Specific Risk 3]**: [Description, probability, impact, time horizon]

            #### Context-Appropriate Operational Risks
            1. **[Context-Specific Risk 1]**: [Description, probability, impact, mitigation approach]
            2. **[Context-Specific Risk 2]**: [Description, probability, impact, mitigation approach]
            3. **[Context-Specific Risk 3]**: [Description, probability, impact, mitigation approach]

            #### Domain-Focused Financial Risks
            1. **[Financial Risk 1]**: [Description relevant to domain context]
            2. **[Financial Risk 2]**: [Description relevant to domain context]
            3. **[Financial Risk 3]**: [Description relevant to domain context]

            ### Risk Prioritization (Context-Sensitive)
            | Risk Category | Domain Relevance | Probability | Impact | Priority Score | Mitigation Urgency |
            |---------------|-----------------|-------------|---------|----------------|-------------------|
            | [Risk 1] | [High/Med/Low] | [H/M/L] | [H/M/L] | [1-10] | [High/Medium/Low] |
            | [Risk 2] | [High/Med/Low] | [H/M/L] | [H/M/L] | [1-10] | [High/Medium/Low] |

            ## Domain-Specific Opportunities Analysis

            ### Context-Relevant Market Opportunities
            - **[Opportunity 1]**: [Domain-specific opportunity description]
            - **[Opportunity 2]**: [Domain-specific opportunity description]
            - **[Opportunity 3]**: [Domain-specific opportunity description]

            ### Innovation Opportunities (Domain-Focused)
            - **[Innovation 1]**: [Context-appropriate innovation opportunity]
            - **[Innovation 2]**: [Context-appropriate innovation opportunity]
            - **[Innovation 3]**: [Context-appropriate innovation opportunity]

            ## Strategic Insights and Recommendations (Context-Informed)

            ### Key Strategic Insights (Domain-Specific)
            1. **[Domain Insight 1]**: [Critical understanding specific to the context]
            2. **[Domain Insight 2]**: [Important pattern relevant to the domain]
            3. **[Domain Insight 3]**: [Strategic opportunity unique to this context]
            4. **[Domain Insight 4]**: [Risk factor requiring attention in this domain]
            5. **[Domain Insight 5]**: [Success factor critical for this context]

            ### Context-Based Recommendations
            #### Immediate Actions (0-3 months) - Domain-Specific
            - [Urgent actions appropriate to the identified domain]
            - [Quick wins possible in this context]
            - [Stakeholder engagement priorities for this domain]

            #### Short-term Actions (3-12 months) - Context-Relevant
            - [Strategic moves suitable for this domain]
            - [Risk management specific to this context]
            - [Opportunity capture relevant to the domain]

            #### Long-term Considerations (12+ months) - Domain-Focused
            - [Strategic positioning for this domain's future]
            - [Long-term risk management for this context]
            - [Market evolution preparation specific to the domain]

            ### Success Factors for Next Phase (Context-Specific)
            - **Critical Requirements**: [Must-have elements for success in this domain]
            - **Key Dependencies**: [Important relationships to manage in this context]
            - **Risk Monitoring**: [Ongoing surveillance requirements for this domain]
            - **Opportunity Tracking**: [Emerging opportunities to watch in this context]
            """,
            agent = ExploreAgent.create_agent(),
            markdown=True,
            output_file="context_analysis_and_risk_mapping_report.md"
        
        )
