# CP4NA Python Client

You may have used LMCTL from the command line but it may also be used in Python based scripts/applications as a client module for CP4NA.

## Quick Import

To use LMCTL in your code, [install it with pip](../install.md) then start importing:

```python
from lmctl.client import client_builder

cp4na_client = client_builder().address('cp4na-ishtar.example.com').client_credentials_auth('LmClient', 'admin').build()
```

For details on how to include LMCTL as a dependency, so it can be installed for all users of your project/application see [Add LMCTL to Python project](add-to-python-project.md)

## Building a Client

A CP4NA client can be configured in a number of ways. The recommended way is to use `client_builder`:

```python
from lmctl.client import client_builder

cp4na_client = client_builder().address('cp4na-ishtar.example.com').client_credentials_auth('LmClient', 'admin').build()
```

This builder provides methods to configure the following types of authentication:

```python
# Zen Authentication (CP4NA 2.2+ on OCP)
cp4na_client = client_builder().address('cp4na-ishtar.example.com').cloudpak_api_key_auth(username='MyUser', api_key='MyKey', cp_front_door_address='cpd-lifecycle-manager.apps.example.com').build()

# Client Credentials (non-Cloud Pak environments)
cp4na_client = client_builder().address('cp4na-ishtar.example.com').client_credentials_auth(client_id='LmClient', client_secret='admin').build()

# UI Username/Password (non-Cloud Pak environments)
cp4na_client = client_builder().address('cp4na-ishtar.example.com').legacy_user_pass_auth(username='almadmin', password='mypass', legacy_auth_address='cp4na-nimrod.example.com').build()

# Client based Username/Password (non-Cloud Pak environments)
cp4na_client = client_builder().address('cp4na-ishtar.example.com').legacy_user_pass_auth(client_id='LmClient', client_secret='admin', username='almadmin', password='mypass').build()

```

## Build Client from existing command line configuration

To build a client from the same configuration file used on the command line, you may import and use `get_global_config` from the `lmctl.config` package:

```python
from lmctl.config import get_global_config

lmctl_config = get_global_config()

# Get the TNCO instance from one of the environments
tnco_env = lmctl_config.environments['default'].tnco

# Get client
cp4na_client = tnco_env.build_client()
```

To load from a configuration file from a non-default location, pass a file path to `get_global_config`

```python
from lmctl.config import get_global_config

lmctl_config = get_global_config('/path/to/my/config.yaml)
```

# TNCO Client APIs

The TNCOClient is organised by the APIs available from TNCO. Each API client is available as a property on the base TNCOClient:
    - auth
    - assemblies
    - behaviour_assembly_confs
    - behaviour_projects
    - behaviour_scenarios
    - behaviour_scenario_execs
    - deployment_locations
    - descriptors
    - descriptor_templates
    - processes
    - resource_drivers
    - resource_packages
    - resource_managers
    - shared_inf_keys

For example:

```python
descriptor_apis = tnco_client.descriptors
```

The APIs are similar in style and support the same core functions: 

- all - get all of a particular type of entity
- get - get a particular entity by ID/name
- create - create a new entity
- update - update an existing entity
- delete - delete an existing entity

> Not all APIs support these functions, you should consult each class in `lmctl.client.api` to discover the functions available on each API.

# Examples

To get an idea of how the TNCOClient can be used, read through the [examples](examples.md) section.