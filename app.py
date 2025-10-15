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
        # Add icon and logo images at the top
        try:
            # Add icon.png
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
            
            # Add logo_red.png
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
            
        except FileNotFoundError as e:
            # Fallback if images are not found
            st.info("Images not found in assets folder")
        
        # Model Selection Section
        st.subheader("Select the model")
        
        # Initialize selected model in session state if not exists
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = config.DEFAULT_MODEL
        
        # Create model options for dropdown
        model_options = {}
        for model_key, model_config in config.AVAILABLE_MODELS.items():
            provider = model_config['provider'].upper()
            name = model_config['name']
            description = model_config['description']
            model_options[model_key] = f"{provider}: {name}"
        
        # Model selection dropdown
        selected_model_key = st.selectbox(
            "Choose model:",
            options=list(model_options.keys()),
            index=list(model_options.keys()).index(st.session_state.selected_model),
            format_func=lambda x: model_options[x],
            help="Select the AI model for workflow processing"
        )
        
        # Show model description
        selected_model_config = config.AVAILABLE_MODELS[selected_model_key]
        st.caption(f"💡 {selected_model_config['description']}")
        st.caption(f"🎯 Good for: {selected_model_config['good_for']}")
        
        # Update button (appears when model is changed from current selection)
        if selected_model_key != st.session_state.selected_model:
            if st.button("🔄 Update Model", type="primary", use_container_width=True):
                st.session_state.selected_model = selected_model_key
                st.success(f"✅ Model updated to {model_options[selected_model_key]}")
                st.rerun()
        
        st.divider()
        
        st.title("Navigation")
        
        # Workflow progress
        st.subheader("Workflow Progress")
        
        phases = [
            ("Setup", "setup"),
            ("Document Collection", "collection"),
            ("Multidisciplinary Analysis", "analysis"),
            ("Problem Definition", "definition"),
            ("Context Exploration", "exploration"),
            ("Option Creation", "creation"),
            ("Implementation Planning", "implementation"),
            ("Simulation Analysis", "simulation"),
            ("Evaluation Framework", "evaluation"),
            ("Final Report", "report")
        ]
        
        completed_phases = st.session_state.workflow_state.get('completed_phases', [])
        current_phase = st.session_state.workflow_state.get('current_phase', 'setup')
        workflow_completed = st.session_state.workflow_state.get('workflow_completed', False)
        
        for phase_name, phase_key in phases:
            if phase_key in completed_phases:
                st.success(f"✅ {phase_name}")
            elif phase_key == current_phase and not workflow_completed:
                st.warning(f"🔄 {phase_name}")
            else:
                st.info(f"⏳ {phase_name}")
        
        # Show overall completion status
        if workflow_completed:
            st.success("🎉 **All Phases Complete!**")
        elif len(completed_phases) > 0:
            completion_percent = len(completed_phases) / len(phases) * 100
            st.info(f"📊 Overall Progress: {completion_percent:.0f}%")
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("Dashboard", use_container_width=True):
            st.session_state.workflow_state['current_phase'] = 'dashboard'
            st.rerun()
        
        # Make View Results button more prominent when workflow is completed
        workflow_completed = st.session_state.workflow_state.get('workflow_completed', False)
        if workflow_completed:
            if st.button("🎯 **VIEW RESULTS**", use_container_width=True, type="primary"):
                st.session_state.workflow_state['current_phase'] = 'results'
                st.rerun()
        else:
            if st.button("View Results", use_container_width=True):
                st.session_state.workflow_state['current_phase'] = 'results'
                st.rerun()
        
        if st.button("New Workflow", use_container_width=True):
            SessionManager.reset_workflow()
            st.rerun()
        
        st.divider()
        
        # System info
        st.subheader("ℹ️ System Info")
        workflow_summary = SessionManager.get_workflow_summary()
        st.write(f"**Workflow ID:** {workflow_summary.get('workflow_id', 'N/A')}")
        st.write(f"**Documents:** {workflow_summary.get('total_documents', 0)}")
        st.write(f"**Current Phase:** {workflow_summary.get('current_phase', 'setup')}")
        
        # Show completion status
        if workflow_summary.get('workflow_completed', False):
            completion_time = workflow_summary.get('workflow_completion_time')
            if completion_time:
                try:
                    completion_dt = datetime.fromisoformat(completion_time)
                    st.write(f"**Status:** ✅ Complete")
                    st.write(f"**Completed:** {completion_dt.strftime('%m/%d %H:%M')}")
                except:
                    st.write(f"**Status:** ✅ Complete")
            else:
                st.write(f"**Status:** ✅ Complete")
        else:
            completed_count = len(workflow_summary.get('completed_phases', []))
            st.write(f"**Status:** 🔄 In Progress ({completed_count}/9)")
        
        # Logout
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            # Clear all data in 'mimetica' collection
            try:
                vector_store = VectorStore()
                # Use clear instead of delete to preserve collection structure
                vector_store.clear_collection()
                st.info("Vector store cleared successfully")
            except Exception as e:
                st.warning(f"Could not clear vector store: {e}")
            # Clear session and logout, then force rerun for a fresh app
            AuthManager.logout()
            st.session_state['workflow_state'] = {'current_phase': 'setup'}
            st.rerun()

