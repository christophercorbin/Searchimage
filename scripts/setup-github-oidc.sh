#!/bin/bash

# Setup script for GitHub OIDC integration with AWS
# This script creates IAM roles for GitHub Actions OIDC authentication

set -e

AWS_ACCOUNT_ID="438465156498"
AWS_REGION="us-east-1"
GITHUB_ORG="christophercorbin"
GITHUB_REPO="Searchimage"
OIDC_PROVIDER_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"

echo "🔧 Setting up GitHub OIDC integration..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Step 1: Create ECR push role
echo "📌 Step 1: Creating github-actions-ecr-role..."

aws iam create-role \
  --role-name github-actions-ecr-role \
  --assume-role-policy-document file://IaC/cloudformation/github-oidc-trust-policy.json \
  --description "Role for GitHub Actions to push Docker images to ECR" \
  --region $AWS_REGION 2>/dev/null || echo "⚠️  Role github-actions-ecr-role already exists"

# Attach ECR policy
echo "📌 Attaching ECR push policy..."
aws iam put-role-policy \
  --role-name github-actions-ecr-role \
  --policy-name github-actions-ecr-policy \
  --policy-document file://IaC/cloudformation/github-actions-ecr-policy.json

echo "✅ ECR role created and policy attached"

# Step 2: Create ECS deployment role
echo ""
echo "📌 Step 2: Creating github-actions-ecs-deploy-role..."

aws iam create-role \
  --role-name github-actions-ecs-deploy-role \
  --assume-role-policy-document file://IaC/cloudformation/github-oidc-trust-policy.json \
  --description "Role for GitHub Actions to deploy to ECS" \
  --region $AWS_REGION 2>/dev/null || echo "⚠️  Role github-actions-ecs-deploy-role already exists"

# Attach ECS policy
echo "📌 Attaching ECS deployment policy..."
aws iam put-role-policy \
  --role-name github-actions-ecs-deploy-role \
  --policy-name github-actions-ecs-policy \
  --policy-document file://IaC/cloudformation/github-actions-ecs-policy.json

echo "✅ ECS deployment role created and policy attached"

# Step 3: Verify roles were created
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Verifying roles..."
echo ""

echo "GitHub Actions ECR Role:"
aws iam get-role --role-name github-actions-ecr-role --query 'Role.Arn' --output text
echo ""

echo "GitHub Actions ECS Deploy Role:"
aws iam get-role --role-name github-actions-ecs-deploy-role --query 'Role.Arn' --output text
echo ""

# Step 4: Display trust relationships
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ GitHub OIDC Setup Complete!"
echo ""
echo "🔐 Trust Relationships Configured:"
echo "  - Both roles trust: $OIDC_PROVIDER_ARN"
echo "  - For repository: christophercorbin/Searchimage"
echo ""
echo "📊 Roles Created:"
echo "  1. github-actions-ecr-role (ECR push + authentication)"
echo "  2. github-actions-ecs-deploy-role (ECS updates + IAM pass role)"
echo ""
echo "🚀 Next Steps:"
echo "  1. GitHub Actions workflows can now authenticate with OIDC"
echo "  2. Push code to dev branch to trigger pipeline"
echo "  3. Monitor: https://github.com/christophercorbin/Searchimage/actions"
echo ""
echo "✨ No AWS credentials stored in GitHub Secrets required!"

