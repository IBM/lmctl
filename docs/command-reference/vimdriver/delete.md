# vimdriver delete

## Description

Remove a VIM driver from a CP4NA orchestration environment by ID (or by infrastructure type)

## Usage

```
lmctl vimdriver delete [OPTIONS] ENVIRONMENT [DRIVER-ID]
```

## Arguments

| Name        | Description                                                                             | Default | Example                              |
| ----------- | --------------------------------------------------------------------------------------- | ------- | ------------------------------------ |
| Environment | name of the environment from the LMCTL configuration file to remove the VIM driver from | -       | dev                                  |
| Driver-ID   | (Optional) ID of the VIM driver to be removed                                           | -       | f801fa73-6278-42f0-b5d3-a0fe40675327 |

## Options

| Name       | Description                                                                                                                          | Default                       | Example                                  |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--config` | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `--pwd`    | password used for authenticating with CP4NA orchestration (only required if CP4NA orchestration is secure and no password has been included in the configuration file) | -                             | --pwd secret                             |
| `--type`   | Infrastructure type used to identify the VIM driver to remove. Use this instead of the driver-id argument                            | -                             | --type Openstack                         |
