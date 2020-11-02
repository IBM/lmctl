# TNCO Python Client

You may have used LMCTL from the command line but it may also be used in Python based scripts/applications as a client module for TNCO.

## Quick Import

To use LMCTL in your code, [install it with pip](../install.md) then start importing:

```python
from lmctl.client import client_builder

tnco_client = client_builder().address('https://tnco-api-host').client_credentials_auth('LmClient', 'admin').build()
```

For details on how to include LMCTL as a dependency so it's installed for all users of your project/application see [Add LMCTL to Python project](add-to-python-project.md)

## Building a Client

A TNCOClient can be configured in a number of ways however, the recommended way is to use TNCOClientBuilder:

```python
from lmctl.client import client_builder

tnco_client = client_builder().address('https://tnco-api-host').client_credentials_auth('LmClient', 'admin').build()
```

Same as:

```python
from lmctl.client import TNCOClientBuilder

tnco_client = TNCOClientBuilder().address('https://tnco-api-host').client_credentials_auth('LmClient', 'admin').build()
```

## Build Client from existing command line configuration

To load a TNCOClient from the same configuration used on the command line, you should use the `lmctl.config` package:

```python
from lmctl.config import get_global_config

lmctl_config = get_global_config()

# Get the TNCO instance from one of the environments
tnco_env = lmctl_config.environments['default'].tnco

# Get client
tnco_client = tnco_env.build_client()
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

The majority of the APIs are similar in style and try to support the same core functions: 

- all - get all of a particular type of entity
- get - get a particular entity by ID/name
- create - create a new entity
- update - update an existing entity
- delete - delete an existing entity

Not all APIs support these functions, you should consult each class in `lmctl.client.api` to discover the functions available on each API.

# Examples

To get an idea of how the TNCOClient can be used, read through the [examples](examples.md) section.