import os
import json
import logging
import httpx
from typing import Optional, Dict, Any, List
from backend.config import settings
from backend.utils.helpers import parse_ai_json

logger = logging.getLogger(__name__)

class AIService:
    """
    Centralized AI abstraction layer.
    Supports configurable providers (Gemini, OpenAI, Groq) with seamless
    fallback to intelligent heuristic algorithms and curated question banks
    when an API key is not configured or an external call fails.
    """

    def __init__(self):
        self.provider = (settings.AI_PROVIDER or "").lower().strip()
        self.api_key = (settings.AI_API_KEY or "").strip()
        self.model = (settings.AI_MODEL or "").strip()

        # Sensible defaults per provider
        if not self.model:
            if self.provider == "gemini":
                self.model = "gemini-1.5-flash"
            elif self.provider == "openai":
                self.model = "gpt-4o-mini"
            elif self.provider == "groq":
                self.model = "llama-3.3-70b-versatile"
            else:
                self.model = "standard-ai"

    def is_configured(self) -> bool:
        """Check if a valid AI provider and key are configured."""
        return bool(self.provider and self.api_key)

    async def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """Call external LLM API if configured."""
        if not self.is_configured():
            return None

        try:
            if self.provider == "gemini":
                return await self._call_gemini(prompt, system_prompt)
            elif self.provider in ["openai", "groq"]:
                return await self._call_openai_compatible(prompt, system_prompt)
            else:
                logger.warning(f"Unsupported AI provider: {self.provider}")
                return None
        except Exception as e:
            logger.error(f"Error calling AI provider {self.provider}: {e}")
            return None

    async def _call_gemini(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """Invoke Google Gemini REST API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        contents = []
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": f"SYSTEM INSTRUCTIONS:\n{system_prompt}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will follow all instructions carefully."}]})

        contents.append({"role": "user", "parts": [{"text": prompt}]})
        payload = {"contents": contents, "generationConfig": {"temperature": 0.4, "maxOutputTokens": 2048}}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
            else:
                logger.error(f"Gemini API returned status {response.status_code}: {response.text}")
                return None

    async def _call_openai_compatible(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """Invoke OpenAI / Groq compatible chat completions endpoint."""
        if self.provider == "groq":
            endpoint = "https://api.groq.com/openai/v1/chat/completions"
        else:
            endpoint = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": 2048
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(endpoint, headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "")
            else:
                logger.error(f"{self.provider} API returned status {response.status_code}: {response.text}")
                return None

    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Generate structured JSON response, falling back safely if None."""
        text_response = await self.generate_text(prompt, system_prompt)
        if text_response:
            parsed = parse_ai_json(text_response)
            if parsed:
                return parsed
        return None

ai_service = AIService()
