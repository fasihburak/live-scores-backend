#!/bin/bash

# Fail immediately
set -e

# Usage: ./deploy_on_ec2.sh <ECR_REPO_URI> <image_tag>
ECR_REPO_URI="$1"
IMAGE_TAG="$2"

echo "ECR_REPO_URI: $ECR_REPO_URI"
echo "IMAGE_TAG: $IMAGE_TAG"

# Remove unused images
docker container prune -f
docker image prune -a -f

# Login to ECR
aws ecr get-login-password --region eu-central-1 | \
    docker login --username AWS --password-stdin "$ECR_REPO_URI"

# Pull the image
docker pull "${ECR_REPO_URI}:${IMAGE_TAG}"

# Stop and remove the existing container if it exists
docker stop livescores-backend || true
docker rm livescores-backend || true

ENV_FILE_NAME="prod.env" 
touch $ENV_FILE_NAME
echo "DEBUG=0" >> $ENV_FILE_NAME 
echo "REDIS_PORT=6379 " >> $ENV_FILE_NAME 
echo "DB_PORT=5432 " >> $ENV_FILE_NAME 
echo "DB_NAME=livescores" >> $ENV_FILE_NAME 


# Run collectstatic inside the new container
docker run --rm \
    --env-file ${ENV_FILE_NAME} \
    "${ECR_REPO_URI}:${IMAGE_TAG}" \
    python manage.py collectstatic --noinput

# Run migrations inside the new container
docker run --rm \
    --env-file ${ENV_FILE_NAME} \
    "${ECR_REPO_URI}:${IMAGE_TAG}" \
    python manage.py migrate --noinput

# Run the container
docker run -d \
    --env-file ${ENV_FILE_NAME} \
    --name livescores-backend \
    -p 80:8001 \
    "${ECR_REPO_URI}:${IMAGE_TAG}" \
    daphne -b 0.0.0.0 -p 8001 live_scores.asgi:application