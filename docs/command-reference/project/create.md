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
| `--param` | Parameters to be passed to the creation of each Project. The values allowed here should take the form "param_name param_value". The parameters allowed for each Project depend on the `--type` and `--rm` chosen (see [params](#params)) | --param lifecycle ansible --param inf openstack |

### Params

Params for the root Project take the format "param_name param_value", whilst params for Subprojects (those set on `--contains`) use the format "subproject_name.param_name param_value". 

For example, the following sets the lifecycle param to "ansible" for the root Project but "sol003" for the Subproject named A:

```
--contains Resource::brent A --param lifecycle ansible --param A.lifecycle sol003
```

The following table describes the known params available: 

| Name | Description | Options | Default | 
| ---- | ---- | --- | --- |
| lifecycle | Used only when `--type Resource` and `--rm brent` (or `--contains Resource::brent`). This parameter guides the creation of the Project (or Subproject) with example files for the intended lifecycle driver | ansible, sol003 | ansible |
| inf | Used only when `--type Resource` and `--rm brent` (or `--contains Resource::brent`). This parameter guides the creation of the Project (or Subproject) with example files for the intended infrastructure driver | openstack | openstack |