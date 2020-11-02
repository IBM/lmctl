# TNCO Client Examples

## Prerequisite

In all examples, it is assumed we have already created a TNCOClient:

```python
from lmctl.client import client_builder

tnco_client = client_builder().address('https://tnco-api-host').client_credentials_auth('LmClient', 'admin').build()
```

## Get and update a descriptor

```python
# Retrieve a descriptor (as a dictionary)
descriptor = tnco_client.descriptors.get('assembly::my-descriptor::1.0')

# Update
descriptor['description'] = 'I just updated this description with the LMCTL client library'
tnco_client.descriptors.update(descriptor)
```

## Create an Assembly

```python
# Send intent to create an Assembly
process_id = tnco_client.assemblies.intent_create({
    'assemblyName': 'Example',
    'descriptorName': 'assembly::my-descriptor::1.0',
    'intendedState': 'Active',
    'properties': {
        'resourceManager': 'brent',
        'deploymentLocation': 'core'
    }
})

# Wait for process to complete
process = tnco_client.processes.get(process_id)
process_status = None
import time
while process_status not in ['Completed', 'Cancelled', 'Failed']:
    # Wait 5 seconds
    time.sleep(5)
    process_status = process['status']
```

