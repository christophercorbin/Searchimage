# GitHub OIDC Setup Guide

This guide explains how to set up GitHub OIDC (OpenID Connect) authentication with your AWS account for the DME Searcher project.

## Overview

GitHub OIDC allows GitHub Actions to authenticate with AWS without storing long-lived credentials. Instead, temporary tokens are issued per workflow run, providing better security and compliance with SOC 2 standards.

**Benefits:**
- ✅ No AWS credentials stored in GitHub Secrets
- ✅ Temporary tokens (max 15 minutes) issued per workflow
- ✅ Fine-grained IAM policies
- ✅ Full audit trail in CloudTrail
- ✅ Automatic token rotation
- ✅ SOC 2 compliant

## Prerequisites

- AWS CLI v2 installed and configured
- IAM permissions to create roles and policies
- GitHub repository: `christophercorbin/Searchimage`
- AWS Account ID: `438465156498`

## Setup Steps

### Option 1: Automatic Setup (Recommended)

Run the provided setup script:

```bash
cd /path/to/DME-searcher
bash scripts/setup-github-oidc.sh
```

This script will:
1. Create `github-actions-ecr-role` (for Docker image push)
2. Create `github-actions-ecs-deploy-role` (for ECS deployment)
3. Attach appropriate IAM policies
4. Display confirmation with role ARNs

### Option 2: Manual Setup

If you prefer to set up manually, follow these steps:

#### Step 1: Create ECR Push Role

```bash
aws iam create-role \
  --role-name github-actions-ecr-role \
  --assume-role-policy-document file://IaC/cloudformation/github-oidc-trust-policy.json \
  --description "Role for GitHub Actions to push Docker images to ECR"
```

#### Step 2: Attach ECR Policy

```bash
aws iam put-role-policy \
  --role-name github-actions-ecr-role \
  --policy-name github-actions-ecr-policy \
  --policy-document file://IaC/cloudformation/github-actions-ecr-policy.json
```

#### Step 3: Create ECS Deployment Role

```bash
aws iam create-role \
  --role-name github-actions-ecs-deploy-role \
  --assume-role-policy-document file://IaC/cloudformation/github-oidc-trust-policy.json \
  --description "Role for GitHub Actions to deploy to ECS"
```

#### Step 4: Attach ECS Policy

```bash
aws iam put-role-policy \
  --role-name github-actions-ecs-deploy-role \
  --policy-name github-actions-ecs-policy \
  --policy-document file://IaC/cloudformation/github-actions-ecs-policy.json
```

## Verification

Verify that both roles were created successfully:

```bash
# List GitHub Actions roles
aws iam list-roles --query "Roles[?contains(RoleName, 'github-actions')]"

# Get ECR role ARN
aws iam get-role --role-name github-actions-ecr-role --query 'Role.Arn'

# Get ECS deployment role ARN
aws iam get-role --role-name github-actions-ecs-deploy-role --query 'Role.Arn'
```

Expected output:
```
arn:aws:iam::438465156498:role/github-actions-ecr-role
arn:aws:iam::438465156498:role/github-actions-ecs-deploy-role
```

## How It Works

### Trust Relationship

Both roles trust the GitHub OIDC provider with this condition:

```json
{
  "Principal": {
    "Federated": "arn:aws:iam::438465156498:oidc-provider/token.actions.githubusercontent.com"
  },
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
    },
    "StringLike": {
      "token.actions.githubusercontent.com:sub": "repo:christophercorbin/Searchimage:*"
    }
  }
}
```

This means:
- Only the GitHub OIDC provider can assume these roles
- Only from the `christophercorbin/Searchimage` repository
- For any branch or environment

### Workflow Integration

The GitHub Actions workflow uses OIDC by specifying:

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::438465156498:role/github-actions-ecr-role
    aws-region: us-east-1
