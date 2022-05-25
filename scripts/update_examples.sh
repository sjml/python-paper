#!/usr/bin/env bash

cd "$(dirname "$0")"
cd ../examples

for d in *; do
  if [ -d $d ]; then
    pushd $d
      rm -rf output
      paper build --output-format docx
      paper build --output-format latex+pdf
    popd
  fi
done
