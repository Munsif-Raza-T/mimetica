import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import io
import time
import base64
import re
from typing import Dict, List, Any
from PIL import Image
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()
from datetime import datetime, timedelta
import threading




# Import custom modules
from config import config
from utils import AuthManager, SessionManager, DocumentProcessor, VectorStore, PDFGenerator
from utils.docx_generator import DocxGenerator
from workflows.decide_workflow import DecideWorkflow
from utils.token_batch_manager import TokenBatchManager  # Import the TokenBatchManager

# Page configuration
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    
    # Initialize session
    SessionManager.init_session()
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4 0%, #ff7f0e 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        text-align: center;
    }
    .phase-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #f8f9fa;
    }
    .completed {
        border-color: #28a745;
        background: #d4edda;
    }
    .in-progress {
        border-color: #ffc107;
        background: #fff3cd;
    }
    .pending {
        border-color: #6c757d;
        background: #e9ecef;
    }
    .workflow-completed {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        border: 3px solid #28a745;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        color: white;
        text-align: center;
    }
    .workflow-completed h2 {
        color: white;
        margin-bottom: 1rem;
    }
    .view-results-btn {
        background: linear-gradient(45deg, #007bff, #0056b3);
        border: none;
        border-radius: 10px;
        padding: 1rem 2rem;
        font-size: 1.2rem;
        font-weight: bold;
        color: white;
        box-shadow: 0 4px 8px rgba(0,123,255,0.3);
        transition: all 0.3s ease;
    }
    .view-results-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,123,255,0.4);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with logo
    # Encode the logo image
    import base64
    logo_path = "assets/logo_white.png"
    
    try:
        with open(logo_path, "rb") as img_file:
            logo_data = base64.b64encode(img_file.read()).decode()
        
        st.markdown(f"""
        <div class="main-header">
            <div style="text-align: center;">
                <img src="data:image/png;base64,{logo_data}" 
                     style="height: 60px; margin-bottom: 10px;" 
                     alt="MIMÉTICA Logo">
            </div>
            <p style="color: white; text-align: center; margin: 0;">{config.APP_DESCRIPTION}</p>
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback to text if logo file is not found
        st.markdown(f"""
        <div class="main-header">
            <h1>{config.APP_TITLE}</h1>
            <p style="color: white; text-align: center; margin: 0;">{config.APP_DESCRIPTION}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Authentication check
    AuthManager.require_auth()
    
    # Sidebar
    create_sidebar()
    
    # Main content area
    current_phase = st.session_state.workflow_state.get('current_phase', 'setup')
    
    if current_phase == 'setup':
        show_setup_page()
    elif current_phase == 'workflow':
        show_workflow_page()
    elif current_phase == 'results':
        show_results_page()
    else:
        show_dashboard_page()

def create_sidebar():
    """Create application sidebar"""
    with st.sidebar:
        # Header images
        try:
            icon_path = "assets/icon.png"
            with open(icon_path, "rb") as icon_file:
                icon_data = base64.b64encode(icon_file.read()).decode()

            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 10px;">
                <img src="data:image/png;base64,{icon_data}" 
                     style="height: 80px;" 
                     alt="Icon">
            </div>
            """, unsafe_allow_html=True)

            logo_red_path = "assets/logo_red.png"
            with open(logo_red_path, "rb") as logo_file:
                logo_data = base64.b64encode(logo_file.read()).decode()

            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{logo_data}" 
                     style="height: 65px;" 
                     alt="MIMÉTICA Logo">
            </div>
            """, unsafe_allow_html=True)

        except FileNotFoundError:
            st.info("Images not found in assets folder")

        # (Optional) Language & Model — consider removing for non-technical users
        st.subheader("Lenguage & Model Preferences")

        lang_options = {"English": "en", "Spanish": "es"}
        current_label = next(
            (label for label, tag in lang_options.items() if tag == st.session_state.get("language_tag", "en")),
            "English"
        )
        selected_label = st.selectbox(
            "Language",
            list(lang_options.keys()),
            index=list(lang_options.keys()).index(current_label),
            key="selected_language"
        )
        st.session_state["language_tag"] = lang_options[selected_label]
        if "workflow_state" not in st.session_state:
            st.session_state["workflow_state"] = {}
        st.session_state["workflow_state"]["language_tag"] = st.session_state["language_tag"]

        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = config.DEFAULT_MODEL

        model_options = {}
        for model_key, model_config in config.AVAILABLE_MODELS.items():
            provider = model_config['provider'].upper()
            name = model_config['name']
            model_options[model_key] = f"{provider}: {name}"

        selected_model_key = st.selectbox(
            "Choose model:",
            options=list(model_options.keys()),
            index=list(model_options.keys()).index(st.session_state.selected_model),
            format_func=lambda x: model_options[x],
            help="Select the AI model for workflow processing",
            key="select_model_sidebar"
        )

        selected_model_config = config.AVAILABLE_MODELS[selected_model_key]
        st.caption(f"💡 {selected_model_config['description']}")
        st.caption(f"🎯 Good for: {selected_model_config['good_for']}")

        if selected_model_key != st.session_state.selected_model:
            if st.button("🔄 Update Model", key="btn_update_model_sidebar", type="primary", use_container_width=True):
                st.session_state.selected_model = selected_model_key
                st.success(f"✅ Model updated to {model_options[selected_model_key]}")
                st.rerun()

        # Progress (no per-phase list)
        st.subheader("Progress")

        TOTAL_PHASES = 10
        completed_phases = st.session_state.workflow_state.get('completed_phases', [])
        workflow_completed = st.session_state.workflow_state.get('workflow_completed', False)

        completed_count = len(completed_phases)
        completion_percent = int((completed_count / TOTAL_PHASES) * 100)

        st.progress(completion_percent / 100)
        if workflow_completed:
            st.caption("🎉 Progress: 100% — Workflow completed!")
        else:
            st.caption(f"Progress: {completion_percent}% ({completed_count}/{TOTAL_PHASES})")

        st.divider()

        # Quick actions (single block only)
        st.subheader("⚡ Quick Actions")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("New Workflow", key="btn_new_workflow_sidebar", use_container_width=True):
                SessionManager.reset_workflow()
                st.rerun()

        with col2:
            if st.button("View Results", key="btn_view_results_sidebar", use_container_width=True, type="primary"):
                st.session_state.workflow_state['current_phase'] = 'results'
                st.rerun()

        # Logout (no vector store clearing)
        #st.divider()
        if st.button("🚪 Logout", key="btn_logout_sidebar", use_container_width=True):
            AuthManager.logout()
            st.session_state['workflow_state'] = {'current_phase': 'setup'}
            st.rerun()