```

The `configure-aws-credentials` action will:
1. Get a token from GitHub's OIDC provider
2. Exchange it for temporary AWS credentials
3. Set up AWS CLI with those credentials
4. Automatically refresh credentials as needed

## IAM Policies Explained

### github-actions-ecr-policy

Allows GitHub Actions to:
- Get authorization tokens for ECR
- Check, upload, and push image layers
- Describe and list repositories
- Create repositories and enable scanning

```json
{
  "ecr:GetAuthorizationToken",
  "ecr:BatchCheckLayerAvailability",
  "ecr:GetDownloadUrlForLayer",
  "ecr:PutImage",
  "ecr:InitiateLayerUpload",
  "ecr:UploadLayerPart",
  "ecr:CompleteLayerUpload",
  "ecr:CreateRepository",
  "ecr:PutImageScanningConfiguration"
}
```

**Restrictions:**
- Only for `searcher-dev`, `searcher-stage`, `searcher-main` repositories
- No delete permissions (can't delete images)
- No permission to modify repository access

### github-actions-ecs-policy

Allows GitHub Actions to:
- Describe ECS clusters, services, tasks, and task definitions
- Register new task definitions
- Update ECS services
- Pass IAM roles to ECS (for task execution)

```json
{
  "ecs:DescribeTaskDefinition",
  "ecs:DescribeServices",
  "ecs:DescribeClusters",
  "ecs:RegisterTaskDefinition",
  "ecs:UpdateService",
  "iam:PassRole"
}
```

**Restrictions:**
- Only for `dme-searcher-dev`, `dme-searcher-stage`, `dme-searcher-prod` services
- Only pass roles to `ecsTaskExecutionRole` and `dme-searcher-task-role`
- No permission to delete or stop services

## Troubleshooting

### Error: Role not found

**Symptom:** `The role with name github-actions-ecr-role cannot be found`

**Solution:** Run the setup script to create the roles:
```bash
bash scripts/setup-github-oidc.sh
```

### Error: OIDC provider not configured

**Symptom:** `OIDC provider is not configured`

**Solution:** The OIDC provider should already be set up. If not, it will be created when you first deploy the CloudFormation stack or when GitHub Actions first attempts to authenticate.

### Error: Not authorized to perform ecr:GetAuthorizationToken

**Symptom:** `User is not authorized to perform: ecr:GetAuthorizationToken on resource`

**Solution:**
1. Verify the role was created: `aws iam get-role --role-name github-actions-ecr-role`
2. Verify the policy is attached: `aws iam list-role-policies --role-name github-actions-ecr-role`
3. Re-run the setup script to ensure policies are current

### Workflow still shows old error

**Symptom:** GitHub Actions still shows old credential errors after setup

**Solution:**
1. Trigger a new workflow run (push to dev branch)
2. GitHub will re-read the role configuration
3. New run should authenticate successfully

## Auditing

All OIDC authentications are logged in CloudTrail:

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=AssumeRoleWithWebIdentity \
  --region us-east-1
```

You'll see entries like:
```json
{
  "EventName": "AssumeRoleWithWebIdentity",
  "EventSource": "sts.amazonaws.com",
  "Principal": "arn:aws:iam::438465156498:oidc-provider/token.actions.githubusercontent.com",
  "SourceIPAddress": "github-actions-runner-ip"
}
```

## Revoking Access

To revoke GitHub Actions access:

```bash
# Delete the role (all associated policies are deleted)
aws iam delete-role-policy \
  --role-name github-actions-ecr-role \
  --policy-name github-actions-ecr-policy

aws iam delete-role --role-name github-actions-ecr-role
```

Or update the trust relationship to restrict access:

```bash
# Update trust policy to deny all
aws iam update-assume-role-policy-document \
  --role-name github-actions-ecr-role \
  --policy-document file://deny-policy.json
```

## Related Documentation

- [AWS OIDC Documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [GitHub OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [AWS Actions Configure Credentials](https://github.com/aws-actions/configure-aws-credentials)

## Questions?

See the main DEPLOYMENT.md guide or check the GitHub Actions workflow at:
https://github.com/christophercorbin/Searchimage/actions
