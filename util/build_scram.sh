DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
#git status
BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$BRANCH" != "build" ]
then
    echo "Not on branch 'build'"
    git diff --quiet --exit-code
    if [ $? -ne 0 ]; then
        echo "Uncommitted changes, exiting"
        exit 1
    fi
    git checkout build
fi
source setenv.sh
cd CMSSW_5_3_7_patch4
scram b -j 7 2>&1 > scram.log
git checkout "$BRANCH"
