"""
Anthropic Rate Limiter - Specialized rate limiting for Anthropic Claude models
Handles the specific rate limits and retry logic for Anthropic API calls
"""

import time
import asyncio
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import streamlit as st
from config import config


class AnthropicRateLimiter:
    """
    Specialized rate limiter for Anthropic Claude API calls
    Handles the 20,000 tokens per minute limit with intelligent backoff and queueing
    """
    
    def __init__(self, 
                 tokens_per_minute: int = 20000,
                 safety_margin: float = 0.8,
                 max_tokens_per_request: int = 15000):
        """
        Initialize Anthropic rate limiter
        
        Args:
            tokens_per_minute: Anthropic TPM limit (default: 20,000)
            safety_margin: Safety factor to avoid hitting limits (0.8 = 80% of limit)
            max_tokens_per_request: Maximum tokens per single request
        """
        self.TPM_LIMIT = tokens_per_minute
        self.SAFETY_MARGIN = safety_margin
        self.EFFECTIVE_TPM = int(tokens_per_minute * safety_margin)
        self.MAX_TOKENS_PER_REQUEST = max_tokens_per_request
        
        # Token usage tracking with sliding window
        self.token_usage_history = []
        self.request_history = []
        self.lock = threading.RLock()
        
        # Rate limiting stats
        self.stats = {
            'total_requests': 0,
            'throttled_requests': 0,
            'total_wait_time': 0,
            'max_wait_time': 0,
            'tokens_processed': 0
        }
        
        # Request queue for managing concurrent requests
        self.request_queue = []
        
    def estimate_tokens_anthropic(self, text: str, include_system_prompt: bool = True) -> int:
        """
        Estimate tokens for Anthropic Claude models
        Claude tokenization is slightly different from OpenAI
        
        Args:
            text: Input text to estimate tokens for
            include_system_prompt: Whether to include system prompt overhead
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        # Basic estimation - Claude tends to use slightly more tokens than GPT-4
        char_count = len(text)
        
        # Anthropic tokenization estimation (slightly higher than OpenAI)
        if char_count < 1000:
            estimated_tokens = char_count / 3.5  # Slightly conservative
        else:
            # For longer texts, use word-based estimation
            import re
            word_count = len(re.findall(r'\b\w+\b', text))
            punct_count = len(re.findall(r'[^\w\s]', text))
            estimated_tokens = word_count * 1.3 + punct_count * 0.6 + char_count * 0.06
        
        # Add system prompt overhead if requested
        if include_system_prompt:
            estimated_tokens += 500  # Typical system prompt overhead
        
        # Add safety buffer for Claude's tokenization
        return max(1, int(estimated_tokens * 1.1))
    
    def get_current_usage(self) -> Dict[str, int]:
        """Get current token usage in the last minute"""
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - 60
            
            # Clean old entries
            self.token_usage_history = [
                (timestamp, tokens) for timestamp, tokens in self.token_usage_history
                if timestamp > cutoff_time
            ]
            
            current_tokens = sum(tokens for _, tokens in self.token_usage_history)
            current_requests = len([
                t for t in self.request_history 
                if t > cutoff_time
            ])
            
            return {
                'tokens_last_minute': current_tokens,
                'requests_last_minute': current_requests,
                'tokens_available': max(0, self.EFFECTIVE_TPM - current_tokens)
            }
    
    def can_make_request(self, estimated_tokens: int) -> bool:
        """Check if a request can be made without exceeding rate limits"""
        usage = self.get_current_usage()
        return (usage['tokens_last_minute'] + estimated_tokens) <= self.EFFECTIVE_TPM
    
    def calculate_wait_time(self, estimated_tokens: int) -> float:
        """Calculate how long to wait before making a request"""
        usage = self.get_current_usage()
        
        if self.can_make_request(estimated_tokens):
            return 0.0
        
        # Calculate time needed for tokens to become available
        excess_tokens = (usage['tokens_last_minute'] + estimated_tokens) - self.EFFECTIVE_TPM
        
        # Conservative estimate: assume tokens are released linearly over time
        wait_time = (excess_tokens / self.EFFECTIVE_TPM) * 60
        
        # Add some buffer and cap at 2 minutes
        return min(wait_time * 1.2, 120)
    
    def wait_for_availability(self, estimated_tokens: int, max_wait: float = 180) -> bool:
        """
        Wait until the request can be made within rate limits
        
        Args:
            estimated_tokens: Tokens needed for the request
            max_wait: Maximum time to wait in seconds
            
        Returns:
            True if request can proceed, False if timeout
        """
        start_time = time.time()
        total_wait = 0
        
        while total_wait < max_wait:
            if self.can_make_request(estimated_tokens):
                return True
            
            wait_time = min(self.calculate_wait_time(estimated_tokens), max_wait - total_wait)
            
            if wait_time <= 0:
                break
            
            if st:
                usage = self.get_current_usage()
                st.info(
                    f"🐌 Anthropic rate limit protection: waiting {wait_time:.1f}s "
                    f"(current: {usage['tokens_last_minute']:,}/{self.EFFECTIVE_TPM:,} TPM, "
                    f"need: {estimated_tokens:,} tokens)"
                )
            
            time.sleep(min(wait_time, 10))  # Sleep in chunks for better UX
            total_wait = time.time() - start_time
            self.stats['total_wait_time'] += min(wait_time, 10)
        
        # Update max wait time stat
        if total_wait > self.stats['max_wait_time']:
            self.stats['max_wait_time'] = total_wait
        
        return total_wait < max_wait
    
    def record_request(self, estimated_tokens: int):
        """Record a request for rate limiting tracking"""
        with self.lock:
            current_time = time.time()
            self.token_usage_history.append((current_time, estimated_tokens))
            self.request_history.append(current_time)
            
            # Update stats
            self.stats['total_requests'] += 1
            self.stats['tokens_processed'] += estimated_tokens
    
    def rate_limited_call(self, func: Callable, estimated_tokens: int, *args, **kwargs):
        """
        Execute a function call with rate limiting
        
        Args:
            func: Function to call
            estimated_tokens: Estimated tokens for the request
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Function result or raises exception
        """
        # Check if request fits within per-request limit
        if estimated_tokens > self.MAX_TOKENS_PER_REQUEST:
            raise ValueError(
                f"Request too large: {estimated_tokens:,} tokens exceeds "
                f"maximum {self.MAX_TOKENS_PER_REQUEST:,} tokens per request"
            )
        
        # Wait for rate limit availability
        if not self.wait_for_availability(estimated_tokens):
            self.stats['throttled_requests'] += 1
            raise Exception(
                f"Rate limit timeout: Could not process {estimated_tokens:,} tokens "
                f"within rate limit constraints"
            )
        
        # Record the request
        self.record_request(estimated_tokens)
        
        # Execute the function with retry logic
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check if it's a rate limit error
                if any(term in error_str for term in ['rate_limit', 'ratelimit', 'rate limit', 'too many requests']):
                    if attempt < max_retries - 1:
                        if st:
                            st.warning(f"⚠️ Rate limit hit, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                        
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        self.stats['throttled_requests'] += 1
                        continue
                    else:
                        self.stats['throttled_requests'] += 1
                        raise e
                else:
                    # Non-rate-limit error, re-raise immediately
                    raise e
        
        # This should never be reached
        raise Exception("Max retries exceeded")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        usage = self.get_current_usage()
        
        return {
            **self.stats,
            'current_usage': usage,
            'effective_tpm_limit': self.EFFECTIVE_TPM,
            'max_tokens_per_request': self.MAX_TOKENS_PER_REQUEST,
            'success_rate': (
                (self.stats['total_requests'] - self.stats['throttled_requests']) / 
                max(1, self.stats['total_requests'])
            ) * 100,
            'average_wait_time': (
                self.stats['total_wait_time'] / 
                max(1, self.stats['throttled_requests'])
            ) if self.stats['throttled_requests'] > 0 else 0
        }
    
    def reset_stats(self):
        """Reset all statistics"""
        with self.lock:
            self.stats = {
                'total_requests': 0,
                'throttled_requests': 0,
                'total_wait_time': 0,
                'max_wait_time': 0,
                'tokens_processed': 0
            }
            # Keep recent history for rate limiting, but clear old entries
            current_time = time.time()
            cutoff_time = current_time - 60
            
            self.token_usage_history = [
                (timestamp, tokens) for timestamp, tokens in self.token_usage_history
                if timestamp > cutoff_time
            ]
            self.request_history = [
                t for t in self.request_history if t > cutoff_time
            ]


def anthropic_rate_limit(estimated_tokens: int = None):
    """
    Decorator for rate limiting Anthropic API calls
    
    Args:
        estimated_tokens: Estimated tokens for the request (if None, will estimate from args)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create rate limiter instance
            if not hasattr(wrapper, '_rate_limiter'):
                wrapper._rate_limiter = AnthropicRateLimiter()
            
            # Estimate tokens if not provided
            tokens = estimated_tokens
            if tokens is None:
                # Try to estimate from function arguments
                tokens = 5000  # Default conservative estimate
                
                # Look for text arguments to estimate from
                for arg in args:
                    if isinstance(arg, str) and len(arg) > 100:
                        tokens = wrapper._rate_limiter.estimate_tokens_anthropic(arg)
                        break
                
                for value in kwargs.values():
                    if isinstance(value, str) and len(value) > 100:
                        tokens = wrapper._rate_limiter.estimate_tokens_anthropic(value)
                        break
            
            # Execute with rate limiting
            return wrapper._rate_limiter.rate_limited_call(func, tokens, *args, **kwargs)
        
        return wrapper
    return decorator


# Global rate limiter instance
_global_anthropic_limiter = None

def get_anthropic_rate_limiter() -> AnthropicRateLimiter:
    """Get or create the global Anthropic rate limiter instance"""
    global _global_anthropic_limiter
    if _global_anthropic_limiter is None:
        _global_anthropic_limiter = AnthropicRateLimiter()
    return _global_anthropic_limiter