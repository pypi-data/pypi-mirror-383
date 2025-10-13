
import os
import requests
from typing import Optional
from .llm_base import BaseLLM
from ..core.exceptions import LLMError

class OpenAILLM(BaseLLM):
    """Cliente para OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"))
        if not self.api_key:
            raise LLMError("OPENAI_API_KEY não encontrada")
        
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = os.getenv("LLM") or "gpt-4o-mini"
    
    def chat(self, system_prompt: str, user_prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
        }
        
        try:
            response = requests.post(self.base_url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise LLMError(f"Erro OpenAI: {str(e)}")
