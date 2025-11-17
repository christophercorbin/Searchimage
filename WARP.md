# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

DME Searcher is a Python 3.12+ event-driven microservice that scans for personal information leaks across the web. It consumes scan requests from Apache Kafka, searches for personal data using Google Serper API, performs ML-based face matching via AWS SageMaker inference endpoints, and publishes findings to downstream services. Built for production AWS deployment with SOC 2 compliance requirements.

## Key Commands

### Local Development

```bash
# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally (requires Kafka, MongoDB, OpenSearch)
python start.py --env dev --flow quick
python start.py --env dev --flow full
python start.py --env stage --flow quick
python start.py --env prod --flow full
```

### Testing

```bash
# Unit tests only
pytest tests/unit/ -v --cov=clients --cov=services --cov=repositories

# Integration tests only
pytest tests/integration/ -v

# All tests with coverage
pytest tests/ -v --cov --cov-report=html

# Run single test file
pytest tests/unit/test_scan_request_dto.py -v
```

### Security Scanning

```bash
# Python security scanning
bandit -r clients/ services/ repositories/ data/

# Dependency vulnerability check
safety check

# SAST analysis
semgrep --config=p/security-audit .

# Container image scanning
docker build -f Dockerfile -t dme-searcher:test .
trivy image dme-searcher:test
```

### Docker

```bash
# Build (regular)
docker build -f Dockerfile -t dme-searcher:latest .

# Build (hardened)
docker build -f Dockerfile.hardened -t dme-searcher:hardened .

# Run locally
docker run --rm \
  -e ENV=dev \
  -e FLOW=quick \
  dme-searcher:latest

# Docker Compose (local dev environment with Kafka, MongoDB, OpenSearch)
docker-compose up -d
```

### AWS CloudWatch Logs

```bash
# Tail dev logs
aws logs tail /ecs/dme-searcher-dev --follow --region us-east-1

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/dme-searcher-dev \
  --filter-pattern "ERROR" \
  --region us-east-1

# Tail staging logs
aws logs tail /ecs/dme-searcher-stage --follow --region us-east-1
```

### AWS ECS

```bash
# Check service status
aws ecs describe-services \
  --cluster dme-cluster \
  --services dme-searcher-dev \
  --region us-east-1

# Check task details
aws ecs describe-tasks \
  --cluster dme-cluster \
  --tasks <task-arn> \
  --region us-east-1

# Force new deployment
aws ecs update-service \
  --cluster dme-cluster \
  --service dme-searcher-dev \
  --force-new-deployment \
  --region us-east-1
```

## Architecture

### Event-Driven Flow

1. **EventConsumer** (`clients/event_consumer.py`) subscribes to Kafka topics:
   - `dme-searcher-dev` (quick flow)
   - `dme-searcher-full-dev` (full flow)
   
2. **EventHandler** (`services/event_handler.py`) orchestrates the scan workflow:
   - Validates and updates scan status (`ScanService`)
   - Processes user-uploaded images (`UserService`)
   - Searches web for exposures (`WebSearcher`)
   - Performs face matching via vector search (`VectorSearcher`)
   - Filters duplicate results for existing users
   - Publishes results to detector workers via Kafka

3. **EventProducer** (`clients/event_producer.py`) dispatches to detector workers:
   - `dme-detector-dev` (quick flow)
   - `dme-detector-full-dev` (full flow)

### Layered Architecture

