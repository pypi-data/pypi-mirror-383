#!/bin/bash
set -e

scripts_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="${scripts_dir}/.."

cd "${repo_dir}"

# Required by Webpack 4+ on Node 17+ https://github.com/webpack/webpack/issues/14532
# export NODE_OPTIONS=--openssl-legacy-provider

rm -fr src/css/background-color/*
rm -fr src/css/color/*
rm -f src/css/background-color.scss
rm -f src/css/color.scss

rm -fr cjs/*
rm -fr css/*
rm -fr demo/*
rm -fr illustrator/*
rm -fr umd/*

node scripts/build-js.js
node scripts/build-css.js
node scripts/build-illustrator.js
node scripts/build-demo.js

rm -fr build/*
rm -fr dist/*

uv build
.venv/bin/twine check dist/*
