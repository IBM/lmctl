# Distributed Packages

The distributable package produced by a `build` of your project (also produced on a `push` and `test`) can be shared to another user/system to be deployed to other TNCO environments. Pushing a package works similar to a `project push`, the difference is it starts from a pre-built package rather than building from source.

# Deploying Distributed Packages

To deploy a package produced by LMCTL, complete the following:

1. Download/copy the `.tgz` or `.csar` package you intend to deploy, to a target location on your machine (navigate to this location)
2. Execute the `pkg push` command, naming the target environment from your LMCTL configuration file. If Ansible RM Resources are included, name the RM to push to:
   ```
   lmctl pkg push example-1.0.tgz dev --armname defaultrm
   ```
3. Verify any Assembly descriptor and behaviour scenarios/configurations are present in your TNCO environment
4. Verify any Resources are present in Brent/Ansible RM using it's APIs
5. Verify any Resource descriptors are present in TNCO
