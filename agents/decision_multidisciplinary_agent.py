from crewai import Agent
from tools.custom_tools import CodeInterpreterTool
from config import config

class DecisionMultidisciplinaryAgent:
    """Agent for integrated multidisciplinary feasibility analysis"""
    
    @staticmethod
    def create_agent():
        return Agent(
            role="Multidisciplinary Feasibility Analyst",
            goal="Conduct comprehensive feasibility analysis across technology, legal, finance, market, communication, and behavioral dimensions",
            backstory="""You are a senior consultant with expertise across multiple disciplines including
            technology assessment, legal compliance, financial analysis, market research, strategic
            communication, and behavioral psychology. Your role is to provide integrated feasibility
            analysis that considers all critical dimensions of strategic initiatives. You excel at
            identifying interdependencies between different domains and providing holistic risk assessments.""",
            tools=[
                CodeInterpreterTool()
            ],
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE
        )
    
    @staticmethod
    def create_task(context_data: str):
        from crewai import Task
        return Task(
            description=(
                f"""
Conduct a comprehensive multidisciplinary feasibility analysis based on the processed documents and context.

Available Context:
{context_data}

Analysis Dimensions:
1. **Technology Feasibility**
   - Technical requirements and capabilities
   - Infrastructure needs and constraints
   - Technology risks and mitigation strategies

2. **Legal and Regulatory Analysis**
   - Compliance requirements and regulations
   - Legal risks and liability considerations
   - Regulatory approval processes

3. **Financial Feasibility**
   - Cost-benefit analysis framework
   - Resource requirements and budget implications
   - ROI projections and financial risks

4. **Market Analysis**
   - Market conditions and competitive landscape
   - Target audience and stakeholder analysis
   - Market entry barriers and opportunities

5. **Communication Strategy**
   - Stakeholder communication requirements
   - Change management considerations
   - Internal and external messaging needs

6. **Behavioral and Cultural Factors**
   - User adoption challenges
   - Organizational culture impact
   - Behavioral change requirements

Provide integrated analysis with cross-dimensional risk assessment and recommendations.
"""
            ),
            expected_output=(
                """
A comprehensive multidisciplinary feasibility report in PDF/Markdown format containing:

# Multidisciplinary Feasibility Analysis

## Executive Summary

## Technology Feasibility Assessment

## Legal and Regulatory Analysis
   - Liability considerations
   - Intellectual property issues
   - Contract and partnership implications
   ### Compliance Strategy
   - Required legal preparations
   - Ongoing compliance monitoring
   - Legal risk mitigation plans

## Financial Feasibility
   ### Investment Requirements
   - Initial capital needs
   - Ongoing operational costs
   - Resource allocation recommendations
   ### Financial Projections
   - Revenue/benefit projections
   - Cost structure analysis
   - Break-even analysis
   ### Financial Risks
   - Budget overrun risks
   - Revenue shortfall scenarios
   - Financial contingency plans

## Market Analysis
   ### Market Environment
   - Industry trends and dynamics
   - Competitive positioning
   - Market opportunity assessment
   ### Stakeholder Analysis
   - Key stakeholder groups
   - Stakeholder interests and concerns
   - Influence and impact mapping
   ### Market Entry Strategy
   - Go-to-market considerations
   - Competitive advantages
   - Market penetration approach

## Communication Strategy
   ### Communication Requirements
   - Internal communication needs
   - External messaging strategy
   - Stakeholder engagement plan
   ### Change Management
   - Organizational readiness assessment
   - Change resistance factors
   - Communication timeline and channels

## Behavioral and Cultural Factors
   ### User Adoption Factors
   - Adoption barriers and drivers
   - User experience considerations
   - Training and support needs
   ### Organizational Impact
   - Cultural alignment assessment
   - Workflow and process changes
   - Employee impact analysis

## Integrated Risk Assessment
   ### Cross-Dimensional Risks
   - Interdependent risk factors
   - Cascading risk scenarios
   - Risk interaction matrix
   ### Risk Prioritization
   - High-impact, high-probability risks
   - Risk mitigation priorities
   - Contingency planning needs

## Strategic Recommendations
   ### Feasibility Conclusion
   - Overall feasibility rating with justification
   - Go/No-Go recommendation
   - Conditional approval scenarios
   ### Success Factors
   - Critical elements for success
   - Key performance indicators
   - Success measurement framework
   ### Next Steps
   - Immediate action items
   - Preparation requirements
   - Decision timeline recommendations
"""
            ),
            agent=DecisionMultidisciplinaryAgent.create_agent(),
            markdown=True,
            output_file="feasibility_report.md"
        )
