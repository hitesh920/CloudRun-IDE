"""
CloudRun IDE - AI Assistant
Google Gemini integration for code assistance using the new google.genai SDK.
"""

from typing import Dict
from app.config import settings


class AIAssistant:
    """AI-powered code assistance using Google Gemini."""
    
    def __init__(self):
        """Initialize Gemini API."""
        self.enabled = False
        self.client = None
        self.model_name = "gemini-2.0-flash"
        
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
            print("⚠️  AI Assistant: DISABLED (no valid API key)")
            return
        
        try:
            from google import genai
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.enabled = True
            print(f"✅ AI Assistant (Gemini {self.model_name}): initialized")
        except Exception as e:
            print(f"❌ AI Assistant initialization failed: {e}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if AI assistant is enabled."""
        return self.enabled
    
    async def _generate(self, prompt: str) -> Dict:
        """Generate content from Gemini with error handling."""
        if not self.enabled or not self.client:
            return {"success": False, "error": "AI assistant not configured"}
        
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
            )
            
            return {
                "success": True,
                "response": response.text,
            }
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Gemini API error: {error_msg}")
            return {
                "success": False,
                "error": f"AI request failed: {error_msg}",
            }
    
    async def fix_error(self, code: str, error: str, language: str) -> Dict:
        """Analyze error and suggest fix."""
        prompt = f"""You are a helpful programming assistant. A {language} program has an error.

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
        prompt = f"""You are a helpful programming assistant. Explain this {language} error in simple terms:

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
        prompt = f"""You are a helpful programming assistant. Explain this {language} code:

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
        prompt = f"""You are a helpful programming assistant. Review and optimize this {language} code:

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
