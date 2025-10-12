import glob
import logging
import os
import platform
import re
import shutil
import tempfile

from pydelica.exception import UnknownLibraryError


class LibrarySetup:
    """Object containing setup for a particular Modelica library version"""

    def __init__(self) -> None:
        """Create a setup object

        Parameters
        ----------
        library_folder : str, optional
            specify location of the Modelica libraries, else use system defaults
        """
        self._logger = logging.getLogger("PyDelica.LibrarySetup")
        self._libraries = []
        self._session_library = None
        self._libraries = self._get_system_libraries()

    def __enter__(self) -> "LibrarySetup":
        return self

    def __exit__(self, *_, **__) -> None:
        if self._session_library:
            shutil.rmtree(self._session_library)

    def use_library(self, name: str, version: str, directory: str = "") -> None:
        """Use a specific library version

        This function looks through all library directories (symlinks) and
        checks which match the requested library. The version number of the
        directory is then compared to requested version and is symlinked
        (or copied if Windows), other versions are unlinked (or removed).

        Parameters
        ----------
        name : str
            library to select
        version : str
            version requested
        directory : str, optional
            alternative directory containing library

        Raises
        ------
        UnknownLibraryError
            if the library and version are not recognised
        """
        _test_str = f"{name} {version}"
        self._logger.debug(f"Selecting Library '{_test_str}'")

        if all(_test_str not in i for i in self._libraries):
            raise UnknownLibraryError(
                f"Cannot import library '{name}' version '{version}', "
                "library not found."
            )

        if directory:
            _libraries = glob.glob(os.path.join(directory, "*"))
        else:
            _libraries = self._libraries

        if not self._session_library:
            self._session_library = tempfile.mkdtemp()

        for library in _libraries:
            # If library does not contain requested library name ignore
            # and continue
            if name.lower() not in library.lower():
                continue

            # Create the address for the symlink/destination
            _new_lib = os.path.join(self._session_library, os.path.basename(library))

            # if no space in library filename then assume no version number
            if " " not in os.path.basename(library):
                continue

            _name, _info = os.path.basename(library).split()

            # If the split name is length 1 this means there is no
            # version string anyway
            if not (_version_re_search := re.findall(r"[0-9]+\.[0-9]+\.[0-9]+", _info)):
                continue

            _version: str = _version_re_search[0]

            # Check that the name matches the requested library name
            if name.lower().strip() == _name.lower().strip():
                # Check the version matches the requested version
                # if it does ensure this is symlinked/copied,
                # if not unlink/remove it
                if version.lower().strip() == _version.lower().strip():
                    if not os.path.exists(_new_lib):
                        if platform.system() != "Windows":
                            self._logger.debug(f"Linking: {library} -> {_new_lib}")
                            os.symlink(library, _new_lib)
                        elif os.path.isdir(library):
                            # Libraries are directories in Windows
                            self._logger.debug(f"Copying: {library} -> {_new_lib}")
                            shutil.copytree(library, _new_lib, symlinks=True)
                        else:
                            # Libraries are directories in Windows
                            self._logger.debug(f"Copying: {library} -> {_new_lib}")
                            shutil.copyfile(library, _new_lib)
                elif os.path.exists(_new_lib):
                    if platform.system() != "Windows":
                        self._logger.debug(f"Unlinking: {_new_lib} -> {library}")
                        os.unlink(_new_lib)
                    else:
                        self._logger.debug(f"Removing: {_new_lib}")
                        # Libraries are directories in Windows
                        if os.path.isdir(_new_lib):
                            shutil.rmtree(_new_lib)
                        else:
                            os.remove(_new_lib)

    @property
    def session_library(self) -> str | None:
        return self._session_library

    def _get_system_libraries(self) -> list[str]:
        if "MODELICAPATH" in os.environ:
            _library_dirs = os.environ["MODELICAPATH"].split(os.pathsep)
            _libs = []
            for library_dir in _library_dirs:
                _libs += glob.glob(os.path.join(library_dir, "*"))
        elif platform.system() == "Windows":
            _home = os.environ["USERPROFILE"]
            _user_libraries = os.path.join(
                _home, "AppData", "Roaming", ".openmodelica", "libraries"
            )
            _library_dir = os.path.join(
                os.environ["OPENMODELICAHOME"], "lib", "omlibrary"
            )
            _libs = glob.glob(os.path.join(_user_libraries, "*"))
            _libs += glob.glob(os.path.join(_library_dir, "*"))
        else:
            # Try typical linux locations
            _library_dirs = [
                "/usr/lib/omlibrary",
                f"{os.environ['HOME']}/.openmodelica/libraries",
            ]
            _libs = []
            for library_dir in _library_dirs:
                _libs += glob.glob(os.path.join(library_dir, "*"))
        return _libs
