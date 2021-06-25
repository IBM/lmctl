# Developer Environment

These docs help you get a full dev environment setup for working on LMCTL.

## Install Python

You need Python3.6+ and pip. Install those according to the instructions for your operating system. 

For Ubuntu, you can do this:

```
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.7
python3.7 --version
```

If you run `python3 --version` and get a different version then you need to do the following, replacing `3.6` with the major and minor version you have:

```
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.6 1
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
sudo update-alternatives --config python3
```

Enter 2 for python3.7

For pip, use:

```
sudo apt install python3-pip
```

## Install base libraries

Once you have Python, you should upgrade and install the following:

```
python3 -m pip install --upgrade pip setuptools wheel virtualenv
```

## Create Virtual Environment

Virtual environments keep your python libraries isolated so it's best to create one for each python project you work on. Create one for this driver project in this repo with the name of `env`, as this is already in the `.gitignore` file so won't be added on commits.

```
python3 -m virtualenv env
```

Activate the environment:

```
source env/bin/activate
```

For windows:

```
env\Scripts\activate.bat
```

## Install LMCTL 

Install LMCTL from source with pip. Include the `--editable` flag so changes you make take effect immediately without a re-install. 

```
python3 -m pip install --editable .
```

Confirm LMCTL is available as a command:

```
lmctl --version
```

## Install the build dependencies

If you want to use the `build.py` script to automate builds, you should install the requirements:

```
python3 -m pip install -r build-requirements.txt
```

Check the help option for build.py to see what it can do:

```
python3 build.py --help
```

Note: `--release` is reserved for maintainers capable of building a release.

## Build LMCTL

To build LMCTL (to distribute/release), you need to build a whl, the `build.py` script handles this for you:

```
python3 build.py
```

The `.whl` file will be created in the `dist` directory at the root of the project. This `.whl` file can be transferred and used to install this version of LMCTL with pip elsewhere.

```
cp dist/lmctl-3.0.0.dev0-py3-none-any.whl another-location/
python3 -m pip install another-location/lmctl-3.0.0.dev0-py3-none-any.whl
```

# Next Steps

Check out [testing](testing.md)