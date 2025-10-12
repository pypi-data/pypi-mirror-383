from pydelica.exception import ResultRetrievalError
import pandas as pd
import pathlib
import logging


class SolutionHandler:
    """Stores solutions extracted from a Modelica simulation"""

    def __init__(self, session_directory: str) -> None:
        """Extract solution information from a given session directory

        Parameters
        ----------
        session_directory : str
            directory from a simulation session
        """
        self._logger = logging.getLogger("PyDelica.Solutions")
        self._session_dir = session_directory
        self._solutions: dict[str, pd.DataFrame] = {}

    def retrieve_session_solutions(
        self, run_directory: pathlib.Path
    ) -> dict[str, pd.DataFrame]:
        """Retrieve any stored solutions

        Parameters
        ----------
        run_directory: pathlib.Path
            directory containing run outputs

        Returns
        -------
        dict[str, pd.DataFrame]
            solutions extracted from valid results files

        Raises
        ------
        ResultRetrievalError
            If no CSV result files were found within the session directory
        """
        _has_csv = run_directory.glob("*_res.csv")

        if not _has_csv:
            raise ResultRetrievalError

        for out_file in _has_csv:
            self._logger.debug("Reading results from output file '%s'", out_file)
            _key = f"{out_file}".split("_res")[0]
            self._solutions[_key] = pd.read_csv(out_file)
        return self._solutions

    def get_solutions(self) -> dict[str, pd.DataFrame]:
        return self._solutions
