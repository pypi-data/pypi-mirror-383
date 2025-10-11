#!/bin/bash
set -e

scripts_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="${scripts_dir}/.."

if ([ "$1" == "--help" ] || [ -z "$1" ]); then
    echo "Usage: publish.sh [version]"
    echo ""
    echo "Example: ./publish.sh 0.0.1"
    exit 1
fi

cd "${repo_dir}"
npm publish
.venv/bin/twine upload --config-file .pypirc --verbose dist/*
gh release create $1
