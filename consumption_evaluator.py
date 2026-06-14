import re
from pydantic import BaseModel
from typing import List, Union, Optional

class EvaluationResult(BaseModel):
    status: str  
    difference_percentage: float
    message: str
    recommendations: List[str]

class ConsumptionEvaluator:
    
    @staticmethod
    def extract_number_from_text(text: str) -> Optional[float]:
        """استخراج أول رقم من النص (صحيح أو عشري)"""
        if text is None:
            return None
        text = str(text).strip()
        
        match = re.search(r'\d+\.?\d*', text)
        if match:
            return float(match.group())
        return None
    
    @staticmethod
    def evaluate(
        calculated_liters: float, 
        actual_input: Union[float, str, int]
    ) -> EvaluationResult:
        
        
        if calculated_liters is None or calculated_liters <= 0:
            return EvaluationResult(
                status="error",
                difference_percentage=0,
                message="❌ System error: Missing calculated value.",
                recommendations=[]
            )
        
        
        if isinstance(actual_input, str):
            actual_input = actual_input.strip()
            extracted = ConsumptionEvaluator.extract_number_from_text(actual_input)
            
            if extracted is None:
                return EvaluationResult(
                    status="error",
                    difference_percentage=0,
                    message="❌ I couldn't find a number in your response. Please enter your **actual consumption in liters** (e.g., 20 or 20.5).",
                    recommendations=["Write a number only, or a sentence with a number like: 'I pumped 20 liters'"]
                )
            actual_liters = extracted
        else:
            actual_liters = float(actual_input)

        
        if actual_liters <= 0:
            return EvaluationResult(
                status="error",
                difference_percentage=0,
                message=f" Invalid value: {actual_liters}. Actual consumption must be **greater than zero**.",
                recommendations=["Please enter a positive number (e.g., 18.5 liters)."]
            )

        
        diff_pct = ((actual_liters - calculated_liters) / calculated_liters) * 100
        
        if diff_pct <= -5:
            status = "excellent"
            msg = f"🌟 Excellent! You used {abs(diff_pct):.1f}% LESS fuel than expected."
            recs = ["Keep up your great driving habits!", "Your car is in perfect condition."]
        elif -5 < diff_pct <= 10:
            status = "good"
            msg = f"✅ Good job! Your consumption is within the normal range ({diff_pct:+.1f}%)."
            recs = ["Maintain your current driving style.", "Regular maintenance is key."]
        elif 10 < diff_pct <= 25:
            status = "warning"
            msg = f"⚠️ Warning: Your consumption is {diff_pct:.1f}% HIGHER than expected."
            recs = [
                "Check tire pressure.",
                "Avoid rapid acceleration and hard braking.",
                "Consider changing the air filter."
            ]
        else:
            status = "critical"
            msg = f" Critical: Your consumption is {diff_pct:.1f}% HIGHER! This indicates a potential issue."
            recs = [
                "Visit a mechanic for a full diagnostic.",
                "Check for fuel leaks or faulty oxygen sensors.",
                "Inspect spark plugs and fuel injectors."
            ]

        return EvaluationResult(
            status=status, 
            difference_percentage=diff_pct, 
            message=msg, 
            recommendations=recs
        )