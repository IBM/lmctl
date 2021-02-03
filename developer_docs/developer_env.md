# Developer Environment

To develop LMCTL you need Python v3.6.9+ (install using instructions suitable for your operating system).

## Pip and Setuptools

Once Python is installed, make sure you have the latest pip, setuptools and wheel:

```
python3 -m pip install -U pip setuptools wheel
```


## Virtualenv

It's recommended that you create a virtualenv to manage an isolated Python env for this project:

Install virtualenv:

```
python3 -m pip install virtualenv
```

Create a virtualenv (you can do this from the root of your LMCTL clone):

```
python3 -m virtualenv env
```

Activate this virtualenv in your terminal when working on LMCTL:

(Unix/Mac)
```
source env/bin/activate
```

(Windows Powershell)
```
Scripts\activate.ps1
```

(Windows Other)
```
Scripts\activate
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

# Next Steps

Check out [testing](testing.md)