#!/bin/sh

#  build.sh
#  This script pushes the changes in the 'build' branch to the remote and calls the remote build script.
#
#  Created by Joosep Pata on 1/16/13.
#  joosep.pata@cern.ch
#
echo "Pushing"
git push ssh://joosep@ied.hep.kbfi.ee/home/joosep/singletop/stpol/ build
echo "Building..."
ssh ied.hep.kbfi.ee "sh /home/joosep/singletop/stpol/build_scram.sh"
echo "Done building!"