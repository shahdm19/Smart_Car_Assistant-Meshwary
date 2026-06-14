from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List, Optional
import re

from fastapi.responses import JSONResponse
from config import config
from logger import get_logger
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from models import get_db, UserFeedback
from consumption_evaluator import ConsumptionEvaluator

logger = get_logger(__name__)
app = FastAPI(title="Smart Car Assistant API", version="6.0.0")


class HistoryMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    prompt: str
    history: List[HistoryMessage] = []
    expected_liters: Optional[float] = None

class ChatResponse(BaseModel):
    response: str
    needs_evaluation_data: bool = False


def get_llm(model_name: str = None):
    selected_model = model_name if model_name else config.MODEL_NAME
    return ChatGroq(
        model=selected_model,
        groq_api_key=config.GROQ_API_KEY,
        temperature=config.TEMPERATURE,
    )

def extract_number_from_text(text: str) -> Optional[float]:
    if text is None:
        return None
    text = str(text).strip()
    match = re.search(r'\d+\.?\d*', text)
    if match:
        return float(match.group())
    return None

def is_evaluation_intent(text: str) -> bool:
    keywords = [
        "evaluate", "consumption", "استهلاك", "قيم", "تقييم", 
        "بنزين", "لتر", "fuel", "efficiency", "actual"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db=Depends(get_db)):
    logger.info(f"Received prompt: {request.prompt[:50]}")
    
    if request.expected_liters is not None:
        actual_liters = extract_number_from_text(request.prompt)
        
        if actual_liters is None or actual_liters <= 0:
            return ChatResponse(
                response=" Please enter your **actual consumption in liters** (e.g., 20 or 20.5).",
                needs_evaluation_data=True
            )
        
        evaluator = ConsumptionEvaluator()
        result = evaluator.evaluate(request.expected_liters, actual_liters)
        
        feedback = UserFeedback(
            calculated_consumption=request.expected_liters,
            actual_consumption=actual_liters,
            difference_percentage=result.difference_percentage,
            status=result.status,
            ai_response_summary=result.message
        )
        db.add(feedback)
        db.commit()
        
        llm = get_llm(config.STRONG_MODEL_NAME)
        prompt_for_llm = f"""
        Evaluation Result:
        Status: {result.status}
        Message: {result.message}
        Recommendations: {', '.join(result.recommendations)}
        
        Write a friendly, concise response with emojis.
        """
        response = llm.invoke([HumanMessage(content=prompt_for_llm)])
        
        return ChatResponse(
            response=response.content,
            needs_evaluation_data=False
        )

    
    if is_evaluation_intent(request.prompt):
        return ChatResponse(
            response="To evaluate your fuel consumption, please use our **Trip Calculator** first to get your expected liters, then tell me how many liters you actually pumped.",
            needs_evaluation_data=True
        )


    messages = [SystemMessage(content=config.SYSTEM_PROMPT)]
    for msg in request.history:
        if msg.role == "user": 
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant": 
            messages.append(AIMessage(content=msg.content))
    
    messages.append(HumanMessage(content=request.prompt))
    
    llm = get_llm()
    response = llm.invoke(messages)

    return ChatResponse(
        response=response.content,
        needs_evaluation_data=False
    )

@app.get("/feedback")
async def get_all_feedback(db=Depends(get_db)):
    """Feedbacks in the database"""
    feedbacks = db.query(UserFeedback).all()
    return [
        {
            "id": f.id,
            "expected_liters": f.calculated_consumption,
            "actual_liters": f.actual_consumption,
            "difference_percentage": f.difference_percentage,
            "status": f.status,
            "ai_response": f.ai_response_summary,
            "timestamp": f.timestamp
        }
        for f in feedbacks
    ] 
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



