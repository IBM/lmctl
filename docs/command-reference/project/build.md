# project build

## Description

Build distributable package for a project

## Usage

```
lmctl project build [OPTIONS]
```

## Options

| Name        | Description                                                                | Default                | Example                       |
| ----------- | -------------------------------------------------------------------------- | ---------------------- | ----------------------------- |
| `--project` | path to the project directory (which includes a valid lmproject.yaml file) | ./ (current directory) | --project /home/user/projectA |
| `--autocorrect` | allow validation warnings and errors to be autocorrected if supported (each warning/error will inform you if this is possible) | False | --autocorrect |