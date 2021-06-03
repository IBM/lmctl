# Overview

A **project** represents a single Assembly/Resource (NS or xNF) to be developed, tested and published for usage in TNCO environments. LMCTL helps developers manage a project through a recommended lifecycle, making use of common stages in continuous integration and deployment pipelines:

- Develop: design and implement the service
- Build: produce a distribution of the service to deploy to an LM environment
- Push: push the distribution to an LM environment
- Test: run behaviour tests against the service in the LM environment
- Publish: publish the distribution to a repository management system

The main benefit of LMCTL is it's ability to organise a collection of artifacts required by an Assembly or Resource, then orchestrate the laborious task of applying changes across TNCO environments for testing.

Once a project is ready for publishing, LMCTL is used to produce a distributable package that can be shared to other LMCTL users and deployed to their development environments or to pre-prod/production environments.

LMCTL also supports bundling related Assembly/Resources as part of a single project, providing further automation by pushing each to the TNCO or specified Resource Manager when the deployed.

As projects managed by LMCTL are organised by a common directory tree, the artifacts of a project are maintained independent of a single TNCO environment. Instead they are pushed into an environment for modification and testing, before the changes are pulled back into the local file system - this makes it simple to integrate with any existing version control or change management process, without sacrificing the ability to view and modify each artifact in the fit-for-purpose user interfaces provided by TNCO.

# Project Structure

A project is organised by a directory tree which includes the following artifacts:

```
myproject/
    lmproject.yaml
    Contains/
```

The following table details the relevance of each item in the project tree:

| Item           | Requirement | Description                                                                                |
| -------------- | ----------- | ------------------------------------------------------------------------------------------ |
| lmproject.yaml | mandatory   | This file details the meta-data required by LMCTL to manage the project                    |
| Contains       | optional    | This optional directory can contain one or more subprojects to be included in this project |

The remaining structure of the project, and each subproject, depends on the type of service under development.

## TOSCA Additions

In addition to the normal project structure, you may also include a `TOSCA-Metadata` directory to be included in the final package. This directory is expected to have a single `TOSCA.meta` file in.

```
myproject/
    lmproject.yaml
    Contains/
      ...
    TOSCA-Metadata/
      TOSCA.meta
```

> Tip: use `--param packaging csar` on the `lmctl project create` command to generate example content for this file

## Assembly Projects

An Assembly project is expected to include a descriptor and, optionally, behaviour test related artifacts.

```
myproject/
    Descriptor/
      assembly.yml
    Behaviour/
        Tests/
        Templates/
        Runtime/
```

The following table details the relevance of each item in the project tree:

| Item                | Requirement | Description                                                                                             |
| ------------------- | ----------- | ------------------------------------------------------------------------------------------------------- |
| Descriptor          | mandatory   | This directory must contain a descriptor file called `assembly.yml`, representing the top level service |
| Behaviour           | optional    | This optional directory contains the Assembly Configurations and Scenarios for behaviour testing         |
| Behaviour/Tests     | optional    | This optional directory contains the Test Scenarios for behaviour testing                                |
| Behaviour/Templates | optional    | This optional directory contains the Assembly Templates for behaviour testing                            |
| Behaviour/Runtime   | optional    | This optional directory contains the Runtime Scenarios, such as Diagnostic tests, for behaviour testing  |

## Resource Projects

The structure of a Resource project depends on the chosen Resource Manager expected to operate it. Currently the tool supports projects for Brent or Ansible RM resources.

### Brent

Any Resource included in a project intended for Brent is expected to have the following structure:

```
myproject/
    Definitions/
      lm/
        resource.yml
    Lifecycle/
        ...
```

| Directory                                    | Requirement | Description                                                                                                   |
| -------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------------- |
| Definitions                                  | mandatory   | contains definition files                                                            |
| Definitions/lm                               | mandatory   | contains the Resource descriptor required by LM and Brent                                                     |
| Lifecycle                                    | mandatory   | contains lifecycle scripts for the Resource (structure of sub-directories depends on chosen Lifecycle driver) |


The Lifecycle directory should be populated with scripts required by the chosen driver(s). For example, if using the Openstack driver and Ansible driver, you would need a directory named `openstack` and one named `ansible`, with the files used by that driver:

```
myproject/
    ...
    Lifecycle/
        openstack/
          heat.yaml
        ansible/
          config/
            host_vars/
              myhost.yaml
            inventory
          scripts/
            Install.yaml
            Start.yaml
```

### Ansible RM

Any Resource included in a project intended for the Ansible RM is expected to have the following structure:

