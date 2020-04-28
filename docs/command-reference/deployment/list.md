# deployment list

## Description

List the deployment locations on a LM environment

## Usage

```
lmctl deployment list [OPTIONS] ENVIRONMENT
```

## Arguments

| Name        | Description                                                                           | Default | Example      |
| ----------- | ------------------------------------------------------------------------------------- | ------- | ------------ |
| Environment | name of the environment from the LMCTL configuration file                             | -       | dev          |

## Options

| Name             | Description                                                                                                                          | Default                       | Example                                  |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--config`       | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `--pwd`          | password used for authenticating with LM (only required if LM is secure and no password has been included in the configuration file) | -                             | --pwd secret                             |
| `-f`, `--format` | format of output [table, yaml, json]                                                                                                 | table                         | -f yaml                                  |
