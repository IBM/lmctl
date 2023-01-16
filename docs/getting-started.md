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

# Login to Cloud Pak for Network Automation

LMCTL requires credentials to access the orchestration component of your Cloud Pak for Network Automation (CP4NA) environment. 

The most efficient method of configuring LMCTL is to use the `lmctl login` with the API gateway (Ishtar Route) address for your environment. On most OCP installations, this can be retrieved with:

```
API_GATEWAY=https://$(oc get route cp4na-o-ishtar -o jsonpath='{.spec.host}')
```

The `login` command will perform the following:

- Authenticate and obtain an access token for the target environment using the provided credentials
- Create an LMCTL configuration file at `~/.lmctl/config.yaml`, if one does not already exist
- Save the environments address(es) and access token to this configuration file with an environment name of `default`.
- Make this environment the "active" choice, which makes it the default used on most commands

The credentials for your environment may be provided in a few different combinations but the most convenient methods are described below:

- [CP4NA 2.2+ on OCP with Zen](#zen-authentication)
- [CP4NA on Kubernetes with Oauth](#oauth-authentication)

Check out the [login command documentation](command-reference/login.md) to view more detailed information on each combination.

## Zen Authentication

> CP4NA 2.2+ on OCP only

You will need to provide the Zen authorization address. On most OCP installations, this can be retrieved with:

```
ZEN_AUTH_ADDRESS=$(oc get orchestration default -o jsonpath='{.status.uiendpoints.orchestration}')/icp4d-api/v1/authorize
```

You'll also need to obtain an API key for your Zen user. This can retrieved by visiting the CP4NA UI (address returned by `oc get orchestration default -o jsonpath='{.status.uiendpoints.orchestration}'`) and logging in with with your Zen username and password.

Access `Profile and Settings` from the user menu icon located in the top right section of the navigation header. From the profile page you can generate your API key by clicking on the `API Key` link in the top right and then `Generate new key`. 

![Zen API Key](images/zen-api-key.png)

You may be warned that generating a new key will invalidate any previous keys. Either use your existing key (if known) or click `Generate` to create a new one. Make a copy of this key and use it to login with lmctl:

```
lmctl login $API_GATEWAY --zen --auth-address $ZEN_AUTH_ADDRESS --username admin --api-key FdpmmyFIIslv0s3eN9tCTKeYAt3457pnmrTZacvo
```

You should see output similar to:

```
Login success
Updating config at: /home/myuser/.lmctl/config.yaml
```

You can test access is ready using `ping`:

```
lmctl ping env
```

If the output of this command ends with `CP4NA orchestration tests passed! ✅` then you're ready to go. 

Eventually your access token will expire, resulting in authentication errors when using lmctl. When this occurs, run `login` again to reauthenticate OR check out the [Automation Reauthentication](#automatic-reauthentication) section below to save your credentials in your config file so lmctl may automatically re-authenticate when the token expires.

## Oauth Authentication

> For any environment where Zen authentication is not used

First, try logging in with the same username and password you use to access the CP4NA orchestration user interface (UI). You will need to provide the UI address (Nimrod Route) for your environment. On most OCP installations, this can be retrieved with:

```
UI_ADDRESS=https://$(oc get route cp4na-o-nimrod -o jsonpath='{.spec.host}')
```

Run `lmctl login`, changing the `--username` and `--password` values to valid credentials for your environment:

```
lmctl login $API_GATEWAY --auth-address $UI_ADDRESS --username almadmin --password password
```

> You may omit the `--password` option and LMCTL will prompt for this as hidden input instead.

You should see output similar to:

```
Login success
Updating config at: /home/myuser/.lmctl/config.yaml
```

You can test access is ready using `ping`:

```
lmctl ping env
```

If the output of this command ends with `CP4NA orchestration tests passed! ✅` then you're ready to go. 

Eventually your access token will expire, resulting in authentication errors when using lmctl. When this occurs, run `login` again to reauthenticate OR check out the [Automatic Reauthentication](#automatic-reauthentication) section below to save your credentials in the lmctl config file so lmctl may automatically re-authenticate you when the token expires.

## Okta Authentication

> For any environment where Okta authentication is used

Run `lmctl login`, changing the values to valid parameters for your environment:

```
lmctl login $API_GATEWAY --okta --client <Client> --client-secret <secret> -u <user> -p <password> --scope <scope>  --auth-address https://<okta server endpoint> --auth-server-id <auth_server_id>
```

> You may omit the `--password` option and LMCTL will prompt for this as hidden input instead.

You should see output similar to:

```
Login success
Updating config at: /home/myuser/.lmctl/config.yaml
```

You can test access is ready using `ping`:

```
lmctl ping env
```

If the output of this command ends with `CP4NA orchestration tests passed! ✅` then you're ready to go. 

Eventually your access token will expire, resulting in authentication errors when using lmctl. When this occurs, run `login` again to reauthenticate OR check out the [Automatic Reauthentication](#automatic-reauthentication) section below to save your credentials in the lmctl config file so lmctl may automatically re-authenticate you when the token expires.


## Automatic Reauthentication

On login success, the resulting access token is saved in the config file, rather than the username/password. Tokens are often short lived, meaning you will have to re-run `login` when it expires.

Alternatively, you may choose to save the credentials in the config file (plain text), by adding `--save-creds` to the login command. This allows LMCTL to re-authenticate on your behalf:

```
lmctl login $API_GATEWAY --auth-address $UI_ADDRESS --username almadmin --password password --save-creds
```

Check the difference in the configuration by running `lmctl get config` before and after this command. 

## Multiple Environments 

You may login in to more than one environment at any one time. Just run `login` again but include the `--name` option, otherwise the environment will be saved with the same default value as the first. 

```
lmctl login DEV_API_GATEWAY --auth-address DEV_UI_ADDRESS --username almadmin --password password --name dev
lmctl login TEST_API_GATEWAY --auth-address TEST_UI_ADDRESS --username almadmin --password password --name test
lmctl login PROD_API_GATEWAY --auth-address PROD_UI_ADDRESS --username almadmin --password password --name prod
```

Only one environment is considered "active", which makes it the default. However, most commands allow you to specify an environment by name. Run the following commands and check out the address reported in the output:

```
lmctl ping env dev

lmctl ping env test

lmctl ping env prod

lmctl ping env
```

You can switch the active environment at any time with `lmctl use`:

```
lmctl use env dev

lmctl ping env
```

## Next Steps

You can read more about the configuration options available with LMCTL in the [configure](configure.md) section of this documentation.

To learn more about creating Assembly/Resource projects, including how to integrate a project with an existing Assembly you have developed using the designer user interface, check out the [projects](projects/overview.md) section of this documentation.

Otherwise, check out the [Command Reference](command-reference/index.md) to learn more about the commands LMCTL provides.
