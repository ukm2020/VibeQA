#!/usr/bin/env python3
"""Test runner for VibeQA Generator."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str) -> bool:
    """Run a command and return success status."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0


def main():
    """Run all tests and checks."""
    print("🧪 Running VibeQA Generator Test Suite")
    print("=" * 50)
    
    success = True
    
    # Run unit tests
    print("\n1. Running unit tests...")
    if not run_command("python -m pytest tests/ -v"):
        success = False
        print("❌ Unit tests failed")
    else:
        print("✅ Unit tests passed")
    
    # Test imports
    print("\n2. Testing imports...")
    try:
        from src.core import create_engine, TestValidator
        from src.frameworks.registry import get_adapter
        from src.cli import main
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        success = False
    
    # Test validator with sample data
    print("\n3. Testing validator...")
    try:
        from src.core.validator import validate_test_json
        
        sample_test = {
            "schema_version": "rf-1.0",
            "title": "Test validation",
            "description": "This is a test for validator functionality",
            "tags": ["test"],
            "environment": {"app_type": "web", "base_url": "https://example.com"},
            "steps": [
                {"action": "navigate", "target": "/", "expected_result": "Page loads"},
                {"action": "click", "selector_type": "css", "selector": "[data-test='btn']", "expected_result": "Button clicked"},
                {"action": "assert_element_visible", "selector_type": "css", "selector": "[data-test='result']", "expected_result": "Result shown"},
                {"action": "assert_element_text", "selector_type": "css", "selector": "[data-test='msg']", "match": "contains", "value": "success", "expected_result": "Success message"}
            ],
            "final_result": "Test passes",
            "design_decisions": "Simple test case."
        }
        
        result = validate_test_json(sample_test)
        if result.success:
            print("✅ Validator test passed")
        else:
            print(f"❌ Validator test failed: {result.errors}")
            success = False
    except Exception as e:
        print(f"❌ Validator test error: {e}")
        success = False
    
    # Test framework adapters
    print("\n4. Testing framework adapters...")
    try:
        from src.frameworks.registry import get_adapter, get_available_frameworks
        
        frameworks = get_available_frameworks()
        print(f"Available frameworks: {frameworks}")
        
        for framework in frameworks:
            adapter = get_adapter(framework)
            print(f"✅ {framework} adapter loaded: {adapter.__class__.__name__}")
            
    except Exception as e:
        print(f"❌ Framework adapter test failed: {e}")
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())

