# Network Service and VNF Packages

## Pushing Packages

After a Project has been fully tested, and all development is complete, the final package can be transferred to a repository making it available to others. Another user can download the package and use the `lmctl pkg` commands to push it to their LM environment. 

This command is similar to the `lmctl project push` command however there is no need for a local version of the project and no `build` is performed as the package is already present.

Run the `push` command, passing the name of the package and an environment that can be found in your `LMCONFIG` file:

```
lmctl pkg push <project-pkg>.tgz <env-name>
```

## Secure LM

The `pkg push` command accepts a password parameter on the `--pwd` option. The value of this parameter is used if the target LM environment is configured with a `username` but no `password` to authenticate the user before making any API calls.

If no `--pwd` value is provided and there is no value for `password` in the lmctl config file then a prompt will be displayed requesting the password:

```
$ lmctl project push dev
Please enter a password for user jack []:
```