"""
Naming convention utilities for ATAMS
Handles singular/plural conversion and case transformations
"""
import inflect
import re

_inflect_engine = inflect.engine()


def to_snake_case(text: str) -> str:
    """
    Convert text to snake_case

    Examples:
        Department → department
        UserProfile → user_profile
        API_Key → api_key
    """
    # Insert underscore before capital letters
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    # Insert underscore before capital letters in acronyms
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def to_pascal_case(text: str) -> str:
    """
    Convert text to PascalCase

    Examples:
        department → Department
        user_profile → UserProfile
        api_key → ApiKey
    """
    words = text.replace('-', '_').split('_')
    return ''.join(word.capitalize() for word in words if word)


def to_plural(text: str) -> str:
    """
    Convert singular to plural

    Examples:
        department → departments
        user → users
        category → categories
    """
    return _inflect_engine.plural(text)


def to_singular(text: str) -> str:
    """
    Convert plural to singular

    Examples:
        departments → department
        users → user
        categories → category
    """
    return _inflect_engine.singular_noun(text) or text


def get_prefix(resource_name: str) -> str:
    """
    Get table column prefix from resource name

    Examples:
        department → d_
        user → u_
        user_profile → up_
    """
    words = resource_name.split('_')
    if len(words) == 1:
        # Single word: use first letter
        return f"{resource_name[0]}_"
    else:
        # Multiple words: use first letter of each word
        return ''.join(word[0] for word in words) + '_'


class ResourceNaming:
    """
    Helper class to generate all naming variations for a resource

    Usage:
        naming = ResourceNaming("department")
        naming.singular  # "department"
        naming.plural    # "departments"
        naming.pascal    # "Department"
        naming.prefix    # "d_"
    """

    def __init__(self, resource_name: str):
        # Normalize input to snake_case
        self.input = to_snake_case(resource_name)

        # Singular form (snake_case)
        self.singular = to_singular(self.input)

        # Plural form (snake_case)
        self.plural = to_plural(self.singular)

        # PascalCase forms
        self.pascal = to_pascal_case(self.singular)
        self.pascal_plural = to_pascal_case(self.plural)

        # Table column prefix
        self.prefix = get_prefix(self.singular)

        # File names
        self.model_file = f"{self.singular}.py"
        self.schema_file = f"{self.singular}.py"
        self.repository_file = f"{self.singular}_repository.py"
        self.service_file = f"{self.singular}_service.py"
        self.endpoint_file = f"{self.plural}.py"

    def __repr__(self):
        return (
            f"ResourceNaming(\n"
            f"  singular='{self.singular}',\n"
            f"  plural='{self.plural}',\n"
            f"  pascal='{self.pascal}',\n"
            f"  prefix='{self.prefix}'\n"
            f")"
        )
