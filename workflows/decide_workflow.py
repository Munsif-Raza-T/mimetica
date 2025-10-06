import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st
from crewai import Crew, Task
import json
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

# Import all agents
from agents import (
    CollectorAgent,
    DecisionMultidisciplinaryAgent, 
    DefineAgent,
    ExploreAgent,
    CreateAgent,
    ImplementAgent,
    SimulateAgent,
    EvaluateAgent,
    ReportAgent
)

# Import utilities
from utils import SessionManager, VectorStore
from utils.enhanced_workflow_manager import EnhancedWorkflowManager
from utils.agent_communication_logger import agent_comm_logger
from config import config

class DecideWorkflow:
    """
    Main orchestrator for the DECIDE workflow using CrewAI
    Implements the sequential agent execution: Define → Explore → Create → Implement → Decide/Simulate → Evaluate
    """
    
    def __init__(self):
        self.workflow_id = st.session_state.workflow_state.get('workflow_id', f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.vector_store = VectorStore()
        self.current_phase = 'collection'
        self.phase_results = {}
        
        # Initialize logging
        SessionManager.add_log("INFO", f"DECIDE Workflow initialized: {self.workflow_id}")
        
        # Set up agent communication logger
        self.comm_logger = SessionManager.get_agent_comm_logger()
        if not self.comm_logger:
            # Create a new one if not available
            from utils.agent_communication_logger import AgentCommunicationLogger
            self.comm_logger = AgentCommunicationLogger()
            st.session_state.agent_comm_logger = self.comm_logger
    
    def execute_crew_with_logging(self, crew: Crew, phase_name: str, agent_name: str) -> Any:
        """Execute a CrewAI crew with comprehensive logging of all interactions"""
        self.comm_logger.start_phase_logging(phase_name)
        self.comm_logger.start_agent_execution(agent_name, f"Executing {phase_name} phase")
        
        # Capture stdout/stderr during execution
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        try:
            # Redirect output to capture CrewAI verbose logging
            sys.stdout = stdout_buffer
            sys.stderr = stderr_buffer
            
            # Execute the crew
            result = crew.kickoff()
            
            # Get captured output
            stdout_content = stdout_buffer.getvalue()
            stderr_content = stderr_buffer.getvalue()
            
            # Log the captured output
            if stdout_content:
                self.comm_logger.log_crewai_output(stdout_content)
                SessionManager.add_agent_communication(
                    f"CrewAI-{agent_name}", 
                    f"Verbose Output:\n{stdout_content[:1000]}...", 
                    "crewai_verbose", 
                    phase_name
                )
            
            if stderr_content:
                self.comm_logger.log_error("CrewAI", stderr_content)
                SessionManager.add_agent_communication(
                    f"CrewAI-{agent_name}", 
                    f"Error Output:\n{stderr_content}", 
                    "error", 
                    phase_name
                )
            
            # Log successful completion
            result_summary = str(result)[:200] if result else "No result"
            self.comm_logger.end_agent_execution(agent_name, result_summary)
            self.comm_logger.end_phase_logging(phase_name, success=True)
            
            SessionManager.add_agent_communication(
                agent_name, 
                f"✅ Phase completed successfully\n📊 Result: {result_summary}...", 
                "completion", 
                phase_name
            )
            
            return result
            
        except Exception as e:
            # Log the error
            error_msg = str(e)
            self.comm_logger.log_error(agent_name, error_msg, e)
            self.comm_logger.end_agent_execution(agent_name, f"Failed: {error_msg}")
            self.comm_logger.end_phase_logging(phase_name, success=False)
            
            SessionManager.add_agent_communication(
                agent_name, 
                f"❌ Phase failed\n🔍 Error: {error_msg}", 
                "error", 
                phase_name
            )
            
            raise e
            
        finally:
            # Restore original stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def run_complete_workflow(self) -> Dict[str, Any]:
        """Run the complete DECIDE workflow using enhanced workflow manager"""
        try:
            SessionManager.add_log("INFO", "Starting enhanced DECIDE workflow execution")
            
            # Create enhanced workflow manager
            enhanced_manager = EnhancedWorkflowManager(self)
            
            # Execute workflow with proper rate limiting
            result = enhanced_manager.run_enhanced_workflow()
            
            return result
        
        except Exception as e:
            error_msg = f"Enhanced workflow execution failed: {str(e)}"
            SessionManager.add_log("ERROR", error_msg)
            return {
                'success': False,
                'error': error_msg,
                'workflow_id': self.workflow_id
            }
    
    def run_collection_phase(self) -> Dict[str, Any]:
        """Run the document collection and processing phase"""
        try:
            SessionManager.update_agent_progress("collector_agent", 0.1, "starting", "Initializing document collection")
            
            # Get processed documents from session state
            documents = st.session_state.workflow_state.get('documents', [])
            
            if not documents:
                return {
                    'success': False,
                    'error': 'No processed documents available',
                    'recommendation': 'Please upload and process documents before running the workflow'
                }
            
            # Prepare documents information for the agent
            documents_info = self.format_documents_info(documents)
            
            SessionManager.update_agent_progress("collector_agent", 0.3, "running", "Creating collection agent")
            SessionManager.add_agent_communication("collector_agent", f"📋 Starting document collection phase\n📊 Processing {len(documents)} documents", "phase_start", "collection")
            
            # Create agent and task
            collector_agent = CollectorAgent.create_agent()
            collector_task = CollectorAgent.create_task(documents_info)
            
            SessionManager.update_agent_progress("collector_agent", 0.5, "running", "Processing documents")
            SessionManager.add_agent_communication("collector_agent", f"🤖 Agent created\n🎯 Task: Analyze and process {len(documents)} documents", "agent_start", "collection")
            
            # Create and execute crew with logging
            crew = Crew(
                agents=[collector_agent],
                tasks=[collector_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("collector_agent", 0.8, "running", "Executing analysis")
            
            # Execute the crew with comprehensive logging
            result = self.execute_crew_with_logging(crew, "collection", "collector_agent")
            
            SessionManager.update_agent_progress("collector_agent", 1.0, "completed", "Document collection completed")
            
            return {
                'success': True,
                'phase': 'collection',
                'agent': 'collector_agent',
                'output': result,
                'documents_processed': len(documents),
                'vector_status': self.get_vector_store_status()
            }
        
        except Exception as e:
            SessionManager.update_agent_progress("collector_agent", 0.0, "failed", f"Error: {str(e)}")
            SessionManager.add_agent_communication("collector_agent", f"❌ Collection phase failed\n🔍 Error: {str(e)}", "error", "collection")
            return {
                'success': False,
                'error': str(e),
                'phase': 'collection'
            }
    
    def run_multidisciplinary_analysis_phase(self) -> Dict[str, Any]:
        """Run the multidisciplinary feasibility analysis phase"""
        try:
            SessionManager.update_agent_progress("decision_multidisciplinary_agent", 0.1, "starting", "Initializing multidisciplinary analysis")
            
            # Get context from previous phase and documents
            context_data = self.get_context_for_analysis()
            
            SessionManager.update_agent_progress("decision_multidisciplinary_agent", 0.3, "running", "Creating analysis agent")
            SessionManager.add_agent_communication("decision_multidisciplinary_agent", "🔬 Starting multidisciplinary feasibility analysis\n📊 Analyzing across 6 dimensions: Technology, Legal, Financial, Market, Communication, Behavioral", "phase_start", "analysis")
            
            # Create agent and task
            analysis_agent = DecisionMultidisciplinaryAgent.create_agent()
            analysis_task = DecisionMultidisciplinaryAgent.create_task(context_data)
            
            SessionManager.update_agent_progress("decision_multidisciplinary_agent", 0.5, "running", "Conducting feasibility analysis")
            SessionManager.add_agent_communication("decision_multidisciplinary_agent", "🤖 Multidisciplinary agent created\n🎯 Task: Comprehensive feasibility analysis across all dimensions", "agent_start", "analysis")
            
            # Create and execute crew with logging
            crew = Crew(
                agents=[analysis_agent],
                tasks=[analysis_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("decision_multidisciplinary_agent", 0.8, "running", "Finalizing analysis")
            
            result = self.execute_crew_with_logging(crew, "analysis", "decision_multidisciplinary_agent")
            
            SessionManager.update_agent_progress("decision_multidisciplinary_agent", 1.0, "completed", "Multidisciplinary analysis completed")
            
            return {
                'success': True,
                'phase': 'analysis',
                'agent': 'decision_multidisciplinary_agent',
                'output': result,
                'analysis_dimensions': ['technology', 'legal', 'financial', 'market', 'communication', 'behavioral']
            }
        
        except Exception as e:
            SessionManager.update_agent_progress("decision_multidisciplinary_agent", 0.0, "failed", f"Error: {str(e)}")
            SessionManager.add_agent_communication("decision_multidisciplinary_agent", f"❌ Analysis phase failed\n🔍 Error: {str(e)}", "error", "analysis")
            return {
                'success': False,
                'error': str(e),
                'phase': 'analysis'
            }
    
    def run_define_phase(self) -> Dict[str, Any]:
        """Run the problem definition phase"""
        try:
            SessionManager.update_agent_progress("define_agent", 0.1, "starting", "Initializing problem definition")
            
            # Get context and feasibility report
            context_data = self.get_context_for_analysis()
            feasibility_report = self.get_previous_phase_output('analysis')
            
            SessionManager.update_agent_progress("define_agent", 0.3, "running", "Creating definition agent")
            SessionManager.add_agent_communication("define_agent", "🎯 Starting problem definition phase\n📋 Analyzing feasibility report and context to define clear objectives", "phase_start", "definition")
            
            # Create agent and task
            define_agent = DefineAgent.create_agent()
            define_task = DefineAgent.create_task(context_data, feasibility_report)
            
            SessionManager.update_agent_progress("define_agent", 0.5, "running", "Defining problem and objectives")
            
            # Create and execute crew with logging
            crew = Crew(
                agents=[define_agent],
                tasks=[define_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("define_agent", 0.8, "running", "Finalizing definition")
            
            result = self.execute_crew_with_logging(crew, "definition", "define_agent")
            
            SessionManager.update_agent_progress("define_agent", 1.0, "completed", "Problem definition completed")
            
            return {
                'success': True,
                'phase': 'definition',
                'agent': 'define_agent',
                'output': result
            }
        
        except Exception as e:
            SessionManager.update_agent_progress("define_agent", 0.0, "failed", f"Error: {str(e)}")
            SessionManager.add_agent_communication("define_agent", f"❌ Definition phase failed\n🔍 Error: {str(e)}", "error", "definition")
            return {
                'success': False,
                'error': str(e),
                'phase': 'definition'
            }
    
    def run_explore_phase(self) -> Dict[str, Any]:
        """Run the exploration and risk mapping phase"""
        try:
            SessionManager.update_agent_progress("explore_agent", 0.1, "starting", "Initializing contextual exploration")
            
            # Get problem definition and context
            problem_definition = self.get_previous_phase_output('definition')
            available_context = self.get_context_for_analysis()
            
            SessionManager.update_agent_progress("explore_agent", 0.3, "running", "Creating exploration agent")
            
            # Create agent and task
            explore_agent = ExploreAgent.create_agent()
            explore_task = ExploreAgent.create_task(problem_definition, available_context)
            
            SessionManager.update_agent_progress("explore_agent", 0.5, "running", "Conducting research and risk mapping")
            
            # Create and execute crew
            crew = Crew(
                agents=[explore_agent],
                tasks=[explore_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("explore_agent", 0.8, "running", "Finalizing exploration")
            
            result = crew.kickoff()
            
            SessionManager.update_agent_progress("explore_agent", 1.0, "completed", "Exploration and risk mapping completed")
            
            return {
                'success': True,
                'phase': 'exploration',
                'agent': 'explore_agent',
                'output': result
            }
        
        except Exception as e:
            SessionManager.update_agent_progress("explore_agent", 0.0, "failed", f"Error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phase': 'exploration'
            }
    
    def run_create_phase(self) -> Dict[str, Any]:
        """Run the strategic option creation phase"""
        try:
            SessionManager.update_agent_progress("create_agent", 0.1, "starting", "Initializing option creation")
            
            # Get problem definition and context analysis
            problem_definition = self.get_previous_phase_output('definition')
            context_analysis = self.get_previous_phase_output('exploration')
            
            SessionManager.update_agent_progress("create_agent", 0.3, "running", "Creating option development agent")
            
            # Create agent and task
            create_agent = CreateAgent.create_agent()
            create_task = CreateAgent.create_task(problem_definition, context_analysis)
            
            SessionManager.update_agent_progress("create_agent", 0.5, "running", "Developing strategic options")
            
            # Create and execute crew
            crew = Crew(
                agents=[create_agent],
                tasks=[create_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("create_agent", 0.8, "running", "Finalizing option analysis")
            
            result = crew.kickoff()
            
            SessionManager.update_agent_progress("create_agent", 1.0, "completed", "Strategic option creation completed")
            
            return {
                'success': True,
                'phase': 'creation',
                'agent': 'create_agent',
                'output': result
            }
        
        except Exception as e:
            SessionManager.update_agent_progress("create_agent", 0.0, "failed", f"Error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phase': 'creation'
            }
    
    def run_implement_phase(self) -> Dict[str, Any]:
        """Run the implementation planning phase"""
        try:
            SessionManager.update_agent_progress("implement_agent", 0.1, "starting", "Initializing implementation planning")
            
            # Get selected option and details (for now, use the first/recommended option)
            option_analysis = self.get_previous_phase_output('creation')
            selected_option = "Recommended Strategic Option"  # This would be selected by user in practice
            
            SessionManager.update_agent_progress("implement_agent", 0.3, "running", "Creating implementation agent")
            
            # Create agent and task
            implement_agent = ImplementAgent.create_agent()
            implement_task = ImplementAgent.create_task(selected_option, option_analysis)
            
            SessionManager.update_agent_progress("implement_agent", 0.5, "running", "Developing implementation roadmap")
            
            # Create and execute crew
            crew = Crew(
                agents=[implement_agent],
                tasks=[implement_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("implement_agent", 0.8, "running", "Finalizing implementation plan")
            
            result = crew.kickoff()
            
            SessionManager.update_agent_progress("implement_agent", 1.0, "completed", "Implementation planning completed")
            
            return {
                'success': True,
                'phase': 'implementation',
                'agent': 'implement_agent',
                'output': result
            }
        
        except Exception as e:
            SessionManager.update_agent_progress("implement_agent", 0.0, "failed", f"Error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phase': 'implementation'
            }
    
    def run_simulate_phase(self) -> Dict[str, Any]:
        """Run the Monte Carlo simulation phase"""
        try:
            SessionManager.update_agent_progress("simulate_agent", 0.1, "starting", "Initializing Monte Carlo simulation")
            
            # Get implementation plan and option analysis
            implementation_plan = self.get_previous_phase_output('implementation')
            option_analysis = self.get_previous_phase_output('creation')
            
            SessionManager.update_agent_progress("simulate_agent", 0.3, "running", "Creating simulation agent")
            
            # Create agent and task
            simulate_agent = SimulateAgent.create_agent()
            simulate_task = SimulateAgent.create_task(implementation_plan, option_analysis)
            
            SessionManager.update_agent_progress("simulate_agent", 0.5, "running", "Running Monte Carlo simulations")
            
            # Create and execute crew
            crew = Crew(
                agents=[simulate_agent],
                tasks=[simulate_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("simulate_agent", 0.8, "running", "Analyzing simulation results")
            
            result = crew.kickoff()
            
            # Generate additional layman explanation if result contains technical analysis
            SessionManager.update_agent_progress("simulate_agent", 0.9, "running", "Generating layman-friendly explanations")
            
            try:
                from tools.custom_tools import monte_carlo_results_explainer
                
                # Extract key simulation numbers from the result for explanation
                result_text = str(result) if not isinstance(result, str) else result
                
                # Generate explanation for different audiences
                exec_explanation = monte_carlo_results_explainer(result_text, "executives")
                manager_explanation = monte_carlo_results_explainer(result_text, "managers")
                general_explanation = monte_carlo_results_explainer(result_text, "general")
                
                # Store explanations in session state for easy access
                if 'workflow_state' in st.session_state:
                    if 'simulation_explanations' not in st.session_state.workflow_state:
                        st.session_state.workflow_state['simulation_explanations'] = {}
                    
                    st.session_state.workflow_state['simulation_explanations'] = {
                        'executive': exec_explanation,
                        'manager': manager_explanation,
                        'general': general_explanation,
                        'timestamp': datetime.now().isoformat()
                    }
                
                SessionManager.add_log("INFO", "Generated layman-friendly explanations for Monte Carlo results")
                
            except Exception as e:
                SessionManager.add_log("WARNING", f"Could not generate layman explanations: {str(e)}")
            
            SessionManager.update_agent_progress("simulate_agent", 1.0, "completed", "Monte Carlo simulation completed")
            
            return {
                'success': True,
                'phase': 'simulation',
                'agent': 'simulate_agent',
                'output': result,
                'simulation_runs': config.MONTE_CARLO_RUNS,
                'explanations_generated': True
            }
        
        except Exception as e:
            SessionManager.update_agent_progress("simulate_agent", 0.0, "failed", f"Error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phase': 'simulation'
            }
    
    def run_evaluate_phase(self) -> Dict[str, Any]:
        """Run the evaluation framework phase"""
        try:
            SessionManager.update_agent_progress("evaluate_agent", 0.1, "starting", "Initializing evaluation framework")
            
            # Get implementation plan and simulation results
            implementation_plan = self.get_previous_phase_output('implementation')
            simulation_results = self.get_previous_phase_output('simulation')
            
            SessionManager.update_agent_progress("evaluate_agent", 0.3, "running", "Creating evaluation agent")
            
            # Create agent and task
            evaluate_agent = EvaluateAgent.create_agent()
            evaluate_task = EvaluateAgent.create_task(implementation_plan, simulation_results)
            
            SessionManager.update_agent_progress("evaluate_agent", 0.5, "running", "Developing KPIs and success metrics")
            
            # Create and execute crew
            crew = Crew(
                agents=[evaluate_agent],
                tasks=[evaluate_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("evaluate_agent", 0.8, "running", "Finalizing evaluation framework")
            
            result = crew.kickoff()
            
            SessionManager.update_agent_progress("evaluate_agent", 1.0, "completed", "Evaluation framework completed")
            
            return {
                'success': True,
                'phase': 'evaluation',
                'agent': 'evaluate_agent',
                'output': result
            }
        
        except Exception as e:
            SessionManager.update_agent_progress("evaluate_agent", 0.0, "failed", f"Error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phase': 'evaluation'
            }
    
    def run_report_phase(self) -> Dict[str, Any]:
        """Run the final report generation phase"""
        try:
            SessionManager.update_agent_progress("report_agent", 0.1, "starting", "Initializing report generation")
            
            # Collect all phase outputs
            all_phase_outputs = self.collect_all_phase_outputs()
            
            SessionManager.update_agent_progress("report_agent", 0.3, "running", "Creating report agent")
            SessionManager.add_agent_communication("report_agent", "📊 Starting final report generation\n📋 Synthesizing all phase outputs into comprehensive report", "phase_start", "report")
            
            # Create agent and task
            report_agent = ReportAgent.create_agent()
            report_task = ReportAgent.create_task(all_phase_outputs)
            
            SessionManager.update_agent_progress("report_agent", 0.5, "running", "Synthesizing comprehensive report")
            SessionManager.add_agent_communication("report_agent", "🤖 Report agent created\n🎯 Task: Generate comprehensive final report with all insights", "agent_start", "report")
            
            # Create and execute crew with logging
            crew = Crew(
                agents=[report_agent],
                tasks=[report_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("report_agent", 0.8, "running", "Finalizing report")
            
            result = self.execute_crew_with_logging(crew, "report", "report_agent")
            
            SessionManager.update_agent_progress("report_agent", 1.0, "completed", "Final report generation completed")
            
            return {
                'success': True,
                'phase': 'report',
                'agent': 'report_agent',
                'output': result,
                'includes_phases': list(self.phase_results.keys())
            }
        
        except Exception as e:
            SessionManager.update_agent_progress("report_agent", 0.0, "failed", f"Error: {str(e)}")
            SessionManager.add_agent_communication("report_agent", f"❌ Report generation failed\n🔍 Error: {str(e)}", "error", "report")
            return {
                'success': False,
                'error': str(e),
                'phase': 'report'
            }
    
    def format_documents_info(self, documents: List[Dict[str, Any]]) -> str:
        """Format document information for agent consumption"""
        if not documents:
            return "No documents available for processing."
        
        info = f"Total Documents: {len(documents)}\n\n"
        
        for i, doc in enumerate(documents, 1):
            info += f"Document {i}:\n"
            info += f"- Filename: {doc.get('filename', 'Unknown')}\n"
            info += f"- File Type: {doc.get('file_type', 'Unknown')}\n"
            info += f"- File Size: {doc.get('file_size', 0)} bytes\n"
            info += f"- Word Count: {doc.get('word_count', 0)}\n"
            info += f"- Processed At: {doc.get('processed_at', 'Unknown')}\n"
            
            # Add content preview (first 500 characters)
            content = doc.get('content', '')
            if content:
                preview = content[:500] + "..." if len(content) > 500 else content
                info += f"- Content Preview: {preview}\n"
            
            info += "\n"
        
        return info
    
    def get_context_for_analysis(self) -> str:
        """Get combined context information for analysis"""
        context = ""
        
        # Add project information
        project_info = st.session_state.workflow_state.get('project_info', {})
        if project_info:
            context += f"Project Information:\n"
            context += f"- Project Name: {project_info.get('name', 'Unknown')}\n"
            context += f"- Description: {project_info.get('description', 'Not provided')}\n"
            
            # Include analysis focus and custom focus if provided
            focus = project_info.get('focus', 'General')
            context += f"- Analysis Focus: {focus}\n"
            
            # Add custom focus if it exists and focus is "Other"
            if focus == "Other" and project_info.get('custom_focus'):
                context += f"- Custom Focus Details: {project_info.get('custom_focus')}\n"
            
            context += f"- Project Created: {project_info.get('created_at', 'Unknown')}\n\n"
        
        # Add document summary
        documents = st.session_state.workflow_state.get('documents', [])
        if documents:
            context += f"Document Summary:\n"
            context += f"- Total Documents: {len(documents)}\n"
            
            total_words = sum(doc.get('word_count', 0) for doc in documents)
            context += f"- Total Word Count: {total_words:,}\n"
            
            file_types = {}
            for doc in documents:
                file_type = doc.get('file_type', 'unknown')
                file_types[file_type] = file_types.get(file_type, 0) + 1
            
            context += f"- File Types: {', '.join(f'{k}: {v}' for k, v in file_types.items())}\n\n"
        
        # Add vector store status
        try:
            vector_info = self.vector_store.get_collection_info()
            if vector_info:
                context += f"Vector Database Status:\n"
                context += f"- Vector Count: {vector_info.get('vector_count', 0)}\n"
                context += f"- Collection: {vector_info.get('name', 'Unknown')}\n\n"
        except:
            context += "Vector Database: Not available\n\n"
        
        return context
    
    def get_previous_phase_output(self, phase_name: str) -> str:
        """Get output from a previous phase"""
        phase_outputs = st.session_state.workflow_state.get('phase_outputs', {})
        
        if phase_name in phase_outputs:
            output_info = phase_outputs[phase_name]
            output = output_info.get('output', {})
            
            if isinstance(output, dict):
                return json.dumps(output, indent=2)
            else:
                return str(output)
        
        return f"No output available for phase: {phase_name}"
    
    def collect_all_phase_outputs(self) -> str:
        """Collect all phase outputs for final report"""
        phase_outputs = st.session_state.workflow_state.get('phase_outputs', {})
        
        if not phase_outputs:
            return "No phase outputs available for report generation."
        
        consolidated_output = "CONSOLIDATED PHASE OUTPUTS FOR FINAL REPORT\n"
        consolidated_output += "=" * 60 + "\n\n"
        
        # Add project information and document details at the beginning
        project_info = st.session_state.workflow_state.get('project_info', {})
        documents = st.session_state.workflow_state.get('documents', [])
        
        consolidated_output += "PROJECT INFORMATION\n"
        consolidated_output += "-" * 30 + "\n"
        consolidated_output += f"Project Name: {project_info.get('name', 'Not specified')}\n"
        consolidated_output += f"Project Description: {project_info.get('description', 'Not specified')}\n"
        
        # Handle analysis focus including custom focus
        analysis_focus = project_info.get('focus', 'Not specified')
        if analysis_focus == "Other" and project_info.get('custom_focus'):
            analysis_focus = project_info.get('custom_focus')
        consolidated_output += f"Analysis Focus: {analysis_focus}\n"
        
        # Add files used information
        if documents:
            file_names = [doc.get('filename', 'Unknown filename') for doc in documents]
            consolidated_output += f"Files Used: {', '.join(file_names)}\n"
        else:
            consolidated_output += "Files Used: No files uploaded\n"
        
        # Add simulation explanations if available
        explanations = st.session_state.workflow_state.get('simulation_explanations', {})
        if explanations:
            consolidated_output += "SIMULATION RESULTS - EXECUTIVE SUMMARY\n"
            consolidated_output += "-" * 40 + "\n"
            consolidated_output += explanations.get('executive', 'Executive explanation not available')
            consolidated_output += "\n\n" + "=" * 60 + "\n\n"
            
            consolidated_output += "SIMULATION RESULTS - MANAGEMENT SUMMARY\n"
            consolidated_output += "-" * 40 + "\n"
            consolidated_output += explanations.get('manager', 'Management explanation not available')
            consolidated_output += "\n\n" + "=" * 60 + "\n\n"
        
        for phase_name, output_info in phase_outputs.items():
            consolidated_output += f"PHASE: {phase_name.upper()}\n"
            consolidated_output += f"Timestamp: {output_info.get('timestamp', 'Unknown')}\n"
            consolidated_output += "-" * 40 + "\n"
            
            output = output_info.get('output', {})
            if isinstance(output, dict):
                consolidated_output += json.dumps(output, indent=2)
            else:
                consolidated_output += str(output)
            
            consolidated_output += "\n\n" + "=" * 60 + "\n\n"
        
        return consolidated_output
    
    def get_vector_store_status(self) -> Dict[str, Any]:
        """Get current vector store status"""
        try:
            return self.vector_store.get_collection_info()
        except Exception as e:
            return {'error': str(e)}
    
    def get_simulation_explanations(self, audience_type: str = "executive") -> str:
        """Get layman-friendly explanations for simulation results
        
        Args:
            audience_type: Type of audience ("executive", "manager", "general")
            
        Returns:
            Formatted explanation text for the specified audience
        """
        try:
            explanations = st.session_state.workflow_state.get('simulation_explanations', {})
            
            if not explanations:
                return "No simulation explanations available. Run the simulation phase first."
            
            if audience_type not in explanations:
                available_types = list(explanations.keys())
                available_types.remove('timestamp')  # Remove timestamp from available types
                return f"Explanation for '{audience_type}' not available. Available types: {', '.join(available_types)}"
            
            return explanations[audience_type]
            
        except Exception as e:
            return f"Error retrieving simulation explanations: {str(e)}"
    
    def generate_workflow_summary(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the complete workflow execution"""
        return {
            'workflow_id': self.workflow_id,
            'execution_date': datetime.now().isoformat(),
            'total_phases': len(all_results),
            'phases_completed': list(all_results.keys()),
            'documents_processed': len(st.session_state.workflow_state.get('documents', [])),
            'success_rate': 100,  # If we reach here, all phases succeeded
            'total_agents_used': 9,
            'methodology': 'DECIDE Framework with CrewAI Multi-Agent Orchestration'
        }
