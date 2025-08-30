#!/bin/bash
# Automated setup script for Linux RDP/VPS

echo "========================================="
echo "Quotex API Setup for Linux VPS/RDP"
echo "========================================="

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
echo "Installing Python 3.11..."
sudo apt install -y python3.11 python3-pip python3.11-venv

# Install Nginx
echo "Installing Nginx..."
sudo apt install -y nginx

# Install project
echo "Setting up project..."
cd /home/$USER
git clone https://github.com/yourusername/pyquotex.git || echo "Project already exists"
cd pyquotex

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install Playwright
echo "Installing Playwright..."
playwright install chromium
playwright install-deps

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/quotex-api.service > /dev/null <<EOF
[Unit]
Description=Quotex API Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER/pyquotex
Environment="PATH=/home/$USER/pyquotex/venv/bin:/usr/bin"
ExecStart=/home/$USER/pyquotex/venv/bin/python /home/$USER/pyquotex/api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Setup Nginx
echo "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/quotex-api > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/quotex-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

# Setup firewall
echo "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
echo "y" | sudo ufw enable

# Start services
echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable quotex-api
sudo systemctl start quotex-api

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)

echo "========================================="
echo "✅ Setup Complete!"
echo "========================================="
echo ""
echo "API Status: sudo systemctl status quotex-api"
echo "API Logs: sudo journalctl -u quotex-api -f"
echo ""
echo "Your API is available at:"
echo "  http://$PUBLIC_IP"
echo "  http://$PUBLIC_IP:8000 (direct)"
echo ""
echo "To setup domain:"
echo "  1. Point your domain A record to: $PUBLIC_IP"
echo "  2. Run: sudo certbot --nginx -d yourdomain.com"
echo ""
echo "========================================="
