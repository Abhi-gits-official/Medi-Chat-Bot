# Medical Assistance Chatbot

A full-stack, real-time medical assistance chatbot application that provides general medical information, first aid guidance, and supportive care through an AI-powered interface.

## ⚠️ Important Disclaimer

**This chatbot provides general medical information and is not a substitute for professional medical advice, diagnosis, or treatment. In case of a medical emergency, please call your local emergency services immediately.**

## Features

### Frontend (React.js + Tailwind CSS)
- **Modern Chat Interface**: Clean, professional, and fully responsive design
- **Real-time Messaging**: Instant communication with the AI assistant
- **Conversation History**: Maintains chat context during the session
- **Loading Indicators**: Visual feedback during response generation
- **Mobile-Friendly**: Optimized for all device sizes
- **Medical Disclaimer**: Prominent safety notice always visible

### Backend (FastAPI + Python)
- **RESTful API**: Single `/chat` endpoint for seamless communication
- **AI Integration**: Powered by Google Gemini Pro model
- **Session Management**: In-memory conversation history storage
- **Error Handling**: Robust error handling with graceful degradation
- **CORS Support**: Properly configured for frontend communication
- **Security**: Environment-based API key management

### AI Capabilities (Google Gemini)
- **First Aid Guidance**: Step-by-step instructions and precautions
- **Symptom Information**: General information about common conditions
- **Instant Relief**: Suggestions for immediate symptom relief
- **Contextual Responses**: Maintains conversation context
- **Safety Guardrails**: Never provides diagnoses or prescriptions
- **Emergency Detection**: Recognizes and responds to medical emergencies

## Technology Stack

### Frontend
- React.js 18 with TypeScript
- Tailwind CSS for styling
- Vite for development and building
- Modern ES6+ features and hooks

### Backend
- FastAPI (Python web framework)
- Google Generative AI (Gemini Pro)
- Uvicorn ASGI server
- Pydantic for data validation
- Python-dotenv for environment management

## Project Structure

```
medical-chatbot/
├── frontend/                 # React.js application
│   ├── src/
│   │   ├── MedicalChatbot.tsx # Main chat component
│   │   ├── App.tsx           # Application root
│   │   ├── index.css         # Tailwind CSS imports
│   │   └── main.tsx          # Application entry point
│   ├── package.json          # Frontend dependencies
│   └── tailwind.config.js    # Tailwind configuration
├── backend/                  # FastAPI server
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables template
├── .github/
│   └── copilot-instructions.md # Development guidelines
└── README.md                # This file
```

## Installation & Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Google Gemini API key

### 1. Clone and Setup
```bash
git clone <repository-url>
cd medical-chatbot
```

### 2. Backend Setup
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1  # PowerShell
# venv\Scripts\activate.bat  # Command Prompt

# Install dependencies
pip install -r requirements.txt

# Create environment file
Copy-Item .env.example .env  # PowerShell
# copy .env.example .env  # Command Prompt

# Edit .env and add your Google Gemini API key
# GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Frontend Setup
```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### 4. Get Google Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key" 
4. Copy the generated API key
5. Open `backend\.env` in a text editor
6. Replace `your_gemini_api_key_here` with your actual API key:
   ```
   GEMINI_API_KEY=AIzaSyYourActualAPIKeyHere
   ```
6. Save the file

**Important**: Keep your API key secure and never commit it to version control.

## Running the Application

### Quick Start (Recommended)
Use the provided startup scripts to run both servers:

**Windows PowerShell:**
```powershell
.\start-dev.ps1
```

**Windows Command Prompt:**
```cmd
start-dev.bat
```

### Manual Start

#### Start Backend Server
```powershell
cd backend
python main.py
# Server will run on http://localhost:8000
```

#### Start Frontend Development Server
```powershell
cd frontend
npm run dev
# Application will be available at http://localhost:5173 or http://localhost:5174
```

### Access the Application
- **Main Application**: http://localhost:5173 or http://localhost:5174
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (FastAPI auto-generated docs)

## API Endpoints

### POST /chat
Main chat endpoint for medical assistance.

**Request Body:**
```json
{
  "message": "I have a headache, what should I do?",
  "conversation_history": [],
  "session_id": "optional_session_id"
}
```

**Response:**
```json
{
  "response": "For a headache, you can try these immediate relief steps..."
}
```

### GET /health
Health check endpoint for monitoring server status.

## Safety Features

### Built-in Safety Guardrails
- **No Diagnoses**: Never provides specific medical diagnoses
- **No Prescriptions**: Never recommends specific medications
- **Emergency Detection**: Recognizes emergency situations and advises calling 911
- **Limitation Awareness**: Clearly states when queries are outside scope
- **Professional Referral**: Encourages consulting healthcare providers when appropriate

### Emergency Response
The AI is programmed to immediately recommend emergency services for:
- Chest pain or difficulty breathing
- Severe bleeding or trauma
- Loss of consciousness
- Signs of stroke or heart attack
- Suicidal thoughts or mental health crises
- Severe allergic reactions

## Development

### Frontend Development
- Uses Vite for fast development and hot reloading
- Tailwind CSS for responsive, utility-first styling
- TypeScript for type safety and better development experience
- Modern React patterns with hooks and functional components

### Backend Development
- FastAPI provides automatic API documentation at `/docs`
- Pydantic models ensure data validation
- Comprehensive error handling and logging
- In-memory session storage for conversation context

### Code Quality
- TypeScript for frontend type safety
- Python type hints for backend
- Comprehensive error handling
- Responsive design principles
- Accessibility considerations

## Deployment Considerations

### Environment Variables
- `GEMINI_API_KEY`: Required for AI functionality
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

### Security Notes
- API keys should be stored securely in environment variables
- CORS is configured for development; adjust for production
- Consider rate limiting for production deployments
- Implement proper logging and monitoring

## Contributing

When contributing to this project, please:
1. Follow the existing code style and patterns
2. Ensure all safety guardrails remain in place
3. Test thoroughly with various medical scenarios
4. Update documentation for any new features
5. Prioritize user safety in all medical responses

## Troubleshooting

### Common Issues

**Frontend not loading or showing errors:**
- Ensure both frontend and backend servers are running
- Check that the backend is accessible at http://localhost:8000
- Try refreshing the browser or clearing cache

**Backend API errors:**
- Verify your `GEMINI_API_KEY` is correctly set in `backend\.env`
- Check that all Python dependencies are installed: `pip install -r requirements.txt`
- Ensure Python version is 3.8 or higher

**CORS errors:**
- The backend is configured for common development ports (5173, 5174)
- If using a different port, update the CORS origins in `backend\main.py`

**Port conflicts:**
- Frontend: Vite will automatically try different ports if 5173 is busy
- Backend: Change the port in `main.py` if 8000 is occupied

### Getting Help

If you encounter issues:
1. Check the console output of both servers for error messages
2. Verify all installation steps were completed
3. Ensure your Google Gemini API key is valid and has proper permissions
4. Check the FastAPI documentation at http://localhost:8000/docs when the backend is running

## License

This project is created for educational and demonstration purposes. Please ensure compliance with healthcare regulations and obtain proper licenses before deploying in production environments.

## Support

For technical issues or questions about the implementation, please refer to:
- FastAPI documentation: https://fastapi.tiangolo.com/
- React documentation: https://react.dev/
- Google Gemini API: https://ai.google.dev/
- Tailwind CSS: https://tailwindcss.com/
