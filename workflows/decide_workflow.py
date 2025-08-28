import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st
from crewai import Crew, Task
import json

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
    
    def run_complete_workflow(self) -> Dict[str, Any]:
        """Run the complete DECIDE workflow from start to finish"""
        try:
            SessionManager.add_log("INFO", "Starting complete DECIDE workflow execution")
            
            # Define the sequential phases
            phases = [
                ('collection', self.run_collection_phase),
                ('analysis', self.run_multidisciplinary_analysis_phase),
                ('definition', self.run_define_phase),
                ('exploration', self.run_explore_phase),
                ('creation', self.run_create_phase),
                ('implementation', self.run_implement_phase),
                ('simulation', self.run_simulate_phase),
                ('evaluation', self.run_evaluate_phase),
                ('report', self.run_report_phase)
            ]
            
            # Execute phases sequentially
            all_results = {}
            
            for phase_name, phase_function in phases:
                SessionManager.add_log("INFO", f"Starting {phase_name} phase")
                SessionManager.update_phase(phase_name, 'in_progress')
                
                try:
                    phase_result = phase_function()
                    
                    if phase_result.get('success'):
                        all_results[phase_name] = phase_result
                        SessionManager.update_phase(phase_name, 'completed')
                        SessionManager.save_phase_output(phase_name, phase_result)
                        SessionManager.add_log("INFO", f"Completed {phase_name} phase successfully")
                    else:
                        error_msg = f"Phase {phase_name} failed: {phase_result.get('error', 'Unknown error')}"
                        SessionManager.add_log("ERROR", error_msg)
                        return {
                            'success': False,
                            'error': error_msg,
                            'completed_phases': list(all_results.keys()),
                            'failed_phase': phase_name
                        }
                
                except Exception as e:
                    error_msg = f"Exception in {phase_name} phase: {str(e)}"
                    SessionManager.add_log("ERROR", error_msg)
                    return {
                        'success': False,
                        'error': error_msg,
                        'completed_phases': list(all_results.keys()),
                        'failed_phase': phase_name
                    }
            
            # Workflow completed successfully
            SessionManager.update_phase('completed', 'completed')
            SessionManager.add_log("INFO", "Complete DECIDE workflow executed successfully")
            
            return {
                'success': True,
                'workflow_id': self.workflow_id,
                'completed_phases': list(all_results.keys()),
                'phase_results': all_results,
                'summary': self.generate_workflow_summary(all_results)
            }
        
        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            SessionManager.add_log("ERROR", error_msg)
            return {
                'success': False,
                'error': error_msg,
                'workflow_id': self.workflow_id
            }
    
    def run_single_phase(self, phase_name: str) -> Dict[str, Any]:
        """Run a single phase of the workflow"""
        try:
            SessionManager.add_log("INFO", f"Running single phase: {phase_name}")
            
            phase_functions = {
                'collection': self.run_collection_phase,
                'analysis': self.run_multidisciplinary_analysis_phase,
                'definition': self.run_define_phase,
                'exploration': self.run_explore_phase,
                'creation': self.run_create_phase,
                'implementation': self.run_implement_phase,
                'simulation': self.run_simulate_phase,
                'evaluation': self.run_evaluate_phase,
                'report': self.run_report_phase
            }
            
            if phase_name not in phase_functions:
                return {
                    'success': False,
                    'error': f"Unknown phase: {phase_name}",
                    'available_phases': list(phase_functions.keys())
                }
            
            # Execute the specific phase
            SessionManager.update_phase(phase_name, 'in_progress')
            result = phase_functions[phase_name]()
            
            if result.get('success'):
                SessionManager.update_phase(phase_name, 'completed')
                SessionManager.save_phase_output(phase_name, result)
                SessionManager.add_log("INFO", f"Single phase {phase_name} completed successfully")
            else:
                SessionManager.add_log("ERROR", f"Single phase {phase_name} failed: {result.get('error')}")
            
            return result
        
        except Exception as e:
            error_msg = f"Single phase execution failed: {str(e)}"
            SessionManager.add_log("ERROR", error_msg)
            return {
                'success': False,
                'error': error_msg,
                'phase': phase_name
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
            
            # Create agent and task
            collector_agent = CollectorAgent.create_agent()
            collector_task = CollectorAgent.create_task(documents_info)
            
            SessionManager.update_agent_progress("collector_agent", 0.5, "running", "Processing documents")
            
            # Create and execute crew
            crew = Crew(
                agents=[collector_agent],
                tasks=[collector_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("collector_agent", 0.8, "running", "Executing analysis")
            
            # Execute the crew
            result = crew.kickoff()
            
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
            
            # Create agent and task
            analysis_agent = DecisionMultidisciplinaryAgent.create_agent()
            analysis_task = DecisionMultidisciplinaryAgent.create_task(context_data)
            
            SessionManager.update_agent_progress("decision_multidisciplinary_agent", 0.5, "running", "Conducting feasibility analysis")
            
            # Create and execute crew
            crew = Crew(
                agents=[analysis_agent],
                tasks=[analysis_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("decision_multidisciplinary_agent", 0.8, "running", "Finalizing analysis")
            
            result = crew.kickoff()
            
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
            
            # Create agent and task
            define_agent = DefineAgent.create_agent()
            define_task = DefineAgent.create_task(context_data, feasibility_report)
            
            SessionManager.update_agent_progress("define_agent", 0.5, "running", "Defining problem and objectives")
            
            # Create and execute crew
            crew = Crew(
                agents=[define_agent],
                tasks=[define_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("define_agent", 0.8, "running", "Finalizing definition")
            
            result = crew.kickoff()
            
            SessionManager.update_agent_progress("define_agent", 1.0, "completed", "Problem definition completed")
            
            return {
                'success': True,
                'phase': 'definition',
                'agent': 'define_agent',
                'output': result
            }
        
        except Exception as e:
            SessionManager.update_agent_progress("define_agent", 0.0, "failed", f"Error: {str(e)}")
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
            
            SessionManager.update_agent_progress("simulate_agent", 1.0, "completed", "Monte Carlo simulation completed")
            
            return {
                'success': True,
                'phase': 'simulation',
                'agent': 'simulate_agent',
                'output': result,
                'simulation_runs': config.MONTE_CARLO_RUNS
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
            
            # Create agent and task
            report_agent = ReportAgent.create_agent()
            report_task = ReportAgent.create_task(all_phase_outputs)
            
            SessionManager.update_agent_progress("report_agent", 0.5, "running", "Synthesizing comprehensive report")
            
            # Create and execute crew
            crew = Crew(
                agents=[report_agent],
                tasks=[report_task],
                verbose=True
            )
            
            SessionManager.update_agent_progress("report_agent", 0.8, "running", "Finalizing report")
            
            result = crew.kickoff()
            
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
            context += f"- Analysis Focus: {project_info.get('focus', 'General')}\n\n"
        
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
