import collections.abc
import os.path
import enum
import pathlib
from typing import Any, Iterable

import defusedxml.ElementTree as ET
from pydelica.exception import UnknownOptionError


class Solver(str, enum.Enum):
    """[Deprecated]"""
    DASSL = "dassl"
    EULER = "euler"
    RUNGE_KUTTA = "rungekutta"


class OutputFormat(str, enum.Enum):
    """[Deprecated]"""
    CSV = "csv"
    MAT = "mat"
    PLT = "plt"


class SimulationOptions(collections.abc.MutableMapping):
    """
    Simulation Options
    ------------------

    Object contains configuration settings for simulation within Modelica
    """

    def __init__(self, xml_model_file: pathlib.Path) -> None:
        """Create a configuration object from a given model XML file

        Parameters
        ----------
        xml_model_file : pathlib.Path
            file containing the parameters and configurations from a model
            after compilation

        Raises
        ------
        FileNotFoundError
            if the specified XML file does not exist
        """
        self._model_xml = xml_model_file

        if not os.path.exists(xml_model_file):
            raise FileNotFoundError(
                "Could not extract simulation options, "
                f"no such file '{xml_model_file}"
            )

        _xml_obj = ET.parse(xml_model_file)

        self._opts = list(_xml_obj.iterfind("DefaultExperiment"))[0].attrib

    def _write_opts(self) -> None:
        _xml_obj = ET.parse(self._model_xml)

        for opt in _xml_obj.findall("DefaultExperiment")[0].attrib:
            _xml_obj.findall("DefaultExperiment")[0].attrib[opt] = str(self._opts[opt])

        _xml_obj.write(self._model_xml)

    def __setitem__(self, key: str, value: Any) -> None:
        self._opts[key] = value
        self._write_opts()

    def __getitem__(self, key: str) -> Any:
        return self._opts[key]

    def __delitem__(self, key: str) -> None:
        del self._opts[key]

    def set_option(self, option_name: str, value: Any) -> None:
        """Set the value of an option

        Parameters
        ----------
        option_name : str
            name of option to update
        value : Any
            new value for option

        Raises
        ------
        UnknownOptionError
            if the option does not exist
        """
        if option_name not in self._opts:
            raise UnknownOptionError(option_name)
        _opt = [i for i in self._opts.keys() if i.lower() == option_name.lower()][0]
        self._opts[_opt] = value
        self._write_opts()

    def __len__(self) -> int:
        return len(self._opts)

    def __iter__(self) -> Iterable:
        return iter(self._opts)