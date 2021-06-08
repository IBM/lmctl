# Getting Started with LMCTL

# Prepare Python 3

LMCTL requires <a href="https://www.python.org" target="_blank">Python 3.6+</a>.

> Currently, testing is performed on versions 3.6, 3.7, 3.8 and 3.9.

On Ubuntu, you can use the following:

```
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.9
python3.9 --version
```

For other operating systems, follow the relevant <a href="https://www.python.org/downloads/" target="_blank">installation instructions</a>

We recommend installing <a href="https://virtualenv.pypa.io/en/latest/" target="_blank">Virtualenv</a> and creating an isolated environment for LMCTL:

```
python3 -m pip install virtualenv
python3 -m virtualenv lmctl-env
```

This will create an environment in a directory named `lmctl-env` (change the name to a value of your choosing). Once created, the virtual environment can be activated anytime with:

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

Why use a virtual environment?

- keeps all dependencies used by LMCTL isolated from other Python applications on your machine
- allow you to have alternate versions installed, in two separate environments, which is useful when there is a new major version of TNCO and LMCTL, with potential non-backward compatible changes

# Install LMCTL

Activate a virtual environment if you intend to use one, then install LMCTL with pip:

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

# LMCTL Login

LMCTL requires credentials to access your TNCO environment. 

The most efficient method of configuring LMCTL is to use the `lmctl login` with the API gateway (Ishtar) address for your environment. On most OCP installations, the API gateway address can be retrieved with:

```
API_GATEWAY=$(oc get route alm-ishtar -o jsonpath='{.spec.host}')
```

The credentials may be provided in different combinations but the most convenient methods are described below. Check out the [login command documentation](command-reference/login.md) to view more detailed information on all combinations.

First, try login with the same username and password you use to access the TNCO user interface (UI). You will need to provide the UI address (Nimrod) for your environment, on most OCP installations, the UI address can be retrieved with:

```
UI_ADDRESS=$(oc get route alm-nimrod -o jsonpath='{.spec.host}')
```

Run `lmctl login`, changing the `--username` and `--password` values to the correct credentials for your environment:

```
lmctl login $API_GATEWAY --auth-address $UI_ADDRESS --username almadmin --password password
```

> You may omit the `--password` option and LMCTL will prompt for this as hidden input instead.

This command will perform the following:

- Authenticate and obtain an access token for the target environment using the provided credentials
- Create an LMCTL configuration file at `~/.lmctl/config.yaml`, if one does not already exist
- Save the environments address(es) and access token to this configuration file with an environment name of `default`.
- Make this environment the "active" choice, which makes it the default used on most commands

You should see output similar to:

```
Login success
Updating config at: /home/myuser/.lmctl/config.yaml
```

You can test access is ready using `ping`:

```
lmctl env ping
```

If the output of this command ends with `TNCO (ALM) tests passed! ✅` then you're almost ready to go. 

Before you go, it's worth considering the following:

**Save Credentials**

The token was saved in the config file, rather than the username/password. Tokens are often short lived, meaning you will have to re-run `login` when it expires.
Alternatively, you may choose to save the credentials in the config file (plain text), by adding `--save-creds` to the login command. This allows LMCTL to re-authenticate on your behalf:

```
lmctl login $API_GATEWAY --auth-address $UI_ADDRESS --username almadmin --password password --save-creds
```

Check the difference in the configuration by running `lmctl get config` before and after this command. 

**Multiple Environments**

You may login in to more than one environment at any one time. Just run `login` again but include the `--name` option, otherwise the environment will be saved with the same default value as the first. 

```
lmctl login DEV_API_GATEWAY --auth-address DEV_UI_ADDRESS --username almadmin --password password --name dev
lmctl login TEST_API_GATEWAY --auth-address TEST_UI_ADDRESS --username almadmin --password password --name test
lmctl login PROD_API_GATEWAY --auth-address PROD_UI_ADDRESS --username almadmin --password password --name prod
```

Only one environment is considered "active", which makes it the default. However, most commands allow you to specify an environment by name. Run the following commands and check out the address reported in the output:

```
# Ping dev
lmctl ping env dev

# Ping test
lmctl ping env test

# Ping prod
lmctl ping env prod

# Ping active env (last logged in)
lmctl ping env
```

You can switch the active environment at any time with `lmctl use`:

```
lmctl use env dev

# Ping active env (will use "dev")
lmctl ping env
```

You can read more about the configuration options available with LMCTL in the [configure](configure.md) section of this documentation.