| Directory  | Requirement | Description                                                                                                                                        |
| ---------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| descriptor | mandatory   | must contain a Resource descriptor file with a file name matching the Resources name e.g. a Resource named vnfcA must have a file called vnfcA.yml |
| lifecycle  | mandatory   | must contain valid ansible playbooks for each supported lifecycle: Install.yml, Start.yml, Configure.yml, Stop.yml, Uninstall.yml                  |
| Meta-Inf   | mandatory   | must contain a mainifest.MF file with details of the Resource                                                                                      |


# ETSI Project Types
LMCTL supports development of projects whos structure complies with the ETSI SOL CSAR packaging specifications. When built, ETSI_VNF projects are structured in compliance with ETSI SOL004 package structure and ETSI_NS projects are compliant with the ETSI SOL007 specification. ETSI projects will contain the same files discussed in the [TOSCA Additions](#tosca-additions) topic but also included additional files and content to make the compliant with the relevent SOL CSAR packaging specification.

In addition to any mandatory key entries, the generated TOSCA-Metadata/TOSCA.meta file will contain an entry called `TNCO-Descriptor` which points to the projects definitions file and allows TNC-O to onboard the resource or asseembly when the project package is pushed to TNC-O.

ETSI projects do not support nested projects within a Contains directory.
## ETSI_VNF Projects
An ETSI_VNF project is structured in a similar way to a standard Brent Resource project, only Brent is supported for ETSI_VNF. It is expected to include a resource descriptor and Lifecycle content as described in the [Brent](#brent) topic above. Additionally, it also contains TOSCA additions in line with the SOL004 specifications.

The following files and directories are automatically generated with the command `lmctl project create --type ETSI_VNF` and will contain basic content that can be extended as required, the Lifecycle directory is structured the same as a [Brent](#brent) Resource project:

```
myproject/
    MRF.mf
    Definitions/
      MRF.yaml        
      lm/
        resource.yml
    Files/
      Changelog.txt
    Files/Licenses/
      License.txt
    TOSCA-Metadata/
      TOSCA.meta
    Lifecycle/
        ...
```

The following table details the relevance of each item in the ETSI_VNF project tree:

| Item                | Requirement | Description                                                                                             |
| ------------------- | ----------- | ------------------------------------------------------------------------------------------------------- |
| TOSCA-Metadata/TOSCA.meta | mandatory   | This is the main TOSCA file providing entry information for processing a CSAR file, also contains `TNCO-Descriptor` referring to the `Definitions/lm/resource.yaml` descriptor file so TNC-O can onboard to Brent |
| MRF.mf | mandatory   | This is the NSD archive manifest file and will contain mandatory list of key names as per SOL004 |
| Definitions         | mandatory   | This directory must exist and should contain a definitions file (`MRF.yaml`) as defined in the TOSCA-Metadata/TOSCA.meta file's `Entry-Definitions` entry |
| Definitions/lm                               | mandatory   | contains the Resource descriptor required by LM and Brent |
| Lifecycle                                    | mandatory   | contains lifecycle scripts for as with [Brent](#brent) Resource |
| Files/Changelog.txt        | mandatory   | This file is a requirement of SOL004 and is referenced in the TOSCA-Metadata/TOSCA.meta file's `ETSI-Entry-Change-Log` entry |
| Files/Licenses/License.txt        | optional   | This file can be included if required if referenced in the TOSCA-Metadata/TOSCA.meta file's `ETSI-Entry-Licenses` entry |


When an ETSI_VNF project is built and pushed to TNC-O it is packaged as a SOL004 compliant CSAR archive and pushed to the TNC-0 SOL005 VNF Package Management API.
## ETSI_NS Projects

An ETSI_NS project is structured in a similar way to standard Assembly projects, in that it is expected to include a descriptor and, optionally, behaviour test related artifacts. However it also contains several TOSCA additions in line with the SOL007 specification.  
The following files and directories are automatically generated with the command `lmctl project create --type ETSI_NS` and will contain basic content that can be extended if required:

```
myproject/
    MRF.mf
    Descriptor/
      assembly.yml
    Definitions/
      MRF.yaml    
    Files/
      Changelog.txt
    Files/Licenses/
      License.txt
    TOSCA-Metadata/
      TOSCA.meta
    Behaviour/
        Tests/
        Templates/
        Runtime/            
```

The following table details the relevance of each item in the ETSI_NS project tree:

| Item                | Requirement | Description                                                                                             |
| ------------------- | ----------- | ------------------------------------------------------------------------------------------------------- |
| Descriptor          | mandatory   | This directory must contain a descriptor file called `assembly.yml`, representing the top level service |
| TOSCA-Metadata/TOSCA.meta | mandatory   | This is the main TOSCA file providing entry information for processing a CSAR file, also contains `TNCO-Descriptor` referring to the `assembly.yml` so TNC-O can onboard the assembly |
| MRF.mf | mandatory   | This is the NSD archive manifest file and will contain mandatory list of key names as per SOL007 |
| Definitions         | mandatory   | This directory must exist and should contain a definitions file (`MRF.yaml`) as defined in the TOSCA-Metadata/TOSCA.meta file's `Entry-Definitions` entry |
| Files/Changelog.txt        | mandatory   | This file is a requirement of SOL007 and is referenced in the TOSCA-Metadata/TOSCA.meta file's `ETSI-Entry-Change-Log` entry |
| Files/Licenses/License.txt        | optional   | This file can be included if required if referenced in the TOSCA-Metadata/TOSCA.meta file's `ETSI-Entry-Licenses` entry |
| Behaviour           | optional    | This optional directory contains the Assembly Configurations and Scenarios for behaviour testing         |
| Behaviour/Tests     | optional    | This optional directory contains the Test Scenarios for behaviour testing                                |
| Behaviour/Templates | optional    | This optional directory contains the Assembly Templates for behaviour testing                            |
| Behaviour/Runtime   | optional    | This optional directory contains the Runtime Scenarios, such as Diagnostic tests, for behaviour testing  |

When an ETSI_NS project is built and pushed to TNC-O it is packaged as a SOL007 compliant CSAR archive and pushed to the TNC-0 SOL005 NSD Management API.

# Project File

A project directory must contain a `lmproject.yml` file, which details the meta-data required by LMCTL. At minimum, this file must provide a name for the project, used in console output and the names for packages/descriptors produced by LMCTL.

```
name: ippbx
```

If the project features nested Resources, then additional information must be specified to ensure they are included in the package produced for this project:

```
schema: 2.0
name: ippbx
type: Assembly
version: 1.0
contains:
  - name: asterisk
    type: Resource
    resource-manager: brent
    directory: asterisk
```

The following table details the full set of values that may be provided in a project file:

| Value            | Requirement | Description                                                                                                             |
| ---------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------- |
| schema           | mandatory   | The LMCTL project file schema in use (use the latest: `2.0)`                                                            |
| name             | mandatory   | The name given to the project (see the importance of this name at [Naming Rules](#naming-rules))                        |
| version          | mandatory   | The currently development version of this project (see the importance of this version at [Naming Rules](#naming-rules)) |
| type             | mandatory   | The type of service under development in this project (Assembly or Resource)                                            |
| resource-manager | optional    | If this project is for a Resource: the type of Resource Manager it is intended for                                      |
| contains         | optional    | A list of subproject meta-data                                                                                          |

The following table details the full set of values expected for each subproject:

| Value            | Requirement | Description                                                                                      |
| ---------------- | ----------- | ------------------------------------------------------------------------------------------------ |
| name             | mandatory   | The name given to the project (see the importance of this name at [Naming Rules](#naming-rules)) |
| type             | mandatory   | The type of service under development in this project (Assembly or Resource)                     |
| resource-manager | optional    | If this project is for a Resource: the type of Resource Manager it is intended for               |
| directory        | mandatory   | The directory under `Contains` which includes the artifacts for this subproject                  |

# Naming Rules

The name of any descriptor, for an Assembly or Resource, is expected to make use of the projects name and version. In all cases, LMCTL will auto-populate the name of the descriptor when pushing to an environment (and remove the current name on pull) unless one is set, so it is best to leave the name field out of any raw artifacts.

The name of the descriptor must meet the following requirements: `project_type::project_name::project_version`. For example, the descriptor for a project with the following configuration would be: `assembly::ippbx::1.3`:

```
schema: 2.0
name: ippbx
type: Assembly
version: 1.3
```

For subprojects, the name of the descriptor must be: `subproject_type::subproject_name-project_name::project_version`. For example, the descriptor for `asterisk` in the following configuration would be: `resource::asterisk-ippbx::1.3`:

```
schema: 2.0
name: ippbx
type: Assembly
version: 1.0
contains:
  - name: asterisk
    type: Resource
    resource-manager: brent
    directory: asterisk
```

# Next Steps

Now you understand the structure of an LMCTL project, you may start [creating one](creating-projects.md)
