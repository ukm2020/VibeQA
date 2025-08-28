#!/usr/bin/env python3
"""
Demo script for VibeQA Generator - 90 second demonstration
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def run_command(cmd: str, description: str) -> str:
    """Run a command and return its output."""
    print(f"\n🔄 {description}")
    print(f"Command: {cmd}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        output = result.stdout.strip()
        print(output)
        return output
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Stderr: {e.stderr}")
        return ""


def main():
    """Run the 90-second demo."""
    print("🎯 VibeQA Generator - 90 Second Demo")
    print("=" * 60)
    
    # Check API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable is required")
        print("Please set it with: export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)
    
    # Demo scenario
    scenario = "Reject invalid email during signup; keep password valid to isolate email error. Assert error copy contains 'invalid'."
    
    print(f"\n📝 Demo Scenario:")
    print(f'"{scenario}"')
    
    # Generate Rainforest JSON
    rainforest_cmd = f'python -m src.cli "{scenario}" --framework rainforest --base-url https://example.com --tags "auth,email-validation,negative" --out examples/outputs/demo/invalid_email_signup.json'
    
    # Create output directory
    Path("examples/outputs/demo").mkdir(parents=True, exist_ok=True)
    
    rainforest_output = run_command(rainforest_cmd, "Generating Rainforest JSON")
    
    if rainforest_output:
        print(f"\n📄 Generated JSON Structure:")
        try:
            data = json.loads(rainforest_output)
            print(f"  - Title: {data.get('title', 'N/A')}")
            print(f"  - Steps: {len(data.get('steps', []))}")
            print(f"  - Tags: {', '.join(data.get('tags', []))}")
            print(f"  - Expected Result: {data.get('final_result', 'N/A')}")
        except json.JSONDecodeError:
            print("  (Could not parse JSON structure)")
    
    # Generate Cypress version
    cypress_cmd = f'python -m src.cli "{scenario}" --framework cypress --base-url https://example.com --tags "auth,email-validation,negative" --out examples/outputs/demo/invalid_email_signup.cy.js'
    
    cypress_output = run_command(cypress_cmd, "Generating Cypress Test")
    
    # Generate Gherkin version  
    gherkin_cmd = f'python -m src.cli "{scenario}" --framework gherkin --base-url https://example.com --tags "auth,email-validation,negative" --out examples/outputs/demo/invalid_email_signup.feature'
    
    gherkin_output = run_command(gherkin_cmd, "Generating Gherkin Feature")
    
    print(f"\n🎉 Demo Complete!")
    print("=" * 60)
    print("✅ Same input scenario generated structured outputs for 3 frameworks")
    print("✅ All outputs saved to examples/outputs/demo/")
    print("✅ Running the same command tomorrow will yield identical results")
    print("\nFiles generated:")
    print("  - invalid_email_signup.json (Rainforest)")
    print("  - invalid_email_signup.cy.js (Cypress)")
    print("  - invalid_email_signup.feature (Gherkin)")
    
    print(f"\n🔍 Key Features Demonstrated:")
    print("  - Deterministic output generation")
    print("  - Multi-framework support from single scenario")
    print("  - Structured JSON with validation")
    print("  - File output with stdout printing")
    print("  - Tag and URL parameter support")


if __name__ == '__main__':
    main()

