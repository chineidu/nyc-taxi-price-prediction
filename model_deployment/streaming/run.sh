#!/bin/bash

# Change to the dir where the script is located
cd "$(dirname "$0")"

DOCKER_FILE="Dockerfile"


if [ ${IMAGE_NAME} == ""]; then
    TAG=`date +"%Y-%m-%d_%H-%M"`
    export IMAGE_NAME="stream-model-duration:${TAG}"
    echo "IMAGE_NAME is not set ... building a new image with tag: ${IMAGE_NAME}"
    docker build -t ${IMAGE_NAME} .
else
    echo "No need to to build image $IMAGE_NAME"
fi


docker-compose up -d
sleep 3

ERROR_CODE="$?"

python test_docker.py
if [ ${ERROR_CODE} != 0 ]; then
    # Run
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}

fi


echo "Done!"
