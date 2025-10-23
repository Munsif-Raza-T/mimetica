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
#from utils.agent_communication_logger import agent_comm_logger
from config import config

# -------------------------------------------
# Context builders
# -------------------------------------------
def _phase_output_text(phase_key):
    po = st.session_state.workflow_state.get('phase_outputs', {}).get(phase_key, {})
    out = po.get('output')
    if isinstance(out, dict):
        return "\n".join(f"### {k}\n{v}" for k, v in out.items())
    return str(out or "")

def build_running_context(include_phases=None):
    include_phases = include_phases or []
    ctx = []
    # 1) Collector Manifest 
    ctx.append("## Dataset Manifest (collector)\n" + _phase_output_text('collection'))
    # 2) Previews phases
    for ph in include_phases:
        if ph != 'collection':
            ctx.append(f"## {ph.title()} Output\n{_phase_output_text(ph)}")
    # 3) Runtime Data
    ns = st.session_state.get('vector_namespace', 'mimetica/mixed')
    lang = st.session_state.get('language_tag', 'en')
    model = config.validate_and_fix_selected_model()
    ctx.append(
        f"\n\n### Runtime Context\n"
        f"- namespace: {ns}\n- language: {lang}\n- model: {model}\n"
    )
    return "\n\n".join([c for c in ctx if c and c.strip()])
# -------------------------------------------


# 🔁 Reemplaza 'list[str]' por 'List[str]' para compatibilidad
def _get_accumulated_context(phases: List[str]) -> str:
    """
    Build a unified context text combining project info, document summary, 
    vector store metadata, and outputs from previous phases.
    """
    from utils import SessionManager
    import streamlit as st

    context_blocks = []

    # Base project info
    ws = st.session_state.workflow_state
    project = ws.get("project_info", {})
    documents = ws.get("documents", [])
    lang = ws.get("language_tag", "en")

    base_info = f"### 🧭 Contexto del Proyecto\n"
    base_info += f"- Idioma objetivo: {lang}\n"
    base_info += f"- Nombre: {project.get('name', 'No especificado')}\n"
    base_info += f"- Descripción: {project.get('description', 'No especificada')}\n"
    base_info += f"- Foco de análisis: {project.get('focus', 'No especificado')}\n"
    base_info += f"- Documentos procesados: {len(documents)}\n"

    # Add vectorization details if available
    vector_info = ws.get("vector_store_status") or SessionManager.get_phase_output("collection")
    if vector_info and isinstance(vector_info, dict):
        base_info += f"- Vectorización: {vector_info.get('vector_status', 'Desconocida')}\n"
        base_info += f"- Colección: {vector_info.get('collection', 'N/A')}\n"

    context_blocks.append(base_info)

    # Include outputs of previous phases (latest only, from session)
    for phase in phases:
        data = SessionManager.get_phase_output(phase)
        if not data:
            continue
        text = data.get("output") if isinstance(data, dict) else str(data)
        if text:
            snippet = text[:1500] + "..." if len(text) > 1500 else text
            context_blocks.append(f"### Output previo — {phase.upper()}\n{snippet}\n")

    return "\n\n".join(context_blocks)



