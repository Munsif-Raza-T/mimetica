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
from dotenv import load_dotenv
load_dotenv()


# Import custom modules
from config import config
from utils import AuthManager, SessionManager, DocumentProcessor, VectorStore
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
    </style>
    """, unsafe_allow_html=True)
    
    # Header
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
        
        for phase_name, phase_key in phases:
            if phase_key in completed_phases:
                st.success(f"✅ {phase_name}")
            elif phase_key == current_phase:
                st.warning(f"🔄 {phase_name}")
            else:
                st.info(f"⏳ {phase_name}")
        
        st.divider()
        
        # Quick actions
        st.subheader("⚡ Quick Actions")
        
        if st.button("Dashboard", use_container_width=True):
            st.session_state.workflow_state['current_phase'] = 'dashboard'
            st.rerun()
        
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
        
        # Logout
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            # Delete all data in 'mimetica' collection
            try:
                vector_store = VectorStore(collection_name="mimetica") if 'collection_name' in VectorStore.__init__.__code__.co_varnames else VectorStore()
                if hasattr(vector_store, 'collection_exists') and vector_store.collection_exists("mimetica"):
                    vector_store.delete_collection("mimetica")
            except Exception as e:
                st.warning(f"Could not delete 'mimetica' collection: {e}")
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
        
        with st.form("project_info"):
            project_name = st.text_input("Project Name", value="Strategic Initiative Analysis")
            project_description = st.text_area("Project Description", 
                                             value="Comprehensive analysis of strategic initiative using MIMÉTICA methodology")
            analysis_focus = st.selectbox("Analysis Focus", 
                                        ["Campaign ROI Optimization", "Digital Transformation", 
                                         "Customer Experience Improvement", "New Service Design", "Other"])
            
            if analysis_focus == "Other":
                custom_focus = st.text_input("Specify Custom Focus")
            
            submitted = st.form_submit_button("💾 Save Project Info", use_container_width=True)
            
            if submitted:
                # Save project info to session
                st.session_state.workflow_state['project_info'] = {
                    'name': project_name,
                    'description': project_description,
                    'focus': analysis_focus,
                    'custom_focus': custom_focus if analysis_focus == "Other" else None,
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
    
    # Workflow control panel
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Run Complete Workflow", type="primary", use_container_width=True):
            run_complete_workflow(workflow)
    
    with col2:
        if st.button("Run Single Phase", use_container_width=True):
            run_single_phase(workflow)
    
    with col3:
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
    """Run the complete DECIDE workflow with TokenBatchManager"""
    try:
        documents = st.session_state.workflow_state.get('documents', [])
        if not documents:
            st.error("No documents found. Please upload documents first.")
            return

        with st.spinner("🔄 Running complete workflow, this might take 5-10 minutes to complete..."):
            # Initialize TokenBatchManager with conservative settings for gpt-4o-mini
            token_manager = TokenBatchManager(
                tpm_limit=200000,           # Your actual TPM limit
                safety_margin=0.7,          # Use 70% of limit for safety
                max_tokens_per_request=120000,  # Conservative request limit
                min_chunk_size=100,         # Minimum chunk size in words
                max_chunk_size=800          # Maximum chunk size in words
            )
            
            # Process documents into smart batches
            st.info("📋 Processing documents into optimized batches...")
            batches, processing_info = token_manager.process_documents_with_batching(documents)
            
            # Display batch processing information
            st.success(f"✅ Document processing complete:")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Documents", processing_info['original_documents'])
            with col2:
                st.metric("Chunks Created", processing_info['total_chunks'])
            with col3:
                st.metric("Batches", processing_info['total_batches'])
            with col4:
                st.metric("Est. Tokens", f"{processing_info['estimated_total_tokens']:,}")
            
            # Process each batch
            results = None
            successful_batches = 0
            failed_batches = 0
            
            progress_bar = st.progress(0)
            status_container = st.empty()
            
            for batch_idx, batch in enumerate(batches):
                try:
                    # Calculate batch tokens
                    batch_tokens = sum(doc.get('estimated_tokens', 0) for doc in batch)
                    
                    # Update progress
                    progress = (batch_idx + 1) / len(batches)
                    progress_bar.progress(progress)
                    
                    status_container.info(
                        f"🔄 Processing batch {batch_idx + 1}/{len(batches)} "
                        f"({len(batch)} documents, ~{batch_tokens:,} tokens)"
                    )
                    
                    # Wait for rate limit window if needed
                    if not token_manager.wait_for_rate_limit_window(batch_tokens):
                        st.warning(f"⚠️ Rate limit timeout for batch {batch_idx + 1}, reducing batch size...")
                        # Split batch in half and retry
                        if len(batch) > 1:
                            half_size = len(batch) // 2
                            batch = batch[:half_size]
                            batch_tokens = sum(doc.get('estimated_tokens', 0) for doc in batch)
                    
                    # Track token usage
                    token_manager.add_token_usage(batch_tokens)
                    
                    # Execute workflow on batch
                    workflow.current_batch = batch
                    batch_results = workflow.run_complete_workflow()
                    
                    # Merge results
                    if results is None:
                        results = batch_results
                    else:
                        if isinstance(results.get('output'), dict) and isinstance(batch_results.get('output'), dict):
                            results['output'].update(batch_results['output'])
                    
                    # Update statistics
                    token_manager.update_batch_stats(True)
                    successful_batches += 1
                    
                    # Show batch completion
                    st.success(f"✅ Batch {batch_idx + 1} completed successfully")
                    
                except Exception as batch_error:
                    token_manager.update_batch_stats(False)
                    failed_batches += 1
                    
                    if "RateLimitError" in str(batch_error):
                        st.warning(f"⚠️ Rate limit hit on batch {batch_idx + 1}, implementing exponential backoff...")
                        
                        # Exponential backoff
                        wait_time = min(30 * (2 ** failed_batches), 120)
                        status_container.warning(f"⏳ Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        
                        # Retry with smaller batch
                        if len(batch) > 1:
                            retry_batch_size = max(1, len(batch) // 2)
                            retry_batch = batch[:retry_batch_size]
                            
                            try:
                                workflow.current_batch = retry_batch
                                batch_results = workflow.run_complete_workflow()
                                
                                if results is None:
                                    results = batch_results
                                else:
                                    if isinstance(results.get('output'), dict) and isinstance(batch_results.get('output'), dict):
                                        results['output'].update(batch_results['output'])
                                
                                st.success(f"✅ Batch {batch_idx + 1} retry completed with {len(retry_batch)} documents")
                                token_manager.update_batch_stats(True)
                                successful_batches += 1
                                failed_batches -= 1  # Adjust since retry succeeded
                                
                            except Exception as retry_error:
                                st.error(f"❌ Batch {batch_idx + 1} failed even on retry: {str(retry_error)}")
                        else:
                            st.error(f"❌ Batch {batch_idx + 1} failed and cannot be split further: {str(batch_error)}")
                    else:
                        st.error(f"❌ Batch {batch_idx + 1} failed: {str(batch_error)}")

        # Processing complete - show summary
        processing_summary = token_manager.get_processing_summary()
        
        st.success("🎉 Complete workflow processing finished!")
        
        # Display final statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Successful Batches", successful_batches)
        with col2:
            st.metric("Failed Batches", failed_batches)
        with col3:
            st.metric("Success Rate", f"{processing_summary.get('success_rate', 0):.1f}%")
        with col4:
            st.metric("Tokens Processed", f"{processing_summary.get('total_tokens_processed', 0):,}")

        # Convert and save results
        if results and successful_batches > 0:
            try:
                if hasattr(results, '__dict__'):
                    results_dict = {
                        'success': True,
                        'output': {},
                        'agent_progress': {},
                        'summary': processing_summary
                    }
                    
                    if hasattr(results, 'output'):
                        output_data = getattr(results, 'output')
                        if isinstance(output_data, dict):
                            results_dict['output'] = {
                                k: str(v) if not isinstance(v, (str, int, float, bool, list, dict)) else v
                                for k, v in output_data.items()
                            }
                        else:
                            results_dict['output'] = str(output_data)
                    
                    # Handle agent progress
                    agent_progress = getattr(results, 'agent_progress', {})
                    if isinstance(agent_progress, dict):
                        results_dict['agent_progress'] = {
                            k: {
                                'progress': float(v.get('progress', 0)),
                                'status': str(v.get('status', '')),
                                'message': str(v.get('message', '')),
                                'timestamp': v.get('timestamp', '')
                            } if isinstance(v, dict) else {'progress': 0, 'status': str(v)}
                            for k, v in agent_progress.items()
                        }
                    
                    results = results_dict
                    
            except Exception as e:
                st.error(f"Error converting workflow output: {str(e)}")
                results = {
                    'success': False,
                    'error': f"Failed to convert output: {str(e)}",
                    'output': str(results)
                }
            
            # Save results
            if isinstance(results.get('agent_progress'), dict):
                st.session_state['agent_progress'] = results['agent_progress']
            
            if results.get('success'):
                st.success("✅ Complete workflow executed successfully!")
                SessionManager.update_phase('results', 'completed')
                
                serializable_results = {
                    'success': results.get('success', True),
                    'output': results.get('output', {}),
                    'agent_progress': results.get('agent_progress', {}),
                    'summary': results.get('summary', {}),
                    'batch_processing_stats': processing_summary
                }
                
                SessionManager.save_phase_output('complete_workflow', serializable_results)
                
                st.subheader("Workflow Summary")
                st.json(serializable_results.get('summary', {}))
                
                # Add View Results button after successful completion
                if st.button("🔍 View Results", type="primary", use_container_width=True):
                    st.session_state.workflow_state['current_phase'] = 'results'
                    st.rerun()
            else:
                st.error(f"❌ Workflow execution failed: {results.get('error', 'Unknown error')}")
        else:
            st.error("❌ Workflow execution failed: No successful batches processed")
            
    except Exception as e:
        st.error(f"Failed to run workflow: {str(e)}")
        SessionManager.add_log("ERROR", f"Complete workflow execution failed: {str(e)}")

def run_single_phase(workflow):
    """Run a single phase of the workflow with TokenBatchManager"""
    phases = [
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
    
    selected_phase = st.selectbox("Select Phase to Run", 
                                 options=[p[1] for p in phases],
                                 format_func=lambda x: next(p[0] for p in phases if p[1] == x))
    
    if st.button(f"▶️ Run {selected_phase} Phase", type="primary"):
        try:
            documents = st.session_state.workflow_state.get('documents', [])
            if not documents:
                st.error("No documents found. Please upload documents first.")
                return
                
            with st.spinner(f"🔄 Running {selected_phase} phase with intelligent batching..."):
                # Initialize TokenBatchManager for single phase
                token_manager = TokenBatchManager(
                    tpm_limit=200000,
                    safety_margin=0.7,
                    max_tokens_per_request=100000,
                    min_chunk_size=100,
                    max_chunk_size=600  # Smaller chunks for single phase
                )
                
                # Process documents into batches
                batches, processing_info = token_manager.process_documents_with_batching(documents)
                
                st.info(f"📋 Processing {selected_phase} phase in {len(batches)} batches...")
                
                result = None
                progress_bar = st.progress(0)
                
                for batch_idx, batch in enumerate(batches):
                    try:
                        batch_tokens = sum(doc.get('estimated_tokens', 0) for doc in batch)
                        
                        # Update progress
                        progress = (batch_idx + 1) / len(batches)
                        progress_bar.progress(progress)
                        
                        st.info(f"🔄 Processing batch {batch_idx + 1}/{len(batches)} (~{batch_tokens:,} tokens)")
                        
                        # Rate limit management
                        if not token_manager.wait_for_rate_limit_window(batch_tokens):
                            st.warning(f"⚠️ Reducing batch size due to rate limits...")
                            if len(batch) > 1:
                                batch = batch[:len(batch)//2]
                                batch_tokens = sum(doc.get('estimated_tokens', 0) for doc in batch)
                        
                        # Track token usage
                        token_manager.add_token_usage(batch_tokens)
                        
                        # Execute phase on batch
                        workflow.current_batch = batch
                        batch_result = workflow.run_single_phase(selected_phase)
                        
                        # Merge results
                        if result is None:
                            result = batch_result
                        else:
                            if isinstance(result.get('output'), dict) and isinstance(batch_result.get('output'), dict):
                                result['output'].update(batch_result['output'])
                        
                        token_manager.update_batch_stats(True)
                        
                    except Exception as batch_error:
                        token_manager.update_batch_stats(False)
                        
                        if "RateLimitError" in str(batch_error):
                            st.warning(f"⚠️ Rate limit hit, implementing backoff...")
                            time.sleep(min(10 * (batch_idx + 1), 60))
                            
                            # Retry with smaller batch
                            if len(batch) > 1:
                                retry_batch = batch[:len(batch)//2]
                                try:
                                    workflow.current_batch = retry_batch
                                    batch_result = workflow.run_single_phase(selected_phase)
                                    
                                    if result is None:
                                        result = batch_result
                                    else:
                                        if isinstance(result.get('output'), dict) and isinstance(batch_result.get('output'), dict):
                                            result['output'].update(batch_result['output'])
                                    
                                    st.success(f"✅ Batch {batch_idx + 1} completed on retry")
                                    
                                except Exception as retry_error:
                                    st.error(f"❌ Batch {batch_idx + 1} failed on retry: {str(retry_error)}")
                            else:
                                st.error(f"❌ Single document batch failed: {str(batch_error)}")
                        else:
                            raise batch_error

                # Convert and save results
                if result:
                    try:
                        if hasattr(result, '__dict__'):
                            result_dict = {
                                'success': True,
                                'output': {},
                                'agent_progress': {},
                                'summary': token_manager.get_processing_summary()
                            }
                            
                            # Safely extract and convert output
                            if hasattr(result, 'output'):
                                output_data = getattr(result, 'output')
                                if isinstance(output_data, dict):
                                    result_dict['output'] = {
                                        k: str(v) if not isinstance(v, (str, int, float, bool, list, dict)) else v
                                        for k, v in output_data.items()
                                    }
                                else:
                                    result_dict['output'] = str(output_data)
                            
                            # Safely extract and convert agent progress
                            agent_progress = getattr(result, 'agent_progress', {})
                            if isinstance(agent_progress, dict):
                                result_dict['agent_progress'] = {
                                    k: {
                                        'progress': float(v.get('progress', 0)),
                                        'status': str(v.get('status', '')),
                                        'message': str(v.get('message', '')),
                                        'timestamp': v.get('timestamp', '')
                                    } if isinstance(v, dict) else {'progress': 0, 'status': str(v)}
                                    for k, v in agent_progress.items()
                                }
                            
                            result = result_dict
                            
                    except Exception as e:
                        st.error(f"Error converting workflow output: {str(e)}")
                        SessionManager.add_log("ERROR", f"Output conversion failed: {str(e)}")
                        result = {
                            'success': False,
                            'error': f"Failed to convert output: {str(e)}",
                            'output': str(result)
                        }
                    
                    # Save agent progress if available
                    if isinstance(result.get('agent_progress'), dict):
                        st.session_state['agent_progress'] = result['agent_progress']

            # Display results
            processing_summary = token_manager.get_processing_summary()
            
            if result and result.get('success'):
                st.success(f"✅ {selected_phase} phase completed successfully!")
                
                # Show processing stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Batches Processed", processing_summary.get('successful_batches', 0))
                with col2:
                    st.metric("Total Tokens", f"{processing_summary.get('total_tokens_processed', 0):,}")
                with col3:
                    st.metric("Success Rate", f"{processing_summary.get('success_rate', 0):.1f}%")
                
                # Ensure the result is JSON serializable
                serializable_result = {
                    'success': result.get('success', True),
                    'output': result.get('output', {}),
                    'agent_progress': result.get('agent_progress', {}),
                    'summary': result.get('summary', {}),
                    'batch_processing_stats': processing_summary
                }
                
                SessionManager.save_phase_output(selected_phase, serializable_result)
                
                # Show phase output
                if 'output' in serializable_result:
                    st.subheader(f"📄 {selected_phase} Output")
                    st.text_area("Result", str(serializable_result['output']), height=300)
            else:
                st.error(f"❌ {selected_phase} phase failed: {result.get('error', 'Unknown error') if result else 'No result returned'}")
                
        except Exception as e:
            st.error(f"Failed to run {selected_phase} phase: {str(e)}")
            SessionManager.add_log("ERROR", f"Single phase execution failed: {str(e)}")

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
    st.header("Workflow Results & Deliverables")
    
    phase_outputs = st.session_state.workflow_state.get('phase_outputs', {})
    
    if not phase_outputs:
        st.warning("No results available. Please run the workflow first.")
        if st.button("← Back to Workflow"):
            st.session_state.workflow_state['current_phase'] = 'workflow'
            st.rerun()
        return
    
    # Results summary with batch processing stats
    st.subheader("Results Summary")
    
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
    
    # Final report section - FIXED TO EXTRACT PROPER MARKDOWN
    if 'report' in phase_outputs:
        st.subheader("Final Comprehensive Report")
        
        report_output = phase_outputs['report'].get('output', {})
        
        # Extract the actual markdown content from the nested structure
        markdown_content = ""
        if isinstance(report_output, str):
            # If output is already a string, use it directly
            markdown_content = report_output
        elif isinstance(report_output, dict):
            # If output is a dict, look for the markdown content
            # Based on your document, it seems the content starts with "# MIMÉTICA"
            if 'output' in report_output:
                markdown_content = report_output['output']
            else:
                # Convert the entire dict to string and extract markdown
                report_str = str(report_output)
                # Find the start of the markdown content (after "# MIMÉTICA")
                start_marker = "# MIMÉTICA Strategic Decision Support System"
                if start_marker in report_str:
                    start_idx = report_str.find(start_marker)
                    # Find the end (before any closing markers like quotes or braces)
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
        
        # Display the markdown content with proper formatting
        if markdown_content:
            st.markdown("### PDF Standard Format")
            st.markdown(markdown_content)
        else:
            st.error("Could not extract markdown content from report output")
            st.json(report_output)  # Show raw output for debugging
        
        # Download options
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("📄 Download PDF Report", type="primary", use_container_width=True):
                download_final_report('pdf')
        
        with col2:
            if st.button("📝 Download Markdown Report", use_container_width=True):
                download_final_report('markdown')
    
    # Other output files section - SHOW AS THEY ARE
    st.subheader("Other Output Files")
    
    # Display all non-report phases as they are
    for phase, output_info in phase_outputs.items():
        if phase != 'report':  # Skip report as it's already shown above
            with st.expander(f"📄 {phase.replace('_', ' ').title()}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    output_content = output_info.get('output', {})
                    # Display output files exactly as they are
                    if isinstance(output_content, dict):
                        st.json(output_content)
                    else:
                        st.text_area("Content", str(output_content), height=200, key=f"output_{phase}")
                
                with col2:
                    timestamp = output_info.get('timestamp', '')
                    st.write(f"**Generated:** {timestamp[:19] if timestamp else 'Unknown'}")
                    
                    # Show batch processing stats if available
                    if 'batch_processing_stats' in output_info:
                        stats = output_info['batch_processing_stats']
                        st.write("**Batch Stats:**")
                        st.write(f"- Chunks: {stats.get('total_chunks', 0)}")
                        st.write(f"- Batches: {stats.get('total_batches', 0)}")
                        st.write(f"- Tokens: {stats.get('total_tokens_processed', 0):,}")
                        st.write(f"- Success: {stats.get('success_rate', 0):.1f}%")
                    
                    # Download button for individual deliverable
                    if st.button(f"💾 Download", key=f"download_{phase}"):
                        download_deliverable(phase, output_info)
    
    # Simulation results visualization
    if 'simulation' in phase_outputs:
        show_simulation_visualizations(phase_outputs['simulation'])


def show_simulation_visualizations(simulation_output):
    """Display Monte Carlo simulation visualizations"""
    st.subheader("Monte Carlo Simulation Results")
    
    # Create sample visualization data (replace with actual simulation data)
    try:
        import numpy as np
        
        # Generate sample data for demonstration
        np.random.seed(42)
        optimistic_data = np.random.normal(120, 15, 1000)
        baseline_data = np.random.normal(100, 20, 1000)
        pessimistic_data = np.random.normal(80, 25, 1000)
        
        # Scenario comparison chart
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(x=optimistic_data, name="Optimistic", 
                                  opacity=0.7, nbinsx=30))
        fig.add_trace(go.Histogram(x=baseline_data, name="Baseline", 
                                  opacity=0.7, nbinsx=30))
        fig.add_trace(go.Histogram(x=pessimistic_data, name="Pessimistic", 
                                  opacity=0.7, nbinsx=30))
        
        fig.update_layout(
            title="Monte Carlo Simulation Results - Scenario Comparison",
            xaxis_title="Outcome Value",
            yaxis_title="Frequency",
            barmode='overlay'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Optimistic (P90)", f"{np.percentile(optimistic_data, 90):.1f}")
            st.metric("Mean", f"{np.mean(optimistic_data):.1f}")
            st.metric("Std Dev", f"{np.std(optimistic_data):.1f}")
        
        with col2:
            st.metric("Baseline (P50)", f"{np.percentile(baseline_data, 50):.1f}")
            st.metric("Mean", f"{np.mean(baseline_data):.1f}")
            st.metric("Std Dev", f"{np.std(baseline_data):.1f}")
        
        with col3:
            st.metric("Pessimistic (P10)", f"{np.percentile(pessimistic_data, 10):.1f}")
            st.metric("Mean", f"{np.mean(pessimistic_data):.1f}")
            st.metric("Std Dev", f"{np.std(pessimistic_data):.1f}")
        
    except Exception as e:
        st.error(f"Failed to generate simulation visualizations: {str(e)}")

def download_deliverable(phase: str, output_info: Dict[str, Any]):
    """Download individual deliverable"""
    try:
        content = output_info.get('output', {})
        timestamp = output_info.get('timestamp', datetime.now().isoformat())
        
        # Convert content to string
        if isinstance(content, dict):
            content_str = str(content)
        else:
            content_str = str(content)
        
        # Create download
        filename = f"mimetica_{phase}_{timestamp[:10]}.txt"
        
        st.download_button(
            label=f"Download {phase}",
            data=content_str,
            file_name=filename,
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Failed to prepare download: {str(e)}")

def download_final_report(format_type: str):
    """Download final comprehensive report"""
    try:
        phase_outputs = st.session_state.workflow_state.get('phase_outputs', {})
        
        if format_type == 'pdf':
            # For PDF, we would normally use a library like reportlab
            # For now, create a text version
            report_content = generate_comprehensive_report(phase_outputs)
            filename = f"mimetica_final_report_{datetime.now().strftime('%Y%m%d')}.txt"
            mime = "text/plain"
            
        else:  # markdown
            report_content = generate_markdown_report(phase_outputs)
            filename = f"mimetica_final_report_{datetime.now().strftime('%Y%m%d')}.md"
            mime = "text/markdown"
        
        st.download_button(
            label=f"Download {format_type.upper()} Report",
            data=report_content,
            file_name=filename,
            mime=mime
        )
        
    except Exception as e:
        st.error(f"Failed to generate {format_type} report: {str(e)}")

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