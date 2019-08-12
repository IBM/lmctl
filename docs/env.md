# Environments

Many of the `lmctl` commands require a target LM environment. These environments are defined in a configuration file that is either passed to `lmctl` on the command line when needed or specified using an `LMCONFIG` environment variable. 

## Commands

### List

The `list` command will read the given configuration file and list the names of it's defined enviroments

To view the environments from the configuration file specified on the `LMCONFIG` environment variable just run `lmctl env list`.

```
$ lmctl env list
Available environments:
  - dev: My private dev environment
  - testing: Central hosted testing environment
```

To view the environments from an alternative configuration file specify the path to it on the `--config` option.

```
$ lmctl env list --config alternative-config.yaml
Available enviroments:
  - pre-prod: Central hosted pre-prod environment
```