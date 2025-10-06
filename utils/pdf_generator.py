"""
PDF Generator utility for MIMÉTICA reports.

This module provides functionality to convert markdown content to PDF format
using ReportLab for cross-platform PDF generation with support for embedding
charts and visualizations.
"""

import io
import re
import base64
import markdown
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from typing import Optional, Dict, Any, List
import streamlit as st


class PDFGenerator:
    """PDF Generator for MIMÉTICA reports using ReportLab"""
    
    def __init__(self):
        """Initialize PDF Generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _add_page_number_and_logo(self, canvas, doc):
        """Add page numbers and logo to PDF pages"""
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.saveState()
        
        # Add page number on the right
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.black)
        canvas.drawRightString(letter[0] - 72, 36, text)  # Bottom right
        
        # Add logo on the left bottom, aligned with page number
        try:
            logo_path = "assets/logo_red.png"
            # Position logo in bottom left, aligned with page number height
            logo_x = 72  # 72 points from left edge (matching right margin)
            logo_y = 36 - 12  # Aligned with page number baseline (36) minus half logo height
            logo_width = 50  # Logo width in points
            logo_height = 25  # Logo height in points
            
            canvas.drawImage(logo_path, logo_x, logo_y, width=logo_width, height=logo_height, mask='auto')
        except Exception as e:
            # If logo fails to load, just skip it
            pass
        
        canvas.restoreState()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for PDF generation"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=26,
            textColor=colors.black,
            spaceAfter=30,
            spaceBefore=20,
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.black,
            spaceAfter=18,
            spaceBefore=24,
            fontName='Helvetica-Bold'
        ))
        
        # Subheader style
        self.styles.add(ParagraphStyle(
            name='CustomSubheader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=12,
            spaceBefore=18,
            fontName='Helvetica-Bold'
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=12,
            spaceBefore=0,
            alignment=4,  # Justify
            fontName='Helvetica',
            leading=14  # Line spacing
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,  # Changed to black for professional look
            alignment=1  # Center alignment
        ))
    
    def _extract_image_placeholders(self, content: str) -> List[Dict]:
        """Extract image placeholders from content and load corresponding images"""
        from utils.image_manager import image_manager
        
        images = []
        # Pattern to match image placeholders
        placeholder_pattern = r'\[IMAGE_PLACEHOLDER: ([a-f0-9-]+)\].*?\[/IMAGE_PLACEHOLDER\]'
        matches = re.findall(placeholder_pattern, content, re.DOTALL)
        
        for i, image_id in enumerate(matches):
            try:
                # Get image metadata
                image_metadata = image_manager.get_image_by_id(image_id)
                if not image_metadata:
                    continue
                
                # Load image bytes
                image_bytes = image_manager.load_image_for_pdf(image_id)
                if not image_bytes:
                    continue
                
                # Create ReportLab Image object
                image_buffer = io.BytesIO(image_bytes)
                img = Image(image_buffer, width=6*inch, height=4*inch)
                
                images.append({
                    'index': i,
                    'image': img,
                    'image_id': image_id,
                    'metadata': image_metadata
                })
            except Exception as e:
                st.warning(f"Failed to process image {image_id}: {str(e)}")
                
        return images
    
    def _get_current_session_images(self):
        """Get ALL images from the generated_images folder"""
        import os
        import glob
        from pathlib import Path
        
        session_images = []
        generated_images_path = Path("generated_images")
        
        if not generated_images_path.exists():
            return session_images
        
        # Define image type mappings for better titles
        image_type_titles = {
            'monte_carlo_distribution': 'Monte Carlo Simulation Distribution',
            'roi_projection': 'ROI Projection Analysis',
            'timeline': 'Implementation Timeline',
            'risk_assessment': 'Risk Assessment Chart',
            'financial_analysis': 'Financial Analysis',
            'performance_metrics': 'Performance Metrics'
        }
        
        # Get ALL PNG files from ALL session folders
        all_image_files = []
        
        # Get all session folders
        session_folders = [d for d in generated_images_path.iterdir() if d.is_dir() and d.name.startswith('session_')]
        
        for session_folder in session_folders:
            image_files = list(session_folder.glob("*.png"))
            all_image_files.extend(image_files)
        
        # Sort by modification time (newest first) to show latest images first
        all_image_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for img_path in all_image_files:
            # Extract image type from filename for better titles
            filename = img_path.stem
            image_type = None
            
            for key in image_type_titles.keys():
                if key in filename.lower():
                    image_type = key
                    break
            
            # Create a descriptive title
            if image_type:
                title = image_type_titles[image_type]
            else:
                # Fallback: create title from filename
                title = filename.replace('_', ' ').title()
                # Remove timestamp and hash parts
                title = ' '.join(word for word in title.split() if not (word.isdigit() or len(word) == 8 and all(c in '0123456789abcdef' for c in word.lower())))
                if not title.strip():
                    title = "Generated Visualization"
            
            session_images.append({
                'path': str(img_path),
                'title': title,
                'filename': img_path.name
            })
        
        return session_images

    def _clean_content_from_placeholders(self, content: str) -> str:
        """Remove image placeholders from content and replace with simple markers"""
        # Pattern to match image placeholders
        placeholder_pattern = r'\[IMAGE_PLACEHOLDER: ([a-f0-9-]+)\].*?\[/IMAGE_PLACEHOLDER\]'
        
        # Replace with simple image markers
        image_count = 0
        def replace_with_marker(match):
            nonlocal image_count
            image_count += 1
            return f"[IMAGE_{image_count}_MARKER]"
        
        cleaned_content = re.sub(placeholder_pattern, replace_with_marker, content, flags=re.DOTALL)
        return cleaned_content
    
    def _insert_images_in_story(self, story: list, images: List[Dict]) -> list:
        """Insert images into the story at appropriate marker locations"""
        new_story = []
        image_index = 0
        
        for element in story:
            if hasattr(element, 'text'):
                text = element.text
                # Check if this element contains an image marker
                marker_pattern = r'\[IMAGE_(\d+)_MARKER\]'
                if re.search(marker_pattern, text):
                    # Replace marker with actual image
                    if image_index < len(images):
                        # Add text before image if any
                        text_before = re.split(marker_pattern, text)[0]
                        if text_before.strip():
                            new_story.append(Paragraph(text_before, element.style))
                        
                        # Add image with caption
                        image_data = images[image_index]
                        new_story.append(image_data['image'])
                        
                        # Add image caption if metadata available
                        if 'metadata' in image_data and 'title' in image_data['metadata']:
                            caption_text = f"Figure {image_index + 1}: {image_data['metadata']['title']}"
                            new_story.append(Paragraph(caption_text, self.styles['Normal']))
                        
                        new_story.append(Spacer(1, 12))
                        
                        # Add text after image if any
                        parts = re.split(marker_pattern, text)
                        if len(parts) > 2 and parts[2].strip():
                            new_story.append(Paragraph(parts[2], element.style))
                        
                        image_index += 1
                    else:
                        # No more images, just add the text without marker
                        cleaned_text = re.sub(marker_pattern, '', text)
                        if cleaned_text.strip():
                            new_story.append(element)
                else:
                    new_story.append(element)
            else:
                new_story.append(element)
        
        # Add any remaining images at the end
        while image_index < len(images):
            new_story.append(Spacer(1, 12))
            image_data = images[image_index]
            new_story.append(image_data['image'])
            
            # Add caption
            if 'metadata' in image_data and 'title' in image_data['metadata']:
                caption_text = f"Figure {image_index + 1}: {image_data['metadata']['title']}"
                new_story.append(Paragraph(caption_text, self.styles['Normal']))
            
            new_story.append(Spacer(1, 12))
            image_index += 1
        
        return new_story

    def markdown_to_pdf(self, markdown_content: str, title: str = "MIMÉTICA Report") -> bytes:
        """
        Convert markdown content to PDF with embedded images
        
        Args:
            markdown_content: The markdown content to convert
            title: The title for the PDF document
            
        Returns:
            bytes: PDF file content as bytes
        """
        try:
            # Extract image placeholders from content
            images = self._extract_image_placeholders(markdown_content)
            
            # Clean content from placeholders and add markers
            cleaned_content = self._clean_content_from_placeholders(markdown_content)
            
            # Create PDF buffer
            buffer = io.BytesIO()
            
            # Create document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72,
                title=title
            )
            
            # Convert markdown to story elements
            story = self._markdown_to_story(cleaned_content, title)
            
            # Insert images into the story
            if images:
                story = self._insert_images_in_story(story, images)
            
            # Build PDF with page numbers and logo
            doc.build(story, onFirstPage=self._add_page_number_and_logo, onLaterPages=self._add_page_number_and_logo)
            
            # Get PDF bytes
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            st.error(f"Failed to generate PDF: {str(e)}")
            raise
    
    def _markdown_to_story(self, markdown_content: str, title: str) -> list:
        """Convert markdown content to ReportLab story elements"""
        story = []
        
        # Add title page
        story.append(Spacer(1, 30))  # Top margin
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Add subtitle/date with professional styling
        date_style = ParagraphStyle(
            'DateStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.black,
            alignment=1,  # Center
            fontName='Helvetica'
        )
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", date_style))
        story.append(Spacer(1, 40))
        
        # Add a professional divider line
        divider_style = ParagraphStyle(
            'DividerStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.black,
            alignment=1,  # Center
            fontName='Helvetica'
        )
        story.append(Paragraph("━" * 50, divider_style))
        story.append(Spacer(1, 30))
        
        # Parse markdown content directly for tables before HTML conversion
        story.extend(self._parse_markdown_content(markdown_content))
        
        # Add footer with professional spacing
        story.append(Spacer(1, 40))
        
        # Add divider before footer
        divider_style = ParagraphStyle(
            'FooterDividerStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            alignment=1,  # Center
            fontName='Helvetica'
        )
        story.append(Paragraph("━" * 60, divider_style))
        story.append(Spacer(1, 20))
        
        # Professional footer
        story.append(Paragraph("Generated by MIMÉTICA MVP 1.0", self.styles['Footer']))
        story.append(Paragraph("Strategic Decision Support System", self.styles['Footer']))
        story.append(Spacer(1, 10))
        story.append(Paragraph(f"© {datetime.now().year} Tuinkel - All Rights Reserved", self.styles['Footer']))
        
        # Add ALL session visualizations at the very end
        try:
            session_images = self._get_current_session_images()
            if session_images:
                story.append(PageBreak())  # Start visualizations on a new page
                story.append(Paragraph("Generated Visualizations", self.styles['CustomHeader']))
                story.append(Spacer(1, 12))
                
                for idx, img_info in enumerate(session_images, start=1):
                    try:
                        # Add the image
                        img = Image(img_info['path'], width=6*inch, height=4*inch)
                        story.append(img)
                        
                        # Add caption with proper title
                        caption = f"Figure {idx}: {img_info['title']}"
                        story.append(Paragraph(caption, self.styles['Normal']))
                        story.append(Spacer(1, 16))
                        
                        # Add page break after every 2 images for better layout
                        if idx % 2 == 0 and idx < len(session_images):
                            story.append(PageBreak())
                            
                    except Exception as e:
                        # Skip images that can't be loaded
                        print(f"Warning: Could not load image {img_info['path']}: {e}")
                        continue
        except Exception as e:
            # If any issue occurs, continue without session images
            print(f"Warning: Could not add session images: {e}")
            pass
        
        return story
    
    def _process_inline_markdown(self, text: str) -> str:
        """Process inline markdown formatting like bold, italic, etc."""
        if not text:
            return text
            
        # Process bold text (**text** or __text__)
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'__(.*?)__', r'<b>\1</b>', text)
        
        # Process italic text (*text* or _text_)
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        text = re.sub(r'_(.*?)_', r'<i>\1</i>', text)
        
        # Process inline code (`text`)
        text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', text)
        
        # Clean up any remaining markdown artifacts
        text = text.replace('\\n', ' ')
        text = text.replace('\\t', ' ')
        
        return text

    def _parse_markdown_content(self, markdown_content: str) -> list:
        """Parse markdown content directly to handle tables and other elements"""
        story = []
        lines = markdown_content.split('\n')
        current_paragraph = ""
        current_table_lines = []
        in_table = False
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this is a table line (contains | characters and not in code block)
            if '|' in line and line.count('|') >= 2 and not line.startswith('```'):
                # Start or continue table
                if not in_table:
                    # Add any pending paragraph
                    if current_paragraph:
                        story.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                        story.append(Spacer(1, 6))
                        current_paragraph = ""
                    in_table = True
                    current_table_lines = []
                
                current_table_lines.append(line)
                
            elif in_table and line == "":
                # End of table
                table_element = self._create_markdown_table(current_table_lines)
                if table_element:
                    story.append(table_element)
                    story.append(Spacer(1, 12))
                in_table = False
                current_table_lines = []
                
            elif in_table and not ('|' in line and line.count('|') >= 2):
                # End of table - non-table line encountered
                table_element = self._create_markdown_table(current_table_lines)
                if table_element:
                    story.append(table_element)
                    story.append(Spacer(1, 12))
                in_table = False
                current_table_lines = []
                # Process this line as normal content
                story.extend(self._process_markdown_line(line, current_paragraph))
                current_paragraph = ""
                
            else:
                # Normal content processing
                if in_table:
                    # Finish the table first
                    table_element = self._create_markdown_table(current_table_lines)
                    if table_element:
                        story.append(table_element)
                        story.append(Spacer(1, 12))
                    in_table = False
                    current_table_lines = []
                
                # Process line
                line_elements = self._process_markdown_line(line, current_paragraph)
                if line_elements:
                    story.extend(line_elements)
                    current_paragraph = ""
                else:
                    # Add to current paragraph
                    if line:
                        # Process inline markdown formatting
                        processed_line = self._process_inline_markdown(line)
                        if current_paragraph:
                            current_paragraph += " " + processed_line
                        else:
                            current_paragraph = processed_line
            
            i += 1
        
        # Handle any remaining content
        if in_table and current_table_lines:
            table_element = self._create_markdown_table(current_table_lines)
            if table_element:
                story.append(table_element)
                story.append(Spacer(1, 12))
                
        if current_paragraph:
            # Process inline markdown formatting before creating paragraph
            processed_paragraph = self._process_inline_markdown(current_paragraph)
            story.append(Paragraph(processed_paragraph, self.styles['CustomBody']))
        
        return story
    
    def _create_markdown_table(self, table_lines: List[str]) -> Optional[Table]:
        """Create a ReportLab Table from markdown table lines"""
        try:
            if not table_lines:
                return None
            
            table_data = []
            for line in table_lines:
                # Skip separator lines (like |---|---|)
                if re.match(r'^[\|\s\-:]+$', line):
                    continue
                    
                # Split by | and clean up cells
                cells = [cell.strip() for cell in line.split('|')]
                # Remove empty cells at start/end (from leading/trailing |)
                if cells and cells[0] == '':
                    cells = cells[1:]
                if cells and cells[-1] == '':
                    cells = cells[:-1]
                
                if cells:  # Only add non-empty rows
                    table_data.append(cells)
            
            if not table_data:
                return None
            
            # Calculate available width (page width minus margins)
            available_width = letter[0] - 144  # 72pt margins on each side
            
            # Determine number of columns
            num_cols = len(table_data[0]) if table_data else 0
            if num_cols == 0:
                return None
            
            # Calculate column widths based on content length and available space
            col_widths = []
            
            if num_cols == 2:
                # For 2-column tables, use 30% for first column, 70% for second
                col_widths = [available_width * 0.3, available_width * 0.7]
            elif num_cols == 3:
                # For 3-column tables, distribute evenly
                col_widths = [available_width / 3] * 3
            elif num_cols > 3:
                # For tables with more columns, make first column narrower
                first_col_width = available_width * 0.2
                remaining_width = available_width - first_col_width
                other_col_width = remaining_width / (num_cols - 1)
                col_widths = [first_col_width] + [other_col_width] * (num_cols - 1)
            else:
                # Single column
                col_widths = [available_width]
            
            # Convert text to Paragraph objects for better text wrapping
            processed_table_data = []
            for row_idx, row in enumerate(table_data):
                processed_row = []
                for col_idx, cell in enumerate(row):
                    if cell:
                        # Apply inline markdown processing to cell content
                        processed_cell = self._process_inline_markdown(cell)
                        
                        # Use appropriate style for header vs data cells
                        if row_idx == 0:  # Header row
                            cell_style = ParagraphStyle(
                                'TableHeader',
                                parent=self.styles['Normal'],
                                fontSize=10,
                                fontName='Helvetica-Bold',
                                textColor=colors.white,
                                alignment=0,  # Left alignment
                                leading=12
                            )
                        else:  # Data row
                            cell_style = ParagraphStyle(
                                'TableData',
                                parent=self.styles['Normal'],
                                fontSize=9,
                                fontName='Helvetica',
                                textColor=colors.black,
                                alignment=0,  # Left alignment
                                leading=11
                            )
                        
                        # Create paragraph for text wrapping
                        paragraph = Paragraph(processed_cell, cell_style)
                        processed_row.append(paragraph)
                    else:
                        processed_row.append("")
                processed_table_data.append(processed_row)
            
            # Create the table with calculated widths and processed data
            table = Table(processed_table_data, colWidths=col_widths)
            
            # Apply table styling (simplified since we're using Paragraph objects)
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),  # Professional dark header
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Clean white background for data
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Left alignment
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Top vertical alignment for text wrapping
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),  # Subtle grid lines
                ('LEFTPADDING', (0, 0), (-1, -1), 6),  # Cell padding
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),  # Cell padding
                ('TOPPADDING', (0, 0), (-1, -1), 6),  # Cell padding
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),  # Cell padding
            ]
            
            table.setStyle(TableStyle(table_style))
            
            # Set word wrap for all cells
            table.hAlign = 'LEFT'
            
            return table
            
        except Exception as e:
            # If table creation fails, return a simple paragraph
            return Paragraph(f"Table content could not be rendered: {str(e)}", self.styles['CustomBody'])
    
    def _process_markdown_line(self, line: str, current_paragraph: str) -> List:
        """Process a single markdown line and return story elements"""
        elements = []
        
        if not line:
            if current_paragraph:
                elements.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                elements.append(Spacer(1, 6))
            return elements
        
        # Clean up the line by removing raw markdown markers that shouldn't be displayed
        cleaned_line = line.strip()
        
        # Handle headers
        if cleaned_line.startswith('# '):
            if current_paragraph:
                elements.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                elements.append(Spacer(1, 6))
            text = cleaned_line[2:].strip()
            elements.append(Paragraph(text, self.styles['CustomTitle']))
            elements.append(Spacer(1, 12))
            
        elif cleaned_line.startswith('## '):
            if current_paragraph:
                elements.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                elements.append(Spacer(1, 6))
            text = cleaned_line[3:].strip()
            elements.append(Paragraph(text, self.styles['CustomHeader']))
            elements.append(Spacer(1, 8))
            
        elif cleaned_line.startswith('### '):
            if current_paragraph:
                elements.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                elements.append(Spacer(1, 6))
            text = cleaned_line[4:].strip()
            elements.append(Paragraph(text, self.styles['CustomSubheader']))
            elements.append(Spacer(1, 6))
            
        elif cleaned_line.startswith('#### '):
            if current_paragraph:
                elements.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                elements.append(Spacer(1, 6))
            text = cleaned_line[5:].strip()
            # Use custom subheader for h4
            elements.append(Paragraph(f"<b>{text}</b>", self.styles['CustomBody']))
            elements.append(Spacer(1, 4))
            
        # Handle bullet points
        elif cleaned_line.startswith('- ') or cleaned_line.startswith('* '):
            if current_paragraph:
                processed_paragraph = self._process_inline_markdown(current_paragraph)
                elements.append(Paragraph(processed_paragraph, self.styles['CustomBody']))
                elements.append(Spacer(1, 6))
            text = self._process_inline_markdown(cleaned_line[2:].strip())
            # Format as bullet point
            bullet_text = f"• {text}"
            elements.append(Paragraph(bullet_text, self.styles['CustomBody']))
            elements.append(Spacer(1, 2))
            
        # Handle numbered lists
        elif re.match(r'^\d+\.\s+', cleaned_line):
            if current_paragraph:
                processed_paragraph = self._process_inline_markdown(current_paragraph)
                elements.append(Paragraph(processed_paragraph, self.styles['CustomBody']))
                elements.append(Spacer(1, 6))
            text = re.sub(r'^\d+\.\s+', '', cleaned_line)
            text = self._process_inline_markdown(text)
            # Get the number for proper formatting
            number = re.match(r'^(\d+)\.', cleaned_line).group(1)
            numbered_text = f"{number}. {text}"
            elements.append(Paragraph(numbered_text, self.styles['CustomBody']))
            elements.append(Spacer(1, 2))
            
        else:
            # Return empty list to indicate this should be added to current paragraph
            return []
        
        return elements
    
    def _html_to_story_elements(self, html_content: str) -> list:
        """Convert HTML content to ReportLab story elements"""
        story = []
        
        # Simple HTML parsing and conversion
        lines = html_content.split('\n')
        current_paragraph = ""
        current_table = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_paragraph:
                    story.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                    story.append(Spacer(1, 6))
                    current_paragraph = ""
                continue
            
            # Handle headers
            if line.startswith('<h1>') and line.endswith('</h1>'):
                if current_paragraph:
                    story.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                    current_paragraph = ""
                text = re.sub(r'</?h1>', '', line)
                story.append(Paragraph(text, self.styles['CustomTitle']))
                story.append(Spacer(1, 12))
                
            elif line.startswith('<h2>') and line.endswith('</h2>'):
                if current_paragraph:
                    story.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                    current_paragraph = ""
                text = re.sub(r'</?h2>', '', line)
                story.append(Paragraph(text, self.styles['CustomHeader']))
                story.append(Spacer(1, 8))
                
            elif line.startswith('<h3>') and line.endswith('</h3>'):
                if current_paragraph:
                    story.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                    current_paragraph = ""
                text = re.sub(r'</?h3>', '', line)
                story.append(Paragraph(text, self.styles['CustomSubheader']))
                story.append(Spacer(1, 6))
                
            # Handle tables
            elif line.startswith('<table>'):
                if current_paragraph:
                    story.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                    current_paragraph = ""
                in_table = True
                current_table = []
                
            elif line.startswith('</table>'):
                if in_table and current_table:
                    table_element = self._create_table_element(current_table)
                    if table_element:
                        story.append(table_element)
                        story.append(Spacer(1, 12))
                in_table = False
                current_table = []
                
            elif in_table and ('<tr>' in line or '<td>' in line or '<th>' in line):
                current_table.append(line)
                
            # Handle paragraphs and other content
            elif line.startswith('<p>') and line.endswith('</p>'):
                text = re.sub(r'</?p>', '', line)
                text = self._clean_html_tags(text)
                current_paragraph = text
                
            else:
                # Add to current paragraph or create new one
                cleaned_line = self._clean_html_tags(line)
                if cleaned_line:
                    if current_paragraph:
                        current_paragraph += " " + cleaned_line
                    else:
                        current_paragraph = cleaned_line
        
        # Add any remaining paragraph
        if current_paragraph:
            story.append(Paragraph(current_paragraph, self.styles['CustomBody']))
            
        # Add any remaining table
        if in_table and current_table:
            table_element = self._create_table_element(current_table)
            if table_element:
                story.append(table_element)
        
        return story
    
    def _create_table_element(self, table_html_lines: List[str]) -> Optional[Table]:
        """Create a ReportLab Table element from HTML table lines"""
        try:
            table_data = []
            
            for line in table_html_lines:
                if '<tr>' in line:
                    # Extract cells from the row
                    cells = []
                    # Simple extraction of td/th content
                    cell_pattern = r'<t[hd][^>]*>(.*?)</t[hd]>'
                    matches = re.findall(cell_pattern, line, re.DOTALL)
                    
                    for match in matches:
                        # Clean the cell content
                        cell_content = self._clean_html_tags(match).strip()
                        cells.append(cell_content)
                    
                    if cells:
                        table_data.append(cells)
            
            if not table_data:
                return None
            
            # Create the table
            table = Table(table_data)
            
            # Apply table styling
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2C3E50')),  # Professional dark header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # White text on dark header
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Left alignment
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
                ('FONTSIZE', (0, 0), (-1, 0), 11),  # Header font size
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header padding
                ('TOPPADDING', (0, 0), (-1, 0), 12),  # Header padding
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),  # Clean white background for data
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Black text for all data
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Data font
                ('FONTSIZE', (0, 1), (-1, -1), 10),  # Data font size
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#BDC3C7')),  # Subtle grid lines
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
                ('LEFTPADDING', (0, 0), (-1, -1), 8),  # Cell padding
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),  # Cell padding
                ('TOPPADDING', (0, 1), (-1, -1), 8),  # Cell padding for data rows
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),  # Cell padding for data rows
            ]
            
            table.setStyle(TableStyle(table_style))
            
            return table
            
        except Exception as e:
            # If table creation fails, return a simple paragraph
            return Paragraph(f"Table content could not be rendered: {str(e)}", self.styles['CustomBody'])
    
    def _clean_html_tags(self, text: str) -> str:
        """Clean HTML tags from text"""
        # Remove common HTML tags
        text = re.sub(r'</?[^>]+>', '', text)
        # Handle HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        return text.strip()
    
    def generate_comprehensive_report_pdf(self, phase_outputs: Dict[str, Any]) -> bytes:
        """
        Generate comprehensive PDF report from phase outputs
        
        Args:
            phase_outputs: Dictionary containing all phase outputs
            
        Returns:
            bytes: PDF file content as bytes
        """
        try:
            # Extract the main report content if available
            markdown_content = ""
            
            # Check if there's a report phase with proper markdown content
            if 'report' in phase_outputs:
                report_output = phase_outputs['report'].get('output', {})
                
                # Extract the actual markdown content from the nested structure
                if isinstance(report_output, str):
                    markdown_content = report_output
                elif isinstance(report_output, dict):
                    if 'output' in report_output:
                        markdown_content = report_output['output']
                    else:
                        # Convert the entire dict to string and extract markdown
                        report_str = str(report_output)
                        # Find the start of the markdown content
                        start_marker = "# MIMÉTICA Strategic Decision Support System"
                        if start_marker in report_str:
                            start_idx = report_str.find(start_marker)
                            # Find the end (before any closing markers)
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
            
            # If no proper markdown content found, generate from all phases
            if not markdown_content or len(markdown_content.strip()) < 100:
                markdown_content = self._generate_fallback_report(phase_outputs)
            
            # Generate PDF
            return self.markdown_to_pdf(markdown_content, "MIMÉTICA Comprehensive Report")
            
        except Exception as e:
            st.error(f"Failed to generate comprehensive PDF report: {str(e)}")
            raise
    
    def _generate_fallback_report(self, phase_outputs: Dict[str, Any]) -> str:
        """Generate fallback markdown report from phase outputs"""
        report = f"""# MIMÉTICA Strategic Decision Support System
