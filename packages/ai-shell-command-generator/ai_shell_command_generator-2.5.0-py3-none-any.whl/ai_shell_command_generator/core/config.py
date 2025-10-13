"""Configuration management for AI Shell Command Generator."""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class ProviderConfig:
    """Configuration for a specific provider."""
    api_key: Optional[str] = None
    api_key_env: Optional[str] = None
    default_model: str = ""
    available_models: list[str] = field(default_factory=list)
    custom_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TeachingConfig:
    """Configuration for teaching mode."""
    detail_level: str = "standard"  # minimal, standard, verbose
    show_alternatives: bool = True
    show_examples: bool = True


@dataclass
class CommandConfig:
    """Main configuration for the application."""
    # Provider settings
    provider: str = "openai"
    model: str = ""
    provider_configs: Dict[str, ProviderConfig] = field(default_factory=dict)
    
    # Shell settings
    shell: str = "bash"
    os_type: str = ""
    
    # Mode settings
    teach_mode: bool = False
    interactive: bool = True
    
    # Feature flags
    risk_check: bool = True
    skip_risk_warnings: bool = False
    verbose: bool = False
    auto_copy: bool = False
    
    # Teaching settings
    teaching: TeachingConfig = field(default_factory=TeachingConfig)
    
    # Config file path
    config_file: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization setup."""
        if not self.os_type:
            from .os_detection import get_os_type
            self.os_type = get_os_type()
        
        # Only set default model if provider is set
        if not self.model and self.provider:
            from ai_shell_command_generator.providers.models import ModelRegistry
            self.model = ModelRegistry.get_default_model(self.provider)
    
    @classmethod
    def from_cli_args(cls, **kwargs) -> 'CommandConfig':
        """Create configuration from CLI arguments."""
        # Extract provider and model
        # In interactive mode (no query), don't default provider - let user select
        is_interactive = kwargs.get('query') is None
        provider = kwargs.get('provider')
        if not provider and not is_interactive:
            provider = 'ollama'  # Default for non-interactive mode
        model = kwargs.get('model')
        
        # Create provider configs
        provider_configs = {
            'anthropic': ProviderConfig(
                api_key_env='ANTHROPIC_API_KEY',
                default_model='claude-3-5-haiku-20241022'
            ),
            'openai': ProviderConfig(
                api_key_env='OPENAI_API_KEY',
                default_model='gpt-5-mini'
            ),
            'ollama': ProviderConfig(
                default_model='gpt-oss:latest'
            )
        }
        
        # Create teaching config
        teaching = TeachingConfig(
            detail_level=kwargs.get('teaching_detail_level', 'standard'),
            show_alternatives=kwargs.get('show_alternatives', True),
            show_examples=kwargs.get('show_examples', True)
        )
        
        # For non-interactive mode, do NOT default shell - require explicit
        # For interactive mode, shell will be set later via detection/confirmation
        shell = kwargs.get('shell')
        
        return cls(
            provider=provider,
            model=model,
            shell=shell,  # Don't default here - handle in validation
            teach_mode=kwargs.get('teach', False),
            interactive=kwargs.get('query') is None,
            risk_check=not kwargs.get('no_risk_check', False),
            skip_risk_warnings=kwargs.get('skip_risk_warnings', False),
            verbose=kwargs.get('verbose', False),
            auto_copy=kwargs.get('copy', False),
            teaching=teaching,
            provider_configs=provider_configs
        )
    def merge_with_env(self) -> 'CommandConfig':
        """Merge with environment variables."""
        # Load API keys from environment
        for provider_name, provider_config in self.provider_configs.items():
            if provider_config.api_key_env:
                api_key = os.getenv(provider_config.api_key_env)
                if api_key:
                    provider_config.api_key = api_key
        
        return self
    
    def get_provider_config(self, provider_name: str) -> ProviderConfig:
        """Get configuration for a specific provider."""
        return self.provider_configs.get(provider_name, ProviderConfig())
    
    def get_api_key(self, provider_name: str) -> Optional[str]:
        """Get API key for a provider."""
        provider_config = self.get_provider_config(provider_name)
        
        # First try explicit API key
        if provider_config.api_key:
            return provider_config.api_key
        
        # Then try environment variable
        if provider_config.api_key_env:
            return os.getenv(provider_config.api_key_env)
        
        return None
    
    def validate(self) -> None:
        """Validate the configuration."""
        # Skip validation in interactive mode if provider not yet selected
        if self.interactive and not self.provider:
            return
        
        # Teaching mode validation - teaching mode trumps other options
        if self.teach_mode:
            conflicts = []
            
            if self.verbose:
                conflicts.append("--verbose (teaching mode is already comprehensive)")
            
            if not self.risk_check:
                conflicts.append("--no-risk-check (teaching mode requires risk assessment for educational purposes)")
            
            if self.skip_risk_warnings:
                conflicts.append("--skip-risk-warnings (teaching mode is educational, not for automation)")
            
            if conflicts:
                raise ValueError(
                    f"Teaching mode (--teach) cannot be used with: {', '.join(conflicts)}\n\n"
                    "Teaching mode provides a complete learning experience with full explanations and risk assessment.\n"
                    "Compatible options: --provider, --model, --shell, --copy, --query\n\n"
                    "Examples:\n"
                    "  ai-shell --teach -q 'find large files'\n"
                    "  ai-shell --teach -p openai -s bash -q 'delete temp files'\n"
                    "  ai-shell --teach --copy -q 'compress directory'"
                )
        
        # Risk check options validation - mutually exclusive
        if not self.risk_check and self.skip_risk_warnings:
            raise ValueError(
                "Options --no-risk-check and --skip-risk-warnings cannot be used together\n\n"
                "--no-risk-check: Disables risk assessment entirely (no API call, faster)\n"
                "--skip-risk-warnings: Performs risk assessment but proceeds regardless of warnings\n\n"
                "Choose one based on your needs:\n"
                "  Use --no-risk-check if you want to skip risk assessment completely\n"
                "  Use --skip-risk-warnings if you want to assess risk but proceed anyway"
            )
        
        # Validate shell - CRITICAL for non-interactive mode
        if not self.interactive and not self.shell:
            raise ValueError(
                "Shell must be specified in non-interactive mode for safety.\n"
                "Use one of: -s bash, -s powershell, -s cmd\n\n"
                "Examples:\n"
                "  ai-shell -s bash -q 'find large files'\n"
                "  ai-shell -s powershell -q 'find large files'\n"
                "  ai-shell -s cmd -q 'list files'"
            )
        
        # Validate shell value if provided
        if self.shell and self.shell not in ['bash', 'cmd', 'powershell']:
            raise ValueError(f"Invalid shell: {self.shell}. Must be one of: bash, cmd, powershell")
        
        # Validate provider
        from ai_shell_command_generator.providers.models import ModelRegistry
        if self.provider not in ModelRegistry.get_available_providers():
            raise ValueError(f"Unknown provider: {self.provider}")
        
        # Validate model for provider
        if self.model and not ModelRegistry.is_valid_model(self.provider, self.model):
            raise ValueError(f"Invalid model '{self.model}' for provider '{self.provider}'")
        
        # Validate API key for cloud providers (only in non-interactive mode)
        if not self.interactive and self.provider in ['anthropic', 'openai']:
            api_key = self.get_api_key(self.provider)
            if not api_key:
                raise ValueError(f"API key required for {self.provider} provider")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'provider': self.provider,
            'model': self.model,
            'shell': self.shell,
            'os_type': self.os_type,
            'teach_mode': self.teach_mode,
            'interactive': self.interactive,
            'risk_check': self.risk_check,
            'auto_copy': self.auto_copy,
            'teaching': {
                'detail_level': self.teaching.detail_level,
                'show_alternatives': self.teaching.show_alternatives,
                'show_examples': self.teaching.show_examples
            }
        }
