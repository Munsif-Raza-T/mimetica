from crewai import Agent
# No external tools needed for this agent
from config import config
import streamlit as st

class CreateAgent:
    """Agent responsible for creating intervention options and strategic alternatives"""
    
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
            role="Strategic Option Development Specialist",
            goal="Create multiple strategic intervention options with comprehensive analysis of pros, cons, and assumptions, adapting approach based on problem context",
            backstory="""You are a strategic planning expert and innovation consultant with extensive experience 
            in developing creative solutions and strategic alternatives. You excel at generating multiple viable 
            options for complex challenges, analyzing trade-offs, and presenting clear recommendations. Your 
            expertise includes option generation, scenario planning, and strategic decision analysis.
            
            CRITICAL: You must analyze the context of each problem to generate contextually appropriate solutions.
            For market studies: focus on competitive analysis, positioning, customer segmentation approaches.
            For customer experience: prioritize journey mapping, touchpoint optimization, service design.
            For ROI/financial optimization: emphasize revenue models, cost reduction, efficiency improvements.
            For digital transformation: balance technology adoption with change management and capability building.
            For operational challenges: focus on process optimization, resource allocation, workflow improvements.
            
            Avoid generic "general vs technical" categorizations. Instead, create meaningfully distinct approaches
            that reflect the specific nature and requirements of the problem domain.""",
            tools=[],
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE,
            llm=llm
        )
    
    @staticmethod
    def create_task(problem_definition: str, context_analysis: str):
        from crewai import Task
        return Task(
            description=f"""
CRITICAL INSTRUCTION: Before generating options, analyze the problem context to determine the appropriate solution approach.

Problem Definition:
{problem_definition}

Context and Risk Analysis:
{context_analysis}

CONTEXT ANALYSIS REQUIREMENT:
First, identify the problem domain by analyzing keywords and objectives:
- MARKET STUDY indicators: "market research", "competitive analysis", "market positioning", "customer segments", "market entry"
- CUSTOMER EXPERIENCE indicators: "customer journey", "user experience", "customer satisfaction", "service quality", "touchpoints"
- FINANCIAL/ROI indicators: "ROI", "cost reduction", "revenue optimization", "profitability", "financial performance"
- DIGITAL TRANSFORMATION indicators: "digital adoption", "technology implementation", "automation", "digital capabilities"
- OPERATIONAL indicators: "process improvement", "efficiency", "workflow", "operational excellence", "productivity"

Based on the identified domain, generate 2 distinct strategic options that are contextually appropriate:

FOR MARKET STUDIES - Generate options like:
• Comprehensive Competitive Intelligence Program vs. Customer-Centric Market Positioning Strategy
• Market Segmentation and Targeting Approach vs. Brand Differentiation and Value Proposition Strategy

FOR CUSTOMER EXPERIENCE - Generate options like:
• Journey Mapping and Touchpoint Optimization vs. Service Design and Experience Innovation
• Voice of Customer Program vs. Digital Experience Transformation

FOR FINANCIAL/ROI - Generate options like:
• Revenue Stream Diversification vs. Cost Structure Optimization
• Performance Analytics and KPI Framework vs. Investment Portfolio Rebalancing

FOR DIGITAL TRANSFORMATION - Generate options like:
• Phased Technology Adoption Strategy vs. Capability Building and Change Management Focus
• Data-Driven Decision Making Platform vs. Digital Skills Development Program

FOR OPERATIONAL IMPROVEMENTS - Generate options like:
• Process Automation and Workflow Optimization vs. Resource Allocation and Capacity Management
• Quality Management System vs. Performance Management and Continuous Improvement

Requirements:
1. **Contextual Option Generation**
   - Develop exactly 2 strategic intervention options that are specific to the identified problem domain
   - Ensure options address the core problem with domain-appropriate approaches
   - Avoid generic "general vs technological" categorizations
   - Create meaningfully distinct strategic approaches within the relevant domain

2. **Domain-Specific Analysis**
   - Tailor pros and cons to the specific problem context
   - Include domain-relevant resource requirements and investment needs
   - Assess implementation complexity based on problem type
   - Identify risks specific to the problem domain

3. **Contextual Assumptions Documentation**
   - Document assumptions that are relevant to the specific problem context
   - Include domain-specific dependencies and requirements
   - Identify success factors appropriate to the problem type
   - Consider constraints specific to the problem domain

4. **Comparative Assessment**
   - Compare options using criteria relevant to the problem context
   - Apply decision criteria that matter for the specific domain
   - Provide recommendation framework appropriate to the problem type
   - Offer selection guidance tailored to the specific context

5. **Implementation Considerations**
   - Suggest implementation approaches suitable for the problem domain
   - Identify resource and capability requirements specific to the context
   - Provide timeline considerations appropriate to the problem type
   - Assess success probability based on domain-specific factors

Create comprehensive option documentation that reflects deep understanding of the problem context and enables informed decision-making.
""",
            expected_output="""
A comprehensive intervention options document in Markdown/PDF format containing:

# Strategic Intervention Options Analysis

## Executive Summary
- **Problem Domain Identified**: [Market Study/Customer Experience/Financial-ROI/Digital Transformation/Operational]
- **Total Options Developed**: [Number of options]
- **Contextual Approach**: [How options were tailored to the specific problem domain]
- **Recommended Approach**: [Top recommendation with domain-specific rationale]
- **Decision Timeline**: [Recommended decision timeframe based on problem urgency]
- **Key Decision Factors**: [Domain-relevant selection criteria]

## Context Analysis and Domain Identification
### Problem Context Assessment
- **Primary Domain**: [Identified problem domain and reasoning]
- **Key Indicators**: [Specific keywords/objectives that led to domain identification]
- **Stakeholder Context**: [Primary stakeholders relevant to this domain]
- **Success Metrics**: [Domain-appropriate KPIs and success measures]

### Strategic Framework Selection
- **Approach Rationale**: [Why specific strategic frameworks were chosen for this domain]
- **Domain Best Practices**: [Relevant industry standards and proven approaches]
- **Contextual Constraints**: [Domain-specific limitations and considerations]
- **Opportunity Landscape**: [Domain-relevant opportunities and potential]

## Strategic Option 1: [Context-Specific Option Name]
### Overview
- [Detailed description tailored to the identified problem domain]

### Domain-Specific Benefits
- [Pros specifically relevant to the problem context]
- [Expected outcomes appropriate to the domain]
- [Strategic advantages within the problem space]

### Domain-Specific Challenges
- [Cons and risks specific to the problem context]
- [Implementation challenges relevant to the domain]
- [Resource constraints typical for this problem type]

### Contextual Assumptions
- [Assumptions specific to the identified problem domain]
- [Market/environmental factors relevant to the context]
- [Stakeholder behavior patterns typical for this domain]

### Implementation Approach
- [Domain-appropriate implementation methodology]
- [Sequencing and phases suitable for the problem type]
- [Resource allocation strategy for this context]
- [Success probability assessment based on domain factors]

## Strategic Option 2: [Context-Specific Option Name]
### Overview
- [Detailed description offering a meaningfully different approach within the same domain]

### Domain-Specific Benefits
- [Alternative benefits within the problem context]
- [Different value propositions for the same domain]
- [Complementary advantages to Option 1]

### Domain-Specific Challenges
- [Different risk profile within the same domain]
- [Alternative implementation challenges]
- [Trade-offs compared to Option 1]

### Contextual Assumptions
- [Different but domain-relevant assumptions]
- [Alternative success factors for the same context]
- [Different stakeholder engagement requirements]

### Implementation Approach
- [Alternative implementation strategy for the same domain]
- [Different resource and capability requirements]
- [Alternative timeline and sequencing]
- [Comparative success probability assessment]

## Contextual Comparative Assessment
### Domain-Relevant Criteria Comparison
| Criteria | Option 1 | Option 2 | Rationale |
|----------|----------|----------|-----------|
| [Domain-specific criterion 1] | [Assessment] | [Assessment] | [Context-based reasoning] |
| [Domain-specific criterion 2] | [Assessment] | [Assessment] | [Context-based reasoning] |
| [Domain-specific criterion 3] | [Assessment] | [Assessment] | [Context-based reasoning] |

### Strategic Fit Analysis
- **Option 1 Fit**: [How well Option 1 aligns with domain requirements]
- **Option 2 Fit**: [How well Option 2 aligns with domain requirements]
- **Context Suitability**: [Which option better suits the specific problem context]

## Domain-Informed Recommendation
### Recommended Option
- **Selection**: [Chosen option with domain-specific justification]
- **Context Rationale**: [Why this option is best for the identified problem domain]
- **Expected Outcomes**: [Domain-appropriate success expectations]

### Implementation Priorities
- **Immediate Focus**: [First steps specific to the problem context]
- **Critical Success Factors**: [Domain-relevant factors for success]
- **Risk Mitigation**: [Context-specific risk management priorities]

### Next Phase Preparation
- **Stakeholder Engagement**: [Domain-appropriate stakeholder management]
- **Resource Mobilization**: [Context-specific resource requirements]
- **Success Measurement**: [Domain-relevant metrics and monitoring]
""",
            agent=CreateAgent.create_agent(),
            markdown=True,
            output_file="intervention_options.md"
        )