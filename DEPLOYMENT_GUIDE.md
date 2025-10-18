# 🚀 SafetyMind Deployment Guide: GitHub + Vercel + Supabase

## 📋 **Prerequisites**

- GitHub account
- Vercel account (free)
- Supabase account (free)
- Your API keys (ElevenLabs, Groq, Mem0)

## 🔧 **Step 1: Prepare Repository**

### Files Created:
- ✅ `.gitignore` - Excludes sensitive files
- ✅ `vercel.json` - Vercel configuration
- ✅ `app.py` - Vercel entry point
- ✅ `requirements.txt` - Updated with PostgreSQL support
- ✅ `supabase_schema.sql` - Database schema

## 🐙 **Step 2: Push to GitHub**

### Initialize Git Repository:
```bash
cd /Users/kim/SafetyMind
git init
git add .
git commit -m "Initial commit: SafetyMind AI-powered incident reporting system"
```

### Create GitHub Repository:
1. Go to [GitHub](https://github.com)
2. Click "New repository"
3. Repository name: `safetymind`
4. Description: "AI-Powered Near-Miss and Incident Reporting System for Oil & Gas Industry"
5. Make it **Public** (for free Vercel deployment)
6. Don't initialize with README (you already have files)

### Push to GitHub:
```bash
git remote add origin https://github.com/YOUR_USERNAME/safetymind.git
git branch -M main
git push -u origin main
```

## 🗄️ **Step 3: Set Up Supabase**

### Create Supabase Project:
1. Go to [Supabase](https://supabase.com)
2. Click "New Project"
3. Choose your organization
4. Project name: `safetymind`
5. Database password: Generate a strong password (save it!)
6. Region: Choose closest to your users
7. Click "Create new project"

### Get Connection Details:
1. Go to **Settings** → **Database**
2. Copy the **Connection string** (URI)
3. Go to **Settings** → **API**
4. Copy:
   - **Project URL**
   - **anon public** key
   - **service_role** key

### Set Up Database Schema:
1. Go to **SQL Editor** in Supabase dashboard
2. Copy the contents of `supabase_schema.sql`
3. Paste and run the SQL script
4. Verify tables are created in **Table Editor**

## ⚡ **Step 4: Deploy to Vercel**

### Connect Repository:
1. Go to [Vercel](https://vercel.com)
2. Sign in with GitHub
3. Click "New Project"
4. Import your `safetymind` repository
5. Click "Import"

### Configure Build Settings:
- **Framework Preset**: Other
- **Root Directory**: `./` (default)
- **Build Command**: Leave empty
- **Output Directory**: Leave empty
- **Install Command**: `pip install -r requirements.txt`

### Set Environment Variables:
In Vercel dashboard, go to **Settings** → **Environment Variables** and add:

```bash
# Database
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

# Supabase
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_ANON_KEY=[YOUR_ANON_KEY]
SUPABASE_SERVICE_ROLE_KEY=[YOUR_SERVICE_ROLE_KEY]

# API Keys
ELEVENLABS_API_KEY=[YOUR_ELEVENLABS_KEY]
GROQ_API_KEY=[YOUR_GROQ_KEY]
MEM0_API_KEY=[YOUR_MEM0_KEY]

# App Settings
SAFETYMIND_HOST=0.0.0.0
SAFETYMIND_PORT=8000
SAFETYMIND_LOG_LEVEL=INFO
```

### Deploy:
1. Click "Deploy"
2. Wait for build to complete (2-3 minutes)
3. Test your deployed app

## 🧪 **Step 5: Test Deployment**

### Check Health Endpoint:
```bash
curl https://your-app.vercel.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T...",
  "version": "1.0.0",
  "database": "connected",
  "services": {
    "elevenlabs": "configured",
    "groq": "configured",
    "mem0": "configured"
  }
}
```

### Test API Endpoints:
- **Web Interface**: `https://your-app.vercel.app/`
- **API Docs**: `https://your-app.vercel.app/docs`
- **Reports**: `https://your-app.vercel.app/reports`
- **Analytics**: `https://your-app.vercel.app/analytics/summary`

## 🔄 **Step 6: Data Migration (Optional)**

If you want to migrate your existing SQLite data:

### Export Local Data:
```python
# Create migration script
import sqlite3
import json
import requests

# Export from SQLite
conn = sqlite3.connect('safetymind.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM reports")
rows = cursor.fetchall()

# Convert to JSON
data = []
for row in rows:
    data.append({
        'title': row[1],
        'description': row[2],
        'event_type': row[3],
        'consequence': row[4],
        'severity': row[5],
        'location': row[6],
        'activity': row[7],
        'status': row[8],
        'occurred_at': row[9],
        'reported_by': row[10],
        'risk_level': row[25]
    })

# Save to file
with open('migration_data.json', 'w') as f:
    json.dump(data, f)
```

### Import to Supabase:
```python
# Import to Supabase
import requests
import json

# Load data
with open('migration_data.json', 'r') as f:
    data = json.load(f)

# Insert into Supabase
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"

for record in data:
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/reports",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        },
        json=record
    )
    print(f"Status: {response.status_code}")
```

## 🎯 **Step 7: Custom Domain (Optional)**

### Add Custom Domain:
1. Go to Vercel dashboard
2. Click on your project
3. Go to **Settings** → **Domains**
4. Add your custom domain
5. Update DNS records as instructed

## 📊 **Step 8: Monitoring & Analytics**

### Vercel Analytics:
- Built-in analytics in Vercel dashboard
- Performance metrics
- Usage statistics

### Supabase Analytics:
- Database performance
- API usage
- Storage usage

## 🔧 **Troubleshooting**

### Common Issues:

1. **Build fails on Vercel**
   - Check Python version in `vercel.json`
   - Ensure all dependencies are in `requirements.txt`
   - Check build logs in Vercel dashboard

2. **Database connection fails**
   - Verify DATABASE_URL format
   - Check Supabase credentials
   - Ensure database is running

3. **API keys not working**
   - Verify environment variables in Vercel
   - Check key format and permissions
   - Test keys locally first

4. **CORS issues**
   - Update CORS_ORIGINS in config
   - Add your domain to allowed origins

### Debug Commands:
```bash
# Check Vercel logs
vercel logs

# Test locally with production env
vercel dev

# Check Supabase connection
psql "postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres"
```

## 🎉 **Success!**

Your SafetyMind application is now deployed and accessible worldwide!

### **Access URLs:**
- **Production App**: `https://your-app.vercel.app`
- **API Documentation**: `https://your-app.vercel.app/docs`
- **Health Check**: `https://your-app.vercel.app/health`

### **Next Steps:**
1. Share the app with your team
2. Set up monitoring and alerts
3. Configure custom domain
4. Plan for scaling as usage grows

## 💰 **Cost Estimate**

### **Free Tier Limits:**
- **Vercel**: 100GB bandwidth/month
- **Supabase**: 500MB database, 1GB bandwidth/month
- **Total**: $0/month for small teams

### **Paid Plans:**
- **Vercel Pro**: $20/month
- **Supabase Pro**: $25/month
- **Total**: ~$45/month for production use

Your SafetyMind application is now production-ready! 🚀
