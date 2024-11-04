#!/bin/bash

# Variables
AWS_REGION="us-east-1" 
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_NAME="sentiment-analysis-app"
IMAGE_TAG="latest"
ECR_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG"

echo "Logging into Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

echo "Creating ECR repository..."
aws ecr create-repository --repository-name $ECR_REPOSITORY_NAME --region $AWS_REGION || echo "Repository already exists."

echo "Building the Docker image..."
docker build -t $ECR_REPOSITORY_NAME .

echo "Tagging the Docker image..."
docker tag $ECR_REPOSITORY_NAME:latest $ECR_URI

echo "Pushing the Docker image to ECR..."
docker push $ECR_URI

echo "Deployment completed. Your image is available at $ECR_URI"
