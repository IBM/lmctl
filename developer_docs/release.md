# Release

The following steps detail how an LMCTL release is produced. This may only be performed by a user with admin rights to this Git repository and the Pypi repository.

**Ensure you've followed the steps in [configure your development environment](developer_env.md) as there are libraries required to complete the release.**

## 1. Ensure Milestone

Ensure there is a milestone created for the release at: [https://github.com/IBM/lmctl/milestones](https://github.com/IBM/lmctl/milestones).

Also ensure all issues going into this release are assigned to this milestone. **Move any issues from unreleased milestones into this release if the code has been merged**

## 2. Update version (on develop)

Ensure the version in `pkg_info.json` starts with the corresponding version for the release.

For example, if releasing `3.2.0`, ensure the `pkg_info.json` contains:

```
{"version": "3.2.0.dev0"}
```

This should have been done after the last release but it's good to check as the planned version may have changed (we expected to release a patch `3.2.1` but due to the nature of changes we've decided it's a minor release `3.3.0` instead)

Commit and push these changes.

## 3. Update CHANGELOG (on develop)

Update the `CHANGELOG.md` file with a list of issues fixed by this release (see other items in this file to get an idea of the desired format).

Commit and push these changes.

## 4. Merge Develop to Master

Development work is normally carried out on the `develop` branch. Merge this branch to `master`, by creating a PR, 

Then perform the release from the `master` branch. This ensures the `master` branch is tagged correctly. 

> Note: do NOT delete the `develop` branch

## 5. Build and Release (on master)

Access the `lmctl` build job on the internal CI/CD tool (maintainers should be aware and have access to this. Speak to another maintainer if not).

Navigate to the job for the `master` branch. The merge to `master` should have already triggered a build. Let this build complete in order to verify there were no issues with the merge. The automated job will not complete the release, it will only build and run the unit tests.

Once ready, click `Build with Parameters` for on the `master` branch job. Enable the `release` option and click `BUILD`.

Wait for the build to complete successfully. 

## 6. Verify Release

Verify the CI/CD job has created a [release on Github](https://github.com/IBM/lmctl/releases).

Ensure the tag, title and changelog are all correct. Also ensure the documentation `tgz` file has been attached. 

Verify the release has been published to [pypi](https://pypi.org/manage/project/lmctl/releases/).

## 7. Cleanup

Complete the following steps to ensure development can continue as normal:

- Merge `master` to `develop` so any release updates and the post-version are copied over from master (doesn't require a PR)
- Close the Milestone for this release on [Github](https://github.com/IBM/lmctl/milestones)
- Create a new Milestone for next release (if one does not exist). Use the value of the `--post-version` option from earlier

# Manual Approach

**Please use the instructions above. The manual approach is now legacy and only kept for the rare circumstances**

## 1-4. Prepare Release

Complete steps 1-4 from the main release instructions (found above).

## 5. Build and Release (on master)

The `build.py` script automates the following steps: 

- Update the release version in pkg_info.json
- Build the Python whl for the library
- Build the Jenkins JNLP Slave image
- Package Documentation
- Push Whl to Pypi
- Push Jenkins JNLP Slave Image to `icr.io/cp4na-drivers` group on IBM Cloud Container Registry
- Create a tagged commit in the git repository to mark this release

To perform a release, run `build.py` and set the following options:

```
python3 build.py --release --version <THE VERSION TO BE RELEASED> --post-version <VERSION TO BE USED AFTER THE RELEASE> --pypi-user <USERNAME FOR PYPI> --pypi-pass <PASSWORD FOR PYPI USER>
```

For example:
```
python3 build.py --release --version 1.0.0 --post-version 1.0.1.dev0 --pypi-user accanto --pypi-pass mypass
```

Confirm the tags/commits were pushed to the repository origin.

## 6. Release artifacts

The Whl has been pushed to Pypi by the `build.py` script but the documentation must be uploaded manually to Github.

Complete the following:

- Visit the [releases](https://github.com/IBM/lmctl/releases) section of the repository
- Click `Draft a new release`
- Input the version the `--version` option earlier as the tag e.g. 1.0.0
- Use the same value for the `Release title` e.g. 1.0.0
- Add release notes in the description of the release. Look at previous releases to see the format. Usually, we will list the issues fixed. This is essentially the same content you have already added to `CHANGELOG.md` so just copy and paste the entry for this release, edit the header to say `Release Notes`.
- Attach the documentation `tgz` file produced by `build.py` in the root directory of this project

## 7. Cleanup

Complete step 7 from the main release instructions (found above).
