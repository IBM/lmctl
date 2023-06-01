# project push

## Description

Push project to a CP4NA orchestration environment

## Usage

```
lmctl project push [OPTIONS] ENVIRONMENT
```

## Arguments

| Name        | Description                                                          | Default | Example |
| ----------- | -------------------------------------------------------------------- | ------- | ------- |
| Environment | name of the environment from the LMCTL configuration file to push to | -       | dev     |

## Options

| Name        | Description                                                                                                                          | Default                       | Example                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--project` | path to the project directory (which includes a valid lmproject.yaml file)                                                           | ./ (current directory)        | --project /home/user/projectA            |
| `--config`  | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `--pwd`     | password used for authenticating with CP4NA orchestration (only required if CP4NA orchestration is secure and no password has been included in the configuration file) | -                             | --pwd secret                             |
| `--armname` | if an Ansible RM Resource is included, this must be set with the name of ARM to push to                                              | defaultrm                     | --armname edgerm                         |
| `--autocorrect` | allow validation warnings and errors to be autocorrected if supported (each warning/error will inform you if this is possible) | False | --autocorrect |
| `--og`, `--object-group` | Name of the Object Group to perform the request in  | -                     | --og mygroup                         |
| `--ogid`, `--object-group-id` | ID of the Object Group to perform the request in | -                     | --ogid 73a4db24-0f3a-4d3e-8699-9c37de17823e              |
