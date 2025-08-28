"""Unit tests for the validator module."""

import pytest
import json
from typing import Dict, Any

from src.core.validator import TestValidator, ValidationResult, validate_test_json


class TestValidationResult:
    """Tests for ValidationResult class."""
    
    def test_initialization(self):
        """Test ValidationResult initialization."""
        result = ValidationResult(True)
        assert result.success is True
        assert result.errors == []
        assert result.warnings == []
    
    def test_add_error(self):
        """Test adding errors."""
        result = ValidationResult(True)
        result.add_error("Test error")
        assert result.success is False
        assert "Test error" in result.errors
    
    def test_add_warning(self):
        """Test adding warnings."""
        result = ValidationResult(True)
        result.add_warning("Test warning")
        assert result.success is True  # Warnings don't affect success
        assert "Test warning" in result.warnings


class TestTestValidator:
    """Tests for TestValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return TestValidator()
    
    @pytest.fixture
    def valid_test_json(self) -> Dict[str, Any]:
        """Valid test JSON fixture."""
        return {
            "schema_version": "rf-1.0",
            "title": "Valid test scenario",
            "description": "This is a valid test description that meets the minimum length requirement.",
            "tags": ["auth", "positive"],
            "environment": {
                "app_type": "web",
                "base_url": "https://example.com"
            },
            "steps": [
                {
                    "action": "navigate",
                    "target": "/login",
                    "expected_result": "Login page loads"
                },
                {
                    "action": "type",
                    "selector_type": "css",
                    "selector": "[data-test='email']",
                    "value": "test@example.com",
                    "expected_result": "Email is entered"
                },
                {
                    "action": "click",
                    "selector_type": "css",
                    "selector": "[data-test='submit']",
                    "expected_result": "Form is submitted"
                },
                {
                    "action": "assert_element_visible",
                    "selector_type": "css",
                    "selector": "[data-test='dashboard']",
                    "expected_result": "Dashboard is visible"
                }
            ],
            "final_result": "User successfully logs in",
            "design_decisions": "Used data-test selectors for reliability."
        }
    
    def test_valid_fixture_passes_validation(self, validator, valid_test_json):
        """Test that valid fixture passes validation."""
        _, result = validator._validate_parsed_json(valid_test_json, ValidationResult(True))
        assert result.success is True
        assert len(result.errors) == 0
    
    def test_missing_field_fails(self, validator, valid_test_json):
        """Test that missing required field fails validation."""
        # Remove required field
        del valid_test_json['title']
        
        _, result = validator._validate_parsed_json(valid_test_json, ValidationResult(True))
        assert result.success is False
        assert any("title" in error for error in result.errors)
    
    def test_unknown_action_fails(self, validator, valid_test_json):
        """Test that unknown action fails validation."""
        valid_test_json['steps'][0]['action'] = 'unknown_action'
        
        _, result = validator._validate_parsed_json(valid_test_json, ValidationResult(True))
        assert result.success is False
        assert any("unknown_action" in error for error in result.errors)
    
    def test_selector_type_required_when_selector_present(self, validator, valid_test_json):
        """Test that selector_type is required when selector is present."""
        # Remove selector_type but keep selector
        del valid_test_json['steps'][1]['selector_type']
        
        _, result = validator._validate_parsed_json(valid_test_json, ValidationResult(True))
        assert result.success is False
        assert any("selector_type" in error for error in result.errors)
    
    def test_steps_length_validation(self, validator, valid_test_json):
        """Test that steps length is validated."""
        # Too few steps
        valid_test_json['steps'] = valid_test_json['steps'][:2]
        
        _, result = validator._validate_parsed_json(valid_test_json, ValidationResult(True))
        assert result.success is False
        assert any("min_items" in error or "4" in error for error in result.errors)
    
    def test_strip_code_fences(self, validator):
        """Test stripping of code fences."""
        json_with_fences = '```json\n{"test": "value"}\n```'
        cleaned = validator._strip_code_fences(json_with_fences)
        assert cleaned == '{"test": "value"}'
        
        json_with_basic_fences = '```\n{"test": "value"}\n```'
        cleaned = validator._strip_code_fences(json_with_basic_fences)
        assert cleaned == '{"test": "value"}'
    
    def test_validate_raw_response_valid_json(self, validator, valid_test_json):
        """Test validation of raw response with valid JSON."""
        raw_response = json.dumps(valid_test_json)
        parsed, result = validator.validate_raw_response(raw_response)
        
        assert parsed is not None
        assert result.success is True
    
    def test_validate_raw_response_invalid_json(self, validator):
        """Test validation of raw response with invalid JSON."""
        raw_response = '{"invalid": json}'
        parsed, result = validator.validate_raw_response(raw_response)
        
        assert parsed is None
        assert result.success is False
        assert any("Invalid JSON" in error for error in result.errors)
    
    def test_variable_usage_validation(self, validator, valid_test_json):
        """Test validation of variable usage."""
        # Add a step that uses an undeclared variable
        valid_test_json['steps'][1]['value'] = 'test+{{undeclared_var}}@example.com'
        
        _, result = validator._validate_parsed_json(valid_test_json, ValidationResult(True))
        assert result.success is False
        assert any("undeclared_var" in error for error in result.errors)
    
    def test_variable_usage_with_declared_variables(self, validator, valid_test_json):
        """Test that declared variables pass validation."""
        # Declare a variable and use it
        valid_test_json['variables'] = [{"name": "test_email", "value": "test@example.com"}]
        valid_test_json['steps'][1]['value'] = '{{test_email}}'
        
        _, result = validator._validate_parsed_json(valid_test_json, ValidationResult(True))
        assert result.success is True
    
    def test_kebab_case_tags(self, validator, valid_test_json):
        """Test that non-kebab-case tags fail validation."""
        valid_test_json['tags'] = ['auth', 'CamelCase']
        
        _, result = validator._validate_parsed_json(valid_test_json, ValidationResult(True))
        assert result.success is False
        assert any("kebab-case" in error for error in result.errors)
    
    def test_design_decisions_length(self, validator, valid_test_json):
        """Test design decisions sentence limit."""
        # Create a string with more than 5 sentences
        long_decisions = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence. Sixth sentence."
        valid_test_json['design_decisions'] = long_decisions
        
        _, result = validator._validate_parsed_json(valid_test_json, ValidationResult(True))
        assert result.success is False
        assert any("5 sentences" in error for error in result.errors)


class TestConvenienceFunction:
    """Tests for the convenience validation function."""
    
    def test_validate_test_json_function(self, valid_test_json):
        """Test the convenience validation function."""
        result = validate_test_json(valid_test_json)
        assert result.success is True
        
        # Test with invalid data
        invalid_json = {"invalid": "data"}
        result = validate_test_json(invalid_json)
        assert result.success is False


if __name__ == '__main__':
    pytest.main([__file__])

