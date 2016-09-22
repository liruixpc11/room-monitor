#!/usr/bin/env bash

mkdir -p dist/ 2>/dev/null >/dev/null
cd $(dirname "$0")
cd ..

cd static
browserify main.src.js | uglifyjs > main.bin.js
