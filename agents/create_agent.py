from crewai import Agent
# No external tools needed for this agent
from config import config

class CreateAgent:
    """Agent responsible for creating intervention options and strategic alternatives"""
    
    @staticmethod
    def create_agent():
        return Agent(
            role="Strategic Option Development Specialist",
            goal="Create multiple strategic intervention options with comprehensive analysis of pros, cons, and assumptions",
            backstory="""You are a strategic planning expert and innovation consultant with extensive experience 
            in developing creative solutions and strategic alternatives. You excel at generating multiple viable 
            options for complex challenges, analyzing trade-offs, and presenting clear recommendations. Your 
            expertise includes option generation, scenario planning, and strategic decision analysis.""",
            tools=[],
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE
        )
    
    @staticmethod
    def create_task(problem_definition: str, context_analysis: str):
        from crewai import Task
        return Task(
            description=f"""
Create at least 2 strategic intervention options based on the problem definition and context analysis.

Problem Definition:
{problem_definition}

Context and Risk Analysis:
{context_analysis}

Requirements:
1. **Option Generation**
   - Develop at least 2 distinct strategic intervention options
   - Ensure options address the core problem and objectives
   - Consider different approaches and methodologies
   - Include both conservative and innovative alternatives

2. **Option Analysis**
   - Detailed pros and cons for each option
   - Resource requirements and investment needs
   - Implementation complexity assessment
   - Risk profile for each option

3. **Assumptions Documentation**
   - Critical assumptions underlying each option
   - Dependency analysis and requirements
   - Success factor identification
   - Constraint considerations

4. **Comparative Assessment**
   - Side-by-side option comparison
   - Decision criteria evaluation
   - Recommendation framework
   - Selection guidance

5. **Implementation Considerations**
   - High-level implementation approach
   - Resource and capability requirements
   - Timeline considerations
   - Success probability assessment

Create comprehensive option documentation that enables informed decision-making.
""",
            expected_output="""
A comprehensive intervention options document in Markdown/PDF format containing:

# Strategic Intervention Options Analysis

## Executive Summary
- **Total Options Developed**: [Number of options]
- **Recommended Approach**: [Top recommendation with brief rationale]
- **Decision Timeline**: [Recommended decision timeframe]
- **Key Decision Factors**: [Most important selection criteria]

## Option Development Methodology
### Approach Framework
- **Option Generation Process**: [How options were developed]
- **Evaluation Criteria**: [Standards used for assessment]
- **Stakeholder Considerations**: [How stakeholder needs were addressed]
- **Risk Integration**: [How risk analysis influenced options]

### Decision Context
- **Problem Alignment**: [How options address core problem]
- **Objective Achievement**: [How options meet defined objectives]
- **Constraint Accommodation**: [How options work within constraints]
- **Opportunity Leverage**: [How options capitalize on opportunities]

## Strategic Option 1: [Option Name]
- Overview, pros/cons, assumptions, implementation considerations, and comparative assessment.

## Strategic Option 2: [Option Name]
- Overview, pros/cons, assumptions, implementation considerations, and comparative assessment.

## Comparative Assessment
- Table or summary comparing all options on key criteria.

## Recommendation
- Final recommendation and rationale.
""",
            agent=CreateAgent.create_agent(),
            markdown=True,
            output_file="intervention_options.md"
        )