# CP4NA Client Examples

## Prerequisite

In all examples, it is assumed we have already created a CP4NA client:

```python
from lmctl.client import client_builder

cp4na_client = client_builder().address('https://cp4na-ishtar.example.com').client_credentials_auth('LmClient', 'admin').build()
``` 

## Create an Assembly

```python
import time
def wait_for_process_to_complete(process_id):
    process = cp4na_client.processes.get(process_id)
    process_status = None
    while process_status not in ['Completed', 'Cancelled', 'Failed']:
        # Wait 5 seconds
        time.sleep(5)
        process_status = process['status']
    if process_status != 'Completed':
        reason = process['statusReason']
        raise Exception(f'Process did not complete successfully: {process_status}, reason={reason}')

# Send intent to create an Assembly (using  dict)
process_id = cp4na_client.assemblies.intent_create({
    'assemblyName': 'Example',
    'descriptorName': 'assembly::my-descriptor::1.0',
    'intendedState': 'Active',
    'properties': {
        'resourceManager': 'brent',
        'deploymentLocation': 'core'
    }
})
wait_for_process_to_complete(process_id)

# Send intent to delete an Assembly (using model object)
from lmctl.client.models import DeleteAssemblyIntent

intent = DeleteAssemblyIntent().set_assembly_name('Example')
process_id = cp4na_client.assemblies.intent_delete(intent)
```

## CRUD a descriptor

```python
# Create a descriptor
cp4na_client.descriptors.create({
    'name': 'assembly::my-descriptor::1.0',
    'description': 'An example',
    'composition': {}
})

# Retrieve a descriptor (as a dictionary)
descriptor = cp4na_client.descriptors.get('assembly::my-descriptor::1.0')

# Update
descriptor['description'] = 'I just updated this description with the LMCTL client library'
cp4na_client.descriptors.update(descriptor)

# Delete
cp4na_client.descriptors.delete('assembly::my-descriptor::1.0')
```

## Execute Scenarios

```python
# Execute a scenario by ID

execution_id = cp4na_client.behaviour_scenario_execs.execute(scenario_id='08783de2-dded-4014-8abe-38eb99401755')

execution = cp4na_client.behaviour_scenario_execs.get(execution_id)
execution_status = None
while execution_status not in ['PASS', 'ABORTED', 'FAIL']:
    # Wait 5 seconds
    time.sleep(5)
    execution_status = execution['status']

if execution_status != 'PASS':
    reason = execution['error']
    raise Exception(f'Execution did not complete successfully: {execution_status}, reason={reason})
```

```python
# Execute a scenario with request parameters (if provided Assembly is required)

execution_id = cp4na_client.behaviour_scenario_execs.execute(execution_request={
    'scenarioId': '08783de2-dded-4014-8abe-38eb99401755'
})

execution = cp4na_client.behaviour_scenario_execs.get(execution_id)
execution_status = None
while execution_status not in ['PASS', 'ABORTED', 'FAIL']:
    # Wait 5 seconds
    time.sleep(5)
    execution_status = execution['status']

if execution_status != 'PASS':
    reason = execution['error']
    raise Exception(f'Execution did not complete successfully: {execution_status}, reason={reason})
```