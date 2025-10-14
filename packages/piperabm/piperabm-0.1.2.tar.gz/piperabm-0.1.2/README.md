<h1 align="center">
    <br>
    Pied Piper
</h1>

<h3 align="center">
    An Agent-Based Model Framework for Simulating Societal Resilience
</h3>

<div align="center">

[![Docs](https://img.shields.io/badge/docs-30363f?logo=read-the-docs&logoColor=white)](https://pied-piper.readthedocs.io/)
![Python Version](https://img.shields.io/badge/python-≥3.10-blue)
[![PyPI Version](https://img.shields.io/pypi/v/piperabm.svg)](https://pypi.org/project/piperabm/)
[![GitHub](https://img.shields.io/badge/github-30363f?logo=github&logoColor=white)](https://github.com/cmudrc/pied-piper)
[![Coverage Status](https://coveralls.io/repos/github/cmudrc/pied-piper/badge.svg?branch=main)](https://coveralls.io/github/cmudrc/pied-piper?branch=main)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

<div align="center">
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Pied_Piper2.jpg/593px-Pied_Piper2.jpg" alt="KeePied Piper of HamelinpDelta" width="520">
    </br>
    <em>
        Illustration by Kate Greenaway for Robert Browning's "The Pied Piper of Hamelin"
    </em>
</div>

## Introduction

Living beings exist in perpetual tension with their environment, continually adapting to changes in their surroundings. This project aims to model the interdependent nature of life between humans and their environment.

## Installation

Install the package using pip:
```sh
pip install piperabm
```

## Usage

Once a `Model` instance is created, it automatically includes interconnected `infrastructure` and `society` components. The simulation is designed to explore how changes in one domain, such as agent behavior or infrastructure layout, affect the other over time. This interdependence forms the core of agent-based modeling within `PiperABM`.

```python
import piperabm as pa

model = pa.Model()
model.infrastructure.add_street(pos_1=[0, 0], pos_2=[-60, 40], name='road')
model.infrastructure.add_home(pos=[5, 0], id=1, name='home 1')
model.infrastructure.add_home(pos=[-60, 40], id=1, name='home 2')
model.infrastructure.bake()
model.society.generate(num=2, gini_index=0.4, average_balance=1000)
model.run(n=100, step_size=60)
```

For more usage examples, refer to the [`examples`](https://github.com/cmudrc/pied-piper/tree/main/examples) folder in the project repository.

## Supported Python Versions

It has been tested and verified to work with Python versions **3.10** to **3.13**. While it is expected to work with older versions of Python (given compatible dependency versions), these environments have not been tested and are not officially supported.

## Contributing

Contributions are welcome! Feel free to:
* Report issues.
* Submit feature requests.
* Create pull requests.

## License

Distributed under the MIT License. See [`LICENSE.txt`](https://github.com/cmudrc/pied-piper/blob/main/LICENSE) for more information.