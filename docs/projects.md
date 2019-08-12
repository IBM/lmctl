# Network Service and VNF Projects

This section describes how to push VNF or Network Service projects from your local machine to an environment created above. VNF and Network Service projects must follow a specific directory structure and **lmctl** will package and push the appropriate components into LM and Ansible RM.

## Starting a Project

To create a new Project, create an empty directory with the name of your Service

```
mkdir ip-pbx
```

Use the `create` command to start a new Project in this directory. If the Service you intend to create is a VNF then include the `--servicetype` option and list the names of your initial VNFCs with the `--vnfc` option

```
## Create a NS project
lmctl project create

## Create a VNF project with VNFCs
lmctl project create --servicetype VNF --vnfc vnfcA --vnfc vnfcB
```

## Project Structure

### Directory structure

A top level project structure can have the following artefacts:

| Directory               | Required | Description                                                                                                                                                 |
| ----------------------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Descriptor**          | Yes      | This directory must contain a descriptor file called **"assembly.yml"**, representing the top level VNF or Network Service. The descriptor is pushed to ALM |
| **Behaviour**           | optional | This optional directory contains the Assembly Templates and Scenarios used by LM scenarios                                                                  |
| **Behaviour/Tests**     | optional | This optional directory contains the Test Scenarios. These are pushed to LM automatically                                                                   |
| **Behaviour/Templates** | optional | This optional directory contains the Assembly Templates. These are pushed to LM automatically                                                               |
| **Behaviour/Runtime**   | optional | This optional directory contains the Runtime Scenarios, such as Diagnostic tests. These are pushed to LM automatically                                      |
| **VNFCs**               | optional | This optional directory can contain one or more VNFCs, each VNFC is packaged and automatically pushed to Ansible RM                                         |

### VNFC directory structure

A VNFC has a specific set of directory and file requirements in order to make it usable with the Ansible RM, they are as follows:

| Directory      | Required | Description                                                                                                                       |
| -------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **descriptor** | Yes      | must contain a Resource descriptor file called <vnfc name>.yml                                                                    |
| **lifecycle**  | Yes      | must contain valid ansible playbooks for each supported lifecycle: Install.yml, Start.yml, Configure.yml, Stop.yml, Uninstall.yml |
| **Meta-Inf**   | Yes      | must contain a mainifest.MF file with details of the VNFC, see example below                                                      |

The **manifest.MF** file must contain the name of the VNFC, its version and the resource manager. The name must match the name of the VNFC resource descriptor name, and the VNFC directory

```
name: docker-network
version: 1.0
resource-manager: docker
```

### Lmproject File

Every project should include a `lmproject.yml` file at root. This file should include definitions of the VNFCs and their target RM package type:

```
name: ippbx
vnfcs:
  definitions:
    asterisk-vnfc:
      directory: asterisk-vnfc
  packages:
    ansible-rm-vnfcs:
      packaging-type: ansible-rm
      executions:
      - vnfc: asterisk-vnfc

```

This file will be auto-generated on first run, however you should remember to add new VNFCs to this file if created later.

## Project Lifecycle

Every Project can be put through the following lifeycle:

- Build - produce a package including all necessary elements to use the Service in an LM environment
- Push - push the project package to an LM environment
- Test - run Service Behaviour tests on the LM environment

Each stage of the lifecycle is represented by a command of `lmctl project`, each later stage will complete the work of the earlier stages i.e. Push will execute a Build then Push. Test will execute a Build, Push and then Test.

### Build

The `build` command completes the following:

- Package VNFCs according to their target RM type
- Produce a `.tgz` package for the Project which includes:
  - packaged VNFCs
  - Service Descriptor
  - Service Behaviour elements

Run the `build` command then check the `_lmctl/_build` directory for the package with name `<project-name>-<project-version>.tgz`

```
cd <project-dir>
lmctl project build
```

The `build` command does NOT require a target LM environment.

### Push

The `push` command performs a build then pushes the elements of the package to a target LM environment.

Run the `push` command, passing the name of an environment that can be found in your `LMCONFIG` file:

```
cd <project-dir>
lmctl project push <env-name>
```

If your project package includes VNFCs, then you may need to include the name of the Ansible RM to push them to (the default is `defaultrm`). The `--armname` should match an Ansible RM included in the chosen environment from your `LMCONFIG` file:

```
lmctl project push <env-name> --armname my-ansible-rm
```

### Test

The `test` command executes all Service Behaviour tests that were pushed to the environment. (The test command will perform a `build` and `push`).

Run the `test` command, passing the name of an environment that can be found in your `LMCONFIG` file:

```
cd <project-dir>
lmctl project test <env-name>
```

As the `test` command will also perform a `push` you may need to include the name of an Ansible RM to push VNFCs to (see `Push`)

### Pull

The `pull` command will pull elements from the target LM environment into your project. This will overwrite any local versions of the following:

- Service Descriptor
- Service Behaviour Tests and Templates

Backup versions of replaced files are stored in a `_lmctl/_prepull` directory.

Run the `pull` command, passing the name of an environment that can be found in your `LMCONFIG` file:

```
cd <project-dir>
lmctl project pull <env-name>
```

## Pushing Packages

After a Project has been fully tested, and all development is complete, the final package can be transferred to a repository making it available to others. Another user can download the package and use the `lmctl pkg` commands to push it to their LM environment.

See `pkg.md` for more details.

## Secure LM

The `push`, `test` and `pull` commands all accept a password parameter on the `--pwd` option. The value of this parameter is used if the target LM environment is configured with a `username` but no `password` to authenticate the user before making any API calls.

If no `--pwd` value is provided and there is no value for `password` in the lmctl config file then a prompt will be displayed requesting the password:

```
$ lmctl project push dev
Please enter a password for user jack []:
```
