#!/bin/sh -l

set -x

# Dockerfile Path
DOCKERFILE="${1}/Dockerfile"

# Generate Docker Tag Name
FIRMWARE_NAME="$(echo "$INPUT_NAME" | cut -d'-' -f1)"
BOARD_NAME="$(if [ "$BOARD" != 'GENERIC' ]; then echo "$BOARD" | tr '[:upper:]' '[:lower:]'; else echo "$INPUT_PORT"; fi)"
PORT_PATH="${INPUT_PORT_ROOT}/${INPUT_PORT}"

# Image Info
DOCKER_ROOT="docker.pkg.github.com/bradenm/micropy-build"
DOCKER_TAG="${DOCKER_ROOT}/${FIRMWARE_NAME}-${BOARD_NAME}:${BRANCH}"
DOCKER_BASE_IMAGE="${INPUT_BASE_IMAGE}"
CONTAINER="$INPUT_NAME"

# Docker Authenticate
sh -c "docker login ${INPUT_DOCKER_REGISTRY} -u ${INPUT_DOCKER_USERNAME} -p ${INPUT_DOCKER_PASSWORD}"

# Paths
ARTIFACTS="/artifacts"
BINARIES="${INPUT_NAME}-${BRANCH}-${BOARD_NAME}" # (Uploaded Artifacts)
ABS_PORT_PATH="/micropython/${INPUT_PORT_PATH:=$PORT_PATH}"

# Build Image
echo
echo "--- BUILD CONFIG ---"
echo "BASE: ${DOCKER_BASE_IMAGE}"
echo "REPO: ${REPO}"
echo "BRANCH: ${BRANCH}"
echo "PORT: ${INPUT_PORT}"
echo "IDF: ${IDF}"
echo "IDF_REPO: ${IDF_REPO}"
echo "PORT_PATH: ${PORT_PATH}"
echo "BOARD: ${BOARD}"
echo "ARTIFACTS: ${ARTIFACTS}"
echo "BINARIES: ${BINARIES}"
echo "ABS_PORT_PATH: ${ABS_PORT_PATH}"
echo

docker build \
    --target mpbuild \
    --cache-from "$DOCKER_BASE_IMAGE" \
    -t "$DOCKER_TAG" \
    -f "$DOCKERFILE" . \
    --build-arg REPO="${REPO}" \
    --build-arg BRANCH="${BRANCH}" \
    --build-arg IDF="${IDF}" \
    --build-arg IDF_REPO="${IDF_REPO}" \
    --build-arg PORT_PATH="${PORT_PATH}" \
    --build-arg BOARD="${BOARD}"

# Gather Compiled Artifacts
sh -c "docker run --name ${CONTAINER} -i ${DOCKER_TAG} copy"

# Copy and Cleanup
sh -c "docker cp ${CONTAINER}:${ARTIFACTS} ./${BINARIES}"
sh -c "docker rm ${CONTAINER}"

# Publish Image
if [ "${GITHUB_REF}" = "refs/heads/master" ]; then
    sh -c "docker push ${DOCKER_TAG}"
fi

# Set Outputs
echo ::set-output name=binaries::$BINARIES
echo ::set-output name=tag::$DOCKER_TAG
