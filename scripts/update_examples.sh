#!/usr/bin/env bash

cd "$(dirname "$0")"
cd ../examples

set -e

for d in *; do
  if [ -d $d ]; then
    pushd $d
      rm -rf output
      echo "   Formatting..."
      paper fmt
      echo "   Building docx..."
      paper build --output-format docx --docx-revision 2
      echo "   Building latex+pdf..."
      paper build --output-format latex+pdf

      diffs=$(git diff output)
      if [[ ${#diff} -le 0 ]]; then
        cd .paper_data
          git checkout . 2> /dev/null
        cd ..
      fi
    popd
  fi
done
