
# 2025-10-12 [v0.6.3](https://gitlab.com/krizar/pydelica/-/tags/v0.6.3)

- Fixed missing compiler handling bug.
- Support Python3.14

# 2024-07-29 [v0.6.2](https://gitlab.com/krizar/pydelica/-/tags/v0.6.2)
- Fix C runtime simulation options retrieval during model execution.

# 2024-07-29 [v0.6.1](https://gitlab.com/krizar/pydelica/-/tags/v0.6.1)

- Support Python3.13

# 2024-07-29 [v0.6.0](https://gitlab.com/krizar/pydelica/-/tags/v0.6.0)

- Fix incorrect file specification during result retrieval.
- Add C Runtime Simulation options functionality.
- Deprecated `OMLogLevel` in favour of the above.
- Deprecation of `Solver` and `OutputFormat` enumerations in favour of string literals.
- Introduce validation of inputs with Pydantic.
- Methods which return paths now return `pathlib.Path` as opposed to `str`.

# 2024-03-02 [v0.5.1](https://gitlab.com/krizar/pydelica/-/tags/v0.5.1)

- Added missing `OutputFormat` option.

# 2023-05-21 [v0.5.0](https://gitlab.com/krizar/pydelica/-/tags/v0.5.0)

- Switch to Pandas v2

# 2023-05-21 [v0.4.4](https://gitlab.com/krizar/pydelica/-/tags/v0.4.4)

- Fix running of models within OpenModelica 1.21.0 under Windows.
- Fix failure to find executable names in later OM versions.

# 2022-05-04 [v0.4.3](https://gitlab.com/krizar/pydelica/-/tags/v0.4.3)

- Fix us of non-existent `HOME` environment variable in Windows, replacing it with `HOMEPATH`.

# 2022-03-09 [v0.4.2](https://gitlab.com/krizar/pydelica/-/tags/v0.4.2)

- Remove libraries after use to prevent junk buildup with temporary directories in Windows.
- Add context manager for `Session` to ensure directory cleanup.
- Add `use_libraries` method for specifying all libraries as dictionary.
- Now requires all used libraries to be specified if `use_library` or `use_libraries` given, else uses the system Modelica libraries.
- Add handling of non-zero return codes during model building.

# 2022-03-09 [v0.3.1](https://gitlab.com/krizar/pydelica/-/tags/v0.3.1)

- Added fixes for Windows support
- Use OM MinGW Make as opposed to compile batch script

# 2022-01-31 [v0.2.3](https://gitlab.com/krizar/pydelica/-/tags/v0.2.3)

- Add ability to append additional arguments to the OMC build command.
- Storage of code profile data in session where applicable.
- Runs now performed in temporary directory.

# 2022-01-14 [v0.1.18](https://gitlab.com/krizar/pydelica/-/tags/v0.1.18)

- Re-added exception trigger when Modelica message "simulation terminated by an assertion" shown.

# 2022-01-14 [v0.1.17](https://gitlab.com/krizar/pydelica/-/tags/v0.1.17)

- Added `NotImplementedError` to handle cases not yet supported on Windows

# 2021-12-16 [v0.1.16](https://gitlab.com/krizar/pydelica/-/tags/v0.1.16)

- Widen library search paths
- Allow user to specify custom location of a library when using `use_library`.

# 2021-12-10 [v0.1.15](https://gitlab.com/krizar/pydelica/-/tags/v0.1.15)

- Switch to using `-inputPath` for passing model input location
- Added ability to import C source files during build.
- Sources are now copied to temporary location before build.

# 2021-09-08 [v0.1.14](https://gitlab.com/krizar/pydelica/-/tags/v0.1.14)

- Uses regex to check for an OpenModelica assertion violation
- Adds ability to specify the level at which an exception should be thrown for an assertion violation.

# 2021-07-29 [v0.1.13](https://gitlab.com/krizar/pydelica/-/tags/v0.1.13)

- Fixes to improve error capturing
- Fixed an issue where parameter values set to exactly 0 would not be parsed to the model.

# 2021-06-11 [v0.1.12](https://gitlab.com/krizar/pydelica/-/tags/v0.1.12)

- Add ability to change library versions. The user can now specify if they wish to for example use MSL 3.2.3 rather than 4.0.0 if both are on their system. NOTE: This feature is disabled for Windows users due to an access permissions issue.
- Add ability to compile mutiple files at once (flatten). This enables the target model to call models from other .mo files (must be located inside the same directory).

# 2021-06-11 [v0.1.10](https://gitlab.com/krizar/pydelica/-/tags/v0.1.10)

- Added additional information to exceptions, these now contain more of the Modelica run output
- Removed obsolete output format specification choosing instead to always use easy access dataframes via CSV output
- Print stdout before raising exceptions in all cases.

# 2021-03-30 [v0.1.9](https://gitlab.com/krizar/pydelica/-/tags/v0.1.9)

- Replace `xml` module with `defusedxml` to fix security issue with XML files

# 2021-03-27 [v0.1.8](https://gitlab.com/krizar/pydelica/-/tags/v0.1.8)

- Throw exceptions when asserts fail in Modelica during a run
  
# 2021-03-15 [v0.1.7](https://gitlab.com/krizar/pydelica/-/tags/v0.1.7)

- Move writing of XML file to simulation stage to prevent bottleneck due to constant re-writes

# 2021-03-09 [v0.1.6](https://gitlab.com/krizar/pydelica/-/tags/v0.1.6)

- Lexer errors count as warnings which may be ignored as these often do not affect results. Let user decide if action must be taken.

# 2021-03-03 [v0.1.3-alpha](https://gitlab.com/krizar/pydelica/-/tags/v0.1.3-alpha)

- Added Windows Mingw support
- Set/Get parameters added via alteration of generated XML files
- Automate compiling via OMC by generating scripts then using `make`
- Started PyDelica as Python API for Modelica
