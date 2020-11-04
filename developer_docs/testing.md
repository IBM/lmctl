
# Unit Tests

LMCTL is tested with the `unittest` python module. Run the unit tests from this repository with:

```
python3 -m unittest discover -s tests.unit
```

This will auto-discover the tests in the `tests/unit` directory.

# Integration Tests

Integration tests for the TNCO client and commands may be executed against a TNCO environment.

To run the tests, you need to create a copy of `tests/integration/test_properties.yaml`

```
cp tests/integration/test_properties.yaml local_test_properties.yaml
```

> Note: we make a copy to avoid accidentally committing your environment details. `local_test_properties.yaml` is already in the `.gitignore` file so please use this name

Edit the contents of this file to set the configuration details for your environment.

```
vi local_test_properties.yaml
```

The `LMCTL_TEST_PROPS` environment variable is used to control the location of the properties file used in the tests. Set this variable to the path to your `local_test_properties.yaml` file

```
export LMCTL_TEST_PROPS=$(pwd)/local_test_properties.yaml
```

You're ready to run the full (or partial) set of integration tests:

```
# Run all integration tests
python3 -m unittest discover -s tests.integration

# Run ONLY the CLI tests
python3 -m unittest discover -s tests.integration.cli

# Run ONLY the client tests
python3 -m unittest discover -s tests.integration.client
```