def show_setup_page():
    """Display simplified setup and document upload page"""
    st.header("📋 Project Setup & Document Upload")

    # define documents BEFORE using it
    documents = st.session_state.workflow_state.get('documents', [])

    col1, col2 = st.columns([2, 1])

    with col1:
        # Project information (Name + Description + Objective)
        st.subheader("Project Information")

        project_name = st.text_input("Project Name", value="Strategic Initiative Analysis")
        project_description = st.text_area(
            "Project Description",
            value="Comprehensive analysis of strategic initiative using MIMÉTICA methodology"
        )
        # >>> NEW: Objective (business goal)
        project_objective = st.text_area(
            "Objective",
            value="Define the main business goal and expected outcome in one paragraph."
        )

        if st.button("💾 Save Project Info", type="primary", use_container_width=True, key="btn_save_project_info"):
            st.session_state.workflow_state['project_info'] = {
                'name': project_name,
                'description': project_description,
                'objective': project_objective,  # <<< keep the objective
                'created_at': datetime.now().isoformat()
            }
            st.success("✅ Project information saved!")

        # Document upload (no technical stats)
        st.subheader("Document Upload")
        uploaded_files = st.file_uploader(
            "Upload your documents (PDF, Word, CSV, Excel)",
            type=['pdf', 'docx', 'doc', 'csv', 'xlsx', 'xls'],
            accept_multiple_files=True,
            help="Upload documents to be analyzed"
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) selected")
            if st.button("🔄 Process Documents", key="btn_process_docs_setup", type="primary", use_container_width=True):
                process_documents(uploaded_files)

        if documents and st.button("🚀 Start DECIDE Workflow", key="btn_start_workflow_setup", type="primary", use_container_width=True):
            start_workflow()

    with col2:
        st.subheader("Current Status")
        if documents:
            st.write(f"**Documents processed:** {len(documents)}")
        else:
            st.info("No documents uploaded yet")

        if documents and st.button("🚀 Start DECIDE Workflow", key="btn_start_workflow_setup_right", type="primary", use_container_width=True):
            start_workflow()

