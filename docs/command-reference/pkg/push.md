# pkg push

## Description

Push a previously built package to a CP4NA orchestration environment

## Usage

```
lmctl pkg push [OPTIONS] PACKAGE ENVIRONMENT
```

## Arguments

| Name        | Description                                                          | Default | Example                    |
| ----------- | -------------------------------------------------------------------- | ------- | -------------------------- |
| Package     | file path of the package to be pushed                                | -       | /home/user/example-1.0.tgz |
| Environment | name of the environment from the LMCTL configuration file to push to | -       | dev                        |

## Options

| Name        | Description                                                                                                                          | Default                       | Example                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--config`  | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `--pwd`     | password used for authenticating with CP4NA orchestration (only required if CP4NA orchestration is secure and no password has been included in the configuration file) | -                             | --pwd secret                             |
| `--armname` | if an Ansible RM Resource is included, this must be set with the name of ARM to push to                                              | defaultrm                     | --armname edgerm                         |
| `--armname` | if an Ansible RM Resource is included, this must be set with the name of ARM to push to                                              | defaultrm                     | --armname edgerm                         |
| `--og`, `--object-group` | Name of the Object Group to perform the request in  | -                     | --og mygroup                         |
| `--ogid`, `--object-group-id` | ID of the Object Group to perform the request in | -                     | --ogid 73a4db24-0f3a-4d3e-8699-9c37de17823e              |
