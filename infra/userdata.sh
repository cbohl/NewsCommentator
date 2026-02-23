#!/bin/bash
set -euo pipefail

APP_DIR="/opt/news-commentator"

# --- Install system dependencies ---
dnf update -y
dnf install -y python3.11 python3.11-pip nginx git rsync

# --- Create app directory ---
mkdir -p "$APP_DIR/backend"

# --- Clone or copy backend code ---
# For now, we use a placeholder. In production, pull from git or S3.
# The deploy.sh script will scp the backend code to this directory.
cat > "$APP_DIR/backend/.env" <<'ENVEOF'
OPENAI_API_KEY=${openai_api_key}
ENVEOF

# --- Create virtualenv and install deps ---
# (deps installed after code is deployed via deploy.sh)

# --- Systemd service ---
cat > /etc/systemd/system/news-commentator.service <<'SERVICEEOF'
[Unit]
Description=News Commentator FastAPI Backend
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/news-commentator/backend
Environment=PATH=/opt/news-commentator/backend/venv/bin:/usr/bin:/bin
ExecStart=/opt/news-commentator/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
systemctl enable news-commentator.service

# --- Nginx reverse proxy ---
cat > /etc/nginx/conf.d/news-commentator.conf <<'NGINXEOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
NGINXEOF

# Remove default nginx config if it exists
rm -f /etc/nginx/conf.d/default.conf

systemctl enable nginx
systemctl start nginx

# --- Set permissions ---
chown -R ec2-user:ec2-user "$APP_DIR"

echo "Userdata complete. Deploy backend code and restart news-commentator service."
