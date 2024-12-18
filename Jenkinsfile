#!/usr/bin/env groovy

String tarquinBranch = "CPNA-2407"

library "tarquin@$tarquinBranch"

pipelineLmctl {
  pkgInfoPath = 'lmctl/pkg_info.json'
  applicationName = 'lmctl'
  attachDocsToRelease = true
  releaseToPypi = true
}
