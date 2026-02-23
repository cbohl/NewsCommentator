# Implementation Plan: AWS Deployment via Terraform

**Branch**: `004-aws-terraform` | **Date**: 2026-02-23 | **Spec**: `specs/004-aws-terraform/spec.md`

## Summary

Add a Terraform configuration that deploys the FastAPI backend to an EC2 instance and the Vite frontend to S3 + CloudFront. The infrastructure is fully codified and reproducible.

## Technical Context

**Terraform Version**: >= 1.5
**AWS Provider**: >= 5.0
**Region**: User-configurable (default `us-east-1`)
**EC2 Instance Type**: `t3.micro` (free tier eligible)
**AMI**: Amazon Linux 2023

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| IV. Idempotent Processing | PASS | SQLite persists on EC2 EBS volume |
| VI. Jina AI Reader | PASS | EC2 has outbound internet access |
| VII. Simplicity | PASS | Minimal AWS resources, no RDS/ElastiCache |

No amendment required.

## Project Structure (additions)

```text
infra/
├── main.tf              # Provider config, EC2 instance, security group, key pair
├── s3.tf                # S3 bucket, bucket policy
├── cloudfront.tf        # CloudFront distribution, OAC, SPA error routing
├── variables.tf         # Input variables (openai_api_key, region, instance_type, key_name)
├── outputs.tf           # CloudFront URL, EC2 public IP
└── userdata.sh          # EC2 bootstrap: install Python, copy code, create .env, start systemd service

frontend/
└── src/
    └── api/
        └── client.ts    # MODIFIED: read API_BASE from env variable at build time

deploy.sh                # Build frontend with API URL, sync to S3, invalidate CloudFront cache
```

## Design Decisions

### EC2 Bootstrap (userdata.sh)

The user data script will:
1. Install Python 3.11, pip, git
2. Create app directory at `/opt/news-commentator/`
3. Copy backend code and install dependencies in a venv
4. Write `.env` with the OpenAI API key from Terraform variable
5. Create and enable a systemd service (`news-commentator.service`)
6. Start the service on port 8000

### Nginx Reverse Proxy

Install Nginx on the EC2 instance to:
- Proxy port 80 → localhost:8000
- Handle the public-facing HTTP (CloudFront talks to EC2 on port 80)

This avoids running uvicorn as root on port 80.

### Frontend Build-time API URL

Change `client.ts` from hardcoded `http://localhost:8000` to:
```typescript
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

At deploy time, build with:
```bash
VITE_API_URL=http://<ec2-public-ip> npm run build
```

### CloudFront → S3 via OAC

- S3 bucket is NOT publicly accessible
- CloudFront uses Origin Access Control (OAC) to read from S3
- Custom error response: 403 → `/index.html` (200) for SPA routing

### Security

- OpenAI API key passed as `TF_VAR_openai_api_key` environment variable or `-var` flag
- Security group: inbound 22 (SSH), 80 (HTTP from CloudFront), 443 (HTTPS)
- S3 bucket: private, only CloudFront can read

## Complexity Tracking

No constitution violations. Infrastructure is additive only.
