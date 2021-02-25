# LMCTL Install

Table of contents:
- [Quickstart](#quickstart)
- [Pre-requisites](#pre-requisites) 
  - [Python 3.6.9+](#python-3.6.9+)
  - [Python Virtual Environment](#python-virtual-environment)
- [Uninstall existing LMCTL](#uninstall-existing-lmctl)
- [Install LMCTL](#install-lmctl)
- [Next Steps: Configure](#next-steps-configure)

## Quickstart

If you're an experienced Python, Pip user and understand the implications of installing into your global system vs Virtual Environment then you can get started with two commands:

```
python3 -m pip install lmctl
lmctl --version
```

To install a specific version <a href="https://pypi.org/project/lmctl/" target="_blank">see available versions</a>, add the number to the end of the command with `==`:

```
python3 -m pip install lmctl==3.0.0
```

## Pre-requisites

Before installing LMCTL, you will need a ready-to-use Python environment.

### Python 3.6.9+

LMCTL requires <a href="https://www.python.org" target="_blank">Python 3.6.9+</a>. Follow the installation instructions for you operating system.

You should also make sure you have the latest version of <a href="https://pip.pypa.io/en/stable/installing/" target="_blank">Pip3</a> (already installed with many Python installations).

As it's possible to have both Python2 and Python3 installed on one machine, this guide will make use of `python3` and `pip3` commands, instead of `python` and `pip`, for clarity.

If you only have Python3, then you may use the latter instead. Verify which command works for you by running both:

```
python --version

python3 --version
```

Use the version which responds with a `3.x` number.

### Python Virtual Environment

It is highly recommended that you install and make use of a virtual environment when installing LMCTL. This will keep all dependencies used by LMCTL isolated from other Python applications on your machine. 

It will also allow you to have alternate versions installed, in two separate environments, which is useful when there is a new major version of TNCO and LMCTL, with potential non-backward compatible changes.

We recommend installing <a href="https://virtualenv.pypa.io/en/latest/" target="_blank">Virtualenv</a>:

```
python3 -m pip install virtualenv
```

Create a new virtual environment with `virtualenv`, specifying a suitable name for it:

```
python3 -m virtualenv lmctl-env
```

This will create an environment in a directory named `lmctl-env` (or any name you decide). Once created, the virtual environment can be activated anytime with:

```
source lmctl-env/bin/activate
```

On Windows, try:

```
lmctl-env\Scripts\activate.bat
```

Ensure the environment is active anytime you install or use LMCTL to maintain isolation from your global Python environment.

To deactivate the virtual environment at anytime just execute:

```
deactivate
```

## Uninstall existing LMCTL

Before continuing it is important that you ensure your global system and/or virtual environment do not already have LMCTL installed.

Check this by running:

```
lmctl --version
```

If you have an existing installation, uninstall it with:

```
python3 -m pip uninstall lmctl
```

Ensure you execute this on your virtual environment if LMCTL has been installed there, otherwise execute this on your machine's global python system by deactivating the virtual environment first.

## Install LMCTL

Activate any virtual environment you intend to use and install LMCTL with pip:

```
python3 -m pip install lmctl
```

To install a specific version <a href="https://pypi.org/project/lmctl/" target="_blank">see available versions</a>, add the number to the end of the command with `==`:

```
python3 -m pip install lmctl==3.0.0
```

Verify the installation has worked by executing:

```
lmctl --version
```

Access the `help` section of LMCTL with:

```
lmctl --help
```

## Next Steps: Configure

Now you have LMCTL installed, it's time to [configure](./configure.md) it with access to your TNCO (ALM) environment.
