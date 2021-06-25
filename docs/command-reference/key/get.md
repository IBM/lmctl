# key get

## Description

Display information about a  shared Infrastructure Key by name

## Usage

```
lmctl key get [OPTIONS] ENVIRONMENT NAME
```

## Arguments

| Name        | Description                                                                        | Default | Example      |
| ----------- | ---------------------------------------------------------------------------------- | ------- | ------------ |
| Environment | name of the environment from the LMCTL configuration file to get the key from      | -       | dev          |
| Name        | name of the shared infrastructure key to get                                       | -       | TestKey      |

## Options

| Name             | Description                                                                                                                          | Default                       | Example                                  |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--config`       | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `--pwd`          | password used for authenticating with CP4NA orchestration (only required if CP4NA orchestration is secure and no password has been included in the configuration file) | -                             | --pwd secret                             |
| `-f`, `--format` | format of output [table, yaml, json]                                                                                                 | table                         | --f yaml                                 |
