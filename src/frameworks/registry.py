"""Framework adapter registry."""

from typing import Dict, Type, List
from .base import FrameworkAdapter
from .rainforest import RainforestAdapter
from .rainforest_prompt import RainforestPromptAdapter
from .rainforest_simple import RainforestSimpleAdapter
from .cypress import CypressAdapter
from .gherkin import GherkinAdapter


# Registry of available framework adapters
FRAMEWORK_ADAPTERS: Dict[str, Type[FrameworkAdapter]] = {
    'rainforest': RainforestAdapter,
    'rainforest-prompt': RainforestPromptAdapter,
    'rainforest-simple': RainforestSimpleAdapter,
    'cypress': CypressAdapter,
    'gherkin': GherkinAdapter,
}


def get_adapter(framework: str) -> FrameworkAdapter:
    """
    Get a framework adapter instance.
    
    Args:
        framework: Name of the framework
        
    Returns:
        Framework adapter instance
        
    Raises:
        ValueError: If framework is not supported
    """
    if framework not in FRAMEWORK_ADAPTERS:
        available = ', '.join(sorted(FRAMEWORK_ADAPTERS.keys()))
        raise ValueError(f"Unsupported framework '{framework}'. Available: {available}")
    
    adapter_class = FRAMEWORK_ADAPTERS[framework]
    return adapter_class()


def get_available_frameworks() -> List[str]:
    """Get list of available framework names."""
    return sorted(FRAMEWORK_ADAPTERS.keys())
