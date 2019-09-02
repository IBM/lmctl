# deployment delete

## Description

Remove a deployment location from a LM environment

## Usage

```
lmctl deployment add [OPTIONS] ENVIRONMENT NAME
```

## Arguments

| Name        | Description                                                                           | Default | Example      |
| ----------- | ------------------------------------------------------------------------------------- | ------- | ------------ |
| Environment | name of the environment from the LMCTL configuration file to remove the location from | -       | dev          |
| Name        | name of the new deployment location to be removed                                     | -       | TestLocation |

## Options

| Name       | Description                                                                                                                          | Default                       | Example                                  |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--config` | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `--pwd`    | password used for authenticating with LM (only required if LM is secure and no password has been included in the configuration file) | -                             | --pwd secret                             |
