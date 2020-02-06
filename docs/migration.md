
# Migrating from 2.0/2.1 to 2.2+

The 2.2 version of LMCTL features additional commands to handle package inspection and VIM/lifecycle driver management.

This version of LMCTL is compatibile with any Stratoss&trade; Lifecycle Manager environment from 2.0.x and 2.1.x.

# Difference from 2.1

The following section describes the differences from LMCTL 2.1. A later section shows the differences from 2.0.

## Pkg Inspect

A new command has been added to detail the contents of a package built with lmctl. 

```
lmctl pkg inspect --help
```

Read more about this command in the [command reference](./command-reference/pkg/inspect.md)

## Driver Commands

Stratoss&trade; Lifecycle Manager 2.1.x versions includes a Resource Manager that may be integrated with through VIM and Lifecycle drivers. This version of lmctl provides commands to add, delete and view the drivers onboarded in an environment.

```
lmctl vimdriver --help
lmctl lifecycledriver --help
```

Read more about these commands in the [vimdriver command reference](./command-reference/vimdriver/add.md) and [lifecycledriver command reference](./command-reference/lifecycledriver/add.md)

# Differences from 2.0

The following section describes the differences from LMCTL 2.0 and explains how the tool will help upgrade the users' existing projects with very little impact on them.

These changes were made in 2.1 but have been included in this documentation for reference.

## Backward Compatibility

Many of the changes below will require changes to either your LMCTL configuration file or project structure. In almost all cases, LMCTL will automatically update your files with the changes, so there will be little impact on the user.

However, the new Descriptor Naming Rules may have some visible impact when attempting to build existing projects that have benefited from the lack of any rules in `2.0`. Read the following page before attempting an `lmctl project validate` or `lmctl project build` on your projects to see if you need to make any changes.

## Improved Configuration File

The LMCTL configuration file has been enhanced in `2.1` to use better property names that reflect the purpose of each value. For example, 'ip_address' has been changed to 'host' as in many cases an environment is accessed through a hostname, not just IP addresses.

All environment configuration has also been moved under an `environments` key, making it clearer what is configured in this file.

## Resource Projects

In `2.0` LMCTL only supported managing projects for NS or VNFs (Assembly). Resources, known as VNFCs, could only be included as a sub-element of another project.

In `2.1` support Resources have been promoted so they may be managed as top level project, with their own independent lifecycle so they may be shared and used by any number of Assemblies.

## Expanded Subproject Support

In `2.0` LMCTL only supported the concept of nesting VNFCs (Resources) in a NS or VNF project (Assembly). This has been expanded so any project may also include any number of nested Assembly types.

## Descriptor Naming Rules

In `2.0` LMCTL there were very few rules on how Assembly/Resources were named in project. In `2.1` LMCTL adds features, such as auto population of descriptor names, which require the naming of each Assembly/Resource to reflect the structure of the project. For example, of a project for an Assembly named `ippbx` with a version value of `1.0` will only be allowed a descriptor with name `assembly::ippbx::1.0`.

Descriptors for subprojects must also be associated with the parent project's name and version. For example, a subproject configured with name `asterisk` would be allowed a descriptor with name: `resource::asterisk-ippbx::1.0`.

This will allow LMCTL to manage the name and version of the project and all subprojects from the single root project file. From a practical point of view, this means if you wanted to begin developing ippbx 2.0, you would only need to update the version number in one place (lmproject.yml).

## Deployment Locations

In `2.1` commands for adding, removing and listing the Deployment Locations on an LM environment have been added.

## Brent Support

`2.1` adds support for Brent, the Carrier Grade Resource Manager. Any Resource project, or subproject, should use `brent` or `lm` as the resource-manager value to indicate it should be packaged for Brent.

The default value for resource-manager on the `project create` command has been changed to `lm`.

## Removed Ansible RM Onboarding Address

In `2.0` LMCTL required the user to configure the address LM uses to communicate with the Ansible RM, so it may be re-onboarded after new resources are pushed, in cases where the onboarded address is different to the one used by the external user (almost always the case).

In `2.1` LMCTL now reads the onboarded address from LM, removing the need to set this in the LMCTL configuration file.
