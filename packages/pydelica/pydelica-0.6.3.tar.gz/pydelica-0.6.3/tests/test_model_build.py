import logging
import os

import pytest

from pydelica.compiler import Compiler
from pydelica.exception import OMExecutionError, OMParsingError

logging.getLogger("PyDelica").setLevel(logging.DEBUG)


@pytest.fixture(scope="module")
def compile_model_custom(modelica_environment):
    _sfode_src = os.path.join(os.path.dirname(__file__), "models", "SineCurrentMSL3.mo")
    _compiler = Compiler()
    return _compiler.compile(_sfode_src, custom_library_spec=modelica_environment)


@pytest.fixture(scope="module")
def compile_model_default():
    _sfode_src = os.path.join(os.path.dirname(__file__), "models", "SineCurrentMSL4.mo")
    _compiler = Compiler()
    return _compiler.compile(_sfode_src)


@pytest.mark.compilation
def test_binary_msl3(compile_model_custom):
    assert os.path.exists(compile_model_custom)


@pytest.mark.compilation
def test_binary_msl4(compile_model_default):
    assert os.path.exists(
        os.path.join(compile_model_default)
    )


@pytest.mark.compilation
def test_build_model_with_fail_messages():
    _banana_src = os.path.join(os.path.dirname(__file__), "models", "FailedInMessage.mo")
    _compiler = Compiler()
    _compiler.compile(_banana_src)


@pytest.mark.compilation
def test_failing_model():
    _fail_src = os.path.join(os.path.dirname(__file__), "models", "BuildFailModel.mo")
    _compiler = Compiler()
    with pytest.raises(OMExecutionError):
        _compiler.compile(_fail_src)


@pytest.mark.compilation
def test_failing_model_missing_semicolon():
    _fail_src = os.path.join(os.path.dirname(__file__), "models", "MissingSemiColon.mo")
    _compiler = Compiler()
    with pytest.raises(OMParsingError):
        _compiler.compile(_fail_src)