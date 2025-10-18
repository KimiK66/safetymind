# Render.com Deployment Guide for SafetyMind

## Quick Setup

1. **Go to [render.com](https://render.com)**
2. **Sign up** with your GitHub account
3. **Connect repository**: `KimiK66/safetymind`
4. **Create Web Service**:
   - **Name**: `safetymind`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: `3.11`

## Environment Variables

Add these in Render dashboard → Environment:

```
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
GROQ_API_KEY=your_groq_api_key_here
MEM0_API_KEY=your_mem0_api_key_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
DATABASE_URL=sqlite:///safetymind.db
```

## Alternative: Use render.yaml

The `render.yaml` file is already configured. If you prefer:
1. **Create Web Service** → **Infrastructure as Code**
2. **Select** `render.yaml` from your repository
3. **Deploy**

## Features

✅ **Python-First**: Built for Python apps  
✅ **Auto-Detection**: Detects FastAPI automatically  
✅ **Persistent Storage**: Better for databases  
✅ **Free Tier**: Generous free tier  
✅ **Better Logs**: Clear error messages  
✅ **No Config Conflicts**: No Vercel issues  

## Troubleshooting

- **Build fails**: Check Python version (use 3.11)
- **Port issues**: Ensure `$PORT` environment variable is used
- **Import errors**: Verify all dependencies in `requirements.txt`
- **Database**: SQLite works on free tier

## Next Steps

1. Deploy to Render
2. Test the API endpoints
3. Access web interface at `https://safetymind.onrender.com`
4. Monitor logs in Render dashboard

## Support

- Render docs: https://render.com/docs
- FastAPI docs: https://fastapi.tiangolo.com
- SafetyMind GitHub: https://github.com/KimiK66/safetymind
