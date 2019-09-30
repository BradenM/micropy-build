#!/bin/sh -l

# Dockerfile Path
DOCKERFILE="$1"

# Generate Docker Tag Name
FIRMWARE_NAME="$(cut -d'-' -f1 <<<"$INPUT_NAME")"
BOARD_NAME="$(if [ "$BOARD" != 'GENERIC' ]; then echo "$BOARD" | tr '[:upper:]' '[:lower:]'; else echo 'esp32'; fi)"

# Image Info
DOCKER_ROOT="docker.pkg.github.com/bradenm/micropy-build"
DOCKER_TAG="${DOCKER_ROOT}/${FIRMWARE_NAME}:${BRANCH}-${BOARD_NAME}"
CONTAINER="$INPUT_NAME"

# Build Image
sh -c "docker build -t ${DOCKER_TAG} ${DOCKERFILE}"

# Paths
ARTIFACTS="/artifacts"
BINARIES="${INPUT_NAME}-${BRANCH}-${BOARD_NAME}" # (Uploaded Artifacts)
ABS_PORT_PATH="/micropython/${INPUT_PORT_PATH}"

# Gather Compiled Artifacts
sh -c "docker run --name ${CONTAINER} -i ${DOCKER_TAG} bash -c 'mkdir -p ${ARTIFACTS} && find ${ABS_PORT_PATH}/ -path "*.bin" -exec cp {} ${ARTIFACTS}/ \;'"
sh -c "docker cp ${CONTAINER}:${ARTIFACTS} ./${BINARIES}"
sh -c "docker rm ${CONTAINER}"

# Publish Image
if [ "${GITHUB_REF}" = "refs/heads/master" ]; then
    sh -c "docker push ${DOCKER_TAG}"
fi

# Set Outputs
echo ::set-output binaries=BINARIES::$BINARIES
echo ::set-output tag=DOCKER_TAG::$DOCKER_TAG