def process_documents(uploaded_files):
    """Process uploaded documents"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    doc_processor = DocumentProcessor()
    vector_store = VectorStore(collection_name="mimetica") if 'collection_name' in VectorStore.__init__.__code__.co_varnames else VectorStore()
    
    processed_documents = []
    
    for i, uploaded_file in enumerate(uploaded_files):
        progress = (i + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"Processing {uploaded_file.name}...")
        # Process document
        doc_result = doc_processor.process_file(uploaded_file)
        if doc_result:
            processed_documents.append(doc_result)
            # Vectorize document always into 'mimetica' collection
            if vector_store.vectorize_document(doc_result):
                SessionManager.add_log("INFO", f"Successfully processed and vectorized {uploaded_file.name}")
            else:
                SessionManager.add_log("WARNING", f"Failed to vectorize {uploaded_file.name}")
        else:
            SessionManager.add_log("ERROR", f"Failed to process {uploaded_file.name}")
    
    # Update session state
    st.session_state.workflow_state['documents'] = processed_documents
    
    progress_bar.progress(1.0)
    status_text.text("✅ All documents processed!")
    
    st.success(f"Successfully processed {len(processed_documents)} documents")
    SessionManager.add_log("INFO", f"Document processing completed: {len(processed_documents)} documents")

def start_workflow():
    """Initialize and start the DECIDE workflow"""
    try:
        # Update session state
        SessionManager.update_phase('workflow', 'in_progress')
        
        
        # Initialize workflow
        if 'workflow_instance' not in st.session_state:
            st.session_state.workflow_instance = DecideWorkflow()
            
            # Initialize image manager for the session
            from utils.image_manager import image_manager
            session_id = f"session_{int(time.time())}"
            image_manager.setup_session_directory(session_id)
            st.session_state.image_session_id = session_id
        
        st.success("🚀 DECIDE Workflow started successfully!")
        SessionManager.add_log("INFO", "DECIDE Workflow initiated")
        
        # Navigate to workflow page
        st.rerun()
        
    except Exception as e:
        st.error(f"Failed to start workflow: {str(e)}")
        SessionManager.add_log("ERROR", f"Workflow start failed: {str(e)}")

def show_workflow_page():
    """Display simplified workflow execution page"""
    st.header("🔄 DECIDE Workflow")

    # Ensure the workflow instance exists
    if 'workflow_instance' not in st.session_state:
        st.error("Workflow not initialized. Please return to setup.")
        if st.button("← Back to Setup", key="btn_back_to_setup_workflow"):
            st.session_state.workflow_state['current_phase'] = 'setup'
            st.rerun()
        return

    # ✅ define before using
    workflow_completed = st.session_state.workflow_state.get('workflow_completed', False)

    if workflow_completed:
        st.success("🎉 Workflow completed successfully!")
        if st.button("View Results", key="btn_view_results_workflow", type="primary", use_container_width=True):
            st.session_state.workflow_state['current_phase'] = 'results'
            st.rerun()
        return

    # Minimal controls (single Run button)
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("▶️ Run", key="btn_run_workflow", type="primary", use_container_width=True):
            run_complete_workflow(st.session_state.workflow_instance)

    with col2:

        project_info = st.session_state.workflow_state.get('project_info', {})
        docs = st.session_state.workflow_state.get('documents', [])
        st.markdown("""
        <div style="background:#f6f8fc;border:1px solid #e5e7eb;border-radius:10px;padding:16px;">
        <h4 style="margin:0 0 8px 0;">Project overview</h4>
        </div>
        """, unsafe_allow_html=True)

        st.write(f"**Name:** {project_info.get('name', '—')}")
        st.write(f"**Description:** {project_info.get('description', '—')}")
        st.write(f"**Objective:** {project_info.get('objective', '—')}")
        st.write(f"**Documents uploaded:** {len(docs)}")

        st.markdown("""
        **About MIMÉTICA**  
        MIMÉTICA aplica la metodología DECIDE para transformar documentos en
        conocimiento accionable: define el problema, explora el contexto, crea opciones,
        planifica la implementación, simula escenarios y evalúa resultados en un informe claro.
        """)

        # Barra de progreso simple
        completed = len(st.session_state.workflow_state.get('completed_phases', []))
        total = 10
        st.progress(completed / total)
        st.caption(f"Progress: {completed}/{total} phases")


    st.caption(f"Progress: {completed}/{total} phases")

def run_complete_workflow(workflow):
    """Run the DECIDE workflow (minimal user messaging)"""
    try:
        documents = st.session_state.workflow_state.get('documents', [])
        if not documents:
            st.error("No documents found. Please upload documents first.")
            return

        with st.spinner("Running analysis…"):
            result = workflow.run_complete_workflow()

        if result.get('success'):
            # ✅ solo mensaje final + guardar resultados
            if 'phase_results' in result:
                st.session_state.workflow_state['last_workflow_result'] = result
                for phase_name, phase_result in result['phase_results'].items():
                    SessionManager.save_phase_output(phase_name, phase_result)

            st.session_state.workflow_state['workflow_completed'] = True
            st.session_state.workflow_state['workflow_completion_time'] = datetime.now().isoformat()
            st.success("Analysis completed. View Results to see the final report.")
            return result
        else:
            st.error("Workflow failed. Please try again.")
            return result

    except Exception as e:
        st.error("Workflow execution failed.")
        SessionManager.add_log("ERROR", f"Workflow execution failed: {str(e)}")
        return {'success': False, 'error': str(e)}


def display_workflow_logs():
    """Display workflow execution logs"""
    if st.session_state.get('logs'):
        st.subheader("Workflow Execution Logs")
        for log_entry in st.session_state.logs:
            if log_entry.get('level') == 'ERROR':
                st.error(f"[{log_entry.get('timestamp', '')}] {log_entry.get('message', '')}")
            elif log_entry.get('level') == 'WARNING':
                st.warning(f"[{log_entry.get('timestamp', '')}] {log_entry.get('message', '')}")
            else:
                st.info(f"[{log_entry.get('timestamp', '')}] {log_entry.get('message', '')}")
    else:
        st.info("No logs available")


def show_workflow_progress():
    """Display detailed workflow progress"""
    st.subheader("Detailed Workflow Progress")
    
    # Progress metrics
    completed_phases = st.session_state.workflow_state.get('completed_phases', [])
    total_phases = 9  # Total number of phases in DECIDE workflow
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Completed Phases", len(completed_phases))
    
    with col2:
        st.metric("Remaining Phases", total_phases - len(completed_phases))
    
    with col3:
        completion_rate = len(completed_phases) / total_phases * 100
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    # Token processing statistics if available
    phase_outputs = st.session_state.workflow_state.get('phase_outputs', {})
    for phase_name, phase_data in phase_outputs.items():
        if 'batch_processing_stats' in phase_data:
            st.subheader(f" {phase_name.title()} - Batch Processing Stats")
            stats = phase_data['batch_processing_stats']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Documents", stats.get('total_documents', 0))
            with col2:
                st.metric("Chunks", stats.get('total_chunks', 0))
            with col3:
                st.metric("Batches", stats.get('total_batches', 0))
            with col4:
                st.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
    
    # Progress timeline
    st.subheader("Progress Timeline")
    
    if phase_outputs:
        timeline_data = []
        for phase, output_info in phase_outputs.items():
            timeline_data.append({
                'Phase': phase.replace('_', ' ').title(),
                'Timestamp': output_info.get('timestamp', ''),
                'Status': 'Completed',
                'Batches': output_info.get('batch_processing_stats', {}).get('total_batches', 'N/A')
            })
        
        if timeline_data:
            df = pd.DataFrame(timeline_data)
            st.dataframe(df, use_container_width=True)
    else:
        st.info("No phase completion data available")

def show_results_page():
    """Display simplified workflow results (final report only)"""
    st.header("📊 Results")

    phase_outputs = st.session_state.workflow_state.get('phase_outputs', {})
    if not phase_outputs:
        st.warning("No results available yet. Please run the workflow first.")
        if st.button("← Back to Workflow", key="btn_back_to_workflow_results"):
            st.session_state.workflow_state['current_phase'] = 'workflow'
            st.rerun()
        return

    project_info = st.session_state.workflow_state.get('project_info', {})
    if project_info:
        with st.container():
            st.markdown("### Project Summary")
            st.write(f"**Name:** {project_info.get('name', '—')}")
            st.write(f"**Description:** {project_info.get('description', '—')}")
            st.write(f"**Objective:** {project_info.get('objective', '—')}")
        st.divider()


    # --- Final Report only ---
    if 'report' in phase_outputs:
        st.subheader("📄 Final Report")

        report_output = phase_outputs['report'].get('output', {})
        markdown_content = ""

        # Extract markdown from structure
        if isinstance(report_output, str):
            markdown_content = report_output
        elif isinstance(report_output, dict):
            markdown_content = report_output.get('output', str(report_output))
        else:
            markdown_content = str(report_output)

        # Render the content
        if markdown_content and markdown_content.strip():
            st.markdown(markdown_content, unsafe_allow_html=False)
        else:
            st.info("Report content is not available yet.")

        # Downloads
        st.markdown("### 📥 Download")
        col1, col2 = st.columns(2)

        with col1:
            try:
                from utils.pdf_generator import PDFGenerator
                pdf_generator = PDFGenerator()
                pdf_bytes = pdf_generator.generate_comprehensive_report_pdf(phase_outputs)
                filename_pdf = f"mimetica_final_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                st.download_button(
                    label="📄 Download PDF",
                    key="btn_download_pdf_results",
                    data=pdf_bytes,
                    file_name=filename_pdf,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            except Exception:
                st.error("PDF generation failed.")

        with col2:
            try:
                from utils.docx_generator import DocxGenerator
                docx_gen = DocxGenerator()
                docx_bytes = docx_gen.generate_comprehensive_report_docx(phase_outputs)
                filename_docx = f"mimetica_final_report_{datetime.now().strftime('%Y%m%d')}.docx"
                st.download_button(
                    label="📘 Download DOCX",
                    key="btn_download_docx_results",
                    data=docx_bytes,
                    file_name=filename_docx,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception:
                st.error("DOCX generation failed.")
    else:
        st.info("Final report not found yet.")

    st.divider()

    # --- Optional: Minimal Monte Carlo (one chart + 3 short lines) ---
    if 'simulation' in phase_outputs:
        st.subheader("📈 Simulation (Monte Carlo)")
        try:
            import numpy as np
            import plotly.graph_objects as go

            # Replace with your real data if available
            np.random.seed(42)
            optimistic = np.random.normal(120, 15, 1000)
            baseline = np.random.normal(100, 20, 1000)
            pessimistic = np.random.normal(80, 25, 1000)

            fig = go.Figure()
            fig.add_trace(go.Histogram(x=optimistic, name="Best", opacity=0.7, nbinsx=30))
            fig.add_trace(go.Histogram(x=baseline, name="Expected", opacity=0.7, nbinsx=30))
            fig.add_trace(go.Histogram(x=pessimistic, name="Worst", opacity=0.7, nbinsx=30))
            fig.update_layout(barmode='overlay', height=420)
            st.plotly_chart(fig, use_container_width=True)

            st.write("- **Best case**: higher outcomes appear more frequently.")
            st.write("- **Expected**: most results cluster around the middle.")
            st.write("- **Worst case**: outcomes shift lower but remain bounded.")
        except Exception:
            st.info("Simulation chart unavailable.")

def show_simulation_visualizations(simulation_output):
    """Display Monte Carlo simulation visualizations with layman explanations"""
    st.subheader("Monte Carlo Simulation Results")
    
    # Display layman explanations first
    try:
        # Check if explanations are available in session state
        explanations = st.session_state.workflow_state.get('simulation_explanations', {})
        
        if explanations:
            st.success("📊 **Simulation Complete!** Below are the results explained in simple terms:")
            
            # Create tabs for different audience explanations
            tab1, tab2, tab3 = st.tabs(["Executive Summary", "Management Details", "General Overview"])
            
            with tab1:
                st.markdown("### For Decision Makers")
                if 'executive' in explanations:
                    st.markdown(explanations['executive'])
                else:
                    st.warning("Executive explanation not available")
            
            with tab2:
                st.markdown("### For Project Managers") 
                if 'manager' in explanations:
                    st.markdown(explanations['manager'])
                else:
                    st.warning("Management explanation not available")
            
            with tab3:
                st.markdown("### For Everyone")
                if 'general' in explanations:
                    st.markdown(explanations['general'])
                else:
                    st.warning("General explanation not available")
            
            st.divider()
            
    except Exception as e:
        st.warning(f"Could not load simulation explanations: {str(e)}")
    
    # Create sample visualization data (replace with actual simulation data)
    try:
        import numpy as np
        
        # Generate sample data for demonstration
        np.random.seed(42)
        optimistic_data = np.random.normal(120, 15, 1000)
        baseline_data = np.random.normal(100, 20, 1000)
        pessimistic_data = np.random.normal(80, 25, 1000)
        
        st.subheader("📈 Detailed Charts and Statistics")
        
        # Scenario comparison chart
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(x=optimistic_data, name="Optimistic Scenario", 
                                  opacity=0.7, nbinsx=30, marker_color="#2E8B57"))
        fig.add_trace(go.Histogram(x=baseline_data, name="Most Likely Scenario", 
                                  opacity=0.7, nbinsx=30, marker_color="#4682B4"))
        fig.add_trace(go.Histogram(x=pessimistic_data, name="Conservative Scenario", 
                                  opacity=0.7, nbinsx=30, marker_color="#DC143C"))
        
        fig.update_layout(
            title="Monte Carlo Simulation Results - Scenario Comparison",
            xaxis_title="Outcome Value",
            yaxis_title="Frequency (How often this outcome occurred)",
            barmode='overlay',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation below the chart
        st.info("""
        **How to read this chart:** 
        - The X-axis shows possible outcome values
        - The Y-axis shows how frequently each outcome occurred in our 1,000 simulations
        - Taller bars mean more likely outcomes
        - The spread shows the range of possibilities for each scenario
        """)
        
        # Summary statistics with better explanations
        st.subheader("📊 Key Numbers Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🟢 Best Case Scenario (Optimistic)**")
            st.metric("90th Percentile", f"{np.percentile(optimistic_data, 90):.1f}", 
                     help="Only 10% of outcomes are better than this")
            st.metric("Average Outcome", f"{np.mean(optimistic_data):.1f}")
            st.metric("Variability", f"{np.std(optimistic_data):.1f}", 
                     help="Lower numbers mean more predictable results")
        
        with col2:
            st.markdown("**🟡 Most Likely Scenario (Baseline)**")
            st.metric("50th Percentile (Median)", f"{np.percentile(baseline_data, 50):.1f}",
                     help="Half of outcomes are above this, half below")
            st.metric("Average Outcome", f"{np.mean(baseline_data):.1f}")
            st.metric("Variability", f"{np.std(baseline_data):.1f}")
        
        with col3:
            st.markdown("**🔴 Worst Case Scenario (Pessimistic)**") 
            st.metric("10th Percentile", f"{np.percentile(pessimistic_data, 10):.1f}",
                     help="Only 10% of outcomes are worse than this")
            st.metric("Average Outcome", f"{np.mean(pessimistic_data):.1f}")
            st.metric("Variability", f"{np.std(pessimistic_data):.1f}")
        
        # Risk assessment summary
        st.subheader("🎯 Risk Assessment Summary")
        
        best_case = np.percentile(optimistic_data, 90)
        most_likely = np.percentile(baseline_data, 50)
        worst_case = np.percentile(pessimistic_data, 10)
        
        risk_col1, risk_col2 = st.columns(2)
        
        with risk_col1:
            upside_potential = ((best_case - most_likely) / most_likely * 100)
            st.metric("🚀 Upside Potential", f"+{upside_potential:.1f}%", 
                     help="How much better than expected you could do")
            
        with risk_col2:
            downside_risk = ((most_likely - worst_case) / most_likely * 100)
            st.metric("⚠️ Downside Risk", f"-{downside_risk:.1f}%",
                     help="How much worse than expected you could do")
        
        # Simple recommendation
        st.subheader("💡 Simple Recommendation")
        
        if downside_risk < 20:
            st.success(f"✅ **Low Risk Profile**: Even in worst case, you only risk {downside_risk:.1f}% downside. This looks like a solid opportunity.")
        elif downside_risk < 40:
            st.warning(f"⚠️ **Moderate Risk Profile**: You could face up to {downside_risk:.1f}% downside. Make sure you have contingency plans.")
        else:
            st.error(f"🚨 **High Risk Profile**: Potential {downside_risk:.1f}% downside requires careful consideration. Consider risk mitigation strategies.")
        
    except Exception as e:
        st.error(f"Failed to generate simulation visualizations: {str(e)}")

def download_deliverable(phase: str, output_info: Dict[str, Any]):
    """Download individual deliverable"""
    try:
        content = output_info.get('output', {})
        timestamp = output_info.get('timestamp', datetime.now().isoformat())
        
        # Create two columns for download options
        col1, col2 = st.columns(2)
        
        with col1:
            # TXT download
            if isinstance(content, dict):
                content_str = str(content)
            else:
                content_str = str(content)
            
            filename_txt = f"mimetica_{phase}_{timestamp[:10]}.txt"
            
            st.download_button(
                label=f"📝 Download TXT",
                data=content_str,
                file_name=filename_txt,
                mime="text/plain",
                key=f"txt_{phase}"
            )
        
        with col2:
            # PDF download
            try:
                pdf_generator = PDFGenerator()
                pdf_bytes = pdf_generator.generate_deliverable_pdf(phase, output_info)
                filename_pdf = f"mimetica_{phase}_{timestamp[:10]}.pdf"
                
                st.download_button(
                    label=f"📄 Download PDF",
                    data=pdf_bytes,
                    file_name=filename_pdf,
                    mime="application/pdf",
                    key=f"pdf_{phase}"
                )
            except Exception as e:
                st.error(f"PDF generation failed: {str(e)}")
        
    except Exception as e:
        st.error(f"Failed to prepare downloads: {str(e)}")

def download_final_report(format_type: str):
    """Download final comprehensive report - DEPRECATED: Use direct download buttons instead"""
    # This function is deprecated and no longer used
    # PDF and Markdown downloads are now handled directly in show_results_page()
    pass

def generate_comprehensive_report(phase_outputs: Dict[str, Any]) -> str:
    """Generate comprehensive text report"""
    report = f"""
