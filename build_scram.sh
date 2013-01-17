DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
#git status
BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [ "$BRANCH" == "master" ]
then
    echo "On branch 'master'"
    git diff --quiet --exit-code
    if [ $? -ne 0 ]
    then
        echo "Uncommitted changes, exiting"
        exit 1
    fi
    git checkout build
else
    echo "Not on branch 'master'"
    git diff --quiet --exit-code
    if [ $? -ne 0 ]
    then
        echo "Uncommitted changes, exiting"
        exit 1
    fi
fi
source setenv.sh
cd CMSSW_5_3_7_patch4
scram b -j 7 | grep -v ">>"
git checkout master
