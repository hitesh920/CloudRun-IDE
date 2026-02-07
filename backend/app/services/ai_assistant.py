"""
CloudRun IDE - AI Assistant
Google Gemini integration for code assistance.
"""

import google.generativeai as genai
from typing import Optional, Dict
from app.config import settings


class AIAssistant:
    """AI-powered code assistance using Google Gemini."""
    
    def __init__(self):
        """Initialize Gemini API."""
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
            print("✅ Gemini AI Assistant initialized")
        else:
            self.enabled = False
            print("⚠️ Gemini API key not found - AI features disabled")
    
    def is_enabled(self) -> bool:
        """Check if AI assistant is enabled."""
        return self.enabled
    
    async def fix_error(self, code: str, error: str, language: str) -> Optional[Dict]:
        """
        Analyze error and suggest fix.
        
        Args:
            code: Source code
            error: Error message
            language: Programming language
            
        Returns:
            Dictionary with fixed code and explanation
        """
        if not self.enabled:
            return {"error": "AI assistant not configured"}
        
        prompt = f"""You are a helpful programming assistant. A {language} program has an error.

CODE:
```{language}
{code}
```

ERROR:
{error}

Please:
1. Explain what's wrong
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
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "success": True,
                "response": response.text,
                "action": "fix_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def explain_error(self, error: str, language: str) -> Optional[Dict]:
        """
        Explain what an error means.
        
        Args:
            error: Error message
            language: Programming language
            
        Returns:
            Dictionary with explanation
        """
        if not self.enabled:
            return {"error": "AI assistant not configured"}
        
        prompt = f"""You are a helpful programming assistant. Explain this {language} error in simple terms:

ERROR:
{error}

Please explain:
1. What this error means
2. Common causes
3. How to fix it

Keep it concise and beginner-friendly.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "success": True,
                "response": response.text,
                "action": "explain_error"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def explain_code(self, code: str, language: str) -> Optional[Dict]:
        """
        Explain what code does.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Dictionary with explanation
        """
        if not self.enabled:
            return {"error": "AI assistant not configured"}
        
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
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "success": True,
                "response": response.text,
                "action": "explain_code"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def optimize_code(self, code: str, language: str) -> Optional[Dict]:
        """
        Suggest code optimizations.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Dictionary with optimized code and suggestions
        """
        if not self.enabled:
            return {"error": "AI assistant not configured"}
        
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
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "success": True,
                "response": response.text,
                "action": "optimize_code"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def chat(self, message: str, context: Optional[str] = None) -> Optional[Dict]:
        """
        General chat with AI about code.
        
        Args:
            message: User message
            context: Optional code context
            
        Returns:
            Dictionary with AI response
        """
        if not self.enabled:
            return {"error": "AI assistant not configured"}
        
        prompt = message
        if context:
            prompt = f"""Context:
```
{context}
```

Question: {message}
"""
        
        try:
            response = self.model.generate_content(prompt)
            return {
                "success": True,
                "response": response.text,
                "action": "chat"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Global AI assistant instance
ai_assistant = AIAssistant()
