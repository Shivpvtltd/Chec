# JSR AutoPilot - Deployment Guide

Complete deployment instructions for the redesigned YouTube automation system.

## 📁 Repository Structure

```
/mnt/okcomputer/output/
├── JSR_Automation/          # GitHub Actions Repository
│   ├── .github/workflows/
│   │   ├── main.yml         # Main production pipeline
│   │   └── backup.yml       # Backup check workflow
│   ├── src/
│   │   ├── prompts/         # Modular Gemini prompts
│   │   ├── shorts/          # Shorts optimization
│   │   ├── video_generation/# Core video processing
│   │   └── youtube/         # Cloud upload
│   ├── config/
│   │   └── categories.json  # Content categories
│   ├── .env.example
│   └── README.md
│
└── JSR_Auto/                # Render Server Repository
    ├── src/
    │   ├── scheduler/       # 4 cron jobs
    │   ├── routes/          # API routes
    │   └── utils/           # Utilities
    ├── package.json
    ├── .env.example
    └── README.md
```

## 🚀 Deployment Steps

### Step 1: Create GitHub Repository (JSR_Automation)

1. Go to https://github.com/new
2. Name: `JSR_Automation`
3. Make it private
4. Don't initialize with README

```bash
# Navigate to JSR_Automation folder
cd /mnt/okcomputer/output/JSR_Automation

# Initialize git
git init
git add .
git commit -m "Initial commit: Video production pipeline"

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/JSR_Automation.git
git push -u origin main
```

### Step 2: Add GitHub Secrets

Go to: Repository Settings → Secrets and Variables → Actions

Add these secrets:

| Secret | Value | Get From |
|--------|-------|----------|
| `GEMINI_API_KEY` | Your Gemini API key | makersuite.google.com |
| `PEXELS_API_KEY` | Your Pexels API key | pexels.com/api |
| `STABILITY_API_KEY` | Your Stability API key | platform.stability.ai |
| `CLOUDINARY_CLOUD_NAME` | Cloud name | cloudinary.com |
| `CLOUDINARY_API_KEY` | API key | cloudinary.com |
| `CLOUDINARY_API_SECRET` | API secret | cloudinary.com |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Full JSON | Firebase Console |
| `TIER1_WEBHOOK_URL` | `https://jsr-auto.onrender.com/webhooks/github-actions` | After Render deploy |
| `TIER1_HEALTH_URL` | `https://jsr-auto.onrender.com/health` | After Render deploy |

### Step 3: Create GitHub Repository (JSR_Auto)

1. Go to https://github.com/new
2. Name: `JSR_Auto`
3. Make it private

```bash
# Navigate to JSR_Auto folder
cd /mnt/okcomputer/output/JSR_Auto

# Initialize git
git init
git add .
git commit -m "Initial commit: Render server"

# Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/JSR_Auto.git
git push -u origin main
```

### Step 4: Deploy to Render

1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect your `JSR_Auto` GitHub repository
4. Configure:
   - **Name**: `jsr-auto`
   - **Environment**: `Node`
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`
   - **Plan**: Free (or paid for better performance)

5. Add Environment Variables:
   - `PORT`: `3000`
   - `NODE_ENV`: `production`
   - `BASE_URL`: `https://jsr-auto.onrender.com`
   - `SESSION_SECRET`: (Generate random string)
   - `YOUTUBE_CLIENT_ID`: (From Google Cloud)
   - `YOUTUBE_CLIENT_SECRET`: (From Google Cloud)
   - `GITHUB_TOKEN`: (GitHub personal access token)
   - `GITHUB_REPO_OWNER`: (Your GitHub username)
   - `GITHUB_REPO_NAME`: `JSR_Automation`
   - `FIREBASE_SERVICE_ACCOUNT_JSON`: (Full JSON from Firebase)

6. Click "Create Web Service"

### Step 5: Configure YouTube OAuth

1. Go to https://console.cloud.google.com/
2. Create new project or select existing
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Add redirect URI: `https://jsr-auto.onrender.com/auth/youtube/callback`
6. Copy Client ID and Client Secret to Render env vars

