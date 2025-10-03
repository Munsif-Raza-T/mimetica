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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
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
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for PDF generation"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.black,  # Changed to black
            spaceAfter=20,
            alignment=1  # Center alignment
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.black,  # Changed to black
            spaceAfter=15,
            spaceBefore=20
        ))
        
        # Subheader style
        self.styles.add(ParagraphStyle(
            name='CustomSubheader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.black,  # Changed to black
            spaceAfter=10,
            spaceBefore=15
        ))
        
        # Body text style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=10,
            alignment=4  # Justify
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
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
            
            # Build PDF
            doc.build(story)
            
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
        story.append(Paragraph(title, self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # If there are no explicit placeholders in content, include session images as Visualizations section
        try:
            placeholder_ids = re.findall(r'\[IMAGE_PLACEHOLDER: ([a-f0-9-]+)\]', markdown_content)
            if not placeholder_ids:
                from utils.image_manager import image_manager
                images = image_manager.get_all_images()
                if images:
                    story.append(Paragraph("Visualizations", self.styles['CustomHeader']))
                    story.append(Spacer(1, 6))
                    for idx, meta in enumerate(images, start=1):
                        try:
                            with open(meta['filepath'], 'rb') as f:
                                img = Image(io.BytesIO(f.read()), width=6*inch, height=4*inch)
                                story.append(img)
                                caption = f"Figure {idx}: {meta.get('title', meta.get('chart_type', 'Visualization'))}"
                                story.append(Paragraph(caption, self.styles['Normal']))
                                story.append(Spacer(1, 12))
                        except Exception:
                            continue
                    story.append(PageBreak())
        except Exception:
            # If any issue occurs, continue without session images
            pass
        
        # Parse markdown content directly for tables before HTML conversion
        story.extend(self._parse_markdown_content(markdown_content))
        
        # Add footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("Generated by MIMÉTICA MVP 1.0 - Strategic Decision Support System", self.styles['Footer']))
        story.append(Paragraph(f"© {datetime.now().year} Tuinkel", self.styles['Footer']))
        
        return story
    
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
                        if current_paragraph:
                            current_paragraph += " " + line
                        else:
                            current_paragraph = line
            
            i += 1
        
        # Handle any remaining content
        if in_table and current_table_lines:
            table_element = self._create_markdown_table(current_table_lines)
            if table_element:
                story.append(table_element)
                story.append(Spacer(1, 12))
                
        if current_paragraph:
            story.append(Paragraph(current_paragraph, self.styles['CustomBody']))
        
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
            
            # Create the table
            table = Table(table_data)
            
            # Apply table styling
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4A90E2')),  # Header background
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Left alignment
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
                ('FONTSIZE', (0, 0), (-1, 0), 10),  # Header font size
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header padding
                ('TOPPADDING', (0, 0), (-1, 0), 8),  # Header padding
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),  # Data background
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Data text color
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Data font
                ('FONTSIZE', (0, 1), (-1, -1), 9),  # Data font size
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DDDDDD')),  # Grid lines
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
                ('LEFTPADDING', (0, 0), (-1, -1), 6),  # Cell padding
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),  # Cell padding
            ]
            
            table.setStyle(TableStyle(table_style))
            
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
        
        # Handle headers
        if line.startswith('# '):
            if current_paragraph:
                elements.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                elements.append(Spacer(1, 6))
            text = line[2:].strip()
            elements.append(Paragraph(text, self.styles['CustomTitle']))
            elements.append(Spacer(1, 12))
            
        elif line.startswith('## '):
            if current_paragraph:
                elements.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                elements.append(Spacer(1, 6))
            text = line[3:].strip()
            elements.append(Paragraph(text, self.styles['CustomHeader']))
            elements.append(Spacer(1, 8))
            
        elif line.startswith('### '):
            if current_paragraph:
                elements.append(Paragraph(current_paragraph, self.styles['CustomBody']))
                elements.append(Spacer(1, 6))
            text = line[4:].strip()
            elements.append(Paragraph(text, self.styles['CustomSubheader']))
            elements.append(Spacer(1, 6))
            
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
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Header background
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text color
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Center alignment
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Header font
                ('FONTSIZE', (0, 0), (-1, 0), 10),  # Header font size
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Header padding
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Data background
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),  # Data text color
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),  # Data font
                ('FONTSIZE', (0, 1), (-1, -1), 9),  # Data font size
                ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grid lines
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertical alignment
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