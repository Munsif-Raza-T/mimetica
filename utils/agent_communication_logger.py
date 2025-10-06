import streamlit as st
import time
import sys
import io
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import contextmanager


class AgentCommunicationLogger:
    """
    Captures and stores all agent communications and CrewAI verbose output
    during workflow execution for display in the results page dropdown.
    """
    
    def __init__(self):
        self.communications = []
        self.current_phase = None
        self.current_agent = None
        self.original_stdout = None
        self.original_stderr = None
        self.captured_output = ""
        
    def start_phase_logging(self, phase_name: str):
        """Start logging for a specific workflow phase"""
        self.current_phase = phase_name
        self.add_communication(
            "SYSTEM", 
            f"🚀 Starting {phase_name.replace('_', ' ').title()} Phase",
            "phase_start"
        )
    
    def end_phase_logging(self, phase_name: str, success: bool = True):
        """End logging for a specific workflow phase"""
        status = "✅ COMPLETED" if success else "❌ FAILED"
        self.add_communication(
            "SYSTEM", 
            f"{status} {phase_name.replace('_', ' ').title()} Phase",
            "phase_end"
        )
        self.current_phase = None
    
    def start_agent_execution(self, agent_name: str, task_description: str = None):
        """Start logging for a specific agent execution"""
        self.current_agent = agent_name
        message = f"🤖 Agent {agent_name} started execution"
        if task_description:
            message += f"\n📋 Task: {task_description}"
        
        self.add_communication(
            agent_name,
            message,
            "agent_start"
        )
    
    def end_agent_execution(self, agent_name: str, result_summary: str = None):
        """End logging for a specific agent execution"""
        message = f"✅ Agent {agent_name} completed execution"
        if result_summary:
            message += f"\n📊 Result: {result_summary[:200]}..."
        
        self.add_communication(
            agent_name,
            message,
            "agent_end"
        )
        self.current_agent = None
    
    def log_agent_reasoning(self, agent_name: str, reasoning: str):
        """Log agent reasoning process"""
        self.add_communication(
            agent_name,
            f"🧠 Reasoning: {reasoning}",
            "agent_reasoning"
        )
    
    def log_agent_action(self, agent_name: str, action: str, details: str = None):
        """Log agent action"""
        message = f"⚡ Action: {action}"
        if details:
            message += f"\n📝 Details: {details}"
        
        self.add_communication(
            agent_name,
            message,
            "agent_action"
        )
    
    def log_agent_communication(self, from_agent: str, to_agent: str, message: str):
        """Log communication between agents"""
        self.add_communication(
            f"{from_agent} → {to_agent}",
            f"💬 {message}",
            "agent_communication"
        )
    
    def log_tool_usage(self, agent_name: str, tool_name: str, tool_input: str, tool_output: str):
        """Log tool usage by agents"""
        message = f"🔧 Tool Used: {tool_name}\n"
        message += f"📥 Input: {tool_input[:150]}...\n" if len(tool_input) > 150 else f"📥 Input: {tool_input}\n"
        message += f"📤 Output: {tool_output[:150]}..." if len(tool_output) > 150 else f"📤 Output: {tool_output}"
        
        self.add_communication(
            agent_name,
            message,
            "tool_usage"
        )
    
    def log_crewai_output(self, output: str):
        """Log raw CrewAI verbose output"""
        if output and output.strip():
            # Clean and format the output
            cleaned_output = self._clean_output(output)
            if cleaned_output:
                self.add_communication(
                    self.current_agent or "CrewAI",
                    cleaned_output,
                    "crewai_verbose"
                )
    
    def log_error(self, source: str, error_message: str, exception: Exception = None):
        """Log errors during execution"""
        message = f"❌ Error: {error_message}"
        if exception:
            message += f"\n🔍 Exception: {str(exception)}"
        
        self.add_communication(
            source,
            message,
            "error"
        )
    
    def add_communication(self, source: str, message: str, comm_type: str = "general"):
        """Add a communication entry"""
        communication = {
            'timestamp': datetime.now().isoformat(),
            'phase': self.current_phase,
            'source': source,
            'message': message,
            'type': comm_type,
            'id': len(self.communications) + 1
        }
        
        self.communications.append(communication)
        
        # Also add to session logs for backward compatibility
        try:
            from utils.session_manager import SessionManager
            SessionManager.add_log("INFO", f"[{source}] {message}", agent=source)
        except ImportError:
            pass
    
    def _clean_output(self, output: str) -> str:
        """Clean and format CrewAI output for better readability"""
        if not output:
            return ""
        
        # Remove ANSI color codes
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        cleaned = ansi_escape.sub('', output)
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        cleaned = cleaned.strip()
        
        # Skip very short or repetitive outputs
        if len(cleaned) < 10 or cleaned.count('\n') > 20:
            return ""
        
        return cleaned
    
    @contextmanager
    def capture_stdout(self):
        """Context manager to capture stdout during CrewAI execution"""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            sys.stdout = stdout_capture
            sys.stderr = stderr_capture
            yield stdout_capture, stderr_capture
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            # Log captured output
            stdout_content = stdout_capture.getvalue()
            stderr_content = stderr_capture.getvalue()
            
            if stdout_content:
                self.log_crewai_output(stdout_content)
            
            if stderr_content:
                self.log_error("CrewAI", stderr_content)
    
    def get_communications_by_phase(self, phase_name: str) -> List[Dict[str, Any]]:
        """Get all communications for a specific phase"""
        return [comm for comm in self.communications if comm['phase'] == phase_name]
    
    def get_communications_by_type(self, comm_type: str) -> List[Dict[str, Any]]:
        """Get all communications of a specific type"""
        return [comm for comm in self.communications if comm['type'] == comm_type]
    
    def get_all_communications(self) -> List[Dict[str, Any]]:
        """Get all communications"""
        return self.communications.copy()
    
    def get_communications_summary(self) -> Dict[str, Any]:
        """Get a summary of all communications"""
        total_comms = len(self.communications)
        phases = set(comm['phase'] for comm in self.communications if comm['phase'])
        sources = set(comm['source'] for comm in self.communications)
        types = {}
        
        for comm in self.communications:
            comm_type = comm['type']
            types[comm_type] = types.get(comm_type, 0) + 1
        
        return {
            'total_communications': total_comms,
            'phases_covered': list(phases),
            'sources': list(sources),
            'communication_types': types,
            'duration_covered': self._get_duration() if self.communications else "0 seconds"
        }
    
    def _get_duration(self) -> str:
        """Calculate the duration covered by communications"""
        if not self.communications:
            return "0 seconds"
        
        start_time = datetime.fromisoformat(self.communications[0]['timestamp'])
        end_time = datetime.fromisoformat(self.communications[-1]['timestamp'])
        duration = end_time - start_time
        
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def format_for_display(self) -> str:
        """Format all communications for display in dropdown"""
        if not self.communications:
            return "No agent communications recorded."
        
        formatted = "# MIMÉTICA Agent Communications and Execution Log\n\n"
        formatted += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        summary = self.get_communications_summary()
        formatted += "## Summary\n"
        formatted += f"- **Total Communications:** {summary['total_communications']}\n"
        formatted += f"- **Phases Covered:** {', '.join(summary['phases_covered'])}\n"
        formatted += f"- **Duration:** {summary['duration_covered']}\n"
        formatted += f"- **Active Agents:** {', '.join(summary['sources'])}\n\n"
        
        formatted += "---\n\n"
        formatted += "## Detailed Communication Log\n\n"
        
        current_phase = None
        for comm in self.communications:
            # Add phase header if phase changed
            if comm['phase'] and comm['phase'] != current_phase:
                current_phase = comm['phase']
                formatted += f"\n### 📋 Phase: {current_phase.replace('_', ' ').title()}\n\n"
            
            # Format timestamp
            timestamp = datetime.fromisoformat(comm['timestamp']).strftime('%H:%M:%S')
            
            # Format the communication entry
            formatted += f"**[{timestamp}] {comm['source']}**\n"
            formatted += f"{comm['message']}\n\n"
        
        formatted += "\n---\n\n"
        formatted += "*This log contains all agent communications, reasoning, actions, and tool usage during the MIMÉTICA workflow execution.*"
        
        return formatted
    
    def clear_communications(self):
        """Clear all stored communications"""
        self.communications = []
        self.current_phase = None
        self.current_agent = None
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export communications to dictionary for JSON serialization"""
        return {
            'communications': self.communications,
            'summary': self.get_communications_summary(),
            'export_timestamp': datetime.now().isoformat()
        }


# Global instance for the application
agent_comm_logger = AgentCommunicationLogger()