### Step 6: Authenticate YouTube

1. Visit: `https://jsr-auto.onrender.com/auth/youtube`
2. Complete Google OAuth flow
3. Tokens are automatically stored in Firestore

### Step 7: Update GitHub Secrets with Webhook URL

After Render deployment:

1. Update `TIER1_WEBHOOK_URL` in GitHub secrets:
   - Value: `https://jsr-auto.onrender.com/webhooks/github-actions`

2. Update `TIER1_HEALTH_URL` in GitHub secrets:
   - Value: `https://jsr-auto.onrender.com/health`

### Step 8: Test the System

#### Test Manual Trigger

```bash
# Trigger main generation manually
curl -X POST https://jsr-auto.onrender.com/webhooks/manual-trigger \
  -H "Content-Type: application/json" \
  -d '{"trigger": "main"}'
```

#### Check Status

```bash
# Check system health
curl https://jsr-auto.onrender.com/health

# Check schedulers
curl https://jsr-auto.onrender.com/status/schedulers
```

## ⏰ Scheduler Timeline (IST)

| Time | Action | Cron |
|------|--------|------|
| 12:05 AM | Main generation trigger | `5 0 * * *` |
| 4:00 AM | Backup check | `0 4 * * *` |
| 5:00 PM | Long videos → PUBLIC | `0 17 * * *` |
| 5:30 PM | Shorts → PUBLIC + links | `30 17 * * *` |

## 🔧 Customization

### Change Scheduler Times

Edit `JSR_Auto/src/server.js`:

```javascript
// Example: Change main trigger to 11:00 PM
cron.schedule('0 23 * * *', async () => {
  // ...
}, {
  scheduled: true,
  timezone: 'Asia/Kolkata'
});
```

### Add New Categories

Edit `JSR_Automation/config/categories.json`:

```json
{
  "categories": [
    {
      "id": "new-category",
      "name": "New Category Name",
      "hindi_name": "हिंदी नाम",
      "sub_categories": [...]
    }
  ]
}
```

## 🐛 Troubleshooting

### GitHub Actions Not Triggering

1. Check `GITHUB_TOKEN` has `repo` scope
2. Verify repository names in env vars
3. Check workflow file syntax

### YouTube Upload Failing

1. Verify OAuth tokens: Visit `/auth/youtube`
2. Check token refresh: `/health`
3. Verify API quotas in Google Cloud Console

### Videos Not Publishing

1. Check Firestore for video records
2. Verify scheduler logs in Render
3. Test manually: `/webhooks/manual-trigger`

### Backup Not Triggering

1. Check workflow status in Firestore
2. Verify backup cron schedule
3. Check if main run completed

## 📊 Monitoring

### Health Check
```bash
curl https://jsr-auto.onrender.com/health
```

### View Recent Videos
```bash
curl https://jsr-auto.onrender.com/status/videos
```

### View Workflow History
```bash
curl https://jsr-auto.onrender.com/status/workflows
```

## 📄 File Summary

### JSR_Automation (GitHub Actions)
- 2 workflow files (main.yml, backup.yml)
- 17 Python scripts
- 1 config file (categories.json)
- 360-minute timeouts on all jobs

### JSR_Auto (Render Server)
- 1 main server file
- 4 scheduler files
- 4 route files
- 5 utility files
- 4 cron jobs

## ✅ Success Criteria Checklist

- [ ] JSR_Automation repository created and pushed
- [ ] JSR_Auto repository created and pushed
- [ ] All GitHub secrets configured
- [ ] Render service deployed
- [ ] YouTube OAuth completed
- [ ] Webhook URLs updated in secrets
- [ ] Manual trigger test passed
- [ ] Health check returns healthy
- [ ] Scheduled for 12:05 AM IST
- [ ] Backup scheduled for 4:00 AM IST
- [ ] Publish long scheduled for 5:00 PM IST
- [ ] Publish shorts scheduled for 5:30 PM IST

---

**Ready for deployment!** 🚀
