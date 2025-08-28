"""Validation logic for VibeQA Generator outputs."""

import json
import re
from typing import Dict, Any, List, Tuple, Optional
from pydantic import ValidationError

from .schema import RainforestTest, ALLOWED_ACTIONS


class ValidationResult:
    """Result of validation with success status and error details."""
    
    def __init__(self, success: bool, errors: Optional[List[str]] = None, 
                 warnings: Optional[List[str]] = None):
        self.success = success
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)


class TestValidator:
    """Validates generated test JSON against the schema."""
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
    
    def validate_raw_response(self, raw_response: str) -> Tuple[Optional[Dict[Any, Any]], ValidationResult]:
        """
        Parse and validate raw LLM response.
        
        Returns:
            Tuple of (parsed_json, validation_result)
        """
        result = ValidationResult(True)
        
        # Strip code fences if present
        cleaned_response = self._strip_code_fences(raw_response.strip())
        
        # Parse JSON
        try:
            parsed_json = json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            result.add_error(f"Invalid JSON: {str(e)}")
            return None, result
        
        # Validate against schema
        return self._validate_parsed_json(parsed_json, result)
    
    def _strip_code_fences(self, text: str) -> str:
        """Remove markdown code fences from response."""
        # Remove ```json ... ``` or ``` ... ```
        text = re.sub(r'^```(?:json)?\s*\n', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n```\s*$', '', text, flags=re.MULTILINE)
        return text.strip()
    
    def _validate_parsed_json(self, data: Dict[Any, Any], result: ValidationResult) -> Tuple[Optional[Dict[Any, Any]], ValidationResult]:
        """Validate parsed JSON against RainforestTest schema."""
        try:
            # Create RainforestTest instance for validation
            test = RainforestTest(**data)
            
            # Additional custom validations
            self._validate_step_actions(test, result)
            
            # Validate variable usage
            var_errors = test.validate_variables_usage()
            for error in var_errors:
                result.add_error(error)
            
            # Check for unknown fields in strict mode
            if self.strict_mode:
                self._check_unknown_fields(data, result)
            
            return data, result
            
        except ValidationError as e:
            for error in e.errors():
                field_path = " -> ".join(str(loc) for loc in error['loc'])
                result.add_error(f"{field_path}: {error['msg']}")
            return None, result
    
    def _validate_step_actions(self, test: RainforestTest, result: ValidationResult) -> None:
        """Validate that each step has the correct fields for its action."""
        for i, step in enumerate(test.steps):
            action = step.action
            step_dict = step.dict(exclude_none=True)
            
            if action not in ALLOWED_ACTIONS:
                result.add_error(f"Step {i+1}: Unknown action '{action}'")
                continue
            
            required_fields = set(ALLOWED_ACTIONS[action])
            present_fields = set(step_dict.keys())
            
            # Check for missing required fields
            missing_fields = required_fields - present_fields
            if missing_fields:
                result.add_error(
                    f"Step {i+1}: Missing required fields for '{action}': {', '.join(sorted(missing_fields))}"
                )
            
            # In strict mode, check for unexpected fields
            if self.strict_mode:
                unexpected_fields = present_fields - required_fields - {'action'}
                if unexpected_fields:
                    result.add_error(
                        f"Step {i+1}: Unexpected fields for '{action}': {', '.join(sorted(unexpected_fields))}"
                    )
    
    def _check_unknown_fields(self, data: Dict[Any, Any], result: ValidationResult) -> None:
        """Check for unknown fields in strict mode."""
        known_top_level_fields = {
            'schema_version', 'title', 'description', 'tags', 'environment',
            'variables', 'steps', 'final_result', 'design_decisions'
        }
        
        unknown_fields = set(data.keys()) - known_top_level_fields
        if unknown_fields:
            result.add_error(f"Unknown top-level fields: {', '.join(sorted(unknown_fields))}")
    
    def generate_correction_prompt(self, original_response: str, validation_result: ValidationResult) -> str:
        """Generate a correction prompt for failed validation."""
        if not validation_result.errors:
            return ""
        
        error_summary = "; ".join(validation_result.errors[:3])  # Limit to first 3 errors
        return f"You omitted or misformatted: {error_summary}. Return the full JSON object again with all required fields. No prose."


def validate_test_json(json_data: Dict[Any, Any], strict_mode: bool = False) -> ValidationResult:
    """
    Convenience function to validate a test JSON object.
    
    Args:
        json_data: The parsed JSON data to validate
        strict_mode: Whether to enforce strict validation
    
    Returns:
        ValidationResult with success status and any errors
    """
    validator = TestValidator(strict_mode=strict_mode)
    _, result = validator._validate_parsed_json(json_data, ValidationResult(True))
    return result

