<p align="center">
<img src="https://gitlab.com/krizar/pydelica/-/raw/main/media/pyd_logo.svg", width="200">
</p>

# PyDelica: Serverless OpenModelica with Python

## About

PyDelica is an API providing a quick and easy to use interface to compile, customise and run OpenModelica models with Python. Unlike OMPython it does not require the launch of a server session to use OMShell but rather dynamically adjusts files produced after model compilation in order to update options and parameters. The lack of server requirement means models can be run in tandem without calling multiple OMC sessions which can be very taxing on CPU. Furthermore PyDelica is able to detect errors during model runs by reading the `stderr` and `stdout` from OpenModelica and throw appropriate exceptions to terminate the program execution.

## Installation

To use PyDelica you will require an installation of OpenModelica on your system, the API has been confirmed to work on both Windows and Linux, but if OM is installable on macOS it should also be possible to still use it. 

To install run:

```bash
pip install pydelica
```

## Getting Started
For the purposes of demonstration the included test model `tests/models/SineCurrent.mo` will be used.
### PyDelica Session
All uses of PyDelica require an instance of the `Session` class:

```python
from pydelica import Session

with Session() as session:
    ...
```
It is strongly recommended that this class be used via the context manager to ensure cleanup of temporary directories.

#### Logging
The `Session` class has one optional argument which is used to set the log level output within OpenModelica itself. The options are based on the `-lv` flag within OM. By default the level is set to `Normal` which means no log level output.

As an example if you wanted to run with statistics logging `-lv=LOG_STATS` you would setup with the following:

```python
from pydelica import Session
from pydelica.logger import OMLogLevel

with Session(log_level=OMLogLevel.STATS) as session:
    ...
```

