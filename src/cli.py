"""Command-line interface for VibeQA Generator."""

import sys
import os
from pathlib import Path
from typing import Optional, List

import click

from .core import create_engine
from .frameworks.registry import get_adapter, get_available_frameworks
from .utils.file_io import write_text_file
from .utils.slugify import slugify


@click.command()
@click.argument('scenario', type=str)
@click.option('--framework', '-f', 
              type=click.Choice(get_available_frameworks(), case_sensitive=False),
              required=True,
              help='Target framework for test generation')
@click.option('--base-url', '-u',
              type=str,
              help='Base URL for the application under test')
@click.option('--tags', '-t',
              type=str,
              help='Comma-separated list of tags to include')
@click.option('--out', '-o',
              type=click.Path(),
              help='Output file path (prints to stdout if not specified)')
@click.option('--strict',
              is_flag=True,
              help='Enable strict validation mode')
@click.option('--model',
              type=str,
              default='gpt-4o',
              help='LLM model to use (default: gpt-4o)')
@click.option('--temperature',
              type=float,
              default=0.2,
              help='Temperature for LLM generation (default: 0.2)')
def main(scenario: str, framework: str, base_url: Optional[str] = None,
         tags: Optional[str] = None, out: Optional[str] = None,
         strict: bool = False, model: str = 'gpt-4o', temperature: float = 0.2):
    """
    Generate test artifacts from plain-English scenarios.
    
    SCENARIO: Plain English description of the test scenario
    """
    try:
        # Check for API key
        if not os.getenv('OPENAI_API_KEY'):
            click.echo("Error: OPENAI_API_KEY environment variable is required", err=True)
            sys.exit(1)
        
        # Parse tags
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Create engine
        engine = create_engine(model=model, temperature=temperature)
        
        # Generate test JSON
        click.echo("Generating test...", err=True)
        test_json = engine.generate_test(
            scenario=scenario,
            base_url=base_url,
            tags=tag_list,
            strict_mode=strict
        )
        
        # Get framework adapter
        adapter = get_adapter(framework)
        
        # Convert to target format
        output_content = adapter.convert(test_json)
        
        # Output to file if specified
        if out:
            output_path = Path(out)
            write_text_file(output_content, output_path)
            click.echo(f"Test written to: {output_path}", err=True)
        
        # Always print to stdout
        click.echo(output_content)
        
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


@click.command()
@click.argument('scenario_file', type=click.Path(exists=True))
@click.option('--framework', '-f',
              type=click.Choice(get_available_frameworks(), case_sensitive=False),
              required=True,
              help='Target framework for test generation')
@click.option('--base-url', '-u',
              type=str,
              help='Base URL for the application under test')
@click.option('--output-dir', '-d',
              type=click.Path(),
              default='output',
              help='Output directory (default: output)')
@click.option('--strict',
              is_flag=True,
              help='Enable strict validation mode')
@click.option('--model',
              type=str,
              default='gpt-4o',
              help='LLM model to use (default: gpt-4o)')
def batch(scenario_file: str, framework: str, base_url: Optional[str] = None,
          output_dir: str = 'output', strict: bool = False, model: str = 'gpt-4o'):
    """
    Generate tests from a batch file containing multiple scenarios.
    
    SCENARIO_FILE: File containing scenarios (one per line)
    """
    try:
        # Check for API key
        if not os.getenv('OPENAI_API_KEY'):
            click.echo("Error: OPENAI_API_KEY environment variable is required", err=True)
            sys.exit(1)
        
        # Read scenarios
        with open(scenario_file, 'r', encoding='utf-8') as f:
            scenarios = [line.strip() for line in f if line.strip()]
        
        if not scenarios:
            click.echo("Error: No scenarios found in file", err=True)
            sys.exit(1)
        
        # Create engine and adapter
        engine = create_engine(model=model)
        adapter = get_adapter(framework)
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        for i, scenario in enumerate(scenarios, 1):
            click.echo(f"Processing scenario {i}/{len(scenarios)}...", err=True)
            
            try:
                # Generate test
                test_json = engine.generate_test(
                    scenario=scenario,
                    base_url=base_url,
                    strict_mode=strict
                )
                
                # Convert and save
                output_content = adapter.convert(test_json)
                
                # Generate filename from scenario
                scenario_id = slugify(scenario[:50])  # First 50 chars
                filename = f"{scenario_id}{adapter.get_file_extension()}"
                file_path = output_path / filename
                
                write_text_file(output_content, file_path)
                click.echo(f"  -> {file_path}", err=True)
                
            except Exception as e:
                click.echo(f"  -> Error: {e}", err=True)
                continue
        
        click.echo("Batch processing complete!", err=True)
        
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    # For direct execution, use the main command
    main()


# For package entry point, create a wrapper that calls main
def cli():
    """CLI entry point for package installation."""
    main()
