#!/usr/bin/env groovy

String tarquinBranch = "develop"

library "tarquin@$tarquinBranch"

pipelineLmctl {
  pkgInfoPath = 'lmctl/pkg_info.json'
  applicationName = 'lmctl'
  attachDocsToRelease = true
  releaseToPypi = true
}
