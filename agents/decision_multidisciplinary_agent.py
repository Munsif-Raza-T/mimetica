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
            goal="Conduct comprehensive feasibility analysis across technology, legal, finance, market, communication, and behavioral dimensions with context-aware assessment",
            backstory="""You are a senior consultant with expertise across multiple disciplines including
            technology assessment, legal compliance, financial analysis, market research, strategic
            communication, and behavioral psychology. Your role is to provide integrated feasibility
            analysis that considers all critical dimensions of strategic initiatives. You excel at
            identifying interdependencies between different domains and providing holistic risk assessments.
            
            CRITICAL: Your analysis must be contextually appropriate to the problem domain:
            For market studies: emphasize market viability, competitive positioning, customer validation.
            For customer experience: focus on user adoption, experience design feasibility, service delivery capability.
            For ROI/financial optimization: prioritize financial viability, cost-benefit analysis, investment justification.
            For digital transformation: balance technical feasibility with organizational readiness and change management.
            For operational improvements: assess process feasibility, resource requirements, operational impact.
            
            DECISION-MAKING REQUIREMENTS:
            For EVERY decision, recommendation, or conclusion you make, you MUST provide clear reasoning that is
            contextually appropriate to the problem domain. Always explain WHY you reached a particular decision
            within the specific context, what domain-relevant factors influenced your judgment, what evidence or
            analysis supports your conclusion, and what alternatives you considered within the problem space.
            Your decision-making process should be transparent, well-documented, and contextually informed to
            build stakeholder confidence and enable domain-appropriate strategic choices.""",
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
CRITICAL INSTRUCTION: Analyze the provided context to identify the problem domain and conduct contextually appropriate feasibility analysis.

Available Context:
{context_data}

CONTEXT ANALYSIS REQUIREMENT:
First, identify the problem domain from the available context:
- MARKET STUDY indicators: "market research", "competitive analysis", "market positioning", "customer segments"
- CUSTOMER EXPERIENCE indicators: "customer journey", "user experience", "customer satisfaction", "service quality"
- FINANCIAL/ROI indicators: "ROI", "cost reduction", "revenue optimization", "profitability", "financial performance"
- DIGITAL TRANSFORMATION indicators: "digital adoption", "technology implementation", "automation", "digital capabilities"
- OPERATIONAL indicators: "process improvement", "efficiency", "workflow", "operational excellence", "productivity"

DOMAIN-SPECIFIC FEASIBILITY ANALYSIS:
Based on the identified domain, conduct feasibility analysis with appropriate emphasis:

FOR MARKET STUDIES - Emphasize:
1. **Market Viability Assessment**: Market size, growth potential, competitive landscape, customer demand validation
2. **Competitive Positioning Feasibility**: Differentiation potential, competitive advantages, market entry barriers
3. **Customer Validation**: Target segment validation, value proposition testing, customer acquisition feasibility
4. **Go-to-Market Feasibility**: Channel viability, marketing approach effectiveness, sales process feasibility

FOR CUSTOMER EXPERIENCE - Focus on:
1. **Experience Design Feasibility**: Journey mapping viability, touchpoint optimization potential, service design capability
2. **User Adoption Assessment**: Adoption barriers, user readiness, experience change management
3. **Service Delivery Capability**: Operational capacity, service quality standards, delivery channel effectiveness
4. **Experience Measurement**: Customer feedback systems, experience metrics, continuous improvement capability

FOR FINANCIAL/ROI - Prioritize:
1. **Financial Viability**: Cost-benefit analysis, ROI projections, payback period, financial risk assessment
2. **Investment Justification**: Capital requirements, funding sources, financial sustainability, value creation
3. **Cost Management**: Cost structure optimization, expense control, efficiency improvements
4. **Revenue Enhancement**: Revenue model viability, pricing strategy, monetization opportunities

FOR DIGITAL TRANSFORMATION - Balance:
1. **Technical Feasibility**: Technology capability, infrastructure readiness, integration complexity, scalability
2. **Organizational Readiness**: Digital maturity, change capacity, skill gaps, cultural alignment
3. **Implementation Feasibility**: Rollout strategy, training requirements, adoption timeline, success factors
4. **Value Realization**: Digital ROI, capability enhancement, competitive advantage, performance improvement

