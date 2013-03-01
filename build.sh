#!/bin/sh

#  build.sh
#  This script pushes the changes in the 'build' branch to the remote and calls the remote build script.
#
#  Created by Joosep Pata on 1/16/13.
#  joosep.pata@cern.ch
#

echo "CMSSW remote build script - local end"
echo "Arguments: $@"

#Check branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "build" ]; then
    echo "ERROR: Not on branch 'build', instead on '$BRANCH'"
    exit 1
fi

#Check for uncommitted changes
git diff --quiet --exit-code
if [ $? -ne 0 ]; then
    echo "Uncommitted changes, exiting"
    exit 1
fi

echo "Pushing"
git push ssh://joosep@ied.hep.kbfi.ee/home/joosep/singletop/stpol/ build
if [ $? -ne 0 ]; then
    echo "Failed to push changes, exiting"
    exit $?
fi

echo "Building..."
ssh ied.hep.kbfi.ee "sh /home/joosep/singletop/stpol/build_scram.sh"
exit $?