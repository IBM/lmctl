# Pushing a Project

The `project push` command is used to push the artifacts of a project to a target Stratoss LM environment. For an Assembly this project will:

- Deploy the service descriptor to LM
- Deploy all service behavior related artifacts to LM

For any Resource projects, the action taken depends on the expectations of the Resource Manager:

- Brent: a resource package with the necessary artifacts is pushed to Brent and the descriptor for the Resource will be updated in LM by re-onboarding Brent
- Ansible RM: a CSAR with the necessary artifacts will be pushed to the RM, and the descriptor for the Resource will be updated in LM by re-onboarding the RM

In all cases the new versions of each artifact will overwrite any existing version present in the environment.

LMCTL performs a push by first executing a build, to produce a `.tgz` package with the latest changes, then orchestrates pushing the content of this package to the relevant services. As a result, it is not necessary to explicitly execute a `build` first.

To build and push your project, navigate to it's directory then:

1. Execute the `project push` command, naming the target environment from your LMCTL configuration file:
   ```
   lmctl project push dev
   ```
2. Verify the descriptor and behavior scenarios/configurations are present in your Stratoss LM environment

## Pushing a Resource Project (or Subprojects)

If your project is for a Resource using the Ansible RM, or includes subprojects which are, then you will need to specify the name of the Ansible RM (from the environment group in your LMCTL configuration file) to push them to. If using Brent, no additional options are required.

1. Execute the `project push` command, naming the target environment from your LMCTL configuration file and naming the Ansible RM to push to (if required):
   ```
   lmctl project push dev --armname defaultrm
   ```
2. Verify the Assembly descriptor and behavior scenarios/configurations are present in your Stratoss LM environment
3. Verify the Resource(s) are present in the Brent/Ansible RM using it's APIs
4. Verify the Resource descriptors are present in Stratoss LM
