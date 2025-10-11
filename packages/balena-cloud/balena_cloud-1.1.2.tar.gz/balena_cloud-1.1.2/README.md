<!-- Banner -->
![alt Banner of the Balena Cloud package](https://raw.githubusercontent.com/MrGreenBoutiqueOffices/python-balena-cloud/main/assets/header_balena_cloud-min.png)

<!-- PROJECT SHIELDS -->
[![GitHub Release][releases-shield]][releases]
[![Python Versions][python-versions-shield]][pypi]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![GitHub Activity][commits-shield]][commits-url]
[![PyPi Downloads][downloads-shield]][downloads-url]
[![GitHub Last Commit][last-commit-shield]][commits-url]
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

[![Build Status][build-shield]][build-url]
[![Typing Status][typing-shield]][typing-url]
[![Code Coverage][codecov-shield]][codecov-url]


Asynchronous Python client for [Balena Cloud][balena].

## About

With this python package it's possible to get your organizations, fleets and devices. But also change or add new devices tags and environment variables.

## Installation

```bash
pip install balena-cloud
```

### Get API token

To use this package you need to have a Balena Cloud API token. You can get one by following the steps below:

1. Go to [Balena Cloud](https://www.balena.io/) and sign in.
2. Click on your profile icon in the top right corner.
3. Click on **Preferences** -> **Access tokens**.
4. Under "Api keys" click on **Create Api Key**.
5. Give your token a (required) name, description, set an expiration date and click on **Create token**.

### Example

```python
import asyncio

from balena_cloud import BalenaCloud


async def main() -> None:
    """Show example on using this package."""

    async with BalenaCloud(token="YOUR_API_TOKEN") as client:
        organizations = await client.organization.get_all()
        for organization in organizations:
            print(organization)


if __name__ == "__main__":
    asyncio.run(main())
```

More examples can be found in the [examples folder](./examples/).

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

The simplest way to begin is by utilizing the [Dev Container][devcontainer]
feature of Visual Studio Code or by opening a CodeSpace directly on GitHub.
By clicking the button below you immediately start a Dev Container in Visual Studio Code.

[![Open in Dev Containers][devcontainer-shield]][devcontainer]

This Python project relies on [Poetry][poetry] as its dependency manager,
providing comprehensive management and control over project dependencies.

You need at least:

- Python 3.11+
- [Poetry][poetry-install]

### Installation

Install all packages, including all development requirements:

```bash
poetry install
```

_Poetry creates by default an virtual environment where it installs all
necessary pip packages_.

### Pre-commit

This repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. To setup the pre-commit check, run:

```bash
poetry run pre-commit install
```

And to run all checks and tests manually, use the following command:

```bash
poetry run pre-commit run --all-files
```

### Testing

It uses [pytest](https://docs.pytest.org/en/stable/) as the test framework. To run the tests:

```bash
poetry run pytest
```

To update the [syrupy](https://github.com/tophat/syrupy) snapshot tests:

```bash
poetry run pytest --snapshot-update
```

## Trademark Legal Notices

All product names, trademarks and registered trademarks in this repository, are
property of their respective owners, and are used by the author for identification
purposes only. The use of these names, trademarks and brands, do not imply endorsement
or affiliation.

## License

MIT License

Copyright (c) 2024-2025 NetOS

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


<!-- LINKS FROM PLATFORM -->
[balena]: https://www.balena.io/

<!-- MARKDOWN LINKS & IMAGES -->
[build-shield]: https://github.com/MrGreenBoutiqueOffices/python-balena-cloud/actions/workflows/tests.yaml/badge.svg
[build-url]: https://github.com/MrGreenBoutiqueOffices/python-balena-cloud/actions/workflows/tests.yaml
[codecov-shield]: https://codecov.io/gh/MrGreenBoutiqueOffices/python-balena-cloud/branch/main/graph/badge.svg?token=1DG9LQJNY6
[codecov-url]: https://codecov.io/gh/MrGreenBoutiqueOffices/python-balena-cloud
[commits-shield]: https://img.shields.io/github/commit-activity/y/MrGreenBoutiqueOffices/python-balena-cloud.svg
[commits-url]: https://github.com/MrGreenBoutiqueOffices/python-balena-cloud/commits/main
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/MrGreenBoutiqueOffices/python-balena-cloud
[downloads-shield]: https://img.shields.io/pypi/dm/balena-cloud
[downloads-url]: https://pypistats.org/packages/balena-cloud
[last-commit-shield]: https://img.shields.io/github/last-commit/MrGreenBoutiqueOffices/python-balena-cloud.svg
[license-shield]: https://img.shields.io/github/license/MrGreenBoutiqueOffices/python-balena-cloud.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[pypi]: https://pypi.org/project/balena-cloud/
[python-versions-shield]: https://img.shields.io/pypi/pyversions/balena-cloud
[releases-shield]: https://img.shields.io/github/release/MrGreenBoutiqueOffices/python-balena-cloud.svg
[releases]: https://github.com/MrGreenBoutiqueOffices/python-balena-cloud/releases
[typing-shield]: https://github.com/MrGreenBoutiqueOffices/python-balena-cloud/actions/workflows/typing.yaml/badge.svg
[typing-url]: https://github.com/MrGreenBoutiqueOffices/python-balena-cloud/actions/workflows/typing.yaml

[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com
