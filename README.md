# Smart Car Assistant API

AI-powered backend for a smart car assistant that provides maintenance advice and fuel consumption analysis.

##  Tech Stack
- **Backend:** FastAPI (Python)
- **LLM:** Groq (Llama 3.1 8B for chat, Llama 3.3 70B for analysis)
- **Database:** SQLite (for feedback storage)

##  API Endpoints

### 1. `POST /chat`
Main endpoint for all interactions (chat & evaluation).

**Request Body:**
```json
{
  "prompt": "User message or actual liters (e.g., '20')",
  "history": [
    {"role": "user", "content": "Previous message"},
    {"role": "assistant", "content": "Previous response"}
  ],
  "expected_liters": 17.5  
}

Note: expected_liters is optional. Send it only when evaluating consumption.

Response:

{
  "response": "Bot response text",
  "needs_evaluation_data": false
}
Note: If needs_evaluation_data is true, the frontend should open the Trip Calculator to get the expected liters.

2. GET /feedback
Returns all saved consumption evaluations (JSON format).

How the Evaluation Flow Works:

1.Frontend opens Trip Calculator → User enters car model & distance.
2.Frontend calls Cost API → Gets consumption_per_100km.
3.Frontend calculates: expected_liters = (consumption_per_100km / 100) * distance.
4.Frontend asks user for actual liters pumped.
5.Frontend sends both to POST /chat.
6.Backend analyzes, saves feedback, and returns a smart response.


 Local Setup:
 pip install -r requirements.txt
# Create .env file with GROQ_API_KEY
uvicorn main:app --reload

