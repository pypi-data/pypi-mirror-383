import os
import pprint
import logging
import pathlib

import pytest
import pandas

import pydelica.exception as pde
from pydelica import Session
from pydelica.model import Model


@pytest.fixture
def pydelica_session():
    _sfode_src = pathlib.Path(__file__).parent.joinpath("models", "SineCurrentMSL4.mo")
    with Session(log_level=logging.DEBUG) as _session:
        _session.build_model(_sfode_src)
        _session.get_runtime_options().LOG_DEBUG = True
        yield _session


@pytest.mark.session
def test_build_with_c_source(pydelica_session: Session):
    _util_src = pathlib.Path(__file__).parent.joinpath("models", "Utilities.mo")
    _c_source_dir = pathlib.Path(__file__).parent.joinpath("c_sources")
    pydelica_session.build_model(
        _util_src, c_source_dir=_c_source_dir, model_addr="Utilities.test"
    )


@pytest.mark.session
def test_get_binary_loc(pydelica_session: Session):
    assert pydelica_session.get_binary_location("SineCurrentModel")


@pytest.mark.session
def test_get_parameters(pydelica_session: Session):
    _params = pydelica_session.get_parameters()
    pprint.pprint(_params)
    assert _params


@pytest.mark.session
def test_get_single_parameter(pydelica_session: Session):
    assert pydelica_session.get_parameter("resistor.T_ref") == 300.15


@pytest.mark.session
def test_get_simopts(pydelica_session: Session):
    _opts = pydelica_session.get_simulation_options()
    pprint.pprint(_opts._opts)
    assert _opts._opts


@pytest.mark.session
def test_get_runopts(pydelica_session: Session):
    _opts = pydelica_session.get_runtime_options()
    pprint.pprint(_opts.model_dump())
    assert _opts.model_dump()


@pytest.mark.session
def test_get_option(pydelica_session: Session):
    assert pydelica_session.get_simulation_option("solver") == "dassl"


@pytest.mark.session
def test_set_parameter(pydelica_session: Session):
    pydelica_session.set_parameter("resistor.alpha", 0.2)
    pydelica_session.set_parameter("sineCurrent.I", 0.0)
    pydelica_session._model_parameters["SineCurrentModel"].write_params()
    with Session() as _other_session:
        _xml = pydelica_session._model_parameters["SineCurrentModel"]._model_xml
        _other_session._model_parameters["SineCurrentModel"] = Model(pathlib.Path(), _xml)
        assert _other_session.get_parameter("resistor.alpha") == 0.2
        assert _other_session.get_parameter("sineCurrent.I") == 0.0


@pytest.mark.session
def test_simulation(pydelica_session: Session):
    import json
    import numpy.testing
    pydelica_session.simulate()
    data_frame = pydelica_session.get_solutions().get("SineCurrentModel")
    assert isinstance(data_frame, pandas.DataFrame)
    df_dict = data_frame.to_dict()
    with open(os.path.join(os.path.dirname(__file__), "data", "test_simulation_results.json")) as in_f:
        other = json.load(in_f)
    
    for column in df_dict.keys():
        _arr_1 = numpy.array(list(df_dict[column].values()))
        _arr_2 = numpy.array(list(other[column].values()))
        numpy.testing.assert_array_almost_equal(_arr_1, _arr_2)

@pytest.mark.session
def test_terminate_on_assertion_never(pydelica_session: Session):
    pydelica_session.fail_on_assert_level("never")
    pydelica_session.set_parameter("resistor.alpha", 0)
    pydelica_session.simulate()
    pydelica_session.set_parameter("resistor.alpha", 0.1)
    pydelica_session.fail_on_assert_level("error")


@pytest.mark.session
def test_terminate_on_assertion_error(pydelica_session: Session):
    pydelica_session.set_parameter("resistor.alpha", -1)
    with pytest.raises(pde.OMAssertionError):
        pydelica_session.simulate()
    pydelica_session.set_parameter("resistor.alpha", 1.2)
    pydelica_session.simulate()
    pydelica_session.set_parameter("resistor.alpha", 0.1)


@pytest.mark.session
def test_terminate_on_assertion_warning(pydelica_session: Session):
    pydelica_session.fail_on_assert_level("warning")
    pydelica_session.set_parameter("resistor.alpha", 1.2)
    with pytest.raises(pde.OMAssertionError):
        pydelica_session.simulate()
    pydelica_session.set_parameter("resistor.alpha", 0.1)
    pydelica_session.fail_on_assert_level("error")


@pytest.mark.session
def test_run_with_runopts(pydelica_session: Session):
    _run_time_opts = pydelica_session.get_runtime_options()
    
    # Sanity check just to make sure when we retrieve the options we get
    # a reference as opposed to copy
    assert id(_run_time_opts) == id(pydelica_session.get_runtime_options())
    
    _run_time_opts.abortSlowSimulation = True
    _run_time_opts.cpu = True
    pydelica_session.simulate()
