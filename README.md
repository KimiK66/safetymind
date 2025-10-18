# SafetyMind: Enhanced AI Near-Miss Reporter

SafetyMind is an advanced AI-powered system for capturing Near-Misses and Incidents in the oil and gas industry, featuring voice input, memory learning, enhanced AI analysis, and comprehensive search and filtering capabilities with industry benchmarking.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys
Create a `.env` file in the project root:
```bash
cp env_template.txt .env
# Edit .env with your API keys
```

Required API keys:
- `ELEVENLABS_API_KEY` - For voice input/output
- `GROQ_API_KEY` - For enhanced AI analysis
- `MEM0_API_KEY` - For memory and learning (optional)

### 3. Run SafetyMind
```bash
python run.py
```

### 4. Access the Application
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Endpoints**: http://localhost:8000/reports

## 🔐 Authentication

- **Reporter**: `reporter:reporter`
- **Reviewer**: `reviewer:reviewer`

## ✨ Enhanced Features

### 🎤 Voice Input Integration
- **Natural Language Processing**: Describe incidents in natural speech
- **Field Extraction**: Automatically extract dates, locations, activities from voice
- **Multi-language Support**: Powered by ElevenLabs multilingual models
- **Voice Feedback**: AI-generated voice responses for confirmation

### 🧠 Memory & Learning System
- **User Preferences**: Learn reporting patterns and common locations
- **Incident Patterns**: Identify recurring issues and seasonal trends
- **Safety Protocols**: Store organization-specific standards
- **Similar Incidents**: Find related past cases for better analysis

### 🎬 Video Generation
- **Removed for Performance**: Video generation components have been removed to optimize application performance and reduce dependencies

### 🚀 Enhanced AI Analysis
- **Groq Integration**: Real-time safety information and best practices
- **Industry Benchmarking**: Compare against oil & gas industry standards
- **Web Search**: Find similar incidents and prevention measures
- **Comprehensive Recommendations**: AI-powered suggestions for prevention

### 📊 Advanced Analytics
- **Interactive Charts**: Visual data representation with Chart.js
- **Memory Insights**: Display learned patterns and trends
- **Industry Comparison**: Real-time benchmarking against industry data
- **Predictive Analysis**: Identify potential risk areas

## 🏗️ Project Structure

```
SafetyMind/
├── run.py                    # Main startup script
├── app.py                    # Alternative startup script
├── requirements.txt           # Python dependencies
├── env_template.txt          # Environment variables template
├── safetymind.db             # SQLite database (created automatically)
├── videos/                   # Generated video storage
├── src/
│   └── safetymind/
│       ├── api.py            # FastAPI application with new endpoints
│       ├── models.py         # Enhanced data models
│       ├── storage.py        # Database operations
│       ├── ai.py             # AI analysis engine
│       ├── benchmark.py      # Industry benchmarking
│       ├── config.py         # Configuration management
│       ├── voice.py          # ElevenLabs voice integration
│       ├── memory.py         # Mem0 memory system
│       ├── groq_analysis.py  # Groq-enhanced AI analysis
│       ├── video_generation.py # Google VEO video generation
│       └── tasks.py          # Background task processing
├── web/
│   └── index.html            # Enhanced web interface
├── data/
│   └── benchmarks/
│       └── oil_gas_benchmark.csv
└── docs/
    └── DNV_MAPPING.md
```

## 🔧 API Endpoints

### Core Endpoints
- `POST /reports` - Create incident report
- `GET /reports` - Search and filter reports
- `GET /reports/{id}` - Get specific report
- `POST /reports/{id}/status` - Update report status
- `POST /reports/{id}/capa` - Add corrective actions

### Voice Input Endpoints
- `POST /reports/voice` - Process voice input and extract fields
- `POST /reports/voice/field` - Process voice for specific field

### Video Generation Endpoints
- **Removed for Performance**: Video generation endpoints have been removed to optimize application performance

### Memory Endpoints
- `GET /memory/similar/{id}` - Get similar incidents
- `GET /memory/patterns` - Get learned patterns
- `GET /memory/protocols` - Get safety protocols
- `POST /memory/protocol` - Add safety protocol

### Groq Analysis Endpoints
- `GET /groq/recommendations/{id}` - Get enhanced recommendations
- `GET /groq/industry-data` - Get real-time industry data

### User Profile Endpoints
- `GET /user/profile` - Get user profile and preferences
- `POST /user/preferences` - Update user preferences

## 🎯 Usage Examples

### Voice Input
1. Click the microphone button in the web interface
2. Describe the incident: "There was a gas leak yesterday at Platform A during maintenance operations"
3. The system will automatically extract:
   - Title: "Gas leak at Platform A"
   - Location: "Platform A"
   - Activity: "Maintenance"
   - Event Type: "Incident"
   - Weather: "Clear" (if mentioned)

