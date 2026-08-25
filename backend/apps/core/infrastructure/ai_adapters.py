import os
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Type
from pydantic import BaseModel
import openai
import anthropic
from google import genai
from google.genai import types
import requests

class AIResult(BaseModel):
    text: str
    raw_response: Dict[str, Any]
    provider: str


class ImageResult(BaseModel):
    image_url: str
    provider: str


def get_mock_ai_result(response_schema: Type[BaseModel] | None, provider_name: str, error_msg: str) -> AIResult:
    """
    Fallback utility providing synthetic but realistic data structure when remote API key
    or rate limits block sandbox development.
    """
    if response_schema:
        mock_data = {
            "business_name": "BrewHub Coffee Subscriptions",
            "tagline": "Fueling your morning routine, automatically.",
            "theme_colors": ["#451a03", "#78350f", "#fef3c7", "#1e293b", "#0f172a"],
            "pages_to_generate": ["index", "plans", "about", "contact"],
            "logo_generation_prompt": "A modern minimalist coffee cup logo with purple neon glows",
            "banner_generation_prompt": "Coffee cups arranged in a neat grid with elegant lighting",
            "copywriting_tone": "warm and professional",
            "seo_keywords": ["coffee subscription", "organic beans", "daily brew"]
        }
        return AIResult(
            text=json.dumps(mock_data),
            raw_response={"mocked": True, "fallback_reason": error_msg},
            provider=f"{provider_name}-fallback"
        )
    else:
        return AIResult(
            text=(
                "<div style='font-family: sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #fff;'>"
                "  <h1 style='color: #8b5cf6;'>Welcome to BrewHub Coffee Subscriptions</h1>"
                "  <p style='color: #a3a3a3; font-size: 1.1em;'>The easiest way to get premium roasted beans delivered straight to your door weekly or monthly.</p>"
                "  <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 40px;'>"
                "    <div style='background: #111; padding: 20px; border-radius: 12px; border: 1px solid #222;'>"
                "      <h3 style='color: #d946ef; margin-top:0;'>Single Origin Box</h3>"
                "      <p style='font-size: 0.9em; color: #a3a3a3;'>Freshly roasted specialty coffee beans chosen by our experts each month.</p>"
                "      <span style='font-weight: bold; color: white;'>$24 / month</span>"
                "    </div>"
                "    <div style='background: #111; padding: 20px; border-radius: 12px; border: 1px solid #222;'>"
                "      <h3 style='color: #d946ef; margin-top:0;'>Espresso Roast</h3>"
                "      <p style='font-size: 0.9em; color: #a3a3a3;'>Bold and rich flavors optimized for espresso extraction and milky drinks.</p>"
                "      <span style='font-weight: bold; color: white;'>$22 / month</span>"
                "    </div>"
                "  </div>"
                "</div>"
            ),
            raw_response={"mocked": True, "fallback_reason": error_msg},
            provider=f"{provider_name}-fallback"
        )


class BaseAIProvider(ABC):
    """
    Abstract Base Class defining the contract for AI provider adapters.
    """
    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: str | None = None, response_schema: Type[BaseModel] | None = None) -> AIResult:
        pass

    @abstractmethod
    def generate_image(self, prompt: str, size: str = "1024x1024") -> ImageResult:
        pass


class OpenAIAdapter(BaseAIProvider):
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "mock-openai-key")
        self.client = openai.OpenAI(api_key=self.api_key)

    def generate_text(self, prompt: str, system_instruction: str | None = None, response_schema: Type[BaseModel] | None = None) -> AIResult:
        if self.api_key.startswith("mock-"):
            return get_mock_ai_result(response_schema, "openai", "Mock key detected - instant fallback")
            
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        kwargs = {}
        if response_schema:
            kwargs["response_format"] = response_schema

        try:
            response = self.client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=messages,
                **kwargs
            )
            message = response.choices[0].message
            return AIResult(
                text=message.content or "",
                raw_response=response.model_dump(),
                provider="openai"
            )
        except Exception as e:
            return get_mock_ai_result(response_schema, "openai", str(e))

    def generate_image(self, prompt: str, size: str = "1024x1024") -> ImageResult:
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                n=1
            )
            return ImageResult(
                image_url=response.data[0].url or "",
                provider="openai"
            )
        except Exception:
            return ImageResult(
                image_url="https://images.unsplash.com/photo-1511920170033-f8396924c348?w=800",
                provider="mock-image"
            )


