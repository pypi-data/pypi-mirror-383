"""
Auto-import injection for api.py
Modifies existing api.py to add new router imports and registrations
"""
import re
from pathlib import Path
from typing import Optional


def inject_router_import(
    api_file: Path,
    endpoint_module: str,
    router_var: str = "router"
) -> bool:
    """
    Inject import statement for new endpoint module

    Args:
        api_file: Path to api.py file
        endpoint_module: Module name (e.g., "departments")
        router_var: Router variable name (default: "router")

    Returns:
        True if injection successful

    Example:
        BEFORE:
            from app.api.v1.endpoints import users, examples

        AFTER:
            from app.api.v1.endpoints import users, examples, departments
    """
    if not api_file.exists():
        return False

    content = api_file.read_text(encoding='utf-8')

    # Pattern untuk mencari import line
    # Matches: from app.api.v1.endpoints import ...
    import_pattern = r'(from\s+app\.api\.v1\.endpoints\s+import\s+)([^\n]+)'

    match = re.search(import_pattern, content)

    if not match:
        # Jika tidak ada import, tambahkan di bawah api_router declaration
        router_pattern = r'(api_router\s*=\s*APIRouter\(\))'
        router_match = re.search(router_pattern, content)

        if router_match:
            # Insert import before api_router
            insert_pos = router_match.start()
            new_import = f"from app.api.v1.endpoints import {endpoint_module}\n\n"
            content = content[:insert_pos] + new_import + content[insert_pos:]
        else:
            # Fallback: add at end of imports section
            # Find last import line
            last_import = list(re.finditer(r'^(from|import)\s+', content, re.MULTILINE))
            if last_import:
                insert_pos = last_import[-1].end()
                # Find end of line
                newline_pos = content.find('\n', insert_pos)
                if newline_pos != -1:
                    insert_pos = newline_pos + 1
                new_import = f"from app.api.v1.endpoints import {endpoint_module}\n"
                content = content[:insert_pos] + new_import + content[insert_pos:]
    else:
        # Ada import, tambahkan endpoint_module ke list
        existing_imports = match.group(2).strip()

        # Check if already imported
        if endpoint_module in existing_imports.split(','):
            return True  # Already imported

        # Add to imports
        new_imports = f"{existing_imports}, {endpoint_module}"
        content = content[:match.start(2)] + new_imports + content[match.end(2):]

    # Write back
    api_file.write_text(content, encoding='utf-8')
    return True


def inject_router_registration(
    api_file: Path,
    endpoint_module: str,
    prefix: str,
    tags: Optional[str] = None
) -> bool:
    """
    Inject router registration line

    Args:
        api_file: Path to api.py file
        endpoint_module: Module name (e.g., "departments")
        prefix: Router prefix (e.g., "/departments")
        tags: Router tags (optional, defaults to capitalized module name)

    Returns:
        True if injection successful

    Example:
        Adds:
            api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])
    """
    if not api_file.exists():
        return False

    content = api_file.read_text(encoding='utf-8')

    # Default tags
    if tags is None:
        tags = endpoint_module.replace('_', ' ').title()

    # Create registration line
    registration_line = (
        f'api_router.include_router({endpoint_module}.router, '
        f'prefix="{prefix}", tags=["{tags}"])\n'
    )

    # Check if already registered
    if registration_line.strip() in content:
        return True  # Already registered

    # Find last include_router call
    include_pattern = r'api_router\.include_router\([^\)]+\)'
    matches = list(re.finditer(include_pattern, content))

    if matches:
        # Insert after last include_router
        last_match = matches[-1]
        insert_pos = last_match.end()
        # Find end of line
        newline_pos = content.find('\n', insert_pos)
        if newline_pos != -1:
            insert_pos = newline_pos + 1
        content = content[:insert_pos] + registration_line + content[insert_pos:]
    else:
        # No existing include_router, add after api_router declaration
        router_pattern = r'(api_router\s*=\s*APIRouter\(\)[^\n]*\n)'
        router_match = re.search(router_pattern, content)

        if router_match:
            insert_pos = router_match.end()
            # Add blank line before registration
            content = content[:insert_pos] + '\n' + registration_line + content[insert_pos:]

    # Write back
    api_file.write_text(content, encoding='utf-8')
    return True


def auto_register_router(
    api_file: Path,
    endpoint_module: str,
    prefix: str,
    tags: Optional[str] = None
) -> bool:
    """
    Auto-register new router to api.py

    Performs both import injection and registration

    Args:
        api_file: Path to api.py file
        endpoint_module: Module name (e.g., "departments")
        prefix: Router prefix (e.g., "/departments")
        tags: Router tags (optional)

    Returns:
        True if successful
    """
    # Inject import
    if not inject_router_import(api_file, endpoint_module):
        return False

    # Inject registration
    if not inject_router_registration(api_file, endpoint_module, prefix, tags):
        return False

    return True