FOR OPERATIONAL IMPROVEMENTS - Assess:
1. **Process Feasibility**: Process redesign potential, workflow optimization, automation opportunities
2. **Resource Capability**: Capacity requirements, skill availability, infrastructure needs, investment requirements
3. **Operational Impact**: Performance improvement potential, efficiency gains, quality enhancement
4. **Change Management**: Implementation readiness, stakeholder buy-in, transition planning, risk mitigation

DECISION-MAKING REQUIREMENTS:
- For EVERY decision, recommendation, assessment, or conclusion, provide explicit reasoning that is contextually appropriate
- Explain WHY you reached each decision within the specific problem domain
- Document what domain-relevant evidence or analysis supports your conclusions
- Mention what alternatives you considered within the problem context and why you chose the recommended path
- Make your decision-making process transparent, traceable, and contextually informed

Analysis Dimensions (Adapted to Context):
1. **Technology Feasibility** (Context-Adapted)
   - Technical requirements and capabilities relevant to the domain
   - Infrastructure needs and constraints specific to the context
   - Technology risks and mitigation strategies appropriate to the domain
   - DECISION REASONING: Explain why you assess the technology as feasible/not feasible within this specific context

2. **Legal and Regulatory Analysis** (Domain-Specific)
   - Compliance requirements and regulations relevant to the problem domain
   - Legal risks and liability considerations specific to the context
   - Regulatory approval processes applicable to the domain
   - DECISION REASONING: Justify your legal risk assessments with domain-specific compliance considerations

3. **Financial Feasibility** (Context-Appropriate)
   - Cost-benefit analysis framework suitable for the domain
   - Resource requirements and budget implications specific to the context
   - ROI projections and financial risks relevant to the problem type
   - DECISION REASONING: Explain your financial viability conclusions with domain-appropriate investment reasoning

4. **Market Analysis** (Domain-Focused)
   - Market conditions and competitive landscape specific to the context
   - Target audience and stakeholder analysis relevant to the domain
   - Market entry barriers and opportunities within the problem space
   - DECISION REASONING: Justify your market opportunity assessments with context-specific strategic reasoning

5. **Communication Strategy** (Context-Sensitive)
   - Stakeholder communication requirements specific to the domain
   - Change management considerations appropriate to the context
   - Internal and external messaging needs relevant to the problem type
   - DECISION REASONING: Explain your communication strategy choices with domain-appropriate rationale

6. **Behavioral and Cultural Factors** (Domain-Relevant)
   - User adoption challenges specific to the context
   - Organizational culture impact relevant to the domain
   - Behavioral change requirements appropriate to the problem type
   - DECISION REASONING: Justify your behavioral assessments with context-specific adoption considerations

Provide integrated analysis with cross-dimensional risk assessment and recommendations, ensuring every decision includes clear justification that is contextually appropriate to the identified problem domain.
"""
            ),
            expected_output=(
                """
A comprehensive multidisciplinary feasibility report in PDF/Markdown format containing:

# Multidisciplinary Feasibility Analysis

## Executive Summary
- **Problem Domain Identified**: [Market Study/Customer Experience/Financial-ROI/Digital Transformation/Operational]
- **Feasibility Assessment Approach**: [How analysis was tailored to the domain context]
- **Overall Feasibility Rating**: [Feasible/Conditionally Feasible/Not Feasible with domain-specific reasoning]
- **Critical Success Factors**: [Domain-appropriate factors for success]
- **Key Risks**: [Highest priority risks specific to the context]
- **Recommended Action**: [Go/No-Go/Conditional with contextual justification]
- **Decision Rationale Summary**: [High-level reasoning for all key recommendations]

## Problem Context and Domain Analysis
### Domain Identification
- **Primary Domain**: [Identified problem domain with supporting evidence]
- **Context Characteristics**: [Key features that define this problem space]
- **Domain-Specific Requirements**: [Unique considerations for this context]
- **Success Criteria**: [Domain-appropriate metrics and outcomes]

### Feasibility Framework Adaptation
- **Analysis Approach**: [How feasibility assessment was tailored to the domain]
- **Evaluation Criteria**: [Domain-specific criteria used for assessment]
- **Risk Framework**: [Context-appropriate risk assessment methodology]
- **Decision Framework**: [Domain-relevant decision-making criteria]

## Technology Feasibility Assessment (Context-Adapted)

