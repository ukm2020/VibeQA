"""Rainforest framework adapter."""

import json
from typing import Dict, Any

from .base import FrameworkAdapter


class RainforestAdapter(FrameworkAdapter):
    """Adapter for Rainforest QA JSON format."""
    
    @property
    def framework_name(self) -> str:
        return "rainforest"
    
    def get_file_extension(self) -> str:
        return ".json"
    
    def convert(self, test_json: Dict[str, Any]) -> str:
        """
        Convert test JSON to Rainforest format.
        
        For Rainforest, we return the JSON as-is since it's already in the correct format.
        
        Args:
            test_json: The validated test JSON object
            
        Returns:
            Pretty-printed JSON string
        """
        return json.dumps(test_json, indent=2, ensure_ascii=False)

