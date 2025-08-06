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

# Run collectstatic inside the new container
docker run --rm \
    --env DEBUG=0 --env REDIS_PORT=6379 --env DB_PORT=5432 --env DB_NAME=livescores \
    "${ECR_REPO_URI}:${IMAGE_TAG}" \
    python manage.py collectstatic --noinput

# Run migrations inside the new container
docker run --rm \
    --env DEBUG=0 --env REDIS_PORT=6379 --env DB_PORT=5432 --env DB_NAME=livescores \
    "${ECR_REPO_URI}:${IMAGE_TAG}" \
    python manage.py migrate --noinput

# Run the container
docker run -d \
    --env DEBUG=0 --env REDIS_PORT=6379 --env DB_PORT=5432 --env DB_NAME=livescores \
    --name livescores-backend \
    -p 80:8001 \
    "${ECR_REPO_URI}:${IMAGE_TAG}" \
    daphne -b 0.0.0.0 -p 8001 live_scores.asgi:application