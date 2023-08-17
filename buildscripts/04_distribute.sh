#! /usr/bin/env bash
set -e

# Change current working directory to be the root, regardless of how this script is invoked
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1

function get_branch_name() {
    BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
}

function distribute_app() {
  ls
  cd src || exit 1

  docker build \
  --tag="${DOCKER_REGISTRY:-local}/domos:${DOCKER_TAG}" \
  . || die "Failed to build ${DOCKER_REGISTRY:-local}/domos:${DOCKER_TAG}"
}

function push_image() {
    echo "Pushing image to Docker Hub"
    docker push "${DOCKER_REGISTRY:-local}/domos:${DOCKER_TAG}"
}

function main() {
  echo "Packaging DevOps Metrics of Success"

  get_branch_name

  if [[ $BRANCH_NAME == "main" ]]; then
    echo "Building main branch so tag as latest"
    DOCKER_TAG="latest"
  else
    echo "Building branch $BRANCH_NAME"
    DOCKER_TAG="$BRANCH_NAME"
  fi

  distribute_app

  if [[ -n $DOCKER_REGISTRY ]]; then
    push_image
  fi
}

main
