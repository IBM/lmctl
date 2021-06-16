# Pull Changes

Many of the artifacts in a project are best modified in the fit-for-purpose interfaces provided by CP4NA orchestration. This makes it vital that a user may download the changes made into the local copy of their project, so they may be pushed into any source/version control system.

# Pull Project Artifacts

Currently only the contents of Assembly projects and subprojects can be pulled. This means you may only pull changes to:

- the service descriptor
- service behaviour assembly configurations and scenarios

Pull the changes by navigating to the project's directory and completing the following:

1. Execute the `project pull` command, naming the target environment from your LMCTL configuration file to pull from:
   ```
   lmctl project pull dev
   ```
2. Verify the `Descriptor/assembly.yml` file has been populated with the design of your service and the `Behaviour` directory has been populated with any Assembly Configurations and/or Scenarios you have in CP4NA orchestration. Verify the contents of any Assembly subprojects have been updated.

A backup of project artifacts prior to the pull are stored in the `_lmctl/pre_pull_backup` directory relative to your project. If you realise you pulled changes from an environment by mistake, you can revert the changes by copying the contents from the pre-pull directory. Note: the pre-pull directory only maintains a backup version of each artifact prior to the **last** pull.
