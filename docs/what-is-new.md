# What's new in LMCTL 3.0

:tada:

Contents:
- :file_folder: [Default LMCTL config file location](#default-lmctl-config-file-location)
- :muscle: [Expanded Command Capabilities](#expanded-command-capabilities)
- :snake: [TNCO Python Client](#tnco-python-client)
- :wrench: [TNCO Environment Improvements](#tnco-environment-address-improvements)
- :closed_lock_with_key: [Client Credential Authentication](#client-credential-authentication)
- :point_right: [Ping TNCO environment to check configuration](#ping-tnco-environment-to-check-configuration)
- :smirk: [New Brand Support](#new-brand-support)

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

Every entity in TNCO has been grouped by the actions allowed on them. Check out the actions available:

```
lmctl --help
```

Pick an action and check the TNCO entities you can interact with:

```
lmctl get --help
```

The arguments/options for each entity are similar in style but there are differences, so be sure to check the help page for each:

```
lmctl get descriptor --help
```

Read more about commands in the [command reference section of the user guide](command-reference/index.md)

# TNCO Python Client

For command line users this part will appear boring but for Python developers looking to interact with TNCO from their favourite language, you're in luck! 

The previous client module was not built with external use in mind (everything from the `lmctl.drivers` package). In v3.0, we've added a new client module (`lmctl.client`) to be imported and used in Python code outside of LMCTL!

What does this mean? It means you can write Python code to interact with TNCO:

```
from lmctl.client import client_builder

tnco_client = client_builder().address('https://tnco-api-host').client_credentials_auth('LmClient', 'admin').build()

# Retrieve a descriptor (as a dictionary)
descriptor = tnco_client.descriptors.get('assembly::my-descriptor::1.0')

# Update
descriptor['description'] = 'I just updated this description with the LMCTL client library'
tnco_client.descriptors.update(descriptor)
```

Read more about the Python client capabilities in the [client section of the user guide](client/index.md)

# TNCO environment address improvements

Previously, when configuring a target TNCO (ALM) environment you would use multiple properties to set the address: 

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

Before v3.0 you could only authenticate with a secure TNCO environment using client credential-less username/password. In short, this means authenticating with just a username/password. Although allowed, this is not a supported TNCO authentication method so could disappear at any time. 

In v3.0, we've added support for legitimate username/password authentication in combination with client credentials AND support for client credentials authentication.

Don't worry, the existing method works so your configuration files don't need any immediate updates. 

However, if you wish to use the new methods, the example below shows the three different types of authentication:

```yaml
environments:
  # The old way
  the-old-way:
    lm:
      address: https://my-tnco-env
      secure: True
      username: jack
      password: some-pass

  # Valid Username/Password authentication
  valid-username-pass-env:
    lm:
      address: https://my-tnco-env
      secure: True
      # Legit username/password access (update values with valid credentials for your environment)
      client_id: NimrodClient
      client_secret: some-secret
      username: jack
      password: some-pass
 
  # Client credential access
  client-env:
    lm:
      address: https://my-tnco-env
      secure: True
      client_id: LmClient
      client_secret: some-secret
```

# Ping TNCO environment to check configuration

Check you've configured your environment(s) correctly by testing the connection:

```
lmctl ping env <name of env>
```

# New Brand Support

The tool remains named `lmctl` however, as `LM` is now part of `TNCO`, we've added support for `tnco` in some places.

In your LMCTL configuration file, you may use `tnco` instead of `alm`/`lm` in the `environments` section. 

In the below example, we show 2 environments, which are fundamentally the same, however one uses `tnco` instead of `lm`:

```yaml
environments:
  envA:
    lm:
      host: 127.0.0.1
      port: 32443
      protocol: https
      secure: True
      username: jack
  envB:
    tnco:
      host: 127.0.0.1
      port: 32443
      protocol: https
      secure: True
      username: jack
```