FOR MARKET STUDIES:
### Market Research Technology Capability
- **Data Collection Technology**: [Feasibility of research tools and platforms]
- **Analytics Capability**: [Market analysis and competitive intelligence tools]
- **Integration Requirements**: [Technology integration with existing market research systems]
- **DECISION REASONING**: [Why market research technology is assessed as feasible/not feasible for this specific market context]

FOR CUSTOMER EXPERIENCE:
### Experience Technology Platform
- **Customer Journey Technology**: [Journey mapping and analytics platforms]
- **Experience Measurement Tools**: [Customer feedback and satisfaction measurement systems]
- **Service Delivery Technology**: [Digital touchpoint and service channel capabilities]
- **DECISION REASONING**: [Why experience technology is viable/not viable for this specific customer context]

FOR FINANCIAL/ROI:
### Financial Technology Infrastructure
- **Financial Analytics Platform**: [Cost analysis and ROI measurement capabilities]
- **Performance Monitoring Tools**: [Financial tracking and reporting systems]
- **Integration Capability**: [Financial system integration requirements]
- **DECISION REASONING**: [Why financial technology approach is feasible/not feasible for this ROI context]

FOR DIGITAL TRANSFORMATION:
### Digital Platform Capability
- **Technology Infrastructure**: [Digital platform and integration capabilities]
- **Scalability Assessment**: [System performance and growth capacity]
- **Security and Compliance**: [Data protection and regulatory compliance capability]
- **DECISION REASONING**: [Why digital technology is ready/not ready for this transformation context]

