#!/bin/sh

#  build.sh
#  stpol
#
#  Created by Joosep Pata on 1/16/13.
#
echo "Pushing"
git push ssh://joosep@ied.hep.kbfi.ee/home/joosep/singletop/stpol/ build
echo "Building..."
ssh ied.hep.kbfi.ee "sh /home/joosep/singletop/stpol/build_scram.sh"
echo "Done building!"