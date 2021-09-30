# ping env

## Description

Test connection with Environments from active config file

Connection is tested by making requests to a few pre-selected APIs on the configured CP4NA orchestration.

## Usage

```
lmctl ping env [OPTIONS] [NAME]
```

## Arguments

| Name        | Description                                        | Default | Example                    |
| ----------- | -------------------------------------------------- | ------- | -------------------------- |
| Name | Name of an environment from your configuration file | -       | dev     |

## Options

| Name             | Description                                                                                                                          | Default                       | Example                                    |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ------------------------------------------ |
| `--client-secret`       | CP4NA orchestration client secret used for authenticating. Only required if the environment is secure and a client_id has been included in your configuration file with no client_secret | - | --client-secret secret   |
| `--pwd`          | CP4NA orchestration password used for authenticating. Only required if the environment is secure and a username has been included in your configuration file with no password  | -                             | --pwd secret                               |
