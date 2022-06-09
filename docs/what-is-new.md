# What's new in LMCTL 3.0

:tada:

Contents:
- New in 3.0.0
  - :file_folder: [Default LMCTL config file location](#default-lmctl-config-file-location)
  - :muscle: [Expanded Command Capabilities](#expanded-command-capabilities)
  - :snake: [CP4NA orchestration Python Client](#cp4na-python-client)
  - :wrench: [CP4NA orchestration Environment Improvements](#cp4na-environment-address-improvements)
  - :closed_lock_with_key: [Client Credential Authentication](#client-credential-authentication)
  - :point_right: [Ping CP4NA orchestration environment to check configuration](#ping-cp4na-environment-to-check-configuration)
- New in 3.1.0
  - :closed_lock_with_key: [Login Command](#login-command)
  - :closed_lock_with_key: [Token Authentication](#token-authentication)
  - :file_folder: [Default Active Environment](#active-environment)
  - :clipboard: [Log Directory](#log-directory)
- New in 3.2.0
  - :closed_lock_with_key: [Zen Authentication](#zen-authentication)

# 3.0.0

# Default LMCTL config file location

Tired of making sure the `LMCONFIG` environment variable is set? :sleeping: 

In v3.0, LMCTL will now check for a configuration file at `<Home directory>/.lmctl/config.yaml`. 

Create/move your configuration file into this location OR create a new one with the new `config` commands:

```
lmctl create config

# Check the option on this command:
# lmctl create config --help
```

Check your configuration file is loaded (from the correct place) with:

```
lmctl get config --print-path
```

> Note: if set, the path on the `LMCONFIG` environment variable takes precedence over the default location

Read more about configuring LMCTL in the [configuration section of the user guide](configure.md)

# Expanded Command Capabilities

In v3.0 the number of available commands has increased significantly :muscle:

You can now manage descriptors, assemblies, behaviour scenarios and much more. 

You'll also notice a change in command style, with the action coming before the entity type:

- Old command style: `lmctl resourcedriver get my-env some-driver-id`
- New command style: `lmctl get resourcedriver some-driver-id -e my-env`

We hope, by moving the verb to the front of the command, the readability of the command increases. Also, by moving the environment name to an option, it reduces the confusion between this value and the name/ID of the object being interaced with (e.g. which arg is the resourcedriver ID and which is the environment name?)

> Note: the `lmctl project` and `lmctl pkg` commands have not yet been changed, so they still accept the environment name as an argument

Don't worry, if you've got scripts using the old style, they will still work! (But they are deprecated, so refactor these when possible)

Every entity in CP4NA orchestration has been grouped by the actions allowed on them. Check out the actions available:

```
lmctl --help
```

Pick an action and check the CP4NA orchestration entities you can interact with:

```
lmctl get --help
```

The arguments/options for each entity are similar in style but there are differences, so be sure to check the help page for each:

```
lmctl get descriptor --help
```

Read more about commands in the [command reference section of the user guide](command-reference/index.md). More specifically read about the [Action Based CLI](command-reference/action-based-cli.md)

# CP4NA Python Client

For command line users this part will appear boring but for Python developers looking to interact with CP4NA orchestration from their favourite language, you're in luck! 

The previous client module was not built with external use in mind (everything from the `lmctl.drivers` package). In v3.0, we've added a new client module (`lmctl.client`) to be imported and used in Python code outside of LMCTL!

What does this mean? It means you can write Python code to interact with CP4NA orchestration:

```
from lmctl.client import client_builder

cp4na_client = client_builder().address('https://cp4na-api-host').client_credentials_auth('LmClient', 'admin').build()

# Retrieve a descriptor (as a dictionary)
descriptor = cp4na_client.descriptors.get('assembly::my-descriptor::1.0')

# Update
descriptor['description'] = 'I just updated this description with the LMCTL client library'
cp4na_client.descriptors.update(descriptor)
```

Read more about the Python client capabilities in the [client section of the user guide](client/index.md)

# CP4NA environment address improvements

Previously, when configuring a target CP4NA environment you would use multiple properties to set the address: 

```yaml
environments:
  default:
    lm:
      host: 127.0.0.1
      port: 32443
      protocol: https
      secure: True
      username: jack
```

In v3.0, we've added shorter configuration options. For example, you can use `address` to configure `host`, `port` and `protocol` in one:

```yaml
environments:
  default:
    lm:
      address: https://127.0.0.1:32443
      secure: True
      username: jack
```

# Client Credential Authentication

Before v3.0 you could only authenticate with a secure CP4NA environment using client credential-less username/password. In short, this means authenticating with just a username/password. Although allowed, this is not a supported CP4NA orchestration authentication method so could disappear at any time. 

In v3.0, we've added support for legitimate username/password authentication in combination with client credentials AND support for client credentials authentication.

Don't worry, the existing method works so your configuration files don't need any immediate updates. 

However, if you wish to use the new methods, the example below shows the three different types of authentication:

```yaml
environments:
  # The old way
  the-old-way:
    lm:
      address: https://my-cp4na-env
      secure: True
      username: jack
      password: some-pass
      auth_address: https://my-cp4na-ui

  # Valid Username/Password authentication
  valid-username-pass-env:
    lm:
      address: https://my-cp4na-env
      secure: True
      # Legit username/password access (update values with valid credentials for your environment)
      client_id: NimrodClient
      client_secret: some-secret
      username: jack
      password: some-pass
 
  # Client credential access
  client-env:
    lm:
      address: https://my-cp4na-env
      secure: True
      client_id: LmClient
      client_secret: some-secret
```

# Ping CP4NA environment to check configuration

Check you've configured your environment(s) correctly by testing the connection:

```
lmctl ping env <name of env>
```

# 3.1.0

# Login Command

The new `lmctl login` command makes it easier to add environments to your config file without modifying YAML files.

```
lmctl login https://my-cp4na-env --auth-address https://my-cp4na-ui --username almadmin --password my-password
```

By default, this command will authenticate, obtain a short-lived access token, then save this environment with the token in the configuration file (rather than your credentials). This means you'll have to `login` again when the token expires. If you'd rather avoid this headache, you can save the credentials in the config file with `--save-creds`. 

```
lmctl login https://my-cp4na-env --auth-address https://my-cp4na-ui --username almadmin --password my-password --save-creds
```

Read more about the login command in the [getting started guide](getting-started.md) and/or [login command reference](command-reference/login.md).

# Token Authentication

On it's own, this feature is fairly unimpressive, but it can be useful in combination with the `lmctl login` command. You may now authenticate with an existing access token, instead of persisting credentials in the LMCTL config file:

```
environments:
  dev:
    tnco:
      address: https://my-cp4na-env
      secure: True
      token: <a-jwt-token>
```

# Active Environment

Most commands require the name of an environment from the configuration file, e.g.:

```
lmctl get descriptors -e my-env
```

This becomes very repetitive, especially when frequently using the same environment. 

In LMCTL 3.1, you may now set an `active_environment` in the configuration file. The active environment is used on any command where the relevant environment argument or option was not supplied. 

```
active_environment: dev
environments:
  my-env:
    tnco:
       ...
  joes-env:
    tnco:
       ...
```

With the above config, the previous command can be shortened to:

```
lmctl get descriptors 
```

> We may still specify the environment when we need to use an alternative `lmctl get descriptors -e joes-env`

The `active_environment` value can also be toggled from the command line, with the `use` command:

```
lmctl use env joes-env
```

# Log Directory

Previously, LMCTL created/appened to a `lmctl.log` file in the current directory. This meant there would be a new log file in each directory you used LMCTL from, which can be a pain, particularly when dealing with LMCTL projects.

In v3.1.0+, LMCTL will now create all logs files at `<Home directory>/.lmctl/logs`. 

You can ask LMCTL for the exact path on your machine using the new `logdir` command:

```
lmctl logdir
```

# 3.2.0

# Zen Authentication

When using Cloud Pak for Network Automation v2.2+ (CP4NA) you may be required to authenticate with Zen credentials, a common authentication framework for IBM Cloudpaks. 

The configuration file and login command now support `auth_mode: zen`, allowing you to authenticate with your Zen credentials: 

```
lmctl login $API_GATEWAY --zen --auth-address $ZEN_AUTH_ADDRESS --username admin --api-key FdpmmyFIIslv0s3eN9tCTKeYAt3457pnmrTZacvo
```

For more details, check out the [Getting Started](getting-started.md#zen-authentication) guide or the [Login Command Reference](command-reference/login.md).

# 3.3.0

# Netconf, Restconf and Sol005 Driver project support

You can now manage Resource projects intended for the Netconf, Restconf or Sol005 resource drivers. 

```
lmctl project create --type ETSI_NS --param driver sol005
```

For more details, check out the [create project command reference](command-reference/project/create.md) and the [guide to managing projects](projects/overview.md).