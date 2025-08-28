#!/usr/bin/env python3
"""
Test script that demonstrates VibeQA Generator with API key.
Run this after setting OPENAI_API_KEY in your environment.
"""

import os
import sys
from pathlib import Path

def test_api_key():
    """Check if API key is available."""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        print("\nTo set it in PowerShell:")
        print("  $env:OPENAI_API_KEY = 'your-api-key-here'")
        print("\nTo set it permanently in Windows:")
        print("  setx OPENAI_API_KEY 'your-api-key-here'")
        print("  (then restart your terminal)")
        return False
    
    print(f"✅ API key found (starts with: {api_key[:10]}...)")
    return True

def test_generation():
    """Test the generation functionality."""
    print("\n🧪 Testing VibeQA Generation...")
    
    try:
        from src.core import create_engine
        from src.frameworks.registry import get_adapter
        
        # Simple test scenario
        scenario = "Login with valid email and password"
        
        print(f"📝 Scenario: {scenario}")
        print("🔄 Generating Rainforest test...")
        
        # Create engine and generate
        engine = create_engine(temperature=0.2)
        test_json = engine.generate_test(
            scenario=scenario,
            base_url="https://example.com",
            tags=["auth", "positive"]
        )
        
        print("✅ Generation successful!")
        print(f"  - Title: {test_json['title']}")
        print(f"  - Steps: {len(test_json['steps'])}")
        print(f"  - Tags: {', '.join(test_json['tags'])}")
        
        # Test framework conversion
        print("\n🔄 Testing framework conversion...")
        
        for framework in ['cypress', 'gherkin']:
            adapter = get_adapter(framework)
            converted = adapter.convert(test_json)
            print(f"✅ {framework.title()} conversion: {len(converted)} characters")
        
        print("\n🎉 All tests passed! VibeQA Generator is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        return False

def main():
    """Run the test suite."""
    print("🔍 VibeQA Generator API Test")
    print("=" * 50)
    
    if not test_api_key():
        return 1
    
    if not test_generation():
        return 1
    
    print("\n" + "=" * 50)
    print("🚀 Ready for production use!")
    print("\nTry the CLI:")
    print('  py -m src.cli "Your scenario here" --framework rainforest')
    print("\nOr run the full demo:")
    print("  py demo.py")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

