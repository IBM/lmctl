# LMCTL Command Line Configuration

LMCTL configuration is written as a YAML formatted file and can exist anywhere on the local file system. By default, LMCTL checks for a file at `<home directory>/.lmctl/config.yaml`, however you may configure an alternative location by setting the `LMCONFIG` environment variable to the intended path.

Table of contents:
- [Initialise configuration file](#initialise-new-configuration-file)
- [Environment Groups](#environment-groups)
  - [TNCO (ALM) Configuration](#tnco-(alm)-configuration)
  - [Ansible RM](#ansible-rm)

## Initialise configuration file

To initialise a new configuration file, at the default location, run the following:

```
lmctl create config
```

If you do not intend to use the default location add the "--path" option with a free path:

```
lmctl create config --path lmctl-config.yaml
```

Open the file to view it's initial content. A `default` environment has been added, which you should update (and rename, if you like) with the details required to access your TNCO environment. You can read more about these details in later chapters.

```
vi ~/.lmctl/config.yaml

# Or if created with --path
vi lmctl-config.yaml
```

If you previously used the "--path" option to create the file in a non-default location then you will need to set the `LMCONFIG` environment variable.

```
export LMCONFIG=~/lmctl-config.yaml
```

On Windows:

```
set LMCONFIG=%HomeDrive%%HomePath%\lmctl-config.yaml
```

Once the file has been modified, you will be able to view it's content with:

```
lmctl get config
```

# Environment Groups

LMCTL can be used to access one or more TNCO (ALM) and/or Resource Manager (RM) instances. To do so, it must be configured with access addresses and credentials.

As any single TNCO environment may have many related RMs, the individual instances are described together in an environment group.

> Note: TNCO comes with a built-in Resource Manager, which you do not need to add access address/credentials for.

Each group has:

- a name used to identify it in commands
- a description for informative use
- a single TNCO instance
- zero to many RM instances (if using the Ansible RM)

Each environment group should be included in the LMCTL configuration file as a key object under `environments`.

```
environments:
  dev:
    description: a dev environment
    tnco:
      ...tnco details...
  test:
    description: a test environment
    tnco:
      ...tnco details...
  prod:
    description: a prod environment
    tnco:
      ...tnco details...
```

## TNCO (ALM) Configuration

The TNCO environment in a group must be provided under the key `tnco`, `lm` or `alm` with the following properties:

```
environments:
  example:
    description: a short example environment
    tnco:
      address: https://app.lm:32443
      secure: true
      username: jack
      password:
  example_with_details:
    description: an example environment
    tnco:
      ### General 

      ## The full HTTP(s) address used to access the API gateway of your TNCO instance
      address: https://app.lm

      ## Set to true if the environment is secure and requires authentication to use the APIs
      ## - Optional
      ## - Default: false
      secure: true

      ### Authentication
      ### Required if "secure" is true.

      # Auth Option 1: TNCO Client credentials
      # ID of the client credentials to authenticate with
      client_id: LmClient
      # Secret for the above client
      client_secret: enter-your-secret

      # Auth Option 2: TNCO User based access
      # ID of the client credentials with password scope authentication enabled
      #client_id: LmClient
      # Secret for the above client
      #client_secret: enter-your-secret
      # The username to authenticate with
      #username: jack
      # The password for the above user
      #password: enter-your-pass
      
      # Auth Option 3: TNCO "unofficial" user based access. 
      # Using username/password without client credentials is not supported by TNCO so could stop functioning in any future release
      # The username to authenticate with
      #username: jack
      # The password for the above user
      #password: enter-your-pass

      ### Deprecated properties maintained for backwards compatibility

      ## When not using "address", access to LM is determined by combining <protocol>://<host>:<port>/<path>/
      ## The host address of the LM API
      ## - Required
      #host: app.lm
      ## The port of the LM API. Leave empty if LM is accessible through host only
      ## - Optional
      #port: 32443
      ## The path of the LM API. Leave empty if LM is accessible on the root path of the host and port given
      ## - Optional
      #path: /my-lm
      ## Set if the environment is accessed through HTTPs or HTTP
      ## - Optional
      ## - Default: https
      #protocol: https
      ## Access to LM Auth is determined by combining <protocol>://<auth_host>:<auth_port>/ui/ (for pre 2.1 LM environments it will use <protocol>://<auth_host>:<auth_port>/)
      ## The host address of the LM Username Auth API
      ## - Optional
      ## - Default: uses value of 'host'
      #auth_host: ui.lm
      ## The port of the LM Username Auth API
      ## - Optional
      ## - Default: uses value of 'port'
      #auth_port: 32443
```

## Ansible RM

Multiple Ansible RM environments may be included in a group under the `arm` key. It is important that the name given to each Ansible RM matches the name used to onboard it to the LM environment in the same group.

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
    tnco:
      address: https://192.168.100.50:32443
      secure: true
      client_id: LmClient
      username: jack
    arm:
      defaultRm:
        host: 192.168.100.50
        port: 31081
        protocol: https
  testing:
    description: an example test environment
    lm:
      address: https://app.lm:32443
      secure: true
      auth_address: https://ui.lm:32443
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
