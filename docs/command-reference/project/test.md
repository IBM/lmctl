# project test

## Description

Execute the behavior tests of the project

## Usage

```
lmctl project test [OPTIONS] ENVIRONMENT
```

## Arguments

| Name        | Description                                                                   | Default | Example |
| ----------- | ----------------------------------------------------------------------------- | ------- | ------- |
| Environment | name of the environment from the LMCTL configuration file to push and test on | -       | dev     |

## Options

| Name        | Description                                                                                                                          | Default                       | Example                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--project` | path to the project directory (which includes a valid lmproject.yaml file)                                                           | ./ (current directory)        | --project /home/user/projectA            |
| `--config`  | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `--pwd`     | password used for authenticating with LM (only required if LM is secure and no password has been included in the configuration file) | -                             | --pwd secret                             |
| `--armname` | if an Ansible RM Resource is included, this must be set with the name of ARM to push to                                              | defaultrm                     | --armname edgerm                         |
| `--tests`   | Specify individual tests to execute                                                                                                  | '\*' (all tests)              | --armname edgerm                         |
