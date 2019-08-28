[![Build Status](https://travis-ci.com/accanto-systems/lmctl.svg?branch=master)](https://travis-ci.com/accanto-systems/lmctl)

# Lifecycle Manager Controller (lmctl) command line tools

This project provides a set of tools to automate the management of Stratoss&trade; Lifecycle Manager (Stratoss LM) environments and the tasks required to deploy VNFs and Network Services.

The **lmctl** tool supports the following use cases:

- Push and pull contents of VNF and Network Service projects to and from Stratoss LM environments
- Run behaviour tests in Stratoss LM environments

## Installation

Ensure you have `python3` installed.

```
apt-get install python3 python3-pip
```

Before installing lmctl, you may optionally start a virtualenv first to prevent dependencies being installed globally (see https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments).

```
pip3 install virtualenv
# Creates a new virtual environment at ./env
python3 -m virtualenv env
```

Install lmctl from pypi:

```
pip3 install lmctl
```

Install lmctl from source (use `--editable` if you want changes you make to the source code to be activate immediately):

```
pip3 install --editable .
```

You should now be able to execute `lmctl` from the console. If you can't, check if lmctl has been installed to your $HOME/.local/bin directory, ensure this directory is included on your $PATH environment variable.

```
lmctl --help

Usage: lmctl [OPTIONS] COMMAND [ARGS]...

  Lifecycle Manager Control tools

Options:
  --help  Show this message and exit.

Commands:
  admin    Administrative commands
  env      Commands for inspecting available LM environments
  pkg      Commands for managing a package built from a NS/VNF Project
  project  Commands for managing a NS/VNF Project
```

## Using Lmctl

Please read the [User Guide](./docs/user_guide.md)
