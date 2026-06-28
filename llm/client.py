import os
import json
import logging
from .prompts import get_system_prompt
from validator.schema import MissionPlan

logger = logging.getLogger(__name__)

class MissionParser:
    def __init__(self, use_mock: bool = False, model_name: str = "gemini-2.5-flash", allowed_routes: list[str] = None):
        self.use_mock = use_mock
        self.model_name = model_name
        self.allowed_routes = allowed_routes
        self.client = None
        
        if not self.use_mock:
            try:
                from google import genai
                from google.genai import types
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key:
                    self.client = genai.Client()
                else:
                    logger.warning("GEMINI_API_KEY not found in environment. Falling back to Mock parser.")
                    self.use_mock = True
            except ImportError:
                logger.warning("google-genai not installed. Falling back to Mock parser.")
                self.use_mock = True
                
    def parse_prompt(self, user_prompt: str) -> dict:
        """
        Parses the user prompt into a dictionary matching the MissionPlan schema.
        """
        if self.use_mock:
            return self._mock_parse(user_prompt)
            
        return self._llm_parse(user_prompt)
        
    def _llm_parse(self, user_prompt: str) -> dict:
        from google.genai import types
        
        system_instruction = get_system_prompt(self.allowed_routes)
        logger.info(f"Sending prompt to LLM ({self.model_name})...")
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=MissionPlan,
                temperature=0.0,
            ),
        )
        
        raw_json = response.text
        try:
            return json.loads(raw_json)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode LLM response: {raw_json}")
            raise ValueError("LLM returned invalid JSON.") from e

    def _mock_parse(self, user_prompt: str) -> dict:
        """
        A naive keyword-based parser for offline testing.
        """
        logger.info("Using Mock parser for prompt...")
        prompt_lower = user_prompt.lower()
        
        plan = {
            "mission_type": "patrol",
            "route": "warehouse_loop",
            "loops": 1,
            "speed": None,
            "return_home": True
        }
        
        if "inspect" in prompt_lower:
            plan["mission_type"] = "inspect"
            plan["route"] = "inspection_route"
        if "perimeter" in prompt_lower:
            plan["route"] = "perimeter"
            
        if "twice" in prompt_lower or "2 times" in prompt_lower:
            plan["loops"] = 2
        elif "thrice" in prompt_lower or "3 times" in prompt_lower:
            plan["loops"] = 3
            
        if "speed" in prompt_lower:
            words = prompt_lower.split()
            for i, word in enumerate(words):
                if "speed" in word and i + 1 < len(words):
                    try:
                        plan["speed"] = float(words[i+1])
                    except ValueError:
                        pass
                        
        if "do not return" in prompt_lower or "stay there" in prompt_lower:
            plan["return_home"] = False
            
        return plan
