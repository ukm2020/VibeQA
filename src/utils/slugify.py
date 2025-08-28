"""String utilities for file naming and formatting."""

import re
def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.
    
    Args:
        text: Input text to slugify
        
    Returns:
        Slugified string suitable for filenames
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r'[^a-z0-9\-]', '', text)
    
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    
    # Strip hyphens from start and end
    text = text.strip('-')
    
    return text


def kebab_case(text: str) -> str:
    """
    Convert text to kebab-case.
    
    Args:
        text: Input text to convert
        
    Returns:
        kebab-case string
    """
    return slugify(text)


def snake_to_kebab(text: str) -> str:
    """
    Convert snake_case to kebab-case.
    
    Args:
        text: snake_case input
        
    Returns:
        kebab-case string
    """
    return text.replace('_', '-')


def camel_to_kebab(text: str) -> str:
    """
    Convert camelCase or PascalCase to kebab-case.
    
    Args:
        text: camelCase or PascalCase input
        
    Returns:
        kebab-case string
    """
    # Insert hyphens before capital letters
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', text)
    return text.lower()


def normalize_tag(tag: str) -> str:
    """
    Normalize a tag to kebab-case format.
    
    Args:
        tag: Input tag string
        
    Returns:
        Normalized kebab-case tag
    """
    # Handle different input formats
    if '_' in tag:
        tag = snake_to_kebab(tag)
    elif any(c.isupper() for c in tag):
        tag = camel_to_kebab(tag)
    else:
        tag = slugify(tag)
    
    return tag
