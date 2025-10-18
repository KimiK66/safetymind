# 🔑 SafetyMind API Keys Setup Guide

## **Quick Setup**

```bash
# Run the setup script
./setup_api_keys.sh

# Edit the .env file with your keys
nano .env

# Restart the application
python3 run.py
```

## **1. ElevenLabs API Key (Voice Processing)**

### **What it's used for:**
- Voice input (speech-to-text)
- Voice output (text-to-speech)
- Natural language processing

### **How to get it:**

1. **Sign up at ElevenLabs**
   - Go to [https://elevenlabs.io](https://elevenlabs.io)
   - Click "Sign Up" (free tier available)
   - Verify your email

2. **Get your API Key**
   - Log in to your account
   - Click on your profile icon (top right)
   - Select "Profile" from dropdown
   - Scroll down to "API Key" section
   - Click "Copy" to copy your API key

3. **Free Tier Limits:**
   - 10,000 characters per month
   - 3 custom voices
   - Standard voice models

### **Configure:**
```bash
# In your .env file
ELEVENLABS_API_KEY=sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## **2. Groq API Key (Enhanced AI Analysis)**

### **What it's used for:**
- Enhanced AI analysis
- Real-time safety information
- Industry best practices
- Improved recommendations

### **How to get it:**

1. **Sign up at Groq**
   - Go to [https://console.groq.com](https://console.groq.com)
   - Click "Sign Up" (free tier available)
   - Verify your email

2. **Get your API Key**
   - Log in to the console
   - Click "API Keys" in the left sidebar
   - Click "Create API Key"
   - Give it a name (e.g., "SafetyMind")
   - Click "Submit"
   - Copy the generated key

3. **Free Tier Limits:**
   - 14,400 requests per day
   - Fast inference speeds
   - Multiple model access

### **Configure:**
```bash
# In your .env file
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## **3. Mem0 API Key (Memory & Learning) - Optional**

### **What it's used for:**
- Learning user preferences
- Incident pattern recognition
- Safety protocol storage
- Similar incident matching

### **How to get it:**

1. **Sign up at Mem0**
   - Go to [https://mem0.ai](https://mem0.ai)
   - Click "Get Started" or "Sign Up"
   - Create an account

2. **Get your API Key**
   - Log in to your dashboard
   - Navigate to "API Keys" or "Settings"
   - Generate a new API key
   - Copy the key

3. **Free Tier Limits:**
   - Basic memory features
   - Limited storage
   - Standard models

### **Configure:**
```bash
# In your .env file
MEM0_API_KEY=m0_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## **🔧 Configuration Methods**

### **Method 1: Environment File (.env) - Recommended**

```bash
# Edit the .env file
nano .env

# Add your keys:
ELEVENLABS_API_KEY=sk_your_actual_key_here
GROQ_API_KEY=gsk_your_actual_key_here
MEM0_API_KEY=m0_your_actual_key_here
```

### **Method 2: Export Environment Variables**

```bash
# For current session
export ELEVENLABS_API_KEY="sk_your_actual_key_here"
export GROQ_API_KEY="gsk_your_actual_key_here"
export MEM0_API_KEY="m0_your_actual_key_here"

# Start the application
python3 run.py
```

### **Method 3: Docker Environment**

```bash
# Create .env.production file
cp env.production.template .env.production

# Edit with your keys
nano .env.production

# Deploy with Docker
./deploy.sh deploy
```

---

## **🧪 Testing Your Configuration**

### **1. Check Health Endpoint**
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T09:16:12.372377",
  "version": "1.0.0",
  "database": "connected",
  "services": {
    "elevenlabs": "configured",
    "groq": "configured",
    "mem0": "configured"
  }
}
```

### **2. Test Voice Input**
1. Go to http://localhost:8000
2. Click the microphone button
3. Record a voice message
4. Check if transcription works

### **3. Test AI Analysis**
1. Create a new incident report
2. Check if AI analysis is generated
3. Verify recommendations are provided

---

## **🚨 Troubleshooting**

### **Common Issues:**

1. **"API key not found"**
   ```bash
   # Check if .env file exists
   ls -la .env
   
   # Check if keys are set
   grep -E "(ELEVENLABS|GROQ|MEM0)" .env
   ```

2. **"Invalid API key"**
   - Verify you copied the key correctly
   - Check for extra spaces or characters
   - Ensure the key is active in your account

3. **"Rate limit exceeded"**
   - Check your API usage in the provider dashboard
   - Consider upgrading to a paid plan
   - Implement rate limiting in your application

4. **"Service not available"**
   - Check if the service is down
   - Verify your internet connection
   - Check API key permissions

### **Debug Mode:**
```bash
# Enable debug logging
export SAFETYMIND_LOG_LEVEL=DEBUG
python3 run.py
```

---

## **💰 Cost Considerations**

### **Free Tier Limits:**

| Service | Free Tier | Paid Plans |
|---------|-----------|------------|
| **ElevenLabs** | 10K chars/month | $5/month for 30K chars |
| **Groq** | 14.4K requests/day | Pay-per-use |
| **Mem0** | Basic features | $20/month for pro |

### **Estimated Monthly Usage:**
- **Small team (10 users)**: ~$10-20/month
- **Medium team (50 users)**: ~$50-100/month
- **Large organization (200+ users)**: ~$200-500/month

---

## **🔒 Security Best Practices**

1. **Never commit API keys to version control**
2. **Use environment variables**
3. **Rotate keys regularly**
4. **Monitor usage and costs**
5. **Use least-privilege access**

---

## **📞 Support**

If you need help:

1. **Check the logs**: `docker logs safetymind-app`
2. **Test individual services**: Use the health endpoint
3. **Verify configuration**: Check your .env file
4. **Contact support**: Each service has support channels

---

## **✅ Quick Checklist**

- [ ] ElevenLabs account created
- [ ] ElevenLabs API key obtained
- [ ] Groq account created
- [ ] Groq API key obtained
- [ ] Mem0 account created (optional)
- [ ] Mem0 API key obtained (optional)
- [ ] .env file configured
- [ ] Application restarted
- [ ] Health endpoint tested
- [ ] Voice input tested
- [ ] AI analysis tested

**Your SafetyMind application is now fully configured! 🎉**
