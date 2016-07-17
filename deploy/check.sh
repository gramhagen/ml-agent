#!/bin/bash

# run everything by default
if [[ $# == 0 ]]; then
    LINT=1
    UNIT=1
    COV=1
else
    LINT=0
    UNIT=0
    COV=0

    for key in "$@"; do
        case ${key} in
            -l|--lint)
                LINT=1
                shift # past argument
                ;;
            -u|--unit)
                UNIT=1
                shift # past argument
                ;;
            -c|--cov)
                COV=1
                shift # past argument
                ;;
            *)
                # unknown option
                echo "unknown option ${key}"
                ;;
        esac
    done
fi

if [[ ${LINT} == 1 ]]; then
    find . -type f -name '*.py' ! -path './docs/*' | xargs pylint --rcfile=.pylintrc
fi

if [[ ${UNIT} == 1 ]]; then
    py.test tests
fi

if [[ ${COV} == 1 ]]; then
    py.test --cov predict --cov-report=html
    open htmlcov/index.html
fi
