"""
Image Manager utility for MIMÉTICA system.

This module manages image generation, storage, and retrieval for reports,
keeping images separate from LLM processing to improve efficiency.
"""

import os
import io
import uuid
import base64
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import matplotlib.pyplot as plt


class ImageManager:
    """Manages image storage and retrieval for the MIMÉTICA system"""
    
    def __init__(self, base_images_dir: str = "generated_images"):
        """
        Initialize the Image Manager
        
        Args:
            base_images_dir: Base directory for storing generated images
        """
        self.base_images_dir = Path(base_images_dir)
        self.current_session_dir = None
        self.image_registry = {}  # Stores image metadata
        
    def setup_session_directory(self, session_id: Optional[str] = None) -> str:
        """
        Setup a directory for the current session
        
        Args:
            session_id: Optional session ID, if None will generate one
            
        Returns:
            str: Session directory path
        """
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.current_session_dir = self.base_images_dir / session_id
        self.current_session_dir.mkdir(parents=True, exist_ok=True)
        
        return str(self.current_session_dir)
    
    def save_chart_image(self, 
                        fig, 
                        chart_type: str, 
                        title: str,
                        data_hash: Optional[str] = None) -> Dict[str, str]:
        """
        Save a matplotlib figure to disk and return metadata
        
        Args:
            fig: Matplotlib figure object
            chart_type: Type of chart (risk_matrix, roi_projection, etc.)
            title: Chart title
            data_hash: Optional hash of the data used to generate the chart
            
        Returns:
            Dict containing image metadata
        """
        if self.current_session_dir is None:
            self.setup_session_directory()
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{chart_type}_{timestamp}_{unique_id}.png"
        filepath = self.current_session_dir / filename
        
        try:
            # Save the figure
            fig.savefig(
                filepath, 
                format='png', 
                bbox_inches='tight', 
                dpi=300, 
                facecolor='white',
                edgecolor='none'
            )
            
            # Create metadata
            image_metadata = {
                'id': unique_id,
                'filename': filename,
                'filepath': str(filepath),
                'chart_type': chart_type,
                'title': title,
                'timestamp': timestamp,
                'data_hash': data_hash,
                'size_bytes': filepath.stat().st_size if filepath.exists() else 0
            }
            
            # Store in registry
            self.image_registry[unique_id] = image_metadata
            
            # Close figure to free memory
            plt.close(fig)
            
            return image_metadata
            
        except Exception as e:
            plt.close(fig)
            raise Exception(f"Error saving chart image: {str(e)}")
    
    def generate_text_placeholder(self, image_metadata: Dict[str, str]) -> str:
        """
        Generate a text placeholder for use in LLM reports
        
        Args:
            image_metadata: Image metadata from save_chart_image
            
        Returns:
            str: Text placeholder for the image
        """
        return f"""
[IMAGE_PLACEHOLDER: {image_metadata['id']}]
Chart Type: {image_metadata['chart_type']}
Title: {image_metadata['title']}
Generated: {image_metadata['timestamp']}
[/IMAGE_PLACEHOLDER]
"""
    
    def get_image_by_id(self, image_id: str) -> Optional[Dict[str, str]]:
        """
        Get image metadata by ID
        
        Args:
            image_id: Image unique ID
            
        Returns:
            Dict containing image metadata or None if not found
        """
        return self.image_registry.get(image_id)
    
    def get_all_images(self) -> List[Dict[str, str]]:
        """
        Get all images in the current session
        
        Returns:
            List of image metadata dictionaries
        """
        return list(self.image_registry.values())
    
    def load_image_for_pdf(self, image_id: str) -> Optional[bytes]:
        """
        Load image bytes for PDF inclusion
        
        Args:
            image_id: Image unique ID
            
        Returns:
            bytes: Image data or None if not found
        """
        metadata = self.get_image_by_id(image_id)
        if not metadata:
            return None
        
        filepath = Path(metadata['filepath'])
        if not filepath.exists():
            return None
        
        try:
            with open(filepath, 'rb') as f:
                return f.read()
        except Exception:
            return None
    
    def get_session_summary(self) -> Dict[str, any]:
        """
        Get summary of current session images
        
        Returns:
            Dict containing session summary
        """
        images = self.get_all_images()
        total_size = sum(img.get('size_bytes', 0) for img in images)
        
        chart_types = {}
        for img in images:
            chart_type = img.get('chart_type', 'unknown')
            chart_types[chart_type] = chart_types.get(chart_type, 0) + 1
        
        return {
            'session_dir': str(self.current_session_dir) if self.current_session_dir else None,
            'total_images': len(images),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'chart_types': chart_types,
            'images': images
        }
    
    def extract_image_placeholders(self, text: str) -> List[str]:
        """
        Extract image placeholder IDs from text
        
        Args:
            text: Text containing image placeholders
            
        Returns:
            List of image IDs found in the text
        """
        import re
        pattern = r'\[IMAGE_PLACEHOLDER: ([a-f0-9-]+)\]'
        matches = re.findall(pattern, text)
        return matches
    
    def cleanup_session(self, session_id: Optional[str] = None):
        """
        Clean up images from a session
        
        Args:
            session_id: Session ID to clean up, if None cleans current session
        """
        if session_id:
            session_dir = self.base_images_dir / session_id
        else:
            session_dir = self.current_session_dir
        
        if session_dir and session_dir.exists():
            import shutil
            shutil.rmtree(session_dir)
            
            # Clear registry if cleaning current session
            if session_dir == self.current_session_dir:
                self.image_registry.clear()
                self.current_session_dir = None
    
    def create_data_hash(self, data: any) -> str:
        """
        Create a hash of the data for caching purposes
        
        Args:
            data: Data to hash
            
        Returns:
            str: SHA256 hash of the data
        """
        import json
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]


# Global instance
image_manager = ImageManager()