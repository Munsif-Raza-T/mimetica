import streamlit as st
from typing import Dict, Any, Optional
from datetime import datetime
import json

class SessionManager:
    """Manages session state and workflow progress"""
    
    @staticmethod
    def init_session():
        """Initialize session state variables"""
        if 'workflow_state' not in st.session_state:
            st.session_state.workflow_state = {
                'current_phase': 'setup',
                'completed_phases': [],
                'phase_outputs': {},
                'documents': [],
                'workflow_id': f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
        
        if 'agent_progress' not in st.session_state:
            st.session_state.agent_progress = {}
        
        if 'logs' not in st.session_state:
            st.session_state.logs = []
    
    @staticmethod
    def update_phase(phase: str, status: str = 'in_progress'):
        """Update current workflow phase"""
        st.session_state.workflow_state['current_phase'] = phase
        if status == 'completed' and phase not in st.session_state.workflow_state['completed_phases']:
            st.session_state.workflow_state['completed_phases'].append(phase)
    
    @staticmethod
    def save_phase_output(phase: str, output: Dict[str, Any]):
        """Save output from a workflow phase"""
        # Ensure the output is JSON serializable
        try:
            if isinstance(output, dict):
                serializable_output = {
                    k: str(v) if not isinstance(v, (str, int, float, bool, list, dict)) else v
                    for k, v in output.items()
                }
            else:
                serializable_output = str(output)
            
            st.session_state.workflow_state['phase_outputs'][phase] = {
                'output': serializable_output,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            st.error(f"Error serializing phase output: {str(e)}")
            # Fallback to string representation
            st.session_state.workflow_state['phase_outputs'][phase] = {
                'output': str(output),
                'timestamp': datetime.now().isoformat(),
                'serialization_error': str(e)
            }
    
    @staticmethod
    def get_phase_output(phase: str) -> Optional[Dict[str, Any]]:
        """Get output from a specific phase"""
        return st.session_state.workflow_state['phase_outputs'].get(phase)
    
    @staticmethod
    def update_agent_progress(agent_name: str, progress: float, status: str, message: str = ""):
        """Update individual agent progress"""
        st.session_state.agent_progress[agent_name] = {
            'progress': progress,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def add_log(level: str, message: str, agent: str = None):
        """Add log entry"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'agent': agent
        }
        st.session_state.logs.append(log_entry)
        
        # Keep only last 1000 logs
        if len(st.session_state.logs) > 1000:
            st.session_state.logs = st.session_state.logs[-1000:]
    
    @staticmethod
    def get_workflow_summary() -> Dict[str, Any]:
        """Get complete workflow state summary"""
        return {
            'workflow_id': st.session_state.workflow_state['workflow_id'],
            'current_phase': st.session_state.workflow_state['current_phase'],
            'completed_phases': st.session_state.workflow_state['completed_phases'],
            'total_documents': len(st.session_state.workflow_state['documents']),
            'agent_progress': st.session_state.agent_progress,
            'last_updated': datetime.now().isoformat()
        }
    
    @staticmethod
    def reset_workflow():
        """Reset workflow state for new session and delete session vector collection"""
        from utils.vector_store import VectorStore
        VectorStore.delete_session_index()
        if 'workflow_state' in st.session_state:
            del st.session_state.workflow_state
        if 'agent_progress' in st.session_state:
            del st.session_state.agent_progress
        if 'logs' in st.session_state:
            del st.session_state.logs
        SessionManager.init_session()
