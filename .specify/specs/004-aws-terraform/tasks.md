# Tasks: AWS Deployment via Terraform

**Input**: `specs/004-aws-terraform/plan.md`

## Phase 1: Frontend API URL Config

- [ ] T001 Update `frontend/src/api/client.ts` — replace hardcoded `localhost:8000` with `import.meta.env.VITE_API_URL || "http://localhost:8000"` fallback

## Phase 2: Terraform Infrastructure

- [ ] T002 Create `infra/variables.tf` — define variables: `aws_region`, `instance_type`, `key_name`, `openai_api_key` (sensitive)
- [ ] T003 [P] Create `infra/main.tf` — AWS provider, EC2 instance (Amazon Linux 2023, t3.micro), security group (22, 80, 443 inbound), user data reference
- [ ] T004 [P] Create `infra/s3.tf` — S3 bucket (private), bucket policy granting CloudFront OAC read access
- [ ] T005 [P] Create `infra/cloudfront.tf` — CloudFront distribution with OAC, S3 origin, custom error response (403 → index.html for SPA), default root object `index.html`
- [ ] T006 Create `infra/outputs.tf` — output `cloudfront_url`, `ec2_public_ip`
- [ ] T007 Create `infra/userdata.sh` — bootstrap script: install Python 3.11 + pip + nginx, create venv, install backend deps, write `.env`, create systemd service, configure nginx reverse proxy, start services

## Phase 3: Deploy Script

- [ ] T008 Create `deploy.sh` — build frontend with `VITE_API_URL`, sync `dist/` to S3, invalidate CloudFront cache

## Phase 4: Gitignore & Docs

- [ ] T009 [P] Update `.gitignore` — add `*.tfstate`, `*.tfstate.backup`, `.terraform/`, `*.tfvars`
- [ ] T010 [P] Add `infra/terraform.tfvars.example` — example variables file with placeholders

## Dependencies

- **Phase 1**: No dependencies
- **Phase 2**: T002 before T003-T005 (variables referenced by other files); T003-T005 in parallel; T006 after T003-T005; T007 after T003
- **Phase 3**: After Phase 2 (needs CloudFront URL and EC2 IP from outputs)
- **Phase 4**: After Phase 2
