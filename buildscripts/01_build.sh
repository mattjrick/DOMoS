# Create a bash script to run dockerfile from root of directory
#! /usr/bin/env bash
set -e

# Change current working directory to be the root, regardless of how this script is invoked
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

function build_app() {
  cd src || exit 1

  docker build \
  --tag "local/devops-metrics:latest" \
  . || die "Failed to build"
}

function main() {
  build_app
}

main
