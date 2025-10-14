<!-- SPDX-FileCopyrightText: 2025 German Aerospace Center <fame@dlr.de>

SPDX-License-Identifier: Apache-2.0 -->
# FAME-Io

## *Prepare input and digest output from simulation models*

[![License](https://img.shields.io/pypi/l/fameio.svg)](https://badge.fury.io/py/fameio)
[![Cite](https://img.shields.io/badge/DOI-10.21105%2Fjoss.04958-blue)](https://doi.org/10.21105/joss.04958)
[![Pipeline](https://gitlab.com/fame-framework/fame-io/badges/main/pipeline.svg)](https://gitlab.com/fame-framework/fame-io/commits/main)
[![Code Coverage](https://gitlab.com/fame-framework/fame-io/badges/main/coverage.svg)](https://gitlab.com/fame-framework/fame-io/-/jobs)
![Last Commit](https://img.shields.io/gitlab/last-commit/fame-framework%2Ffame-io)

FAME-Io compiles input for FAME models and extracts model output to human-readable files. Model data is handled in the efficient protobuf format.<br>
[FAME](https://gitlab.com/fame-framework/wiki/-/wikis/home) is the open **F**ramework for distributed **A**gent-based **M**odels of **E**nergy systems.
Check out the full [FAME-Io documentation](https://fame-framework.gitlab.io/fame-io).

## What is FAME-Io?

FAME-Io is the input-output toolkit for FAME-based simulation models.
The relationship to other components can be seen below.

<img src="https://gitlab.com/fame-framework/wiki/-/wikis/architecture/diagrams/Workflow.png" alt="FAME component workflow" width="75%">

FAME-Io (orange) combines model data (purple) and user input data (green) for the computation (blue).
After the computation, FAME-Io returns the results in a readable format.

Thus, with FAME-Io you can:

* Compile input binaries for simulation models built with FAME,
* Extract output binaries to human-readable formats like CSV and JSON,
* Edit large CSV files to enhance compilation speed.

## Who is FAME-Io for?

FAME-Io is a vital file-conversion component for FAME-based workflows. If your model is not built with [FAME](https://gitlab.com/fame-framework/wiki/-/wikis/home), you will probably not profit from FAME-Io.

## Applications

FAME-Io is used with any model that is based on FAME.
An example of its application is the electricity market model [AMIRIS](https://helmholtz.software/software/amiris).

## Community

FAME-Io is mainly developed by the German Aerospace Center, Institute of Networked Energy Systems.
We provide support via the dedicated email address [fame@dlr.de](mailto:fame@dlr.de).

**We welcome all contributions**: bug reports, feature requests, documentation enhancements, and code.<br>
For substantial enhancements, we recommend that you contact us via [fame@dlr.de](mailto:fame@dlr.de) for working together on the code in common projects or towards common publications and thus further develop FAME-Io.
<br>Please see our [Contribution Guidelines](docs/source/contribute/contribute.rst).

## Citing FAME-Io

If you use FAME-Io in academic work, please cite: [DOI 10.21105/joss.04958](https://doi.org/10.21105/joss.04958)

```
@article{fameio2023joss,
  author  = {Felix Nitsch and Christoph Schimeczek and Ulrich Frey and Benjamin Fuchs},
  title   = {FAME-Io: Configuration tools for complex agent-based simulations},
  journal = {Journal of Open Source Software},
  year    = {2023},
  doi     = {doi: https://doi.org/10.21105/joss.04958}
}
```

In other contexts, please include a link to our [Gitlab repository](https://gitlab.com/fame-framework/fame-io).
