# DME Searcher - Data Mining Engine

Data Mining Engine that scans for personal information leaks across the web, including face images, contact information, and web assets.

## Overview

DME Searcher is an event-driven microservice that:
- Consumes scan requests from Apache Kafka
- Searches for personal data leaks using web search APIs
- Performs face matching against user-provided images via ML inference
- Publishes findings to downstream processing services

**Built for:** Production AWS deployment with SOC 2 compliance

---

## Quick Start

### Local Development

**Prerequisites:**
- Python 3.12+
- Docker & Docker Compose
- Git

**Setup:**

```bash
# Clone repository
git clone https://github.com/christophercorbin/Searchimage.git
cd Searchimage

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your local configuration

# Run locally (requires Kafka, MongoDB, OpenSearch running)
python start.py --env dev --flow quick
```

### Docker

**Build:**
```bash
docker build -f Dockerfile -t dme-searcher:latest .
```

**Run:**
```bash
docker run --rm \
  -e ENV=dev \
  -e FLOW=quick \
  dme-searcher:latest
```

**With Docker Compose (local dev environment):**
```bash
docker-compose up -d
# Starts: Kafka, MongoDB, OpenSearch, DME Searcher
```

---

## Architecture

```
GitHub Push (dev/staging/main)
    ↓
GitHub Actions Workflow
    ├─ Security Scanning (Bandit, Safety, Semgrep)
    ├─ Unit Tests (pytest)
    ├─ Docker Build (multi-stage, hardened)
    ├─ Image Scanning (Trivy)
    └─ Push to ECR (searcher-dev/stage/main)
    ↓
ECS Fargate Deployment
    ├─ Dev environment (auto-deploy)
    ├─ Staging environment (auto-deploy)
    └─ Prod environment (manual approval)
    ↓
Kafka Consumer
    ├─ Consumes scan requests
    ├─ Executes search workflow
    └─ Publishes results
```

---

## Deployment

### AWS Deployment

**Full deployment guide:** See [DEPLOYMENT.md](./DEPLOYMENT.md)

Quick deploy to dev:
```bash
# 1. Deploy infrastructure (one-time)
cd IaC/cloudformation
aws cloudformation create-stack \
  --stack-name dme-searcher-iam \
  --template-body file://iam-roles.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1

# 2. Push code (triggers CI/CD pipeline)
git push origin dev

# 3. Monitor deployment
aws logs tail /ecs/dme-searcher-dev --follow --region us-east-1
```

---

## Configuration

All configuration via environment variables. See [CONFIGURATION.md](./CONFIGURATION.md) for complete reference.

**Key Variables:**
```bash
ENV=dev|stage|prod        # Environment
FLOW=quick|full           # Search flow (1-2 pages vs 5 pages)
AWS_REGION=us-east-1      # AWS region
LOG_LEVEL=INFO|DEBUG      # Logging level
```

**Secrets (from AWS Secrets Manager):**
- `SERPER_API_KEY` - Google Serper API Key
- `MONGODB_URL` - MongoDB connection string

---

## Security

**Hardened Docker image with:**
- ✅ Non-root user (UID 10001)
- ✅ Read-only root filesystem
- ✅ Capability dropping (CAP_ALL)
- ✅ Multi-stage build
- ✅ Minimal base (Alpine)
- ✅ No package managers or shells
- ✅ All dependencies pinned

**Security docs:** See [SECURITY.md](./SECURITY.md) and [DOCKER_HARDENING.md](./DOCKER_HARDENING.md)

---

## Testing

**Unit Tests:**
```bash
pytest tests/unit/ -v --cov=clients --cov=services
```

**Integration Tests:**
```bash
pytest tests/integration/ -v
```

**All Tests:**
```bash
pytest tests/ -v --cov --cov-report=html
```

**Security Scanning:**
```bash
# Code security
bandit -r clients/ services/ repositories/ data/

# Dependency vulnerabilities
safety check

# SAST
semgrep --config=p/security-audit .
```

---

## Documentation

- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - AWS deployment, CloudFormation, ECS
- **[SECURITY.md](./SECURITY.md)** - Security policies, credential management, incident response
- **[DOCKER_HARDENING.md](./DOCKER_HARDENING.md)** - Container security, SOC 2 mapping
- **[CONFIGURATION.md](./CONFIGURATION.md)** - Environment variables, secrets, settings
- **[CI_CD_PIPELINE.md](./CI_CD_PIPELINE.md)** - GitHub Actions workflow explanation

---

## Repository Structure

```
dme-searcher/
├── src/
│   ├── clients/           # AWS, Kafka, database clients
│   ├── services/          # Business logic
│   ├── repositories/      # Data access layer
│   └── data/              # Models and DTOs
├── tests/                 # Unit and integration tests
├── IaC/
│   └── cloudformation/    # AWS infrastructure templates
├── .github/workflows/     # CI/CD pipelines
├── Dockerfile             # Hardened multi-stage build
├── requirements.txt       # Python dependencies (pinned)
├── docker-compose.yml     # Local dev environment
├── .env.example           # Environment template
└── docs/                  # Additional documentation
```

---

## Development Workflow

1. **Create branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and test locally:**
   ```bash
   pytest tests/ -v
   bandit -r clients/ services/
   ```

3. **Push and create PR:**
   ```bash
   git push origin feature/my-feature
   ```

4. **CI/CD validates:**
   - ✅ Code formatting
   - ✅ Security scanning
   - ✅ Unit tests
   - ✅ Integration tests

5. **Merge to dev/staging/main:**
   - Automatically builds Docker image
   - Pushes to ECR
   - Deploys to ECS

---

## Monitoring & Logs

**CloudWatch Logs:**
```bash
# View dev logs
aws logs tail /ecs/dme-searcher-dev --follow --region us-east-1

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/dme-searcher-dev \
  --filter-pattern "ERROR" \
  --region us-east-1
```

**CloudWatch Metrics:**
- CPU utilization
- Memory utilization
- Task count
- Custom application metrics

**Alarms:**
- High CPU (>90%)
- Low task count
- Deployment failures

---

## Troubleshooting

**Service not starting?**
```bash
# Check logs
aws logs tail /ecs/dme-searcher-dev --follow

# Check task status
aws ecs describe-tasks \
  --cluster dme-cluster \
  --tasks <task-arn> \
  --region us-east-1
```

**Image not found in ECR?**
```bash
# List images
aws ecr list-images --repository-name searcher-dev --region us-east-1

# Check pipeline ran successfully (GitHub Actions)
# Go to: https://github.com/christophercorbin/Searchimage/actions
```

**Cannot connect to Kafka?**
```bash
# Verify broker connectivity
telnet kafka-broker:9092

# Check security group rules
aws ec2 describe-security-groups --group-ids sg-12345678
```

---

## Contributing

1. Follow Python style guide (PEP 8)
2. Add tests for new features
3. Ensure all tests pass
4. Update documentation
5. Create PR with clear description

---

## Support

- **Documentation:** See docs/ directory and README links
- **Issues:** GitHub Issues
- **Security:** [SECURITY.md](./SECURITY.md)

---

## License

Proprietary - Protexxa Inc.

---

## Version

v1.0.0 - Hardened, SOC 2 aligned production release

## ECS Deployment Infrastructure

The following ECS infrastructure has been provisioned:
- **Cluster**: dme-cluster
- **Service**: dme-searcher-dev
- **Task Definition**: dme-searcher-dev:1
- **Task Execution Role**: ecsTaskExecutionRole
- **Task Role**: dme-searcher-task-role

GitHub Actions CI/CD pipeline now supports full deployment to ECS!
