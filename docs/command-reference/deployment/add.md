# deployment add

## Description

Add a deployment location to a CP4NA orchestration environment

## Usage

```
lmctl deployment add [OPTIONS] ENVIRONMENT NAME
```

## Arguments

| Name        | Description                                                                         | Default | Example      |
| ----------- | ----------------------------------------------------------------------------------- | ------- | ------------ |
| Environment | name of the environment from the LMCTL configuration file to create the location on | -       | dev          |
| Name        | name of the new deployment location to be added                                     | -       | TestLocation |

## Options

| Name                          | Description                                                                                                                          | Default                       | Example                                  |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--config`                    | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `--pwd`                       | password used for authenticating with CP4NA orchestration (only required if CP4NA orchestration is secure and no password has been included in the configuration file) | -                             | --pwd secret                             |
| `-r`, `--rm`                  | name of the Resource Manager to associate the deployment location with                                                               | -                             | --rm defaultrm                           |
| `-i`, `--infrastructure-type` | Optional type of infrastructure managed by the Deployment Location                                                                   | -                             | -i Openstack                             |
| `-d`, `--description`         | Description of the deployment location                                                                                               | -                             | -d 'my openstack location'               |
| `-p`, `--properties`          | path to a yaml or json formated file containing properties for the Deployment Location                                               | -                             | -p test_location_props.yaml              |
| `-f`, `--format`              | format of output [table, yaml, json]                                                                                                 | table                         | --f yaml                                 |
