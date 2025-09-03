"""
Token Batch Manager - Intelligent document chunking and batching for OpenAI API rate limits
Handles document processing, token estimation, and batch creation for optimal API usage
"""

import time
import streamlit as st
from typing import Dict, List, Any, Tuple, Optional, Set
from datetime import datetime
import concurrent.futures
import re
from functools import lru_cache
import threading


class TokenBatchManager:
    """Manages document chunking and batching to respect OpenAI rate limits"""
    
    def __init__(self, 
                 tpm_limit: int = 200000,
                 safety_margin: float = 0.7,
                 max_tokens_per_request: int = 100000,
                 min_chunk_size: int = 100,
                 max_chunk_size: int = 1000):
        """
        Initialize the Token Batch Manager
        
        Args:
            tpm_limit: Tokens per minute limit for the API
            safety_margin: Safety factor (0.0-1.0) to apply to limits
            max_tokens_per_request: Maximum tokens per single API request
            min_chunk_size: Minimum words per chunk
            max_chunk_size: Maximum words per chunk
        """
        self.TPM_LIMIT = tpm_limit
        self.SAFETY_MARGIN = safety_margin
        self.MAX_TOKENS_PER_MIN = int(tpm_limit * safety_margin)
        self.MAX_TOKENS_PER_REQUEST = max_tokens_per_request
        self.MIN_CHUNK_SIZE = min_chunk_size
        self.MAX_CHUNK_SIZE = max_chunk_size
        
        # Token usage tracking
        self.token_usage_history = []
        
        # Batch processing stats
        self.processing_stats = {
            'total_documents': 0,
            'total_chunks': 0,
            'total_batches': 0,
            'successful_batches': 0,
            'failed_batches': 0,
            'total_tokens_processed': 0,
            'start_time': None,
            'end_time': None
        }
    
    @lru_cache(maxsize=10000)
    def estimate_tokens_accurate(self, text: str) -> int:
        """
        More accurate token estimation using multiple methods with caching
        
        Args:
            text: Input text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        if not text or not text.strip():
            return 0
        
        # Quick estimation for very short texts
        if len(text) < 100:
            return max(1, int(len(text) / 3))
        
        # Use regex to count words more efficiently
        word_count = len(re.findall(r'\b\w+\b', text))
        char_count = len(text)
        
        # Optimized token estimation based on GPT-3 tokenizer characteristics
        # Using weighted average of different methods
        estimate1 = word_count * 1.3  # Word-based estimate
        estimate2 = char_count / 4    # Character-based estimate
        estimate3 = len(re.findall(r'[A-Za-z0-9]+|\s+|[^\w\s]', text)) * 0.9  # Token pattern estimate
        
        # Weighted average with more weight on the pattern-based estimate
        estimated_tokens = (estimate1 + estimate2 + 2 * estimate3) / 4
        
        # Add smaller buffer (reduced from 1.1 to 1.05 for better accuracy)
        return max(1, int(estimated_tokens * 1.05))
    
    def chunk_document_smart(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Smart document chunking with token-aware splitting
        
        Args:
            doc: Document dictionary with content and metadata
            
        Returns:
            List of document chunks
        """
        content = doc.get('content', '')
        if not content or not content.strip():
            return [doc]
        
        # Estimate total tokens in document
        total_tokens = self.estimate_tokens_accurate(content)
        
        # If document is small enough, return as-is
        if total_tokens <= self.MAX_TOKENS_PER_REQUEST:
            doc_copy = doc.copy()
            doc_copy['estimated_tokens'] = total_tokens
            doc_copy['chunk_id'] = f"{doc.get('id', 'doc')}_0"
            doc_copy['total_chunks'] = 1
            return [doc_copy]
        
        # Split document into sentences for better context preservation
        sentences = self._split_into_sentences(content)
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_tokens = self.estimate_tokens_accurate(sentence)
            
            # Handle oversized sentences
            if sentence_tokens > self.MAX_TOKENS_PER_REQUEST:
                # Save current chunk if it exists
                if current_chunk:
                    self._save_current_chunk(doc, current_chunk, chunks, current_tokens)
                    current_chunk = []
                    current_tokens = 0
                
                # Split oversized sentence into word chunks
                word_chunks = self._split_sentence_by_words(sentence, self.MAX_TOKENS_PER_REQUEST)
                for word_chunk in word_chunks:
                    chunks.append(self._create_chunk(doc, word_chunk, len(chunks)))
                continue
            
            # Check if adding this sentence would exceed limit
            if current_tokens + sentence_tokens > self.MAX_TOKENS_PER_REQUEST and current_chunk:
                # Save current chunk
                self._save_current_chunk(doc, current_chunk, chunks, current_tokens)
                current_chunk = [sentence]
                current_tokens = sentence_tokens
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # Add remaining content
        if current_chunk:
            self._save_current_chunk(doc, current_chunk, chunks, current_tokens)
        
        # Update total chunks count for all chunks
        for chunk in chunks:
            chunk['total_chunks'] = len(chunks)
        
        return chunks if chunks else [doc]  # Fallback to original document
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex for better performance
        """
        if not text:
            return []
            
        # Efficient regex-based sentence splitting
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])\s*[\n\r]+\s*(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)
        
        # Filter and clean in a single pass
        return [s.strip() for s in sentences if s and len(s.strip()) > 10]
    
    def _split_sentence_by_words(self, sentence: str, max_tokens: int) -> List[str]:
        """Split an oversized sentence into word-based chunks"""
        words = sentence.split()
        word_chunks = []
        current_word_chunk = []
        current_word_tokens = 0
        
        for word in words:
            word_tokens = self.estimate_tokens_accurate(word + " ")
            
            if current_word_tokens + word_tokens > max_tokens and current_word_chunk:
                word_chunks.append(" ".join(current_word_chunk))
                current_word_chunk = [word]
                current_word_tokens = word_tokens
            else:
                current_word_chunk.append(word)
                current_word_tokens += word_tokens
        
        if current_word_chunk:
            word_chunks.append(" ".join(current_word_chunk))
        
        return word_chunks
    
    def _save_current_chunk(self, original_doc: Dict[str, Any], 
                           sentences: List[str], 
                           chunks: List[Dict[str, Any]], 
                           token_count: int):
        """Save current sentence chunk to chunks list"""
        chunk_content = ". ".join(sentences)
        chunk = self._create_chunk(original_doc, chunk_content, len(chunks), token_count)
        chunks.append(chunk)
    
    def _create_chunk(self, original_doc: Dict[str, Any], 
                     content: str, 
                     chunk_index: int, 
                     token_count: Optional[int] = None) -> Dict[str, Any]:
        """Create a chunk dictionary from original document and content"""
        if token_count is None:
            token_count = self.estimate_tokens_accurate(content)
        
        return {
            **original_doc,
            'content': content,
            'chunk_id': f"{original_doc.get('id', 'doc')}_{chunk_index}",
            'chunk_index': chunk_index,
            'total_chunks': 0,  # Will be updated later
            'estimated_tokens': token_count,
            'original_doc_id': original_doc.get('id', 'unknown')
        }
    
    def create_smart_batches(self, docs: List[Dict[str, Any]], 
                           max_tokens_per_batch: Optional[int] = None) -> List[List[Dict[str, Any]]]:
        """
        Create optimally packed batches using an improved bin packing algorithm
        
        Args:
            docs: List of document chunks
            max_tokens_per_batch: Override default batch token limit
            
        Returns:
            List of document batches
        """
        if max_tokens_per_batch is None:
            max_tokens_per_batch = min(self.MAX_TOKENS_PER_MIN // 2, 60000)
        
        # Early return for empty input
        if not docs:
            return []
        
        # Initialize batches with optimal pre-allocation
        estimated_batch_count = sum(doc.get('estimated_tokens', 0) for doc in docs) // max_tokens_per_batch + 1
        batches = [[] for _ in range(estimated_batch_count)]
        batch_tokens = [0] * estimated_batch_count
        
        # Sort docs by token count in descending order for better packing
        sorted_docs = sorted(docs, key=lambda x: x.get('estimated_tokens', 0), reverse=True)
        
        for doc in sorted_docs:
            doc_tokens = doc.get('estimated_tokens', 0)
            
            if doc_tokens > max_tokens_per_batch:
                if st:
                    st.warning(f"⚠️ Skipping oversized chunk: {doc_tokens:,} tokens (ID: {doc.get('chunk_id', 'unknown')})")
                continue
            
            # Find the best batch for this document using best-fit algorithm
            best_batch_idx = -1
            min_remaining_space = max_tokens_per_batch + 1
            
            for i, tokens in enumerate(batch_tokens):
                remaining_space = max_tokens_per_batch - tokens
                if doc_tokens <= remaining_space < min_remaining_space:
                    min_remaining_space = remaining_space
                    best_batch_idx = i
            
            # If no existing batch fits, create a new one
            if best_batch_idx == -1:
                batches.append([doc])
                batch_tokens.append(doc_tokens)
            else:
                batches[best_batch_idx].append(doc)
                batch_tokens[best_batch_idx] += doc_tokens
        
        # Remove empty batches and ensure optimal packing
        return [batch for batch in batches if batch]
    
    def process_documents_with_batching(self, documents: List[Dict[str, Any]]) -> Tuple[List[List[Dict[str, Any]]], Dict[str, Any]]:
        """
        Complete document processing pipeline with parallel processing
        
        Args:
            documents: List of original documents
            
        Returns:
            Tuple of (batches, processing_info)
        """
        self.processing_stats['start_time'] = datetime.now()
        self.processing_stats['total_documents'] = len(documents)
        
        if st:
            st.info(f"📄 Processing {len(documents)} documents for batching...")
        
        # Parallel document chunking
        chunked_docs = []
        chunk_lock = threading.Lock()
        
        def process_doc(doc_tuple):
            i, doc = doc_tuple
            if st:
                st.info(f"📋 Chunking document {i+1}/{len(documents)}: {doc.get('filename', 'Unknown')}")
            
            doc_chunks = self.chunk_document_smart(doc)
            with chunk_lock:
                chunked_docs.extend(doc_chunks)
        
        # Use ThreadPoolExecutor for parallel processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(32, len(documents))) as executor:
            # Process documents in parallel
            list(executor.map(process_doc, enumerate(documents)))
        
        self.processing_stats['total_chunks'] = len(chunked_docs)
        
        if st:
            st.success(f"✅ Created {len(chunked_docs)} document chunks from {len(documents)} documents")
        
        # Create smart batches
        batches = self.create_smart_batches(chunked_docs)
        self.processing_stats['total_batches'] = len(batches)
        
        # Calculate processing info
        processing_info = {
            'original_documents': len(documents),
            'total_chunks': len(chunked_docs),
            'total_batches': len(batches),
            'estimated_total_tokens': sum(doc.get('estimated_tokens', 0) for doc in chunked_docs),
            'average_tokens_per_batch': sum(
                sum(doc.get('estimated_tokens', 0) for doc in batch) 
                for batch in batches
            ) / len(batches) if batches else 0,
            'batch_token_distribution': [
                sum(doc.get('estimated_tokens', 0) for doc in batch) 
                for batch in batches
            ]
        }
        
        if st:
            st.info(f"🎯 Created {len(batches)} processing batches")
            st.info(f"📊 Estimated total tokens: {processing_info['estimated_total_tokens']:,}")
            st.info(f"📈 Average tokens per batch: {processing_info['average_tokens_per_batch']:,.0f}")
        
        return batches, processing_info
    
    def add_token_usage(self, tokens_used: int):
        """Track token usage with sliding window"""
        current_time = time.time()
        self.token_usage_history.append((current_time, tokens_used))
        
        # Keep only last 60 seconds of history
        cutoff_time = current_time - 60
        self.token_usage_history = [
            (t, tokens) for t, tokens in self.token_usage_history 
            if t > cutoff_time
        ]
        
        self.processing_stats['total_tokens_processed'] += tokens_used
    
    def get_current_token_usage(self) -> int:
        """Get current token usage in the last minute"""
        current_time = time.time()
        cutoff_time = current_time - 60
        return sum(
            tokens for t, tokens in self.token_usage_history 
            if t > cutoff_time
        )
    
    def wait_for_rate_limit_window(self, required_tokens: int) -> bool:
        """
        Smart waiting for rate limit window
        
        Args:
            required_tokens: Tokens needed for next request
            
        Returns:
            True if safe to proceed, False if timeout reached
        """
        max_wait_time = 60  # Maximum wait time in seconds
        wait_time = 0
        
        while (self.get_current_token_usage() + required_tokens > self.MAX_TOKENS_PER_MIN 
               and wait_time < max_wait_time):
            
            sleep_duration = min(5, max_wait_time - wait_time)
            current_usage = self.get_current_token_usage()
            
            if st:
                st.info(f"⏳ Rate limit protection: waiting {sleep_duration}s "
                       f"(usage: {current_usage:,}/{self.MAX_TOKENS_PER_MIN:,} TPM)")
            
            time.sleep(sleep_duration)
            wait_time += sleep_duration
        
        if wait_time >= max_wait_time:
            if st:
                st.warning("⚠️ Rate limit wait timeout - proceeding with reduced batch size")
            return False
        
        return True
    
    def update_batch_stats(self, success: bool):
        """Update batch processing statistics"""
        if success:
            self.processing_stats['successful_batches'] += 1
        else:
            self.processing_stats['failed_batches'] += 1
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get comprehensive processing summary"""
        self.processing_stats['end_time'] = datetime.now()
        
        if self.processing_stats['start_time']:
            duration = self.processing_stats['end_time'] - self.processing_stats['start_time']
            self.processing_stats['total_duration_seconds'] = duration.total_seconds()
        
        success_rate = 0
        if self.processing_stats['total_batches'] > 0:
            success_rate = (self.processing_stats['successful_batches'] / 
                          self.processing_stats['total_batches']) * 100
        
        return {
            **self.processing_stats,
            'success_rate': success_rate,
            'average_tokens_per_minute': (
                self.processing_stats['total_tokens_processed'] / 
                max(1, self.processing_stats.get('total_duration_seconds', 1) / 60)
            )
        }
    
    def reset_stats(self):
        """Reset processing statistics"""
        self.processing_stats = {
            'total_documents': 0,
            'total_chunks': 0,
            'total_batches': 0,
            'successful_batches': 0,
            'failed_batches': 0,
            'total_tokens_processed': 0,
            'start_time': None,
            'end_time': None
        }
        self.token_usage_history.clear()