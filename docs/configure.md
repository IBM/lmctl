# LMCTL Command Line Configuration

LMCTL configuration is written as a YAML formatted file and can exist anywhere on the local file system. By default, LMCTL checks for a file at `<home directory>/.lmctl/config.yaml`, however you may configure an alternative location by setting the `LMCONFIG` environment variable to the intended path.

Table of contents:
- [LMCTL Command Line Configuration](#lmctl-command-line-configuration)
  - [Initialise configuration file](#initialise-configuration-file)
- [Environment Groups](#environment-groups)
  - [CP4NA orchestration Configuration](#cp4na-orchestration-configuration)
  - [Ansible RM](#ansible-rm)
- [Complete Configuration Example](#complete-configuration-example)

## Initialise configuration file

> It is recommended that you use the `lmctl login` command instead of manually creating the configuration file. If you use the login command you can skip this section.

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

As any single CP4NA orchestration environment may have many related RMs, the individual instances are described together in an environment group.

> Note: CP4NA orchestration comes with a built-in Resource Manager, which you do not need to add access address/credentials for.

Each group has:

- a name used to identify it in commands
- a description for informative use
- a single CP4NA orchestration instance (known as TNCO)
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

This section gives an overview of the configuration properties of LMCTL. It is e xpected most users do not need to read through this section as it is more efficient to use "lmctl login" to configure an environment, rather than modifying properties in a file. 

The CP4NA environment in a group must be provided under the key `tnco`, `lm` or `alm` with the following properties:

```
environments:
  simple_example:
    description: a short example environment
    tnco:
      address: ishtar-route.ocp.example.com
      token: <your-access-token>
  
  example_with_details:
    description: an example environment
    tnco:
      ###############
      #  General    #
      ###############
      
      ## The full address used to access the API gateway (Ishtar route) of your CP4NA instance.
      ## HTTPs is assumed by default so it's not necessary to include the protocol
      address: ishtar-route.ocp.example.com


      #####################################################################
      # Token Authentication (recommended auth mode for all environments) #
      #####################################################################
     
      ## Indicate the environment is using token based auth
      auth_mode: token 

      ## Use "lmctl login" to obtain a token by entering your username/password/api-key for the environment
      token: enter-your-access-token

      #####################################################################
      #  Cloud Pak Authentication                                         #
      #  Required unless specifying a Token                               #
      #####################################################################
      
      ## Indicate environment is using the auth mode for Cloud Paks
      ## "cp-api-key" is a rename of the "zen" value previously used here. Using the value "zen" is still supported but will eventually be removed
      #auth_mode: cp-api-key 
      
      ## The full address used to access the Cloud Pak front door 
      ## It is no longer necessary to add the "icp4d-api/v1/authorize" endpoint here
      #auth_address: cpd-lifecycle-manager.apps.example.com

      ## The username to authenticate with
      #username: example-user

      ## The API key for the above user - it is not recommended to specify this in a file as it is stored in plain text.
      ## You can omit this value and each command call will prompt you for it instead.
      ## Alternatively use "lmctl login" to login once and store an access token instead (auth_mode: token). Only the token is held in plain text.
      ## The token will eventually expire and you will need to login again
      #api_key: enter-your-api-key

      #####################################################
      # Oauth Authentication (non-CP4NA environments)     #
      #####################################################
     
      ## Indicate the environment is using oauth
      #auth_mode: oauth 

      #=========================#
      # Oauth Option 1:         #
      # TNCO Client credentials #
      #=========================#

      ## ID of the client credentials to authenticate with
      #client_id: LmClient
      
      ## Secret for the above client
      ## You can omit this value and each command call will prompt you for it instead.
      ## Alternatively use "lmctl login" to login once and store an access token instead (auth_mode: token). Only the token is held in plain text.
      ## The token will eventually expire and you will need to login again
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
      ## You can omit this value and each command call will prompt you for it instead.
      ## Alternatively use "lmctl login" to login once and store an access token instead (auth_mode: token). Only the token is held in plain text.
      ## The token will eventually expire and you will need to login again
      #password: enter-your-pass
      
      #=================================#
      # Oauth Option 3:                 #
      # "unofficial" user based access  #
      #=================================#

      ## Using username/password without client credentials is not supported by TNCO so could stop functioning in any future release
      ## The username to authenticate with
      #username: jack
      
      ## The password for the above user
      ## You can omit this value and each command call will prompt you for it instead.
      ## Alternatively use "lmctl login" to login once and store an access token instead (auth_mode: token). Only the token is held in plain text.
      ## The token will eventually expire and you will need to login again
      #password: enter-your-pass
      
      ## GUI address required to support this method of authentication
      #auth_address: nimrod-route.ocp.example.com

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
      client_id: admin
  testing:
    description: an example test environment
    tnco:
      address: 192.168.100.50:32443
      auth_address: 192.168.100.50:32444
      username: jack
```
