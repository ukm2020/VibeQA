"""Schema definitions and validation for VibeQA Generator."""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
import re


class Environment(BaseModel):
    """Environment configuration for test execution."""
    app_type: str = Field(default="web", pattern="^web$")
    base_url: str = Field(..., min_length=1)


class Variable(BaseModel):
    """Test variable definition."""
    name: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)


class TestStep(BaseModel):
    """Individual test step with action and expected result."""
    action: str = Field(..., min_length=1)
    target: Optional[str] = None
    selector_type: Optional[str] = None
    selector: Optional[str] = None
    value: Optional[str] = None
    timeout_seconds: Optional[int] = None
    match: Optional[str] = None
    expected_result: str = Field(..., min_length=1)

    @validator('selector_type')
    def validate_selector_type(cls, v, values):
        """Ensure selector_type is 'css' when selector is present."""
        if 'selector' in values and values['selector'] is not None:
            if v != 'css':
                raise ValueError("selector_type must be 'css' when selector is present")
        return v

    @validator('action')
    def validate_action(cls, v):
        """Ensure action is one of the allowed values."""
        allowed_actions = {
            'navigate', 'wait_for_element', 'type', 'click',
            'assert_element_text', 'assert_element_visible',
            'assert_no_navigation', 'open_new_tab', 'switch_to_new_tab'
        }
        if v not in allowed_actions:
            raise ValueError(f"action must be one of: {', '.join(sorted(allowed_actions))}")
        return v

    @validator('match')
    def validate_match(cls, v, values):
        """Validate match field for assert_element_text actions."""
        if values.get('action') == 'assert_element_text':
            if v not in ['equals', 'contains', 'regex']:
                raise ValueError("match must be 'equals', 'contains', or 'regex' for assert_element_text")
        return v


class RainforestTest(BaseModel):
    """Complete Rainforest test specification."""
    schema_version: str = Field(default="rf-1.0", pattern="^rf-1\.0$")
    title: str = Field(..., min_length=5, max_length=120)
    description: str = Field(..., min_length=20, max_length=400)
    tags: List[str] = Field(..., min_items=1)
    environment: Environment
    variables: Optional[List[Variable]] = None
    steps: List[TestStep] = Field(..., min_items=4, max_items=12)
    final_result: str = Field(..., min_length=1)
    design_decisions: str = Field(..., min_length=1)

    @validator('tags')
    def validate_tags(cls, v):
        """Ensure tags are kebab-case."""
        kebab_pattern = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
        for tag in v:
            if not kebab_pattern.match(tag):
                raise ValueError(f"Tag '{tag}' must be kebab-case (lowercase, hyphens only)")
        return v

    @validator('design_decisions')
    def validate_design_decisions_length(cls, v):
        """Ensure design_decisions is <= 5 sentences."""
        sentences = v.count('.') + v.count('!') + v.count('?')
        if sentences > 5:
            raise ValueError("design_decisions must be <= 5 sentences")
        return v

    def validate_variables_usage(self) -> List[str]:
        """Validate that all {{variable}} references are declared."""
        errors = []
        declared_vars = set()
        if self.variables:
            declared_vars = {var.name for var in self.variables}

        # Find all {{variable}} references in steps
        var_pattern = re.compile(r'\{\{(\w+)\}\}')
        for i, step in enumerate(self.steps):
            for field_name, field_value in step.dict().items():
                if isinstance(field_value, str):
                    matches = var_pattern.findall(field_value)
                    for var_name in matches:
                        if var_name not in declared_vars:
                            errors.append(
                                f"Step {i+1}: Variable '{var_name}' used but not declared"
                            )
        return errors


ALLOWED_ACTIONS = {
    'navigate': ['target', 'expected_result'],
    'wait_for_element': ['selector_type', 'selector', 'timeout_seconds', 'expected_result'],
    'type': ['selector_type', 'selector', 'value', 'expected_result'],
    'click': ['selector_type', 'selector', 'expected_result'],
    'assert_element_text': ['selector_type', 'selector', 'match', 'value', 'expected_result'],
    'assert_element_visible': ['selector_type', 'selector', 'expected_result'],
    'assert_no_navigation': ['expected_result'],
    'open_new_tab': ['target', 'expected_result'],
    'switch_to_new_tab': ['expected_result'],
}

