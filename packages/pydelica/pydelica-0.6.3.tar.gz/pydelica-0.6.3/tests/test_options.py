import pytest
import os.path
import glob

from pydelica.options import LibrarySetup


@pytest.mark.session
def test_use_library():
    with LibrarySetup() as library:
        library.use_library("Modelica", "3.2.3")
        _lib_dir = library.session_library
        assert glob.glob(os.path.join(_lib_dir, "Modelica 3.2.3*"))
        assert not glob.glob(os.path.join(_lib_dir, "Modelica 4.0.0*"))
        library.use_library("Modelica", "4.0.0")
        assert glob.glob(os.path.join(_lib_dir, "Modelica 4.0.0*"))
        assert not glob.glob(os.path.join(_lib_dir, "Modelica 3.2.3*"))
