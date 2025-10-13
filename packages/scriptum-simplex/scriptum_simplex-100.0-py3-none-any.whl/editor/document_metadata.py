"""
Document metadata management for Scriptum Simplex.

This module handles loading and saving document-specific metadata from TOML files.
Metadata files are named <document_name>.meta.toml and stored alongside the markdown file.
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import tomli  # For reading TOML (Python 3.11+)
    import tomli_w  # For writing TOML
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False
    logging.warning("TOML libraries not available. Install tomli and tomli_w for metadata support.")


class DocumentMetadata:
    """
    Manages document-specific metadata stored in TOML files.
    
    Metadata includes:
    - Image root path for resolving relative image paths
    - Export settings (theme, page size, etc.)
    - Document information (title, author, etc.)
    - Editor preferences (display theme, etc.)
    """
    
    def __init__(self, markdown_file_path: Optional[str] = None):
        """
        Initialize metadata manager.
        
        Args:
            markdown_file_path: Path to the markdown file (optional)
        """
        self.markdown_file_path = markdown_file_path
        self.metadata: Dict[str, Any] = self._get_default_metadata()
        
        if markdown_file_path and TOML_AVAILABLE:
            self.load()
    
    def _get_default_metadata(self) -> Dict[str, Any]:
        """
        Get default metadata structure.
        
        Returns:
            Dictionary with default metadata values
        """
        return {
            'document': {
                'title': '',
                'author_first_name': '',
                'author_last_name': '',
                'organization': '',
                'summary': '',
                'url': '',
                'license': '',
                'original_publication_date': '',
                'last_publication_date': '',
            },
            'revision_history': [],  # List of {date, version, description}
            'images': {
                'root_path': '',  # Empty means use document directory
            },
            'export': {
                'theme': 'default',
                'include_toc': False,
                'page_size': 'A4',
            },
            'editor': {
                'display_theme': 'default',
            }
        }
    
    def get_metadata_file_path(self) -> Optional[str]:
        """
        Get the path to the metadata file for the current document.
        
        Returns:
            Path to .meta.toml file, or None if no markdown file is set
        """
        if not self.markdown_file_path:
            return None
        
        # Get the base name without extension
        base_path = Path(self.markdown_file_path)
        metadata_path = base_path.parent / f"{base_path.stem}.meta.toml"
        return str(metadata_path)
    
    def load(self) -> bool:
        """
        Load metadata from the .meta.toml file.
        
        Returns:
            True if metadata was loaded successfully, False otherwise
        """
        if not TOML_AVAILABLE:
            logging.warning("TOML libraries not available")
            return False
        
        metadata_path = self.get_metadata_file_path()
        if not metadata_path or not os.path.exists(metadata_path):
            logging.info(f"No metadata file found at {metadata_path}")
            return False
        
        try:
            with open(metadata_path, 'rb') as f:
                loaded_metadata = tomli.load(f)
            
            # Merge loaded metadata with defaults (to handle missing keys)
            self._merge_metadata(loaded_metadata)
            
            logging.info(f"Loaded metadata from {metadata_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error loading metadata: {e}")
            return False
    
    def save(self) -> bool:
        """
        Save metadata to the .meta.toml file.
        
        Returns:
            True if metadata was saved successfully, False otherwise
        """
        if not TOML_AVAILABLE:
            logging.warning("TOML libraries not available")
            return False
        
        metadata_path = self.get_metadata_file_path()
        if not metadata_path:
            logging.warning("No markdown file path set, cannot save metadata")
            return False
        
        try:
            with open(metadata_path, 'wb') as f:
                tomli_w.dump(self.metadata, f)
            
            logging.info(f"Saved metadata to {metadata_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving metadata: {e}")
            return False
    
    def _merge_metadata(self, loaded: Dict[str, Any]) -> None:
        """
        Merge loaded metadata with defaults.
        
        Args:
            loaded: Loaded metadata dictionary
        """
        for section, values in loaded.items():
            if section in self.metadata:
                if isinstance(values, dict):
                    self.metadata[section].update(values)
                else:
                    self.metadata[section] = values
            else:
                self.metadata[section] = values
    
    def get_image_root_path(self) -> str:
        """
        Get the root path for resolving relative image paths.
        
        Returns:
            Absolute path to image root directory
        """
        root_path = self.metadata['images']['root_path']
        
        # If no root path is set, use the document's directory
        if not root_path and self.markdown_file_path:
            return str(Path(self.markdown_file_path).parent)
        
        # If root path is relative, make it absolute relative to document
        if root_path and not os.path.isabs(root_path) and self.markdown_file_path:
            doc_dir = Path(self.markdown_file_path).parent
            return str(doc_dir / root_path)
        
        # Return as-is if absolute or no document path
        return root_path or ''
    
    def resolve_image_path(self, image_path: str) -> str:
        """
        Resolve an image path to an absolute path.
        
        Args:
            image_path: Image path from markdown (can be relative or absolute)
            
        Returns:
            Absolute path to the image file
        """
        # If already absolute, return as-is
        if os.path.isabs(image_path):
            return image_path
        
        # Get the image root path
        root_path = self.get_image_root_path()
        
        if root_path:
            # Resolve relative to image root
            resolved = os.path.join(root_path, image_path)
            return os.path.abspath(resolved)
        
        # Fallback: return as-is
        return image_path
    
    def set_image_root_path(self, path: str) -> None:
        """
        Set the image root path.
        
        Args:
            path: Path to set as image root (can be relative or absolute)
        """
        self.metadata['images']['root_path'] = path
    
    def get_export_theme(self) -> str:
        """Get the theme for PDF export."""
        return self.metadata['export']['theme']
    
    def set_export_theme(self, theme: str) -> None:
        """Set the theme for PDF export."""
        self.metadata['export']['theme'] = theme
    
    def get_display_theme(self) -> str:
        """Get the theme for editor display."""
        return self.metadata['editor']['display_theme']
    
    def set_display_theme(self, theme: str) -> None:
        """Set the theme for editor display."""
        self.metadata['editor']['display_theme'] = theme
    
    def get_document_title(self) -> str:
        """Get the document title."""
        return self.metadata['document']['title']
    
    def set_document_title(self, title: str) -> None:
        """Set the document title."""
        self.metadata['document']['title'] = title
    
    def get_author_first_name(self) -> str:
        """Get the author's first name."""
        return self.metadata['document'].get('author_first_name', '')
    
    def set_author_first_name(self, name: str) -> None:
        """Set the author's first name."""
        self.metadata['document']['author_first_name'] = name
    
    def get_author_last_name(self) -> str:
        """Get the author's last name."""
        return self.metadata['document'].get('author_last_name', '')
    
    def set_author_last_name(self, name: str) -> None:
        """Set the author's last name."""
        self.metadata['document']['author_last_name'] = name
    
    def get_organization(self) -> str:
        """Get the organization name."""
        return self.metadata['document'].get('organization', '')
    
    def set_organization(self, org: str) -> None:
        """Set the organization name."""
        self.metadata['document']['organization'] = org
    
    def get_summary(self) -> str:
        """Get the document summary."""
        return self.metadata['document'].get('summary', '')
    
    def set_summary(self, summary: str) -> None:
        """Set the document summary."""
        self.metadata['document']['summary'] = summary
    
    def get_url(self) -> str:
        """Get the document URL."""
        return self.metadata['document'].get('url', '')
    
    def set_url(self, url: str) -> None:
        """Set the document URL."""
        self.metadata['document']['url'] = url
    
    def get_license(self) -> str:
        """Get the document license."""
        return self.metadata['document'].get('license', '')
    
    def set_license(self, license: str) -> None:
        """Set the document license."""
        self.metadata['document']['license'] = license
    
    def get_original_publication_date(self) -> str:
        """Get the original publication date."""
        return self.metadata['document'].get('original_publication_date', '')
    
    def set_original_publication_date(self, date: str) -> None:
        """Set the original publication date."""
        self.metadata['document']['original_publication_date'] = date
    
    def get_last_publication_date(self) -> str:
        """Get the last publication date."""
        return self.metadata['document'].get('last_publication_date', '')
    
    def set_last_publication_date(self, date: str) -> None:
        """Set the last publication date."""
        self.metadata['document']['last_publication_date'] = date
    
    def get_revision_history(self) -> list:
        """Get the revision history."""
        return self.metadata.get('revision_history', [])
    
    def add_revision(self, date: str, version: str, description: str) -> None:
        """Add a revision to the history."""
        if 'revision_history' not in self.metadata:
            self.metadata['revision_history'] = []
        self.metadata['revision_history'].append({
            'date': date,
            'version': version,
            'description': description
        })
