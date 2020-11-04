LMCTL is a command-line client that provides commands for interacting with IBM Telco Network Cloud Manager (TNCM) Orchestrator (TNCO/ALM) environments. 

In addition it includes an opinionated pattern for managing xNF/Network Service designs during the CICD lifecycle, as file based projects, to produce packages suitable for production release.

## Quick Install

Assumes you already have Python3.6+ and have decided if LMCTL should be installed in a [virtual environment](https://pypi.org/project/virtualenv/) (recommended) or globallly.

Install the latest from Pypi:
```
python3 -m pip install lmctl
```

Verify LMCTL is ready to use:
```
lmctl --version
```

Initiate a config file:
```
lmctl create config

lmctl get config --print-path
```

## Documentation

Documentation available in the source code: <a href="https://github.com/IBM/lmctl/blob/master/docs/index.md" target="_blank">https://github.com/IBM/lmctl/blob/master/docs/index.md</a>

## Links

- Code: <a href="https://github.com/IBM/lmctl" target="_blank">https://github.com/IBM/lmctl</a>
- Releases: <a href="https://github.com/IBM/lmctl/releases" target="_blank">https://github.com/IBM/lmctl/releases</a>
