#!/bin/bash
## sudo install-dependencies.sh
##
## Purpose: This script checks and installs pip and then installs devops-toolset-dependencies
## Requires: - Admin privileges

python3 -m pip --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    # Install pip
    sudo apt install python3-pip -y
fi

python3 -m pip install -r ../../requirements.txt