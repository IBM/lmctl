#!/usr/bin/env groovy

String tarquinBranch = "develop"

library "tarquin@$tarquinBranch"

pipelinePy {
  pkgInfoPath = 'lmctl/pkg_info.json'
  applicationName = 'lmctl'
  attachDocsToRelease = true
}
