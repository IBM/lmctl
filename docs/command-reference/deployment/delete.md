# deployment delete

## Description

Remove a deployment location from a CP4NA orchestration environment

## Usage

```
lmctl deployment delete [OPTIONS] ENVIRONMENT NAME
```

## Arguments

| Name        | Description                                                                           | Default | Example      |
| ----------- | ------------------------------------------------------------------------------------- | ------- | ------------ |
| Environment | name of the environment from the LMCTL configuration file to remove the location from | -       | dev          |
| Name        | name of the deployment location to be removed                                         | -       | TestLocation |

## Options

| Name       | Description                                                                                                                          | Default                       | Example                                  |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--config` | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `--pwd`    | password used for authenticating with CP4NA orchestration (only required if CP4NA orchestration is secure and no password has been included in the configuration file) | -                             | --pwd secret                             |
