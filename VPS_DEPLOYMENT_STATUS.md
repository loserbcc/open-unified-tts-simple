# VPS Deployment Status - Open TTS Studio Demo

**Date**: 2025-12-08
**VPS IP**: 159.203.79.182
**VPS Provider**: DigitalOcean ($6/month)

## ✅ Completed Setup

### 1. GitHub Repository
- **Renamed**: `loserbcc/open-tts-studio` (was `open-unified-tts-simple`)
- **v0.0.1 Tagged**: Alpha release with full docs

### 2. VPS Provisioning
- **Droplet Created**: open-tts-studio-demo
- **Size**: 1GB RAM, 1 vCPU, 25GB SSD
- **Region**: NYC3
- **OS**: Ubuntu 22.04

### 3. Automated Installation Complete
```bash
✅ System packages updated
✅ Tailscale installed
✅ Docker + Docker Compose installed
✅ Project cloned from GitHub
✅ .env configuration created
```

### 4. Configuration Files
- **Project Directory**: `/root/open-tts-studio/`
- **Git Remote**: Updated to new repo name
- **Environment Variables**:
  ```bash
  TTS_API_URL=http://100.94.124.64:8765  # Moya's Tailscale IP
  DOMAIN=159.203.79.182
  LETSENCRYPT_EMAIL=brian@loser.com
  ```

## ⏳ Pending: Tailscale Authentication

**Auth URL**: https://login.tailscale.com/a/1b3d6db501389a

Once authenticated, the VPS will:
- Join your Tailscale network
- Access Moya's TTS backend securely via Tailscale IP

## 🚀 Next Steps (After Tailscale Auth Completes)

### 1. Verify Connectivity
```bash
ssh root@159.203.79.182
ping 100.94.124.64  # Moya's Tailscale IP
curl http://100.94.124.64:8765/v1/voices  # Test TTS API
```

### 2. Build Docker Images
```bash
cd ~/open-tts-studio
docker compose -f docker-compose.production.yml build
```

### 3. Launch Demo
```bash
docker compose -f docker-compose.production.yml up -d
```

### 4. Verify Services
```bash
docker compose -f docker-compose.production.yml ps
docker compose -f docker-compose.production.yml logs -f
```

### 5. Test Public Access
Visit: `http://159.203.79.182`

## 📊 Architecture

```
┌─────────────────┐
│   Public VPS    │  159.203.79.182
│  nginx + Studio │  (Gradio UI)
└────────┬────────┘
         │ Tailscale VPN (100.x.x.x network)
         ▼
┌─────────────────┐
│   Moya Server   │  100.94.124.64:8765
│  TTS Backend    │  (Kokoro/VoxCPM)
└─────────────────┘
```

## 🔐 Security Features

- ✅ Rate limiting: 2 generations/minute per IP
- ✅ Connection limits: 10 concurrent per IP
- ✅ Backend isolated via Tailscale (not publicly exposed)
- ✅ Fail2ban monitoring
- ✅ Security headers (HSTS, XSS protection, etc.)
- ⏳ SSL/TLS (to be configured with Let's Encrypt)

## 📝 Quick Commands

```bash
# SSH to VPS
ssh root@159.203.79.182

# View deployment logs
ssh root@159.203.79.182 'cd ~/open-tts-studio && docker compose -f docker-compose.production.yml logs -f'

# Restart services
ssh root@159.203.79.182 'cd ~/open-tts-studio && docker compose -f docker-compose.production.yml restart'

# Check Tailscale status
ssh root@159.203.79.182 'tailscale status'
```

## 💰 Cost Breakdown

| Item | Cost | Notes |
|------|------|-------|
| VPS | $6/month | DigitalOcean s-1vcpu-1gb |
| Domain | $0 (using IP) | Could add for $12/year |
| SSL | Free | Let's Encrypt |
| Tailscale | Free | Personal plan |
| **Total** | **$6/month** | 🎉 Very affordable! |

## 🎯 Current Status

**WAITING**: Tailscale authentication in browser
**THEN**: Launch containers and test demo
**FINALLY**: Share demo URL!
