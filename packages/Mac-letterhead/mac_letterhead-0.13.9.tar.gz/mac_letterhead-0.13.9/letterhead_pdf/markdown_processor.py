#!/usr/bin/env python3

import os
import logging
import tempfile
import urllib.request
import importlib.util
import sys
from typing import Optional, Dict, Tuple, List
import fitz  # PyMuPDF
import re

# Check if markdown is available
try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError as e:
    MARKDOWN_AVAILABLE = False
    logging.warning(f"Markdown module not available: {e}. Install with: uvx mac-letterhead@0.8.2")

# Check if pycmarkgfm is available for GitHub Flavored Markdown
PYCMARKGFM_AVAILABLE = False
try:
    import pycmarkgfm
    PYCMARKGFM_AVAILABLE = True
    logging.info("pycmarkgfm available for GitHub Flavored Markdown support")
except ImportError:
    PYCMARKGFM_AVAILABLE = False
    logging.info("pycmarkgfm not available, using standard markdown")

# Check if WeasyPrint is available and functional
WEASYPRINT_AVAILABLE = False
if importlib.util.find_spec("weasyprint") is not None:
    try:
        # Set library path for WeasyPrint before importing (needed for uvx isolation)
        dyld_fallback_path = os.environ.get('DYLD_FALLBACK_LIBRARY_PATH', '')
        homebrew_lib = '/opt/homebrew/lib'
        if homebrew_lib not in dyld_fallback_path:
            if dyld_fallback_path:
                os.environ['DYLD_FALLBACK_LIBRARY_PATH'] = f"{homebrew_lib}:{dyld_fallback_path}"
            else:
                os.environ['DYLD_FALLBACK_LIBRARY_PATH'] = homebrew_lib
        
        # Try to import and test WeasyPrint functionality
        from weasyprint import HTML
        # Create a simple test to verify WeasyPrint can actually work
        test_html = HTML(string="<html><body>Test</body></html>")
        # If this doesn't raise an exception, WeasyPrint is functional
        WEASYPRINT_AVAILABLE = True
        logging.info("WeasyPrint is available and functional")
    except Exception as e:
        WEASYPRINT_AVAILABLE = False
        logging.warning(f"WeasyPrint installed but not functional: {e}. Using ReportLab fallback.")

# Check if Pygments is available for syntax highlighting
PYGMENTS_AVAILABLE = importlib.util.find_spec("pygments") is not None
if PYGMENTS_AVAILABLE:
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_by_name, guess_lexer
        from pygments.formatters import HtmlFormatter
        logging.info("Pygments available for syntax highlighting")
    except ImportError:
        PYGMENTS_AVAILABLE = False
        logging.warning("Pygments import failed. Code blocks will not have syntax highlighting.")

# Import ReportLab for fallback rendering
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether, ListFlowable, ListItem, Preformatted
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# WeasyPrint will be imported later when needed to avoid import errors

# Define point unit (1/72 inch)
pt = 1

