# Production Deployment Guide - Open TTS Studio Demo

This guide shows how to deploy a **secure public demo** of Open TTS Studio.

## Architecture

```
┌─────────────────┐
│   Public VPS    │  Frontend (Gradio UI)
│  $5/mo hosting  │  + nginx + rate limiting + SSL
└────────┬────────┘
         │ Tailscale VPN (secure)
         ▼
┌─────────────────┐
│   Moya Server   │  Backend (TTS API)
│  Your hardware  │  + Kokoro/VoxCPM
└─────────────────┘
```

**Why this setup:**
- ✅ **Secure**: Your main servers not exposed publicly
- ✅ **Isolated**: Frontend can't access your local network
- ✅ **Protected**: Rate limiting prevents abuse
- ✅ **Cheap**: Frontend VPS costs ~$5/month

---

## Prerequisites

### On Your VPS (Public)
- Ubuntu 22.04 or similar
- Docker + Docker Compose installed
- Domain pointing to VPS IP
- Port 80, 443 open

### On Moya (Your Server)
- Tailscale installed and running
- TTS API running (Kokoro or VoxCPM backend)
- Port 8765 accessible via Tailscale

---

## Step 1: Setup Backend on Moya

```bash
# SSH to Moya
ssh moya

# Start Kokoro backend
cd /home/brian/projects/open-unified-tts-simple
docker compose -f docker-compose.kokoro.yml up -d

# Start unified TTS API server
uv run python server.py

# Get Moya's Tailscale IP
tailscale ip -4
# Example output: 100.64.1.2
```

**Test it:**
```bash
curl http://100.64.1.2:8765/v1/voices
# Should return list of voices
```

---

## Step 2: Setup VPS (Public Frontend)

### 2.1 Get a VPS
**Recommended cheap options:**
- DigitalOcean: $6/month droplet
- Linode: $5/month "Nanode"
- Vultr: $6/month instance
- Hetzner: €4.51/month CX11

Choose Ubuntu 22.04 image.

### 2.2 Install Tailscale on VPS

```bash
# SSH to VPS
ssh root@YOUR_VPS_IP

# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Authenticate (follow URL)
tailscale up

# Verify you can reach Moya
ping 100.64.1.2  # Replace with Moya's Tailscale IP
curl http://100.64.1.2:8765/v1/voices  # Should work!
```

### 2.3 Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo apt-get update
sudo apt-get install -y docker-compose-plugin

# Verify
docker --version
docker compose version
```

### 2.4 Clone Project

```bash
# Clone your repo
git clone https://github.com/loserbcc/open-tts-studio.git
cd open-tts-studio

# Copy environment file
cp .env.production.example .env

# Edit with your values
nano .env
```

**Edit .env:**
```bash
TTS_API_URL=http://100.64.1.2:8765  # Moya's Tailscale IP
DOMAIN=demo.open-tts-studio.com     # Your domain
LETSENCRYPT_EMAIL=your@email.com    # Your email
```

---

## Step 3: Setup SSL Certificate

### Option A: Let's Encrypt (Automated)

```bash
# Install certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Stop nginx temporarily
docker compose -f docker-compose.production.yml down nginx

# Get certificate
sudo certbot certonly --standalone -d demo.open-tts-studio.com --email your@email.com --agree-tos

# Copy to project
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/demo.open-tts-studio.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/demo.open-tts-studio.com/privkey.pem ssl/key.pem
sudo chown -R $USER:$USER ssl/

# Auto-renewal (every 3 months)
sudo crontab -e
# Add: 0 3 1 * * certbot renew --quiet && cp /etc/letsencrypt/live/demo.open-tts-studio.com/*.pem /path/to/open-tts-studio/ssl/ && docker compose restart nginx
```

### Option B: Self-Signed (Testing Only)

```bash
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem \
  -subj "/CN=demo.open-tts-studio.com"
