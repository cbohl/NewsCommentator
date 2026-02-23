# Feature Specification: AWS Deployment via Terraform

**Feature Branch**: `004-aws-terraform`
**Created**: 2026-02-23
**Status**: Draft
**Input**: User request: "Terraform this project onto AWS — EC2 for backend, S3 + CloudFront for frontend."

## Constitution Check

No amendment required. The infrastructure is additive — no locked stack components change. SQLite stays on EC2's filesystem, APScheduler stays in-process, all technology choices preserved.

## User Scenarios & Testing

### User Story 1 - Deploy Backend to EC2 (Priority: P1)

The FastAPI backend runs on an EC2 instance with the SQLite database, APScheduler, and all dependencies. The instance is provisioned and configured entirely via Terraform.

**Why this priority**: Nothing works without the backend running.

**Independent Test**: After `terraform apply`, SSH into the instance and verify `curl http://localhost:8000/health` returns a valid response.

**Acceptance Scenarios**:

1. **Given** Terraform has been applied, **When** the EC2 instance finishes booting, **Then** the FastAPI app is running on port 8000 via a systemd service.
2. **Given** the backend is running, **When** calling `POST /trigger` from the instance, **Then** the pipeline processes an article successfully.
3. **Given** the instance reboots, **When** it comes back up, **Then** the FastAPI service starts automatically and the SQLite database persists.

---

### User Story 2 - Deploy Frontend to S3 + CloudFront (Priority: P1)

The built Vite frontend is hosted in an S3 bucket with a CloudFront distribution providing HTTPS and CDN caching.

**Why this priority**: Equal to US1 — users need a URL to access the app.

**Independent Test**: After `terraform apply` and uploading the frontend build, visit the CloudFront URL and see the News Commentator homepage.

**Acceptance Scenarios**:

1. **Given** Terraform has been applied, **When** the frontend is built and uploaded to S3, **Then** the CloudFront distribution serves the app over HTTPS.
2. **Given** the frontend is loaded, **When** the browser fetches `/articles`, **Then** it successfully reaches the EC2 backend API (CORS configured for the CloudFront domain).
3. **Given** a user visits a deep path (e.g., refreshes the page), **When** CloudFront receives the request, **Then** it serves `index.html` (SPA routing fallback).

---

### User Story 3 - Secure Configuration (Priority: P1)

Secrets (OpenAI API key) are not hardcoded in Terraform or committed to git. The EC2 instance's security group restricts access appropriately.

**Why this priority**: Non-negotiable for any deployment.

**Independent Test**: Verify the OpenAI key is not in any Terraform file, and that only necessary ports are open.

**Acceptance Scenarios**:

1. **Given** the infrastructure is deployed, **When** inspecting Terraform files, **Then** the OpenAI API key is sourced from a Terraform variable or AWS SSM Parameter Store, never hardcoded.
2. **Given** the EC2 security group, **When** inspecting its rules, **Then** only port 22 (SSH), port 80, and port 443 are open inbound.
3. **Given** the S3 bucket, **When** attempting direct access, **Then** it is not publicly accessible — only CloudFront can read from it via OAC.

---

### Edge Cases

- What if `terraform apply` is run twice? All resources must be idempotent — no duplicates or errors on re-apply.
- What if the EC2 instance is terminated? Terraform can recreate it, but the SQLite database would be lost. User accepts this risk for MVP (backups are a future concern).
- What if the frontend API URL changes? The frontend build must reference the backend URL via an environment variable, not a hardcoded localhost.

## Requirements

### Functional Requirements

- **FR-001**: Terraform MUST provision an EC2 instance (Amazon Linux 2023 or Ubuntu) with Python 3.11+, pip, and the backend dependencies.
- **FR-002**: Terraform MUST configure a systemd service for the FastAPI app that starts on boot.
- **FR-003**: Terraform MUST provision an S3 bucket with static website hosting disabled (CloudFront serves content).
- **FR-004**: Terraform MUST provision a CloudFront distribution with OAC pointing to the S3 bucket, with a custom error response routing 403/404 to `index.html` for SPA support.
- **FR-005**: The frontend API client MUST read the backend URL from an environment variable at build time (not hardcoded to localhost).
- **FR-006**: Terraform MUST create a security group allowing inbound SSH (22), HTTP (80), and HTTPS (443).
- **FR-007**: The OpenAI API key MUST be passed via Terraform variable and written to the `.env` file on the EC2 instance.
- **FR-008**: Terraform MUST output the CloudFront URL and EC2 public IP after apply.
- **FR-009**: A deploy script or instructions MUST exist for building the frontend with the correct API URL and uploading to S3.

### Key Entities (new)

- **`infra/`** directory at project root containing all Terraform files.
- **`infra/main.tf`** — Provider, EC2, security group, key pair.
- **`infra/s3.tf`** — S3 bucket, bucket policy, CloudFront OAC.
- **`infra/cloudfront.tf`** — CloudFront distribution.
- **`infra/variables.tf`** — Input variables (API key, region, instance type, key pair name).
- **`infra/outputs.tf`** — CloudFront URL, EC2 public IP.
- **`infra/userdata.sh`** — EC2 bootstrap script (install deps, clone/copy code, start service).

## Success Criteria

- **SC-001**: `terraform apply` completes with zero errors from a clean state.
- **SC-002**: The CloudFront URL serves the frontend and displays articles from the EC2 backend.
- **SC-003**: The EC2 backend survives a reboot and auto-starts the FastAPI service.
- **SC-004**: No secrets appear in any committed file.
- **SC-005**: `terraform destroy` cleanly removes all resources.
