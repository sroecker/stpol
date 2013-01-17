DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
#git status
BRANCH=$(git rev-parse --abbrev-ref HEAD)

function uncommitted(){
    git diff --quiet --exit-code
    if [ $? -ne 0 ]; then
        return $FALSE
    fi
        return $TRUE
}

if [ "$BRANCH" != "build" ]
then
    echo "Not on branch 'build'"
    if [ uncommitted ]
    then
        echo "Uncommitted changes, exiting"
        exit 1
    fi
    git checkout build
fi
source setenv.sh
cd CMSSW_5_3_7_patch4
scram b -j 7 | grep -v ">>"
git checkout "$BRANCH"