class MarkdownProcessor:
    """Handles conversion of Markdown files to PDF with proper formatting"""
    
    def __init__(self, use_gfm=None):
        """Initialize the Markdown processor with default settings
        
        Args:
            use_gfm: Boolean to force GFM mode (True/False) or None for auto-detection
        """
        # Determine which markdown backend to use
        if use_gfm is None:
            # Auto-detect: prefer GFM if available, fallback to standard markdown
            self.use_gfm = PYCMARKGFM_AVAILABLE
        else:
            # Explicit choice
            self.use_gfm = use_gfm and PYCMARKGFM_AVAILABLE
        
        # Initialize the appropriate markdown backend
        if self.use_gfm:
            logging.info("Using GitHub Flavored Markdown (pycmarkgfm) backend")
            # pycmarkgfm doesn't need explicit initialization like python-markdown
            self.md = None  # We'll use pycmarkgfm.gfm_to_html() directly
        else:
            # Check if standard markdown is available
            if not MARKDOWN_AVAILABLE:
                from letterhead_pdf.exceptions import MarkdownProcessingError
                raise MarkdownProcessingError("No markdown module available. Install with: uvx mac-letterhead[markdown]@0.8.0")
            
            logging.info("Using standard markdown backend")
            # Initialize Markdown with extensions
            extensions = [
                'tables',
                'fenced_code',
                'footnotes',
                'attr_list',
                'def_list',
                'abbr',
                'sane_lists'
            ]
            
            # Add codehilite extension if Pygments is available
            if PYGMENTS_AVAILABLE:
                extensions.append('codehilite')
                
            self.md = markdown.Markdown(extensions=extensions)
        
        # Initialize styles
        self.styles = getSampleStyleSheet()
        self.setup_styles()
        
        # Temp directory for downloaded images
        self.temp_dir = None
    
    def md_to_html(self, md_content: str) -> str:
        """Convert markdown content to HTML using the appropriate backend
        
        Args:
            md_content: Raw markdown content string
            
        Returns:
            HTML content string
        """
        if self.use_gfm:
            # Use GitHub Flavored Markdown
            logging.debug("Using pycmarkgfm.gfm_to_html for markdown conversion")
            html = pycmarkgfm.gfm_to_html(md_content)
            logging.debug("GFM HTML preview: %s", html[:200])
            return html
        else:
            # Use standard markdown
            logging.debug("Using standard markdown.convert for markdown conversion")
            return self.md.convert(md_content)
    
    def setup_styles(self):
        """Set up custom styles for PDF generation"""
        # Modify existing styles
        self.styles['Normal'].fontSize = 9
        self.styles['Normal'].leading = 11
        self.styles['Normal'].spaceBefore = 4
        self.styles['Normal'].spaceAfter = 4
        
        # Improve code style
        self.styles['Code'].fontName = 'Courier'
        self.styles['Code'].fontSize = 8
        self.styles['Code'].leading = 10
        self.styles['Code'].backColor = colors.lightgrey
        self.styles['Code'].borderWidth = 1
        self.styles['Code'].borderColor = colors.grey
        self.styles['Code'].borderPadding = 6
        self.styles['Code'].spaceBefore = 6
        self.styles['Code'].spaceAfter = 6
        
        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='CustomHeading1',
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            alignment=TA_LEFT,
            spaceBefore=10,
            spaceAfter=5,
            keepWithNext=True
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            fontName='Helvetica-Bold',
            fontSize=12,
            leading=16,
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=4,
            keepWithNext=True
        ))
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            spaceBefore=6,
            spaceAfter=3,
            keepWithNext=True
        ))
        self.styles.add(ParagraphStyle(
            name='BulletItem',
            parent=self.styles['Normal'],
            leftIndent=20,
            firstLineIndent=0
        ))
        self.styles.add(ParagraphStyle(
            name='NumberItem',
            parent=self.styles['Normal'],
            leftIndent=20,
            firstLineIndent=0
        ))
        self.styles.add(ParagraphStyle(
            name='Blockquote',
            parent=self.styles['Normal'],
            leftIndent=30,
            rightIndent=30,
            spaceBefore=12,
            spaceAfter=12,
            fontStyle='italic'
        ))

    def analyze_page_regions(self, page):
        """Analyze a page to detect all content regions and page size"""
        page_rect = page.rect
        
        # Determine page size
        width = page_rect.width
        height = page_rect.height
        
        # Determine closest standard size
        if abs(width - 595) <= 1 and abs(height - 842) <= 1:
            page_size = A4
        elif abs(width - 612) <= 1 and abs(height - 792) <= 1:
            page_size = LETTER
        else:
            page_size = A4
            logging.info(f"Non-standard page size detected ({width}x{height}), defaulting to A4")
        
        # Split page into quarters vertically for classification
        top_quarter = page_rect.height / 4
        bottom_quarter = page_rect.height * 3 / 4
        
        # Track all content regions separately
        content_regions = []
        
        # Analyze text blocks
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:  # Text block
                block_rect = fitz.Rect(block["bbox"])
                block_center_y = (block_rect.y0 + block_rect.y1) / 2
                
                # Classify by vertical position
                if block_center_y < top_quarter:
                    region_type = "header"
                elif block_center_y > bottom_quarter:
                    region_type = "footer"
                else:
                    region_type = "middle"
                
                content_regions.append((region_type, block_rect))
                logging.info(f"Text {region_type}: {block_rect}")
        
        # Analyze drawings/graphics
        drawings = page.get_drawings()
        for drawing in drawings:
            drawing_rect = fitz.Rect(drawing["rect"])
            drawing_center_y = (drawing_rect.y0 + drawing_rect.y1) / 2
            
            # Skip very small drawings (likely artifacts)
            if drawing_rect.width < 5 or drawing_rect.height < 5:
                continue
            
            # Skip very large drawings that cover most of the page (likely backgrounds)
            page_area = page_rect.width * page_rect.height
            drawing_area = drawing_rect.width * drawing_rect.height
            area_percentage = (drawing_area / page_area) * 100
            
            if area_percentage > 80:  # Skip drawings covering more than 80% of page
                logging.info(f"Skipping large background drawing: {drawing_rect} ({area_percentage:.1f}% of page)")
                continue
            
            # Skip drawings that span nearly the full width or height (likely borders/backgrounds)
            width_percentage = (drawing_rect.width / page_rect.width) * 100
            height_percentage = (drawing_rect.height / page_rect.height) * 100
            
            if width_percentage > 90 and height_percentage > 90:
                logging.info(f"Skipping full-page drawing: {drawing_rect}")
                continue
            
            # Classify by vertical position
            if drawing_center_y < top_quarter:
                region_type = "header"
            elif drawing_center_y > bottom_quarter:
                region_type = "footer"
            else:
                region_type = "middle"
            
            content_regions.append((region_type, drawing_rect))
            logging.info(f"Drawing {region_type}: {drawing_rect}")
        
        # Analyze images
        images = page.get_images()
        for img_index, img in enumerate(images):
            # Get image placement info
            image_list = page.get_image_rects(img[0])
            for image_rect in image_list:
                image_center_y = (image_rect.y0 + image_rect.y1) / 2
                
                # Classify by vertical position
                if image_center_y < top_quarter:
                    region_type = "header"
                elif image_center_y > bottom_quarter:
                    region_type = "footer"
                else:
                    region_type = "middle"
                
                content_regions.append((region_type, image_rect))
                logging.info(f"Image {region_type}: {image_rect}")
        
        # For backward compatibility, also provide combined regions
        header_rect = None
        footer_rect = None
        middle_rect = None
        
        for region_type, rect in content_regions:
            if region_type == "header":
                header_rect = header_rect.include_rect(rect) if header_rect else rect
            elif region_type == "footer":
                footer_rect = footer_rect.include_rect(rect) if footer_rect else rect
            elif region_type == "middle":
                middle_rect = middle_rect.include_rect(rect) if middle_rect else rect
        
        return {
            'header': header_rect,
            'footer': footer_rect,
            'middle': middle_rect,
            'content_regions': content_regions,  # All individual content regions
            'page_rect': page_rect,
            'page_size': page_size,
            'width': width,
            'height': height
        }

    def analyze_letterhead(self, letterhead_path: str) -> Dict[str, Dict[str, float]]:
        """Analyze letterhead PDF to determine safe printable areas"""
        logging.info(f"Analyzing letterhead margins: {letterhead_path}")
        
        try:
            doc = fitz.open(letterhead_path)
            margins = {
                'first_page': {'top': 0, 'right': 0, 'bottom': 0, 'left': 0},
                'other_pages': {'top': 0, 'right': 0, 'bottom': 0, 'left': 0}
            }
            
            if doc.page_count > 0:
                regions = self.analyze_page_regions(doc[0])
                page_rect = regions['page_rect']
                
                margins['first_page'] = self._calculate_smart_margins(regions, page_rect)
                
                if doc.page_count > 1:
                    regions = self.analyze_page_regions(doc[1])
                    margins['other_pages'] = self._calculate_smart_margins(regions, page_rect)
                else:
                    margins['other_pages'] = margins['first_page'].copy()
            
            # Add minimal padding for top and bottom
            for page_type in margins:
                margins[page_type]['top'] += 20
                margins[page_type]['bottom'] += 20
            
            logging.info(f"Detected margins for first page: {margins['first_page']}")
            logging.info(f"Detected margins for other pages: {margins['other_pages']}")
            
            return margins
            
        except Exception as e:
            from letterhead_pdf.exceptions import MarkdownProcessingError
            error_msg = f"Error analyzing letterhead margins: {str(e)}"
            logging.error(error_msg)
            raise MarkdownProcessingError(error_msg) from e
        finally:
            if 'doc' in locals():
                doc.close()

    def _calculate_smart_margins(self, regions: Dict, page_rect) -> Dict[str, float]:
        """Calculate margins using comprehensive content analysis including middle blocks"""
        content_regions = regions.get('content_regions', [])
        
        # Default margins (standard document margins)
        default_margin = 72  # 1 inch in points
        min_margin = 36      # 0.5 inch minimum
        safe_padding = 20    # Safe distance from letterhead content
        
        page_width = page_rect.width
        page_height = page_rect.height
        
        # Start with default printable area
        printable_rect = fitz.Rect(
            default_margin,  # left
            default_margin,  # top
            page_width - default_margin,   # right
            page_height - default_margin   # bottom
        )
        
        logging.info(f"Initial printable area: {printable_rect}")
        
        # Adjust for each content region
        for region_type, content_rect in content_regions:
            if printable_rect.intersects(content_rect):
                logging.info(f"Content overlaps printable area: {region_type} at {content_rect}")
                printable_rect = self._adjust_printable_area(printable_rect, content_rect, page_rect)
        
        # Ensure minimum printable area
        min_width = page_width * 0.3  # At least 30% of page width
        min_height = page_height * 0.3  # At least 30% of page height
        
        if printable_rect.width < min_width or printable_rect.height < min_height:
            logging.warning(f"Printable area too small: {printable_rect.width}x{printable_rect.height}")
            # Fall back to centered rectangle with minimum size
            center_x = page_width / 2
            center_y = page_height / 2
            printable_rect = fitz.Rect(
                center_x - min_width/2,
                center_y - min_height/2,
                center_x + min_width/2,
                center_y + min_height/2
            )
        
        # Convert printable rectangle to margins
        left_margin = max(min_margin, printable_rect.x0)
        top_margin = max(min_margin, printable_rect.y0)
        right_margin = max(min_margin, page_width - printable_rect.x1)
        bottom_margin = max(min_margin, page_height - printable_rect.y1)
        
        # Log the effective printable area
        final_printable_width = page_width - left_margin - right_margin
        final_printable_height = page_height - top_margin - bottom_margin
        usable_percentage = (final_printable_width * final_printable_height) / (page_width * page_height) * 100
        
        logging.info(f"Final printable area: {final_printable_width:.1f}x{final_printable_height:.1f}pt ({usable_percentage:.1f}% of page)")
        logging.info(f"Margins: top={top_margin:.1f}, right={right_margin:.1f}, bottom={bottom_margin:.1f}, left={left_margin:.1f}")
        
        return {
            'top': top_margin,
            'right': right_margin,
            'bottom': bottom_margin,
            'left': left_margin
        }
    
    def _adjust_printable_area(self, printable_rect: fitz.Rect, content_rect: fitz.Rect, page_rect: fitz.Rect) -> fitz.Rect:
        """Adjust printable area to avoid overlapping with content"""
        safe_padding = 20
        
        # Calculate possible adjustments
        adjustments = []
        
        # Option 1: Move left boundary right (avoid content on left)
        if content_rect.x1 + safe_padding < page_rect.width * 0.8:
            new_rect = fitz.Rect(
                max(printable_rect.x0, content_rect.x1 + safe_padding),
                printable_rect.y0,
                printable_rect.x1,
                printable_rect.y1
            )
            if new_rect.width > 0:
                adjustments.append(new_rect)
        
        # Option 2: Move right boundary left (avoid content on right)
        if content_rect.x0 - safe_padding > page_rect.width * 0.2:
            new_rect = fitz.Rect(
                printable_rect.x0,
                printable_rect.y0,
                min(printable_rect.x1, content_rect.x0 - safe_padding),
                printable_rect.y1
            )
            if new_rect.width > 0:
                adjustments.append(new_rect)
        
        # Option 3: Move top boundary down (avoid content above)
        if content_rect.y1 + safe_padding < page_rect.height * 0.8:
            new_rect = fitz.Rect(
                printable_rect.x0,
                max(printable_rect.y0, content_rect.y1 + safe_padding),
                printable_rect.x1,
                printable_rect.y1
            )
            if new_rect.height > 0:
                adjustments.append(new_rect)
        
        # Option 4: Move bottom boundary up (avoid content below)
        if content_rect.y0 - safe_padding > page_rect.height * 0.2:
            new_rect = fitz.Rect(
                printable_rect.x0,
                printable_rect.y0,
                printable_rect.x1,
                min(printable_rect.y1, content_rect.y0 - safe_padding)
            )
            if new_rect.height > 0:
                adjustments.append(new_rect)
        
        # Choose the adjustment that preserves the most area
        if adjustments:
            best_rect = max(adjustments, key=lambda r: r.width * r.height)
            logging.info(f"Adjusted printable area from {printable_rect} to {best_rect}")
            return best_rect
        
        # If no good adjustment found, return original
        return printable_rect

    def extract_images(self, html_content):
        """Extract images from HTML content and return cleaned content"""
        # Find all image tags
        img_pattern = re.compile(r'<img[^>]+>')
        img_tags = img_pattern.findall(html_content)
        
        # Extract image sources
        images = []
        for img_tag in img_tags:
            src_match = re.search(r'src="([^"]+)"', img_tag)
            if src_match:
                src = src_match.group(1)
                # Only include local images
                if not src.startswith(('http://', 'https://')):
                    images.append(src)
            
            # Remove the image tag from the content
            html_content = html_content.replace(img_tag, '')
        
        return html_content, images

    def clean_html_for_reportlab(self, html_content):
        """Clean HTML content to be compatible with ReportLab"""
        # Remove Pygments code highlighting divs and spans - they're not compatible with ReportLab
        # Replace codehilite divs with simple pre tags
        html_content = re.sub(r'<div class="codehilite"><pre><span></span>(.*?)</pre></div>', 
                             r'<pre>\1</pre>', html_content, flags=re.DOTALL)
        
        # Remove all span elements with class attributes (from Pygments)
        html_content = re.sub(r'<span[^>]*class="[^"]*"[^>]*>(.*?)</span>', r'\1', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', html_content, flags=re.DOTALL)
        
        # Remove any remaining div tags with classes
        html_content = re.sub(r'<div[^>]*class="[^"]*"[^>]*>(.*?)</div>', r'\1', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<div[^>]*>(.*?)</div>', r'\1', html_content, flags=re.DOTALL)
        
        # Clean links - remove title and other attributes
        link_pattern = re.compile(r'<a\s+([^>]+)>')
        
        def clean_link(match):
            attrs = match.group(1)
            # Keep only href attribute
            href_match = re.search(r'href="([^"]+)"', attrs)
            if href_match:
                href = href_match.group(1)
                return f'<a href="{href}">'
            return '<a>'
        
        html_content = link_pattern.sub(clean_link, html_content)
        
        # Convert HTML formatting to ReportLab formatting
        html_content = html_content.replace('<strong>', '<b>').replace('</strong>', '</b>')
        html_content = html_content.replace('<em>', '<i>').replace('</em>', '</i>')
        
        # Handle GFM strikethrough: <del> -> <strike> (ReportLab compatibility)
        html_content = html_content.replace('<del>', '<strike>').replace('</del>', '</strike>')
        
        # Handle inline code tags more carefully
        html_content = re.sub(r'<code[^>]*>(.*?)</code>', r'<font face="Courier">\1</font>', html_content)
        
        # Handle GFM task list checkboxes - convert to better text representation
        # Use Unicode checkbox symbols for better visual appearance
        html_content = re.sub(r'<input type="checkbox" checked[^>]*\s*/?\s*>\s*', '☑ ', html_content)  # ☑ U+2611
        html_content = re.sub(r'<input type="checkbox"[^>]*\s*/?\s*>\s*', '☐ ', html_content)  # ☐ U+2610 - back to original
        
        # Handle checkbox syntax in table cells and other text content
        # Convert [x] and [ ] patterns to Unicode checkbox symbols
        # Back to original symbols
        html_content = re.sub(r'\[x\]', '☑', html_content)  # ☑ U+2611 - checked
        html_content = re.sub(r'\[\s\]', '☐', html_content)  # ☐ U+2610 - unchecked
        
        # Remove any remaining data-gfm-task attributes and other GFM attributes
        html_content = re.sub(r'\s+data-gfm-task="[^"]*"', '', html_content)
        html_content = re.sub(r'\s+disabled=""', '', html_content)
        
        # Remove any remaining class attributes from any tags
        html_content = re.sub(r'(\s+class="[^"]*")', '', html_content)
        
        return html_content

    def process_list_items(self, list_type, lines, start_index, nesting_level=0):
        """Process list items and return a list of items and the new index
        
        Args:
            list_type: 'bullet' or 'number'
            lines: List of HTML lines to process
            start_index: Starting index in lines
            nesting_level: Current nesting depth (0 = top level)
        
        Returns:
            Tuple of (items_with_indentation, new_index)
        """
        items = []
        i = start_index
        
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('<li>'):
                # Extract text from list item
                text = line.replace('<li>', '').replace('</li>', '')
                
                # Handle multi-line list items
                j = i + 1
                while j < len(lines) and not lines[j].strip().endswith('</li>') and not lines[j].strip() == '</ul>' and not lines[j].strip() == '</ol>':
                    text += ' ' + lines[j].strip()
                    j += 1
                
                if j < len(lines) and lines[j].strip().endswith('</li>'):
                    text += ' ' + lines[j].strip().replace('</li>', '')
                    i = j
                
                # Convert HTML formatting
                text = text.replace('<strong>', '<b>').replace('</strong>', '</b>')
                text = text.replace('<em>', '<i>').replace('</em>', '</i>')
                text = text.replace('<code>', '<font face="Courier">').replace('</code>', '</font>')
                
                # Store item with its nesting level
                items.append({
                    'text': text,
                    'nesting_level': nesting_level,
                    'has_nested': '<ul>' in text or '<ol>' in text
                })
            
            elif line == '</ul>' or line == '</ol>':
                break
            
            i += 1
        
        return items, i

    def preprocess_markdown_indentation(self, md_content):
        """Preprocess markdown to normalize list indentation and fix colon-list formatting
        
        This ensures that:
        1. Both 2-space and 4-space indented lists work correctly with the Python 
           markdown library, which requires 4-space indentation for nesting.
        2. Lists following lines ending with ':' are properly recognized by inserting
           blank lines where needed.
        
        Uses context-aware processing to properly handle mixed indentation patterns.
        
        Args:
            md_content: Raw markdown content string
            
        Returns:
            Preprocessed markdown with normalized 4-space list indentation and fixed colon-list formatting
        """
        import re
        
        lines = md_content.split('\n')
        processed_lines = []
        
        # Pattern to match list items (unordered and ordered)
        list_item_pattern = re.compile(r'^(\s*)([-*+]|\d+\.)\s+(.*)$')
        
        # Pattern to match lines ending with colon (potential list introduction)
        colon_line_pattern = re.compile(r'^.*:\s*$')
        
        # Track indentation context for proper nesting
        indent_stack = []  # Stack of (original_indent, normalized_indent) pairs
        
        for i, line in enumerate(lines):
            match = list_item_pattern.match(line)
            if match:
                indent_str, marker, content = match.groups()
                current_indent = len(indent_str)
                
                # Check if previous line ends with colon and has no blank line
                if (processed_lines and 
                    colon_line_pattern.match(processed_lines[-1]) and
                    current_indent == 0):  # Only for top-level lists
                    # Insert blank line before the list for proper markdown parsing
                    processed_lines.append('')
                    logging.debug(f"Inserted blank line after colon before list: {line.strip()}")
                
                # Find the appropriate nesting level by comparing with stack
                normalized_indent = self._calculate_normalized_indent(current_indent, indent_stack)
                
                # Reconstruct the line with normalized indentation
                indent_spaces = ' ' * normalized_indent
                processed_line = f"{indent_spaces}{marker} {content}"
                processed_lines.append(processed_line)
                
                # Log the conversion for debugging
                if current_indent != normalized_indent:
                    logging.debug(f"Converted indentation: {current_indent} -> {normalized_indent} spaces: {line.strip()}")
            else:
                # Non-list line - reset indentation context and keep as-is
                if line.strip() == '':
                    # Empty line - don't reset context (lists can have blank lines)
                    pass
                elif not line.startswith(' '):
                    # Non-indented line (like headers) - reset context
                    indent_stack = []
                
                processed_lines.append(line)
        
        return '\n'.join(processed_lines)
    
    def _calculate_normalized_indent(self, current_indent, indent_stack):
        """Calculate the normalized indentation level based on context
        
        Args:
            current_indent: Current number of spaces
            indent_stack: Stack tracking indentation context
            
        Returns:
            Normalized indentation (multiple of 4)
        """
        if current_indent == 0:
            # Top level - reset stack
            indent_stack.clear()
            return 0
        
        # Remove stack entries for indentation levels we've moved back from
        while indent_stack and indent_stack[-1][0] >= current_indent:
            indent_stack.pop()
        
        # Check if this is a known indentation level
        for original, normalized in indent_stack:
            if original == current_indent:
                return normalized
        
        # New indentation level - calculate normalized value
        if not indent_stack:
            # First nested level
            normalized = 4
        else:
            # Deeper nesting - add 4 spaces to the previous level
            normalized = indent_stack[-1][1] + 4
        
        # Add to stack for future reference
        indent_stack.append((current_indent, normalized))
        
        return normalized

    def detect_list_nesting_structure(self, html_content):
        """Analyze HTML structure to detect list nesting levels and calculate indentation
        
        Returns:
            Dict with nesting information and calculated indentation values
        """
        import re
        
        # Find all nested list structures
        nested_levels = []
        
        # Count maximum nesting depth by analyzing nested ul/ol tags
        ul_ol_pattern = r'<(ul|ol)[^>]*>'
        close_pattern = r'</(?:ul|ol)>'
        
        depth = 0
        max_depth = 0
        
        # Simple depth tracking - count opening vs closing tags
        for match in re.finditer(ul_ol_pattern + '|' + close_pattern, html_content):
            tag = match.group(0)
            if tag.startswith('</'):
                depth -= 1
            else:
                depth += 1
                max_depth = max(max_depth, depth)
        
        # Calculate base indentation per level
        # We'll use 15pt for 2-space equivalent, 20pt for 4-space equivalent
        # The system will auto-detect based on typical patterns
        base_indent = 18  # Compromise between 15pt and 20pt for good readability
        
        return {
            'max_depth': max_depth,
            'base_indent': base_indent,
            'indent_per_level': base_indent
        }
    
    def calculate_list_indentation(self, nesting_level, indent_info):
        """Calculate appropriate indentation for a given nesting level
        
        Args:
            nesting_level: The depth level (0, 1, 2, etc.)
            indent_info: Dict from detect_list_nesting_structure
            
        Returns:
            Indentation value in points
        """
        base = indent_info['base_indent']
        per_level = indent_info['indent_per_level']
        
        # Calculate total indentation: base + (level * per_level)
        total_indent = base + (nesting_level * per_level)
        
        # Ensure minimum indentation
        return max(total_indent, 12)

    def parse_nested_lists(self, text):
        """Parse nested list structures and return ReportLab-compatible structure"""
        import re
        
        # For now, implement a simple approach that handles one level of nesting
        # This addresses the TODO and provides basic nested list functionality
        
        # Find nested <ul> or <ol> blocks
        nested_pattern = r'<(ul|ol)>(.*?)</\1>'
        
        def replace_nested_list(match):
            list_type = match.group(1)
            list_content = match.group(2)
            
            # Extract list items from the nested content
            item_pattern = r'<li>(.*?)</li>'
            items = re.findall(item_pattern, list_content, re.DOTALL)
            
            # Create a simple text representation for now
            # In a full implementation, this would create nested ListFlowable objects
            nested_text = ""
            for i, item in enumerate(items, 1):
                # Add indentation to show nesting
                if list_type == 'ul':
                    nested_text += "\n    • " + item.strip()
                else:
                    nested_text += f"\n    {i}. " + item.strip()
            
            return nested_text
        
        # Replace nested lists with indented text representation
        result = re.sub(nested_pattern, replace_nested_list, text, flags=re.DOTALL)
        
        return result

    def safe_list_item_value(self, item_type, proposed_value=None):
        """
        Return safe value for ListItem to prevent ReportLab crashes.
        
        ReportLab has a critical bug where setting integer values (except 0) 
        on ListItem objects in bulleted lists causes crashes. This function
        provides safe defaults and validates proposed values.
        
        Args:
            item_type (str): 'bullet' or 'number'
            proposed_value: The value to validate (optional)
            
        Returns:
            Safe value for ListItem.value parameter
        """
        if item_type == 'bullet':
            # For bullets: use string values or 0 only
            if proposed_value is None:
                return '•'  # Safe default bullet character
            elif proposed_value == 0:
                return 0  # Zero is safe
            else:
                return str(proposed_value)  # Convert to string for safety
        else:
            # For numbered lists: avoid integer values except 0
            if proposed_value is None:
                return 0  # Safe default for numbered lists
            elif isinstance(proposed_value, int) and proposed_value != 0:
                return str(proposed_value)  # Convert problematic integers to strings
            else:
                return proposed_value  # Other values should be safe
    
    def markdown_to_flowables(self, html_content: str) -> list:
        """Convert HTML content from markdown to reportlab flowables"""
        # Create list of flowables
        flowables = []
        
        # Extract images first to avoid parsing issues
        html_content, images = self.extract_images(html_content)
        
        # Clean HTML for ReportLab compatibility
        html_content = self.clean_html_for_reportlab(html_content)
        
        # Add local images as separate flowables if they exist
        for img_src in images:
            try:
                # Local image
                img_obj = Image(img_src)
                img_obj.drawHeight = 0.5 * inch  # Even smaller height
                img_obj.drawWidth = 0.5 * inch * (img_obj.imageWidth / img_obj.imageHeight)
                flowables.append(img_obj)
                flowables.append(Spacer(1, 6))  # Smaller spacer
            except Exception as e:
                logging.warning(f"Failed to load local image {img_src}: {e}")
        
        # Process HTML content line by line to identify elements
        lines = html_content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Headers
            if line.startswith('<h1>'):
                text = line.replace('<h1>', '').replace('</h1>', '')
                flowables.append(Paragraph(text, self.styles['CustomHeading1']))
                flowables.append(Spacer(1, 6))
            
            elif line.startswith('<h2>'):
                text = line.replace('<h2>', '').replace('</h2>', '')
                flowables.append(Paragraph(text, self.styles['CustomHeading2']))
                flowables.append(Spacer(1, 4))
            
            elif line.startswith('<h3>'):
                text = line.replace('<h3>', '').replace('</h3>', '')
                flowables.append(Paragraph(text, self.styles['CustomHeading3']))
                flowables.append(Spacer(1, 4))
            
            # Paragraphs
            elif line.startswith('<p>'):
                text = line.replace('<p>', '').replace('</p>', '')
                # Handle multi-line paragraphs
                j = i + 1
                while j < len(lines) and not lines[j].strip().endswith('</p>'):
                    text += ' ' + lines[j].strip()
                    j += 1
                if j < len(lines) and lines[j].strip().endswith('</p>'):
                    text += ' ' + lines[j].strip().replace('</p>', '')
                    i = j
                
                # Add paragraph text
                if text.strip():
                    flowables.append(Paragraph(text, self.styles['Normal']))
                    flowables.append(Spacer(1, 6))
            
            # Lists - improved handling with dynamic indentation
            elif line.startswith('<ul>'):
                # Detect indentation structure for the entire HTML content
                indent_info = self.detect_list_nesting_structure(html_content)
                items, i = self.process_list_items('bullet', lines, i + 1)
                
                # Create bullet list with dynamic indentation
                bullet_list = []
                for item_data in items:
                    if isinstance(item_data, dict):
                        item_text = item_data['text']
                        nesting_level = item_data['nesting_level']
                        calculated_indent = self.calculate_list_indentation(nesting_level, indent_info)
                    else:
                        # Backward compatibility for simple string items
                        item_text = item_data
                        calculated_indent = 20
                    
                    # Create dynamic style for this indentation level
                    item_style = ParagraphStyle(
                        name=f'BulletItem_Level{nesting_level if isinstance(item_data, dict) else 0}',
                        parent=self.styles['Normal'],
                        leftIndent=calculated_indent,
                        firstLineIndent=0
                    )
                    
                    # Use safe value to prevent ReportLab crashes with integer values
                    safe_value = self.safe_list_item_value('bullet')
                    bullet_list.append(ListItem(
                        Paragraph(item_text, item_style), 
                        leftIndent=calculated_indent,
                        value=safe_value
                    ))
                
                # Use base indentation for the list container
                base_indent = indent_info['base_indent']
                flowables.append(ListFlowable(
                    bullet_list,
                    bulletType='bullet',
                    start=0,
                    bulletFontName='Helvetica',
                    bulletFontSize=10,
                    leftIndent=base_indent,
                    spaceBefore=6,
                    spaceAfter=6
                ))
            
            elif line.startswith('<ol>'):
                # Detect indentation structure for the entire HTML content
                indent_info = self.detect_list_nesting_structure(html_content)
                items, i = self.process_list_items('number', lines, i + 1)
                
                # Create numbered list with dynamic indentation
                number_list = []
                for item_data in items:
                    if isinstance(item_data, dict):
                        item_text = item_data['text']
                        nesting_level = item_data['nesting_level']
                        calculated_indent = self.calculate_list_indentation(nesting_level, indent_info)
                    else:
                        # Backward compatibility for simple string items
                        item_text = item_data
                        calculated_indent = 20
                    
                    # Create dynamic style for this indentation level
                    item_style = ParagraphStyle(
                        name=f'NumberItem_Level{nesting_level if isinstance(item_data, dict) else 0}',
                        parent=self.styles['Normal'],
                        leftIndent=calculated_indent,
                        firstLineIndent=0
                    )
                    
                    # Use safe value to prevent ReportLab crashes with integer values
                    safe_value = self.safe_list_item_value('number')
                    number_list.append(ListItem(
                        Paragraph(item_text, item_style), 
                        leftIndent=calculated_indent,
                        value=safe_value
                    ))
                
                # Use base indentation for the list container
                base_indent = indent_info['base_indent']
                flowables.append(ListFlowable(
                    number_list,
                    bulletType='1',
                    start=1,
                    bulletFontName='Helvetica',
                    bulletFontSize=10,
                    leftIndent=base_indent,
                    spaceBefore=6,
                    spaceAfter=6
                ))
            
            # Code blocks - improved styling
            elif line.startswith('<pre>'):
                code = []
                j = i
                while j < len(lines) and not lines[j].strip().endswith('</pre>'):
                    if j > i:  # Skip the opening <pre> tag
                        code.append(lines[j])
                    j += 1
                if j < len(lines) and lines[j].strip().endswith('</pre>'):
                    code.append(lines[j].replace('</pre>', ''))
                    i = j
                
                code_text = '\n'.join(code).replace('<code>', '').replace('</code>', '')
                # Use Preformatted for better code block rendering
                flowables.append(Preformatted(code_text, self.styles['Code']))
                flowables.append(Spacer(1, 8))
            
            # Tables
            elif line.startswith('<table>'):
                data = []
                j = i + 1
                while j < len(lines) and not lines[j].strip() == '</table>':
                    if lines[j].strip().startswith('<tr>'):
                        row = []
                        k = j + 1
                        while k < len(lines) and not lines[k].strip() == '</tr>':
                            if lines[k].strip().startswith('<td>') or lines[k].strip().startswith('<th>'):
                                cell_text = lines[k].strip()
                                cell_text = cell_text.replace('<td>', '').replace('</td>', '')
                                cell_text = cell_text.replace('<th>', '').replace('</th>', '')
                                row.append(cell_text)
                            k += 1
                        j = k
                        if row:
                            data.append(row)
                    j += 1
                i = j
                
                if data:
                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('LEFTPADDING', (0, 0), (-1, -1), 6),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 6)
                    ]))
                    flowables.append(table)
                    flowables.append(Spacer(1, 12))
            
            # Blockquotes
            elif line.startswith('<blockquote>'):
                text = []
                j = i + 1
                while j < len(lines) and not lines[j].strip() == '</blockquote>':
                    if lines[j].strip().startswith('<p>'):
                        p_text = lines[j].strip().replace('<p>', '').replace('</p>', '')
                        text.append(p_text)
                    j += 1
                i = j
                
                if text:
                    quote_text = ' '.join(text)
                    flowables.append(Paragraph(quote_text, self.styles['Blockquote']))
                    flowables.append(Spacer(1, 6))
            
            i += 1
        
        # If no content was added, add a blank paragraph
        if not flowables:
            flowables.append(Paragraph("", self.styles['Normal']))
        
        logging.info(f"Generated {len(flowables)} flowables")
        return flowables

    def md_to_pdf(self, md_path: str, output_path: str, letterhead_path: str, css_path: str = None, save_html: str = None, pdf_backend: str = 'auto') -> str:
        """Convert markdown file to PDF with proper margins based on letterhead
        
        Args:
            md_path: Path to input markdown file
            output_path: Path for output PDF file  
            letterhead_path: Path to letterhead PDF template
            css_path: Optional path to custom CSS file
            save_html: Optional path to save intermediate HTML file for debugging
            pdf_backend: PDF backend to use ('auto', 'weasyprint', 'reportlab')
        """
        logging.info(f"Converting markdown to PDF: {md_path} -> {output_path}")
        
        try:
            # Read markdown content
            with open(md_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Preprocess markdown to normalize list indentation
            # This ensures both 2-space and 4-space indented lists work correctly
            md_content = self.preprocess_markdown_indentation(md_content)
            
            # Convert to HTML using appropriate backend
            html_content = self.md_to_html(md_content)
            backend_info = "GitHub Flavored Markdown" if self.use_gfm else "standard markdown"
            logging.info("Generated HTML content using %s", backend_info)
            
            # Save intermediate HTML if requested (save the raw HTML before any processing)
            if save_html:
                with open(save_html, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logging.info(f"Saved intermediate HTML to: {save_html}")
            
            # Analyze letterhead for margins and page size
            doc = fitz.open(letterhead_path)
            try:
                first_page = doc[0]
                regions = self.analyze_page_regions(first_page)
                margins = self.analyze_letterhead(letterhead_path)
                page_size = regions['page_size']
            finally:
                doc.close()
            
            # Create temporary file for initial PDF
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
                # Determine which PDF backend to use
                use_weasyprint = False
                if pdf_backend == 'weasyprint':
                    if WEASYPRINT_AVAILABLE:
                        use_weasyprint = True
                    else:
                        raise PDFCreationError(f"WeasyPrint backend requested but not available")
                elif pdf_backend == 'reportlab':
                    use_weasyprint = False
                else:  # auto
                    use_weasyprint = WEASYPRINT_AVAILABLE
                
                backend_name = "WeasyPrint" if use_weasyprint else "ReportLab"
                logging.info(f"Using {backend_name} for PDF generation")
                
                if use_weasyprint:
                    # Use WeasyPrint for high-quality PDF generation
                    self._md_to_pdf_weasyprint(html_content, temp_pdf.name, margins, page_size, css_path)
                else:
                    # Use ReportLab
                    self._md_to_pdf_reportlab(html_content, temp_pdf.name, margins, page_size)
                
                # Create final PDF with metadata
                pdf = fitz.open(temp_pdf.name)
                try:
                    pdf.set_metadata({
                        'title': os.path.basename(md_path),
                        'author': 'Mac-letterhead',
                        'creator': 'Mac-letterhead',
                        'producer': 'Mac-letterhead'
                    })
                    pdf.save(output_path)
                finally:
                    pdf.close()
            
            # Clean up temporary files
            os.unlink(temp_pdf.name)
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
            
            return output_path
            
        except Exception as e:
            from letterhead_pdf.exceptions import MarkdownProcessingError
            error_msg = f"Error converting markdown to PDF: {str(e)}"
            logging.error(error_msg)
            raise MarkdownProcessingError(error_msg) from e
    
    def _md_to_pdf_weasyprint(self, html_content, output_path, margins, page_size, css_path=None):
        """Convert HTML to PDF using WeasyPrint"""
        logging.info("Using WeasyPrint for PDF generation")
        
        # Enhance GFM task list HTML for better CSS styling
        html_content = self._enhance_gfm_task_lists_for_weasyprint(html_content)
        
        # Import WeasyPrint components when needed
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        # Load default CSS from package
        defaults_css = ""
        try:
            # Try modern importlib.resources first (Python 3.9+)
            try:
                from importlib import resources
                with resources.open_text('letterhead_pdf.resources', 'defaults.css') as f:
                    defaults_css = f.read()
                logging.info("Loaded default CSS from package using importlib.resources")
            except (ImportError, AttributeError):
                # Fallback to importlib_resources for older Python versions
                try:
                    import importlib_resources
                    with importlib_resources.open_text('letterhead_pdf.resources', 'defaults.css') as f:
                        defaults_css = f.read()
                    logging.info("Loaded default CSS from package using importlib_resources")
                except ImportError:
                    # Final fallback to file path
                    current_dir = os.path.dirname(__file__)
                    defaults_css_path = os.path.join(current_dir, 'resources', 'defaults.css')
                    with open(defaults_css_path, 'r', encoding='utf-8') as f:
                        defaults_css = f.read()
                    logging.info("Loaded default CSS from package using file path")
        except Exception as e:
            logging.warning(f"Could not load default CSS: {e}")
            defaults_css = ""
        
        # Load custom CSS if provided
        custom_css = ""
        debug_info = []
        
        if css_path:
            debug_info.append(f"CSS path provided: {css_path}")
            css_exists = os.path.exists(css_path)
            debug_info.append(f"CSS path exists: {css_exists}")
            
            if css_exists:
                try:
                    with open(css_path, 'r', encoding='utf-8') as f:
                        custom_css = f.read()
                    debug_info.append(f"✅ CSS loaded successfully, length: {len(custom_css)} chars")
                    debug_info.append(f"CSS preview: {custom_css[:100]}...")
                except Exception as e:
                    debug_info.append(f"❌ CSS load failed: {str(e)}")
            else:
                debug_info.append(f"❌ CSS file not found: {css_path}")
        else:
            debug_info.append("No CSS path provided")
        
        # Write debug info to a temp file that we can check
        try:
            debug_file = "/tmp/mac-letterhead-css-debug.txt"
            with open(debug_file, 'w') as f:
                f.write(f"CSS Debug Info - {os.getpid()}\n")
                f.write(f"Timestamp: {__import__('datetime').datetime.now()}\n")
                f.write("\n".join(debug_info))
                f.write(f"\nFinal CSS length: {len(custom_css)}")
        except:
            pass  # Don't let debug logging break the main process
        
        # Also try regular logging
        logging.info(f"CSS processing: {'; '.join(debug_info)}")
        
        # Generate Pygments CSS for syntax highlighting if available
        pygments_css = ""
        if PYGMENTS_AVAILABLE:
            pygments_css = HtmlFormatter().get_style_defs('.codehilite')
            logging.info("Added Pygments CSS for syntax highlighting")
        
        # Process custom CSS to remove @page rules that would override margins
        processed_custom_css = custom_css
        if custom_css:
            # Remove any @page rules from custom CSS to preserve smart margins
            import re
            processed_custom_css = re.sub(r'@page\s*{[^}]*}', '', custom_css, flags=re.DOTALL | re.IGNORECASE)
            if processed_custom_css != custom_css:
                logging.info("Removed @page rules from custom CSS to preserve smart letterhead margins")
        
        # Create CSS in the correct order: defaults + custom + hardcoded page settings
        combined_css = f"""
        /* ==================== DEFAULT CSS FROM PACKAGE ==================== */
        {defaults_css}
        
        /* ==================== CUSTOM USER CSS (if provided) ==================== */
        {processed_custom_css}
        
        /* ==================== SYNTAX HIGHLIGHTING ==================== */
        {pygments_css}
        
        /* ==================== HARDCODED PAGE LAYOUT (CANNOT BE OVERRIDDEN) ==================== */
        /* Smart letterhead margins - these override any @page rules above */
        @page {{
            margin-top: {margins['first_page']['top']}pt !important;
            margin-right: {margins['first_page']['right']}pt !important;
            margin-bottom: {margins['first_page']['bottom']}pt !important;
            margin-left: {margins['first_page']['left']}pt !important;
            
            @bottom-center {{
                content: counter(page);
                font-family: Helvetica, Arial, sans-serif;
                font-size: 9pt;
                color: #666666;
            }}
        }}
        """
        
        # Create a minimal HTML document with the content
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Markdown Document</title>
            <style>
                {combined_css}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Configure fonts
        font_config = FontConfiguration()
        
        # Convert HTML to PDF
        html = HTML(string=html_template)
        html.write_pdf(output_path, font_config=font_config)
    
    def _md_to_pdf_reportlab(self, html_content, output_path, margins, page_size):
        """Convert HTML to PDF using ReportLab (fallback method)"""
        logging.info("Using ReportLab for PDF generation")
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=page_size,
            leftMargin=margins['first_page']['left'],
            rightMargin=margins['first_page']['right'],
            topMargin=margins['first_page']['top'],
            bottomMargin=margins['first_page']['bottom'],
            allowSplitting=True,
            displayDocTitle=True,
            pageCompression=0
        )
        
        # Convert HTML to reportlab flowables
        flowables = self.markdown_to_flowables(html_content)
        
        # Build PDF
        doc.build(flowables)
    
    def _enhance_gfm_task_lists_for_weasyprint(self, html_content: str) -> str:
        """Enhance GFM task list HTML for better WeasyPrint rendering with CSS classes"""
        import re
        
        # Add CSS classes to task list items for better styling control
        # Pattern: <li data-gfm-task="..."><input type="checkbox" checked="" disabled="" /> text</li>
        # Replace with: <li class="task-item task-checked" data-gfm-task="...">text</li>
        
        def replace_checked_task(match):
            full_match = match.group(0)
            data_attr = match.group(1) if match.group(1) else ''
            checkbox_html = match.group(2)
            text_content = match.group(3)
            
            # Add CSS classes and replace checkbox with Unicode symbol
            return f'<li class="task-item task-checked"{data_attr}>☑ {text_content}</li>'
        
        def replace_unchecked_task(match):
            full_match = match.group(0)
            data_attr = match.group(1) if match.group(1) else ''
            checkbox_html = match.group(2)
            text_content = match.group(3)
            
            # Add CSS classes and replace checkbox with Unicode symbol
            return f'<li class="task-item task-unchecked"{data_attr}>☐ {text_content}</li>'
        
        # Pattern for checked tasks
        checked_pattern = re.compile(
            r'<li(\s+data-gfm-task="[^"]*")?>\s*(<input type="checkbox" checked[^>]*\s*/?\s*>)\s*(.*?)</li>',
            re.DOTALL
        )
        
        # Pattern for unchecked tasks  
        unchecked_pattern = re.compile(
            r'<li(\s+data-gfm-task="[^"]*")?>\s*(<input type="checkbox"[^>]*\s*/?\s*>)\s*(.*?)</li>',
            re.DOTALL
        )
        
        # Replace checked tasks first (more specific pattern)
        html_content = checked_pattern.sub(replace_checked_task, html_content)
        
        # Then replace remaining unchecked tasks
        html_content = unchecked_pattern.sub(replace_unchecked_task, html_content)
        
        # Handle checkbox syntax in table cells and other text content (for WeasyPrint)
        # Convert [x] and [ ] patterns to Unicode checkbox symbols with appropriate styling
        # Back to original symbols with CSS scaling for table cells
        html_content = re.sub(r'\[x\]', '<span class="task-checked">☑</span>', html_content)  # ☑ U+2611 - checked
        html_content = re.sub(r'\[\s\]', '<span class="task-unchecked task-unchecked-scaled">☐</span>', html_content)  # ☐ U+2610 - unchecked with scaling
        
        return html_content
