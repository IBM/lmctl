# project create

## Description

Create a new project in a target directory

## Usage

```
lmctl project create [OPTIONS] [LOCATION]
```

## Arguments

| Name     | Description                                            | Default                | Example             |
| -------- | ------------------------------------------------------ | ---------------------- | ------------------- |
| Location | path to the directory the project should be created in | ./ (current directory) | /home/user/projectA |

## Options

| Name                      | Description                                                                                                                                                                                                                                                                                                         | Default                 | Example                                                      |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------ |
| `--name`                  | name of the service managed in the project                                                                                                                                                                                                                                                                          | (target directory name) | --name myexample                                             |
| `--version`               | version of the service managed in the project                                                                                                                                                                                                                                                                       | 1.0                     | --version 2.1                                                |
| `--type`, `--servicetype` | type of service managed in this project (Assembly or Resource)                                                                                                                                                                                                                                                      | Assembly                | --type Resource                                              |
| `--rm`                    | Resource projects only - the type of Resource Manager this Resource supports                                                                                                                                                                                                                                        | lm                      | --rm ansiblerm, --rm lm (brent)                              |
| `--contains`, `--vnfc`    | Subprojects to initiate under this project. Must specify 2 values separated by spaces: type name. For a Resource subproject, you may set the rm by including it it in the type value using the format \'type::rm\' e.g. Resource::ansiblerm. If no rm is set then the value of the --rm option will be used instead |                         | --contains Assembly subA --contains Resource::ansiblerm subB |
