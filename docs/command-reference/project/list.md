# project list

## Description

List element(s) of a Project

## Usage

```
lmctl project list [OPTIONS] ELEMENT
```

## Arguments

| Name    | Description                                                | Default | Example |
| ------- | ---------------------------------------------------------- | ------- | ------- |
| Element | Type of elements to be listed. Supported elements: 'tests' | -       | tests   |

## Options

| Name        | Description                                                                | Default                | Example                       |
| ----------- | -------------------------------------------------------------------------- | ---------------------- | ----------------------------- |
| `--project` | path to the project directory (which includes a valid lmproject.yaml file) | ./ (current directory) | --project /home/user/projectA |
