#! /usr/bin/env bash
set -e

# Change current working directory to be the root, regardless of how this script is invoked
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

function build_app() {
  cd src || exit 1

  docker build \
  --tag "${DOCKER_REGISTRY:-local}/domos:${DOCKER_TAG:-latest}" \
  . || die "Failed to build"
}

function main() {
  build_app
}

main