```
services/          # Business logic layer
├── event_handler.py      # Main orchestrator
├── scan_service.py       # Scan state management
├── user_service.py       # User image processing & leak filtering
├── web_searcher.py       # Google Serper API integration
├── vector_searcher.py    # OpenSearch face vector similarity
├── image_processor.py    # ML face embedding via SageMaker
└── util_service.py       # Shared utilities

repositories/      # Data access layer
├── scan_repo.py          # MongoDB scans collection
├── leak_repo.py          # MongoDB leaks collection
├── user_image_repo.py    # MongoDB userImages collection
├── web_image_repo.py     # MongoDB webImages collection
├── opensearch_repo.py    # OpenSearch face vectors (ANN search)
└── storage_s3_repo.py    # S3 image storage

data/              # Domain models & DTOs
├── scan_request_dto.py   # Inbound scan request from Kafka
├── detector_request_dto.py # Outbound to detector workers
├── scan_entity.py        # Scan database model
├── leak_entity.py        # Leak database model
└── [other entities/DTOs]

clients/           # Infrastructure clients
├── event_consumer.py     # Kafka consumer (Confluent)
├── event_producer.py     # Kafka producer
└── db.py                 # MongoDB client with AWS Secrets Manager
```

### Environment Configuration

Config follows singleton pattern with environment-specific classes (`config.py`):
- **BaseConfig** (dev): Default development settings
- **TestConfig**: Unit/integration test overrides
- **StageConfig**: Staging environment
- **ProdConfig**: Production (main broker cluster)
- **Prod1445Config**: Production (secondary broker cluster)

IMPORTANT: Call `Config.get(env)` in `start.py` BEFORE importing any application modules to ensure consistent environment.

### Search Flows

**Quick Flow** (`--flow quick`):
- 1 page per search term
- 10 results per page (images), 10 results per page (sites)
- Faster, lower cost

**Full Flow** (`--flow full`):
- 5 pages per search term  
- 100 results per page
- Comprehensive scan, higher cost

Configuration: `MAX_PAGES_TO_SEARCH_[QUICK|FULL]` and `MAX_SEARCH_RESULTS_PER_PAGE_[QUICK|FULL]`

### External Dependencies

- **Kafka**: Event-driven messaging (MSK clusters in AWS)
- **MongoDB**: Primary datastore for scans, leaks, images
- **OpenSearch**: Face vector similarity search (ANN with k-NN)
- **S3**: Image storage (user images, web images)
- **AWS SageMaker**: ML inference endpoints for face embedding
  - `defenderImageAnalyzerEndpointC5i` (full flow)
  - `defenderImageAnalyzerEndpointC6i2x` (quick flow)
- **Google Serper API**: Web search (images & sites)
- **AWS Secrets Manager**: Credentials (MongoDB URLs, API keys)

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/deploy.yml`):

1. **Security & Quality** (all branches):
   - Pylint (errors/fatal only)
   - Bandit (Python security)
   - Safety (dependency vulnerabilities)
   - Semgrep (SAST)

2. **Unit Tests** (all branches):
   - pytest with coverage
   - Upload to Codecov

3. **Build & Push** (all branches):
   - Multi-stage Docker build
   - Trivy container scanning
   - Push to ECR:
     - `dev` branch → `searcher-dev:latest-dev`
     - `staging` branch → `searcher-stage:latest-staging`
     - `main` branch → `searcher-main:latest`

4. **Deploy**:
   - **Dev**: Auto-deploy on push to `dev`
   - **Staging**: Auto-deploy on push to `staging` 
   - **Production**: Manual approval required for `main`

OIDC authentication (no long-lived AWS credentials):
- ECR push: `arn:aws:iam::722568544242:role/github-actions-ecr-role`
- ECS deploy: `arn:aws:iam::722568544242:role/github-actions-ecs-deploy-role`

## Secrets Management

NEVER commit secrets to git. Use AWS Secrets Manager:

```python
# Secrets are retrieved via DbClient (clients/db.py)
# MongoDB URLs: dev/mongodb, stage/mongodb, production/mongodb
# Serper API key: dme-searcher/serper-api-key (stored in config as IMAGE_DOWNLOADER_API_KEY)
```

For local development, copy `.env.example` to `.env` and populate with dev credentials.

## Important Patterns

### 1. Manual Offset Management

Kafka consumer manually stores offsets (`EVENT_CONSUMER_ENABLE_AUTO_OFFSET_STORE = False`) to ensure at-least-once processing. Only commit after successful message handling:

```python
if self._configs.EVENT_CONSUMER_ENABLE_AUTO_OFFSET_STORE is False:
    self._client.store_offsets(msg)
