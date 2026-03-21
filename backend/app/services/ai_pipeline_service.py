import logging
import json
import re
from typing import Optional, Dict, List
from app.models.user import User
from app.models.email_message import EmailMessage
from app.models.prompt_library import PromptTemplate
import httpx

logger = logging.getLogger(__name__)

class AIPipelineService:
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=60.0)

    async def process_email(self, user: User, email_msg: EmailMessage):
        """Main entry point to process an email through the AI pipeline"""
        if not user.ai_providers:
            logger.warning(f"No AI providers configured for user {user.username}")
            return

        # 1. Classify
        is_collab, urgency = await self._classify_email(user, email_msg)
        email_msg.is_collaboration = is_collab
        email_msg.urgency = urgency
        
        if is_collab:
            # 2. Extract Data
            extracted_data = await self._extract_data(user, email_msg)
            email_msg.ai_data = extracted_data
            email_msg.status = 'Collaboration'
        else:
            email_msg.status = 'Skim'
            
        email_msg.save()

    async def _classify_email(self, user: User, email_msg: EmailMessage) -> tuple[bool, str]:
        """Classify if the email is a collaboration and its urgency"""
        provider = user.ai_providers[0] # Use first available for now
        
        prompt = f"""
        Analyze this email and determine if it's a "collaboration" or "sponsorship" request for a Studygram/Content Creator.
        Also determine the urgency (High, Medium, Normal) based on keywords like ASAP, deadline, this week.
        
        Email Subject: {email_msg.subject}
        Email Body: {email_msg.body[:2000]}
        
        Respond ONLY in JSON format:
        {{
            "is_collaboration": true/false,
            "urgency": "High/Medium/Normal",
            "reason": "short explanation"
        }}
        """
        
        result = await self._call_ai(provider, prompt)
        if not result:
            return False, "Normal"
            
        try:
            data = json.loads(self._clean_json(result))
            return data.get("is_collaboration", False), data.get("urgency", "Normal")
        except:
            return False, "Normal"

    async def _extract_data(self, user: User, email_msg: EmailMessage) -> Dict:
        """Extract Scope, Platform, and Price from a collaboration email"""
        provider = user.ai_providers[0]
        
        prompt = f"""
        Extract the following data from this collaboration email. 
        If not explicitly mentioned, use "###" for price and "Not Specified" for others.
        
        Email Body: {email_msg.body[:3000]}
        
        JSON Fields:
        - scope: (App name, Web name, or Product name)
        - platform: (TikTok, Instagram, YouTube, X, etc.)
        - price: (The offer amount or ###)
        - collaborator_name: (The person or brand name)
        """
        
        result = await self._call_ai(provider, prompt)
        if not result:
            return {}
            
        try:
            return json.loads(self._clean_json(result))
        except:
            return {}

    async def generate_draft(self, user: User, email_msg: EmailMessage, prompt_template: PromptTemplate) -> str:
        """Generate a reply draft using a specific prompt template"""
        provider = user.ai_providers[0]
        
        # Replace variables in template
        content = prompt_template.content
        # Simple replacement for common variables
        context_vars = {
            "collaborator_name": email_msg.ai_data.get("collaborator_name", "Team"),
            "scope": email_msg.ai_data.get("scope", "your product"),
            "sender_name": user.display_name or user.username
        }
        for key, val in context_vars.items():
            content = content.replace(f"{{{{{key}}}}}", str(val))

        full_prompt = f"""
        Context: I am a Studygram creator receiving a collaboration request.
        Original Email Body: {email_msg.body[:1500]}
        
        Task: Draft a professional response based on this template instructions:
        ---
        {content}
        ---
        Respond with ONLY the email body text.
        """
        
        return await self._call_ai(provider, full_prompt) or "Failed to generate draft."

    async def _call_ai(self, provider: Dict, prompt: str) -> Optional[str]:
        """Generic wrapper to call AI providers"""
        p_type = provider.get('type', 'openai')
        api_key = provider.get('api_key')
        
        if not api_key:
            return None

        try:
            if p_type == 'openai':
                resp = await self.http_client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo", # Or user configured
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                if resp.status_code == 200:
                    return resp.json()['choices'][0]['message']['content']
            elif p_type == 'deepseek':
                resp = await self.http_client.post(
                    "https://api.deepseek.com/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [{"role": "user", "content": prompt}]
                    }
                )
                if resp.status_code == 200:
                    return resp.json()['choices'][0]['message']['content']
            elif p_type == 'gemini':
                # Simplified Google AI call
                resp = await self.http_client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}",
                    json={
                        "contents": [{"parts": [{"text": prompt}]}]
                    }
                )
                if resp.status_code == 200:
                    return resp.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            logger.error(f"AI Call Error ({p_type}): {str(e)}")
            
        return None

    def _clean_json(self, text: str) -> str:
        """Remove markdown code blocks from AI response"""
        return re.sub(r'```json\n?|\n?```', '', text).strip()

ai_pipeline = AIPipelineService()
