"""Base framework adapter interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class FrameworkAdapter(ABC):
    """Base class for framework-specific adapters."""
    
    @abstractmethod
    def convert(self, test_json: Dict[str, Any]) -> str:
        """
        Convert a test JSON object to framework-specific format.
        
        Args:
            test_json: The validated test JSON object
            
        Returns:
            String representation in the target framework format
        """
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Get the file extension for this framework.
        
        Returns:
            File extension including the dot (e.g., '.json', '.cy.js')
        """
        pass
    
    @property
    @abstractmethod
    def framework_name(self) -> str:
        """Name of the framework."""
        pass
