from crewai import Agent
# No external tools needed for this agent
from config import config

class DefineAgent:
    """Agent responsible for defining scope, objectives, and success criteria"""
    
    @staticmethod
    def create_agent():
        return Agent(
            role="Strategic Problem Definition Specialist",
            goal="Define clear problem statements, objectives, scope, and success criteria for strategic initiatives",
            backstory="""You are a strategic planning expert with extensive experience in problem 
            definition and objective setting. You excel at transforming complex business challenges 
            into clear, actionable problem statements with measurable objectives. Your expertise 
            includes stakeholder analysis, scope definition, and creating SMART goals that align 
            with organizational strategy.""",
            tools=[],
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE
        )
    
    @staticmethod
    def create_task(context_data: str, feasibility_report: str):
        from crewai import Task
        return Task(
            description=f"""
Define the strategic problem, objectives, scope, and success criteria based on the collected data and feasibility analysis.

Available Context:
{context_data}

Feasibility Analysis Summary:
{feasibility_report}

Your tasks:
1. **Problem Statement Definition**
   - Articulate the core problem or opportunity
   - Identify root causes and contributing factors
   - Define the business case and urgency

2. **Objective Setting**
   - Create SMART objectives (Specific, Measurable, Achievable, Relevant, Time-bound)
   - Align objectives with organizational strategy
   - Prioritize primary and secondary objectives

3. **Scope Definition**
   - Define project boundaries and limitations
   - Identify what is included and excluded
   - Specify stakeholder groups and their roles

4. **Success Criteria Development**
   - Define quantitative and qualitative success metrics
   - Establish baseline measurements
   - Create measurement frameworks and timelines

5. **Constraints and Assumptions**
   - Document key constraints and limitations
   - Identify critical assumptions
   - Assess dependency relationships

Ensure all definitions are clear, measurable, and aligned with feasibility findings.
""",
            expected_output="""
A comprehensive problem definition document in PDF/Markdown format containing:

# Strategic Problem Definition and Objectives

## Problem Statement
### Core Problem Description
- **Primary Problem**: [Clear, concise problem statement]
- **Problem Context**: [Background and situational factors]
- **Business Impact**: [Current cost/impact of the problem]
- **Urgency Assessment**: [Timeline pressures and priorities]

### Root Cause Analysis
- **Primary Causes**: [Main contributing factors]
- **Secondary Causes**: [Supporting factors]
- **System Factors**: [Organizational/process contributors]
- **External Factors**: [Market/environmental influences]

### Opportunity Definition
- **Strategic Opportunity**: [Potential value creation]
- **Competitive Advantage**: [Unique positioning opportunity]
- **Market Timing**: [Window of opportunity assessment]

## Strategic Objectives
### Primary Objectives
1. **Objective 1**: [SMART goal with specific metrics]
   - Specific: [What exactly will be achieved]
   - Measurable: [How success will be measured]
   - Achievable: [Realistic assessment]
   - Relevant: [Strategic alignment]
   - Time-bound: [Specific timeline]

2. **Objective 2**: [Second primary objective]
3. **Objective 3**: [Third primary objective]

### Secondary Objectives
- [Supporting objectives that complement primary goals]
- [Nice-to-have outcomes that add value]

### Objective Prioritization
- **Must-Have**: [Critical objectives for success]
- **Should-Have**: [Important but not critical]
- **Could-Have**: [Desirable additional outcomes]

## Project Scope
### Scope Definition
**In Scope:**
- [Specific activities, deliverables, and outcomes included]
- [Stakeholder groups and organizational units affected]
- [Systems, processes, and functions to be addressed]

**Out of Scope:**
- [Explicitly excluded items to prevent scope creep]
- [Related but separate initiatives]
- [Future phase considerations]

### Stakeholder Scope
- **Primary Stakeholders**: [Direct impact and involvement]
- **Secondary Stakeholders**: [Indirect impact or interest]
- **External Stakeholders**: [Outside parties affected]

### Geographic/Organizational Scope
- **Locations**: [Geographic boundaries]
- **Business Units**: [Organizational scope]
- **Systems**: [Technology scope]

## Success Criteria and Metrics
### Quantitative Success Metrics
1. **Metric 1**: [Primary quantitative measure]
   - Current Baseline: [Starting point measurement]
   - Target Value: [Desired end state]
   - Measurement Method: [How it will be measured]
   - Frequency: [How often measured]

2. **Metric 2**: [Second quantitative measure]
3. **Metric 3**: [Third quantitative measure]

### Qualitative Success Indicators
- **Stakeholder Satisfaction**: [Target satisfaction levels]
- **Quality Measures**: [Quality standards and assessments]
- **Process Improvements**: [Operational enhancements]

### Success Timeline
- **Short-term (0-3 months)**: [Early indicators of progress]
- **Medium-term (3-12 months)**: [Intermediate milestones]
- **Long-term (12+ months)**: [Ultimate success measures]

## Constraints and Assumptions
### Project Constraints
- **Budget Constraints**: [Financial limitations]
- **Time Constraints**: [Schedule limitations]
- **Resource Constraints**: [Personnel/skill limitations]
- **Technology Constraints**: [Technical limitations]
- **Regulatory Constraints**: [Compliance requirements]

### Critical Assumptions
- **Market Assumptions**: [Market condition assumptions]
- **Resource Assumptions**: [Availability assumptions]
- **Technology Assumptions**: [Technical capability assumptions]
- **Stakeholder Assumptions**: [Cooperation and support assumptions]

### Dependencies
- **Internal Dependencies**: [Other projects/initiatives]
- **External Dependencies**: [Third-party requirements]
- **Sequential Dependencies**: [Order of operations]

## Risk Factors
### Definition-Related Risks
- **Scope Creep Risk**: [Potential for expanding scope]
- **Objective Misalignment**: [Conflicting stakeholder goals]
- **Success Metric Challenges**: [Measurement difficulties]

### Mitigation Strategies
- [Specific approaches to manage definition risks]
- [Governance mechanisms for scope management]
- [Communication strategies for alignment]

## Approval and Governance
### Decision Authority
- **Primary Decision Maker**: [Ultimate authority]
- **Approval Committee**: [Governing body]
- **Stakeholder Sign-off**: [Required approvals]

### Change Management Process
- [Process for modifying objectives or scope]
- [Approval requirements for changes]
- [Communication protocol for changes]
""",
            agent=DefineAgent.create_agent(),
            markdown=True,
            output_file="problem_definition.md"
        )
