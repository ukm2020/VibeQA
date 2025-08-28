#!/usr/bin/env python3
"""Setup verification script for VibeQA Generator."""

import os
import sys
import json
from pathlib import Path


def check_structure():
    """Verify project structure."""
    print("📁 Checking project structure...")
    
    required_dirs = [
        "src/core", "src/frameworks", "src/utils", "tests",
        "examples/inputs", "examples/outputs/rainforest",
        "examples/outputs/cypress", "examples/outputs/gherkin",
        "prompts", "logs"
    ]
    
    required_files = [
        "pyproject.toml", "README.md", "LICENSE",
        "requirements.txt", "src/cli.py",
        "src/core/engine.py", "src/core/validator.py", "src/core/schema.py",
        "prompts/system_prompt_v1.txt", "prompts/user_prompt_template_v1.txt"
    ]
    
    missing = []
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing.append(f"Directory: {dir_path}")
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(f"File: {file_path}")
    
    if missing:
        print("❌ Missing components:")
        for item in missing:
            print(f"  - {item}")
        return False
    
    print("✅ Project structure complete")
    return True


def check_examples():
    """Verify example files."""
    print("\n📄 Checking example files...")
    
    example_scenarios = ["invalid_email_signup", "happy_path_login", "retry_after_blank_fields"]
    frameworks = ["rainforest", "cypress", "gherkin"]
    extensions = {"rainforest": ".json", "cypress": ".cy.js", "gherkin": ".feature"}
    
    missing = []
    
    for scenario in example_scenarios:
        input_file = Path(f"examples/inputs/{scenario}.txt")
        if not input_file.exists():
            missing.append(f"Input: {input_file}")
        
        for framework in frameworks:
            output_file = Path(f"examples/outputs/{framework}/{scenario}{extensions[framework]}")
            if not output_file.exists():
                missing.append(f"Output: {output_file}")
    
    if missing:
        print("❌ Missing example files:")
        for item in missing:
            print(f"  - {item}")
        return False
    
    print("✅ All example files present")
    return True


def check_golden_outputs():
    """Verify golden outputs are valid."""
    print("\n🏆 Checking golden outputs...")
    
    rainforest_files = list(Path("examples/outputs/rainforest").glob("*.json"))
    
    if not rainforest_files:
        print("❌ No Rainforest golden outputs found")
        return False
    
    for json_file in rainforest_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Basic validation
            required_fields = ["schema_version", "title", "description", "tags", "environment", "steps", "final_result", "design_decisions"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ {json_file.name} missing fields: {missing_fields}")
                return False
            
            if data["schema_version"] != "rf-1.0":
                print(f"❌ {json_file.name} has wrong schema version: {data['schema_version']}")
                return False
            
            if not (4 <= len(data["steps"]) <= 12):
                print(f"❌ {json_file.name} has wrong number of steps: {len(data['steps'])}")
                return False
            
        except json.JSONDecodeError as e:
            print(f"❌ {json_file.name} is not valid JSON: {e}")
            return False
        except Exception as e:
            print(f"❌ Error checking {json_file.name}: {e}")
            return False
    
    print(f"✅ All {len(rainforest_files)} golden outputs are valid")
    return True


def check_cli_structure():
    """Verify CLI can be imported."""
    print("\n🖥️  Checking CLI structure...")
    
    try:
        from src.cli import main
        print("✅ CLI main function importable")
        return True
    except ImportError as e:
        print(f"❌ CLI import failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("🔍 VibeQA Generator Setup Verification")
    print("=" * 50)
    
    checks = [
        check_structure,
        check_examples,
        check_golden_outputs,
        check_cli_structure,
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Setup verification complete - all checks passed!")
        print("\nNext steps:")
        print("1. Set OPENAI_API_KEY environment variable")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Run demo: python demo.py")
        return 0
    else:
        print("💥 Setup verification failed - see errors above")
        return 1


if __name__ == '__main__':
    sys.exit(main())

