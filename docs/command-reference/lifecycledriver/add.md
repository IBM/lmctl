# lifecycledriver add

## Description

Add a lifecycle driver to a CP4NA orchestration environment

## Usage

```
lmctl lifecycledriver add [OPTIONS] ENVIRONMENT
```

## Arguments

| Name        | Description                                                                                 | Default | Example |
| ----------- | ------------------------------------------------------------------------------------------- | ------- | ------- |
| Environment | name of the environment from the LMCTL configuration file to create the lifecycle driver on | -       | dev     |

## Options

| Name             | Description                                                                                                                          | Default                       | Example                                    |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ------------------------------------------ |
| `--config`       | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml   |
| `--pwd`          | password used for authenticating with CP4NA orchestration (only required if CP4NA orchestration is secure and no password has been included in the configuration file) | -                             | --pwd secret                               |
| `--type`         | Lifecycle type of the driver to add                                                                                                  | Ansible                       | --type Ansible                             |
| `--url`          | url of lifecycle driver to add                                                                                                       | -                             | --url http://ansible-lifecycle-driver:8293 |
| `-f`, `--format` | format of output [table, yaml, json]                                                                                                 | table                         | --f yaml                                   |
| `--certificate` | Filename of a file containing the public certificate of the lifecycle driver (if SSL enabled) | - | --certificate lifecycle-driver.cert |