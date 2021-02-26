# Action Based CLI

Table of contents:
- [Actions](#actions)
- [Targets](#targets)
- [Common Create/Update Options](#common-create/update-options)
  - [-f and --set options](#-f-and---set-options)
  - [What attributes can I include in a file or with --set?](#what-attributes-can-i-include-in-a-file-or-with---set?)
- [Common Get Options](#common-get-options)
  - [-f as reference](#-f-as-reference)
- [Common Delete Options](#common-delete-options)
  - [--ignore-missing](#--ignore-missing)

# Actions

LMCTL features a set of common **actions** which can be performed on supported **targets**. Each action is represented by an LMCTL command. For example, LMCTL supports actions such as `get`, `create`, `delete`:

```
lmctl get --help
lmctl create --help
lmctl delete --help
```

# Targets

Targets represent different types of objects which LMCTL may manage (may be an object in a TNCO environment or local, such as config file and environment settings).

The `--help` option will display the list of available targets for the given action.

```
lmctl get --help
```

Output:
```
Usage: lmctl get [OPTIONS] COMMAND [ARGS]...

  Display details of supported objects

Options:
  --help  Show this message and exit.

Commands:
  assembly            Get Assembly
  assemblyconfig      Get Assembly Configuration
  behaviourproject    Get Behaviour Project
  config              Get the active LMCTL Configuration file
  deploymentlocation  Get Deployment Location
  descriptor          Get Descriptor
  descriptortemplate  Get Descriptor Template
  env                 Get LMCTL Environments from active config file
  infrastructurekey   Get Infrastructure Key
  process             Get the status of an Assembly Process
  resourcedriver      Get Resource Driver
  resourcemanager     Get Resource Manager
  scenario            Get Scenario
  scenarioexecution   Get Scenario Execution
```

The target is a subcommand of the action command. Each target subcommand may have different arguments and options depending on the object type. 

```
lmctl get descriptor --help

lmctl get resourcedriver --help
```

The arguments and options may differ however, there are several which are re-used with the exact same behaviour in order to provide consistent functionality. 

For example, almost all `get` targets feature the `-o, --output` option, which allows you to determine if the result should be printed as YAML, JSON or a table (default):

```
lmctl get descriptor -e dev-env
```

Output:
```
| Name                                            | Description         |
|-------------------------------------------------+---------------------|
| resource::example::1.0                          | An example resource |
```

```
lmctl get descriptor -e dev-env -o yaml
```

Output:
```
items:
- name: resource::example::1.0
  description: An example resource
```

The following sections describe other arguments/options which are similar across all targets:

# Common Create/Update Options

## -f and --set options

The `-f, --file` and `--set` options are frequently used by actions which will result in the modification of an object, such as `create` or `update`.

With `-f`, you may reference a local file which contains either YAML or JSON representation of the object you are attemping to create/update. 

For example, with a `descriptor.yaml` including the following content:

```yaml
name: assembly::example::1.0
description: An example descriptor
properties:
  propA:
    type: string
```

We can create this descriptor in a TNCO environment with:

```
lmctl create descriptor -e dev-env -f descriptor.yaml
```

The `--set` option instead allows you to pass attributes of the object on the command line. For example we could create the some of the above descriptor without any file:

```
lmctl create descriptor -e frosty --set name=assembly::example::1.0 --set "description=An example descriptor"
```

We are not able to add `properties` as this is a nested object. As a result, `--set` is only recommended when creating simple objects.

## What attributes can I include in a file or with --set?

Any field accepted on the Rest API for the target object type may be used. In simple terms, when using `-f`, you are writing the request body that will be sent. 

If you're still unsure, many targets support the `genfile` command, which will generate an example file for you:

```
lmctl genfile assembly
```

Output:
```
Generated file: assembly.yaml
```

# Common Get Options

## -o, --output

This option allows you to determine the format of the output on the console. By default, most commands will use the `table` format:

```
lmctl get descriptor -e dev-env
```

Output:
```
| Name                                            | Description         |
|-------------------------------------------------+---------------------|
| resource::example::1.0                          | An example resource |
```

You can use `-o` to print YAML instead:

```
lmctl get descriptor -e dev-env -o yaml
```

Output:
```
items:
- name: resource::example::1.0
  description: An example resource
```

Alternatively, print JSON:

```
lmctl get descriptor -e dev-env -o json
```

Output:
```
{
  "items": [
    "name": "resource::example::1.0",
    "description": "An example resource"
  ]
}
```

YAML and JSON options are convenient for pushing the result to a file:

```
lmctl get descriptor -e dev-env -o yaml > descriptors.yaml
```

## -f as reference

Another benefit of `-f, --file` is the ability to re-use the file. Many action commands which target an existing object can use `-f` to determine the instance.

For example, if you've previously created an Assembly with a file (`my-assembly.yaml`), you can also remove it with the file:

```
lmctl delete assembly -e dev-env -f my-assembly.yaml
```

The file is parsed to resolve the name of the Assembly to delete.

# Common Delete Options

## --ignore-missing

When you attempt to delete an object that does not exist, you will get an error similar to:

```
TNCO error occurred: DELETE request to https://9.20.192.196/api/catalog/descriptors/assembly::example::1.0 failed: status=404, message=No descriptor found with name: assembly::example::1.0
```

In many circumstances you may be happy to accept that if the object does not exist, then the delete result should be positive. When this is the case, include the `--ignore-missing` option:

```
lmctl delete descriptor -e dev-env assembly::example::1.0 --ignore-missing
```

Output:
```
No Descriptor found with name assembly::testexample::1.0 (ignoring)
```

The command will let you know the object was not found but will exit with a 0 code (success) instead of raising an error.

> Note: care should be taken when using `--ignore-missing`. A spelling mistake in the ID/name of the target object could be overlooked as the command will pass.