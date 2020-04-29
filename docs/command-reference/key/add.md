# key add

## Description

Add a shared infrastructure key

## Usage

```
lmctl key add [OPTIONS] ENVIRONMENT NAME
```

## Arguments

| Name        | Description                                                                         | Default | Example      |
| ----------- | ----------------------------------------------------------------------------------- | ------- | ------------ |
| Environment | name of the environment from the LMCTL configuration file to create the key on      | -       | dev          |
| Name        | name of the new shared infrastructure key to be added                               | -       | TestKey      |

## Options

| Name                          | Description                                                                                                                          | Default                       | Example                                  |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--config`                    | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `--pwd`                       | password used for authenticating with LM (only required if LM is secure and no password has been included in the configuration file) | -                             | --pwd secret                             |
| `-u`, `--public`              | Optional path to the file containing the public key (usually .pub)                                                                   | -                             | -u myKey.pub                          |
| `-i`, `--private`             | Optional path to the file containing the private key (usually .pem)                                                                  | -                             | -i myKey.pem                          |
| `-d`, `--description`         | Description of the infrastructure key                                                                                              | -                             | -d 'my shared key'                            |
| `-f`, `--format`              | format of output [table, yaml, json]                                                                                                 | table                         | --f yaml                                 |
