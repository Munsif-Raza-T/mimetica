import os
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
import openai
from openai import OpenAI
import streamlit as st
from config import config
import uuid
import hashlib

class VectorStore:
    """Manages document vectorization and similarity search using Pinecone (session-based)"""

    def __init__(self):
        self.index = None
        self.openai_client = None
        # Use a session-unique index name
        if 'vector_index_name' not in st.session_state:
            # Generate a unique, valid Pinecone index name for this session
            session_id = st.session_state.get('workflow_id') or str(uuid.uuid4())
            # Sanitize: lowercase, replace invalid chars with hyphen
            index_name = "mimetica"
            st.session_state['vector_index_name'] = index_name
        self.index_name = st.session_state['vector_index_name']
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Pinecone and OpenAI clients (new SDK)"""
        try:
            pinecone_api_key = os.getenv("PINECONE_API_KEY", "")
            pinecone_env = os.getenv("PINECONE_ENVIRONMENT", "")
            if not pinecone_api_key or not pinecone_env:
                raise Exception("PINECONE_API_KEY and PINECONE_ENVIRONMENT must be set in environment variables.")
            
            # Initialize Pinecone
            pc = Pinecone(api_key=pinecone_api_key)
            
            # Ensure index exists
            retries = 3
            while retries > 0:
                try:
                    if self.index_name not in pc.list_indexes().names():
                        # Create index if it doesn't exist
                        pc.create_index(
                            name=self.index_name,
                            dimension=config.VECTOR_SIZE,
                            metric="cosine",
                            spec=ServerlessSpec(cloud="aws", region=pinecone_env)
                        )
                        # Wait for index to be ready
                        import time
                        time.sleep(5)
                    
                    # Try to connect to the index
                    self.index = pc.Index(self.index_name)
                    # Test the connection
                    self.index.describe_index_stats()
                    break
                except Exception as e:
                    retries -= 1
                    if retries == 0:
                        raise e
                    time.sleep(2)
            
            # Initialize OpenAI client
            self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
            
            # Verify OpenAI connection
            self.openai_client.models.list()
            
        except Exception as e:
            st.error(f"Failed to initialize vector store: {str(e)}")
            self.index = None
            self.openai_client = None
            raise e

    
    # Pinecone index creation is handled in _initialize_clients
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            if not self.openai_client:
                raise Exception("OpenAI client not initialized")
            
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        
        except Exception as e:
            st.error(f"Failed to generate embedding: {str(e)}")
            return []
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def vectorize_document(self, document: Dict[str, Any]) -> bool:
        """Vectorize a document and store in Pinecone"""
        try:
            if not self.index or not self.openai_client:
                st.error("Vector store not properly initialized")
                return False
            content = document.get('content', '')
            if not content:
                st.warning(f"No content to vectorize for {document.get('filename', 'unknown')}")
                return False
            chunks = self.chunk_text(content)
            if not chunks:
                st.warning(f"No chunks created for {document.get('filename', 'unknown')}")
                return False
            vectors = []
            metadata = []
            ids = []
            for i, chunk in enumerate(chunks):
                embedding = self.generate_embedding(chunk)
                if not embedding:
                    continue
                chunk_id = str(uuid.uuid4())
                ids.append(chunk_id)
                vectors.append(embedding)
                metadata.append({
                    'document_id': document.get('file_hash', ''),
                    'filename': document.get('filename', ''),
                    'file_type': document.get('file_type', ''),
                    'chunk_index': i,
                    'chunk_text': chunk,
                    'processed_at': document.get('processed_at', ''),
                    'word_count': len(chunk.split())
                })
            if vectors:
                # Pinecone upsert
                to_upsert = list(zip(ids, vectors, metadata))
                self.index.upsert(vectors=to_upsert)
                st.success(f"Vectorized {document.get('filename', 'unknown')}: {len(vectors)} chunks")
                return True
            else:
                st.warning(f"No valid chunks to upload for {document.get('filename', 'unknown')}")
                return False
        except Exception as e:
            st.error(f"Failed to vectorize document {document.get('filename', 'unknown')}: {str(e)}")
            return False
    
    def search_similar(self, query: str, limit: int = 10, score_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Search for similar documents/chunks using Pinecone"""
        try:
            if not self.index or not self.openai_client:
                return []
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                return []
            # Pinecone query
            search_results = self.index.query(
                vector=query_embedding,
                top_k=limit,
                include_metadata=True
            )
            results = []
            for match in search_results.matches:
                meta = match.metadata or {}
                results.append({
                    'chunk_text': meta.get('chunk_text', ''),
                    'filename': meta.get('filename', ''),
                    'file_type': meta.get('file_type', ''),
                    'score': match.score,
                    'chunk_index': meta.get('chunk_index', 0)
                })
            return results
        except Exception as e:
            st.error(f"Search failed: {str(e)}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the Pinecone index"""
        try:
            if not self.index:
                return {}
            stats = self.index.describe_index_stats()
            return {
                'name': self.index_name,
                'vector_count': stats.get('total_vector_count', 0),
                'vector_size': config.VECTOR_SIZE,
                'distance_metric': 'cosine'
            }
        except Exception as e:
            st.warning(f"Could not get index info: {str(e)}")
            return {}
    
    def collection_exists(self, name: str) -> bool:
        """Check if a collection exists"""
        try:
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY", ""))
            return name in pc.list_indexes().names()
        except Exception as e:
            st.error(f"Failed to check collection existence: {str(e)}")
            return False

    def delete_collection(self, name: str) -> bool:
        """Delete a collection"""
        try:
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY", ""))
            if name in pc.list_indexes().names():
                pc.delete_index(name)
                return True
            return False
        except Exception as e:
            st.error(f"Failed to delete collection: {str(e)}")
            return False

    def create_collection(self, name: str) -> bool:
        """Create a new collection"""
        try:
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY", ""))
            if name not in pc.list_indexes().names():
                pc.create_index(
                    name=name,
                    dimension=config.VECTOR_SIZE,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region=os.getenv("PINECONE_ENVIRONMENT", ""))
                )
                # Wait for a moment to ensure index is ready
                import time
                time.sleep(5)
                return True
            return False
        except Exception as e:
            st.error(f"Failed to create collection: {str(e)}")
            return False

    def clear_collection(self) -> bool:
        """Clear all vectors from the current index"""
        try:
            if not self.index:
                return False
            self.index.delete(delete_all=True)
            return True
        except Exception as e:
            st.error(f"Failed to clear index: {str(e)}")
            return False

    def reset_collection(self, name: str) -> bool:
        """Reset a collection by deleting and recreating it"""
        try:
            # Delete if exists
            if self.collection_exists(name):
                if not self.delete_collection(name):
                    st.error("Failed to delete existing collection")
                    return False
                
                # Small delay to ensure deletion is complete
                import time
                time.sleep(2)
            
            # Create new collection
            if self.create_collection(name):
                # Reinitialize clients to connect to new collection
                self._initialize_clients()
                return True
            
            return False
        except Exception as e:
            st.error(f"Failed to reset collection: {str(e)}")
            return False
