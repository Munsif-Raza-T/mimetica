import json
from typing import Dict, Any, Optional, List
from datetime import datetime

import streamlit as st


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
        
        # Initialize agent communications storage
        if 'agent_communications' not in st.session_state:
            st.session_state.agent_communications = []
        
        # Initialize agent communication logger
        if 'agent_comm_logger' not in st.session_state:
            try:
                from utils.agent_communication_logger import AgentCommunicationLogger
                st.session_state.agent_comm_logger = AgentCommunicationLogger()
            except ImportError:
                st.session_state.agent_comm_logger = None
    
    @staticmethod
    def update_phase(phase: str, status: str = 'in_progress'):
        """Update current workflow phase"""
        st.session_state.workflow_state['current_phase'] = phase
        if status == 'completed' and phase not in st.session_state.workflow_state['completed_phases']:
            st.session_state.workflow_state['completed_phases'].append(phase)
            
            # Check if all phases are completed
            SessionManager.check_workflow_completion()
    
    @staticmethod
    def check_workflow_completion():
        """Check if all workflow phases are completed and mark workflow as complete"""
        required_phases = [
            'collection', 'analysis', 'definition', 'exploration', 
            'creation', 'implementation', 'simulation', 'evaluation', 'report'
        ]
        
        completed_phases = st.session_state.workflow_state.get('completed_phases', [])
        
        # Check if all required phases are completed
        if all(phase in completed_phases for phase in required_phases):
            if not st.session_state.workflow_state.get('workflow_completed', False):
                st.session_state.workflow_state['workflow_completed'] = True
                st.session_state.workflow_state['workflow_completion_time'] = datetime.now().isoformat()
                SessionManager.add_log("INFO", "Complete DECIDE workflow execution finished successfully")
    
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
    def get_agent_comm_logger():
        """Get the agent communication logger instance"""
        return st.session_state.get('agent_comm_logger')
    
    @staticmethod
    def add_agent_communication(source: str, message: str, comm_type: str = "general", phase: str = None):
        """Add agent communication entry"""
        communication = {
            'timestamp': datetime.now().isoformat(),
            'phase': phase or st.session_state.workflow_state.get('current_phase'),
            'source': source,
            'message': message,
            'type': comm_type,
            'id': len(st.session_state.agent_communications) + 1
        }
        
        st.session_state.agent_communications.append(communication)
        
        # Also use the logger if available
        logger = SessionManager.get_agent_comm_logger()
        if logger:
            logger.add_communication(source, message, comm_type)
    
    @staticmethod
    def get_agent_communications() -> list:
        """Get all agent communications"""
        return st.session_state.get('agent_communications', [])
    
    @staticmethod
    def get_agent_communications_by_phase(phase_name: str) -> list:
        """Get agent communications for a specific phase"""
        all_comms = SessionManager.get_agent_communications()
        return [comm for comm in all_comms if comm.get('phase') == phase_name]
    
    @staticmethod
    def clear_agent_communications():
        """Clear all agent communications"""
        st.session_state.agent_communications = []
        logger = SessionManager.get_agent_comm_logger()
        if logger:
            logger.clear_communications()
    
    @staticmethod
    def get_formatted_agent_communications() -> str:
        """Get formatted agent communications for display"""
        logger = SessionManager.get_agent_comm_logger()
        if logger:
            return logger.format_for_display()
        
        # Fallback formatting
        comms = SessionManager.get_agent_communications()
        if not comms:
            return "No agent communications recorded."
        
        formatted = "# MIMÉTICA Agent Communications Log\n\n"
        formatted += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        formatted += "## Communication Log\n\n"
        
        for comm in comms:
            timestamp = datetime.fromisoformat(comm['timestamp']).strftime('%H:%M:%S')
            formatted += f"**[{timestamp}] {comm['source']}**\n"
            formatted += f"{comm['message']}\n\n"
        
        return formatted
    
    @staticmethod
    def get_workflow_summary() -> Dict[str, Any]:
        """Get complete workflow state summary"""
        return {
            'workflow_id': st.session_state.workflow_state['workflow_id'],
            'current_phase': st.session_state.workflow_state['current_phase'],
            'completed_phases': st.session_state.workflow_state['completed_phases'],
            'total_documents': len(st.session_state.workflow_state['documents']),
            'agent_progress': st.session_state.agent_progress,
            'workflow_completed': st.session_state.workflow_state.get('workflow_completed', False),
            'workflow_completion_time': st.session_state.workflow_state.get('workflow_completion_time'),
            'last_updated': datetime.now().isoformat()
        }
    
    @staticmethod
    def is_workflow_completed() -> bool:
        """Check if the workflow is completed"""
        return st.session_state.workflow_state.get('workflow_completed', False)
    
    @staticmethod
    def reset_workflow():
        """Reset workflow state for new session and clear session vector collection"""
        try:
            from utils.vector_store import VectorStore
            # Use clear instead of delete to preserve collection structure
            VectorStore.clear_session_collection()
        except ImportError:
            pass  # VectorStore not available
        
        if 'workflow_state' in st.session_state:
            del st.session_state.workflow_state
        if 'agent_progress' in st.session_state:
            del st.session_state.agent_progress
        if 'logs' in st.session_state:
            del st.session_state.logs
        if 'agent_communications' in st.session_state:
            del st.session_state.agent_communications
        if 'agent_comm_logger' in st.session_state:
            del st.session_state.agent_comm_logger
        
        # Also clear workflow instance to force fresh initialization
        if 'workflow_instance' in st.session_state:
            del st.session_state.workflow_instance
        
        SessionManager.init_session()
