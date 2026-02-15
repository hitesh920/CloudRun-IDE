"""
CloudRun IDE - AI Assistant
Multi-provider AI integration for code assistance.
Supports: Groq (free), Google Gemini
"""

import json
from typing import Dict
from app.config import settings


class AIAssistant:
    """AI-powered code assistance. Tries Groq first, then Gemini."""
    
    def __init__(self):
        """Initialize AI provider."""
        self.enabled = False
        self.provider = None
        self.provider_name = None
        
        # Try Groq first (free, fast)
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here":
            try:
                import requests
                self.provider = "groq"
                self.provider_name = "Groq (llama-3.3-70b)"
                self.groq_key = settings.GROQ_API_KEY
                self.groq_model = "llama-3.3-70b-versatile"
                self.enabled = True
                print(f"✅ AI Assistant ({self.provider_name}): initialized")
                return
            except Exception as e:
                print(f"⚠️  Groq init failed: {e}")
        
        # Fallback to Gemini
        if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
            try:
                from google import genai
                self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
                self.provider = "gemini"
                self.provider_name = "Gemini (2.0-flash)"
                self.gemini_model = "gemini-2.0-flash"
                self.enabled = True
                print(f"✅ AI Assistant ({self.provider_name}): initialized")
                return
            except Exception as e:
                print(f"⚠️  Gemini init failed: {e}")
        
        print("⚠️  AI Assistant: DISABLED (no GROQ_API_KEY or GEMINI_API_KEY)")
    
    def is_enabled(self) -> bool:
        """Check if AI assistant is enabled."""
        return self.enabled
    
    def get_provider_name(self) -> str:
        """Get the active provider name."""
        return self.provider_name or "None"
    
    async def _generate(self, prompt: str) -> Dict:
        """Generate content from AI provider."""
        if not self.enabled:
            return {"success": False, "error": "AI assistant not configured"}
        
        try:
            import asyncio
            
            if self.provider == "groq":
                response = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self._call_groq(prompt)
                )
            elif self.provider == "gemini":
                response = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self._call_gemini(prompt)
                )
            else:
                return {"success": False, "error": "No AI provider configured"}
            
            return {"success": True, "response": response}
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ AI API error ({self.provider}): {error_msg}")
            return {"success": False, "error": f"AI request failed: {error_msg}"}
    
    def _call_groq(self, prompt: str) -> str:
        """Call Groq API (OpenAI-compatible)."""
        import requests
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.groq_model,
                "messages": [
                    {"role": "system", "content": "You are a helpful programming assistant."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 2048,
                "temperature": 0.3,
            },
            timeout=30,
        )
        
        if response.status_code != 200:
            error_data = response.json().get("error", {})
            raise Exception(f"{response.status_code}: {error_data.get('message', response.text)}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API using google-genai SDK."""
        response = self.client.models.generate_content(
            model=self.gemini_model,
            contents=prompt,
        )
        return response.text
    
    async def fix_error(self, code: str, error: str, language: str) -> Dict:
        """Analyze error and suggest fix."""
        prompt = f"""A {language} program has an error.

CODE:
```{language}
{code}
```

ERROR:
{error}

Please:
1. Explain what's wrong (briefly)
2. Provide the corrected code
3. Explain the fix

Format your response as:
**Problem:** (brief explanation)
**Solution:** (what to fix)
**Fixed Code:**
```{language}
(corrected code here)
```
"""
        result = await self._generate(prompt)
        if result.get("success"):
            result["action"] = "fix_error"
        return result
    
    async def explain_error(self, error: str, language: str) -> Dict:
        """Explain what an error means."""
        prompt = f"""Explain this {language} error in simple terms:

ERROR:
{error}

Please explain:
1. What this error means
2. Common causes
3. How to fix it

Keep it concise and beginner-friendly.
"""
        result = await self._generate(prompt)
        if result.get("success"):
            result["action"] = "explain_error"
        return result
    
    async def explain_code(self, code: str, language: str) -> Dict:
        """Explain what code does."""
        prompt = f"""Explain this {language} code:

CODE:
```{language}
{code}
```

Please explain:
1. What the code does (step by step)
2. Key concepts used
3. Any potential issues

Keep it clear and educational.
"""
        result = await self._generate(prompt)
        if result.get("success"):
            result["action"] = "explain_code"
        return result
    
    async def optimize_code(self, code: str, language: str) -> Dict:
        """Suggest code optimizations."""
        prompt = f"""Review and optimize this {language} code:

CODE:
```{language}
{code}
```

Please provide:
1. Optimization suggestions
2. Best practices to apply
3. Optimized version of the code

**Suggestions:**
(list improvements)

**Optimized Code:**
```{language}
(improved code here)
```
"""
        result = await self._generate(prompt)
        if result.get("success"):
            result["action"] = "optimize_code"
        return result


# Global AI assistant instance
ai_assistant = AIAssistant()
