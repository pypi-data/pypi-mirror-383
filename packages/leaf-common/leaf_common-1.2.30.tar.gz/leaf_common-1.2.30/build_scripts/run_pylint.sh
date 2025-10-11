#!/usr/bin/env bash

# set -euo pipefail

RCFILE=./.pylintrc
UP_TO_SNUFF_DIRS=$(ls -1)
DEPENDENCY_DIRS=""
IGNORE="${DEPENDENCY_DIRS} build_scripts"

dirs=$1
if [ "x${dirs}" == "x" ]
then
    dirs=${UP_TO_SNUFF_DIRS}
fi

# Comb through directories to see what we will actually use
use_dirs=""
retval=0
for dir in ${dirs}
do
    # At end of loop ignore_this will be set if we need to ignore
    ignore_this=""

    # If we actually have a single file, skip it
    if [[ -f ${dir} ]]
    then
        ignore_this=${dir}
    fi

    # See if it's a directory we specifically want to ignore
    for ignore_dir in ${IGNORE}
    do
        if [ "x${ignore_dir}" == $"x${dir}" ]
        then
            ignore_this=${dir}
        fi
    done

    # If we do not need to ignore...
    if [ "x" == "x${ignore_this}" ]
    then
        use_dirs="${use_dirs} ${dir}"
    fi
done

echo "Running pylint on directories '${use_dirs}':"
# shellcheck disable=2086
pylint --load-plugins=pylint_protobuf -j 0 -rn --rcfile=${RCFILE} ${use_dirs}
retval=$?

echo "Pylint complete."

exit ${retval}
