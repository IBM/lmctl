# use env

## Description

Change the active environment (default environment used by commands). This will modify the `active_environment` field in your configuration file.

## Usage

```
lmctl use env [NAME]
```

## Arguments

| Name        | Description                                        | Default | Example                    |
| ----------- | -------------------------------------------------- | ------- | -------------------------- |
| Name | Name of an environment from your configuration file to be used as the active environment | -       | dev     |

## Examples

```
# Without an active environment, commands require the "-e" or "--environment" option
lmctl get descriptor -e dev

# Make the environment named "dev" active
lmctl use env dev

# Commands will now use "dev" by default
lmctl get descriptor
```