```

### 2. Face Vector Similarity

Three thresholds control face matching (`config.py`):
- `MAX_SIMILARITY_DISTANCE_DEEPFACE = 0.35` (ML model threshold)
- `MAX_SIMILARITY_DISTANCE_VECTOR_DB = 0.19` (OpenSearch k-NN)
- `MAX_MACTHING_SIMILARITY_DISTANCE = 0.07` (user image deduplication)

### 3. Company Name Filtering

Filter out demo companies via `COMPANY_NAME_FILTER` set in config. Also extract company domains from work emails (non-common providers like gmail.com).

### 4. Duplicate Prevention

`DUPLICATE_PREVENTION` flag controls whether to filter search results against existing user leaks (`UserService.filter_search_results`).

### 5. Temporary File Cleanup

User images are downloaded to temp directory (`scan_dto.user_images_local_dir`). Always purge via `shutil.rmtree()` after processing (controlled by `PURGE_SCRAPPED_DATA = True`).

### 6. Long-Running Consumer

Consumer has extended timeout (`EVENT_CONSUMER_MAX_POLL_INTERVAL_MS = 3600000` = 1 hour) because scans can take minutes to hours, especially full searches on famous people.

## Testing Strategy

- **Unit tests** mock external dependencies (AWS, Kafka, MongoDB, OpenSearch)
- **Integration tests** require real AWS resources (use `--env test`)
- Use `conftest.py` to add project root to PYTHONPATH
- Code coverage tracked for `clients/`, `services/`, `repositories/`

## Security Hardening

Hardened Docker image (`Dockerfile.hardened`):
- Non-root user (UID 10001)
- Read-only root filesystem
- Dropped Linux capabilities (no CAP_ALL)
- Multi-stage build (Alpine base)
- No package managers/shells in final image
- All dependencies pinned

See `DOCKER_HARDENING.md` and `SECURITY.md` for full details.

## Deployment

See `DEPLOYMENT.md` for complete AWS deployment guide including:
- CloudFormation infrastructure setup
- ECR repository creation
- ECS task/service definitions
- GitHub OIDC configuration
- Secrets Manager setup

Infrastructure as Code: `IaC/cloudformation/`
- `iam-roles.yml` - GitHub OIDC + IAM roles
- `ecr-repositories.yml` - ECR repos for dev/stage/prod
- `ecs-infrastructure.yml` - ECS cluster, task definitions, services

## Common Issues

### Issue: Kafka consumer not receiving messages
- Check security group rules allow traffic from Kafka brokers
- Verify consumer group ID is unique per environment
- Check topic name matches environment (`dme-searcher-dev` vs `dme-searcher-prd`)

### Issue: MongoDB connection fails
- Verify secret exists in Secrets Manager: `aws secretsmanager get-secret-value --secret-id dev/mongodb`
- Check network connectivity from ECS tasks to MongoDB (security groups, NACLs)
- Ensure IAM task role has `secretsmanager:GetSecretValue` permission

### Issue: Face embedding fails
- Check SageMaker endpoint is deployed and in service
- Verify IAM task role has `sagemaker:InvokeEndpoint` permission
- Check image format is supported (JPEG, PNG)
- Ensure at least one face is clearly visible in image

### Issue: Docker build fails on M1/M2 Mac
- Use `--platform linux/amd64` flag with docker build
- Or build via GitHub Actions which uses AMD64 runners

### Issue: Tests fail with "No module named 'clients'"
- Ensure `conftest.py` is present in project root
- Run tests from project root directory
- Check `PYTHONPATH` includes project root

## Known Limitations

- Only one face per user image is processed (largest face if multiple detected)
- Company search only uses first name provided (`request.names[0]`)
- Search result pagination capped at 5 pages for full flow (prevents runaway scans)
- Temporary files must be cleaned up manually (no automatic garbage collection)
- Consumer group rebalancing can cause duplicate processing (at-least-once semantics)
