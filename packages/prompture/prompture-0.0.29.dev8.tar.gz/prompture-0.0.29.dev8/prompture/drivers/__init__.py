from .openai_driver import OpenAIDriver
from .local_http_driver import LocalHTTPDriver
from .ollama_driver import OllamaDriver
from .claude_driver import ClaudeDriver
from .azure_driver import AzureDriver
from .lmstudio_driver import LMStudioDriver
from .google_driver import GoogleDriver
from .groq_driver import GroqDriver
from .openrouter_driver import OpenRouterDriver
from .grok_driver import GrokDriver
from ..settings import settings


# Central registry: maps provider → factory function
DRIVER_REGISTRY = {
    "openai": lambda model=None: OpenAIDriver(
        api_key=settings.openai_api_key,
        model=model or settings.openai_model
    ),
    "ollama": lambda model=None: OllamaDriver(
        endpoint=settings.ollama_endpoint,
        model=model or settings.ollama_model
    ),
    "claude": lambda model=None: ClaudeDriver(
        api_key=settings.claude_api_key,
        model=model or settings.claude_model
    ),
    "lmstudio": lambda model=None: LMStudioDriver(
        endpoint=settings.lmstudio_endpoint,
        model=model or settings.lmstudio_model
    ),
    "azure": lambda model=None: AzureDriver(
        api_key=settings.azure_api_key,
        endpoint=settings.azure_api_endpoint,
        deployment_id=settings.azure_deployment_id
    ),
    "local_http": lambda model=None: LocalHTTPDriver(
        endpoint=settings.local_http_endpoint,
        model=model
    ),
    "google": lambda model=None: GoogleDriver(
        api_key=settings.google_api_key,
        model=model or settings.google_model
    ),
    "groq": lambda model=None: GroqDriver(
        api_key=settings.groq_api_key,
        model=model or settings.groq_model
    ),
    "openrouter": lambda model=None: OpenRouterDriver(
        api_key=settings.openrouter_api_key,
        model=model or settings.openrouter_model
    ),
    "grok": lambda model=None: GrokDriver(
        api_key=settings.grok_api_key,
        model=model or settings.grok_model
    ),
}


def get_driver(provider_name: str = None):
    """
    Factory to get a driver instance based on the provider name (legacy style).
    Uses default model from settings if not overridden.
    """
    provider = (provider_name or settings.ai_provider or "ollama").strip().lower()
    if provider not in DRIVER_REGISTRY:
        raise ValueError(f"Unknown provider: {provider_name}")
    return DRIVER_REGISTRY[provider]()  # use default model from settings


def get_driver_for_model(model_str: str):
    """
    Factory to get a driver instance based on a full model string.
    Format: provider/model_id
    Example: "openai/gpt-4-turbo-preview"
    
    Args:
        model_str: Model identifier string. Can be either:
                   - Full format: "provider/model" (e.g. "openai/gpt-4")
                   - Provider only: "provider" (e.g. "openai")
    
    Returns:
        A configured driver instance for the specified provider/model.
        
    Raises:
        ValueError: If provider is invalid or format is incorrect.
    """
    if not isinstance(model_str, str):
        raise ValueError("Model string must be a string, got {type(model_str)}")
        
    if not model_str:
        raise ValueError("Model string cannot be empty")

    # Extract provider and model ID
    parts = model_str.split("/", 1)
    provider = parts[0].lower()
    model_id = parts[1] if len(parts) > 1 else None

    # Validate provider
    if provider not in DRIVER_REGISTRY:
        raise ValueError(f"Unsupported provider '{provider}'")
        
    # Create driver with model ID if provided, otherwise use default
    return DRIVER_REGISTRY[provider](model_id)


__all__ = [
    "OpenAIDriver",
    "LocalHTTPDriver",
    "OllamaDriver",
    "ClaudeDriver",
    "LMStudioDriver",
    "AzureDriver",
    "GoogleDriver",
    "GroqDriver",
    "OpenRouterDriver",
    "GrokDriver",
    "get_driver",
    "get_driver_for_model",
]
