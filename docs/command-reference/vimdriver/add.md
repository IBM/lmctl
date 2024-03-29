# vimdriver add

## Description

Add a VIM driver to a CP4NA orchestration environment

## Usage

```
lmctl vimdriver add [OPTIONS] ENVIRONMENT
```

## Arguments

| Name        | Description                                                                           | Default | Example |
| ----------- | ------------------------------------------------------------------------------------- | ------- | ------- |
| Environment | name of the environment from the LMCTL configuration file to create the VIM driver on | -       | dev     |

## Options

| Name             | Description                                                                                                                          | Default                       | Example                                  |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--config`       | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `--pwd`          | password used for authenticating with CP4NA orchestration (only required if CP4NA orchestration is secure and no password has been included in the configuration file) | -                             | --pwd secret                             |
| `--type`         | Infrastructure type of the VIM driver to add                                                                                         | Openstack                     | --type Openstack                         |
| `--url`          | url of VIM driver to add                                                                                                             | -                             | --url http://os-vim-driver:8292          |
| `-f`, `--format` | format of output [table, yaml, json]                                                                                                 | table                         | --f yaml                                 |
| `--certificate` | Filename of a file containing the public certificate of the VIM driver (if SSL enabled) | - | --certificate vim-driver.cert |