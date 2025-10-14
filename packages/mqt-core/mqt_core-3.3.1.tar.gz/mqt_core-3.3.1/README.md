[![PyPI](https://img.shields.io/pypi/v/mqt.core?logo=pypi&style=flat-square)](https://pypi.org/project/mqt.core/)
![OS](https://img.shields.io/badge/os-linux%20%7C%20macos%20%7C%20windows-blue?style=flat-square)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![DOI](https://img.shields.io/badge/JOSS-10.21105/joss.07478-blue.svg?style=flat-square)](https://doi.org/10.21105/joss.07478)
[![CI](https://img.shields.io/github/actions/workflow/status/munich-quantum-toolkit/core/ci.yml?branch=main&style=flat-square&logo=github&label=ci)](https://github.com/munich-quantum-toolkit/core/actions/workflows/ci.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/munich-quantum-toolkit/core/cd.yml?style=flat-square&logo=github&label=cd)](https://github.com/munich-quantum-toolkit/core/actions/workflows/cd.yml)
[![Documentation](https://img.shields.io/readthedocs/mqt-core?logo=readthedocs&style=flat-square)](https://mqt.readthedocs.io/projects/core)
[![codecov](https://img.shields.io/codecov/c/github/munich-quantum-toolkit/core?style=flat-square&logo=codecov)](https://codecov.io/gh/munich-quantum-toolkit/core)

<p align="center">
  <a href="https://mqt.readthedocs.io">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/munich-quantum-toolkit/.github/refs/heads/main/docs/_static/logo-mqt-dark.svg" width="60%">
      <img src="https://raw.githubusercontent.com/munich-quantum-toolkit/.github/refs/heads/main/docs/_static/logo-mqt-light.svg" width="60%" alt="MQT Logo">
    </picture>
  </a>
</p>

# MQT Core - The Backbone of the Munich Quantum Toolkit (MQT)

MQT Core is an open-source C++20 and Python library for quantum computing that forms the backbone of the quantum software tools developed as part of the [_Munich Quantum Toolkit (MQT)_](https://mqt.readthedocs.io).

<p align="center">
  <a href="https://mqt.readthedocs.io/projects/core">
  <img width=30% src="https://img.shields.io/badge/documentation-blue?style=for-the-badge&logo=read%20the%20docs" alt="Documentation" />
  </a>
</p>

## Key Features

- Fully fledged intermediate representation (IR) for quantum computations.
- A state-of-the-art decision diagram (DD) package for quantum computing.
- A dedicated ZX-diagram package for working with the ZX-calculus.
- A QIR runtime based on the decision diagram package.

If you have any questions, feel free to create a [discussion](https://github.com/munich-quantum-toolkit/core/discussions) or an [issue](https://github.com/munich-quantum-toolkit/core/issues) on [GitHub](https://github.com/munich-quantum-toolkit/core).

## Contributors and Supporters

The _[Munich Quantum Toolkit (MQT)](https://mqt.readthedocs.io)_ is developed by the [Chair for Design Automation](https://www.cda.cit.tum.de/) at the [Technical University of Munich](https://www.tum.de/) and supported by the [Munich Quantum Software Company (MQSC)](https://munichquantum.software).
Among others, it is part of the [Munich Quantum Software Stack (MQSS)](https://www.munich-quantum-valley.de/research/research-areas/mqss) ecosystem, which is being developed as part of the [Munich Quantum Valley (MQV)](https://www.munich-quantum-valley.de) initiative.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/munich-quantum-toolkit/.github/refs/heads/main/docs/_static/mqt-logo-banner-dark.svg" width="90%">
    <img src="https://raw.githubusercontent.com/munich-quantum-toolkit/.github/refs/heads/main/docs/_static/mqt-logo-banner-light.svg" width="90%" alt="MQT Partner Logos">
  </picture>
</p>

Thank you to all the contributors who have helped make MQT Core a reality!

<p align="center">
  <a href="https://github.com/munich-quantum-toolkit/core/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=munich-quantum-toolkit/core" alt="Contributors to munich-quantum-toolkit/core" />
  </a>
</p>

The MQT will remain free, open-source, and permissively licensed—now and in the future.
We are firmly committed to keeping it open and actively maintained for the quantum computing community.

To support this endeavor, please consider:

- Starring and sharing our repositories: https://github.com/munich-quantum-toolkit
- Contributing code, documentation, tests, or examples via issues and pull requests
- Citing the MQT in your publications (see [Cite This](#cite-this))
- Citing our research in your publications (see [References](https://mqt.readthedocs.io/projects/core/en/latest/references.html))
- Using the MQT in research and teaching, and sharing feedback and use cases
- Sponsoring us on GitHub: https://github.com/sponsors/munich-quantum-toolkit

<p align="center">
  <a href="https://github.com/sponsors/munich-quantum-toolkit">
  <img width=20% src="https://img.shields.io/badge/Sponsor-white?style=for-the-badge&logo=githubsponsors&labelColor=black&color=blue" alt="Sponsor the MQT" />
  </a>
</p>

## Getting Started

`mqt.core` is available via [PyPI](https://pypi.org/project/mqt.core/).

```console
(.venv) $ pip install mqt.core
```

The following code gives an example on the usage:

```python3
from mqt.core import QuantumComputation

qc = QuantumComputation(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure(range(2), range(2))

print(qc)
```

**Detailed documentation and examples are available at [ReadTheDocs](https://mqt.readthedocs.io/projects/core).**

## System Requirements

Building the project requires a C++ compiler with support for C++20 and CMake 3.24 or newer.
For details on how to build the project, please refer to the [documentation](https://mqt.readthedocs.io/projects/core).
Building (and running) is continuously tested under Linux, macOS, and Windows using the [latest available system versions for GitHub Actions](https://github.com/actions/runner-images).
MQT Core is compatible with all [officially supported Python versions](https://devguide.python.org/versions/).

The project relies on some external dependencies:

- [boost/multiprecision](https://github.com/boostorg/multiprecision): A library for multiprecision arithmetic (used in the ZX package).
- [nlohmann/json](https://github.com/nlohmann/json): A JSON library for modern C++.
- [pybind/pybind11_json](https://github.com/pybind/pybind11_json): A library for using `nlohmann::json` with `pybind11` (only used for creating the Python bindings).
- [google/googletest](https://github.com/google/googletest): A testing framework for C++ (only used in tests).

CMake will automatically look for installed versions of these libraries. If it does not find them, they will be fetched automatically at configure time via the [FetchContent](https://cmake.org/cmake/help/latest/module/FetchContent.html) module (check out the documentation for more information on how to customize this behavior).

It is recommended (although not required) to have [GraphViz](https://www.graphviz.org) installed for visualization purposes.

If you want to use the ZX library, it is recommended (although not strictly necessary) to have [GMP](https://gmplib.org/) installed in your system.

## Cite This

Please cite the work that best fits your use case.

### MQT Core (the tool)

When citing the software itself or results produced with it, cite the MQT Core paper:

```bibtex
@article{burgholzer2025MQTCore,
  title        = {{{MQT Core}}: {{The}} Backbone of the {{Munich Quantum Toolkit (MQT)}}},
  author       = {Burgholzer, Lukas and Stade, Yannick and Peham, Tom and Wille, Robert},
  year         = 2025,
  journal      = {Journal of Open Source Software},
  publisher    = {The Open Journal},
  volume       = 10,
  number       = 108,
  pages        = 7478,
  doi          = {10.21105/joss.07478},
  url          = {https://doi.org/10.21105/joss.07478}
}
```

### The Munich Quantum Toolkit (the project)

When discussing the overall MQT project or its ecosystem, cite the MQT Handbook:

```bibtex
@inproceedings{mqt,
  title        = {The {{MQT}} Handbook: {{A}} Summary of Design Automation Tools and Software for Quantum Computing},
  shorttitle   = {{The MQT Handbook}},
  author       = {Wille, Robert and Berent, Lucas and Forster, Tobias and Kunasaikaran, Jagatheesan and Mato, Kevin and Peham, Tom and Quetschlich, Nils and Rovara, Damian and Sander, Aaron and Schmid, Ludwig and Schoenberger, Daniel and Stade, Yannick and Burgholzer, Lukas},
  year         = 2024,
  booktitle    = {IEEE International Conference on Quantum Software (QSW)},
  doi          = {10.1109/QSW62656.2024.00013},
  eprint       = {2405.17543},
  eprinttype   = {arxiv},
  addendum     = {A live version of this document is available at \url{https://mqt.readthedocs.io}}
}
```

---

## Acknowledgements

The Munich Quantum Toolkit has been supported by the European Research Council (ERC) under the European Union's Horizon 2020 research and innovation program (grant agreement No. 101001318), the Bavarian State Ministry for Science and Arts through the Distinguished Professorship Program, as well as the Munich Quantum Valley, which is supported by the Bavarian state government with funds from the Hightech Agenda Bayern Plus.

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/munich-quantum-toolkit/.github/refs/heads/main/docs/_static/mqt-funding-footer-dark.svg" width="90%">
    <img src="https://raw.githubusercontent.com/munich-quantum-toolkit/.github/refs/heads/main/docs/_static/mqt-funding-footer-light.svg" width="90%" alt="MQT Funding Footer">
  </picture>
</p>