# MIMÉTICA Strategic Decision Support System
## Comprehensive Analysis Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Workflow ID: {st.session_state.workflow_state.get('workflow_id', 'Unknown')}

## Executive Summary
This report presents the comprehensive analysis conducted using the MIMÉTICA 
decision support system following the DECIDE methodology.

"""
    
    # Add token processing summary
    total_tokens = sum(
        phase_data.get('batch_processing_stats', {}).get('total_tokens_processed', 0)
        for phase_data in phase_outputs.values()
    )
    total_batches = sum(
        phase_data.get('batch_processing_stats', {}).get('total_batches', 0)
        for phase_data in phase_outputs.values()
    )
    
    if total_tokens > 0:
        report += f"""
## Processing Statistics
- Total Tokens Processed: {total_tokens:,}
- Total Batches: {total_batches}
- Phases Completed: {len(phase_outputs)}

"""
    
    # Add each phase output
    for phase, output_info in phase_outputs.items():
        report += f"\n## {phase.replace('_', ' ').title()}\n"
        report += f"Generated: {output_info.get('timestamp', 'Unknown')}\n\n"
        
        # Add batch processing stats if available
        if 'batch_processing_stats' in output_info:
            stats = output_info['batch_processing_stats']
            report += f"**Processing Statistics:**\n"
            report += f"- Documents: {stats.get('total_documents', 0)}\n"
            report += f"- Chunks: {stats.get('total_chunks', 0)}\n"
            report += f"- Batches: {stats.get('total_batches', 0)}\n"
            report += f"- Tokens: {stats.get('total_tokens_processed', 0):,}\n"
            report += f"- Success Rate: {stats.get('success_rate', 0):.1f}%\n\n"
        
        content = output_info.get('output', {})
        if isinstance(content, dict):
            for key, value in content.items():
                report += f"**{key}:** {value}\n"
        else:
            report += str(content)
        
        report += "\n" + "="*50 + "\n"
    
    return report

def generate_markdown_report(phase_outputs: Dict[str, Any]) -> str:
    """Generate comprehensive markdown report"""
    report = f"""# MIMÉTICA Strategic Decision Support System
