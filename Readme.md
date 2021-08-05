[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Build Status](https://travis-ci.com/IBM/lmctl.svg?branch=master)](https://travis-ci.com/IBM/lmctl)
[![PyPI version](https://badge.fury.io/py/lmctl.svg)](https://badge.fury.io/py/lmctl)

# LMCTL 

:computer: LMCTL is a command-line client that provides commands for interacting with IBM Cloud Pak for Network Automation (CP4NA) orchestration environments (previously known as TNCO/ALM).

In addition it includes an opinionated pattern for managing xNF/Network Service designs during the CICD lifecycle, as file based projects, to produce packages suitable for production release.

- [Quick Install](#quick-install)
- [Latest Release](#latest-release)
- [User Guide](#user-guide)
- [Development Doc](#development-docs)

# Quick Install

Assumes you already have Python3.6+ and have decided if LMCTL should be installed in a [virtual environment](https://pypi.org/project/virtualenv/) (recommended) or globallly.

:rocket: Install the latest from Pypi:
```
python3 -m pip install lmctl
```

:roller_coaster: Want bleeding edge? Install from source code:
```
git clone git@github.com:IBM/lmctl.git
cd ./lmctl
python3 -m pip install .
```

Verify LMCTL is ready to use:
```
lmctl --version
```

Login to an environment:
```
lmctl login alm-ishtar.example.com --auth-address alm-nimrod.example.com --username almadmin --save-creds
```

For more complete install and login instructions, check out the [getting started guide](docs/getting-started.md)

# Latest release

:newspaper: [See what's new in the latest release](docs/what-is-new.md)

# User Guide

:notebook: To get started, read the [User Guide](docs/index.md)

# Development Docs

:clipboard: For documentation related to developing LMCTL please see the [development docs](developer_docs/index.md)
