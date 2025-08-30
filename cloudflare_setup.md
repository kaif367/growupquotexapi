# 🌐 Domain Setup Guide for Google Cloud RDP

## Quick Setup - 3 Methods

### Method 1: Free Domain + Cloudflare (Recommended) ✅

**Step 1: Free Domain लें**
```
1. Freenom.com पर जाएं
2. Free domain register करें (.tk, .ml, .ga, .cf)
   Example: yourapi.tk
```

**Step 2: Cloudflare Setup**
```
1. cloudflare.com पर account बनाएं (FREE)
2. "Add Site" पर click करें
3. अपना domain add करें (yourapi.tk)
4. Free plan select करें
5. DNS Records add करें:

   Type: A
   Name: @
   Content: YOUR_RDP_PUBLIC_IP
   Proxy: ON (Orange cloud ✓)
   
   Type: A  
   Name: api
   Content: YOUR_RDP_PUBLIC_IP
   Proxy: ON (Orange cloud ✓)
```

**Step 3: Nameservers Update करें**
```
Freenom dashboard में जाएं:
Management Tools > Nameservers > Use custom nameservers

Cloudflare nameservers add करें:
- adam.ns.cloudflare.com
- anna.ns.cloudflare.com
```

### Method 2: DuckDNS (Simplest) 🦆

```bash
# 1. duckdns.org पर जाएं
# 2. Login करें (Google/GitHub)
# 3. Subdomain create करें: yourapi
# 4. आपका domain होगा: yourapi.duckdns.org

# Auto-update script for IP
echo "url=\"https://www.duckdns.org/update?domains=yourapi&token=YOUR_TOKEN&ip=\"" | curl -k -o ~/duckdns.log -K -
```

### Method 3: No-IP (Alternative) 🌍

```
1. noip.com पर account बनाएं
2. Free hostname create करें
3. Dynamic Update Client install करें
4. Domain: yourapi.ddns.net
```

## 🔧 RDP पर Complete Setup Commands

### Windows RDP:
```powershell
# 1. Get your public IP
Invoke-RestMethod ifconfig.me

# 2. Open ports in Windows Firewall
New-NetFirewallRule -DisplayName "API HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "API HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
New-NetFirewallRule -DisplayName "API Direct" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# 3. Run API
cd D:\pyquotex-master
python api_server.py
```

### Linux RDP:
```bash
# 1. Get public IP
curl ifconfig.me

# 2. Quick setup with Nginx
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx -y

# 3. Configure Nginx
sudo nano /etc/nginx/sites-available/default
```

**Nginx Config:**
```nginx
server {
    listen 80;
    server_name yourapi.tk api.yourapi.tk yourapi.duckdns.org;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# 4. Restart Nginx
sudo systemctl restart nginx

# 5. Get FREE SSL
sudo certbot --nginx -d yourapi.tk -d api.yourapi.tk
```

## ⚡ Google Cloud Firewall Rules

**Console में जाएं:**
1. VPC network → Firewall rules
2. CREATE FIREWALL RULE
3. Settings:
   - Name: allow-api
   - Direction: Ingress
   - Targets: All instances in network
   - Source IP ranges: 0.0.0.0/0
   - Protocols and ports: 
     ✓ Specified protocols and ports
     ✓ TCP: 80, 443, 8000

**या Command line से:**
```bash
gcloud compute firewall-rules create allow-api \
    --allow tcp:80,tcp:443,tcp:8000 \
    --source-ranges 0.0.0.0/0
```

## 📱 Testing Your Domain

```bash
# Direct IP test
curl http://YOUR_RDP_IP:8000/status

# Domain test (after DNS propagation)
curl https://yourapi.tk/status

# API test
curl -X POST https://yourapi.tk/candles/progressive \
  -H "Content-Type: application/json" \
  -d '{"asset":"EURUSD_otc","period":60,"days":1}'
```

## 🚀 One-Click Deploy Script

```bash
#!/bin/bash
# save as deploy.sh

echo "Enter your domain (e.g., yourapi.tk):"
read DOMAIN

echo "Enter your RDP public IP:"
read IP

# Update DNS (manual step)
echo "========================================="
echo "Go to Cloudflare/DNS provider and add:"
echo "A Record: @ -> $IP"
echo "A Record: api -> $IP"
echo "Press Enter when done..."
read

# Setup API
cd ~/pyquotex-master
nohup python3 api_server.py > api.log 2>&1 &

# Setup Nginx
sudo tee /etc/nginx/sites-available/api <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN api.$DOMAIN;
    location / {
        proxy_pass http://localhost:8000;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Get SSL
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN -d api.$DOMAIN

echo "✅ Done! Your API is live at https://$DOMAIN"
```

## 💡 Pro Tips:

1. **Cloudflare Benefits (FREE):**
   - Automatic SSL certificate
   - DDoS protection
   - CDN for faster access
   - Hide your real IP

2. **Domain Propagation:**
   - Usually takes 5-30 minutes
   - Check status: https://dnschecker.org

3. **Keep API Running:**
   ```bash
   # Use screen/tmux
   screen -S api
   python3 api_server.py
   # Detach: Ctrl+A then D
   
   # Or use PM2
   npm install -g pm2
   pm2 start api_server.py --interpreter python3
   pm2 save
   pm2 startup
   ```

## ✅ Final Checklist:

- [ ] RDP public IP noted
- [ ] Domain registered (free/paid)
- [ ] DNS records added
- [ ] Firewall ports opened (80,443,8000)
- [ ] API server running
- [ ] Nginx configured
- [ ] SSL certificate installed
- [ ] Domain working: https://yourdomain.com/status

---

**Need help?** Common issues:

1. **"Connection refused"** → Check firewall rules
2. **"502 Bad Gateway"** → API server not running
3. **"DNS not found"** → Wait for propagation
4. **"SSL error"** → Run certbot again
