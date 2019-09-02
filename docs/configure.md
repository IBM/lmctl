# Configuration File

LMCTL configuration is provided in a YAML formatted file, that may be created anywhere on the local file system then referenced on each command with the `--config` option or with the `LMCONFIG` environment variable. If both are set, the value of `--config` takes priority over the environment variable.

Create a new file and set the environment variable:

```
touch ~/lmctl-config.yaml
export LMCONFIG=~/lmctl-config.yaml
```

On Windows:

```
type nul > %HomeDrive%%HomePath%\lmctl-config.yaml
set LMCONFIG=%HomeDrive%%HomePath%\lmctl-config.yaml
```

The contents of the configuration file is expected to take the following format:

```
environments:
    ...configuration for environment groups...
```

# Environment Groups

In order for LMCTL to connect to one or more Lifecycle Manager (LM) and/or Resource Manager (RM) instances, it must be configured with access addresses and credentials.

A user should group the RM instances with their owning LM instance in an `environment group`. Each group has:

- a name used to identify it in commands
- a description for informative use
- a single LM instance
- zero to many RM instances

Each environment group should be included in the LMCTL configuration file as a key object under `environments`.

```
environments:
  dev:
    description: a dev environment
  test:
    description: a test environment
  prod:
    description: a prod environment
```

Once you have created an LMCTL configuration file you may view the current environment groups with the `env` command:

```
lmctl env list
```

If `LMCONFIG` is not set:

```
lmctl env list --config /path/to/lmctl-config.yaml
```

## Lifecycle Manager

The LM environment in a group must be provided under `lm` or `alm` with the following properties:

```
environments:
  example:
    description: an example environment
    lm:
      host: app.lm
      port: 32443
      protocol: https
      secure: true
      auth_host: ui.lm
      auth_port: 32443
      username: jack
      password:
  example_with_comments:
    description: an example environment
    lm:
      ## The host address of the LM API
      ## - Required
      host: app.lm

      ## The port of the LM API. Leave empty if LM is accessible through host only
      ## - Optional
      port: 32443

      ## Set if the environment is accessed through HTTPs or HTTP
      ## - Optional
      ## - Default: https
      protocol: https

      ## Set to true if the environment is secure and requires authentication to use the APIs
      ## - Optional
      ## - Default: false
      secure: true

      ## The host address of the LM Username Auth API
      ## - Optional
      ## - Default: uses value of 'host'
      auth_host: ui.lm

      ## The port of the LM Username Auth API
      ## - Optional
      ## - Default: uses value of 'port'
      auth_port: 32443

      ## The username to authenticate with
      ## - Required - if 'secure' is true
      username: jack

      ## The password for the above user
      ## - Optional - only needed if 'secure' is true and
      ##              may be provided on the command line to avoid storing in plain-text
      password:
```

## Ansible RM

Multiple Ansible RM environments may be included in a group under `arm`. It is important that the name given to each Ansible RM matches the name used to onboard it to the LM environment in the same group.

Ansible RM environments have the following properties:

```
environments:
  example:
    arm:
      firstRm:
        host: localhost
        port: 31081
        protocol: https
      secondRm:
        ...repeat...

  example_with_comments:
    arm:
      firstRm:
        ## The host address of the Ansible RM API
        ## - Required
        host: localhost

        ## The port of the Ansible RM API. Leave empty if the RM is accessible through host only
        ## - Optional
        port: 31081

        ## Set if the environment is accessed through HTTPs or HTTP
        ## - Optional
        ## - Default: https
        protocol: https
```

# Complete Configuration Example

```
environments:
  dev:
    description: a local dev environment
    lm:
      host: 192.168.100.50
      port: 32443
      protocol: https
      secure: true
      auth_host: 192.168.100.50
      auth_port: 32443
      username: jack
    arm:
      defaultRm:
        host: 192.168.100.50
        port: 31081
        protocol: https
  testing:
    description: an example test environment
    lm:
      host: app.lm
      port: 32443
      protocol: https
      secure: true
      auth_host: ui.lm
      auth_port: 32443
      username: jack
    arm:
      coreRm:
        host: 10.x.y.z
        port: 31081
        protocol: https
      edgeRm:
        host: 10.x.y.z
        port: 31082
        protocol: https
```