FOR OPERATIONAL IMPROVEMENTS:
### Operational Technology Assessment
- **Process Technology**: [Workflow and process management capabilities]
- **Automation Potential**: [Process automation and efficiency technology]
- **Integration Requirements**: [Operational system integration needs]
- **DECISION REASONING**: [Why operational technology supports/doesn't support this improvement context]

## Legal and Regulatory Analysis (Domain-Specific)

### Context-Relevant Compliance Requirements
- **Domain-Specific Regulations**: [Laws and standards applicable to this problem context]
- **Compliance Complexity**: [Regulatory burden specific to the domain]
- **Legal Risk Assessment**: [Legal exposure relevant to the context]
- **DECISION REASONING**: [Why legal approach is compliant/non-compliant for this specific domain]

### Regulatory Strategy (Context-Appropriate)
- **Compliance Approach**: [Domain-specific regulatory strategy]
- **Risk Mitigation**: [Legal risk management for this context]
- **Ongoing Compliance**: [Regulatory monitoring needs for this domain]
- **DECISION REASONING**: [Why this compliance strategy is optimal for this specific context]

## Financial Feasibility (Domain-Focused)

### Investment Analysis (Context-Specific)
- **Domain-Appropriate Investment**: [Investment requirements specific to the problem context]
- **Cost Structure**: [Cost patterns typical for this domain]
- **Funding Strategy**: [Financing approach suitable for this context]
- **DECISION REASONING**: [Why investment is justified/not justified for this specific domain context]

### Financial Projections (Context-Relevant)
- **Domain-Specific ROI**: [Return expectations appropriate to the problem context]
- **Financial Metrics**: [Performance indicators relevant to the domain]
- **Risk Assessment**: [Financial risks specific to the context]
- **DECISION REASONING**: [Why financial projections are realistic/unrealistic for this domain]

### Financial Strategy (Domain-Appropriate)
- **Resource Allocation**: [Financial resource strategy for this context]
- **Performance Monitoring**: [Financial tracking approach for this domain]
- **Contingency Planning**: [Financial risk management for this context]
- **DECISION REASONING**: [Why financial strategy is sound/unsound for this specific situation]

## Market Analysis (Context-Focused)

### Market Viability (Domain-Specific)
- **Market Context Assessment**: [Market conditions relevant to the specific domain]
- **Competitive Landscape**: [Competition analysis specific to the problem context]
- **Market Opportunity**: [Opportunities within the relevant domain]
- **DECISION REASONING**: [Why market opportunity is viable/not viable for this specific context]

### Stakeholder Analysis (Context-Relevant)
- **Domain-Specific Stakeholders**: [Key stakeholders relevant to this problem context]
- **Stakeholder Dynamics**: [Influence patterns specific to the domain]
- **Engagement Strategy**: [Stakeholder management approach for this context]
- **DECISION REASONING**: [Why stakeholder strategy is effective/ineffective for this domain]

### Market Strategy (Domain-Appropriate)
- **Go-to-Market Approach**: [Market entry strategy suitable for this context]
- **Positioning Strategy**: [Market positioning relevant to the domain]
- **Competitive Strategy**: [Competitive approach appropriate to the context]
- **DECISION REASONING**: [Why market strategy is suitable/unsuitable for this specific domain]

## Communication Strategy (Context-Sensitive)

### Domain-Appropriate Communication
- **Communication Framework**: [Communication approach tailored to the problem context]
- **Stakeholder Messaging**: [Messages relevant to the specific domain]
- **Channel Strategy**: [Communication channels appropriate to the context]
- **DECISION REASONING**: [Why communication approach is effective/ineffective for this domain]

### Change Management (Context-Specific)
- **Change Strategy**: [Change management approach for this specific context]
- **Resistance Management**: [Resistance handling specific to the domain]
- **Adoption Strategy**: [Adoption approach relevant to the problem context]
- **DECISION REASONING**: [Why change approach is suitable/unsuitable for this specific situation]

## Behavioral and Cultural Factors (Domain-Relevant)

### Adoption Feasibility (Context-Specific)
- **User Adoption**: [Adoption patterns relevant to this domain]
- **Behavioral Change**: [Change requirements specific to the context]
- **Cultural Alignment**: [Cultural factors affecting this domain]
- **DECISION REASONING**: [Why adoption is likely/unlikely in this specific context]

### Organizational Impact (Domain-Focused)
- **Cultural Readiness**: [Organizational preparedness for this domain]
- **Capability Requirements**: [Skills and capabilities needed for this context]
- **Change Capacity**: [Organizational change capability for this domain]
- **DECISION REASONING**: [Why organizational impact is manageable/unmanageable for this context]

## Integrated Risk Assessment (Context-Informed)

### Domain-Specific Risk Analysis
- **Context-Relevant Risks**: [Risks specific to the identified domain]
- **Risk Interactions**: [How risks compound within this context]
- **Mitigation Strategies**: [Risk management approaches for this domain]
- **DECISION REASONING**: [Why risk profile is acceptable/unacceptable for this context]

### Risk Prioritization (Domain-Appropriate)
| Risk Category | Domain Relevance | Probability | Impact | Priority | Mitigation Strategy |
|---------------|-----------------|-------------|---------|----------|-------------------|
| [Context Risk 1] | [High/Med/Low] | [H/M/L] | [H/M/L] | [1-10] | [Domain-specific approach] |
| [Context Risk 2] | [High/Med/Low] | [H/M/L] | [H/M/L] | [1-10] | [Domain-specific approach] |

## Strategic Recommendations (Context-Informed)

### Feasibility Conclusion (Domain-Specific)
- **Overall Assessment**: [Feasible/Conditionally Feasible/Not Feasible for this specific domain]
- **CRITICAL DECISION REASONING**: [Comprehensive justification for the feasibility recommendation within this domain context, explaining all domain-specific factors considered, alternatives evaluated within the context, and why this conclusion is most appropriate for this specific problem space]

### Context-Appropriate Success Factors
- **Domain-Specific Success Elements**: [Critical factors for success within this context]
- **Context-Relevant KPIs**: [Performance indicators appropriate to the domain]
- **Success Measurement**: [Measurement framework suitable for this context]
- **DECISION REASONING**: [Why these success factors are critical for this specific domain]

### Domain-Informed Next Steps
- **Immediate Actions**: [Next steps appropriate to the problem context]
- **Preparation Requirements**: [Preparation needs specific to the domain]
- **Decision Timeline**: [Timeline recommendations suitable for this context]
- **DECISION REASONING**: [Why these actions and timeline are appropriate for this specific domain]

## Decision Audit Trail (Context-Specific)

### Key Domain-Informed Decisions
- [List all major decisions made with domain context noted]

### Context-Appropriate Decision Rationale
- [For each decision, explain reasoning within the specific domain context]

### Domain-Relevant Alternative Considerations
- [Document alternatives considered within the problem context]

### Context-Specific Supporting Evidence
- [Reference evidence and analysis supporting decisions within the domain]
"""
            ),
            agent=DecisionMultidisciplinaryAgent.create_agent(),
            markdown=True,
            output_file="feasibility_report.md"
        )
