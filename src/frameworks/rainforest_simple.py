"""Ultra-simplified Rainforest adapter for basic AI systems."""

from typing import Dict, Any
from .base import FrameworkAdapter


class RainforestSimpleAdapter(FrameworkAdapter):
    """Ultra-simplified adapter for Rainforest AI (maximum 4 steps)."""
    
    @property
    def framework_name(self) -> str:
        return "rainforest-simple"
    
    def get_file_extension(self) -> str:
        return ".txt"
    
    def convert(self, test_json: Dict[str, Any]) -> str:
        """
        Convert test JSON to ultra-simplified Rainforest prompt.
        
        Maximum 4 steps, very basic language, designed for AI systems
        that struggle with complexity.
        
        Args:
            test_json: The validated test JSON object
            
        Returns:
            Ultra-simplified prompt string
        """
        title = test_json['title']
        base_url = test_json['environment']['base_url']
        final_result = test_json['final_result']
        
        # Extract core test flow
        core_steps = self._extract_core_flow(test_json['steps'])
        
        # Build minimal prompt
        prompt = f"""Test: {title}

Site: {base_url}

Steps:
{chr(10).join(f"{i}. {step}" for i, step in enumerate(core_steps, 1))}

Expected: {final_result}"""
        
        return prompt
    
    def _extract_core_flow(self, steps: list) -> list:
        """Extract the absolute core flow (max 4 steps)."""
        core = []
        
        # Find key actions only
        has_navigation = False
        has_form_fill = False
        has_submission = False
        has_validation = False
        
        for step in steps:
            action = step['action']
            
            # 1. Navigation (if present)
            if action == 'navigate' and not has_navigation:
                core.append("Go to the login page")
                has_navigation = True
                
            # 2. Form filling (combine all inputs)
            elif action == 'type' and not has_form_fill:
                core.append("Enter invalid login credentials")
                has_form_fill = True
                
            # 3. Submission
            elif action == 'click' and 'submit' in step.get('selector', '').lower() and not has_submission:
                core.append("Submit the form")
                has_submission = True
                
            # 4. Validation (any assertion)
            elif action.startswith('assert_') and not has_validation:
                if 'text' in action:
                    text = step.get('value', 'error')
                    core.append(f"Check error message contains '{text}'")
                else:
                    core.append("Verify error message appears")
                has_validation = True
                
            # Stop at 4 steps
            if len(core) >= 4:
                break
        
        # Ensure we have at least the basics
        if not has_navigation:
            core.insert(0, "Go to the application")
        if not has_validation and len(core) < 4:
            core.append("Verify error is shown")
            
        return core[:4]  # Absolute max 4 steps

