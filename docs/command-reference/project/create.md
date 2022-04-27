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
| `--type`, `--servicetype` | type of service managed in this project (Assembly, Resource, ETSI_VNF or ETSI_NS)                                                                                               | Assembly                | --type Resource                                              |
| `--rm`                    | Resource projects only - the type of Resource Manager this Resource supports                                                                                                                                                                                                                                        | lm                      | --rm ansiblerm, --rm lm (brent)                              |
| `--contains`, `--vnfc`    | Subprojects to initiate under this project. Must specify 2 values separated by spaces: type name. For a Resource subproject, you may set the rm by including it it in the type value using the format \'type::rm\' e.g. Resource::ansiblerm. If no rm is set then the value of the --rm option will be used instead |                         | --contains Assembly subA --contains Resource::ansiblerm subB |
| `--param` | Parameters to be passed to the creation of each Project. The values allowed here should take the form "param_name param_value". The parameters allowed for each Project depend on the `--type` and `--rm` chosen (see [params](#params)) | --param lifecycle ansible --param inf openstack |

### Params

Params for the root Project take the format "param_name param_value", whilst params for Subprojects (those set on `--contains`) use the format "subproject_name.param_name param_value". 

For example, the following sets the driver param to "ansible" for the root Project but "sol003" for the Subproject named A:

```
--contains Resource::brent A --param driver ansible --param A.driver sol003

```

The following table describes the known params available for all projects: 

| Name | Description | Options | Default | 
| ---- | ---- | --- | --- |
| packaging | Decide if the project will be packaged as a TGZ or CSAR (with TOSCA metadata) | tgz, csar | tgz |

The following table describes the known params available for projects using the `brent` rm type: 

| Name | Description | Options                              | Default | 
| ---- | ---- |------------------------------------------------| --- |
| driver | This parameter guides the creation of the Project (or Subproject) with example files for the intended driver | ansible, sol003, sol005, restconf              | - |
| lifecycle | Deprecated: same as `driver` | ansible, sol003, sol005, restconf, kubernetes, netconf | - |
| inf | This parameter guides the creation of the Project (or Subproject) with example files for a separate driver to be used on Create/Delete | openstack, kubernetes                | - |

If both `driver` and `lifecycle` have not been set then the default for `driver` is set to `ansible` and the default for `inf` is set to `openstack`. This means if you choose to not set any parameters, you will have a Resource which will use the Openstack driver for Create/Delete but Ansible for all other transitions.

Example combinations:

Resource with Openstack driver for Create/Delete (will be included in the generated descriptor) but Ansible driver for all others (only Install is included in the generated descriptor):
```
lmctl project create --type Resource

#Same as
lmctl project create --type Resource --param driver ansible --param inf openstack
```

Resource with Ansible driver for all transitions (only Install is included in the generated descriptor):
```
lmctl project create --type Resource --param driver ansible
```

Resource with Sol003 driver for all transitions (only Install, Configure and Uninstall are included in the generated descriptor):
```
lmctl project create --type Resource --param driver sol003
```

Resource with Sol005 driver for all transitions (only Install, Configure ,Uninstall are included in the generated descriptor):
```
lmctl project create --type Resource --param driver sol005
```

Resource with Restconf driver for all transitions (Create, Update ,Delete are included in the generated descriptor):
```
lmctl project create --type Resource --param driver restconf
```

Resource with Netconf driver for all transitions (Create, Update ,Delete are included in the generated descriptor):
```
lmctl project create --type Resource --param driver netconf
```

Resource with Openstack driver for Create/Delete (will be included in the generated descriptor) but Sol003 driver for all others (only Install, Configure and Uninstall are included in the generated descriptor):
```
lmctl project create --type Resource --param driver sol003 --param inf openstack
```

Resource with Openstack driver for Create/Delete (will be included in the generated descriptor) but Sol005 driver for all others (only Install, Configure and Uninstall are included in the generated descriptor):
```
lmctl project create --type Resource --param driver sol005 --param inf openstack
```


ETSI_VNF with Openstack driver for Create/Delete (will be included in the generated descriptor) but Ansible driver for all others (only Install is included in the generated descriptor):
```
lmctl project create --type ETSI_VNF
```

ETSI_VNF Resource with Sol003 driver for all transitions (only Install, Configure and Uninstall are included in the generated descriptor):
```
lmctl project create --type ETSI_VNF --param driver sol003
```

ETSI_NS Resource with Sol005 driver for all transitions (only Install, Configure and Uninstall are included in the generated descriptor):
```
lmctl project create --type ETSI_NS --param driver sol005
```

### Params for Brent/LM 2.1
The following table describes the known params available for projects using the `brent2.1`/`lm2.1` rm type: 

| Name | Description | Options                 | Default | 
| ---- | ---- |----------------------------------------| --- |
| lifecycle | This parameter guides the creation of the Project (or Subproject) with example files for the intended lifecycle driver | ansible, sol003, sol005, restconf, netconf | ansible |
| inf | This parameter guides the creation of the Project (or Subproject) with example files for the intended infrastructure driver | openstack               | openstack |
