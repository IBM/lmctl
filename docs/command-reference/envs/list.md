# env list

## Description

List all available environments from an LMCTL configuration file. Uses the configuration file set on the `LMCONFIG` environment variable unless an alternative is provided with the `--config` option.

## Usage

```
lmctl env list [OPTIONS]
```

## Options

| Name       | Description                                                                                               | Default | Example                                  |
| ---------- | --------------------------------------------------------------------------------------------------------- | ------- | ---------------------------------------- |
| `--config` | path to an LMCTL configuration file to use instead of the file specified on LMCONFIG environment variable | -       | --config /home/user/my_lmctl_config.yaml |
