"""File I/O utilities for VibeQA Generator."""

import json
from pathlib import Path
from typing import Dict, Any, Optional


def write_json_file(data: Dict[str, Any], file_path: Path, pretty: bool = True) -> None:
    """
    Write JSON data to a file.
    
    Args:
        data: Dictionary to write as JSON
        file_path: Path to write the file
        pretty: Whether to pretty-print the JSON
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))


def read_json_file(file_path: Path) -> Dict[str, Any]:
    """
    Read JSON data from a file.
    
    Args:
        file_path: Path to read from
        
    Returns:
        Dictionary containing the JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_text_file(content: str, file_path: Path) -> None:
    """
    Write text content to a file.
    
    Args:
        content: Text content to write
        file_path: Path to write the file
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def read_text_file(file_path: Path) -> str:
    """
    Read text content from a file.
    
    Args:
        file_path: Path to read from
        
    Returns:
        Text content of the file
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def ensure_directory(dir_path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        dir_path: Directory path to ensure exists
    """
    dir_path.mkdir(parents=True, exist_ok=True)


def get_output_filename(scenario_id: str, framework: str) -> str:
    """
    Generate output filename for a given scenario and framework.
    
    Args:
        scenario_id: Identifier for the scenario
        framework: Target framework (rainforest, cypress, gherkin)
        
    Returns:
        Appropriate filename with extension
    """
    extensions = {
        'rainforest': '.json',
        'cypress': '.cy.js',
        'gherkin': '.feature'
    }
    
    extension = extensions.get(framework, '.txt')
    return f"{scenario_id}{extension}"

