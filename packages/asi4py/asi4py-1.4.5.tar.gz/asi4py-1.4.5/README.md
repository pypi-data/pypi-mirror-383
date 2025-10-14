# Atomic Similation Interface (ASI) API

Atomic Simulation Interface (ASI) is a native C-style API that includes functions for export and import of data structures that are used in electronic structure calculations and for classical molecular dynamics simulations. ASI aims to be a uniform, generic and efficient interface for connecting various computational chemistry and materials science codes in multiscale simulation workflows, such as QM/MM, QM/ML, QM/QM. ASI specifies functions, data types and calling conventions for export and import of density matrices, overlap and Hamiltonian matrices, electrostatic potential, atomic coordinates, charges, total energy and forces. 

## ASI API specification

ASI API is specified as a C header file [`asi.h`][1]. Codes implementing ASI API must provide linkable library with definitions of functions from [`asi.h`][1]. Depending on particular usage of the implementaions, some functions can be ommited or implemented as stubs, if they are not going to used. To use Python ASI wrapper it is necessary to have all functions from `asi.h` defined, but of course stub definitions can be used.

[**ASI API specification**][1].

[1]: https://pvst.gitlab.io/asi/asi_8h.html

## Supported in:

* [DFTB+](https://dftbplus.org/): [in separate branch](https://github.com/PavelStishenko/dftbplus/tree/ASI_v1.3).
* [FHI-aims](https://fhi-aims.org/): in the main branch.


## Building

### FHI-aims

FHI-aims has embedded support of ASI API. Just build latest version of FHI-aims as a shared library and use with your code.


### DFTB+

1. Download and build DFTB+ from [the branch with ASI API](https://github.com/PavelStishenko/dftbplus/tree/ASI_v1.3) with shared library support.

2. Set environment variables `DFTBP_INCLUDE` and `DFTBP_LIB_DIR` to folders with DFTB+ C-headers and libraries.

3. Optionally export environment variables `INSTALL_PREFIX` and `BUILD_PATH` to set installation and building locations.

4. Run `make && make install` from the root of the working copy of this repository. 

5. The shared library implementing ASI API for DFTB+ will be in `${INSTALL_PREFIX}/lib`.

## Testing

Use `Makefile` in `tests` folder to build native tests. Set environment variables in the header of `tests/Makefile` to link with proper ASI API implementaions.

To run tests go to `tests/testcases` and run `run_dftbp_tests.sh` or `run_aims_tests.sh` to run test.

## Usage

See `tests/src` for examples of usage in native code.

See `tests/python` for examples of usage in Python scripts.


