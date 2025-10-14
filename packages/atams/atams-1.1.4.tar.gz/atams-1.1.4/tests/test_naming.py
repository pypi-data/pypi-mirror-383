"""Test naming utilities"""
from atams.utils.naming import (
    ResourceNaming,
    to_snake_case,
    to_pascal_case,
    to_plural,
    to_singular,
    get_prefix
)


def test_to_snake_case():
    """Test snake_case conversion"""
    assert to_snake_case("Department") == "department"
    assert to_snake_case("UserProfile") == "user_profile"
    assert to_snake_case("APIKey") == "api_key"
    assert to_snake_case("user_profile") == "user_profile"


def test_to_pascal_case():
    """Test PascalCase conversion"""
    assert to_pascal_case("department") == "Department"
    assert to_pascal_case("user_profile") == "UserProfile"
    assert to_pascal_case("api-key") == "ApiKey"


def test_to_plural():
    """Test pluralization"""
    assert to_plural("user") == "users"
    assert to_plural("department") == "departments"
    assert to_plural("category") == "categories"


def test_to_singular():
    """Test singularization"""
    assert to_singular("users") == "user"
    assert to_singular("departments") == "department"
    assert to_singular("categories") == "category"
    # Should return same if already singular
    assert to_singular("user") == "user"


def test_get_prefix():
    """Test prefix generation"""
    assert get_prefix("department") == "d_"
    assert get_prefix("user") == "u_"
    assert get_prefix("user_profile") == "up_"


def test_resource_naming():
    """Test ResourceNaming class"""
    naming = ResourceNaming("department")

    assert naming.singular == "department"
    assert naming.plural == "departments"
    assert naming.pascal == "Department"
    assert naming.pascal_plural == "Departments"
    assert naming.prefix == "d_"

    # Test file names
    assert naming.model_file == "department.py"
    assert naming.schema_file == "department.py"
    assert naming.repository_file == "department_repository.py"
    assert naming.service_file == "department_service.py"
    assert naming.endpoint_file == "departments.py"


def test_resource_naming_with_plural_input():
    """Test ResourceNaming with plural input"""
    naming = ResourceNaming("departments")

    # Should normalize to singular
    assert naming.singular == "department"
    assert naming.plural == "departments"


def test_resource_naming_with_pascal_input():
    """Test ResourceNaming with PascalCase input"""
    naming = ResourceNaming("UserProfile")

    assert naming.singular == "user_profile"
    assert naming.plural == "user_profiles"
    assert naming.pascal == "UserProfile"
    assert naming.prefix == "up_"
