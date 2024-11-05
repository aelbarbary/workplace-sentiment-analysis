#!/bin/bash

AWS_REGION="us-east-1" 
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_NAME="sentiment-analysis-app"
IMAGE_TAG="latest"
ECR_URI="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG"

echo "Logging into Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

echo "Pulling the Docker image..."
docker pull $ECR_URI

# Step 3: Run the Docker container
echo "Running the Docker container..."
docker run -d -p 80:5000 $ECR_URI || { echo "Failed to run the container"; exit 1; }

