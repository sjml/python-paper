#!/usr/bin/env bash


cd "$(dirname "$0")"

set -e



# assumes you have stylua installed
#   https://github.com/johnnymorganz/stylua
pushd ../paper/resources/project_template/.paper_resources/filters > /dev/null
  echo "Auto-formatting Lua filters..."
  stylua --indent-type=Spaces --indent-width=2 ./*
popd > /dev/null

pushd ../paper/resources/writers > /dev/null
  echo "Auto-formatting Lua writers..."
  stylua --indent-type=Spaces --indent-width=2 ./*
popd > /dev/null



# assumes you have black installed
#   https://black.readthedocs.io/en/stable/
pushd ../paper > /dev/null
  echo "Auto-formatting Python files..."
  black --quiet --line-length 120 .
popd > /dev/null
