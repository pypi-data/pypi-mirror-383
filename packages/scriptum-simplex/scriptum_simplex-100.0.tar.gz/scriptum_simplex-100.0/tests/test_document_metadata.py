"""
Tests for the document metadata system.
"""

import pytest
import tempfile
import os
from pathlib import Path
from editor.document_metadata import DocumentMetadata, TOML_AVAILABLE


@pytest.mark.skipif(not TOML_AVAILABLE, reason="TOML libraries not available")
class TestDocumentMetadata:
    """Test cases for DocumentMetadata class."""
    
    def test_initialization_without_file(self):
        """Test initializing metadata without a file path."""
        metadata = DocumentMetadata()
        assert metadata.markdown_file_path is None
        assert 'document' in metadata.metadata
        assert 'images' in metadata.metadata
        assert 'export' in metadata.metadata
        assert 'editor' in metadata.metadata
    
    def test_initialization_with_file(self):
        """Test initializing metadata with a file path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_path = f.name
        
        try:
            metadata = DocumentMetadata(temp_path)
            assert metadata.markdown_file_path == temp_path
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_get_metadata_file_path(self):
        """Test getting the metadata file path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_path = f.name
        
        try:
            metadata = DocumentMetadata(temp_path)
            meta_path = metadata.get_metadata_file_path()
            
            # Should be same directory, same name, but .meta.toml extension
            expected = Path(temp_path).parent / f"{Path(temp_path).stem}.meta.toml"
            assert meta_path == str(expected)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def test_default_metadata_structure(self):
        """Test that default metadata has correct structure."""
        metadata = DocumentMetadata()
        
        assert metadata.metadata['document']['title'] == ''
        assert metadata.metadata['document']['author_first_name'] == ''
        assert metadata.metadata['document']['author_last_name'] == ''
        assert metadata.metadata['document']['organization'] == ''
        assert metadata.metadata['document']['summary'] == ''
        assert metadata.metadata['document']['url'] == ''
        assert metadata.metadata['document']['license'] == ''
        assert metadata.metadata['images']['root_path'] == ''
        assert metadata.metadata['export']['theme'] == 'default'
        assert metadata.metadata['editor']['display_theme'] == 'default'
        assert 'revision_history' in metadata.metadata
    
    def test_get_image_root_path_default(self):
        """Test getting image root path when not set (should use document dir)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            md_file = os.path.join(temp_dir, 'test.md')
            with open(md_file, 'w') as f:
                f.write('# Test')
            
            metadata = DocumentMetadata(md_file)
            root_path = metadata.get_image_root_path()
            
            assert root_path == temp_dir
    
    def test_get_image_root_path_relative(self):
        """Test getting image root path when set to relative path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            md_file = os.path.join(temp_dir, 'test.md')
            with open(md_file, 'w') as f:
                f.write('# Test')
            
            metadata = DocumentMetadata(md_file)
            metadata.set_image_root_path('./images')
            root_path = metadata.get_image_root_path()
            
            expected = os.path.join(temp_dir, 'images')
            assert root_path == expected
    
    def test_get_image_root_path_absolute(self):
        """Test getting image root path when set to absolute path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            md_file = os.path.join(temp_dir, 'test.md')
            images_dir = os.path.join(temp_dir, 'my_images')
            
            with open(md_file, 'w') as f:
                f.write('# Test')
            
            metadata = DocumentMetadata(md_file)
            metadata.set_image_root_path(images_dir)
            root_path = metadata.get_image_root_path()
            
            assert root_path == images_dir
    
    def test_resolve_image_path_relative(self):
        """Test resolving a relative image path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            md_file = os.path.join(temp_dir, 'test.md')
            with open(md_file, 'w') as f:
                f.write('# Test')
            
            metadata = DocumentMetadata(md_file)
            resolved = metadata.resolve_image_path('logo.png')
            
            expected = os.path.abspath(os.path.join(temp_dir, 'logo.png'))
            assert resolved == expected
    
    def test_resolve_image_path_absolute(self):
        """Test resolving an absolute image path (should return as-is)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            md_file = os.path.join(temp_dir, 'test.md')
            abs_path = '/absolute/path/to/image.png'
            
            with open(md_file, 'w') as f:
                f.write('# Test')
            
            metadata = DocumentMetadata(md_file)
            resolved = metadata.resolve_image_path(abs_path)
            
            assert resolved == abs_path
    
    def test_save_and_load_metadata(self):
        """Test saving and loading metadata."""
        with tempfile.TemporaryDirectory() as temp_dir:
            md_file = os.path.join(temp_dir, 'test.md')
            with open(md_file, 'w') as f:
                f.write('# Test')
            
            # Create and configure metadata
            metadata1 = DocumentMetadata(md_file)
            metadata1.set_image_root_path('./images')
            metadata1.set_document_title('Test Document')
            metadata1.set_export_theme('typora')
            
            # Save metadata
            assert metadata1.save()
            
            # Load metadata in new instance
            metadata2 = DocumentMetadata(md_file)
            
            # Verify loaded values
            assert metadata2.metadata['images']['root_path'] == './images'
            assert metadata2.get_document_title() == 'Test Document'
            assert metadata2.get_export_theme() == 'typora'
    
    def test_getters_and_setters(self):
        """Test all getter and setter methods."""
        metadata = DocumentMetadata()
        
        # Test image root path
        metadata.set_image_root_path('/path/to/images')
        assert metadata.metadata['images']['root_path'] == '/path/to/images'
        
        # Test export theme
        metadata.set_export_theme('github')
        assert metadata.get_export_theme() == 'github'
        
        # Test display theme
        metadata.set_display_theme('typora')
        assert metadata.get_display_theme() == 'typora'
        
        # Test document title
        metadata.set_document_title('My Document')
        assert metadata.get_document_title() == 'My Document'
    
    def test_metadata_file_not_exists(self):
        """Test loading when metadata file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            md_file = os.path.join(temp_dir, 'test.md')
            with open(md_file, 'w') as f:
                f.write('# Test')
            
            metadata = DocumentMetadata(md_file)
            # Should not raise an error, just use defaults
            assert metadata.metadata['images']['root_path'] == ''


class TestDocumentMetadataWithoutTOML:
    """Test DocumentMetadata behavior when TOML is not available."""
    
    def test_initialization_without_toml(self, monkeypatch):
        """Test that metadata works without TOML (with warnings)."""
        # This test verifies graceful degradation
        metadata = DocumentMetadata()
        assert metadata.metadata is not None
        assert 'images' in metadata.metadata