def show_setup_page():
    """Display setup and document upload page"""
    st.header("📋 Project Setup & Document Upload")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Project information
        st.subheader("Project Information")
        
        project_name = st.text_input("Project Name", value="Strategic Initiative Analysis")
        project_description = st.text_area("Project Description", 
                                         value="Comprehensive analysis of strategic initiative using MIMÉTICA methodology")
        analysis_focus = st.selectbox("Analysis Focus", 
                                    ["Campaign ROI Optimization", "Digital Transformation", 
                                     "Customer Experience Improvement", "New Service Design", "Other"])
        
        # Show custom focus input immediately when "Other" is selected
        custom_focus = None
        if analysis_focus == "Other":
            custom_focus = st.text_input("Specify Custom Focus")
        
        if st.button("💾 Save Project Info", type="primary", use_container_width=True):
            # Save project info to session
            st.session_state.workflow_state['project_info'] = {
                'name': project_name,
                'description': project_description,
                'focus': analysis_focus if analysis_focus != "Other" else custom_focus,
                'created_at': datetime.now().isoformat()
            }
            st.success("✅ Project information saved!")


        st.subheader("Document Upload")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload your documents (PDF, Word, CSV, Excel)",
            type=['pdf', 'docx', 'doc', 'csv', 'xlsx', 'xls'],
            accept_multiple_files=True,
            help="Upload documents that will be analyzed by the MIMÉTICA system"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) selected")
            
            # Process documents button
            if st.button("🔄 Process Documents", type="primary", use_container_width=True):
                process_documents(uploaded_files)
        
        
    
    with col2:
        st.subheader("Current Status")
        
        # Display uploaded documents
        documents = st.session_state.workflow_state.get('documents', [])
        if documents:
            st.write(f"**Documents Processed:** {len(documents)}")
            
            # Document processor for stats
            doc_processor = DocumentProcessor()
            stats = doc_processor.get_document_stats(documents)
            
            if stats:
                st.metric("Total Files", stats.get('total_files', 0))
                st.metric("Total Size", f"{stats.get('total_size_mb', 0)} MB")
                st.metric("Total Words", f"{stats.get('total_words', 0):,}")
                
                # File types breakdown
                file_types = stats.get('file_types', {})
                if file_types:
                    st.write("**File Types:**")
                    for file_type, count in file_types.items():
                        st.write(f"- {file_type}: {count} files")
        else:
            st.info("No documents uploaded yet")
        
        # Vector store status
        st.subheader("🔍 Vector Database")
        try:
            vector_store = VectorStore(collection_name="mimetica") if 'collection_name' in VectorStore.__init__.__code__.co_varnames else VectorStore()
            collection_info = vector_store.get_collection_info() if hasattr(vector_store, 'get_collection_info') else None
            if collection_info:
                st.metric("Vectors Stored", collection_info.get('vector_count', 0))
                st.write(f"**Collection:** {collection_info.get('name', 'mimetica')}")
            else:
                st.info("Vector database not initialized")
        except Exception as e:
            st.error(f"Vector database error: {str(e)}")
        
        # Start workflow button
        if documents and st.button("🚀 Start DECIDE Workflow", type="primary", use_container_width=True):
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
    """Display workflow execution page"""
    st.header("🔄 DECIDE Workflow Execution")
    
    if 'workflow_instance' not in st.session_state:
        st.error("Workflow not initialized. Please return to setup.")
        if st.button("← Back to Setup"):
            st.session_state.workflow_state['current_phase'] = 'setup'
            st.rerun()
        return
    
    workflow = st.session_state.workflow_instance
    
    # Check if workflow is completed
    workflow_completed = st.session_state.workflow_state.get('workflow_completed', False)
    
    if workflow_completed:
        # Show workflow completion status with enhanced styling
        st.markdown("""
        <div class="workflow-completed">
            <h2>🎉 Workflow Completed Successfully!</h2>
            <p>All phases of the DECIDE methodology have been executed successfully.</p>
        </div>
        """, unsafe_allow_html=True)
        
        completion_time = st.session_state.workflow_state.get('workflow_completion_time', 'Unknown')
        if completion_time != 'Unknown':
            try:
                completion_dt = datetime.fromisoformat(completion_time)
                st.info(f"✅ **Completed on:** {completion_dt.strftime('%Y-%m-%d at %H:%M:%S')}")
            except:
                st.info(f"✅ **Completed at:** {completion_time}")
        
        # Show summary of completed phases
        completed_phases = st.session_state.workflow_state.get('completed_phases', [])
        if completed_phases:
            st.success(f"**📋 Phases Completed:** {len(completed_phases)}/9")
            phase_names = [phase.replace('_', ' ').title() for phase in completed_phases]
            st.write("**✅ Workflow Path:** " + " → ".join(phase_names))
        
        # Large, prominent "View Results" button with enhanced styling
        st.markdown("---")
        st.markdown("### 🎯 Your Comprehensive Analysis is Ready!")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 **VIEW COMPREHENSIVE RESULTS**", 
                        type="primary", 
                        use_container_width=True,
                        help="Access your complete analysis, reports, and downloadable deliverables"):
                st.session_state.workflow_state['current_phase'] = 'results'
                st.rerun()
        
        # Add call-to-action text
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; margin: 1rem 0;">
            <p style="margin: 0; color: #666;">
                📊 View detailed analysis results<br/>
                📄 Download comprehensive reports<br/>
                📈 Access simulation visualizations
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Show completion summary
        st.subheader("📊 Workflow Summary")
        
        phase_outputs = st.session_state.workflow_state.get('phase_outputs', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Deliverables", len(phase_outputs))
        with col2:
            total_tokens = sum(
                phase_data.get('batch_processing_stats', {}).get('total_tokens_processed', 0)
                for phase_data in phase_outputs.values()
            )
            st.metric("Tokens Processed", f"{total_tokens:,}")
        with col3:
            documents = st.session_state.workflow_state.get('documents', [])
            st.metric("Documents Analyzed", len(documents))
        with col4:
            st.metric("Status", "Complete ✅")
        
        # Additional options
        st.subheader("⚡ Additional Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state.workflow_state['current_phase'] = 'dashboard'
                st.rerun()
        
        with col2:
            if st.button("🔄 New Workflow", use_container_width=True):
                SessionManager.reset_workflow()
                st.rerun()
        
        with col3:
            if st.button("📝 View Logs", use_container_width=True):
                with st.expander("📋 Execution Logs", expanded=True):
                    display_workflow_logs()
    
    else:
        # Show workflow control panel (existing functionality)
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("▶️ Run Complete Workflow", type="primary", use_container_width=True):
                run_complete_workflow(workflow)
        
        with col2:
            if st.button("View Progress", use_container_width=True):
                show_workflow_progress()
    
        # Agent progress display
        st.subheader("🤖 Agent Progress")
        
        agent_progress = st.session_state.get('agent_progress', {})
        
        if agent_progress:
            for agent_name, progress_info in agent_progress.items():
                with st.expander(f"🤖 {agent_name.replace('_', ' ').title()}", expanded=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        progress_value = progress_info.get('progress', 0)
                        st.progress(progress_value)
                        st.write(f"**Status:** {progress_info.get('status', 'Unknown')}")
                        st.write(f"**Message:** {progress_info.get('message', 'No message')}")
                    
                    with col2:
                        timestamp = progress_info.get('timestamp', '')
                        if timestamp:
                            st.write(f"**Updated:** {timestamp[:19]}")
        else:
            st.info("No agent progress data available")
        
        # Live logs
        st.subheader("📝 Live Logs")
        
        logs = st.session_state.get('logs', [])
        if logs:
            # Display last 10 logs
            recent_logs = logs[-10:]
            for log in reversed(recent_logs):
                level = log.get('level', 'INFO')
                message = log.get('message', '')
                timestamp = log.get('timestamp', '')
                agent = log.get('agent', '')
                
                if level == 'ERROR':
                    st.error(f"[{timestamp[:19]}] {agent}: {message}")
                elif level == 'WARNING':
                    st.warning(f"[{timestamp[:19]}] {agent}: {message}")
                else:
                    st.info(f"[{timestamp[:19]}] {agent}: {message}")
        else:
            st.info("No logs available")

def run_complete_workflow(workflow):
    """Run the complete DECIDE workflow with enhanced rate limiting"""
    try:
        documents = st.session_state.workflow_state.get('documents', [])
        if not documents:
            st.error("No documents found. Please upload documents first.")
            return

        with st.spinner("🔄 Running enhanced workflow with provider-aware rate limiting..."):
            # Get current model and provider info
            current_model = config.validate_and_fix_selected_model()
            model_config = config.get_current_model_config()
            provider = model_config['provider']
            rate_limits = config.get_rate_limit_settings(current_model)
            
            # Display workflow information
            st.info(f"🎯 Using {provider} provider ({current_model})")
            st.info(f"📊 Rate limits: {rate_limits['tokens_per_minute']:,} TPM, {rate_limits['inter_phase_delay']}s between phases")
            
            # Execute enhanced workflow
            result = workflow.run_complete_workflow()
            
            if result.get('success'):
                st.success("🎉 Workflow completed successfully!")
                
                # Display execution statistics if available
                if 'execution_stats' in result:
                    stats = result['execution_stats']
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Phases Completed", len(stats.get('phases_completed', [])))
                    with col2:
                        duration = stats.get('total_duration_minutes', 0)
                        st.metric("Duration", f"{duration:.1f}m")
                    with col3:
                        st.metric("Rate Limit Hits", stats.get('rate_limit_hits', 0))
                    with col4:
                        wait_time = stats.get('total_wait_time', 0)
                        st.metric("Wait Time", f"{wait_time:.0f}s")
                
                # Update session state with results
                if 'phase_results' in result:
                    st.session_state.workflow_state['last_workflow_result'] = result
                    
                    # Save individual phase outputs
                    for phase_name, phase_result in result['phase_results'].items():
                        SessionManager.save_phase_output(phase_name, phase_result)
                
                # Display completion message
                completed_phases = result.get('completed_phases', [])
                st.success(f"✅ Successfully completed {len(completed_phases)} phases: {', '.join(completed_phases)}")
                
                # Mark workflow as completed in session state
                st.session_state.workflow_state['workflow_completed'] = True
                st.session_state.workflow_state['workflow_completion_time'] = datetime.now().isoformat()
                
                # Show provider-specific statistics
                if 'execution_stats' in result and 'provider_stats' in result['execution_stats']:
                    provider_stats = result['execution_stats']['provider_stats']
                    
                    with st.expander("📈 Provider Performance Stats", expanded=False):
                        if provider == 'anthropic':
                            st.write("**Anthropic Rate Limiting Stats:**")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Requests", provider_stats.get('total_requests', 0))
                                st.metric("Success Rate", f"{provider_stats.get('success_rate', 100):.1f}%")
                            with col2:
                                st.metric("Throttled Requests", provider_stats.get('throttled_requests', 0))
                                st.metric("Avg Wait Time", f"{provider_stats.get('average_wait_time', 0):.1f}s")
                        else:
                            st.write("**OpenAI Token Management Stats:**")
                            st.json(provider_stats)
                
                return result
            else:
                error_msg = result.get('error', 'Unknown error')
                failed_phase = result.get('failed_phase', 'Unknown')
                completed_phases = result.get('completed_phases', [])
                
                st.error(f"❌ Workflow failed at {failed_phase} phase: {error_msg}")
                
                if completed_phases:
                    st.info(f"✅ Completed phases before failure: {', '.join(completed_phases)}")
                
                # Show execution stats even for failed workflows
                if 'execution_stats' in result:
                    stats = result['execution_stats']
                    st.warning(f"⏱️ Execution time before failure: {stats.get('total_duration_minutes', 0):.1f} minutes")
                    
                    if stats.get('rate_limit_hits', 0) > 0:
                        st.warning(f"🚫 Rate limit hits encountered: {stats['rate_limit_hits']}")
                
                return result

    except Exception as e:
        st.error(f"❌ Workflow execution failed: {str(e)}")
        SessionManager.add_log("ERROR", f"Workflow execution failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


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
    """Display workflow results and deliverables"""
    st.header("📊 Workflow Results & Deliverables")
    
    phase_outputs = st.session_state.workflow_state.get('phase_outputs', {})
    
    if not phase_outputs:
        st.warning("No results available. Please run the workflow first.")
        if st.button("← Back to Workflow"):
            st.session_state.workflow_state['current_phase'] = 'workflow'
            st.rerun()
        return
    
    # 1. FINAL REPORT SECTION - PDF PREVIEW WITH DOWNLOAD BUTTONS
    if 'report' in phase_outputs:
        st.subheader("📄 Final Comprehensive Report")
        
        report_output = phase_outputs['report'].get('output', {})
        
        # Extract the actual markdown content from the nested structure
        markdown_content = ""
        if isinstance(report_output, str):
            markdown_content = report_output
        elif isinstance(report_output, dict):
            if 'output' in report_output:
                markdown_content = report_output['output']
            else:
                # Convert the entire dict to string and extract markdown
                report_str = str(report_output)
                start_marker = "# MIMÉTICA Strategic Decision Support System"
                if start_marker in report_str:
                    start_idx = report_str.find(start_marker)
                    end_markers = ["', 'includes_phases'", "\"', 'includes_phases'", "\\n---\\n\\nThis report contains"]
                    end_idx = len(report_str)
                    for marker in end_markers:
                        marker_idx = report_str.find(marker, start_idx)
                        if marker_idx != -1:
                            end_idx = min(end_idx, marker_idx)
                    
                    markdown_content = report_str[start_idx:end_idx]
                    # Clean up any escaped characters
                    markdown_content = markdown_content.replace('\\n', '\n')
                    markdown_content = markdown_content.replace('\\t', '\t')
                    markdown_content = markdown_content.replace('\\"', '"')
                    markdown_content = markdown_content.replace("\\'", "'")
        
        # Display the report content as PDF preview
        with st.container():
            # Check for visualizations and display accordingly
            has_visualizations = "data:image/png;base64," in str(markdown_content)
            
            if has_visualizations:
                # Display content with embedded visualizations
                import re
                import base64
                from PIL import Image
                import io
                
                # Check if content contains image placeholders
                placeholder_pattern = r'\[IMAGE_PLACEHOLDER: ([a-f0-9-]+)\].*?\[/IMAGE_PLACEHOLDER\]'
                if re.search(placeholder_pattern, markdown_content, re.DOTALL):
                    # Content has image placeholders - process them
                    from utils.image_manager import image_manager
                    
                    # Split content around image placeholders
                    parts = re.split(placeholder_pattern, markdown_content, flags=re.DOTALL)
                    
                    for i, part in enumerate(parts):
                        if i % 2 == 0:
                            # Text content - render as markdown
                            if part.strip():
                                # Clean the content from any tool artifacts
                                clean_text = re.sub(r'.*successfully.*\n', '', part)
                                clean_text = re.sub(r'.*generated successfully.*\n', '', clean_text)
                                clean_text = re.sub(r'🎨 VISUALIZATION TOOL CALLED:.*\n', '', clean_text)
                                if clean_text.strip():
                                    st.markdown(clean_text.strip())
                        else:
                            # This is an image ID - load and display the image
                            image_id = part
                            try:
                                image_bytes = image_manager.load_image_for_pdf(image_id)
                                if image_bytes:
                                    image = Image.open(io.BytesIO(image_bytes))
                                    
                                    # Get image metadata for caption
                                    metadata = image_manager.get_image_by_id(image_id)
                                    if metadata and 'title' in metadata:
                                        st.image(image, caption=metadata['title'], use_column_width=True)
                                    else:
                                        st.image(image, use_column_width=True)
                            except Exception as e:
                                st.error(f"Failed to load image {image_id}: {str(e)}")
                else:
                    # Legacy: Check for base64 images (for backwards compatibility)
                    base64_pattern = r'Base64 Image Data: data:image/png;base64,([A-Za-z0-9+/=]+)'
                    if re.search(base64_pattern, markdown_content):
                        # Split content around base64 images
                        parts = re.split(base64_pattern, markdown_content)
                        
                        for i, part in enumerate(parts):
                            if i % 2 == 0:
                                # Text content - render as markdown
                                if part.strip():
                                    # Clean the content from any tool artifacts
                                    clean_text = re.sub(r'.*successfully.*\n', '', part)
                                    clean_text = re.sub(r'.*generated successfully.*\n', '', clean_text)
                                    clean_text = re.sub(r'Base64 Image Data:.*\n', '', clean_text)
                                    clean_text = re.sub(r'🎨 VISUALIZATION TOOL CALLED:.*\n', '', clean_text)
                                    if clean_text.strip():
                                        st.markdown(clean_text.strip())
                            else:
                                # Base64 image data - display as image
                                try:
                                    image_data = base64.b64decode(part)
                                    image = Image.open(io.BytesIO(image_data))
                                    st.image(image, use_column_width=True)
                                except Exception:
                                    pass  # Skip invalid image data
                    else:
                        # No images, just display text
                        if markdown_content:
                            # Clean the content from any tool artifacts and formatting issues
                            clean_content = markdown_content
                            
                            # Remove tool output messages
                            clean_content = re.sub(r'.*successfully.*\n', '', clean_content)
                            clean_content = re.sub(r'.*generated successfully.*\n', '', clean_content) 
                            clean_content = re.sub(r'🎨 VISUALIZATION TOOL CALLED:.*\n', '', clean_content)
                            clean_content = re.sub(r'\*\*GENERATE.*?\*\*:', '', clean_content, flags=re.DOTALL)
                            clean_content = re.sub(r'Use the strategic_visualization_generator tool.*?\n', '', clean_content)
                            
                            if clean_content.strip():
                                st.markdown(clean_content.strip())
            else:
                # No image placeholders found, display as properly rendered markdown text
                if markdown_content:
                    # Clean the content from any tool artifacts and formatting issues
                    import re
                    clean_content = markdown_content
                    
                    # Remove tool output messages
                    clean_content = re.sub(r'.*successfully.*\n', '', clean_content)
                    clean_content = re.sub(r'.*generated successfully.*\n', '', clean_content) 
                    clean_content = re.sub(r'Base64 Image Data:.*\n', '', clean_content)
                    clean_content = re.sub(r'🎨 VISUALIZATION TOOL CALLED:.*\n', '', clean_content)
                    clean_content = re.sub(r'\*\*GENERATE.*?\*\*:', '', clean_content, flags=re.DOTALL)
                    clean_content = re.sub(r'Use the strategic_visualization_generator tool.*?\n', '', clean_content)
                    
                    # Clean up any remaining formatting artifacts
                    clean_content = clean_content.replace('\\n', '\n')
                    clean_content = clean_content.replace('\\t', '\t')
                    clean_content = clean_content.replace('\\"', '"')
                    clean_content = clean_content.replace("\\'", "'")
                    clean_content = clean_content.replace('\\\\', '\\')
                    
                    # Remove any CrewAI output wrappers
                    clean_content = re.sub(r'^.*?\n# MIMÉTICA', '# MIMÉTICA', clean_content, flags=re.DOTALL)
                    clean_content = re.sub(r"', 'includes_phases.*$", '', clean_content, flags=re.DOTALL)
                    clean_content = re.sub(r'", "includes_phases.*$', '', clean_content, flags=re.DOTALL)
                    
                    # Final cleanup - remove empty lines and ensure proper spacing
                    lines = clean_content.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('```') and 'strategic_visualization_generator' not in line:
                            cleaned_lines.append(line)
                    
                    final_content = '\n\n'.join(cleaned_lines)
                    
                    # Render the cleaned markdown content
                    if final_content.strip():
                        st.markdown(final_content)
                    else:
                        st.write("Report content is being processed...")
                        # Show debug info to help troubleshoot
                        with st.expander("🔍 Debug: Raw Content Preview", expanded=False):
                            st.text(f"Original content length: {len(markdown_content)}")
                            st.text("First 500 characters:")
                            st.code(markdown_content[:500])
                        
                        # Fallback: show a cleaned version without special formatting
                        fallback_content = re.sub(r'[#*`]', '', markdown_content[:2000])
                        if fallback_content.strip():
                            st.text(fallback_content)
                        else:
                            st.error("Unable to extract readable content from report")
                else:
                    st.error("No report content available")
        
        # 2. DOWNLOAD BUTTONS FOR PDF AND DOCX (as requested)
        st.markdown("### 📥 Download Final Report")
        col1, col2 = st.columns([1, 1])

        with col1:
            try:
                from utils.pdf_generator import PDFGenerator
                pdf_generator = PDFGenerator()
                pdf_bytes = pdf_generator.generate_comprehensive_report_pdf(phase_outputs)
                filename = f"mimetica_final_report_{datetime.now().strftime('%Y%m%d')}.pdf"
                
                if pdf_bytes and len(pdf_bytes) > 0:
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True
                    )
            except Exception as e:
                st.download_button(
                    label="📄 PDF Generation Failed",
                    data="",
                    file_name="error.txt",
                    disabled=True,
                    use_container_width=True
                )
        
        with col2:
            try:
                docx_gen = DocxGenerator()
                docx_bytes = docx_gen.generate_comprehensive_report_docx(phase_outputs)
                filename = f"mimetica_final_report_{datetime.now().strftime('%Y%m%d')}.docx"
                st.download_button(
                    label="📘 Download DOCX Report",
                    data=docx_bytes,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Failed to generate DOCX: {str(e)}")
        
        st.divider()
    
    # 3. OTHER OUTPUT FILES DROPDOWN (as requested)
    st.subheader("📋 Other Output Files")
    try:
        project_root = Path(__file__).resolve().parent
        md_files = sorted([
            p for p in project_root.glob("*.md")
            if p.name.lower().endswith('.md') and p.name not in {
                'comprehensive_strategic_analysis_report.md', 'README.md'
            }
        ], key=lambda x: x.name.lower())

        if md_files:
            file_map = {p.name: p for p in md_files}
            selected_name = st.selectbox("Select an output file to view", options=list(file_map.keys()))
            if selected_name:
                p = file_map[selected_name]
                try:
                    md_content = p.read_text(encoding='utf-8', errors='ignore')
                except Exception:
                    md_content = p.read_text(errors='ignore')

                # Display the selected file content
                with st.container():
                    st.markdown(f"**Viewing:** {selected_name}")
                    
                    tabs = st.tabs(["📖 Rendered View", "📝 Raw Text"])
                    with tabs[0]:
                        st.markdown(md_content, unsafe_allow_html=False)
                    with tabs[1]:
                        st.text_area("Raw Content", md_content, height=300)

                # Download selected markdown as PDF
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    try:
                        pdf_gen = PDFGenerator()
                        title = selected_name.replace('_', ' ').replace('.md', '').title()
                        pdf_bytes = pdf_gen.markdown_to_pdf(md_content, title=title)
                        st.download_button(
                            label="📄 Download as PDF",
                            data=pdf_bytes,
                            file_name=f"{p.stem}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"PDF export failed: {str(e)}")
                
                with col2:
                    st.download_button(
                        label="📝 Download as Text",
                        data=md_content,
                        file_name=selected_name,
                        mime="text/markdown",
                        use_container_width=True
                    )
        else:
            st.info("No other output files found in the workspace.")
    except Exception as e:
        st.error(f"Failed to load output files: {str(e)}")
    
    st.divider()
    
    # 4. MONTE CARLO SIMULATION SECTION (as requested)
    if 'simulation' in phase_outputs:
        show_simulation_visualizations(phase_outputs['simulation'])
        st.divider()
    
    # 5. AGENT COMMUNICATION DROPDOWN (as requested)
    st.subheader("🤖 Agent Communications & Execution Details")
    
    agent_comms = SessionManager.get_formatted_agent_communications()
    
    if agent_comms and agent_comms != "No agent communications recorded.":
        with st.expander("📋 View Complete Agent Communication Log", expanded=False):
            st.markdown("### Agent Interactions During Workflow Execution")
            st.info("This section contains all the detailed communications, reasoning, and interactions between AI agents during the workflow execution. You can see exactly how each agent processed your documents and made decisions.")
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["📝 Formatted View", "🔍 Raw Communications", "📊 Summary"])
            
            with tab1:
                st.markdown(agent_comms)
            
            with tab2:
                # Show raw communication data
                raw_comms = SessionManager.get_agent_communications()
                if raw_comms:
                    st.json(raw_comms[-10:])  # Show last 10 communications as JSON
                    st.caption(f"Showing last 10 of {len(raw_comms)} total communications")
                else:
                    st.info("No raw communications available")
            
            with tab3:
                # Show communication summary
                comm_logger = SessionManager.get_agent_comm_logger()
                if comm_logger:
                    summary = comm_logger.get_communications_summary()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Communications", summary['total_communications'])
                    with col2:
                        st.metric("Phases Covered", len(summary['phases_covered']))
                    with col3:
                        st.metric("Duration", summary['duration_covered'])
                    
                    st.write("**Communication Types:**")
                    for comm_type, count in summary['communication_types'].items():
                        st.write(f"- {comm_type.replace('_', ' ').title()}: {count}")
                    
                    st.write("**Phases Covered:**")
                    st.write(", ".join(summary['phases_covered']))
                    
                    st.write("**Active Sources:**")
                    st.write(", ".join(summary['sources']))
                else:
                    st.info("Communication summary not available")
            
            # Download option for communications
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📄 Download Communications as Text",
                    data=agent_comms,
                    file_name=f"agent_communications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                # Export as JSON
                raw_comms = SessionManager.get_agent_communications()
                if raw_comms:
                    import json
                    comms_json = json.dumps(raw_comms, indent=2)
                    st.download_button(
                        label="📊 Download Communications as JSON",
                        data=comms_json,
                        file_name=f"agent_communications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
    else:
        st.info("No agent communications were recorded during this session. Communications are captured when the workflow is executed.")
    
    # ADDITIONAL FEATURES - Results summary with batch processing stats
    with st.expander("📊 Workflow Statistics & Processing Details", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Deliverables", len(phase_outputs))
        
        with col2:
            # Calculate total tokens processed across all phases
            total_tokens = sum(
                phase_data.get('batch_processing_stats', {}).get('total_tokens_processed', 0)
                for phase_data in phase_outputs.values()
            )
            st.metric("Tokens Processed", f"{total_tokens:,}")
        
        with col3:
            # Calculate total batches processed
            total_batches = sum(
                phase_data.get('batch_processing_stats', {}).get('total_batches', 0)
                for phase_data in phase_outputs.values()
            )
            st.metric("Total Batches", total_batches)
        
        with col4:
            completion_status = "Complete" if len(phase_outputs) >= 8 else "In Progress"
            st.metric("Status", completion_status)
        
        # Token usage visualization
        if total_tokens > 0:
            st.subheader("Token Usage by Phase")
            
            # Create token usage chart
            token_data = []
            for phase, phase_data in phase_outputs.items():
                stats = phase_data.get('batch_processing_stats', {})
                if stats.get('total_tokens_processed', 0) > 0:
                    token_data.append({
                        'Phase': phase.replace('_', ' ').title(),
                        'Tokens': stats['total_tokens_processed'],
                        'Batches': stats.get('total_batches', 0),
                        'Success Rate': stats.get('success_rate', 0)
                    })
            
            if token_data:
                df_tokens = pd.DataFrame(token_data)
                fig = px.bar(df_tokens, x='Phase', y='Tokens', 
                            title='Token Usage by Phase',
                            hover_data=['Batches', 'Success Rate'])
                st.plotly_chart(fig, use_container_width=True)
        
        # Individual phase deliverables in expander
        st.subheader("Individual Phase Deliverables")
        
        # Show each phase output in tabs
        if phase_outputs:
            phase_names = list(phase_outputs.keys())
            tabs = st.tabs([phase.replace('_', ' ').title() for phase in phase_names])
            
            for tab, phase in zip(tabs, phase_names):
                with tab:
                    output_info = phase_outputs[phase]
                    
                    st.write(f"**Generated:** {output_info.get('timestamp', 'Unknown')}")
                    
                    # Show batch processing stats if available
                    if 'batch_processing_stats' in output_info:
                        with st.expander("📊 Processing Statistics"):
                            stats = output_info['batch_processing_stats']
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Documents", stats.get('total_documents', 0))
                            with col2:
                                st.metric("Chunks", stats.get('total_chunks', 0))
                            with col3:
                                st.metric("Batches", stats.get('total_batches', 0))
                            with col4:
                                st.metric("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
                    
                    # Display content
                    content = output_info.get('output', {})
                    if isinstance(content, dict):
                        for key, value in content.items():
                            st.write(f"**{key}:**")
                            st.write(str(value))
                            st.write("")
                    else:
                        st.write(str(content))
                    
                    # Download options for individual deliverable
                    st.write("**Download Options:**")
                    download_deliverable(phase, output_info)

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
    """Display main dashboard"""
    st.header("MIMÉTICA Dashboard")
    
    # Key metrics
    st.subheader("Key Metrics")
    
    workflow_summary = SessionManager.get_workflow_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Documents", workflow_summary.get('total_documents', 0))
    
    with col2:
        st.metric("Completed Phases", len(workflow_summary.get('completed_phases', [])))
    
    with col3:
        st.metric("Current Phase", workflow_summary.get('current_phase', 'setup').title())
    
    with col4:
        agent_progress = workflow_summary.get('agent_progress', {})
        active_agents = len([a for a in agent_progress.values() if a.get('status') == 'running'])
        st.metric("Active Agents", active_agents)
    
    # Token usage summary across all phases
    phase_outputs = st.session_state.workflow_state.get('phase_outputs', {})
    if phase_outputs:
        st.subheader("Token Usage Summary")
        
        total_tokens = sum(
            phase_data.get('batch_processing_stats', {}).get('total_tokens_processed', 0)
            for phase_data in phase_outputs.values()
        )
        total_batches = sum(
            phase_data.get('batch_processing_stats', {}).get('total_batches', 0)
            for phase_data in phase_outputs.values()
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tokens Processed", f"{total_tokens:,}")
        with col2:
            st.metric("Total Batches", total_batches)
        with col3:
            avg_tokens_per_batch = total_tokens // total_batches if total_batches > 0 else 0
            st.metric("Avg Tokens/Batch", f"{avg_tokens_per_batch:,}")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    logs = st.session_state.get('logs', [])
    if logs:
        recent_logs = logs[-5:]  # Last 5 logs
        for log in reversed(recent_logs):
            level = log.get('level', 'INFO')
            message = log.get('message', '')
            timestamp = log.get('timestamp', '')
            
            if level == 'ERROR':
                st.error(f"[{timestamp[:19]}] {message}")
            elif level == 'WARNING':
                st.warning(f"[{timestamp[:19]}] {message}")
            else:
                st.info(f"[{timestamp[:19]}] {message}")
    else:
        st.info("No recent activity")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("New Project", use_container_width=True):
            SessionManager.reset_workflow()
            st.rerun()
    
    with col2:
        if st.button("Continue Workflow", use_container_width=True):
            st.session_state.workflow_state['current_phase'] = 'workflow'
            st.rerun()
    
    with col3:
        if st.button("View Results", use_container_width=True):
            st.session_state.workflow_state['current_phase'] = 'results'
            st.rerun()

if __name__ == "__main__":
    main()