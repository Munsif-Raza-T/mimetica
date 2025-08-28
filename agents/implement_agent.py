from crewai import Agent
# Using project_management_tool for implementation planning
from tools.custom_tools import project_management_tool
from config import config

class ImplementAgent:
    """Agent responsible for creating detailed implementation roadmaps"""
    
    @staticmethod
    def create_agent():
        return Agent(
            role="Implementation Planning and Project Management Specialist",
            goal="Create comprehensive implementation roadmaps with detailed timelines, milestones, and responsibility assignments",
            backstory="""You are a senior project management expert and implementation specialist with extensive 
            experience in translating strategic plans into actionable roadmaps. You excel at breaking down complex 
            initiatives into manageable phases, creating realistic timelines, and establishing clear accountability 
            frameworks. Your expertise includes project planning, resource allocation, risk management, and 
            stakeholder coordination.""",
            tools=[
                project_management_tool
            ],
            verbose=True,
            allow_delegation=False,
            max_iter=config.MAX_ITERATIONS,
            temperature=config.TEMPERATURE
        )
    
    @staticmethod
    def create_task(selected_option: str, option_details: str):
        from crewai import Task
        return Task(
            description = f"""
            Create a comprehensive implementation roadmap for the selected strategic option.
            
            Selected Strategic Option:
            {selected_option}
            
            Option Details and Analysis:
            {option_details}
            
            Implementation Planning Requirements:
            1. **Project Structure Design**
               - Break down the option into implementable phases
               - Define work packages and deliverables
               - Create work breakdown structure (WBS)
               - Establish project governance framework
               
            2. **Timeline and Milestone Planning**
               - Develop detailed project schedule
               - Identify critical milestones and dependencies
               - Create realistic timeline with buffer considerations
               - Define phase gates and decision points
               
            3. **Resource Planning and Allocation**
               - Detail human resource requirements by phase
               - Specify technology and infrastructure needs
               - Plan budget allocation and cash flow
               - Identify external resource requirements
               
            4. **Responsibility Assignment**
               - Define roles and responsibilities (RACI matrix)
               - Assign accountability for deliverables
               - Establish reporting relationships
               - Create escalation procedures
               
            5. **Risk Management Integration**
               - Incorporate risk mitigation into timeline
               - Plan contingency activities
               - Define risk monitoring and response procedures
               - Create alternative implementation paths
               
            6. **Quality and Control Framework**
               - Define quality standards and checkpoints
               - Establish review and approval processes
               - Create monitoring and reporting mechanisms
               - Plan performance measurement systems
            
            Create a detailed, actionable implementation plan ready for execution.
            """,
            expected_output = """A comprehensive implementation roadmap document containing:
            
            # Implementation Roadmap and Deployment Plan
            
            ## Executive Summary
            - **Implementation Scope**: [What will be implemented]
            - **Total Duration**: [Overall timeline]
            - **Key Milestones**: [Major checkpoints and deliverables]
            - **Resource Requirements**: [Summary of resources needed]
            - **Success Probability**: [Implementation success assessment]
            - **Critical Success Factors**: [Most important elements for success]
            
            ## Implementation Strategy Overview
            ### Strategic Approach
            - **Implementation Philosophy**: [Overall approach and methodology]
            - **Phased Implementation Rationale**: [Why phases were chosen this way]
            - **Risk Management Approach**: [How risks will be managed during implementation]
            - **Quality Assurance Strategy**: [How quality will be ensured]
            
            ### Implementation Principles
            - **Principle 1**: [Guiding principle for implementation]
            - **Principle 2**: [Second guiding principle]
            - **Principle 3**: [Third guiding principle]
            - **Change Management Approach**: [How change will be managed]
            
            ## Project Structure and Organization
            
            ### Work Breakdown Structure (WBS)
            #### Phase 1: [Phase Name] - Preparation and Setup
            **Duration**: [Timeline]
            **Objectives**: [What this phase achieves]
            
            **Work Packages:**
            1. **WP 1.1**: [Work package name]
               - **Activities**: [Specific tasks and activities]
               - **Deliverables**: [Expected outputs]
               - **Duration**: [Time required]
               - **Dependencies**: [What must be completed first]
            
            2. **WP 1.2**: [Second work package]
            3. **WP 1.3**: [Third work package]
            
            #### Phase 2: [Phase Name] - Core Implementation
            **Duration**: [Timeline]
            **Objectives**: [What this phase achieves]
            
            **Work Packages:**
            1. **WP 2.1**: [Work package name]
            2. **WP 2.2**: [Second work package]
            3. **WP 2.3**: [Third work package]
            
            #### Phase 3: [Phase Name] - Integration and Testing
            **Duration**: [Timeline]
            **Objectives**: [What this phase achieves]
            
            #### Phase 4: [Phase Name] - Deployment and Closure
            **Duration**: [Timeline]
            **Objectives**: [What this phase achieves]
            
            ### Project Governance Structure
            #### Governance Bodies
            - **Steering Committee**: [Executive oversight and decision-making]
              - Members: [Key stakeholders and executives]
              - Meeting Frequency: [How often they meet]
              - Responsibilities: [Decision authority and oversight duties]
            
            - **Project Management Office (PMO)**: [Day-to-day management]
              - Project Manager: [Lead project manager]
              - Team Leads: [Phase and workstream leaders]
              - Responsibilities: [Operational management duties]
            
            - **Technical Review Board**: [Technical oversight and quality]
              - Technical Experts: [Subject matter experts]
              - Review Schedule: [When technical reviews occur]
              - Authority: [Technical decision-making scope]
            
            #### Decision-Making Framework
            - **Decision Categories**: [Types of decisions and who makes them]
            - **Escalation Process**: [How issues are escalated]
            - **Approval Authorities**: [Who can approve what level of changes]
            
            ## Detailed Implementation Timeline
            
            ### Master Schedule Overview
            | Phase | Start Date | End Date | Duration | Key Deliverables |
            |-------|------------|----------|----------|------------------|
            | Phase 1 | [Date] | [Date] | [Weeks] | [Main outputs] |
            | Phase 2 | [Date] | [Date] | [Weeks] | [Main outputs] |
            | Phase 3 | [Date] | [Date] | [Weeks] | [Main outputs] |
            | Phase 4 | [Date] | [Date] | [Weeks] | [Main outputs] |
            
            ### Critical Path Analysis
            #### Critical Activities
            1. **Activity 1**: [Critical path activity with timing]
            2. **Activity 2**: [Second critical activity]
            3. **Activity 3**: [Third critical activity]
            
            #### Dependencies and Constraints
            - **External Dependencies**: [Dependencies on external parties]
            - **Internal Dependencies**: [Dependencies on internal resources]
            - **Resource Constraints**: [Limited resource availability]
            - **Technical Constraints**: [Technical limitations affecting timeline]
            
            ### Milestone Schedule
            #### Major Milestones
            | Milestone | Target Date | Success Criteria | Responsible Party |
            |-----------|-------------|------------------|-------------------|
            | **M1**: [Milestone name] | [Date] | [Success criteria] | [Owner] |
            | **M2**: [Milestone name] | [Date] | [Success criteria] | [Owner] |
            | **M3**: [Milestone name] | [Date] | [Success criteria] | [Owner] |
            | **M4**: [Milestone name] | [Date] | [Success criteria] | [Owner] |
            
            #### Phase Gate Reviews
            - **Gate 1**: [End of Phase 1 review criteria]
            - **Gate 2**: [End of Phase 2 review criteria]
            - **Gate 3**: [End of Phase 3 review criteria]
            - **Gate 4**: [Project completion criteria]
            
            ## Resource Allocation and Management
            
            ### Human Resource Plan
            #### Staffing by Phase
            | Role | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Total FTE |
            |------|---------|---------|---------|---------|-----------|
            | Project Manager | [FTE] | [FTE] | [FTE] | [FTE] | [Total] |
            | Technical Lead | [FTE] | [FTE] | [FTE] | [FTE] | [Total] |
            | Business Analyst | [FTE] | [FTE] | [FTE] | [FTE] | [Total] |
            | Developer | [FTE] | [FTE] | [FTE] | [FTE] | [Total] |
            | QA Specialist | [FTE] | [FTE] | [FTE] | [FTE] | [Total] |
            
            #### Key Personnel Requirements
            - **Project Manager**: [Skills and experience requirements]
            - **Technical Lead**: [Technical expertise needed]
            - **Subject Matter Experts**: [Domain expertise requirements]
            - **External Consultants**: [Specialized skills needed]
            
            #### Resource Onboarding Plan
            - **Recruitment Timeline**: [When new resources are needed]
            - **Training Requirements**: [Skills development needs]
            - **Knowledge Transfer Plan**: [How knowledge will be shared]
            
            ### Budget and Financial Planning
            #### Budget Allocation by Phase
            | Budget Category | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Total |
            |----------------|---------|---------|---------|---------|-------|
            | Personnel Costs | [$] | [$] | [$] | [$] | [$] |
            | Technology Costs | [$] | [$] | [$] | [$] | [$] |
            | External Services | [$] | [$] | [$] | [$] | [$] |
            | Infrastructure | [$] | [$] | [$] | [$] | [$] |
            | Contingency | [$] | [$] | [$] | [$] | [$] |
            | **Total** | **[$]** | **[$]** | **[$]** | **[$]** | **[$]** |
            
            #### Cash Flow Planning
            - **Monthly Cash Flow**: [Expected spending by month]
            - **Payment Schedule**: [When payments are due]
            - **Budget Monitoring**: [How budget will be tracked]
            
            ### Technology and Infrastructure Plan
            #### Technology Requirements by Phase
            - **Development Environment**: [Tools and systems needed]
            - **Testing Infrastructure**: [Testing tools and environments]
            - **Production Infrastructure**: [Live system requirements]
            - **Security Infrastructure**: [Security tools and processes]
            
            #### Infrastructure Timeline
            - **Environment Setup**: [When environments will be ready]
            - **System Integration**: [Integration timeline and approach]
            - **Go-Live Preparation**: [Production readiness activities]
            
            ## Responsibility and Accountability Framework
            
            ### RACI Matrix
            | Activity/Deliverable | Project Manager | Technical Lead | Business Lead | Stakeholder |
            |----------------------|----------------|----------------|---------------|-------------|
            | **Project Planning** | R | A | C | I |
            | **Requirements Definition** | A | C | R | C |
            | **Solution Design** | A | R | C | I |
            | **Development** | A | R | C | I |
            | **Testing** | A | R | C | C |
            | **Deployment** | A | R | C | I |
            | **Change Management** | C | I | R | A |
            
            **Legend**: R=Responsible, A=Accountable, C=Consulted, I=Informed
            
            ### Role Definitions
            #### Project Manager
            - **Primary Responsibilities**: [Key duties and accountabilities]
            - **Authority Level**: [Decision-making authority]
            - **Reporting Relationships**: [Who they report to and manage]
            - **Key Performance Measures**: [How success is measured]
            
            #### Technical Lead
            - **Primary Responsibilities**: [Technical leadership duties]
            - **Authority Level**: [Technical decision authority]
            - **Expertise Requirements**: [Technical skills needed]
            
            #### Business Lead
            - **Primary Responsibilities**: [Business oversight duties]
            - **Stakeholder Management**: [Stakeholder relationships managed]
            - **Business Decision Authority**: [Business decisions they can make]
            
            ### Communication and Reporting Framework
            #### Reporting Structure
            - **Weekly Status Reports**: [Content and recipients]
            - **Monthly Executive Reports**: [Executive summary format]
            - **Milestone Reports**: [Milestone achievement reporting]
            - **Exception Reports**: [Issue and risk reporting]
            
            #### Communication Plan
            - **Team Meetings**: [Regular team communication schedule]
            - **Stakeholder Updates**: [Stakeholder communication plan]
            - **Escalation Procedures**: [How issues are escalated]
            
            ## Risk Management Integration
            
            ### Risk Mitigation in Timeline
            #### High-Priority Risk Management
            1. **Risk**: [Specific high-priority risk]
               - **Mitigation Activities**: [Planned risk reduction activities]
               - **Timeline Impact**: [How mitigation affects schedule]
               - **Resource Requirements**: [Resources needed for mitigation]
               - **Monitoring Plan**: [How risk will be monitored]
            
            2. **Risk**: [Second high-priority risk]
            3. **Risk**: [Third high-priority risk]
            
            ### Contingency Planning
            #### Alternative Implementation Paths
            - **Scenario 1**: [If major risk materializes]
              - **Alternative Approach**: [Backup implementation strategy]
              - **Timeline Impact**: [How timeline changes]
              - **Resource Impact**: [Changed resource requirements]
            
            - **Scenario 2**: [If resource constraints occur]
            - **Scenario 3**: [If technical issues arise]
            
            #### Risk Response Procedures
            - **Risk Monitoring**: [How risks are tracked during implementation]
            - **Response Triggers**: [When to activate contingency plans]
            - **Decision Procedures**: [How response decisions are made]
            
            ## Quality Assurance and Control
            
            ### Quality Framework
            #### Quality Standards
            - **Deliverable Quality Standards**: [Standards for all deliverables]
            - **Process Quality Standards**: [Standards for work processes]
            - **Technical Quality Standards**: [Technical quality requirements]
            
            #### Quality Control Checkpoints
            | Phase | Quality Check | Criteria | Responsible Party |
            |-------|---------------|----------|-------------------|
            | Phase 1 | [Check type] | [Pass/fail criteria] | [QA owner] |
            | Phase 2 | [Check type] | [Pass/fail criteria] | [QA owner] |
            | Phase 3 | [Check type] | [Pass/fail criteria] | [QA owner] |
            | Phase 4 | [Check type] | [Pass/fail criteria] | [QA owner] |
            
            ### Review and Approval Processes
            #### Review Procedures
            - **Peer Reviews**: [Technical and design reviews]
            - **Management Reviews**: [Executive oversight reviews]
            - **Stakeholder Reviews**: [Business stakeholder approvals]
            
            #### Approval Authority
            - **Technical Approvals**: [Who approves technical decisions]
            - **Business Approvals**: [Who approves business decisions]
            - **Budget Approvals**: [Who approves spending decisions]
            
            ## Performance Monitoring and Control
            
            ### Performance Measurement Framework
            #### Key Performance Indicators (KPIs)
            - **Schedule Performance**: [Timeline adherence metrics]
            - **Budget Performance**: [Cost control metrics]
            - **Quality Performance**: [Quality achievement metrics]
            - **Resource Performance**: [Resource utilization metrics]
            
            #### Monitoring and Reporting
            - **Real-time Monitoring**: [Continuous performance tracking]
            - **Periodic Reviews**: [Regular performance assessments]
            - **Corrective Action Process**: [How performance issues are addressed]
            
            ### Success Measurement
            #### Implementation Success Criteria
            - **On-Time Delivery**: [Schedule success criteria]
            - **On-Budget Delivery**: [Budget success criteria]
            - **Quality Achievement**: [Quality success criteria]
            - **Stakeholder Satisfaction**: [Satisfaction success criteria]
            
            ## Change Management and Adaptation
            
            ### Change Control Process
            #### Change Request Procedure
            - **Change Identification**: [How changes are identified]
            - **Impact Assessment**: [How change impact is evaluated]
            - **Approval Process**: [How changes are approved]
            - **Implementation**: [How approved changes are implemented]
            
            ### Adaptation Mechanisms
            - **Agile Adjustments**: [How plan adapts to new information]
            - **Scope Management**: [How scope changes are managed]
            - **Resource Reallocation**: [How resources are reallocated]
            
            ## Implementation Readiness Checklist
            
            ### Pre-Implementation Requirements
            #### Organizational Readiness
            - [ ] **Leadership Commitment**: [Executive support confirmed]
            - [ ] **Resource Availability**: [Required resources secured]
            - [ ] **Stakeholder Alignment**: [Stakeholder buy-in achieved]
            - [ ] **Change Readiness**: [Organization prepared for change]
            
            #### Technical Readiness
            - [ ] **Infrastructure Ready**: [Technical infrastructure prepared]
            - [ ] **Development Environment**: [Development tools ready]
            - [ ] **Security Framework**: [Security measures in place]
            - [ ] **Integration Points**: [System integration points defined]
            
            #### Process Readiness
            - [ ] **Procedures Defined**: [Work procedures documented]
            - [ ] **Quality Framework**: [Quality processes established]
            - [ ] **Communication Plan**: [Communication mechanisms ready]
            - [ ] **Training Plan**: [Training programs prepared]
            
            ## Next Steps and Handover
            
            ### Immediate Actions
            1. **Resource Mobilization**: [Next steps to secure resources]
            2. **Detailed Planning**: [Further planning requirements]
            3. **Stakeholder Engagement**: [Stakeholder preparation activities]
            4. **Infrastructure Preparation**: [Technical preparation steps]
            
            ### Handover to Implementation Team
            - **Documentation Handover**: [What documents are provided]
            - **Knowledge Transfer**: [How knowledge is transferred]
            - **Ongoing Support**: [Continued planning support available]
            - **Success Monitoring**: [How implementation success will be tracked]
            """,
            markdown=True,
            agent = ImplementAgent.create_agent(),
            output_file="implementation_roadmap.md"
        )
