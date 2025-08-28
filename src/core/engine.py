"""LLM engine integration for VibeQA Generator."""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    raise ImportError("OpenAI package is required. Install with: pip install openai")

from .validator import TestValidator, ValidationResult


class PromptEngine:
    """Handles LLM interactions and prompt management."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o", 
                 temperature: float = 0.2, max_tokens: int = 1500):
        """
        Initialize the prompt engine.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use for generation
            temperature: Temperature for generation
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.validator = TestValidator()
        
        # Load prompts
        self.system_prompt = self._load_prompt("system_prompt_v1.txt")
        self.user_prompt_template = self._load_prompt("user_prompt_template_v1.txt")
    
    def _load_prompt(self, filename: str) -> str:
        """Load prompt template from file."""
        prompt_path = Path("prompts") / filename
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    def generate_test(self, scenario: str, base_url: Optional[str] = None,
                     tags: Optional[List[str]] = None, variables: Optional[Dict[str, str]] = None,
                     strict_mode: bool = False) -> Dict[str, Any]:
        """
        Generate a test from a scenario description.
        
        Args:
            scenario: Plain English scenario description
            base_url: Base URL for the application
            tags: List of tags to include
            variables: Variables available for the test
            strict_mode: Whether to use strict validation
        
        Returns:
            Dictionary containing the generated test JSON
            
        Raises:
            ValueError: If generation or validation fails
        """
        # Prepare prompt variables
        base_url_or_none = base_url or "None specified"
        tags_csv_or_empty = ",".join(tags) if tags else ""
        variables_or_empty = json.dumps(variables) if variables else "None"
        
        user_prompt = self.user_prompt_template.format(
            scenario=scenario,
            base_url_or_none=base_url_or_none,
            tags_csv_or_empty=tags_csv_or_empty,
            variables_or_empty=variables_or_empty
        )
        
        # Log the request
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_data = {
            "run_id": run_id,
            "timestamp": datetime.now().isoformat(),
            "scenario": scenario,
            "base_url": base_url,
            "tags": tags,
            "variables": variables,
            "model": self.model,
            "temperature": self.temperature
        }
        
        # Generate initial response
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=1.0
            )
            
            raw_response = response.choices[0].message.content
            log_data["raw_response"] = raw_response
            
        except Exception as e:
            log_data["error"] = str(e)
            self._log_run(log_data)
            raise ValueError(f"Failed to generate test: {str(e)}")
        
        # Validate response
        self.validator.strict_mode = strict_mode
        parsed_json, validation_result = self.validator.validate_raw_response(raw_response)
        
        log_data["parsed_json"] = parsed_json
        log_data["validation_result"] = {
            "success": validation_result.success,
            "errors": validation_result.errors,
            "warnings": validation_result.warnings
        }
        
        # Retry once if validation failed
        if not validation_result.success and parsed_json is None:
            correction_prompt = self.validator.generate_correction_prompt(raw_response, validation_result)
            
            try:
                retry_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_prompt},
                        {"role": "assistant", "content": raw_response},
                        {"role": "user", "content": correction_prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    top_p=1.0
                )
                
                retry_raw_response = retry_response.choices[0].message.content
                log_data["retry_raw_response"] = retry_raw_response
                
                # Validate retry
                parsed_json, validation_result = self.validator.validate_raw_response(retry_raw_response)
                log_data["retry_validation_result"] = {
                    "success": validation_result.success,
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings
                }
                
            except Exception as e:
                log_data["retry_error"] = str(e)
                self._log_run(log_data)
                raise ValueError(f"Failed to generate test on retry: {str(e)}")
        
        # Log the final result
        self._log_run(log_data)
        
        # Check final validation
        if not validation_result.success or parsed_json is None:
            error_msg = "Validation failed: " + "; ".join(validation_result.errors)
            raise ValueError(error_msg)
        
        # Set default base_url if not provided
        if base_url and 'environment' in parsed_json:
            parsed_json['environment']['base_url'] = base_url
        elif 'environment' in parsed_json and not parsed_json['environment'].get('base_url'):
            parsed_json['environment']['base_url'] = "https://example.com"
        
        return parsed_json
    
    def _log_run(self, log_data: Dict[str, Any]) -> None:
        """Log run data to JSONL file."""
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"run_{log_data['run_id']}.jsonl"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, separators=(',', ':'))
                f.write('\n')
        except Exception as e:
            # Don't fail the main operation if logging fails
            print(f"Warning: Failed to write log: {e}")


def create_engine(model: str = "gpt-4o", temperature: float = 0.2) -> PromptEngine:
    """Create a configured PromptEngine instance."""
    return PromptEngine(model=model, temperature=temperature)

