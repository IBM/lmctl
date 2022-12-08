# LMCTL Command Line Configuration

LMCTL configuration is written as a YAML formatted file and can exist anywhere on the local file system. By default, LMCTL checks for a file at `<home directory>/.lmctl/config.yaml`, however you may configure an alternative location by setting the `LMCONFIG` environment variable to the intended path.

Table of contents:
- [Initialise configuration file](#initialise-new-configuration-file)
- [Environment Groups](#environment-groups)
  - [CP4NA orchestration Configuration](#cp4na-orchestration-configuration)
  - [Ansible RM](#ansible-rm)

## Initialise configuration file

> If you use `lmctl login` then you can skip this section

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

LMCTL can be used to access one or more CP4NA orchestration and/or Resource Manager (RM) instances. To do so, it must be configured with access addresses and credentials.

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

You may also choose an environment group to be the `active_environment`. By doing so, this environment will be considered the default and used on any command which expects an environment name as an argument or option.

```
active_environment: dev
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

Try `lmctl get descriptors`, `lmctl get descriptor -e dev` and `lmctl get descriptor -e prod` to observe the difference.

The `active_environment` value can be changed anytime from the command line with `lmctl use env`:

```
lmctl use env prod
```

## CP4NA orchestration Configuration

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
      ###############
      #  General    #
      ###############
      
      ## The full HTTP(s) address used to access the API gateway (Ishtar route) of your TNCO instance
      address: https://ishtar-route.ocp.example.com

      ## Set to true if TNCO is secure and requires authentication to use the APIs
      secure: True

      #####################################################################
      #  Zen Authentication                                               #
      #  Required if "secure" is true and not using Oauth or Token #
      #####################################################################
      
      # Indicate environment is using Zen
      auth_mode: zen
      
      ## The full HTTP(s) address and path used to access the Zen authentication APIs E.g. https://<hostname>/icp4d-api/v1/authorize
      auth_address: https://cpd-lifecycle-manager.apps.example.com/icp4d-api/v1/authorize

      ## The username to authenticate with
      username: example-user

      ## The API key for the above user
      #api_key: enter-your-api-key

      #####################################################
      # Oauth Authentication                              #
      #####################################################
     
      # Indicate the environment is using oauth
      #auth_mode: oauth 

      #=========================#
      # Oauth Option 1:         #
      # TNCO Client credentials #
      #=========================#

      ## ID of the client credentials to authenticate with
      #client_id: LmClient
      
      ## Secret for the above client
      #client_secret: enter-your-secret

      #=========================#
      # Oauth Option 2:         #
      # TNCO User based access  #
      #=========================#

      ## ID of the client credentials with password scope authentication enabled
      #client_id: LmClient

      ## Secret for the above client
      #client_secret: enter-your-secret

      ## The username to authenticate with
      #username: jack

      ## The password for the above user
      #password: enter-your-pass
      
      #=================================#
      # Oauth Option 3:                 #
      # "unofficial" user based access  #
      #=================================#

      ## Using username/password without client credentials is not supported by TNCO so could stop functioning in any future release
      ## The username to authenticate with
      #username: jack
      
      ## The password for the above user
      #password: enter-your-pass

      #####################################################
      # Token Authentication                              #
      #####################################################
     
      # Indicate the environment is using token based auth
      #auth_mode: token 

      #token: enter-your-token

      #####################################################
      # Okta Authentication                              #
      #####################################################
     
      # Indicate the environment is using okta
      #auth_mode: okta 

      #=========================#
      # Okta Option 1:         #
      # Okta User based access  #
      #=========================#

      ## ID of the client credentials with password scope authentication enabled
      #client_id: LmClient

      ## Secret for the above client
      #client_secret: enter-your-secret

      ## The username to authenticate with
      #username: jack

      ## The password for the above user
      #password: enter-your-pass

      ## Authorization server's id of Okta server
      #auth_server_id : default
      
      ## Scopes you grant for Okta users
      #scope: lmctl

      #####################################################
      # Token Authentication                              #
      #####################################################
     
      # Indicate the environment is using token based auth
      #auth_mode: token 

      #token: enter-your-token
```

## Ansible RM

> Deprecated

Multiple Ansible RM environments may be included in a group under the `arm` key. It is important that the name given to each Ansible RM matches the name used to onboard it to the CP4NA orchestration environment in the same group.

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
  testing:
    description: an example test environment
    tnco:
      address: https://app.lm:32443
      secure: true
      auth_address: https://ui.lm:32443
      username: jack
  okta:
    tnco:
      address: https://Na4d.example
      auth_address: https://dev.okta.com
      auth_mode: okta
      auth_server_id: default
      client_id: LmClient
      scope: lmctl
      secure: true
      username: jack
```
