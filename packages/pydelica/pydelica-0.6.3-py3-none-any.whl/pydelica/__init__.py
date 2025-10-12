import json
import logging
import os
import pydantic
import platform
import subprocess
import tempfile
import warnings
import typing
import pathlib

import pandas

import pydelica.exception as pde
from pydelica.compiler import Compiler
from pydelica.logger import OMLogLevel
from pydelica.model import Model
from pydelica.options import SimulationOptions, Solver, OutputFormat, RuntimeOptions
from pydelica.solutions import SolutionHandler


class Session:
    @pydantic.validate_call
    def __init__(self, log_level: OMLogLevel | int | str = logging.INFO) -> None:
        """Session object which handles model runs.

        This class is used to initiate model runs, building the models and
        allowing the user to set parameter values etc.

        Parameters
        ----------
        log_level : OMLogLevel | str | int, optional
            level of Modelica logging, by default logging.INFO
            (use of OMLogLevel will be deprecated in v0.7.0)
        """
        self._solutions: dict[str, SolutionHandler] = {}
        self._model_parameters: dict[str, Model] = {}
        self._simulation_opts: dict[str, SimulationOptions] = {}
        self._runtime_opts: dict[str, RuntimeOptions] = {}
        self._current_profile: dict | None = None
        self._current_info: dict | None = None
        self._binaries: dict[str, pathlib.Path] = {}
        self._custom_libraries: list[dict[str, str]] = []
        self._logger: logging.Logger = logging.getLogger("PyDelica")
        if log_level == OMLogLevel.DEBUG:
            warnings.warn(
                "DeprecationNotice: Use of 'OMLogLevel' for log level settings will be deprecated in v0.7.0, "
                "please use Session.get_run_options.log_level to enabled/disable log flags"
            )
            self._logger.setLevel(logging.DEBUG)
        elif isinstance(log_level, (int, str)):
            self._logger.setLevel(log_level)
        self._compiler = Compiler()
        self._log_level = log_level
        self._session_directory = os.getcwd()
        self._assert_fail_level = "error"

    def __enter__(self):
        return self

    def __exit__(self, *_, **__):
        self._compiler.clear_cache()

    @pydantic.validate_call
    def use_libraries(self, library_specs: list[dict[str, str]]) -> None:
        """Use a Modelica library specification list

        Parameters
        ----------
        libary_specs : list[dict[str, str]]
            list of dictionaries containing version and location info of libraries
        """
        self._custom_libraries = library_specs

    @pydantic.validate_call
    def use_library(
        self,
        library_name: str,
        library_version: str | None = None,
        library_directory: str | None = None,
    ) -> None:
        """Specify version of a library to use

        Parameters
        ----------
        library_name : str
            name of the Modelica library
        library_version : str, optional
            semantic version number, by default latest
        library_directory : str, optional
            location of library on system, by default OM default paths
        """
        self._custom_libraries.append(
            {
                "name": library_name,
                "version": library_version or "",
                "directory": library_directory or "",
            }
        )

    @pydantic.validate_call
    def fail_on_assert_level(
        self, assert_level: typing.Literal["info", "warning", "error", "debug", "never"]
    ) -> None:
        """Change assertion level on which model execution should fail

        By default Modelica model simulation will only fail if an assertion
        of level 'error' is given. The possible values and rankings are:

        info < warning < error < never

        where 'never' will mean no exception is raised

        Parameters
        ----------
        assert_level : str
            new level of assertion to trigger failure
        """
        self._assert_fail_level = assert_level

    @property
    def code_profile(self) -> dict | None:
        return self._current_profile

    @property
    def code_info(self) -> dict | None:
        return self._current_info

    @property
    def default_model(self) -> str:
        return list(self._binaries.keys())[0]

    @pydantic.validate_call
    def _recover_profile(
        self, build_dir: pydantic.DirectoryPath, run_dir: pydantic.DirectoryPath
    ) -> None:
        """Recovers a profile file if one exists"""
        _prof_files = list(run_dir.glob("*_prof.json"))
        _info_files = list(build_dir.glob("*_info.json"))
        if _prof_files:
            self._current_profile = json.load(_prof_files[0].open())
        if _info_files:
            self._current_info = json.load(_info_files[0].open())

    @pydantic.validate_call
    def build_model(
        self,
        modelica_source_file: pydantic.FilePath,
        model_addr: str | None = None,
        extra_models: list[str] | None = None,
        c_source_dir: pydantic.DirectoryPath | None = None,
        profiling: (
            typing.Literal["none", "blocks", "all", "all_perf", "all_stat"] | None
        ) = None,
        update_input_paths_to: pydantic.DirectoryPath | None = None,
        omc_build_flags: dict[str, str | None] | None = None,
    ) -> None:
        """Build a Modelica model from a source file

        Parameters
        ----------
        modelica_source_file : str
            Modelica source file to compile
        model_addr : str, optional
            address of model within source file, else default
        extra_models : list[str], optional
            additional models required for compile, by default None
        c_source_dir : str, optional
            directory containing any additional required C sources, by default None
        profiling : Literal["none", "blocks", "all", "all_perf", "all_stat"], optional
            if set, activates the OMC profiling at the specified level
        update_input_paths_to : str, optional
            update input paths within model to another location, by default None
        omc_build_flags : dict[str, str | None], optional
            additional flags to pass to the OMC compiler

        Raises
        ------
        pde.ModelicaFileGenerationError
            if the XML parameter file was not generated
        RuntimeError
            If model compilation failed
        """
        if not omc_build_flags:
            omc_build_flags = {}

        self._logger.debug(
            "Building model %sfrom file '%s'",
            f"{model_addr} " if model_addr else "",
            modelica_source_file,
        )

        for flag, value in omc_build_flags.items():
            self._compiler.set_omc_flag(flag, value)

        self._compiler.set_profile_level(profiling)

        _binary_loc = self._compiler.compile(
            modelica_source_file=modelica_source_file,
            model_addr=model_addr,
            extra_models=extra_models,
            c_source_dir=c_source_dir,
            custom_library_spec=self._custom_libraries,
        )

        _xml_files = _binary_loc.glob("*.xml")

        if not _xml_files:
            raise pde.ModelicaFileGenerationError(
                "Failed to retrieve XML files from model compilation"
            )

        self._logger.debug("Parsing generated XML files")
        for xml_file in _xml_files:
            _model_name = os.path.basename(xml_file).split("_init")[0]
            self._model_parameters[_model_name] = Model(modelica_source_file, xml_file)

            _binary = _model_name

            if platform.system() == "Windows":
                _binary += ".exe"

            _binary_addr = _binary_loc.absolute().joinpath(_binary)

            # In later versions of OM the binary name cannot have '.' within the name
            if not os.path.exists(_binary_addr):
                if not (
                    (
                        _binary_addr := pathlib.Path(
                            f"{_binary_addr}".replace(".", "_", 1)
                        )
                    ).exists
                ):
                    raise RuntimeError(
                        f"Compilation of model '{_model_name}' failed, "
                        f"no binary for '{_model_name}' found."
                    )

            self._logger.debug("Located compiled binary '%s'", _binary_addr)

            self._binaries[_model_name] = _binary_addr
            self._solutions[_model_name] = SolutionHandler(self._session_directory)

            self._logger.debug(
                "Extracting default simulation options for model '%s' from XML file",
                _model_name,
            )

            self._simulation_opts[_model_name] = SimulationOptions(xml_file)
            self._runtime_opts[_model_name] = RuntimeOptions()

            # Option to update any variable recognised as an input
            # i.e. .mat/.csv to point to the correct location as an
            # absolute path
            if update_input_paths_to:
                self._set_input_files_directory(_model_name, update_input_paths_to)

            # Allows easy creation of a Pandas dataframe for displaying solutions
            self.set_output_format("csv")

    def _get_cache_key(self, model_name: str, member_dict: dict) -> str:
        """Retrieve Model Name in cache dictionary

        Retrieves model name as stored within the given dictionary. In some versions of OM
        '.' in the model name is replaced by '_' in the files.
        """
        if (_model_name := model_name) not in member_dict and (
            _model_name := model_name.replace(".", "_")
        ) not in member_dict:
            raise KeyError(f"Key '{model_name}' not found")
        return _model_name

    @pydantic.validate_call
    def get_binary_location(self, model_name: str) -> pathlib.Path:
        try:
            _model_name: str = self._get_cache_key(model_name, self._binaries)
        except KeyError as e:
            raise pde.BinaryNotFoundError(
                f"Failed to retrieve binary for model '{model_name}'"
            ) from e
        return self._binaries[_model_name]

    def get_parameters(
        self, model_name: str | None = None
    ) -> Model | dict[str, typing.Any]:
        """Retrieve a full parameter list

        Parameters
        ----------
        model_name : str, optional
            specify name of model to extract parameters, by default extract all

        Returns
        -------
        dict[str, typing.Any]
            dictionary containing parameters by name and their values
        """
        if model_name:
            try:
                _model_name: str = self._get_cache_key(
                    model_name, self._model_parameters
                )
            except KeyError as e:
                raise pde.UnknownModelError(model_name) from e

            return self._model_parameters[_model_name]
        else:
            _out_params: dict[str, typing.Any] = {}
            for model in self._model_parameters:
                for param in self._model_parameters[model]:
                    if param in _out_params:
                        continue
                    _out_params[param] = self._model_parameters[model][param]
        return _out_params

    @pydantic.validate_call
    def get_parameter(self, param_name: str) -> typing.Any:
        """Retrieve the value of a specific parameter

        Parameters
        ----------
        param_name : str
            name of parameter to retrieve

        Returns
        -------
        typing.Any
            the value of the parameter specified
        """
        for model in self._model_parameters:
            if param_name in (_model_params := self.get_parameters(model)):
                if isinstance(
                    _model_params,
                    dict,
                ):
                    raise AssertionError(
                        "Expected type 'Model' for parameter retrieval for model "
                        f"'{model}' but got type 'dict'"
                    )
                if isinstance(
                    _param := _model_params.get_parameter(param_name),
                    dict,
                ):
                    raise AssertionError(
                        "Expected non-mutable value for requested parameter"
                        f"'{param_name}' but got type 'dict'"
                    )
                return _param
        raise pde.UnknownParameterError(param_name)

    @pydantic.validate_call
    def get_simulation_options(
        self, model_name: str | None = None
    ) -> SimulationOptions:
        """Retrieve dictionary of the Simulation Options

        Parameters
        ----------
        model_name : str
            name of model to get simulation options for

        Returns
        -------
        SimulationOptions
            dictionary containing all simulation options

        Raises
        ------
        KeyError
            if the given model name is not recognised
        """
        if not model_name:
            model_name = self.default_model
        try:
            _model_name: str = self._get_cache_key(model_name, self._simulation_opts)
        except KeyError as e:
            raise pde.UnknownModelError(model_name) from e
        return self._simulation_opts[_model_name]

    @pydantic.validate_call
    def get_simulation_option(
        self, option: str, model_name: str | None = None
    ) -> typing.Any:
        """Retrieve a single option for a given model.

        Parameters
        ----------
        option : str
            option to search for
        model_name : str, optional
            name of modelica model

        Returns
        -------
        typing.Any
            value for the given option

        Raises
        ------
        KeyError
            if the given model is not recognised
        KeyError
            if the given option name is not recognised
        """
        if not model_name:
            return self._simulation_opts[self.default_model][option]
        model_name = self._get_cache_key(model_name, self._simulation_opts)
        return self._simulation_opts[model_name][option]

    @pydantic.validate_call
    def set_parameter(self, param_name: str, value: typing.Any) -> None:
        """Set a parameter to a given value

        Parameters
        ----------
        param_name : str
            name of model parameter to update
        value : typing.Any
            new value to assign to the given parameters
        """
        if isinstance(value, dict):
            raise TypeError(
                "Cannot assign a value of type dictionary as a parameter value"
                f" for parameter '{param_name}'"
            )
        self._logger.debug(
            "Searching for parameter '%s' and assigning new value", param_name
        )
        for model in self._model_parameters:
            if param_name in self._model_parameters[model]:
                self._model_parameters[model].set_parameter(param_name, value)
                return
        raise pde.UnknownParameterError(param_name)

    @pydantic.validate_call
    def get_runtime_options(self, model_name: str | None = None) -> RuntimeOptions:
        """Retrieve runtime options object for the given model

        Parameters
        ----------
        model_name : str
            name of model to get runtime options for

        Returns
        -------
        RuntimeOptions
            contains all runtime options

        Raises
        ------
        KeyError
            if the given model name is not recognised
        """
        if not model_name:
            model_name = self.default_model
        try:
            _model_name: str = self._get_cache_key(model_name, self._runtime_opts)
        except KeyError as e:
            raise pde.UnknownModelError(model_name) from e
        return self._runtime_opts[_model_name]

    def _set_input_files_directory(
        self, model_name: str, input_dir: pathlib.Path | None = None
    ) -> None:
        if not input_dir:
            input_dir = self._model_parameters[model_name].get_source_path().parent

        for param, value in self._model_parameters[model_name].items():
            if not value["value"]:
                continue

            _has_addr_elem = any(
                i in value["value"]
                for i in [os.path.sep, ".mat", ".csv"]
                if value["type"] == str
            )

            if value["type"] == str and _has_addr_elem:
                _addr = input_dir.joinpath(value["value"])
                self._model_parameters[model_name].set_parameter(param, f"{_addr}")

    @pydantic.validate_call
    def simulate(
        self, model_name: str | None = None, verbosity: OMLogLevel | None = None
    ) -> None:
        """Run simulation using the built models

        Parameters
        ----------
        model_name : str, optional
            Specify model to execute, by default use first in list
        verbosity : OMLogLevel, optional (Deprecated)
            specify level of Modelica outputs, else use default
        """
        if not model_name:
            model_name = self.default_model
            self._logger.warning(
                "No model name specified, using first result '%s'", model_name
            )
        try:
            _binary_loc: pathlib.Path = self.get_binary_location(model_name)
            _model_name: str = self._get_cache_key(model_name, self._model_parameters)
        except KeyError as e:
            raise pde.BinaryNotFoundError(
                f"Could not find binary for Model '{model_name}',"
                " did you run 'build_models' on the source file?"
            ) from e

        self._logger.debug("Launching simulation for model '%s'", model_name)

        # Write parameters to the XML file read by the binary
        self._model_parameters[_model_name].write_params()

        _binary_dir = _binary_loc.parent

        _env = os.environ.copy()

        # If the binary or library directories are not in PATH temporarily add them during
        # model execution in Windows
        if platform.system() == "Windows":
            self._append_locs_to_winpath(_env)
        _args: list[str] = [f"{_binary_loc}", f"-inputPath={_binary_dir}"]

        if not os.path.exists(_binary_loc):
            raise pde.BinaryNotFoundError(
                f"Failed to retrieve binary for model '{model_name}' "
                f"from location '{_binary_dir}'"
            )

        if verbosity and verbosity.value:
            _args += [verbosity.value]
        elif isinstance(self._log_level, OMLogLevel) and self._log_level.value:
            _args += [self._log_level.value]

        # Add any C runtime options
        # Model name is stored with XML file key ('.' -> '_')
        _model_name_key: str = model_name.replace(".", "_")
        _args += self._runtime_opts[_model_name_key].assemble_args()

        self._logger.debug("Executing simulation command: %s ", " ".join(_args))

        with tempfile.TemporaryDirectory() as run_dir:
            _run_path = pathlib.Path(run_dir)
            _run_sim = subprocess.run(
                _args,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                shell=False,
                cwd=_run_path,
                env=_env,
            )

            pde.parse_error_string_simulate(_run_sim.stdout, self._assert_fail_level)

            if _run_sim.returncode != 0:
                _print_msg = _run_sim.stderr or _run_sim.stdout
                if not _print_msg:
                    _print_msg = "Cause unknown, no error logs were found."
                raise pde.OMExecutionError(
                    f"[{_run_sim.returncode}] Simulation failed with: {_print_msg}"
                )

            self._solutions[_model_name].retrieve_session_solutions(_run_path)
            self._recover_profile(_binary_dir, _run_path)

    def _append_locs_to_winpath(self, _env: dict[str, typing.Any]) -> None:
        _om_home = os.environ["OPENMODELICAHOME"]
        _path: str = os.environ["PATH"]
        _separator: str = ";" if ";" in _path else ":"
        _path_entries: list[str] = os.environ["PATH"].split(_separator)

        _required: tuple[str, str] = (
            os.path.join(_om_home, "bin"),
            os.path.join(_om_home, "lib"),
        )

        for path in _required:
            if path not in _path_entries:
                _path_entries.append(path)

        _env["PATH"] = f"{_separator}".join(_path_entries)

    @pydantic.validate_call
    def set_output_format(
        self, format: OutputFormat | typing.Literal["csv", "mat", "plt"]
    ) -> None:
        if isinstance(format, OutputFormat):
            warnings.warn(
                "DeprecationNotice: Use of 'OutputFormat' for output format will be deprecated in v0.7.0, "
                "please use literal strings 'csv', 'mat' or 'plt'"
            )
            format = format.value

        for model in self._simulation_opts:
            self._simulation_opts[model].set_option("outputFormat", format)

    @pydantic.validate_call
    def set_solver(
        self,
        solver: Solver | typing.Literal["dassl", "euler", "rungekutta"],
        model_name: str | None = None,
    ) -> None:
        if isinstance(solver, Solver):
            warnings.warn(
                "DeprecationNotice: Use of 'Solver' for solver type will be deprecated in v0.7.0, "
                "please use literal strings 'euler', 'dassl' or 'rungekutta'"
            )
            solver = solver.value
        if model_name:
            _model_name: str = self._get_cache_key(model_name, self._simulation_opts)
            self._simulation_opts[_model_name].set_option("solver", solver)
        else:
            for model in self._simulation_opts:
                self._simulation_opts[model].set_option("solver", solver)

    @pydantic.validate_call
    def set_time_range(
        self,
        start_time: pydantic.NonNegativeInt | None = None,
        stop_time: pydantic.PositiveInt | None = None,
        model_name: str | None = None,
    ) -> None:
        if model_name:
            _model_name: str = self._get_cache_key(model_name, self._simulation_opts)
            if start_time:
                self._simulation_opts[_model_name].set_option("startTime", start_time)
            if stop_time:
                self._simulation_opts[_model_name].set_option("stopTime", stop_time)
        else:
            for model in self._simulation_opts:
                if start_time:
                    self._simulation_opts[model].set_option("startTime", start_time)
                if stop_time:
                    self._simulation_opts[model].set_option("stopTime", stop_time)

    @pydantic.validate_call
    def set_tolerance(
        self, tolerance: pydantic.PositiveFloat, model_name: str | None = None
    ) -> None:
        if model_name:
            _model_name: str = self._get_cache_key(model_name, self._simulation_opts)
            self._simulation_opts[_model_name].set_option("tolerance", tolerance)
        else:
            for model in self._simulation_opts:
                self._simulation_opts[model].set_option("tolerance", tolerance)

    @pydantic.validate_call
    def set_variable_filter(
        self, filter_str: str, model_name: str | None = None
    ) -> None:
        if model_name:
            _model_name: str = self._get_cache_key(model_name, self._simulation_opts)
            self._simulation_opts[_model_name].set_option("variableFilter", filter_str)
        else:
            for model in self._simulation_opts:
                self._simulation_opts[model].set_option("variableFilter", filter_str)

    @pydantic.validate_call
    def set_simulation_option(
        self, option_name: str, value: typing.Any, model_name: str | None = None
    ) -> None:
        if model_name:
            _model_name: str = self._get_cache_key(model_name, self._simulation_opts)
            self._simulation_opts[_model_name].set_option(option_name, value)
        else:
            for model in self._simulation_opts:
                self._simulation_opts[model].set_option(option_name, value)

    def get_solutions(self) -> dict[str, pandas.DataFrame]:
        """Returns solutions to all simulated models as a dictionary of dataframes

        Outputs are written as Pandas dataframes the columns of which can be
        accessed by variable name.

        Returns
        -------
        dict
            dictionary containing outputs to all simulated models as Pandas
            dataframes

        Raises
        ------
        pde.BinaryNotFoundError
            if no models have been compiled
        """
        if not self._binaries:
            raise pde.BinaryNotFoundError(
                "Cannot retrieve solutions, you need to compile and"
                " run one or more models first"
            )

        # The SolutionHandler class takes into account the case of multiple
        # output files, however with OM there is only ever a single file per
        # model so we only need to retrieve the first one

        return {
            model: self._solutions[model].get_solutions()[
                list(self._solutions[model].get_solutions().keys())[0]
            ]
            for model in self._solutions
        }