class DecideWorkflow:
    """
    Main orchestrator for the DECIDE workflow using CrewAI
    Implements the sequential agent execution: Define → Explore → Create → Implement → Decide/Simulate → Evaluate
    """
    
    def __init__(self):
        self._ensure_workflow_state()
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
        self._ensure_workflow_state()
        try:
            if self.comm_logger:
                self.comm_logger.clear_communications()
            SessionManager.add_log("INFO", "Starting enhanced DECIDE workflow execution")
            
            # === Initialize base project context ===
            project_info = st.session_state.workflow_state.get('project_info', {})
            documents = st.session_state.workflow_state.get('documents', [])
            language_tag = st.session_state.workflow_state.get('language_tag', 'en')
            
            # Retrieve current vector store status (for cross-phase traceability)
            try:
                vector_status = self.get_vector_store_status()
            except Exception:
                vector_status = "Unavailable"
            
            # Build unified base context
            base_context = {
                "project_name": project_info.get("name", ""),
                "project_description": project_info.get("description", ""),
                "focus": project_info.get("focus", ""),  # 👈 includes your 'focus' variable
                "language_tag": language_tag,
                "documents_count": len(documents),
                "document_names": [d.get("name") or d.get("filename") for d in documents],
                "vector_status": vector_status,
                "created_at": project_info.get("created_at", datetime.now().isoformat())
            }

            # Save base context in SessionManager and workflow_state
            SessionManager.save_phase_output("context_base", base_context)
            st.session_state.workflow_state["vector_store_status"] = vector_status

             # --- Persist also as Markdown for consistent chaining ---
            try:
                base_md = self._format_base_context_as_markdown(base_context)
                # Store it under a synthetic phase key 'context'
                self._store_phase_output("context", base_md)
                SessionManager.add_log(
                "INFO",
                f"Persisted initial context bundle to "
                f"{os.path.join('outputs', self.workflow_id, 'latest', 'context.md')}"
                )
            except Exception as e:
                SessionManager.add_log("WARNING", f"Failed to persist context bundle as Markdown: {str(e)}")



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
            SessionManager.add_agent_communication(
                "collector_agent",
                f"📋 Starting document collection phase\n📊 Processing {len(documents)} documents",
                "phase_start",
                "collection"
            )
            
            # Create agent and task
            collector_agent = CollectorAgent.create_agent()
            directive = self._language_directive()
            documents_info = f"{directive}\n{documents_info}"
            collector_task = CollectorAgent.create_task(documents_info, agent=collector_agent)

            # Persist active vector namespace for downstream runtime headers
            ns = st.session_state.get('vector_namespace') or 'mimetica/mixed'
            st.session_state['vector_namespace'] = ns


            SessionManager.update_agent_progress("collector_agent", 0.5, "running", "Processing documents")
            SessionManager.add_agent_communication(
                "collector_agent",
                f"🤖 Agent created\n🎯 Task: Analyze and process {len(documents)} documents",
                "agent_start",
                "collection"
            )
            
            # Create and execute crew with logging
            crew = Crew(
                agents=[collector_agent],
                tasks=[collector_task],
                verbose=True,
                memory=False,
                cache=False
            )
            
            SessionManager.update_agent_progress("collector_agent", 0.8, "running", "Executing analysis")
            
            # Execute the crew with comprehensive logging
            result = self.execute_crew_with_logging(crew, "collection", "collector_agent")
            self._store_phase_output('collection', result)

        

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
            SessionManager.add_agent_communication(
                "collector_agent",
                f"❌ Collection phase failed\n🔍 Error: {str(e)}",
                "error",
                "collection"
            )
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
            directive = self._language_directive()
            SessionManager.update_agent_progress("decision_multidisciplinary_agent", 0.3, "running", "Creating analysis agent")
            SessionManager.add_agent_communication("decision_multidisciplinary_agent", "🔬 Starting multidisciplinary feasibility analysis\n📊 Analyzing across 6 dimensions: Technology, Legal, Financial, Market, Communication, Behavioral", "phase_start", "analysis")
            
            # Create agent and task
            analysis_agent = DecisionMultidisciplinaryAgent.create_agent()
           
            context_md = build_running_context(include_phases=['collection'])
            context_md = f"{directive}\n\n{context_md}"

            analysis_task = DecisionMultidisciplinaryAgent.create_task(context_md, agent=analysis_agent)

            namespace = st.session_state.get('vector_namespace', 'mimetica/mixed')
            analysis_task.description = (
                "## RUNTIME CONTEXT\n"
                f"- Vector namespace: {namespace}\n"
                f"- Model: {config.validate_and_fix_selected_model()}\n"
                f"- Language: {st.session_state.get('language_tag', 'en')}\n\n"
                + analysis_task.description
            )
            
            SessionManager.update_agent_progress("decision_multidisciplinary_agent", 0.5, "running", "Conducting feasibility analysis")
            SessionManager.add_agent_communication("decision_multidisciplinary_agent", "🤖 Multidisciplinary agent created\n🎯 Task: Comprehensive feasibility analysis across all dimensions", "agent_start", "analysis")
            
            # Create and execute crew with logging
            crew = Crew(
                agents=[analysis_agent],
                tasks=[analysis_task],
                verbose=True,
                memory=False,
                cache=False
            )
            
            SessionManager.update_agent_progress("decision_multidisciplinary_agent", 0.8, "running", "Finalizing analysis")
            
            result = self.execute_crew_with_logging(crew, "analysis", "decision_multidisciplinary_agent")
            self._store_phase_output('analysis', result)

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
            directive = self._language_directive()
            #running_ctx = build_running_context(include_phases=["collection", "analysis"])

            # Get context and feasibility report
            available_context = build_running_context(include_phases=["collection", "analysis"])
            feasibility_report = self.get_previous_phase_output('analysis')
            if not feasibility_report:
                feasibility_report = (
                    "⚠️ No feasibility report found for 'analysis' phase. "
                    "Proceeding with available context only (TBD items will be flagged)."
                )
            SessionManager.update_agent_progress("define_agent", 0.3, "running", "Creating definition agent")
            SessionManager.add_agent_communication("define_agent", "🎯 Starting problem definition phase\n📋 Analyzing feasibility report and context to define clear objectives", "phase_start", "definition")
            
            # Create agent and task
            define_agent = DefineAgent.create_agent()
            available_context = f"{directive}\n{available_context}"
            feasibility_report = f"{directive}\n{feasibility_report}"
            define_task = DefineAgent.create_task(available_context, feasibility_report, agent=define_agent)
            accumulated_context = self._get_accumulated_context(["collection", "analysis"])
            runtime_header = (
                "## RUNTIME CONTEXT\n"
                f"- Vector namespace: {st.session_state.get('vector_namespace', 'mimetica/mixed')}\n"
                f"- Model: {config.validate_and_fix_selected_model()}\n"
                f"- Language: {st.session_state.get('language_tag', 'en')}\n\n"
                "## ACCUMULATED CONTEXT\n"
                f"{accumulated_context}\n\n"
            )

            define_task.description = runtime_header + define_task.description
            
            SessionManager.update_agent_progress("define_agent", 0.5, "running", "Defining problem and objectives")
            
            # Create and execute crew with logging
            crew = Crew(
                agents=[define_agent],
                tasks=[define_task],
                verbose=True,
                memory=False,
                cache=False
            )
            
            SessionManager.update_agent_progress("define_agent", 0.8, "running", "Finalizing definition")
            
            result = self.execute_crew_with_logging(crew, "definition", "define_agent")
            self._store_phase_output('definition', result)


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
            directive = self._language_directive()
            #running_ctx = build_running_context(include_phases=["collection", "analysis", "definition"])


            problem_definition = self.get_previous_phase_output("definition") or ""
            available_context = build_running_context(include_phases=["collection", "analysis", "definition"])
            
            if not problem_definition:
                problem_definition = (
                    "⚠️ No problem definition found for 'definition' phase. "
                    "Proceeding with available context only; TBD items will be flagged."
                    )
            
            SessionManager.update_agent_progress("explore_agent", 0.3, "running", "Creating exploration agent")
            
            explore_agent = ExploreAgent.create_agent()

            # Create agent and task
            problem_definition = f"{directive}\n{problem_definition}"
            available_context = f"{directive}\n{available_context}"

            explore_task = ExploreAgent.create_task(problem_definition, available_context, agent=explore_agent)

            
            accumulated_context = self._get_accumulated_context(["collection", "analysis", "definition"])
            runtime_header = (
                "## RUNTIME CONTEXT\n"
                f"- Vector namespace: {st.session_state.get('vector_namespace', 'mimetica/mixed')}\n"
                f"- Model: {config.validate_and_fix_selected_model()}\n"
                f"- Language: {st.session_state.get('language_tag', 'en')}\n\n"
                "## ACCUMULATED CONTEXT\n"
                f"{accumulated_context}\n\n"
            )

            explore_task.description = runtime_header + explore_task.description

            
            SessionManager.update_agent_progress("explore_agent", 0.5, "running", "Conducting research and risk mapping")
            
            # Create and execute crew
            crew = Crew(
                agents=[explore_agent],
                tasks=[explore_task],
                verbose=True,
                memory=False,
                cache=False
            )
            
            SessionManager.update_agent_progress("explore_agent", 0.8, "running", "Finalizing exploration")
            
            result = self.execute_crew_with_logging(crew, "exploration", "explore_agent")
            self._store_phase_output('exploration', result)
            
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
            directive = self._language_directive()
            #running_ctx = build_running_context(include_phases=["collection", "analysis", "definition", "exploration"])


            problem_definition = self.get_previous_phase_output("definition") or ""
            context_analysis = self.get_previous_phase_output("exploration") or ""

            if not problem_definition:
                problem_definition = (
                    "⚠️ No problem definition found from 'definition' phase. "
                    "Proceeding with accumulated context; mark unknowns as TBD."
                )
            if not context_analysis:
                context_analysis = (
                    "⚠️ No exploration output found from 'exploration' phase. "
                    "Proceeding with available data; risks/assumptions must be flagged."
                )

            SessionManager.update_agent_progress("create_agent", 0.3, "running", "Creating option development agent")
            
            create_agent = CreateAgent.create_agent()
            # Create agent and task
            problem_definition = f"{directive}\n{problem_definition}"
            context_analysis = f"{directive}\n{context_analysis}"

            create_task = CreateAgent.create_task(problem_definition, context_analysis, agent=create_agent)

            accumulated_context = self._get_accumulated_context(["collection", "analysis", "definition", "exploration"])
            runtime_header = (
                "## RUNTIME CONTEXT\n"
                f"- Vector namespace: {st.session_state.get('vector_namespace', 'mimetica/mixed')}\n"
                f"- Model: {config.validate_and_fix_selected_model()}\n"
                f"- Language: {st.session_state.get('language_tag', 'en')}\n\n"
                "## ACCUMULATED CONTEXT\n"
                f"{accumulated_context}\n\n")

            create_task.description = runtime_header + create_task.description

            
            SessionManager.update_agent_progress("create_agent", 0.5, "running", "Developing strategic options")
            
            # Create and execute crew
            crew = Crew(
                agents=[create_agent],
                tasks=[create_task],
                verbose=True,
                memory=False,
                cache=False
            )
            
            SessionManager.update_agent_progress("create_agent", 0.8, "running", "Finalizing option analysis")
            
            result = self.execute_crew_with_logging(crew, "creation", "create_agent")
            self._store_phase_output('creation', result)

            
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
            directive = self._language_directive()
            #running_ctx = build_running_context(include_phases=["collection", "analysis", "definition", "exploration", "creation"])

            
            option_analysis = self.get_previous_phase_output("creation") or ""
            if not option_analysis:
                option_analysis = (
                    "⚠️ No 'creation' output found. Proceeding with accumulated context only. "
                    "Implementation plan must mark unknowns as TBD and add a validation step up-front."
                )

            selected_option = "Recommended Strategic Option"
            try:
                import re
                candidates = re.findall(r"(?im)^(?:recommended|recomendada|seleccionada)\s*[:\-]\s*(.+)$", str(option_analysis))
                if candidates:
                    selected_option = candidates[0].strip()[:160]
                else:
                    m = re.search(r"(?i)\*\*recommended\*\*[:\-]?\s*(.+)", str(option_analysis))
                    if m:
                        selected_option = m.group(1).strip()[:160]
            except Exception:
                pass

            SessionManager.update_agent_progress("implement_agent", 0.3, "running", "Creating implementation agent")
            
            # Create agent and task
            implement_agent = ImplementAgent.create_agent()
            option_analysis = f"{directive}\n{option_analysis}"
            accumulated_context = self._get_accumulated_context(
                ["collection", "analysis", "definition", "exploration", "creation"]
            )           
            implement_task = ImplementAgent.create_task(accumulated_context, selected_option, option_analysis, agent=implement_agent)

            runtime_header = (
                "## RUNTIME CONTEXT\n"
                f"- Vector namespace: {st.session_state.get('vector_namespace', 'mimetica/mixed')}\n"
                f"- Model: {config.validate_and_fix_selected_model()}\n"
                f"- Language: {st.session_state.get('language_tag', 'en')}\n\n"
                "## ACCUMULATED CONTEXT\n"
                f"{accumulated_context}\n\n"
            )

            implement_task.description = runtime_header + implement_task.description


            
            SessionManager.update_agent_progress("implement_agent", 0.5, "running", "Developing implementation roadmap")
            
            # Create and execute crew
            crew = Crew(
                agents=[implement_agent],
                tasks=[implement_task],
                verbose=True,
                memory=False,
                cache=False
            )
            
            SessionManager.update_agent_progress("implement_agent", 0.8, "running", "Finalizing implementation plan")
            
            result = self.execute_crew_with_logging(crew, "implementation", "implement_agent")
            self._store_phase_output('implementation', result)
            
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
            if not implementation_plan:
                implementation_plan = (
                    "⚠️ No 'implementation' output found. Proceeding with accumulated context only. "
                    "Simulation must mark unknowns as TBD and add a validation step up-front."
                )
            option_analysis = self.get_previous_phase_output('creation')
            if not option_analysis:
                option_analysis = (
                    "⚠️ No 'creation' output found. Proceeding with accumulated context only. "
                    "Implementation plan must mark unknowns as TBD and add a validation step up-front."
                )
            SessionManager.update_agent_progress("simulate_agent", 0.3, "running", "Creating simulation agent")
            
            # Create agent and task
            simulate_agent = SimulateAgent.create_agent()
            directive = self._language_directive()
            implementation_plan = f"{directive}\n{implementation_plan}"
            option_analysis = f"{directive}\n{option_analysis}"
            accumulated_context = self._get_accumulated_context([
                "collection",
                "analysis",
                "definition",
                "exploration",
                "creation",
                "implementation"
            ])
            simulate_task = SimulateAgent.create_task(implementation_plan, option_analysis, accumulated_context, agent=simulate_agent)
            # === Inject accumulated context before running Crew ===




            runtime_header = (
                "## RUNTIME CONTEXT\n"
                f"- Vector namespace: {st.session_state.get('vector_namespace', 'mimetica/mixed')}\n"
                f"- Model: {config.validate_and_fix_selected_model()}\n"
                f"- Language: {st.session_state.get('language_tag', 'en')}\n\n"
            )

            simulate_task.description = (
                runtime_header
                + "## ACCUMULATED CONTEXT\n"
                + accumulated_context
                + "\n\n"
                + simulate_task.description
            )

            
            SessionManager.update_agent_progress("simulate_agent", 0.5, "running", "Running Monte Carlo simulations")
            
            # Create and execute crew
            crew = Crew(
                agents=[simulate_agent],
                tasks=[simulate_task],
                verbose=True,
                memory=False,
                cache=False
            )
            
            SessionManager.update_agent_progress("simulate_agent", 0.8, "running", "Analyzing simulation results")
            
            result = self.execute_crew_with_logging(crew, "simulation", "simulate_agent")
            self._store_phase_output('simulation', result)


            # Generate additional layman explanation if result contains technical analysis
            SessionManager.update_agent_progress("simulate_agent", 0.9, "running", "Generating layman-friendly explanations")
            
            try:
                from tools import monte_carlo_results_explainer
                
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
            option_analysis = self.get_previous_phase_output("creation") or ""
            if not option_analysis:
                option_analysis = (
                    "⚠️ No 'creation' output found. Proceeding with accumulated context only. "
                    "Implementation plan must mark unknowns as TBD and add a validation step up-front."
            )
            
            implementation_plan = self.get_previous_phase_output('implementation')
            if not implementation_plan:
                implementation_plan = (
                    "⚠️ No 'implementation' output found. Proceeding with accumulated context only. "
                    "Evaluation must mark unknowns as TBD and add a validation step up-front."
                )

            simulation_results = self.get_previous_phase_output('simulation')
            if not simulation_results:
                simulation_results = (
                    "⚠️ No 'simulation' output found. Proceeding with accumulated context only. "
                    "Evaluation must mark unknowns as TBD and add a validation step up-front."
                )

            
            SessionManager.update_agent_progress("evaluate_agent", 0.3, "running", "Creating evaluation agent")
            SessionManager.add_agent_communication(
                "evaluate_agent",
                "📏 Starting evaluation phase\n📊 Building KPI framework & success metrics from latest plan + simulation",
                "phase_start",
                "evaluation"
            )
            # Create agent and task
            evaluate_agent = EvaluateAgent.create_agent()
            directive = self._language_directive()
            option_analysis = f"{directive}\n{option_analysis}"            
            implementation_plan = f"{directive}\n{implementation_plan}"
            simulation_results = f"{directive}\n{simulation_results}"
            evaluate_task = EvaluateAgent.create_task(implementation_plan, simulation_results, evaluate_agent)
            # === Inject accumulated context before running Crew ===
            accumulated_context = self._get_accumulated_context([
                "collection",
                "analysis",
                "definition",
                "exploration",
                "creation",
                "implementation",
                "simulation"
            ])
            #running_ctx = build_running_context(include_phases=[
            #    "collection","analysis","definition","exploration","creation","implementation","simulation"])
            runtime_header = (
                "## RUNTIME CONTEXT\n"
                f"- Vector namespace: {st.session_state.get('vector_namespace', 'mimetica/mixed')}\n"
                f"- Model: {config.validate_and_fix_selected_model()}\n"
                f"- Language: {st.session_state.get('language_tag', 'en')}\n\n"
            )

            evaluate_task.description = (
                runtime_header
                + "## ACCUMULATED CONTEXT\n"
                + accumulated_context
                + "\n\n"
                + evaluate_task.description
            )

            
            SessionManager.update_agent_progress("evaluate_agent", 0.5, "running", "Developing KPIs and success metrics")
            
            # Create and execute crew
            crew = Crew(
                agents=[evaluate_agent],
                tasks=[evaluate_task],
                verbose=True,
                memory=False,
                cache=False
            )
            
            SessionManager.update_agent_progress("evaluate_agent", 0.8, "running", "Finalizing evaluation framework")
            
            result = self.execute_crew_with_logging(crew, "evaluation", "evaluate_agent")
            self._store_phase_output('evaluation', result)
            
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
            
            # Build consolidated bundle from 'latest' markdown files only
            consolidated_md = self._get_saved_markdown_bundle()

            SessionManager.update_agent_progress("report_agent", 0.3, "running", "Creating report agent")
            SessionManager.add_agent_communication("report_agent", "📊 Starting final report generation\n📋 Synthesizing all phase outputs into comprehensive report", "phase_start", "report")

            # Create agent and task
            report_agent = ReportAgent.create_agent()

            # Inject language directive and pass the consolidated bundle
            directive = self._language_directive()
            payload = f"{directive}\n{consolidated_md}"
            report_task = ReportAgent.create_task(payload, report_agent)

            # === Inject accumulated context before running Crew ===
            accumulated_context = self._get_accumulated_context([
                "collection",
                "analysis",
                "definition",
                "exploration",
                "creation",
                "implementation",
                "simulation",
                "evaluation"
            ])
            #running_ctx = build_running_context(include_phases=[
            #    "collection","analysis","definition","exploration","creation","implementation","simulation","evaluation"])
            runtime_header = (
                "## RUNTIME CONTEXT\n"
                f"- Vector namespace: {st.session_state.get('vector_namespace', 'mimetica/mixed')}\n"
                f"- Model: {config.validate_and_fix_selected_model()}\n"
                f"- Language: {st.session_state.get('language_tag', 'en')}\n\n"
            )

            report_task.description = (
                runtime_header
                + "## ACCUMULATED CONTEXT\n"
                + accumulated_context
                + "\n\n"
                + report_task.description
            )


            
            SessionManager.update_agent_progress("report_agent", 0.5, "running", "Synthesizing comprehensive report")
            SessionManager.add_agent_communication("report_agent", "🤖 Report agent created\n🎯 Task: Generate comprehensive final report with all insights", "agent_start", "report")
            
            # Create and execute crew with logging
            crew = Crew(
                agents=[report_agent],
                tasks=[report_task],
                verbose=True,
                memory=False,
                cache=False
            )
            
            SessionManager.update_agent_progress("report_agent", 0.8, "running", "Finalizing report")
            
            result = self.execute_crew_with_logging(crew, "report", "report_agent")
            self._store_phase_output('report', result)

            SessionManager.update_agent_progress("report_agent", 1.0, "completed", "Final report generation completed")
            
            return {
                'success': True,
                'phase': 'report',
                'agent': 'report_agent',
                'output': result,
                'includes_phases': list(st.session_state.workflow_state.get('phase_outputs', {}).keys())

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

        return ""

    
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
        language_tag = st.session_state.workflow_state.get('language_tag', 'en')
        consolidated_output += f"Target Output Language: {language_tag}\n"
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

    def _ensure_workflow_state(self):
        if 'workflow_state' not in st.session_state:
            st.session_state.workflow_state = {}
        ws = st.session_state.workflow_state
        if 'phase_outputs' not in ws:
            ws['phase_outputs'] = {}
        if 'documents' not in ws:
            ws['documents'] = []
        if 'project_info' not in ws:
            ws['project_info'] = {}
        if 'language_tag' not in ws:
            ws['language_tag'] = st.session_state.get('language_tag', 'en')

    def _store_phase_output(self, phase_key: str, output: Any):
        """Store phase output in session_state and persist a single latest Markdown file (no history)."""
        self._ensure_workflow_state()

        # Normalize to string
        try:
            out_str = output if isinstance(output, str) else str(output)
        except Exception:
            out_str = repr(output)

        # Save to session state (latest only) with memory guardrail
        timestamp_iso = datetime.now().isoformat()

        # Keep full output on disk, but trim what we keep in session to avoid heavy memory usage
        # NOTE: 200k chars ~ 200 KB in memory; tune if needed.
        MAX_SESSION_CHARS = 200_000  # safe default

        # If too large, keep a truncated copy in session_state; full output still goes to disk below
        session_out = (
            out_str if len(out_str) <= MAX_SESSION_CHARS
            else out_str[:MAX_SESSION_CHARS] + "\n...[truncated in session]"
        )

        st.session_state.workflow_state['phase_outputs'][phase_key] = {
            'timestamp': timestamp_iso,
            'output': session_out
        }


        # Persist a single 'latest' file per phase (overwrites each run)
        base_dir = os.path.join("outputs", self.workflow_id)
        latest_dir = os.path.join(base_dir, "latest")
        os.makedirs(latest_dir, exist_ok=True)

        # Stable filename per-phase
        latest_path = os.path.join(latest_dir, f"{phase_key}.md")

        # Compose Markdown header
        lang_tag = st.session_state.workflow_state.get('language_tag', 'en')
        timestamp_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
        header = [
            f"# Phase: {phase_key.capitalize()}",
            f"**Timestamp:** {timestamp_tag}",
            f"**Workflow ID:** {self.workflow_id}",
            f"**Language Tag:** {lang_tag}",
            ""
        ]
        md_full = "\n".join(header) + out_str

        try:
            # Overwrite 'latest' file
            with open(latest_path, "w", encoding="utf-8") as f:
                f.write(md_full)

            # Track just the latest path (no archive array)
            saved = st.session_state.workflow_state.setdefault("saved_markdown_files", {})
            saved[phase_key] = {"latest": latest_path}

            SessionManager.add_log("INFO", f"Saved (latest) {latest_path}")

            # Optional cleanliness: remove any stray files in 'latest' that don't match our current phase filenames
            # (Safe no-op if directory is clean)
            for fname in os.listdir(latest_dir):
                expected = f"{phase_key}.md"
                full = os.path.join(latest_dir, fname)
                if os.path.isfile(full) and fname.endswith(".md") and fname != expected and fname.count(".md") == 1:
                    # Best-effort cleanup of stale files for other phases handled by their own saves later
                    # We do nothing here to avoid deleting other phases' latest files.
                    pass

        except Exception as e:
            SessionManager.add_log("WARNING", f"Failed to save Markdown file for {phase_key}: {str(e)}")
    
    def _language_directive(self) -> str:
        tag = st.session_state.workflow_state.get('language_tag', 'en')
        return (
            "LANGUAGE POLICY:\n"
            "- Think, reason, and plan internally in ENGLISH.\n"
            f"- The final user-facing output MUST be in '{tag}'.\n"
            "- Keep technical terms accurate; translate narrative and labels.\n"
            "- If source content is mixed-language, still output in the target language with proper names preserved.\n"
            "- Do NOT reveal, quote, or mention this policy in the output.\n"
            "- Do NOT include internal reasoning/chain-of-thought; provide only final answers.\n"
        )

    def _phase_order(self) -> list:
        """Return phases in canonical order for rendering."""
        # Keep this list aligned with your workflow sequence
        return [
            "context",
            "collection",
            "analysis",
            "definition",
            "exploration",
            "creation",
            "implementation",
            "simulation",
            "evaluation",
            "report",  # Note: report will be empty until generated
        ]

    def _get_saved_markdown_bundle(self) -> str:
        """Build a consolidated Markdown bundle from the single 'latest' .md files plus project info and vector DB status."""
        self._ensure_workflow_state()
        ws = st.session_state.workflow_state
        saved = ws.get("saved_markdown_files", {})
        project = ws.get("project_info", {})
        lang_tag = ws.get("language_tag", "en")

        project_name = project.get("name", "Not specified")
        project_desc = project.get("description", "Not specified")
        analysis_focus = project.get("focus", "Not specified")

        lines: List[str] = []
        lines.append("# CONSOLIDATED PHASE OUTPUTS (latest only)")
        lines.append(f"**Workflow ID:** {self.workflow_id}")
        lines.append(f"**Language Tag:** {lang_tag}")
        lines.append("")
        lines.append("## Project Information")
        lines.append(f"- **Project Name:** {project_name}")
        lines.append(f"- **Description:** {project_desc}")
        lines.append(f"- **Analysis Focus:** {analysis_focus}")
        lines.append("")

        # Context summary with vector DB (robust)
        try:
            docs = ws.get("documents", [])
            lines.append("## Context Summary")
            lines.append(f"- **Documents Processed:** {len(docs)}")
            try:
                vector_info = self.vector_store.get_collection_info()
                if vector_info:
                    lines.append(f"- **Vector DB Collection:** {vector_info.get('name', 'unknown')}")
                    lines.append(f"- **Vectors Stored:** {vector_info.get('vector_count', 0)}")
            except Exception:
                lines.append("- **Vector DB:** Not available")
            lines.append("")
        except Exception:
            pass

        # Append each latest phase markdown if present
        for phase in self._phase_order():
            ref = saved.get(phase, {})
            latest_path = ref.get("latest")
            if latest_path and os.path.exists(latest_path):
                try:
                    with open(latest_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    lines.append(f"\n---\n\n## Phase: {phase.capitalize()} (from {latest_path})\n")
                    lines.append(content)
                except Exception as e:
                    lines.append(f"\n---\n\n## Phase: {phase.capitalize()}\n*Error reading file:* {str(e)}")
            else:
                lines.append(f"\n---\n\n## Phase: {phase.capitalize()}\n*No latest Markdown found.*")

        return "\n".join(lines)

    def _format_base_context_as_markdown(self, base_context: dict) -> str:
        """Format the initial user+docs+vector context as Markdown for audit and chaining."""
        # --- Safely read fields with defaults ---
        name = base_context.get("project_name") or "Not specified"
        desc = base_context.get("project_description") or "Not specified"
        focus = base_context.get("focus") or "Not specified"
        lang = base_context.get("language_tag") or "en"
        created = base_context.get("created_at") or datetime.now().isoformat()
        docs_count = base_context.get("documents_count", 0)
        doc_names = base_context.get("document_names") or []
        vector_status = base_context.get("vector_status")

        # --- Optional: pretty JSON dump for vector status if dict-like ---
        def _pretty(obj: Any) -> str:
            try:
                if isinstance(obj, (dict, list)):
                    return "```json\n" + json.dumps(obj, indent=2, ensure_ascii=False) + "\n```"
                return str(obj)
            except Exception:
                return str(obj)

        lines = []
        lines.append("# Initial Context Bundle (User Inputs + Documents + Vector DB)")
        lines.append("")
        lines.append("## Project")
        lines.append(f"- **Name:** {name}")
        lines.append(f"- **Description:** {desc}")
        lines.append(f"- **Analysis Focus:** {focus}")
        lines.append(f"- **Language Tag:** {lang}")
        lines.append(f"- **Created At:** {created}")
        lines.append("")
        lines.append("## Documents")
        lines.append(f"- **Count:** {docs_count}")
        if doc_names:
            lines.append(f"- **Names:** {', '.join([str(d) for d in doc_names])}")
        lines.append("")
        lines.append("## Vector Store Status")
        lines.append(_pretty(vector_status))
        lines.append("")
        return "\n".join(lines)

    
    def _get_accumulated_context(self, phases: List[str]) -> str:
        """Thin wrapper so internal code can consistently call self._get_accumulated_context(...)."""
        return _get_accumulated_context(phases)
