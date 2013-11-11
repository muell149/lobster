#!/usr/bin/env python

import base64
import json
import os
import pickle
import shutil
import subprocess
import sys

fragment = """import FWCore.ParameterSet.Config as cms
process.source.fileNames = cms.untracked.vstring({input_files})
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))
process.source.lumisToProcess = cms.untracked.VLuminosityBlockRange({lumis})"""

def edit_process_source(cmssw_config_file, files, lumis):
    with open(cmssw_config_file, 'a') as config:
        frag = fragment.format(input_files=repr([str(f) for f in files]), lumis=[str(l) for l in lumis])
        print "--- config file fragment:"
        print frag
        print "---"
        config.write(frag)

(config, data) = sys.argv[1:]
with open(data, 'rb') as f:
    (args, files, lumis) = pickle.load(f)

configfile = config.replace(".py", "_mod.py")
shutil.copy2(config, configfile)

env = os.environ
env['X509_USER_PROXY'] = 'proxy'

edit_process_source(configfile, files, lumis)

# exit_code = subprocess.call('python "{0}" {1} > cmssw.log 2>&1'.format(configfile, ' '.join(map(repr, args))), shell=True, env=env)
exit_code = subprocess.call('cmsRun -j report.xml "{0}" {1} > cmssw.log 2>&1'.format(configfile, ' '.join(map(repr, args))), shell=True, env=env)

sys.exit(exit_code)
