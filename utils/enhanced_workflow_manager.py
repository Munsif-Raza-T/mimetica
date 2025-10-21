import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import streamlit as st
from config import config
from utils.anthropic_rate_limiter import get_anthropic_rate_limiter, AnthropicRateLimiter
from utils.token_batch_manager import TokenBatchManager


class EnhancedWorkflowManager:
    def __init__(self, workflow_instance):
        self.workflow = workflow_instance

        try:
            self.current_model = config.validate_and_fix_selected_model()
        except Exception:
            self.current_model = getattr(config, "DEFAULT_MODEL", None)

        # ✅ Carga segura de la config del modelo
        model_map = getattr(config, "AVAILABLE_MODELS", {}) or {}
        self.model_config = model_map.get(self.current_model) or {}

        # ✅ Provider con fallback
        self.provider = self.model_config.get('provider', 'openai')

        self.anthropic_limiter = None
        self.openai_token_manager = None

        if self.provider == 'anthropic':
            self.anthropic_limiter = get_anthropic_rate_limiter()
        else:
            self.openai_token_manager = TokenBatchManager()

        self.execution_stats = {
            'start_time': None,
            'end_time': None,
            'phases_completed': [],
            'phases_failed': [],
            'total_wait_time': 0,
            'rate_limit_hits': 0,
            'provider': self.provider,
            'model': self.current_model
        }

        # ✅ AHORA _get_phase_settings devuelve un dict
        self.phase_settings = self._get_phase_settings()

        ws = st.session_state.setdefault("workflow_state", {})
        if "language_tag" not in ws:
            ws["language_tag"] = st.session_state.get("language_tag", "en")

    def _get_phase_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get phase execution settings based on provider using central config"""
        # lee del config con fallback seguro
        try:
            rl = config.get_rate_limit_settings(self.current_model) or {}
        except Exception:
            rl = {}

        if self.provider == 'anthropic':
            return {
                'inter_phase_delay': rl.get('inter_phase_delay', 15),
                'max_retries': rl.get('max_retries', 3),
                'retry_delay': rl.get('retry_delay', 30),
                'timeout_per_phase': 120,
                'chunk_documents': True,
                'max_document_tokens': 15000,
                'safety_margin': rl.get('safety_margin', 0.7),
            }
        else:  # openai / default
            return {
                'inter_phase_delay': rl.get('inter_phase_delay', 5),
                'max_retries': rl.get('max_retries', 2),
                'retry_delay': rl.get('retry_delay', 15),
                'timeout_per_phase': 180,
                'chunk_documents': False,
                'max_document_tokens': 20000,
                'safety_margin': rl.get('safety_margin', 0.85),
            }

    def estimate_phase_tokens(self, phase_name: str, phase_function: Callable) -> int:
        """
        Estimate tokens required for a workflow phase
        
        Args:
            phase_name: Name of the phase
            phase_function: Phase function to analyze
            
        Returns:
            Estimated token count
        """
        base_estimates = {
            'collection': 8000,
            'analysis': 12000,
            'definition': 10000,
            'exploration': 15000,  # Highest because it does research
            'creation': 12000,
            'implementation': 10000,
            'simulation': 8000,
            'evaluation': 6000,
            'report': 14000  # High because it synthesizes all phases
        }
        
        base_estimate = base_estimates.get(phase_name, 10000)
        
        # Adjust based on provider
        if self.provider == 'anthropic':
            # Anthropic tends to use slightly more tokens
            return int(base_estimate * 1.1)
        else:
            return base_estimate
    
    def wait_between_phases(self, next_phase_name: str, estimated_tokens: int):
        """
        Wait appropriate time between phases based on provider and rate limits
        
        Args:
            next_phase_name: Name of the next phase to execute
            estimated_tokens: Estimated tokens for next phase
        """
        delay = self.phase_settings['inter_phase_delay']
        
        if self.provider == 'anthropic' and self.anthropic_limiter:
            # Check if we need additional wait time for Anthropic
            usage = self.anthropic_limiter.get_current_usage()
            
            if usage['tokens_last_minute'] > (self.anthropic_limiter.EFFECTIVE_TPM * 0.6):
                # We're using more than 60% of our limit, be more cautious
                additional_delay = min(30, (usage['tokens_last_minute'] / self.anthropic_limiter.EFFECTIVE_TPM) * 60)
                delay = max(delay, additional_delay)
                
                if st:
                    st.info(
                        f"🛡️ Rate limit protection: Extended delay {delay:.1f}s before {next_phase_name} "
                        f"(current usage: {usage['tokens_last_minute']:,}/{self.anthropic_limiter.EFFECTIVE_TPM:,})"
                    )
        
        if delay > 0:
            if st:
                st.info(f"⏸️ Waiting {delay:.1f}s before starting {next_phase_name} phase...")
            time.sleep(delay)
            self.execution_stats['total_wait_time'] += delay
    
    def execute_phase_with_rate_limiting(self, phase_name: str, phase_function: Callable) -> Dict[str, Any]:
        """
        Execute a workflow phase with proper rate limiting
        
        Args:
            phase_name: Name of the phase
            phase_function: Function to execute for this phase
            
        Returns:
            Phase execution result
        """
        estimated_tokens = self.estimate_phase_tokens(phase_name, phase_function)
        max_retries = self.phase_settings['max_retries']
        retry_delay = self.phase_settings['retry_delay']
        
        if st:
            st.info(f"🚀 Starting {phase_name} phase (estimated {estimated_tokens:,} tokens)")
        
        for attempt in range(max_retries + 1):
            try:
                if self.provider == 'anthropic' and self.anthropic_limiter:
                    # Use Anthropic rate limiter
                    if not self.anthropic_limiter.wait_for_availability(
                        estimated_tokens, 
                        max_wait=self.phase_settings['timeout_per_phase']
                    ):
                        raise Exception(f"Rate limit timeout for {phase_name} phase")
                    
                    # Execute the phase
                    start_time = time.time()
                    result = phase_function()
                    execution_time = time.time() - start_time
                    
                    # Record the request
                    self.anthropic_limiter.record_request(estimated_tokens)
                    
                    if st:
                        st.success(f"✅ {phase_name} phase completed in {execution_time:.1f}s")
                    
                    return result
                
                elif self.provider == 'openai' and self.openai_token_manager:
                    # Use OpenAI token manager
                    if not self.openai_token_manager.wait_for_rate_limit_window(estimated_tokens):
                        if st:
                            st.warning(f"⚠️ Rate limit timeout for {phase_name}, proceeding with caution...")
                    
                    # Execute the phase
                    start_time = time.time()
                    result = phase_function()
                    execution_time = time.time() - start_time
                    
                    # Record token usage
                    self.openai_token_manager.add_token_usage(estimated_tokens)
                    
                    if st:
                        st.success(f"✅ {phase_name} phase completed in {execution_time:.1f}s")
                    
                    return result
                
                else:
                    # Fallback: just execute with basic delay
                    time.sleep(5)  # Basic delay
                    return phase_function()
            
            except Exception as e:
                error_str = str(e).lower()
                is_rate_limit_error = any(term in error_str for term in [
                    'rate_limit', 'ratelimit', 'rate limit', 'too many requests',
                    'quota exceeded', 'throttled'
                ])
                
                if is_rate_limit_error and attempt < max_retries:
                    self.execution_stats['rate_limit_hits'] += 1
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    
                    if st:
                        st.warning(
                            f"🔄 Rate limit hit in {phase_name} phase. "
                            f"Retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries + 1})"
                        )
                    
                    time.sleep(wait_time)
                    self.execution_stats['total_wait_time'] += wait_time
                    continue
                else:
                    # Non-rate-limit error or max retries exceeded
                    if st:
                        st.error(f"❌ {phase_name} phase failed: {str(e)}")
                    raise e
        
        raise Exception(f"Max retries exceeded for {phase_name} phase")
    
    def run_enhanced_workflow(self) -> Dict[str, Any]:
        """
        Run the complete DECIDE workflow with enhanced rate limiting
        
        Returns:
            Workflow execution result
        """
        self.execution_stats['start_time'] = datetime.now()
        
        if st:
            st.info(f"🎯 Starting enhanced DECIDE workflow with {self.provider} provider ({self.current_model})")
            
            # Show rate limiting settings
            settings = self.phase_settings
            st.info(
                f"📊 Rate limiting settings: {settings['inter_phase_delay']}s between phases, "
                f"{settings['max_retries']} max retries, {settings['safety_margin']} safety margin"
            )
        
        # Define the sequential phases
        phases = [
            ('collection', self.workflow.run_collection_phase),
            ('analysis', self.workflow.run_multidisciplinary_analysis_phase),
            ('definition', self.workflow.run_define_phase),
            ('exploration', self.workflow.run_explore_phase),
            ('creation', self.workflow.run_create_phase),
            ('implementation', self.workflow.run_implement_phase),
            ('simulation', self.workflow.run_simulate_phase),
            ('evaluation', self.workflow.run_evaluate_phase),
            ('report', self.workflow.run_report_phase)
        ]
        
        all_results = {}
        
        try:
            for i, (phase_name, phase_function) in enumerate(phases):
                # Wait between phases (except for the first one)
                if i > 0:
                    estimated_tokens = self.estimate_phase_tokens(phase_name, phase_function)
                    self.wait_between_phases(phase_name, estimated_tokens)
                
                # Update session state
                if hasattr(st, 'session_state') and hasattr(st.session_state, 'workflow_state'):
                    try:
                        from utils.session_manager import SessionManager
                        SessionManager.update_phase(phase_name, 'in_progress')
                    except ImportError:
                        pass  # SessionManager not available
                
                # Execute phase with rate limiting
                try:
                    phase_result = self.execute_phase_with_rate_limiting(phase_name, phase_function)
                    
                    if not isinstance(phase_result, dict):
                        phase_result = {
                            'success': True,           
                            'phase': phase_name,
                            'output': phase_result
                        }

                    if phase_result.get('success'):
                        all_results[phase_name] = phase_result
                        self.execution_stats['phases_completed'].append(phase_name)
                        
                        # Update session state
                        if hasattr(st, 'session_state') and hasattr(st.session_state, 'workflow_state'):
                            try:
                                from utils.session_manager import SessionManager
                                SessionManager.update_phase(phase_name, 'completed')
                                
                            except ImportError:
                                pass  # SessionManager not available
                    else:
                        error_msg = f"Phase {phase_name} failed: {phase_result.get('error', 'Unknown error')}"
                        self.execution_stats['phases_failed'].append(phase_name)
                        return {
                            'success': False,
                            'error': error_msg,
                            'completed_phases': self.execution_stats['phases_completed'],
                            'failed_phase': phase_name,
                            'execution_stats': self.get_execution_stats()
                        }
                
                except Exception as e:
                    error_msg = f"Exception in {phase_name} phase: {str(e)}"
                    self.execution_stats['phases_failed'].append(phase_name)
                    
                    if hasattr(st, 'session_state') and hasattr(st.session_state, 'workflow_state'):
                        try:
                            from utils.session_manager import SessionManager
                            SessionManager.add_log("ERROR", error_msg)
                        except ImportError:
                            pass  # SessionManager not available
                    
                    return {
                        'success': False,
                        'error': error_msg,
                        'completed_phases': self.execution_stats['phases_completed'],
                        'failed_phase': phase_name,
                        'execution_stats': self.get_execution_stats()
                    }
            
            # Workflow completed successfully
            self.execution_stats['end_time'] = datetime.now()
            
            if hasattr(st, 'session_state') and hasattr(st.session_state, 'workflow_state'):
                try:
                    from utils.session_manager import SessionManager
                    SessionManager.update_phase('completed', 'completed')
                    SessionManager.add_log("INFO", "Complete DECIDE workflow executed successfully")
                except ImportError:
                    pass  # SessionManager not available
            
            if st:
                stats = self.get_execution_stats()
                st.success(
                    f"🎉 Complete DECIDE workflow executed successfully! "
                    f"Duration: {stats['total_duration_minutes']:.1f}m, "
                    f"Rate limit hits: {stats['rate_limit_hits']}"
                )
            
            return {
                'success': True,
                'workflow_id': self.workflow.workflow_id,
                'completed_phases': self.execution_stats['phases_completed'],
                'phase_results': all_results,
                'execution_stats': self.get_execution_stats(),
                'summary': self.workflow.generate_workflow_summary(all_results)
            }
        
        except Exception as e:
            self.execution_stats['end_time'] = datetime.now()
            error_msg = f"Workflow execution failed: {str(e)}"
            
            if hasattr(st, 'session_state') and hasattr(st.session_state, 'workflow_state'):
                try:
                    from utils.session_manager import SessionManager
                    SessionManager.add_log("ERROR", error_msg)
                except ImportError:
                    pass  # SessionManager not available
            
            return {
                'success': False,
                'error': error_msg,
                'workflow_id': self.workflow.workflow_id,
                'completed_phases': self.execution_stats['phases_completed'],
                'execution_stats': self.get_execution_stats()
            }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get comprehensive execution statistics"""
        stats = {**self.execution_stats}
        
        if stats['start_time'] and stats['end_time']:
            duration = stats['end_time'] - stats['start_time']
            stats['total_duration_seconds'] = duration.total_seconds()
            stats['total_duration_minutes'] = duration.total_seconds() / 60
        
        # Add provider-specific stats
        if self.provider == 'anthropic' and self.anthropic_limiter:
            anthropic_stats = self.anthropic_limiter.get_stats()
            stats['provider_stats'] = anthropic_stats
        elif self.provider == 'openai' and self.openai_token_manager:
            openai_stats = self.openai_token_manager.get_processing_summary()
            stats['provider_stats'] = openai_stats
        
        return stats
    def _is_quality_block(self, output_str: str) -> bool:
        out = (output_str or "").lower()
        return ("validator report" in out) or (" block" in out) or ("blocked" in out)


    def reset_stats(self):
        """Reset execution statistics"""
        self.execution_stats = {
            'start_time': None,
            'end_time': None,
            'phases_completed': [],
            'phases_failed': [],
            'total_wait_time': 0,
            'rate_limit_hits': 0,
            'provider': self.provider,
            'model': self.current_model
        }
        
        if self.anthropic_limiter:
            self.anthropic_limiter.reset_stats()
        if self.openai_token_manager:
            self.openai_token_manager.reset_stats()