# Change Log

## [2.6.3](https://github.com/IBM/lmctl/tree/2.6.2) (2020-12-08)
[Full Changelog](https://github.com/IBM/lmctl/compare/2.6.1...2.6.3)

**Fixed bugs:**

- Cannot override kami address in 2.6.x [\#72](https://github.com/IBM/lmctl/issues/72)

## [2.6.2](https://github.com/IBM/lmctl/tree/2.6.2) (2020-12-08)

Use 2.6.3

## [2.6.1](https://github.com/IBM/lmctl/tree/2.6.1) (2020-12-03)
[Full Changelog](https://github.com/IBM/lmctl/compare/2.6.0...2.6.1)

**Fixed bugs:**

- lmctl project test executing all the behaviors [\#69](https://github.com/IBM/lmctl/issues/69)

## [2.6.0](https://github.com/IBM/lmctl/tree/2.6.0) (2020-08-28)
[Full Changelog](https://github.com/IBM/lmctl/compare/2.5.0...2.6.0)

**Implemented enhancements:**

- Support CSAR packaging and Tosca metadata directory [\#53](https://github.com/IBM/lmctl/issues/53)
- Support Assembly Templates [\#58](https://github.com/IBM/lmctl/issues/58)
- Support Type projects [\#59](https://github.com/IBM/lmctl/issues/59)

## [2.5.0](https://github.com/IBM/lmctl/tree/2.5.0) (2020-05-19)
[Full Changelog](https://github.com/IBM/lmctl/compare/2.4.1...2.5.0)

**Implemented enhancements:**

- Support managing shared infrastructure keys [\#42](https://github.com/IBM/lmctl/issues/42)
- Add new resourcedriver command [\#45](https://github.com/IBM/lmctl/issues/45)
- Support latest changes in Brent v2.2 resource package and descriptor structure [\#46](https://github.com/IBM/lmctl/issues/46)
- Remove content directory included in packages [\#47](https://github.com/IBM/lmctl/issues/47) 
- Support Kubernetes based structure from project create command [\#49](https://github.com/IBM/lmctl/issues/49)

**Fixed bugs:**

- deployment list command doc typos [\#43](https://github.com/IBM/lmctl/issues/43)

## [2.4.1](https://github.com/IBM/lmctl/tree/2.4.1) (2020-02-20)
[Full Changelog](https://github.com/IBM/lmctl/compare/2.4.0...2.4.1)

**Fixed bugs:**

- Pkg Push fails: AttributeError: 'Pkg' object has no attribute 'config' [\#40](https://github.com/IBM/lmctl/issues/40)

## [2.4.0](https://github.com/IBM/lmctl/tree/2.4.0) (2020-02-06)
[Full Changelog](https://github.com/IBM/lmctl/compare/2.3.0...2.4.0)

**Implemented enhancements:**

- Add support for resource descriptors containing infrastructure and lifecycle manifests in Brent resource packages [\#38](https://github.com/IBM/lmctl/issues/38)
- Driver onboarding commands should allow a public certificate to be specified [\#36](https://github.com/IBM/lmctl/issues/36)

**Documentation:**

- Included an index page in the user guide
- Included an index page for the command reference section of the user guide
- Moved migration from 2.0 to a separate page

## [2.3.0](https://github.com/IBM/lmctl/tree/2.3.0) (2019-11-21)
[Full Changelog](https://github.com/IBM/lmctl/compare/2.2.1...2.3.0)

**Fixed bugs:**

- NameError: name 'project' is not defined on pkg push [\#33](https://github.com/IBM/lmctl/issues/33)

**Implemented enhancements:**

- Support configurable lifecycle and infrastructure types on project create command [\#30](https://github.com/IBM/lmctl/issues/30)
- Support subpath access to API and support /ui subpath for UI access  [\#28](https://github.com/IBM/lmctl/issues/28)

## [2.2.1](https://github.com/IBM/lmctl/tree/2.2.1) (2019-11-06)
[Full Changelog](https://github.com/IBM/lmctl/compare/2.2.0...2.2.1)

**Fixed bugs:**

- Lmctl build directory not relative to project being built [\#24](https://github.com/IBM/lmctl/issues/24)
- AttributeError: YAML object has no attribute YAMLError on invalid descriptor [\#25](https://github.com/IBM/lmctl/issues/25)

## [2.2.0](https://github.com/IBM/lmctl/tree/2.2.0) (2019-10-09)
[Full Changelog](https://github.com/IBM/lmctl/compare/2.1.2...2.2.0)

**Fixed bugs:**

- NameError: name 'secret' is not defined [\#22](https://github.com/IBM/lmctl/issues/22)

**Implemented enhancements:**

- Add command to show package details [\#14](https://github.com/IBM/lmctl/issues/14)
- Add commands to onboard VIM and Lifecycle drivers [\#15](https://github.com/IBM/lmctl/issues/15)

## [2.1.2](https://github.com/IBM/lmctl/tree/2.1.2) (2019-09-23)
[Full Changelog](https://github.com/IBM/lmctl/compare/2.1.1...2.1.2)

**Fixed bugs:**

- 401 unauthorised when pushing resource to secure LM environment [\#16](https://github.com/IBM/lmctl/issues/16)

**Merged pull requests:**

- Resolves \#16 by ensuring auth headers are added to Resource onboarding requests [\#17](https://github.com/IBM/lmctl/pull/17) ([dvaccarosenna](https://github.com/dvaccarosenna))

## [2.1.1](https://github.com/IBM/lmctl/tree/2.1.1) (2019-09-18)

[Full Changelog](https://github.com/IBM/lmctl/compare/2.1.0...2.1.1)

**Fixed bugs:**

- project pull results in error: AttributeError: 'DescriptorPullMutator' object has no attribute 'journal' [\#5](https://github.com/IBM/lmctl/issues/5)

**Merged pull requests:**

- issue5 - fixes \#5 by ensuring the journal is passed to the descriptor… [\#6](https://github.com/IBM/lmctl/pull/6) ([dvaccarosenna](https://github.com/dvaccarosenna))

## [2.1.0](https://github.com/IBM/lmctl/tree/2.1.0) (2019-09-02)

[Full Changelog](https://github.com/IBM/lmctl/compare/2.0.7.1...2.1.0)

**Implemented enhancements:**

- Support for Brent RM package type [\#4](https://github.com/IBM/lmctl/issues/4)
- Add commands for managing deployment locations [\#3](https://github.com/IBM/lmctl/issues/3)
- Expand subproject support to allow Assemblies to be included as part of a project [\#2](https://github.com/IBM/lmctl/issues/2)
- Support Resource projects [\#1](https://github.com/IBM/lmctl/issues/1)

## [2.0.7.1](https://github.com/IBM/lmctl/tree/2.0.7.1) (2019-08-21)

[Full Changelog](https://github.com/IBM/lmctl/compare/2.0.7...2.0.7.1)

## [2.0.7](https://github.com/IBM/lmctl/tree/2.0.7) (2019-08-21)

\* _This Change Log was automatically generated by [github_changelog_generator](https://github.com/skywinder/Github-Changelog-Generator)_
