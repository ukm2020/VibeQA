"""Rainforest AI prompt adapter for human-language test generation."""

from typing import Dict, Any
from .base import FrameworkAdapter


class RainforestPromptAdapter(FrameworkAdapter):
    """Adapter for Rainforest AI prompt format (human-readable)."""
    
    @property
    def framework_name(self) -> str:
        return "rainforest-prompt"
    
    def get_file_extension(self) -> str:
        return ".txt"
    
    def convert(self, test_json: Dict[str, Any]) -> str:
        """
        Convert test JSON to simplified Rainforest AI prompt.
        
        This generates a concise, simplified prompt optimized for Rainforest's
        AI limitations (max 5-6 steps, simplified language).
        
        Args:
            test_json: The validated test JSON object
            
        Returns:
            Simplified prompt string for Rainforest AI
        """
        title = test_json['title']
        description = test_json['description']
        steps = test_json['steps']
        base_url = test_json['environment']['base_url']
        final_result = test_json['final_result']
        
        # Simplify and consolidate steps for Rainforest AI limitations
        simplified_steps = self._consolidate_steps(steps)
        
        # Start building the simplified prompt
        prompt_parts = []
        
        # Concise test description
        prompt_parts.append(f"Create a test: {title}")
        prompt_parts.append(f"Goal: {final_result}")
        prompt_parts.append(f"Site: {base_url}")
        prompt_parts.append("")
        
        # Simplified steps (max 5-6)
        prompt_parts.append("Steps:")
        for i, step_desc in enumerate(simplified_steps, 1):
            prompt_parts.append(f"{i}. {step_desc}")
        
        prompt_parts.append("")
        
        # Simple guidance for Rainforest AI
        prompt_parts.append("Use data-test selectors when possible.")
        prompt_parts.append("Include clear validation for each step.")
        
        return "\n".join(prompt_parts)
    
    def _consolidate_steps(self, steps: list) -> list:
        """
        Consolidate detailed steps into simplified ones for Rainforest AI.
        
        Combines related actions and reduces step count to 4-6 steps maximum.
        """
        consolidated = []
        i = 0
        
        while i < len(steps):
            current_step = steps[i]
            action = current_step['action']
            
            # Group navigation and initial waits
            if action == 'navigate':
                nav_desc = f"Go to {current_step.get('target', 'the application')}"
                # Look ahead for wait_for_element after navigate
                if i + 1 < len(steps) and steps[i + 1]['action'] == 'wait_for_element':
                    i += 1  # Skip the wait step, it's implied
                consolidated.append(nav_desc)
                
            # Group form filling (type actions)
            elif action == 'type':
                form_actions = []
                while i < len(steps) and steps[i]['action'] == 'type':
                    step = steps[i]
                    field_name = self._extract_field_name(step.get('selector', ''))
                    value = step.get('value', 'data')
                    form_actions.append(f"enter '{value}' in {field_name}")
                    i += 1
                i -= 1  # Back up one since we'll increment at end of loop
                
                if len(form_actions) == 1:
                    consolidated.append(f"Fill form: {form_actions[0]}")
                else:
                    consolidated.append(f"Fill form: {', '.join(form_actions)}")
                    
            # Group clicks and submissions
            elif action == 'click':
                element_name = self._extract_field_name(current_step.get('selector', 'button'))
                consolidated.append(f"Click {element_name}")
                
            # Group assertions and validations
            elif action in ['assert_element_text', 'assert_element_visible', 'wait_for_element']:
                if action == 'wait_for_element':
                    element_name = self._extract_field_name(current_step.get('selector', 'element'))
                    consolidated.append(f"Wait for {element_name} to appear")
                elif action == 'assert_element_text':
                    text = current_step.get('value', 'expected text')
                    consolidated.append(f"Verify error message contains '{text}'")
                elif action == 'assert_element_visible':
                    element_name = self._extract_field_name(current_step.get('selector', 'element'))
                    consolidated.append(f"Confirm {element_name} is visible")
                    
            # Skip redundant waits that follow other actions
            elif action == 'wait_for_element' and i > 0:
                # Skip if this is just waiting for something we just interacted with
                pass
            else:
                # Fallback for other actions
                consolidated.append(current_step.get('expected_result', 'Perform action'))
            
            i += 1
            
            # Limit to 6 steps maximum for Rainforest AI
            if len(consolidated) >= 6:
                break
        
        return consolidated[:6]  # Ensure max 6 steps
    
    def _extract_field_name(self, selector: str) -> str:
        """Extract a human-readable field name from a CSS selector."""
        if not selector:
            return "element"
            
        # Extract from data-test attributes
        if 'data-test=' in selector:
            # Extract the data-test value
            start = selector.find("data-test='") + len("data-test='")
            if start > len("data-test='") - 1:
                end = selector.find("'", start)
                if end > start:
                    test_name = selector[start:end]
                    # Convert kebab-case to readable name
                    return test_name.replace('-', ' ').replace('_', ' ')
        
        # Fallback extractions
        if 'login' in selector.lower():
            return "login button"
        elif 'submit' in selector.lower():
            return "submit button"
        elif 'email' in selector.lower():
            return "email field"
        elif 'password' in selector.lower():
            return "password field"
        elif 'error' in selector.lower():
            return "error message"
        elif 'button' in selector.lower():
            return "button"
        elif 'input' in selector.lower():
            return "input field"
        else:
            return "element"
    
    def _convert_step_to_human_language(self, step: Dict[str, Any], step_number: int) -> str:
        """Convert a JSON step to human-readable language."""
        action = step['action']
        expected_result = step['expected_result']
        
        if action == 'navigate':
            target = step['target']
            return f"Navigate to '{target}' and verify {expected_result.lower()}"
            
        elif action == 'wait_for_element':
            selector = step['selector']
            timeout = step.get('timeout_seconds', 10)
            return f"Wait up to {timeout} seconds for element '{selector}' to appear, confirming {expected_result.lower()}"
            
        elif action == 'type':
            selector = step['selector']
            value = step['value']
            return f"Enter '{value}' into the field '{selector}' and verify {expected_result.lower()}"
            
        elif action == 'click':
            selector = step['selector']
            return f"Click on element '{selector}' and confirm {expected_result.lower()}"
            
        elif action == 'assert_element_text':
            selector = step['selector']
            match_type = step['match']
            value = step['value']
            
            if match_type == 'equals':
                return f"Verify that element '{selector}' displays exactly '{value}' and {expected_result.lower()}"
            elif match_type == 'contains':
                return f"Check that element '{selector}' contains the text '{value}' and {expected_result.lower()}"
            elif match_type == 'regex':
                return f"Validate that element '{selector}' matches the pattern '{value}' and {expected_result.lower()}"
                
        elif action == 'assert_element_visible':
            selector = step['selector']
            return f"Confirm that element '{selector}' is visible on the page and {expected_result.lower()}"
            
        elif action == 'assert_no_navigation':
            return f"Verify that the page does not navigate away and {expected_result.lower()}"
            
        elif action == 'open_new_tab':
            target = step['target']
            return f"Open '{target}' in a new browser tab and verify {expected_result.lower()}"
            
        elif action == 'switch_to_new_tab':
            return f"Switch focus to the newly opened tab and confirm {expected_result.lower()}"
        
        # Fallback to expected result
        return f"Perform action and verify {expected_result.lower()}"
