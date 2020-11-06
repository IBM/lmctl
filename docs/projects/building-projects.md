# Building Packages

The `project build` command is used to produce a distributable package for a project. A build does not require access to a TNCO environment, so can be executed anytime on the project source by navigating to it's directory and executing the command.

Building a project to produce a release package is an important step of the lifecycle, which is why the `push` and `test` commands will first execute a build, to ensure the latest changes are bundled. This means it is rarely the case that a user will need to call `build` explicitly.

# Build a Project

To build a project, navigate to it's directory and execute build:

```
lmctl project build
```

This command will produce a `.tgz` package (or `.csar` if packaging is configured in the lmproject file) in the auto-created LMCTL build workspace directory (`_lmctl/build`) relative to your project. This package includes:

- All artifacts required by the root service of your project
- All artifacts required by each subproject

The structure of the directories and artifacts in the package are determined by LMCTL and should not be altered.

# Next Steps

[Deploying projects](deploing-projects.md)