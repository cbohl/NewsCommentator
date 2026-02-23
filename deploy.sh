#!/bin/bash
set -euo pipefail

# --- Configuration ---
# These values come from terraform output
EC2_IP=$(cd infra && terraform output -raw ec2_public_ip)
S3_BUCKET=$(cd infra && terraform output -raw s3_bucket_name)
CF_DIST_ID=$(cd infra && terraform output -raw cloudfront_distribution_id)
CF_URL=$(cd infra && terraform output -raw cloudfront_url)
KEY_PATH="${SSH_KEY_PATH:?Set SSH_KEY_PATH to your EC2 key pair .pem file}"

echo "EC2 IP: $EC2_IP"
echo "S3 Bucket: $S3_BUCKET"
echo "CloudFront Distribution: $CF_DIST_ID"
echo "CloudFront URL: $CF_URL"

# --- Deploy Backend ---
echo ""
echo "=== Deploying Backend ==="

# Sync backend code to EC2
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '*.db' --exclude '.env' \
  -e "ssh -i $KEY_PATH -o StrictHostKeyChecking=no" \
  backend/ ec2-user@"$EC2_IP":/opt/news-commentator/backend/

# Update CORS_ORIGINS in .env on EC2
ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no ec2-user@"$EC2_IP" \
  "grep -q CORS_ORIGINS /opt/news-commentator/backend/.env && \
   sed -i 's|^CORS_ORIGINS=.*|CORS_ORIGINS=$CF_URL,http://localhost:5173|' /opt/news-commentator/backend/.env || \
   echo 'CORS_ORIGINS=$CF_URL,http://localhost:5173' >> /opt/news-commentator/backend/.env"

# Install deps and restart service on EC2
ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no ec2-user@"$EC2_IP" << 'REMOTE'
cd /opt/news-commentator/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
REMOTE

# Restart the service (requires sudo)
ssh -i "$KEY_PATH" -o StrictHostKeyChecking=no ec2-user@"$EC2_IP" \
  "sudo systemctl restart news-commentator"

echo "Backend deployed. Testing health..."
sleep 3
curl -s "http://$EC2_IP/health" && echo ""

# --- Deploy Frontend ---
echo ""
echo "=== Deploying Frontend ==="

# Build frontend with CloudFront URL (API routes go through CloudFront too)
cd frontend
VITE_API_URL="$CF_URL" npm run build
cd ..

# Sync to S3
aws s3 sync frontend/dist/ "s3://$S3_BUCKET" --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id "$CF_DIST_ID" \
  --paths "/*" \
  --query 'Invalidation.Id' \
  --output text

echo ""
echo "=== Deploy Complete ==="
echo "Frontend: https://$(cd infra && terraform output -raw cloudfront_url | sed 's|https://||')"
echo "Backend:  http://$EC2_IP"