## Comprehensive Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Workflow ID:** {st.session_state.workflow_state.get('workflow_id', 'Unknown')}

## Executive Summary

This report presents the comprehensive analysis conducted using the MIMÉTICA decision support system following the DECIDE methodology (Define → Explore → Create → Implement → Decide/Simulate → Evaluate).

"""
    
    # Add token processing summary
    total_tokens = sum(
        phase_data.get('batch_processing_stats', {}).get('total_tokens_processed', 0)
        for phase_data in phase_outputs.values()
    )
    total_batches = sum(
        phase_data.get('batch_processing_stats', {}).get('total_batches', 0)
        for phase_data in phase_outputs.values()
    )
    
    if total_tokens > 0:
        report += f"""## Processing Statistics

- **Total Tokens Processed:** {total_tokens:,}
- **Total Batches:** {total_batches}
- **Phases Completed:** {len(phase_outputs)}

---

"""
    
    # Add each phase output
    for phase, output_info in phase_outputs.items():
        report += f"## {phase.replace('_', ' ').title()}\n\n"
        report += f"**Generated:** {output_info.get('timestamp', 'Unknown')}\n\n"
        
        # Add batch processing stats if available
        if 'batch_processing_stats' in output_info:
            stats = output_info['batch_processing_stats']
            report += f"### Processing Statistics\n\n"
            report += f"| Metric | Value |\n"
            report += f"|--------|-------|\n"
            report += f"| Documents | {stats.get('total_documents', 0)} |\n"
            report += f"| Chunks | {stats.get('total_chunks', 0)} |\n"
            report += f"| Batches | {stats.get('total_batches', 0)} |\n"
            report += f"| Tokens | {stats.get('total_tokens_processed', 0):,} |\n"
            report += f"| Success Rate | {stats.get('success_rate', 0):.1f}% |\n\n"
        
        content = output_info.get('output', {})
        if isinstance(content, dict):
            for key, value in content.items():
                report += f"### {key}\n{value}\n\n"
        else:
            report += f"{content}\n\n"
        
        report += "---\n\n"
    
    report += f"""
