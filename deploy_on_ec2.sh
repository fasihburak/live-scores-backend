#!/bin/bash

# Usage: ./deploy_on_ec2.sh <ecr_repo_url> <image_tag>
ECR_REPO_URL="$1"
IMAGE_TAG="$2"

# Remove unused images
docker image prune -f

# Login to ECR
aws ecr get-login-password --region eu-central-1 | \
    docker login --username AWS --password-stdin "$ECR_REPO_URL"

# Pull the image
docker pull "${ECR_REPO_URL}:${IMAGE_TAG}"

# Stop and remove the existing container if it exists
docker stop livescores-backend || true
docker rm livescores-backend || true

# Run collectstatic inside the new container
docker run --rm \
    --env DEBUG=0 \
    "${ECR_REPO_URL}:${IMAGE_TAG}" \
    python manage.py collectstatic --noinput

# Run migrations inside the new container
docker run --rm \
    --env DEBUG=0 \
    "${ECR_REPO_URL}:${IMAGE_TAG}" \
    python manage.py migrate --noinput

# Run the container
docker run -d \
    --env DEBUG=0 \
    --name livescores-backend \
    -p 80:8001 \
    "${ECR_REPO_URL}:${IMAGE_TAG}" \
    daphne -b 0.0.0.0 -p 8001 live_scores.asgi:application