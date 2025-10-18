#!/bin/bash
# SafetyMind API Keys Setup Script

echo "🔑 SafetyMind API Keys Setup"
echo "============================"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# SafetyMind Environment Configuration
# Add your actual API keys below

# ElevenLabs API Key for voice input/output
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Groq API Key for enhanced AI analysis
GROQ_API_KEY=your_groq_api_key_here

# Mem0 API Key (optional - for memory and learning)
MEM0_API_KEY=your_mem0_api_key_here

# Application Settings
SAFETYMIND_HOST=0.0.0.0
SAFETYMIND_PORT=8000
SAFETYMIND_LOG_LEVEL=INFO

# Voice Settings
VOICE_MODEL_ID=eleven_multilingual_v2
VOICE_SPEED=1.0
VOICE_STABILITY=0.5

# Memory Settings
MEMORY_MAX_CONTEXT_SIZE=10000
MEMORY_LEARNING_RATE=0.1

# Groq Settings
GROQ_MODEL=llama-3.1-70b-versatile
GROQ_MAX_TOKENS=4000
GROQ_TEMPERATURE=0.7
EOF
    echo "✅ .env file created"
else
    echo "📄 .env file already exists"
fi

echo ""
echo "🔧 Next Steps:"
echo "1. Edit the .env file with your actual API keys:"
echo "   nano .env"
echo ""
echo "2. Get your API keys from:"
echo "   - ElevenLabs: https://elevenlabs.io"
echo "   - Groq: https://console.groq.com"
echo "   - Mem0: https://mem0.ai (optional)"
echo ""
echo "3. Restart the application:"
echo "   python3 run.py"
echo ""
echo "4. Test the health endpoint:"
echo "   curl http://localhost:8000/health"
