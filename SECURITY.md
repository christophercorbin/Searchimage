# Security Policy for DME Searcher

## Table of Contents

1. [Reporting Security Vulnerabilities](#reporting-security-vulnerabilities)
2. [Security Practices](#security-practices)
3. [Credential Management](#credential-management)
4. [Dependency Security](#dependency-security)
5. [Incident Response](#incident-response)
6. [Security Audit Trail](#security-audit-trail)

---

## Reporting Security Vulnerabilities

### Responsible Disclosure

If you discover a security vulnerability in DME Searcher, please report it responsibly:

**DO NOT** open a public GitHub issue for security vulnerabilities.

**INSTEAD:**

1. Email: `security@protexxa.com`
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

3. Allow up to 30 days for acknowledgment and patch before public disclosure

---

## Security Practices

### 1. Secrets Management

**Never commit secrets to git:**
- API keys
- Database passwords
- AWS credentials
- Private keys

**Proper secret management:**

```bash
# ❌ WRONG - Don't do this
echo "SERPER_API_KEY=abc123xyz" >> config.py

# ✅ RIGHT - Use AWS Secrets Manager
aws secretsmanager create-secret \
  --name dme-searcher/serper-api-key \
  --secret-string "abc123xyz"

# ✅ RIGHT - Use environment variables (for development)
export SERPER_API_KEY=abc123xyz
```

**Secrets in this project:**
- `SERPER_API_KEY` - Google Serper API Key (stored in Secrets Manager)
- `MONGODB_URL` - Database connection string (stored in Secrets Manager)
- `AWS_ACCESS_KEY_ID` - AWS credentials (use IAM roles instead)
- `AWS_SECRET_ACCESS_KEY` - AWS credentials (use IAM roles instead)

### 2. Code Review & Authorization

All code changes require:
- Pull request review by at least one authorized reviewer
- Automated security scanning must pass
- No secrets in code
- No direct commits to main/staging branches

### 3. Supply Chain Security

**Package Pinning:**
- All Python dependencies pinned to specific versions in `requirements.txt`
- Poetry lock file for reproducible builds (future)

**Vulnerability Scanning:**
- Automated with `safety` check in CI/CD
- `bandit` for security-specific Python issues
- `semgrep` for SAST analysis
- Trivy for container image scanning

**Commit Signing (Recommended):**
```bash
# Configure git to sign commits
git config --global user.signingkey <key-id>
git commit -S -m "Your message"
```

### 4. Access Control

**GitHub Repository Access:**
- Organization members only
- Branch protection on main/staging
- Require reviews before merge
- Require status checks to pass

**AWS Account Access:**
- Use GitHub OIDC for CI/CD (no long-lived credentials)
- Use IAM roles for ECS tasks
- Encrypt all data in transit (TLS)
- MFA on AWS console access (recommended)

**Database Access:**
- Use AWS Secrets Manager for connection strings
- Network isolation (VPC security groups)
- Read-only access where possible
- Encrypted connections (TLS)

### 5. Network Security

**External API Calls:**
- Google Serper API: HTTPS only
- AWS services: TLS with SigV4 authentication
- MongoDB: TLS encryption required
- OpenSearch: TLS encryption enforced

**Container Networking:**
- Read-only root filesystem enforced
- Dropped Linux capabilities
- Non-root user execution
- No unnecessary network exposure

---

## Credential Management

### AWS Credentials

**DO NOT use long-lived AWS credentials. Instead:**

1. **For CI/CD (GitHub Actions):**
   ```yaml
   - name: Configure AWS credentials
     uses: aws-actions/configure-aws-credentials@v4
     with:
       role-to-assume: arn:aws:iam::722568544242:role/github-actions-ecr-role
       aws-region: us-east-1
   ```

2. **For ECS Tasks:**
   - Use task execution role for pulling images
   - Use task role for application permissions

3. **For Local Development:**
   ```bash
   # Use AWS CLI with IAM user (development only)
   aws configure

   # Or use temporary credentials via STS
   aws sts assume-role --role-arn arn:aws:iam::722568544242:role/dev-role
   ```

### API Keys & Secrets

**Google Serper API Key:**
```bash
# Store in AWS Secrets Manager
aws secretsmanager create-secret \
  --name dme-searcher/serper-api-key \
  --secret-string "YOUR_API_KEY"

# Application retrieves at runtime
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='dme-searcher/serper-api-key')
api_key = secret['SecretString']
```

**MongoDB Credentials:**
```bash
# Store connection string in Secrets Manager
aws secretsmanager create-secret \
  --name dev/mongodb \
  --secret-string "mongodb://user:pass@host:27017/dme-dev"

# Application retrieves via environment variable in ECS
{
  "Secrets": [
    {
      "Name": "MONGODB_URL",
      "ValueFrom": "arn:aws:secretsmanager:us-east-1:...:secret:dev/mongodb"
    }
  ]
}
```

### Secret Rotation

```bash
# Update secret in AWS
aws secretsmanager update-secret \
  --secret-id dme-searcher/serper-api-key \
  --secret-string "NEW_API_KEY"

# Force ECS service to re-pull secret
aws ecs update-service \
  --cluster dme-cluster \
  --service dme-searcher-dev \
  --force-new-deployment
```

---

## Dependency Security

### Checking Dependencies

```bash
# List all installed packages
pip list

# Check for vulnerabilities
pip install safety
safety check

# Check specific package
pip show confluent-kafka
```

### Updating Dependencies

```bash
# Check for outdated packages
pip list --outdated

# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade pymongo

# Save updated requirements
pip freeze > requirements.txt
```

### Dangerous Dependencies

Avoid or carefully vet:
- Packages with known CVEs (security history)
- Unmaintained packages (no recent updates)
- Packages from untrusted sources
- Packages with suspicious dependencies

**Current Dependencies Review:**

| Package | Version | Status | Notes |
|---------|---------|--------|-------|
| confluent-kafka | 2.3.0 | ✅ Current | Maintained by Confluent |
| pymongo | 4.10.1 | ✅ Current | Maintained by MongoDB |
| boto3 | 1.34.69 | ✅ Current | Official AWS SDK |
| Pillow | 10.2.0 | ✅ Current | Active development |
| numpy | 1.26.4 | ✅ Current | Widely used, well-maintained |

---

## Incident Response

### Security Incident Report Form

If a security incident occurs:

1. **Immediate Actions:**
   - Stop the service if necessary
   - Collect evidence (logs, memory dumps)
   - Notify security team: `security@protexxa.com`

2. **Investigation:**
   - Determine root cause
   - Assess scope of impact
   - Identify affected systems/data

3. **Containment:**
   - Revoke compromised credentials
   - Patch vulnerability immediately
   - Deploy fixed image to production

4. **Communication:**
   - Notify affected parties
   - Document findings
   - Update security policies if needed

### Common Security Scenarios

**Scenario 1: Exposed API Key**
```bash
# 1. Immediately rotate the key
aws secretsmanager update-secret \
  --secret-id dme-searcher/serper-api-key \
  --secret-string "NEW_KEY"

# 2. Force service update
aws ecs update-service \
  --cluster dme-cluster \
  --service dme-searcher-dev \
  --force-new-deployment

# 3. Monitor for unauthorized usage
aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=dme-searcher

# 4. Review IAM policies
aws iam get-role-policy --role-name dme-searcher-task-role --policy-name dme-searcher-task-policy
```

**Scenario 2: Vulnerability in Dependency**
```bash
# 1. Update dependency
pip install --upgrade vulnerable-package

# 2. Run tests
pytest tests/ --cov=80

# 3. Rebuild image
docker build -f Dockerfile -t dme-searcher:patched .

# 4. Push to ECR
docker push 722568544242.dkr.ecr.us-east-1.amazonaws.com/searcher-dev:patched

# 5. Update ECS task definition
aws ecs register-task-definition \
  --cli-input-json file://task-def.json

# 6. Deploy
aws ecs update-service \
  --cluster dme-cluster \
  --service dme-searcher-dev \
  --task-definition dme-searcher-dev:2 \
  --force-new-deployment
```

**Scenario 3: Unauthorized Container Image**
```bash
# 1. Check ECR image history
aws ecr describe-images \
  --repository-name searcher-dev \
  --image-ids imageTag=latest-dev

# 2. Revoke access
aws iam update-assume-role-policy \
  --role-name dme-searcher-task-role \
  --policy-document file://restricted-policy.json

# 3. Scan image
trivy image --severity CRITICAL searcher-dev:latest-dev

# 4. Delete suspicious images
aws ecr batch-delete-image \
  --repository-name searcher-dev \
  --image-ids imageTag=suspicious-tag
```

---

## Security Audit Trail

### What Gets Logged

1. **CloudWatch Logs:**
   - Application startup/shutdown
   - Event processing (aggregated)
   - Errors and exceptions
   - Performance metrics

2. **AWS CloudTrail:**
   - IAM role assumptions (GitHub OIDC)
   - ECR image pushes/pulls
   - ECS service updates
   - Secrets Manager access

3. **GitHub Audit Log:**
   - Code repository access
   - Branch protection changes
   - Deployment approvals
   - Secrets rotation

### Accessing Audit Logs

```bash
# CloudWatch Logs
aws logs tail /ecs/dme-searcher-dev --follow

# CloudTrail events (last 90 days)
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceType,AttributeValue=ECR \
  --max-results 10

# GitHub Audit Logs
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/orgs/christophercorbin/audit-log
```

### Compliance Requirements

**SOC 2 Logging Requirements:**
- Retain logs for 90+ days
- Encrypt logs in transit (TLS)
- Restrict access to logs (IAM)
- Monitor for suspicious activity
- Alert on security events

---

## Security Contacts

- **Security Team:** security@protexxa.com
- **DevOps Lead:** devops@protexxa.com
- **AWS Support:** https://console.aws.amazon.com/support

---

## Related Documents

- [DEPLOYMENT.md](./DEPLOYMENT.md) - AWS deployment security
- [DOCKER_HARDENING.md](./DOCKER_HARDENING.md) - Container security
- [CONFIGURATION.md](./CONFIGURATION.md) - Configuration security
- [CI_CD_PIPELINE.md](./CI_CD_PIPELINE.md) - Pipeline security