class ClaudeAdapter(BaseAIProvider):
    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "mock-anthropic-key")
        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_text(self, prompt: str, system_instruction: str | None = None, response_schema: Type[BaseModel] | None = None) -> AIResult:
        if self.api_key.startswith("mock-"):
            return get_mock_ai_result(response_schema, "claude", "Mock key detected - instant fallback")
            
        system_text = system_instruction or ""
        if response_schema:
            system_text += f"\nReturn strictly valid JSON conforming to this JSON Schema: {response_schema.model_json_schema()}"

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=4000,
                system=system_text,
                messages=[{"role": "user", "content": prompt}]
            )
            return AIResult(
                text=response.content[0].text,
                raw_response=response.model_dump(),
                provider="claude"
            )
        except Exception as e:
            return get_mock_ai_result(response_schema, "claude", str(e))

    def generate_image(self, prompt: str, size: str = "1024x1024") -> ImageResult:
        return ImageResult(
            image_url="https://images.unsplash.com/photo-1511920170033-f8396924c348?w=800",
            provider="mock-image"
        )


class GeminiAdapter(BaseAIProvider):
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "mock-gemini-key")
        self.client = genai.Client(api_key=self.api_key)

    def generate_text(self, prompt: str, system_instruction: str | None = None, response_schema: Type[BaseModel] | None = None) -> AIResult:
        if self.api_key.startswith("mock-"):
            return get_mock_ai_result(response_schema, "gemini", "Mock key detected - instant fallback")
            
        config = types.GenerateContentConfig()
        if system_instruction:
            config.system_instruction = system_instruction
        if response_schema:
            config.response_mime_type = "application/json"
            config.response_schema = response_schema

        try:
            response = self.client.models.generate_content(
                model='gemini-1.5-pro',
                contents=prompt,
                config=config,
            )
            raw_data = response.model_dump() if hasattr(response, "model_dump") else {}
            return AIResult(
                text=response.text or "",
                raw_response=raw_data,
                provider="gemini"
            )
        except Exception as e:
            return get_mock_ai_result(response_schema, "gemini", str(e))

    def generate_image(self, prompt: str, size: str = "1024x1024") -> ImageResult:
        return ImageResult(
            image_url="https://images.unsplash.com/photo-1511920170033-f8396924c348?w=800",
            provider="mock-image"
        )


class DeepSeekAdapter(BaseAIProvider):
    def __init__(self):
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "mock-deepseek-key")
        self.client = openai.OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")

    def generate_text(self, prompt: str, system_instruction: str | None = None, response_schema: Type[BaseModel] | None = None) -> AIResult:
        if self.api_key.startswith("mock-"):
            return get_mock_ai_result(response_schema, "deepseek", "Mock key detected - instant fallback")
            
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )
            return AIResult(
                text=response.choices[0].message.content or "",
                raw_response=response.model_dump(),
                provider="deepseek"
            )
        except Exception as e:
            return get_mock_ai_result(response_schema, "deepseek", str(e))

    def generate_image(self, prompt: str, size: str = "1024x1024") -> ImageResult:
        return ImageResult(
            image_url="https://images.unsplash.com/photo-1511920170033-f8396924c348?w=800",
            provider="mock-image"
        )


class OpenRouterAdapter(BaseAIProvider):
    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "mock-openrouter-key")

    def generate_text(self, prompt: str, system_instruction: str | None = None, response_schema: Type[BaseModel] | None = None) -> AIResult:
        if self.api_key.startswith("mock-"):
            return get_mock_ai_result(response_schema, "openrouter", "Mock key detected - instant fallback")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": "meta-llama/llama-3.1-70b-instruct",
            "messages": messages
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response_json = response.json()
            return AIResult(
                text=response_json["choices"][0]["message"]["content"],
                raw_response=response_json,
                provider="openrouter"
            )
        except Exception as e:
            return get_mock_ai_result(response_schema, "openrouter", str(e))

    def generate_image(self, prompt: str, size: str = "1024x1024") -> ImageResult:
        return ImageResult(
            image_url="https://images.unsplash.com/photo-1511920170033-f8396924c348?w=800",
            provider="mock-image"
        )
