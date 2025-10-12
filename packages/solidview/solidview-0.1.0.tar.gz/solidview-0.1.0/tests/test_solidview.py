"""
Test suite for SolidView package.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

try:
    from solid2 import cube, sphere
    SOLID2_AVAILABLE = True
except ImportError:
    SOLID2_AVAILABLE = False

from solidview import SolidViewer, view3d


class TestSolidViewer:
    """Test cases for SolidViewer class."""
    
    def test_init_without_openscad_path(self):
        """Test SolidViewer initialization without providing OpenSCAD path."""
        with patch.object(SolidViewer, '_find_openscad', return_value='/mock/openscad'):
            viewer = SolidViewer()
            assert viewer.openscad_exec == '/mock/openscad'
    
    def test_init_with_openscad_path(self):
        """Test SolidViewer initialization with custom OpenSCAD path."""
        custom_path = '/custom/openscad'
        viewer = SolidViewer(openscad_exec=custom_path)
        assert viewer.openscad_exec == custom_path
    
    @patch('platform.system')
    @patch('os.path.isfile')
    def test_find_openscad_windows(self, mock_isfile, mock_system):
        """Test OpenSCAD detection on Windows."""
        mock_system.return_value = 'Windows'
        mock_isfile.side_effect = lambda path: path == r"C:\Program Files\OpenSCAD\openscad.exe"
        
        viewer = SolidViewer()
        result = viewer._find_openscad()
        assert result == r"C:\Program Files\OpenSCAD\openscad.exe"
    
    @patch('platform.system')
    @patch('os.path.isfile')
    def test_find_openscad_macos(self, mock_isfile, mock_system):
        """Test OpenSCAD detection on macOS."""
        mock_system.return_value = 'Darwin'
        mock_isfile.side_effect = lambda path: path == "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
        
        viewer = SolidViewer()
        result = viewer._find_openscad()
        assert result == "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
    
    @patch('platform.system')
    @patch('os.path.isfile')
    @patch('shutil.which')
    def test_find_openscad_not_found(self, mock_which, mock_isfile, mock_system):
        """Test OpenSCAD detection when not found."""
        mock_system.return_value = 'Linux'
        mock_isfile.return_value = False
        mock_which.return_value = None
        
        viewer = SolidViewer()
        with pytest.raises(FileNotFoundError):
            viewer._find_openscad()
    
    def test_cleanup_files(self):
        """Test temporary file cleanup."""
        # Create temporary files
        temp_files = []
        for _ in range(2):
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_files.append(temp_file.name)
            temp_file.close()
        
        viewer = SolidViewer(openscad_exec='/mock/openscad')
        viewer._cleanup_files([f.name for f in temp_files])
        
        # Check that files are deleted
        for temp_file in temp_files:
            assert not os.path.exists(temp_file)
    
    @pytest.mark.skipif(not SOLID2_AVAILABLE, reason="SolidPython2 not available")
    @patch('solidview.viewer.process')
    @patch('solidview.viewer.view_stl')
    def test_view_success(self, mock_view_stl, mock_process):
        """Test successful object viewing."""
        mock_view_stl.return_value = "mock_result"
        
        viewer = SolidViewer(openscad_exec='/mock/openscad')
        obj = cube([10, 10, 10])
        
        result = viewer.view(obj, width=400, height=400)
        
        assert result == "mock_result"
        mock_process.assert_called_once()
        mock_view_stl.assert_called_once()
    
    @pytest.mark.skipif(not SOLID2_AVAILABLE, reason="SolidPython2 not available")
    @patch('solidview.viewer.process')
    def test_view_render_failure(self, mock_process):
        """Test object viewing when rendering fails."""
        mock_process.side_effect = Exception("Render failed")
        
        viewer = SolidViewer(openscad_exec='/mock/openscad')
        obj = cube([10, 10, 10])
        
        with pytest.raises(RuntimeError, match="Failed to render object"):
            viewer.view(obj)
    
    @pytest.mark.skipif(not SOLID2_AVAILABLE, reason="SolidPython2 not available")
    @patch('solidview.viewer.process')
    def test_save_stl_success(self, mock_process):
        """Test successful STL file saving."""
        output_path = "/tmp/test.stl"
        
        viewer = SolidViewer(openscad_exec='/mock/openscad')
        obj = cube([10, 10, 10])
        
        result = viewer.save_stl(obj, output_path)
        
        assert result == output_path
        mock_process.assert_called_once()
    
    @pytest.mark.skipif(not SOLID2_AVAILABLE, reason="SolidPython2 not available")
    def test_save_stl_file_exists(self):
        """Test STL saving when file already exists."""
        with tempfile.NamedTemporaryFile() as temp_file:
            viewer = SolidViewer(openscad_exec='/mock/openscad')
            obj = cube([10, 10, 10])
            
            with pytest.raises(FileExistsError):
                viewer.save_stl(obj, temp_file.name, overwrite=False)


class TestConvenienceFunction:
    """Test cases for the view3d convenience function."""
    
    @pytest.mark.skipif(not SOLID2_AVAILABLE, reason="SolidPython2 not available")
    @patch('solidview.SolidViewer')
    def test_view3d_creates_viewer(self, mock_viewer_class):
        """Test that view3d creates a SolidViewer instance."""
        mock_viewer = MagicMock()
        mock_viewer_class.return_value = mock_viewer
        
        obj = cube([10, 10, 10])
        view3d(obj, width=400, height=400)
        
        mock_viewer_class.assert_called_once_with(None)
        mock_viewer.view.assert_called_once_with(obj, 400, 400)
    
    @pytest.mark.skipif(not SOLID2_AVAILABLE, reason="SolidPython2 not available")
    @patch('solidview.SolidViewer')
    def test_view3d_reuses_viewer(self, mock_viewer_class):
        """Test that view3d reuses the same viewer instance."""
        mock_viewer = MagicMock()
        mock_viewer_class.return_value = mock_viewer
        
        obj = cube([10, 10, 10])
        
        # Call twice
        view3d(obj)
        view3d(obj)
        
        # Should only create viewer once
        mock_viewer_class.assert_called_once_with(None)
        assert mock_viewer.view.call_count == 2


class TestIntegration:
    """Integration tests (require actual dependencies)."""
    
    @pytest.mark.skipif(not SOLID2_AVAILABLE, reason="SolidPython2 not available")
    def test_object_to_scad_conversion(self):
        """Test that SolidPython2 objects can be converted to SCAD code."""
        obj = cube([10, 10, 10])
        scad_code = str(obj)
        
        # Basic check that it produces some SCAD-like code
        assert "cube" in scad_code.lower()
        assert "[10" in scad_code or "10" in scad_code