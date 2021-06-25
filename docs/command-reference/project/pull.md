# project pull

## Description

Pull contents of the Project artifacts from a CP4NA orchestration environment

## Usage

```
lmctl project pull [OPTIONS] ENVIRONMENT
```

## Arguments

| Name        | Description                                                            | Default | Example |
| ----------- | ---------------------------------------------------------------------- | ------- | ------- |
| Environment | name of the environment from the LMCTL configuration file to pull from | -       | dev     |

## Options

| Name        | Description                                                                                                                          | Default                       | Example                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--project` | path to the project directory (which includes a valid lmproject.yaml file)                                                           | ./ (current directory)        | --project /home/user/projectA            |
| `--config`  | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `--pwd`     | password used for authenticating with CP4NA orchestration (only required if CP4NA orchestration is secure and no password has been included in the configuration file) | -                             | --pwd secret                             |
