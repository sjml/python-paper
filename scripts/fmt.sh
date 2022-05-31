#!/usr/bin/env bash


cd "$(dirname "$0")"

set -e

# assumes you have stylua installed
#   https://github.com/johnnymorganz/stylua
pushd ../paper/resources/project_template/.paper_resources/filters
  echo "    Auto-formatting Lua files..."
  stylua --indent-type=Spaces --indent-width=2 ./*
popd
echo


# assumes you have black installed
#   https://black.readthedocs.io/en/stable/
pushd ../paper
  echo "    Auto-formatting Python files..."
  black --quiet --line-length 120 .
popd
echo
