import hashlib
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional
from config import config

class AuthManager:
    """Handles user authentication and session management"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return AuthManager.hash_password(password) == hashed
    
    @staticmethod
    def login(password: str) -> bool:
        """Authenticate user with password"""
        correct_hash = AuthManager.hash_password(config.DEFAULT_PASSWORD)
        if AuthManager.verify_password(password, correct_hash):
            # First set authentication state
            st.session_state.authenticated = True
            st.session_state.login_time = datetime.now()
            
            # Clear collection data on successful login (without deleting/recreating)
            try:
                from utils.vector_store import VectorStore
                vector_store = VectorStore()
                
                # Use clear_collection to empty the collection without deletion/recreation
                if vector_store.clear_collection():
                    st.success("Vector store cleared successfully")
                    st.session_state['collection_reset'] = True
                else:
                    st.warning("Vector store clearing may be incomplete")
                    # Still return True for login as this is not critical
            except Exception as e:
                st.warning(f"Could not clear vector store during login: {str(e)}")
                # Log the full error for debugging
                import traceback
                print(f"Vector store clear error: {traceback.format_exc()}")
            
            return True
        return False
    
    @staticmethod
    def logout():
        """Clear authentication state and clear session vector collection"""
        from utils.vector_store import VectorStore
        # Use clear instead of delete to preserve collection structure
        VectorStore.clear_session_collection()
        if 'authenticated' in st.session_state:
            del st.session_state.authenticated
        if 'login_time' in st.session_state:
            del st.session_state.login_time
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated and session is valid"""
        if not st.session_state.get('authenticated', False):
            return False
        
        login_time = st.session_state.get('login_time')
        if not login_time:
            return False
        
        # Check session timeout
        if datetime.now() - login_time > timedelta(seconds=config.SESSION_TIMEOUT):
            AuthManager.logout()
            return False
        
        return True
    
    @staticmethod
    def require_auth():
        """Decorator/function to require authentication"""
        if not AuthManager.is_authenticated():
            st.warning("Please log in to access MIMÉTICA")
            
            with st.container():
                st.subheader("🔐 Login to MIMÉTICA")
                password = st.text_input("Password", type="password", key="login_password")
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button("Login", type="primary"):
                        if AuthManager.login(password):
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid password")
                
                st.info("💡 Contact your administrator for access credentials")
            
            st.stop()
