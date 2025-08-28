"""Unit tests for framework adapters."""

import pytest
import json
from typing import Dict, Any

from src.frameworks.registry import get_adapter, get_available_frameworks, FRAMEWORK_ADAPTERS
from src.frameworks.rainforest import RainforestAdapter
from src.frameworks.cypress import CypressAdapter
from src.frameworks.gherkin import GherkinAdapter


class TestFrameworkRegistry:
    """Tests for framework registry."""
    
    def test_get_available_frameworks(self):
        """Test getting available frameworks."""
        frameworks = get_available_frameworks()
        assert isinstance(frameworks, list)
        assert 'rainforest' in frameworks
        assert 'cypress' in frameworks
        assert 'gherkin' in frameworks
    
    def test_get_adapter_valid_framework(self):
        """Test getting adapter for valid framework."""
        adapter = get_adapter('rainforest')
        assert isinstance(adapter, RainforestAdapter)
        
        adapter = get_adapter('cypress')
        assert isinstance(adapter, CypressAdapter)
        
        adapter = get_adapter('gherkin')
        assert isinstance(adapter, GherkinAdapter)
    
    def test_get_adapter_invalid_framework(self):
        """Test getting adapter for invalid framework."""
        with pytest.raises(ValueError, match="Unsupported framework"):
            get_adapter('invalid_framework')


class TestRainforestAdapter:
    """Tests for Rainforest adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create adapter instance."""
        return RainforestAdapter()
    
    @pytest.fixture
    def sample_test_json(self) -> Dict[str, Any]:
        """Sample test JSON."""
        return {
            "schema_version": "rf-1.0",
            "title": "Sample test",
            "description": "This is a sample test for adapter testing purposes.",
            "tags": ["test", "sample"],
            "environment": {
                "app_type": "web",
                "base_url": "https://example.com"
            },
            "steps": [
                {
                    "action": "navigate",
                    "target": "/login",
                    "expected_result": "Login page loads"
                }
            ],
            "final_result": "Test completes",
            "design_decisions": "Simple test for validation."
        }
    
    def test_framework_name(self, adapter):
        """Test framework name."""
        assert adapter.framework_name == "rainforest"
    
    def test_file_extension(self, adapter):
        """Test file extension."""
        assert adapter.get_file_extension() == ".json"
    
    def test_convert(self, adapter, sample_test_json):
        """Test conversion to Rainforest format."""
        result = adapter.convert(sample_test_json)
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == sample_test_json
        
        # Should be pretty-printed
        assert '\n' in result
        assert '  ' in result  # Indentation


class TestCypressAdapter:
    """Tests for Cypress adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create adapter instance."""
        return CypressAdapter()
    
    @pytest.fixture
    def sample_test_json(self) -> Dict[str, Any]:
        """Sample test JSON with various step types."""
        return {
            "schema_version": "rf-1.0",
            "title": "Cypress test sample",
            "description": "This is a sample test for Cypress adapter testing.",
            "tags": ["test", "cypress"],
            "environment": {
                "app_type": "web",
                "base_url": "https://example.com"
            },
            "variables": [
                {"name": "testEmail", "value": "test@example.com"}
            ],
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
                    "action": "assert_element_text",
                    "selector_type": "css",
                    "selector": "[data-test='message']",
                    "match": "contains",
                    "value": "success",
                    "expected_result": "Success message is shown"
                }
            ],
            "final_result": "User logs in successfully",
            "design_decisions": "Test covers main login flow."
        }
    
    def test_framework_name(self, adapter):
        """Test framework name."""
        assert adapter.framework_name == "cypress"
    
    def test_file_extension(self, adapter):
        """Test file extension."""
        assert adapter.get_file_extension() == ".cy.js"
    
    def test_convert(self, adapter, sample_test_json):
        """Test conversion to Cypress format."""
        result = adapter.convert(sample_test_json)
        
        # Should contain Cypress-specific elements
        assert "describe(" in result
        assert "it(" in result
        assert "cy.visit(" in result
        assert "cy.get(" in result
        assert "cy.type(" in result
        assert ".click()" in result
        assert ".should(" in result
        
        # Should include variables
        assert "testEmail" in result
        
        # Should include comments
        assert "Generated by VibeQA Generator" in result
        assert "Step 1:" in result


class TestGherkinAdapter:
    """Tests for Gherkin adapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create adapter instance."""
        return GherkinAdapter()
    
    @pytest.fixture
    def sample_test_json(self) -> Dict[str, Any]:
        """Sample test JSON for Gherkin testing."""
        return {
            "schema_version": "rf-1.0",
            "title": "Gherkin test sample",
            "description": "This is a sample test for Gherkin adapter testing.",
            "tags": ["test", "gherkin", "bdd"],
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
            "final_result": "User successfully logs in and sees dashboard",
            "design_decisions": "Standard login flow with assertions."
        }
    
    def test_framework_name(self, adapter):
        """Test framework name."""
        assert adapter.framework_name == "gherkin"
    
    def test_file_extension(self, adapter):
        """Test file extension."""
        assert adapter.get_file_extension() == ".feature"
    
    def test_convert(self, adapter, sample_test_json):
        """Test conversion to Gherkin format."""
        result = adapter.convert(sample_test_json)
        
        # Should contain Gherkin-specific elements
        assert "Feature:" in result
        assert "Scenario:" in result
        assert "Background:" in result
        assert "Given" in result
        assert "When" in result
        assert "Then" in result
        
        # Should include tags
        assert "@test" in result
        assert "@gherkin" in result
        assert "@bdd" in result
        
        # Should include base URL in background
        assert "https://example.com" in result
    
    def test_step_conversion(self, adapter):
        """Test individual step conversion."""
        # Test navigate step
        step = {
            "action": "navigate",
            "target": "/login",
            "expected_result": "Login page loads"
        }
        result = adapter._convert_single_step(step, "Given")
        assert 'I navigate to "/login"' in result
        
        # Test type step
        step = {
            "action": "type",
            "selector_type": "css",
            "selector": "[data-test='email']",
            "value": "test@example.com",
            "expected_result": "Email is entered"
        }
        result = adapter._convert_single_step(step, "When")
        assert 'I type "test@example.com" into "[data-test=\'email\']"' in result
        
        # Test assertion step
        step = {
            "action": "assert_element_visible",
            "selector_type": "css",
            "selector": "[data-test='dashboard']",
            "expected_result": "Dashboard is visible"
        }
        result = adapter._convert_single_step(step, "Then")
        assert 'the element "[data-test=\'dashboard\']" should be visible' in result


if __name__ == '__main__':
    pytest.main([__file__])

