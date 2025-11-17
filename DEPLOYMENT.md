# DME Searcher - AWS Deployment Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Account Setup](#aws-account-setup)
3. [GitHub OIDC Configuration](#github-oidc-configuration)
4. [Infrastructure Deployment](#infrastructure-deployment)
5. [Docker Image Build & Push](#docker-image-build--push)
6. [ECS Deployment](#ecs-deployment)
7. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
8. [Environment Variables & Secrets](#environment-variables--secrets)

---

## Prerequisites

Before starting, ensure you have:

- **AWS Account** with appropriate permissions (Admin or custom role)
- **AWS CLI v2** installed and configured
- **Docker** installed locally
- **Git** with SSH keys configured for GitHub
- **IAM User** with sufficient permissions for CloudFormation, ECR, ECS, Secrets Manager
- **GitHub Personal Access Token** (optional, for private repos)

### Required AWS Permissions

The minimal IAM policy needed:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:*",
        "ecr:*",
        "ecs:*",
        "logs:*",
        "cloudformation:*",
        "secretsmanager:*",
        "cloudwatch:*"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## AWS Account Setup

### Step 1: Create AWS Secrets

Store sensitive configuration in AWS Secrets Manager:

```bash
# Create Serper API Key secret
aws secretsmanager create-secret \
  --name dme-searcher/serper-api-key \
  --description "Google Serper API Key" \
  --secret-string "YOUR_SERPER_API_KEY" \
  --region us-east-1

# Create MongoDB connection strings
# For dev
aws secretsmanager create-secret \
  --name dev/mongodb \
  --description "MongoDB connection string for dev" \
  --secret-string "mongodb://user:password@hostname:27017/dme-dev" \
  --region us-east-1

# For staging
aws secretsmanager create-secret \
  --name staging/mongodb \
  --description "MongoDB connection string for staging" \
  --secret-string "mongodb://user:password@hostname:27017/dme-stage" \
  --region us-east-1

# For production
aws secretsmanager create-secret \
  --name prod/mongodb \
  --description "MongoDB connection string for production" \
  --secret-string "mongodb://user:password@hostname:27017/dme" \
  --region us-east-1
```

### Step 2: Tag Resources for Organization

```bash
# Tag ECR repositories
aws ecr tag-resource \
  --resource-arn "arn:aws:ecr:us-east-1:722568544242:repository/searcher-dev" \
  --tags Key=Project,Value=DMESearcher Key=Environment,Value=dev
```

---

## GitHub OIDC Configuration

GitHub Actions uses OpenID Connect (OIDC) to authenticate with AWS without storing long-lived credentials.

### Step 1: Deploy IAM Stack

```bash
cd IaC/cloudformation

# Deploy IAM roles and OIDC provider
aws cloudformation create-stack \
  --stack-name dme-searcher-iam \
  --template-body file://iam-roles.yml \
  --parameters \
    ParameterKey=GitHubOrg,ParameterValue=christophercorbin \
    ParameterKey=GitHubRepo,ParameterValue=Searchimage \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# Wait for stack to complete
aws cloudformation wait stack-create-complete \
  --stack-name dme-searcher-iam \
  --region us-east-1
```

### Step 2: Verify OIDC Provider

```bash
# List OIDC providers
aws iam list-open-id-connect-providers

# Should see: token.actions.githubusercontent.com
```

### Step 3: GitHub Repository Secrets

Add these secrets to your GitHub repository settings (**Settings → Secrets and variables → Actions**):

```
AWS_REGION = us-east-1
AWS_ACCOUNT_ID = 722568544242
```

---

## Infrastructure Deployment

### Step 1: Create ECR Repositories

```bash
# Deploy ECR stack
aws cloudformation create-stack \
  --stack-name dme-searcher-ecr \
  --template-body file://ecr-repositories.yml \
  --parameters ParameterKey=AWSAccountId,ParameterValue=722568544242 \
  --region us-east-1

# Wait for completion
aws cloudformation wait stack-create-complete \
  --stack-name dme-searcher-ecr \
  --region us-east-1

# Get ECR repository URIs
aws cloudformation describe-stacks \
  --stack-name dme-searcher-ecr \
  --query 'Stacks[0].Outputs' \
  --region us-east-1
```

**Output:**
```
SearcherDevRepositoryUri: 722568544242.dkr.ecr.us-east-1.amazonaws.com/searcher-dev
SearcherStageRepositoryUri: 722568544242.dkr.ecr.us-east-1.amazonaws.com/searcher-stage
SearcherMainRepositoryUri: 722568544242.dkr.ecr.us-east-1.amazonaws.com/searcher-main
```

### Step 2: Create ECS Infrastructure

**Before deploying, update the following in `ecs-infrastructure.yml`:**

1. Replace subnet IDs with your VPC subnets:
   ```yaml
   Subnets:
     - subnet-xxxxxxxx  # Your subnet
   ```

2. Replace security group:
   ```yaml
   SecurityGroups:
     - sg-xxxxxxxx  # Your security group
   ```

```bash
# Deploy ECS for DEV
aws cloudformation create-stack \
  --stack-name dme-searcher-ecs-dev \
  --template-body file://ecs-infrastructure.yml \
  --parameters \
    ParameterKey=EnvironmentName,ParameterValue=dev \
    ParameterKey=ContainerImage,ParameterValue=722568544242.dkr.ecr.us-east-1.amazonaws.com/searcher-dev:latest-dev \
    ParameterKey=DesiredTaskCount,ParameterValue=1 \
    ParameterKey=TaskMemory,ParameterValue=512 \
    ParameterKey=TaskCPU,ParameterValue=256 \
  --region us-east-1

# Deploy ECS for STAGING
aws cloudformation create-stack \
  --stack-name dme-searcher-ecs-stage \
  --template-body file://ecs-infrastructure.yml \
  --parameters \
    ParameterKey=EnvironmentName,ParameterValue=stage \
    ParameterKey=ContainerImage,ParameterValue=722568544242.dkr.ecr.us-east-1.amazonaws.com/searcher-stage:latest-staging \
    ParameterKey=DesiredTaskCount,ParameterValue=2 \
    ParameterKey=TaskMemory,ParameterValue=1024 \
    ParameterKey=TaskCPU,ParameterValue=512 \
  --region us-east-1

# Deploy ECS for PRODUCTION
aws cloudformation create-stack \
  --stack-name dme-searcher-ecs-prod \
  --template-body file://ecs-infrastructure.yml \
  --parameters \
    ParameterKey=EnvironmentName,ParameterValue=prod \
    ParameterKey=ContainerImage,ParameterValue=722568544242.dkr.ecr.us-east-1.amazonaws.com/searcher-main:latest \
    ParameterKey=DesiredTaskCount,ParameterValue=3 \
    ParameterKey=TaskMemory,ParameterValue=2048 \
    ParameterKey=TaskCPU,ParameterValue=1024 \
  --region us-east-1

# Wait for all stacks
aws cloudformation wait stack-create-complete --stack-name dme-searcher-ecs-dev --region us-east-1
aws cloudformation wait stack-create-complete --stack-name dme-searcher-ecs-stage --region us-east-1
aws cloudformation wait stack-create-complete --stack-name dme-searcher-ecs-prod --region us-east-1
```

---

## Docker Image Build & Push

### Option 1: GitHub Actions (Automated)

Simply push to your branch:

```bash
git add .
git commit -m "Deploy to AWS"

# Push to dev branch → builds and pushes to searcher-dev ECR
git push origin dev

# Push to staging branch → builds and pushes to searcher-stage ECR
git push origin staging

# Push to main branch → builds and pushes to searcher-main ECR (prod)
git push origin main
```

GitHub Actions will automatically:
1. Run security scans
2. Run unit tests
3. Build Docker image
4. Push to appropriate ECR repo
5. Deploy to ECS (for dev/staging automatically, requires approval for main)

### Option 2: Manual Build & Push

```bash
# Build the image
docker build -f Dockerfile -t searcher:latest .

# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 722568544242.dkr.ecr.us-east-1.amazonaws.com

# Tag the image
docker tag searcher:latest 722568544242.dkr.ecr.us-east-1.amazonaws.com/searcher-dev:latest-dev

# Push to ECR
docker push 722568544242.dkr.ecr.us-east-1.amazonaws.com/searcher-dev:latest-dev
```

---

## ECS Deployment

### Check ECS Services

```bash
# Get service status
aws ecs describe-services \
  --cluster dme-cluster \
  --services dme-searcher-dev \
  --region us-east-1

# List tasks
aws ecs list-tasks \
  --cluster dme-cluster \
  --service-name dme-searcher-dev \
  --region us-east-1

# Describe specific task
aws ecs describe-tasks \
  --cluster dme-cluster \
  --tasks arn:aws:ecs:us-east-1:722568544242:task/dme-cluster/12345678 \
  --region us-east-1
```

### View Logs

```bash
# Get recent logs
aws logs tail /ecs/dme-searcher-dev --follow --region us-east-1

# Get specific log stream
aws logs describe-log-streams \
  --log-group-name /ecs/dme-searcher-dev \
  --region us-east-1
```

### Manual Service Update

```bash
# Force new deployment
aws ecs update-service \
  --cluster dme-cluster \
  --service dme-searcher-dev \
  --force-new-deployment \
  --region us-east-1
```

---

## Monitoring & Troubleshooting

### CloudWatch Metrics

```bash
# View CPU utilization
aws cloudwatch get-metric-statistics \
  --namespace ECS/ContainerInsights \
  --metric-name CPUUtilization \
  --dimensions Name=ServiceName,Value=dme-searcher-dev \
              Name=ClusterName,Value=dme-cluster \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T01:00:00Z \
  --period 300 \
  --statistics Average \
  --region us-east-1
```

### Common Issues

**Issue: "Image not found" error**
```bash
# Verify image exists in ECR
aws ecr list-images --repository-name searcher-dev --region us-east-1

# Check task definition references correct image
aws ecs describe-task-definition \
  --task-definition dme-searcher-dev \
  --region us-east-1
```

**Issue: "No logs in CloudWatch"**
```bash
# Verify log group exists
aws logs describe-log-groups --region us-east-1 | grep dme-searcher

# Check task execution role has CloudWatch permissions
aws iam get-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-name ecs-task-execution-policy
```

**Issue: "Cannot pull image from ECR"**
```bash
# Verify ECR authentication
aws ecr get-authorization-token --region us-east-1

# Check security group allows outbound HTTPS
aws ec2 describe-security-groups --group-ids sg-12345678
```

---

## Environment Variables & Secrets

### Application Configuration

All configuration is loaded from:
1. **Environment Variables** (from ECS task definition)
2. **AWS Secrets Manager** (for sensitive data)

Example ECS task environment variables:
```json
{
  "Environment": [
    {"Name": "ENV", "Value": "dev"},
    {"Name": "FLOW", "Value": "quick"},
    {"Name": "AWS_REGION", "Value": "us-east-1"},
    {"Name": "LOG_LEVEL", "Value": "INFO"}
  ],
  "Secrets": [
    {"Name": "SERPER_API_KEY", "ValueFrom": "arn:aws:secretsmanager:..."},
    {"Name": "MONGODB_URL", "ValueFrom": "arn:aws:secretsmanager:..."}
  ]
}
```

### Updating Secrets

```bash
# Update Serper API key
aws secretsmanager update-secret \
  --secret-id dme-searcher/serper-api-key \
  --secret-string "NEW_API_KEY" \
  --region us-east-1

# Update MongoDB connection
aws secretsmanager update-secret \
  --secret-id dev/mongodb \
  --secret-string "mongodb://user:password@host:27017/dme-dev" \
  --region us-east-1

# After updating, force new ECS deployment
aws ecs update-service \
  --cluster dme-cluster \
  --service dme-searcher-dev \
  --force-new-deployment \
  --region us-east-1
```

---

## Next Steps

1. **Configure GitHub Repository**: Add AWS secrets to GitHub Actions
2. **Deploy Infrastructure**: Run CloudFormation stacks
3. **Push Code**: Trigger CI/CD pipeline with git push
4. **Monitor Deployment**: Watch CloudWatch logs and ECS service status
5. **Test Application**: Validate Kafka connection and event processing

For more details, see:
- [CONFIGURATION.md](./CONFIGURATION.md) - All environment variables
- [DOCKER_HARDENING.md](./DOCKER_HARDENING.md) - Security details
- [CI_CD_PIPELINE.md](./CI_CD_PIPELINE.md) - GitHub Actions workflow