### Video Generation
1. Create or select an incident report
2. Click "Generate Video" button
3. The system creates a 4-scene storyboard:
   - Pre-incident conditions
   - Incident sequence
   - Immediate response
   - Prevention measures

### Memory Learning
The system automatically learns from:
- User reporting patterns
- Common incident types
- Recurring equipment failures
- Seasonal safety trends

## 🔑 API Key Setup

### ElevenLabs
1. Sign up at [ElevenLabs](https://elevenlabs.io)
2. Get your API key from the dashboard
3. Add to `.env`: `ELEVENLABS_API_KEY=your_key_here`

### Google API
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable Generative AI API
3. Create API key
4. Add to `.env`: `GOOGLE_API_KEY=your_key_here`

### Groq
1. Sign up at [Groq](https://groq.com)
2. Get your API key
3. Add to `.env`: `GROQ_API_KEY=your_key_here`

### Mem0 (Optional)
1. Sign up at [Mem0](https://mem0.ai)
2. Get your API key
3. Add to `.env`: `MEM0_API_KEY=your_key_here`

## 🚀 Deployment

### Local Development
```bash
python run.py
```

### Production Deployment

#### Using Docker
```bash
# Build image
docker build -t safetymind .

# Run container
docker run -p 8000:8000 --env-file .env safetymind
```

#### Using v0.dev
1. Export your code to v0.dev
2. Configure environment variables
3. Deploy with v0's deployment tools

#### Using Supabase
1. Set up Supabase project
2. Migrate database schema
3. Configure environment variables
4. Deploy FastAPI application

## 🧪 Testing

### Run Integration Tests
```bash
python test_enhanced_safetymind.py
```

### Test Individual Components
```bash
# Test voice integration
python -c "from src.safetymind.voice import parse_voice_input; print(parse_voice_input('Gas leak at Platform A'))"

# Test memory system
python -c "from src.safetymind.memory import get_user_context; print(get_user_context('test_user'))"

# Test video generation
python -c "from src.safetymind.video_generation import create_incident_storyboard; print('Video generation ready')"
```

## 📊 Database Schema

### Enhanced Report Model
- Basic fields: title, description, event_type, location, activity
- Additional fields: witnesses, equipment_involved, weather_conditions
- AI fields: immediate_causes, underlying_causes, ai_analysis
- Media fields: images, video_url, voice_recording_url
- Memory fields: similar_incidents, mem0_context

### New Models
- `UserProfile`: User preferences and reporting patterns
- `SafetyProtocol`: Organization safety standards
- `IncidentPattern`: Learned patterns from historical data

## 🔧 Configuration

### Environment Variables
```bash
# API Keys
ELEVENLABS_API_KEY=your_elevenlabs_key
GOOGLE_API_KEY=your_google_key
GROQ_API_KEY=your_groq_key
MEM0_API_KEY=your_mem0_key

# Voice Settings
VOICE_MODEL_ID=eleven_multilingual_v2
VOICE_SPEED=1.0
VOICE_STABILITY=0.5

# Video Settings
VIDEO_STORAGE_PATH=./videos
MAX_VIDEO_SIZE_MB=100

# Memory Settings
MEMORY_MAX_CONTEXT_SIZE=10000
MEMORY_LEARNING_RATE=0.1

# Groq Settings
GROQ_MODEL=llama-3.1-70b-versatile
GROQ_MAX_TOKENS=4000
GROQ_TEMPERATURE=0.7
```

## 🐛 Troubleshooting

### Common Issues

1. **Voice Input Not Working**
   - Check microphone permissions
   - Verify ElevenLabs API key
   - Ensure audio format is supported

2. **Video Generation Fails**
   - Verify Google API key
   - Check video storage path permissions
   - Ensure sufficient disk space

3. **Memory System Issues**
   - Check Mem0 API key (optional)
   - Verify database connectivity
   - Check memory storage permissions

4. **Groq Analysis Errors**
   - Verify Groq API key
   - Check internet connectivity
   - Ensure API rate limits not exceeded

### Debug Mode
```bash
export SAFETYMIND_LOG_LEVEL=DEBUG
python run.py
```

## 📈 Performance

### Background Tasks
- Video generation runs asynchronously
- Memory updates processed in background
- Task queue manages resource-intensive operations
- Automatic cleanup of old tasks

### Optimization
- Caching for frequently accessed data
- Lazy loading of heavy components
- Efficient database queries
- Compressed video storage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- ElevenLabs for voice synthesis
- Google for VEO video generation
- Groq for enhanced AI analysis
- Mem0 for memory management
- FastAPI for the web framework
- Chart.js for data visualization

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API documentation at `/docs`

---

**SafetyMind** - Making workplace safety smarter with AI 🛡️