## Report Footer

*This report was generated by MIMÉTICA MVP 1.0 - Strategic Decision Support System*  
*Powered by CrewAI Multi-Agent Orchestration with Intelligent Token Batch Management*  
*© {datetime.now().year} Tuinkel*
"""
    
    return report

def show_dashboard_page():
    """Display a minimal dashboard"""
    st.header("MIMÉTICA Dashboard")

    summary = SessionManager.get_workflow_summary()

    documents = summary.get('total_documents', 0)
    completed = len(summary.get('completed_phases', []))
    total = 10
    status = "Complete ✅" if summary.get('workflow_completed') else "In progress"

    # Simple cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Documents", documents)
    with col2:
        st.metric("Progress", f"{completed}/{total}")
    with col3:
        st.metric("Status", status)

    st.subheader("Quick Actions")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("New Project", key="btn_new_project_dashboard", use_container_width=True):
            SessionManager.reset_workflow()
            st.rerun()
    with c2:
        if st.button("Continue", key="btn_continue_dashboard", use_container_width=True):
            st.session_state.workflow_state['current_phase'] = 'workflow'
            st.rerun()
    with c3:
        if st.button("View Results", key="btn_view_results_dashboard", use_container_width=True, type="primary"):
            st.session_state.workflow_state['current_phase'] = 'results'
            st.rerun()


if __name__ == "__main__":
    main()