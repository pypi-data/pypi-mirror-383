"""OpenAI GPT-5 provider implementation."""

import os
import json
from typing import Dict, List, Optional
from ai_shell_command_generator.providers.base import BaseProvider
from ai_shell_command_generator.providers.models import ModelRegistry
from ai_shell_command_generator.utils.logger import get_logger


class OpenAIProvider(BaseProvider):
    """OpenAI GPT-5 API provider."""
    
    def __init__(self, model: str, api_key: Optional[str] = None, **kwargs):
        self.logger = get_logger(__name__)
        """
        Initialize OpenAI provider.
        
        Args:
            model: The GPT model to use
            api_key: OpenAI API key (optional, can use env var)
            **kwargs: Additional arguments
        """
        super().__init__(model, **kwargs)
        
        # Validate model
        if not ModelRegistry.is_valid_model('openai', model):
            raise ValueError(f"Invalid OpenAI model: {model}")
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # If no key found, prompt user interactively
        if not self.api_key:
            try:
                from ai_shell_command_generator.cli.prompts import prompt_for_api_key
                prompted_key = prompt_for_api_key('openai')
                if prompted_key:
                    self.api_key = prompted_key
                    # Set in environment for this session
                    os.environ['OPENAI_API_KEY'] = prompted_key
                else:
                    raise ValueError("OpenAI API key required but not provided")
            except ImportError:
                # If prompts not available (testing?), raise error
                raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        # Initialize client
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI provider requires openai package. Install with: pip install openai")
    
    def generate_command(self, query: str, shell: str, os_info: str) -> str:
        """Generate command using OpenAI."""
        # Build system message (simplified)
        if shell == 'cmd':
            system_msg = "You are a Windows CMD.EXE command generator. Output ONLY the command, nothing else."
        elif shell == 'powershell':
            system_msg = "You are a Windows PowerShell command generator. Output ONLY the command, nothing else."
        else:
            system_msg = "You are a shell command generator. Output ONLY the command, nothing else."
        
        # Build user message with context (like Anthropic/Ollama)
        if shell == 'cmd':
            shell_desc = "Windows CMD.EXE batch command"
        elif shell == 'powershell':
            shell_desc = "Windows PowerShell command"
        else:
            shell_desc = "macOS shell command"
        
        user_msg = f"Generate a {shell_desc} for this task: {query}"
        
        # Log the request details
        self.logger.debug("=== OpenAI API Request ===")
        self.logger.debug(f"Model: {self.model}")
        self.logger.debug(f"Max completion tokens: 10000")
        self.logger.debug("Messages:")
        self.logger.debug(f"  System: {repr(system_msg)}")
        self.logger.debug(f"  User: {repr(user_msg)}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=10000,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ]
            )
            
            # Log the response details
            self.logger.debug("=== OpenAI API Response ===")
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                self.logger.debug(f"Prompt tokens: {usage.prompt_tokens}")
                self.logger.debug(f"Completion tokens: {usage.completion_tokens}")
                self.logger.debug(f"Total tokens: {usage.total_tokens}")
                
                # Log reasoning tokens if available
                if hasattr(usage, 'completion_tokens_details') and usage.completion_tokens_details:
                    details = usage.completion_tokens_details
                    if hasattr(details, 'reasoning_tokens'):
                        self.logger.debug(f"Reasoning tokens: {details.reasoning_tokens}")
            
            if response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content.strip()
                self.logger.debug(f"Response content: {repr(content)}")
            else:
                self.logger.debug("Response content: EMPTY")
            
            if not response.choices or not response.choices[0].message.content:
                return f"echo 'OpenAI returned empty response'"
            
            command = response.choices[0].message.content.strip()
            if not command:
                return f"echo 'OpenAI returned empty command'"
            
            return self._clean_command(command)
        except Exception as e:
            return f"echo 'Error generating command with OpenAI: {str(e)}'"
    
    def generate_teaching_response(self, query: str, shell: str, os_info: str) -> Dict:
        """Generate command with teaching explanation."""
        if shell == 'cmd':
            shell_desc = "Windows CMD.EXE"
        elif shell == 'powershell':
            shell_desc = "Windows PowerShell"
        else:
            shell_desc = f"{os_info} shell"
        
        teaching_prompt = self._build_teaching_prompt(query, shell, os_info)
        
        # Log the teaching request
        self.logger.debug("=== OpenAI Teaching API Request ===")
        self.logger.debug(f"Model: {self.model}")
        self.logger.debug(f"Max completion tokens: 10000")
        self.logger.debug(f"Teaching prompt: {repr(teaching_prompt)}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=10000,
                messages=[
                    {"role": "user", "content": teaching_prompt}
                ]
            )
            
            # Log teaching response
            self.logger.debug("=== OpenAI Teaching API Response ===")
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                self.logger.debug(f"Prompt tokens: {usage.prompt_tokens}")
                self.logger.debug(f"Completion tokens: {usage.completion_tokens}")
                self.logger.debug(f"Total tokens: {usage.total_tokens}")
            
            response_text = response.choices[0].message.content.strip()
            self.logger.debug(f"Response content: {repr(response_text)}")
            
            from ai_shell_command_generator.teaching.formatter import parse_teaching_response
            return parse_teaching_response(response_text)
            
        except Exception as e:
            return {
                'command': f"echo 'Error: {str(e)}'",
                'breakdown': 'Error occurred',
                'os_notes': '',
                'safer_approach': '',
                'learned': []
            }
    
    def assess_risk(self, command: str, shell: str) -> Dict:
        """Assess command risk using OpenAI."""
        risk_prompt = self._build_risk_prompt(command, shell)
        
        # Log the risk assessment request
        self.logger.debug("=== OpenAI Risk Assessment API Request ===")
        self.logger.debug(f"Model: {self.model}")
        self.logger.debug(f"Max completion tokens: 5000")
        self.logger.debug(f"Risk prompt: {repr(risk_prompt)}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_completion_tokens=5000,
                messages=[
                    {"role": "user", "content": risk_prompt}
                ]
            )
            
            # Log risk assessment response
            self.logger.debug("=== OpenAI Risk Assessment API Response ===")
            if hasattr(response, 'usage') and response.usage:
                usage = response.usage
                self.logger.debug(f"Prompt tokens: {usage.prompt_tokens}")
                self.logger.debug(f"Completion tokens: {usage.completion_tokens}")
                self.logger.debug(f"Total tokens: {usage.total_tokens}")
            result_text = response.choices[0].message.content.strip()
            return self._parse_risk_response(result_text)
        except Exception as e:
            return {'is_risky': False, 'severity': 'low', 'reason': f'Assessment failed: {e}'}
    
    def list_available_models(self) -> List[str]:
        """List available OpenAI models."""
        return list(ModelRegistry.OPENAI_MODELS.keys())
    
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
    
    @property
    def requires_api_key(self) -> bool:
        """OpenAI requires API key."""
        return True
    
    @property
    def supports_streaming(self) -> bool:
        """OpenAI supports streaming."""
        return True
    
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
