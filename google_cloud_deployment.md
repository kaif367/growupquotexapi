# Google Cloud RDP पर Quotex API Deploy करने की Complete Guide

## 📋 Requirements
- Google Cloud RDP Instance (Windows/Linux)
- Domain Name (optional)
- Python 3.11+

## 🚀 Step 1: RDP पर API Setup

### Windows RDP के लिए:

1. **Python Install करें:**
```powershell
# Python 3.11 download करें
https://www.python.org/downloads/
```

2. **Project Copy करें:**
```powershell
# GitHub से clone करें या zip upload करें
git clone https://github.com/yourusername/pyquotex.git
cd pyquotex
```

3. **Dependencies Install करें:**
```powershell
pip install -r requirements.txt
playwright install chromium
```

4. **API Server को Background Service बनाएं:**

### Linux RDP के लिए:

```bash
# Python और dependencies
sudo apt update
sudo apt install python3.11 python3-pip nginx certbot python3-certbot-nginx

# Project setup
git clone https://github.com/yourusername/pyquotex.git
cd pyquotex
pip3 install -r requirements.txt
playwright install chromium
playwright install-deps
```

## 🌐 Step 2: Domain Setup (Free/Paid Options)

### Option A: Free Domain (DuckDNS)

1. **DuckDNS पर जाएं:** https://www.duckdns.org
2. **Login करें और subdomain create करें:**
   - Example: `yourapi.duckdns.org`
3. **RDP का Public IP add करें**

### Option B: Paid Domain (Namecheap/GoDaddy)

1. **Domain खरीदें**
2. **DNS Settings में जाएं**
3. **A Record add करें:**
   ```
   Type: A
   Host: @ (या api)
   Value: YOUR_RDP_PUBLIC_IP
   TTL: 300
   ```

### Option C: Cloudflare (Free SSL + CDN)

1. **Cloudflare account बनाएं:** https://cloudflare.com
2. **Domain add करें**
3. **DNS Records setup करें:**
   ```
   Type: A
   Name: @ या api
   Content: YOUR_RDP_IP
   Proxy: ON (Orange Cloud)
   ```

## 🔧 Step 3: Nginx Reverse Proxy Setup (Linux)

```bash
# Nginx configuration
sudo nano /etc/nginx/sites-available/quotex-api

# Add this configuration:
```

```nginx
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/quotex-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Step 4: SSL Certificate (HTTPS)

### Free SSL with Let's Encrypt:

```bash
# For Linux
sudo certbot --nginx -d yourdomain.com -d api.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### For Windows RDP:
Use **Win-ACME** या **Certify The Web**

## 📦 Step 5: Service Setup (24/7 Running)

### Linux - Systemd Service:

```bash
sudo nano /etc/systemd/system/quotex-api.service
```

```ini
[Unit]
Description=Quotex API Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/pyquotex
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin"
ExecStart=/usr/bin/python3 /home/ubuntu/pyquotex/api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl daemon-reload
sudo systemctl enable quotex-api
sudo systemctl start quotex-api
sudo systemctl status quotex-api
```

### Windows - Task Scheduler:

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: "When computer starts"
4. Action: Start Program
   - Program: `python.exe`
   - Arguments: `C:\path\to\api_server.py`
   - Start in: `C:\path\to\pyquotex`

## 🔥 Step 6: Firewall Rules

### Google Cloud Console:
1. VPC network → Firewall rules
2. Create rule:
   - Direction: Ingress
   - Targets: All instances
   - Source IP: 0.0.0.0/0
   - Protocols: tcp:80,443,8000

### Windows Firewall:
```powershell
New-NetFirewallRule -DisplayName "Quotex API" -Direction Inbound -Protocol TCP -LocalPort 8000,80,443 -Action Allow
```

### Linux:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

## 📱 Step 7: Testing

```bash
# Local test
curl http://localhost:8000/status

# Domain test
curl https://yourdomain.com/status

# API test
curl -X POST https://yourdomain.com/candles/progressive \
  -H "Content-Type: application/json" \
  -d '{"asset":"EURUSD_otc","period":60,"days":1}'
```

## 🎯 Step 8: Monitoring

### Simple monitoring script:
```bash
#!/bin/bash
# monitor.sh
while true; do
    if ! curl -f http://localhost:8000/status > /dev/null 2>&1; then
        echo "API is down, restarting..."
        systemctl restart quotex-api
    fi
    sleep 60
done
```

## 💡 Pro Tips:

1. **Free Domain Options:**
   - DuckDNS: yourname.duckdns.org
   - No-IP: yourname.ddns.net
   - Freenom: yourname.tk/.ml/.ga

2. **CDN + SSL Free:**
   - Cloudflare (Best option)
   - Provides SSL, DDoS protection, CDN

3. **Backup:**
   - Regular backup of `session.json`
   - Config files backup

4. **Security:**
   - Change default ports
   - Use API keys for authentication
   - Rate limiting

## 🚨 Troubleshooting:

**Port already in use:**
```bash
# Find process
netstat -tulpn | grep 8000
# Kill process
kill -9 PID
```

**Domain not working:**
- Check DNS propagation: https://dnschecker.org
- Wait 24-48 hours for propagation
- Check firewall rules

**SSL not working:**
- Check port 443 is open
- Verify domain DNS points to correct IP
- Check certificate status: `sudo certbot certificates`

## 📞 Support Commands:

```bash
# Check logs
sudo journalctl -u quotex-api -f

# Restart service
sudo systemctl restart quotex-api

# Check nginx
sudo nginx -t
sudo systemctl restart nginx

# Check ports
sudo netstat -tulpn
```

---

## Quick Start for Google Cloud RDP:

```bash
# 1. SSH into your instance
gcloud compute ssh instance-name

# 2. Run setup script
curl -sSL https://raw.githubusercontent.com/yourusername/pyquotex/main/setup.sh | bash

# 3. Configure domain
nano /etc/nginx/sites-available/default
# Add your domain

# 4. Get SSL
certbot --nginx -d yourdomain.com

# Done! API running at https://yourdomain.com
```
