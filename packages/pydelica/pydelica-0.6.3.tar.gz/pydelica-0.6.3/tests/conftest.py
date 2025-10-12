import pytest

MODELICA_STANDARD_LIBRARY_VERSION = "3.2.3"

@pytest.fixture(scope="session")
def modelica_environment():
    return [
        {
            "name": "Modelica",
            "version": MODELICA_STANDARD_LIBRARY_VERSION
        },
        {
            "name": "ModelicaServices",
            "version": MODELICA_STANDARD_LIBRARY_VERSION
        },
        {
            "name": "Complex",
            "version": MODELICA_STANDARD_LIBRARY_VERSION
        },
    ]
