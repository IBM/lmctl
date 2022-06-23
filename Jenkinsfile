#!/usr/bin/env groovy

String tarquinBranch = "TNC/tnc-o-tracking#4626"

library "tarquin@$tarquinBranch"

pipelinePy {
  pkgInfoPath = 'lmctl/pkg_info.json'
  applicationName = 'lmctl'
  attachDocsToRelease = true
  releaseToPypi = true
}
