# pkg inspect

## Description

Inspect a package to see the contents to be pushed into a target CP4NA orchestration environment

## Usage

```
lmctl pkg inspect [OPTIONS] PACKAGE
```

## Arguments

| Name        | Description                                                          | Default | Example                    |
| ----------- | -------------------------------------------------------------------- | ------- | -------------------------- |
| Package     | file path of the package to be inspected                                | -       | /home/user/example-1.0.tgz |

## Options

| Name        | Description                                                                                                                          | Default                       | Example                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------- | ---------------------------------------- |
| `--config`  | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable                            | LMCONFIG environment variable | --config /home/user/my_lmctl_config.yaml |
| `-f`, `--format` | format of output [yaml, json]                                                                                                 | yaml                         | --f yaml                                 |
