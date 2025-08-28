"""Gherkin framework adapter."""

from typing import Dict, Any, List
from .base import FrameworkAdapter


class GherkinAdapter(FrameworkAdapter):
    """Adapter for Gherkin/Cucumber feature format."""
    
    @property
    def framework_name(self) -> str:
        return "gherkin"
    
    def get_file_extension(self) -> str:
        return ".feature"
    
    def convert(self, test_json: Dict[str, Any]) -> str:
        """
        Convert test JSON to Gherkin format.
        
        Args:
            test_json: The validated test JSON object
            
        Returns:
            Gherkin feature file content
        """
        title = test_json['title']
        description = test_json['description']
        tags = test_json['tags']
        steps = test_json['steps']
        final_result = test_json['final_result']
        base_url = test_json['environment']['base_url']
        
        # Start building the feature file
        lines = []
        
        # Add tags
        if tags:
            tag_line = " ".join(f"@{tag}" for tag in tags)
            lines.append(tag_line)
        
        lines.extend([
            f"Feature: {title}",
            f"  {description}",
            "",
            f"  Background:",
            f"    Given the application is running at \"{base_url}\"",
            "",
            f"  Scenario: {title}",
        ])
        
        # Convert steps to Given/When/Then format
        gherkin_steps = self._convert_steps_to_gherkin(steps, final_result)
        for step in gherkin_steps:
            lines.append(f"    {step}")
        
        return "\n".join(lines)
    
    def _convert_steps_to_gherkin(self, steps: List[Dict[str, Any]], final_result: str) -> List[str]:
        """Convert test steps to Gherkin Given/When/Then format."""
        gherkin_steps = []
        
        # Determine step types based on position and action
        for i, step in enumerate(steps):
            action = step['action']
            expected_result = step['expected_result']
            
            if i == 0:
                keyword = "Given"
            elif self._is_assertion(action):
                keyword = "Then"
            else:
                keyword = "When"
            
            gherkin_step = self._convert_single_step(step, keyword)
            gherkin_steps.append(gherkin_step)
        
        # Add final result as the last Then step if not already covered
        if not any(step.startswith("Then") for step in gherkin_steps[-2:]):
            gherkin_steps.append(f"Then {final_result}")
        
        return gherkin_steps
    
    def _is_assertion(self, action: str) -> bool:
        """Check if an action is an assertion."""
        assertion_actions = {
            'assert_element_text', 'assert_element_visible', 'assert_no_navigation'
        }
        return action in assertion_actions
    
    def _convert_single_step(self, step: Dict[str, Any], keyword: str) -> str:
        """Convert a single step to Gherkin format."""
        action = step['action']
        expected_result = step['expected_result']
        
        if action == 'navigate':
            target = step['target']
            return f"{keyword} I navigate to \"{target}\""
            
        elif action == 'wait_for_element':
            selector = step['selector']
            timeout = step.get('timeout_seconds', 10)
            return f"{keyword} I wait {timeout} seconds for element \"{selector}\" to appear"
            
        elif action == 'type':
            selector = step['selector']
            value = step['value']
            return f"{keyword} I type \"{value}\" into \"{selector}\""
            
        elif action == 'click':
            selector = step['selector']
            return f"{keyword} I click on \"{selector}\""
            
        elif action == 'assert_element_text':
            selector = step['selector']
            match_type = step['match']
            value = step['value']
            
            if match_type == 'equals':
                return f"{keyword} the element \"{selector}\" should have text \"{value}\""
            elif match_type == 'contains':
                return f"{keyword} the element \"{selector}\" should contain text \"{value}\""
            elif match_type == 'regex':
                return f"{keyword} the element \"{selector}\" should match pattern \"{value}\""
                
        elif action == 'assert_element_visible':
            selector = step['selector']
            return f"{keyword} the element \"{selector}\" should be visible"
            
        elif action == 'assert_no_navigation':
            return f"{keyword} I should remain on the current page"
            
        elif action == 'open_new_tab':
            target = step['target']
            return f"{keyword} I open \"{target}\" in a new tab"
            
        elif action == 'switch_to_new_tab':
            return f"{keyword} I switch to the new tab"
        
        # Fallback to expected result
        return f"{keyword} {expected_result.lower()}"

