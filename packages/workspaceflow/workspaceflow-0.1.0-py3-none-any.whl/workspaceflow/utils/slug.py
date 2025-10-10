"""Slug generation and validation utilities"""

import re
from slugify import slugify as python_slugify


def generate_slug(name: str, max_length: int = 255) -> str:
    """
    Generate a URL-safe slug from a workspace name.

    Args:
        name: The workspace name to convert
        max_length: Maximum length of the slug (default: 255)

    Returns:
        A URL-safe slug

    Example:
        >>> generate_slug("My Awesome Project")
        'my-awesome-project'
        >>> generate_slug("Project #123 (Test)")
        'project-123-test'
    """
    slug = python_slugify(
        name,
        max_length=max_length,
        lowercase=True,
        separator="-"
    )

    # Ensure slug is not empty
    if not slug:
        slug = "workspace"

    return slug


def is_valid_slug(slug: str) -> bool:
    """
    Validate if a string is a valid slug.

    A valid slug contains only lowercase letters, numbers, and hyphens.
    It cannot start or end with a hyphen.

    Args:
        slug: The slug to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> is_valid_slug("my-project")
        True
        >>> is_valid_slug("My Project")
        False
        >>> is_valid_slug("-invalid-")
        False
    """
    if not slug:
        return False

    # Pattern: lowercase letters, numbers, hyphens (not at start/end)
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug))


def ensure_unique_slug(base_slug: str, existing_slugs: set[str], max_attempts: int = 100) -> str:
    """
    Ensure a slug is unique by appending a number if necessary.

    Args:
        base_slug: The base slug to make unique
        existing_slugs: Set of existing slugs to check against
        max_attempts: Maximum number of attempts to find a unique slug

    Returns:
        A unique slug

    Raises:
        ValueError: If unable to find a unique slug after max_attempts

    Example:
        >>> ensure_unique_slug("project", {"project", "project-1"})
        'project-2'
    """
    if base_slug not in existing_slugs:
        return base_slug

    for i in range(1, max_attempts + 1):
        candidate = f"{base_slug}-{i}"
        if candidate not in existing_slugs:
            return candidate

    raise ValueError(f"Unable to generate unique slug after {max_attempts} attempts")
