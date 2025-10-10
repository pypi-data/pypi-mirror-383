#!/bin/bash

PYTHON_SYMLINK='python3'
SCRIPT_PATH=$2
HELP_FILE=$3

_m3cli_completion() {
    local IFS=$'
'
    COMP_WORDS="${COMP_WORDS[*]}"
    $PYTHON_SYMLINK $SCRIPT_PATH "bash"  ${COMP_WORDS}
    COMPREPLY=""
    if [ -f "${HELP_FILE}" ] ; then
      COMPREPLY=($(cat ${HELP_FILE}))
    fi
    return 0
}

_m3_completionetup() {
    local COMPLETION_OPTIONS=""
    local BASH_VERSION_ARR=(${BASH_VERSION//./ })
    # Only BASH version 4.4 and later have the nosort option.
    if [ ${BASH_VERSION_ARR[0]} -gt 4 ] || ([ ${BASH_VERSION_ARR[0]} -eq 4 ] && [ ${BASH_VERSION_ARR[1]} -ge 4 ]); then
        COMPLETION_OPTIONS="-o nosort"
    fi

    complete $COMPLETION_OPTIONS -F _m3cli_completion m3
}
rm -f ${HELP_FILE}
_m3_completionetup;