```

---

## Step 4: Update nginx Config

```bash
# Edit nginx-production.conf
nano nginx-production.conf

# Change line 66 and 80:
server_name _;  →  server_name demo.open-tts-studio.com;
```

---

## Step 5: Launch!

```bash
# Start all services
docker compose -f docker-compose.production.yml up -d

# Watch logs
docker compose -f docker-compose.production.yml logs -f

# Check status
docker compose -f docker-compose.production.yml ps
```

**Visit:** https://demo.open-tts-studio.com

---

## Step 6: Monitor & Secure

### Check Rate Limiting

```bash
# Tail nginx logs
docker compose -f docker-compose.production.yml logs -f nginx

# You should see 429 errors if someone hits rate limits
```

### Monitor Resources

```bash
# CPU/Memory usage
docker stats

# Disk space
df -h
```

### Setup Fail2ban (Optional)

```bash
# Already included in docker-compose.production.yml
# Check banned IPs
docker compose exec fail2ban fail2ban-client status nginx-limit-req
```

---

## Maintenance

### Update to New Version

```bash
cd open-tts-studio
git pull
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml build --no-cache
docker compose -f docker-compose.production.yml up -d
```

### View Logs

```bash
# All services
docker compose -f docker-compose.production.yml logs -f

# Just studio
docker compose -f docker-compose.production.yml logs -f studio

# Just nginx
docker compose -f docker-compose.production.yml logs -f nginx
```

### Restart Services

```bash
# All
docker compose -f docker-compose.production.yml restart

# Just studio
docker compose -f docker-compose.production.yml restart studio
```

---

## Security Checklist

- [x] TTS backend not exposed publicly (Tailscale only)
- [x] Rate limiting enabled (2 generations/minute per IP)
- [x] SSL/TLS enabled with valid certificate
- [x] Security headers configured (HSTS, XSS protection)
- [x] Fail2ban monitoring nginx logs
- [x] Resource limits on containers
- [x] Sensitive files blocked (.env, .git, etc.)
- [ ] Monitor logs for abuse
- [ ] Setup alerting (optional: UptimeRobot, etc.)

---

## Troubleshooting

### Can't reach TTS backend

```bash
# On VPS, test Tailscale connection
ping 100.64.1.2  # Moya's IP

# Test TTS API
curl http://100.64.1.2:8765/v1/voices

# Check Tailscale status
tailscale status
```

### SSL certificate errors

```bash
# Verify certificate files exist
ls -la ssl/

# Check nginx config
docker compose exec nginx nginx -t

# Reload nginx
docker compose restart nginx
```

### High CPU/memory usage

```bash
# Check which container
docker stats

# Reduce resource limits in docker-compose.production.yml
# Lower CPUs or memory under deploy.resources.limits
```

### Getting rate limited yourself

```bash
# Temporary: Disable rate limiting
# Edit nginx-production.conf, comment out limit_req lines
# Restart nginx

# Permanent: Whitelist your IP
# Add to nginx-production.conf:
geo $limit {
    default 1;
    YOUR.IP.ADDRESS.HERE 0;  # No rate limiting
}
map $limit $limit_key {
    0 "";
    1 $binary_remote_addr;
}
limit_req_zone $limit_key zone=general:10m rate=10r/s;
```

---

## Cost Estimate

| Item | Cost | Notes |
|------|------|-------|
| **VPS** | $5-6/month | DigitalOcean, Linode, Vultr |
| **Domain** | $12/year | Optional if using subdomain |
| **SSL** | Free | Let's Encrypt |
| **Tailscale** | Free | Personal use up to 100 devices |
| **Total** | **~$6/month** | Very cheap for public demo! |

---

## Next Steps

Once deployed:
1. ✅ Test from different networks
2. ✅ Monitor for a few days
3. ✅ Share demo link in GitHub README
4. ✅ Add to Show HN post
5. ✅ Collect feedback from real users!

---

**Questions?** Open an issue or email buddy@loser.com
