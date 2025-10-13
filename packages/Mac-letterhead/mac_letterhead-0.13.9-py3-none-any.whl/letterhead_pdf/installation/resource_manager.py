"""
ResourceManager - Handles stationery files and resource bundling.

This class manages all file operations related to droplet resources:
- Validating and copying letterhead files
- Setting up app bundle resource structure
- Managing icons and other assets
"""

import os
import logging
import shutil
from typing import Optional

from letterhead_pdf.exceptions import InstallerError


class ResourceManager:
    """Manages resources for droplet creation."""
    
    def __init__(self):
        """Initialize the ResourceManager."""
        self.logger = logging.getLogger(__name__)
    
    def setup_app_resources(self, app_path: str, letterhead_path: str, css_path: str = None, development_mode: bool = False, python_path: str = None) -> None:
        """
        Set up all resources for the app bundle.
        
        Args:
            app_path: Path to the app bundle
            letterhead_path: Path to the letterhead PDF file
            css_path: Path to custom CSS file (optional)
            development_mode: If True, create dev_mode marker file
            python_path: Path to Python interpreter (for development mode)
            
        Raises:
            InstallerError: If resource setup fails
        """
        self.logger.info(f"Setting up resources for app: {app_path} (dev_mode={development_mode})")
        
        try:
            # Ensure app bundle structure exists
            contents_dir = os.path.join(app_path, "Contents")
            resources_dir = os.path.join(contents_dir, "Resources")
            os.makedirs(resources_dir, exist_ok=True)
            
            # Copy letterhead to app resources
            self._copy_letterhead(resources_dir, letterhead_path)
            
            # Copy CSS file to app resources
            self._copy_css(resources_dir, css_path)
            
            # Copy application icons
            self._copy_icons(resources_dir)
            
            # Create dev_mode marker file if in development mode
            if development_mode:
                self._create_dev_mode_marker(resources_dir, python_path)
            
            self.logger.info("App resources setup completed")
            
        except Exception as e:
            error_msg = f"Failed to setup app resources: {str(e)}"
            self.logger.error(error_msg)
            raise InstallerError(error_msg) from e
    
    def _copy_letterhead(self, resources_dir: str, letterhead_path: str) -> None:
        """Copy letterhead file to app resources."""
        abs_letterhead_path = os.path.abspath(letterhead_path)
        
        # Validate letterhead file
        if not os.path.exists(abs_letterhead_path):
            raise InstallerError(f"Letterhead file not found: {abs_letterhead_path}")
        
        if not abs_letterhead_path.lower().endswith('.pdf'):
            raise InstallerError(f"Letterhead must be a PDF file: {abs_letterhead_path}")
        
        # Copy letterhead to standard location in app bundle
        app_letterhead_path = os.path.join(resources_dir, "letterhead.pdf")
        shutil.copy2(abs_letterhead_path, app_letterhead_path)
        
        self.logger.info(f"Copied letterhead: {abs_letterhead_path} -> {app_letterhead_path}")
        
        # Verify the copy
        if not os.path.exists(app_letterhead_path):
            raise InstallerError(f"Failed to copy letterhead to: {app_letterhead_path}")
    
    def _copy_css(self, resources_dir: str, css_path: str = None) -> None:
        """Copy CSS file to app resources or use defaults."""
        app_css_path = os.path.join(resources_dir, "style.css")
        
        if css_path:
            # Use custom CSS file
            abs_css_path = os.path.abspath(css_path)
            
            # Validate custom CSS file
            if not os.path.exists(abs_css_path):
                raise InstallerError(f"Custom CSS file not found: {abs_css_path}")
            
            if not abs_css_path.lower().endswith('.css'):
                raise InstallerError(f"CSS file must have .css extension: {abs_css_path}")
            
            # Copy custom CSS file
            shutil.copy2(abs_css_path, app_css_path)
            self.logger.info(f"Copied custom CSS: {abs_css_path} -> {app_css_path}")
        else:
            # Use default CSS file from package resources
            try:
                package_resources_dir = self._get_package_resources_dir()
                default_css_path = os.path.join(package_resources_dir, "defaults.css")
                
                if os.path.exists(default_css_path):
                    shutil.copy2(default_css_path, app_css_path)
                    self.logger.info(f"Copied default CSS: {default_css_path} -> {app_css_path}")
                else:
                    # If defaults.css doesn't exist, create a minimal CSS file
                    self._create_minimal_css(app_css_path)
                    self.logger.info(f"Created minimal CSS: {app_css_path}")
                    
            except Exception as e:
                # Fall back to creating minimal CSS
                self.logger.warning(f"Could not copy default CSS, creating minimal CSS: {e}")
                self._create_minimal_css(app_css_path)
        
        # Verify the CSS copy
        if not os.path.exists(app_css_path):
            raise InstallerError(f"Failed to copy CSS to: {app_css_path}")
    
    def _create_minimal_css(self, css_path: str) -> None:
        """Create a minimal CSS file for Markdown rendering."""
        minimal_css = """
/* Minimal CSS for Mac-letterhead Markdown rendering */
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    font-size: 12pt;
    line-height: 1.4;
    color: #000000;
    margin: 0;
    padding: 0;
}

h1, h2, h3, h4, h5, h6 {
    margin-top: 0.5em;
    margin-bottom: 0.3em;
    font-weight: bold;
}

p {
    margin-top: 0;
    margin-bottom: 0.5em;
}

ul, ol {
    margin-top: 0;
    margin-bottom: 0.5em;
    padding-left: 1.5em;
}

li {
    margin-bottom: 0.2em;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 1em;
}

th, td {
    border: 1px solid #ccc;
    padding: 0.3em 0.5em;
    text-align: left;
}

th {
    background-color: #f5f5f5;
    font-weight: bold;
}

code {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.9em;
    background-color: #f5f5f5;
    padding: 0.1em 0.3em;
    border-radius: 3px;
}

blockquote {
    margin: 0.5em 0;
    padding-left: 1em;
    border-left: 3px solid #ccc;
    color: #666;
}
"""
        
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(minimal_css.strip())
    
    def _copy_icons(self, resources_dir: str) -> None:
        """Copy application icons to app resources."""
        try:
            # Find the icons in the package resources
            package_resources_dir = self._get_package_resources_dir()
            
            # Copy Mac-letterhead.icns directly (referenced by Info.plist)
            self._copy_icon_if_exists(
                package_resources_dir, 
                resources_dir, 
                "Mac-letterhead.icns", 
                "Mac-letterhead.icns"
            )
            
            # Copy main application icon (legacy support)
            self._copy_icon_if_exists(
                package_resources_dir, 
                resources_dir, 
                "Mac-letterhead.icns", 
                "applet.icns"
            )
            
            # Also copy as droplet icon for drag-and-drop (legacy support)
            self._copy_icon_if_exists(
                package_resources_dir, 
                resources_dir, 
                "Mac-letterhead.icns", 
                "droplet.icns"
            )
            
            # Copy PNG icon if available
            self._copy_icon_if_exists(
                package_resources_dir, 
                resources_dir, 
                "icon.png", 
                "icon.png"
            )
            
        except Exception as e:
            # Don't fail the entire installation for icon issues
            self.logger.warning(f"Could not copy icons: {e}")
    
    def _get_package_resources_dir(self) -> str:
        """Get the path to the package resources directory."""
        # Find the resources directory relative to this module
        current_dir = os.path.dirname(os.path.abspath(__file__))
        package_dir = os.path.dirname(current_dir)  # letterhead_pdf/
        resources_dir = os.path.join(package_dir, "resources")
        
        if not os.path.exists(resources_dir):
            raise InstallerError(f"Package resources directory not found: {resources_dir}")
        
        return resources_dir
    
    def _copy_icon_if_exists(
        self, 
        source_dir: str, 
        dest_dir: str, 
        source_name: str, 
        dest_name: str
    ) -> None:
        """Copy an icon file if it exists."""
        source_path = os.path.join(source_dir, source_name)
        if os.path.exists(source_path):
            dest_path = os.path.join(dest_dir, dest_name)
            shutil.copy2(source_path, dest_path)
            # Ensure proper permissions for macOS icon system
            os.chmod(dest_path, 0o644)
            self.logger.info(f"Copied icon: {source_name} -> {dest_name}")
        else:
            self.logger.warning(f"Icon not found: {source_path}")
    
    def validate_letterhead(self, letterhead_path: str) -> bool:
        """
        Validate a letterhead file.
        
        Args:
            letterhead_path: Path to the letterhead file
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            abs_path = os.path.abspath(letterhead_path)
            
            # Check if file exists
            if not os.path.exists(abs_path):
                self.logger.error(f"Letterhead file not found: {abs_path}")
                return False
            
            # Check if it's a PDF
            if not abs_path.lower().endswith('.pdf'):
                self.logger.error(f"Letterhead must be a PDF file: {abs_path}")
                return False
            
            # Check if file is readable
            try:
                with open(abs_path, 'rb') as f:
                    # Read first few bytes to check PDF signature
                    header = f.read(4)
                    if header != b'%PDF':
                        self.logger.error(f"File is not a valid PDF: {abs_path}")
                        return False
            except Exception as e:
                self.logger.error(f"Cannot read letterhead file: {abs_path} - {e}")
                return False
            
            # Check file size (should be reasonable)
            file_size = os.path.getsize(abs_path)
            if file_size == 0:
                self.logger.error(f"Letterhead file is empty: {abs_path}")
                return False
            
            if file_size > 100 * 1024 * 1024:  # 100MB limit
                self.logger.warning(f"Letterhead file is very large ({file_size} bytes): {abs_path}")
            
            self.logger.info(f"Letterhead validation passed: {abs_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating letterhead: {e}")
            return False
    
    def _create_dev_mode_marker(self, resources_dir: str, python_path: str = None) -> None:
        """Create a development mode marker file with python path."""
        dev_mode_path = os.path.join(resources_dir, "dev_mode")
        
        # Use provided python_path or detect current python interpreter
        if python_path is None:
            import sys
            python_path = sys.executable
        
        try:
            with open(dev_mode_path, 'w', encoding='utf-8') as f:
                f.write(python_path)
            
            self.logger.info(f"Created dev_mode marker: {dev_mode_path} (python: {python_path})")
            
        except Exception as e:
            self.logger.warning(f"Could not create dev_mode marker: {e}")
    
    def get_letterhead_from_app(self, app_path: str) -> Optional[str]:
        """
        Get the letterhead file path from an existing app bundle.
        
        Args:
            app_path: Path to the app bundle
            
        Returns:
            str: Path to the letterhead file, or None if not found
        """
        letterhead_path = os.path.join(app_path, "Contents", "Resources", "letterhead.pdf")
        if os.path.exists(letterhead_path):
            return letterhead_path
        return None
