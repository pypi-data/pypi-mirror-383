# Style guide
* CamelCase for typedef structs (and Python classes)
* snake_case_t for typedef primitives
* snake_case for functions and variables
* ALL_CAPS for macros and constants
* short prefixes on exported functions to avoid name collisions, e.g. fg_ for flowgrid.c functions
* All accesses to arrays are bounds-checked.
* cartesian coordinates are passed as `CartPair` structs, not as separate row/col arguments.
* Functions that modify values in-place take the pointer of the value to modify as the first argument.
* `FlowGrid` instances are passed by reference.
* Only pass `FlowGrid` if you need to access multiple fields or modify the graph. If you only need dimensions or a vertex, pass those directly.
* Version numbering: `MAJOR.MINOR.YYYYMMDD`
  * Major version changes for API-breaking changes
  * Minor version changes for new features, optimizations, or non-breaking API changes
  * Date-based patch version for bug fixes and small changes