See the source for more options [here](https://gitlab.com/krizar/pydelica/-/blob/master/pydelica/logging.py).

#### Building/Compiling Models
Before you can run a model you must first compile it. This is done using the `build_model` member function which takes the path to the Modelica source file.

```python
model_path = os.path.join('tests', 'models', 'SineCurrent.mo')
session.build_model(model_path)
```

If the required model is not top level, that is to say it exists within a module or , we can optionally specify the address within Modelica. This is also required if the required model is not the default. For example say model `A` existed within module `M`:

```python
model_path = 'FictionalModelFile.mo'
session.build_model(model_path, 'M.A')
```

The `build_model` function also allows you to specify additional flags/options to hand to the OMC compiler, these are given
in the form of a dictionary where the value can be `None` if the flag does not take any input. You can also directly set the profiling level for profiling the Modelica code. When set, the profile dictionary is also stored in the session after the simulation and is accessible via the `code_profile` and `code_info` attributes:

```python
session.build_model(
    model_path,
    model_addr='M.A'
    profiling="all",
    omc_build_flags={"-g": "MetaModelica"}
)
session.simulate()
print(session.code_profile)
print(session.code_info)
```

#### Specifying Additional Model-Based Dependencies

If additional model files are required to execute the main model these can be specified with the `extra_models` argument:

```python
session.build_model(
    model_path,
    extra_models=["extra_model.mo"]
)
```

#### Using Alternative Inputs Location

If your model inputs are stored in an alternative directory, this can be specified with the `update_input_paths_to` argument:

```python
session.build_model(
    model_path,
    update_input_paths_to="/path/to/inputs"
)
```

#### Examining Parameters and Options
We can examine all parameters for a given model using the `get_parameters` method which will return a Python dictionary:

```python
session.get_parameters('SineCurrentModel')
```

if the parameter is unique to a single model then the model name argument can be dropped. Returning the value for a single parameter is as simple as:

```python
session.get_parameter(<parameter-name>)
```

For simulation options the analogous methods are `get_simulation_options` and `get_simulation_option` respectively for general case, for more specific see below.

#### Setting Parameters and Options
Set a parameter to a different value using the `set_parameter` function:

```python
session.set_parameter(<parameter-name>, <new-value>)
```

#### Setting C Runtime Simulation flags
To set options provided to the command line during simulation execution you can use `get_runtime_options`:

```python
runtime_options = session.get_runtime_options(<model-name>)
```

This will return a `RuntimeOptions` instance with configurable attributes, use `help(session.get_runtime_options)` to see the docstring detailing each,
or by going to the [C Runtime Simulation Flags](https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/simulationflags.html#cruntime-simflags) OM manual page.

```python
runtime_options.nls = "homotopy"
```

#### Further Configuration
The output file type can be specified:

```python
from pydelica.options import OutputFormat
session.set_output_format(OutputFormat.CSV) # Other options are MAT and PLT
```

Set the solver:

```python
from pydelica.options import Solver
session.set_solver(Solver.DASSL)    # Other options are EULER and RUNGE_KUTTA
```

Set the time range:

```python
# Each argument is optional
session.set_time_range(start_time=0, stop_time=10, model_name='SineCurrentModel')
```

Set tolerance:

```python
# Model name is optional
session.set_tolerance(tolerance=1E-9, model_name='SineCurrentModel')
```

Set variable filter for outputs:

```python
# Model name is optional
session.set_variable_filter(filter_str='output*', model_name='SineCurrentModel')
```

#### Failing Simulation on Lower Assertion Level
By default PyDelica will look for the expression `assert | error` as an indication of a Modelica assertion
failure and then terminate when this is violated. You can override this behaviour using the `fail_on_assert_level`
method of the `Session` class:

```python
from pydelica import Session

with Session() as pd_session:
    pd_session.fail_on_assert_level('warning')
```

Possible values ranked by order (highest at the top):

|**Value**|**Description**|
|---|---|
|`'never'`|Do not throw an exception on Modelica assertion violation|
|`'error'`|Default. Throw an exception on an assertion of level `AssertionLevel.error`|
|`'warning'`|Throw an exception on assertion of level `AssertionLevel.warning`|
|`'info'`|Throw an exception on any `assert \| info` statement|
|`'debug'`|Throw an exception on any `assert \| debug` statement|

#### Running the Simulation
To run the simulation use the `simulate` method. If a model name is specified then that model is run,
else this is the first model in the model list. At the simulation step parameter values are written to the
XML file read by the binary before the model binary is executed.

```python
# Model name is optional, verbosity is also optional and overwrites that of the session
session.simulate(model_name='SineCurrentModel')
```

#### Retrieving Results
To view the results use the `get_solutions` method which will return a python dictionary containing
the solutions for all models after a model run:

```python
solutions = session.get_solutions()
```
The variables for each model are stored as a Pandas dataframe.

#### Using Alternative Libraries

**NOTE:** Currently only works in WSL on Windows machines.

You can use an alternative library version via the `use_library` method:
```python
session.use_library("Modelica", "3.2.3")
```
you can also optionally specify the location of this library:
```python
session.use_library("Modelica", "3.2.3", library_directory="/home/user/my_om_libraries")
```

#### Including Extra C Resources

When building a model extra C file resources can be specified using the `c_source_dir` argument to `build_model`:

```python
session.build_model(
    model_path,
    c_source_dir=os.path.join(model_dir, "Resources", "Include")
)
```

## Docker

A Docker image is available for OpenModelica with Pydelica:

```sh
$ docker pull artemisbeta/pydelica
```

You can try out Pydelica within a Jupyter notebook by running:

```sh
$ docker run -ti artemisbeta/pydelica jupyter notebook --ip 0.0.0.0 --no-browser
```

and opening the resulting URL within your browser.

## Troubleshooting

### Simulation fails with no error thrown
Try setting the assertion level to a lower level, for some reason OM ranks missing input file errors
as type `debug`, see [here](#failing-simulation-on-lower-assertion-level).

```
stdout | info | ... loading "data" from "Default/myInput.mat"
assert | debug | Not possible to open file "Default/myInput.mat": No such file or directory
assert | info | simulation terminated by an assertion at initialization
```

### PyDelica cannot find OMC
PyDelica relies on either locating OMC on UNIX using the `which` command, or in the case of Windows using the `OPENMODELICAHOME` environment variable. Ensure at least one of these is available after installating OpenModelica.

## Use Cases

_Pydelica_ is currently being used in the following projects, if you would like to be included in this list please open an issue:

* [_Power Balance Models_](https://github.com/ukaea/powerbalance), _United Kingdom Atomic Energy Authority_: A tokamak power balance model with Python API and CLI
