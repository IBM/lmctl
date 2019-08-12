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

Please read the [User Guide](./docs/userguide.md)

## Building a distribution from source

A distribution can be built using `setuptools`. To build a `.whl` package you will need to install `wheel`

```
pip3 install wheel
```

```
python3 setup.py bdist_wheel
```

Check the `/dist` directory for the `.whl` package.

## Releasing a distribution

A lmctl distrubtion may be uploaded to a repository using `twine`. Ensure you have it installed using pip:

```
pip3 install twine
```

Now uploaded to the target repository. All packages in the `dist/*` directory will be uploaded.

```
python3 -m twine upload --repository-url http://repo.lifecyclemanager.com/repository/pypi/ dist/*
```

You will require a username and password if the repository is secured.

## Installed from released distribution

An existing distribution of lmctl can be installed using `pip`. Firstly find the `pip.conf` file for your installation of `pip`, or create one if necessary:

```
touch $HOME/pip/pip.conf
export PIP_CONFIG_FILE=$HOME/pip/pip.conf
```

Add the lifecyclemanager.com `pypi` repository group (includes a proxy to the public pypi repository):

```
[global]
index = http://repo.lifecyclemanager.com/repository/pypi-all/pypi
index-url = http://repo.lifecyclemanager.com/repository/pypi-all/simple
trusted-host = repo.lifecyclemanager.com
```

Use `pip` to install the lmcontroller, specifying your desired version:

```
pip3 install lmcontroller==2.0.0
```
