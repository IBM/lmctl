# Creating a new Project

A new project may be created by manually initialising the directory tree and all the required artifacts or, more efficiently, by using the `project create` command provided by LMCTL:

1. Create a new directory using the name of your intended project and navigate to it:

   ```
   mkdir example && cd example
   ```

2. Execute the `project create`, specifying the name, version and type:

   ```
   lmctl project create --name example --version 1.0 --type Assembly
   ```

3. View the contents of the sub-directories and files created by LMCTL

## Creating a Resource Project

When creating a Resource project you must specify the intended Resource Manager on the `rm` option:

```
lmctl project create --name example --version 1.0 --type Resource --rm brent
```

For an Ansible RM project:

```
lmctl project create --name example --version 1.0 --type Resource --rm ansible-rm
```

When using `brent` on the `--rm` option, LMCTL can also produce the expected directory structure for the type of infrastructure and/or lifecycle driver used to manage this Resource, via `--param` values. (See [create command](../command-reference/project/create.md))

## Creating an ETSI_VNF Resource Project

When creating an ETSI_VNF project you must specify the type as `ETSI_VNF`:

```
lmctl project create --name example --version 1.0 --type ETSI_VNF
```
Only Brent Resource Manager is supported.

## Creating an ETSI_NS Assembly Project

When creating an ETSI_NS project you must specify the type as `ETSI_NS`:

```
lmctl project create --name example --version 1.0 --type ETSI_NS
```

## Creating Subprojects

To include subprojects, specify the name of each with the `--contains` option. For each value on this option you must specify the type of the subproject and name, separated by spaces. If the subproject is a Resource, then the type must also include the intended Resource Manager, separated by two colons (`::`):

```
lmctl project create --name example --version 1.0 --type Assembly --contains Assembly subassembly --contains Resource::brent subresource
```

# Creating a Project from existing sources in TNCO (ALM)

If you have already designed a service in TNCO you can base a project around it and pull the existing content using LMCTL. (Note: currently it is not possible to pull the contents of Resources from Ansible RM or Brent):

1. Create a Project as explained in [Creating a new Project](#creating-a-new-project). Ensure the name and version correspond with the service design in TNCO you intend to base this project on. For example, if you designed `assembly::example::2.0` then make sure your project type is Assembly, name is 'example' and version is '2.0'.

2. Use the `project pull` command to pull the contents from a target named environment:

   ```
   lmctl project pull dev
   ```

3. Verify the `Descriptor/assembly.yml` file has been populated with the design of your service and the `Behaviour` directory has been populated with any Assembly Configurations and/or Scenarios you have in Stratoss LM

The pull command will also pull the contents of any subprojects that are also of the Assembly type.

# Next Steps

[Build the project](building-projects.md)