## Comprehensive Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

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
                    report += f"### {key}\n{str(value)}\n\n"
            else:
                report += f"{str(content)}\n\n"
            
            report += "---\n\n"
        
        report += f"""
## Report Footer

*This report was generated by MIMÉTICA MVP 1.0 - Strategic Decision Support System*  
*Powered by CrewAI Multi-Agent Orchestration with Intelligent Token Batch Management*  
*© {datetime.now().year} Tuinkel*
"""
        
        return report
    
    def generate_deliverable_pdf(self, phase: str, output_info: Dict[str, Any]) -> bytes:
        """
        Generate PDF for individual deliverable
        
        Args:
            phase: Phase name
            output_info: Phase output information
            
        Returns:
            bytes: PDF file content as bytes
        """
        try:
            # Create markdown content for the individual deliverable
            markdown_content = f"""# {phase.replace('_', ' ').title()}

**Generated:** {output_info.get('timestamp', 'Unknown')}

"""
            
            # Add batch processing stats if available
            if 'batch_processing_stats' in output_info:
                stats = output_info['batch_processing_stats']
                markdown_content += f"""## Processing Statistics

| Metric | Value |
|--------|-------|
| Documents | {stats.get('total_documents', 0)} |
| Chunks | {stats.get('total_chunks', 0)} |
| Batches | {stats.get('total_batches', 0)} |
| Tokens | {stats.get('total_tokens_processed', 0):,} |
| Success Rate | {stats.get('success_rate', 0):.1f}% |

"""
            
            # Add content
            content = output_info.get('output', {})
            if isinstance(content, dict):
                for key, value in content.items():
                    markdown_content += f"## {key}\n\n{str(value)}\n\n"
            else:
                markdown_content += f"## Content\n\n{str(content)}\n\n"
            
            # Generate PDF
            title = f"MIMÉTICA - {phase.replace('_', ' ').title()}"
            return self.markdown_to_pdf(markdown_content, title)
            
        except Exception as e:
            st.error(f"Failed to generate PDF for {phase}: {str(e)}")
            raise


# Global instance
pdf_generator = PDFGenerator()