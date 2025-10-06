from crewai import Agent
from tools.custom_tools import CodeInterpreterTool
from config import config
import streamlit as st

class DecisionMultidisciplinaryAgent:
    """Agent for integrated multidisciplinary feasibility analysis"""
    
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
            role="Multidisciplinary Feasibility Analyst",
            goal="Conduct comprehensive feasibility analysis across technology, legal, finance, market, communication, and behavioral dimensions",
            backstory="""You are a senior consultant with expertise across multiple disciplines including
            technology assessment, legal compliance, financial analysis, market research, strategic
            communication, and behavioral psychology. Your role is to provide integrated feasibility
            analysis that considers all critical dimensions of strategic initiatives. You excel at
            identifying interdependencies between different domains and providing holistic risk assessments.
            
            CRITICAL: For every decision, recommendation, or conclusion you make, you MUST provide clear
            reasoning and justification. Always explain WHY you reached a particular decision, what factors
            influenced your judgment, what evidence or analysis supports your conclusion, and what alternatives
            you considered. Your decision-making process should be transparent and well-documented to build
            stakeholder confidence and enable informed strategic choices.""",
            tools=[
                CodeInterpreterTool()
            ],
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE,
            llm=llm
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

DECISION-MAKING REQUIREMENTS:
- For EVERY decision, recommendation, assessment, or conclusion you make, provide explicit reasoning
- Explain WHY you reached each decision and what factors influenced your judgment
- Document what evidence or analysis supports your conclusions
- Mention what alternatives you considered and why you chose the recommended path
- Make your decision-making process transparent and traceable

Analysis Dimensions:
1. **Technology Feasibility**
   - Technical requirements and capabilities
   - Infrastructure needs and constraints
   - Technology risks and mitigation strategies
   - DECISION REASONING: Explain why you assess the technology as feasible/not feasible

2. **Legal and Regulatory Analysis**
   - Compliance requirements and regulations
   - Legal risks and liability considerations
   - Regulatory approval processes
   - DECISION REASONING: Justify your legal risk assessments and compliance recommendations

3. **Financial Feasibility**
   - Cost-benefit analysis framework
   - Resource requirements and budget implications
   - ROI projections and financial risks
   - DECISION REASONING: Explain your financial viability conclusions and investment recommendations

4. **Market Analysis**
   - Market conditions and competitive landscape
   - Target audience and stakeholder analysis
   - Market entry barriers and opportunities
   - DECISION REASONING: Justify your market opportunity assessments and strategic recommendations

5. **Communication Strategy**
   - Stakeholder communication requirements
   - Change management considerations
   - Internal and external messaging needs
   - DECISION REASONING: Explain your communication strategy choices and approach rationale

6. **Behavioral and Cultural Factors**
   - User adoption challenges
   - Organizational culture impact
   - Behavioral change requirements
   - DECISION REASONING: Justify your behavioral assessments and adoption strategy recommendations

Provide integrated analysis with cross-dimensional risk assessment and recommendations, ensuring every decision includes clear justification.
"""
            ),
            expected_output=(
                """
A comprehensive multidisciplinary feasibility report in PDF/Markdown format containing:

# Multidisciplinary Feasibility Analysis

## Executive Summary
- Include decision rationale summary for all key recommendations

## Technology Feasibility Assessment
- **Decision Reasoning**: Explain why the technology is assessed as feasible/not feasible, what evidence supports this conclusion, and what alternatives were considered

## Legal and Regulatory Analysis
   - Liability considerations
   - Intellectual property issues
   - Contract and partnership implications
   - **Decision Reasoning**: Justify legal risk assessments and explain why certain compliance approaches are recommended
   ### Compliance Strategy
   - Required legal preparations
   - Ongoing compliance monitoring
   - Legal risk mitigation plans
   - **Decision Reasoning**: Explain why this compliance strategy is optimal given the circumstances

## Financial Feasibility
   ### Investment Requirements
   - Initial capital needs
   - Ongoing operational costs
   - Resource allocation recommendations
   - **Decision Reasoning**: Justify investment recommendations and explain cost estimation methodology
   ### Financial Projections
   - Revenue/benefit projections
   - Cost structure analysis
   - Break-even analysis
   - **Decision Reasoning**: Explain assumptions behind projections and why they are realistic
   ### Financial Risks
   - Budget overrun risks
   - Revenue shortfall scenarios
   - Financial contingency plans
   - **Decision Reasoning**: Justify risk assessments and explain contingency plan choices

## Market Analysis
   ### Market Environment
   - Industry trends and dynamics
   - Competitive positioning
   - Market opportunity assessment
   - **Decision Reasoning**: Explain market opportunity conclusions and competitive positioning rationale
   ### Stakeholder Analysis
   - Key stakeholder groups
   - Stakeholder interests and concerns
   - Influence and impact mapping
   - **Decision Reasoning**: Justify stakeholder prioritization and engagement strategy choices
   ### Market Entry Strategy
   - Go-to-market considerations
   - Competitive advantages
   - Market penetration approach
   - **Decision Reasoning**: Explain why this market entry strategy is recommended over alternatives

## Communication Strategy
   ### Communication Requirements
   - Internal communication needs
   - External messaging strategy
   - Stakeholder engagement plan
   - **Decision Reasoning**: Justify communication approach and explain channel selection rationale
   ### Change Management
   - Organizational readiness assessment
   - Change resistance factors
   - Communication timeline and channels
   - **Decision Reasoning**: Explain change management strategy choices and timeline rationale

## Behavioral and Cultural Factors
   ### User Adoption Factors
   - Adoption barriers and drivers
   - User experience considerations
   - Training and support needs
   - **Decision Reasoning**: Justify adoption strategy and explain why certain interventions are prioritized
   ### Organizational Impact
   - Cultural alignment assessment
   - Workflow and process changes
   - Employee impact analysis
   - **Decision Reasoning**: Explain organizational impact assessments and mitigation strategy choices

## Integrated Risk Assessment
   ### Cross-Dimensional Risks
   - Interdependent risk factors
   - Cascading risk scenarios
   - Risk interaction matrix
   - **Decision Reasoning**: Explain risk prioritization methodology and interaction analysis
   ### Risk Prioritization
   - High-impact, high-probability risks
   - Risk mitigation priorities
   - Contingency planning needs
   - **Decision Reasoning**: Justify risk ranking and explain mitigation strategy selections

## Strategic Recommendations
   ### Feasibility Conclusion
   - Overall feasibility rating with justification
   - Go/No-Go recommendation
   - Conditional approval scenarios
   - **CRITICAL DECISION REASONING**: Provide comprehensive justification for the final feasibility recommendation, explaining all factors considered, alternatives evaluated, and why this conclusion is the most appropriate given the analysis
   ### Success Factors
   - Critical elements for success
   - Key performance indicators
   - Success measurement framework
   - **Decision Reasoning**: Explain why these success factors are critical and how KPIs were selected
   ### Next Steps
   - Immediate action items
   - Preparation requirements
   - Decision timeline recommendations
   - **Decision Reasoning**: Justify action item prioritization and timeline recommendations

## Decision Audit Trail
   ### Key Decisions Made
   - List all major decisions and recommendations made in this analysis
   ### Decision Rationale Summary
   - For each key decision, provide a concise explanation of the reasoning
   ### Alternative Considerations
   - Document what alternatives were considered for major decisions
   ### Supporting Evidence
   - Reference the evidence and analysis that supports each key decision
"""
            ),
            agent=DecisionMultidisciplinaryAgent.create_agent(),
            markdown=True,
            output_file="feasibility_report.md"
        )
