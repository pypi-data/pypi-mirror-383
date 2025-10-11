"""Ollama local AI provider implementation."""

import json
from typing import Dict, List, Optional
from ai_shell_command_generator.providers.base import BaseProvider
from ai_shell_command_generator.utils.logger import get_logger


class OllamaProvider(BaseProvider):
    """Ollama local AI provider."""
    
    def __init__(self, model: str, host: str = "localhost:11434", **kwargs):
        self.logger = get_logger(__name__)
        """
        Initialize Ollama provider.
        
        Args:
            model: The Ollama model to use
            host: Ollama host address
            **kwargs: Additional arguments
        """
        super().__init__(model, **kwargs)
        self.host = host
        
        # Initialize ollama client
        try:
            import ollama
            self.ollama = ollama
        except ImportError:
            raise ImportError("Ollama provider requires ollama package. Install with: pip install ollama")
    
    def generate_command(self, query: str, shell: str, os_info: str) -> str:
        """Generate command using Ollama."""
        prompt = self._build_command_prompt(query, shell, os_info)
        
        # Log the request details
        self.logger.debug("=== Ollama API Request ===")
        self.logger.debug(f"Model: {self.model}")
        self.logger.debug(f"Host: {self.host}")
        self.logger.debug(f"Prompt: {repr(prompt)}")
        
        try:
            response = self.ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Log the response details
            self.logger.debug("=== Ollama API Response ===")
            if 'prompt_eval_count' in response:
                self.logger.debug(f"Prompt eval count: {response['prompt_eval_count']}")
            if 'eval_count' in response:
                self.logger.debug(f"Eval count: {response['eval_count']}")
            if 'total_duration' in response:
                self.logger.debug(f"Total duration: {response['total_duration']}ns")
            
            command = response['message']['content'].strip()
            self.logger.debug(f"Response content: {repr(command)}")
            return self._clean_command(command)
        except Exception as e:
            return f"echo 'Error connecting to Ollama: {str(e)}'"
    
    def generate_teaching_response(self, query: str, shell: str, os_info: str) -> Dict:
        """Generate command with teaching explanation."""
        prompt = self._build_teaching_prompt(query, shell, os_info)
        
        # Log the teaching request
        self.logger.debug("=== Ollama Teaching API Request ===")
        self.logger.debug(f"Model: {self.model}")
        self.logger.debug(f"Host: {self.host}")
        self.logger.debug(f"Teaching prompt: {repr(prompt)}")
        
        try:
            response = self.ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Log teaching response
            self.logger.debug("=== Ollama Teaching API Response ===")
            if 'prompt_eval_count' in response:
                self.logger.debug(f"Prompt eval count: {response['prompt_eval_count']}")
            if 'eval_count' in response:
                self.logger.debug(f"Eval count: {response['eval_count']}")
            if 'total_duration' in response:
                self.logger.debug(f"Total duration: {response['total_duration']}ns")
            
            response_text = response['message']['content'].strip()
            self.logger.debug(f"Response content: {repr(response_text[:200])}...")  # First 200 chars
            
            # Use the shared parser from teaching.formatter
            from ai_shell_command_generator.teaching.formatter import parse_teaching_response
            return parse_teaching_response(response_text)
            
        except Exception as e:
            return {
                'command': f"echo 'Error generating teaching response: {str(e)}'",
                'breakdown': 'Error occurred during generation',
                'os_notes': '',
                'safer_approach': '',
                'learned': []
            }
    
    def assess_risk(self, command: str, shell: str) -> Dict:
        """Assess command risk using Ollama."""
        risk_prompt = self._build_risk_prompt(command, shell)
        
        # Log the risk assessment request
        self.logger.debug("=== Ollama Risk Assessment API Request ===")
        self.logger.debug(f"Model: {self.model}")
        self.logger.debug(f"Host: {self.host}")
        self.logger.debug(f"Risk prompt: {repr(risk_prompt)}")
        
        try:
            response = self.ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": risk_prompt}]
            )
            
            # Log risk assessment response
            self.logger.debug("=== Ollama Risk Assessment API Response ===")
            if 'prompt_eval_count' in response:
                self.logger.debug(f"Prompt eval count: {response['prompt_eval_count']}")
            if 'eval_count' in response:
                self.logger.debug(f"Eval count: {response['eval_count']}")
            if 'total_duration' in response:
                self.logger.debug(f"Total duration: {response['total_duration']}ns")
            
            result_text = response['message']['content'].strip()
            self.logger.debug(f"Response content: {repr(result_text)}")
            return self._parse_risk_response(result_text)
        except Exception as e:
            return {'is_risky': False, 'severity': 'low', 'reason': f'Assessment failed: {e}'}
    
    def list_available_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            models = self.ollama.list()
            if models and models.models:
                return [model.model for model in models.models]
            return []
        except Exception:
            return []
    
    @property
    def requires_api_key(self) -> bool:
        """Ollama doesn't require API key."""
        return False
    
    @property
    def supports_streaming(self) -> bool:
        """Ollama supports streaming."""
        return True
    
    def _build_command_prompt(self, query: str, shell: str, os_info: str) -> str:
        """Build prompt for command generation."""
        if shell == 'cmd':
            shell_desc = "Windows CMD.EXE batch command"
        elif shell == 'powershell':
            shell_desc = "Windows PowerShell command"
        else:
            shell_desc = f"{os_info} shell command"
        
        return f"""Generate a {shell_desc} for this task: {query}

Return ONLY the command, without any explanation or markdown formatting."""
    
    def _build_teaching_prompt(self, query: str, shell: str, os_info: str) -> str:
        """Build prompt for teaching response."""
        return f"""Generate a {shell} command for {os_info} that: {query}

You MUST format your response using these EXACT headers (do not change the wording):

COMMAND:
[the exact command to run]

BREAKDOWN:
[explain each part of the command with proper indentation]

OS NOTES:
[platform-specific considerations for {os_info}]
[BSD vs GNU differences if relevant]
[any gotchas or limitations]

SAFER APPROACH:
[if this command has risks, show a safer alternative or preview step]

WHAT YOU LEARNED:
[key concepts from this command - 3-5 bullet points]

CRITICAL: Use the EXACT header text shown above. Do not modify headers like "WHAT YOU LEARNED" to "WHAT YOU LEARN" or any other variation.

Be concise but clear. Teach the user to understand, not just copy."""
    
    def _build_risk_prompt(self, command: str, shell: str) -> str:
        """Build prompt for risk assessment."""
        return f"""Analyze this {shell} command for potential risks:

Command: {command}

You MUST respond with ONLY a JSON object. Do NOT include any other text, explanations, or markdown.

Use this EXACT format:
{{"is_risky": true/false, "severity": "low/medium/high", "reason": "brief explanation"}}

CRITICAL: Output ONLY the JSON object above. No additional text before or after.

Consider risks like: data deletion (rm, dd), permission changes (chmod, chown), 
system modifications (install, update), network exposure, recursive operations."""
    
    def _parse_risk_response(self, response_text: str) -> Dict:
        """Parse risk assessment response."""
        try:
            # Extract JSON from response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                json_text = response_text[start:end]
                return json.loads(json_text)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Fallback parsing
        return {'is_risky': False, 'severity': 'low', 'reason': 'Could not parse risk assessment'}
