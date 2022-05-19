#!/usr/bin/env bash
set -eu
set -e pipefail

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install gitlint ansible ansible-test tox

gitlint install-hook

# Initialize tox venvs
tox -l > /dev/null
