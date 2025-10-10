import pytest
from cryptography.fernet import InvalidToken

from wristband.fastapi_auth.models import RawUserInfo, UserInfo, UserInfoRole
from wristband.fastapi_auth.utils import DataEncryptor, map_userinfo_claims

SECRET = "a" * 32  # valid 32-char secret
LONG_SECRET = "a" * 64  # longer than 32 chars


####################################
# USERINFO MAPPING TESTS
####################################


def test_map_userinfo_claims_minimal_fields():
    """Test mapping with only required fields."""
    raw = RawUserInfo(
        sub="user_123",
        tnt_id="tenant_123",
        app_id="app_123",
        idp_name="Wristband",
    )

    result = map_userinfo_claims(raw)

    assert isinstance(result, UserInfo)
    assert result.user_id == "user_123"
    assert result.tenant_id == "tenant_123"
    assert result.application_id == "app_123"
    assert result.identity_provider_name == "Wristband"
    # All optional fields should be None
    assert result.full_name is None
    assert result.email is None
    assert result.roles is None


def test_map_userinfo_claims_all_fields():
    """Test mapping with all optional fields populated."""
    roles = [UserInfoRole(id="role_1", name="admin", display_name="Administrator")]

    raw = RawUserInfo(
        sub="user_123",
        tnt_id="tenant_123",
        app_id="app_123",
        idp_name="Wristband",
        name="John Doe Smith",
        given_name="John",
        family_name="Smith",
        middle_name="Doe",
        nickname="Johnny",
        preferred_username="jsmith",
        picture="https://example.com/pic.jpg",
        email="john@example.com",
        email_verified=True,
        gender="male",
        birthdate="1990-01-01",
        zoneinfo="America/Los_Angeles",
        locale="en-US",
        phone_number="+16045551234",
        phone_number_verified=True,
        updated_at=1640995200,
        roles=roles,
        custom_claims={"department": "engineering", "level": 5},
    )

    result = map_userinfo_claims(raw)

    assert isinstance(result, UserInfo)
    # Verify required field mappings
    assert result.user_id == "user_123"
    assert result.tenant_id == "tenant_123"
    assert result.application_id == "app_123"
    assert result.identity_provider_name == "Wristband"

    # Verify optional field mappings
    assert result.full_name == "John Doe Smith"
    assert result.given_name == "John"
    assert result.family_name == "Smith"
    assert result.middle_name == "Doe"
    assert result.nickname == "Johnny"
    assert result.display_name == "jsmith"
    assert result.picture_url == "https://example.com/pic.jpg"
    assert result.email == "john@example.com"
    assert result.email_verified is True
    assert result.gender == "male"
    assert result.birthdate == "1990-01-01"
    assert result.time_zone == "America/Los_Angeles"
    assert result.locale == "en-US"
    assert result.phone_number == "+16045551234"
    assert result.phone_number_verified is True
    assert result.updated_at == 1640995200
    assert result.roles is not None
    assert len(result.roles) == 1
    assert result.custom_claims == {"department": "engineering", "level": 5}


def test_map_userinfo_claims_claim_name_mappings():
    """Test that OIDC claim names are correctly mapped to User entity field names."""
    raw = RawUserInfo(
        sub="user_123",
        tnt_id="tenant_123",
        app_id="app_123",
        idp_name="Wristband",
        name="Full Name",  # maps to full_name
        preferred_username="username",  # maps to display_name
        picture="https://pic.jpg",  # maps to picture_url
        zoneinfo="America/New_York",  # maps to time_zone
    )

    result = map_userinfo_claims(raw)

    # Verify the specific mappings that differ between OIDC and User entity
    assert result.full_name == "Full Name"  # name -> full_name
    assert result.display_name == "username"  # preferred_username -> display_name
    assert result.picture_url == "https://pic.jpg"  # picture -> picture_url
    assert result.time_zone == "America/New_York"  # zoneinfo -> time_zone


def test_map_userinfo_claims_with_roles():
    """Test mapping preserves roles array correctly."""
    roles = [
        UserInfoRole(id="role_1", name="admin", display_name="Administrator"),
        UserInfoRole(id="role_2", name="user", display_name="User"),
        UserInfoRole(id="role_3", name="viewer", display_name="Viewer"),
    ]

    raw = RawUserInfo(
        sub="user_123",
        tnt_id="tenant_123",
        app_id="app_123",
        idp_name="Wristband",
        roles=roles,
    )

    result = map_userinfo_claims(raw)

    assert result.roles is not None
    assert len(result.roles) == 3
    assert result.roles[0].id == "role_1"
    assert result.roles[1].name == "user"
    assert result.roles[2].display_name == "Viewer"


def test_map_userinfo_claims_with_custom_claims():
    """Test mapping preserves custom_claims dict correctly."""
    custom_claims = {
        "department": "engineering",
        "level": 5,
        "manager": "jane_doe",
        "metadata": {"hire_date": "2020-01-01", "office": "SF"},
    }

    raw = RawUserInfo(
        sub="user_123",
        tnt_id="tenant_123",
        app_id="app_123",
        idp_name="Wristband",
        custom_claims=custom_claims,
    )

    result = map_userinfo_claims(raw)

    assert result.custom_claims is not None
    assert result.custom_claims["department"] == "engineering"
    assert result.custom_claims["level"] == 5
    assert result.custom_claims["metadata"]["office"] == "SF"


def test_map_userinfo_claims_none_values():
    """Test that None values are preserved during mapping."""
    raw = RawUserInfo(
        sub="user_123",
        tnt_id="tenant_123",
        app_id="app_123",
        idp_name="Wristband",
        email=None,
        email_verified=None,
        roles=None,
        custom_claims=None,
    )

    result = map_userinfo_claims(raw)

    assert result.email is None
    assert result.email_verified is None
    assert result.roles is None
    assert result.custom_claims is None


def test_map_userinfo_claims_profile_scope_only():
    """Test mapping with only profile scope fields."""
    raw = RawUserInfo(
        sub="user_123",
        tnt_id="tenant_123",
        app_id="app_123",
        idp_name="Wristband",
        name="John Smith",
        given_name="John",
        family_name="Smith",
        nickname="Johnny",
        picture="https://example.com/pic.jpg",
        birthdate="1990-01-01",
        locale="en-US",
    )

    result = map_userinfo_claims(raw)

    # Profile fields should be populated
    assert result.full_name == "John Smith"
    assert result.given_name == "John"
    assert result.family_name == "Smith"

    # Email and phone fields should be None
    assert result.email is None
    assert result.email_verified is None
    assert result.phone_number is None
    assert result.phone_number_verified is None


def test_map_userinfo_claims_email_scope_only():
    """Test mapping with only email scope fields."""
    raw = RawUserInfo(
        sub="user_123",
        tnt_id="tenant_123",
        app_id="app_123",
        idp_name="Wristband",
        email="john@example.com",
        email_verified=True,
    )

    result = map_userinfo_claims(raw)

    # Email fields should be populated
    assert result.email == "john@example.com"
    assert result.email_verified is True

    # Profile and phone fields should be None
    assert result.full_name is None
    assert result.phone_number is None


def test_map_userinfo_claims_phone_scope_only():
    """Test mapping with only phone scope fields."""
    raw = RawUserInfo(
        sub="user_123",
        tnt_id="tenant_123",
        app_id="app_123",
        idp_name="Wristband",
        phone_number="+16045551234",
        phone_number_verified=True,
    )

    result = map_userinfo_claims(raw)

    # Phone fields should be populated
    assert result.phone_number == "+16045551234"
    assert result.phone_number_verified is True

    # Email and profile fields should be None
    assert result.email is None
    assert result.full_name is None


def test_map_userinfo_claims_boolean_fields():
    """Test that boolean fields are correctly mapped."""
    raw = RawUserInfo(
        sub="user_123",
        tnt_id="tenant_123",
        app_id="app_123",
        idp_name="Wristband",
        email_verified=False,
        phone_number_verified=False,
    )

    result = map_userinfo_claims(raw)

    assert result.email_verified is False
    assert result.phone_number_verified is False


def test_map_userinfo_claims_empty_roles_list():
    """Test mapping with empty roles list."""
    raw = RawUserInfo(
        sub="user_123",
        tnt_id="tenant_123",
        app_id="app_123",
        idp_name="Wristband",
        roles=[],
    )

    result = map_userinfo_claims(raw)

    assert result.roles is not None
    assert len(result.roles) == 0


def test_map_userinfo_claims_empty_custom_claims():
    """Test mapping with empty custom_claims dict."""
    raw = RawUserInfo(
        sub="user_123",
        tnt_id="tenant_123",
        app_id="app_123",
        idp_name="Wristband",
        custom_claims={},
    )

    result = map_userinfo_claims(raw)

    assert result.custom_claims is not None
    assert result.custom_claims == {}


####################################
# DATA ENCRYPTOR TESTS
####################################


def test_encrypt_and_decrypt_roundtrip():
    enc = DataEncryptor(SECRET)
    data = {"user_id": "123", "email": "user@example.com"}
    encrypted = enc.encrypt(data)
    assert isinstance(encrypted, str)
    decrypted = enc.decrypt(encrypted)
    assert decrypted == data


def test_encrypt_rejects_non_dict():
    enc = DataEncryptor(SECRET)
    with pytest.raises(TypeError, match="Data must be a dictionary"):
        enc.encrypt(["not", "a", "dict"])  # type: ignore


def test_decrypt_rejects_empty_string():
    enc = DataEncryptor(SECRET)
    with pytest.raises(ValueError, match="Empty encrypted string cannot be decrypted"):
        enc.decrypt("")


def test_decrypt_rejects_invalid_token():
    enc = DataEncryptor(SECRET)
    with pytest.raises(InvalidToken):
        enc.decrypt("invalid.encrypted.string")


def test_short_secret_raises():
    with pytest.raises(ValueError, match="secret_key must be at least 32 characters long"):
        DataEncryptor("short")


def test_missing_secret_raises():
    with pytest.raises(ValueError, match="secret_key is required"):
        DataEncryptor(None)


def test_empty_string_secret_raises():
    with pytest.raises(ValueError, match="secret_key is required"):
        DataEncryptor("")


def test_exactly_32_char_secret():
    """Test that exactly 32 characters works correctly."""
    enc = DataEncryptor(SECRET)
    data = {"test": "value"}
    encrypted = enc.encrypt(data)
    decrypted = enc.decrypt(encrypted)
    assert decrypted == data


def test_long_secret_truncated():
    """Test that secrets longer than 32 chars are properly truncated."""
    enc = DataEncryptor(LONG_SECRET)
    data = {"test": "value"}
    encrypted = enc.encrypt(data)
    decrypted = enc.decrypt(encrypted)
    assert decrypted == data


def test_different_keys_cannot_decrypt():
    """Test that data encrypted with one key cannot be decrypted with another."""
    enc1 = DataEncryptor("a" * 32)
    enc2 = DataEncryptor("b" * 32)

    data = {"user_id": "123"}
    encrypted = enc1.encrypt(data)

    with pytest.raises(InvalidToken):
        enc2.decrypt(encrypted)


def test_encrypt_various_data_types():
    """Test encryption/decryption with various data types in the dictionary."""
    enc = DataEncryptor(SECRET)
    data = {
        "string": "test",
        "number": 42,
        "float": 3.14,
        "boolean": True,
        "null": None,
        "list": [1, 2, 3],
        "nested_dict": {"key": "value"},
    }
    encrypted = enc.encrypt(data)
    decrypted = enc.decrypt(encrypted)
    assert decrypted == data


def test_encrypt_empty_dict():
    """Test that empty dictionaries can be encrypted and decrypted."""
    enc = DataEncryptor(SECRET)
    data = {}
    encrypted = enc.encrypt(data)
    decrypted = enc.decrypt(encrypted)
    assert decrypted == data


def test_encrypted_strings_are_different():
    """Test that encrypting the same data twice produces different encrypted strings."""
    enc = DataEncryptor(SECRET)
    data = {"user_id": "123"}
    encrypted1 = enc.encrypt(data)
    encrypted2 = enc.encrypt(data)
    # Fernet includes timestamp and random IV, so encryptions should be different
    assert encrypted1 != encrypted2
    # But both should decrypt to the same data
    assert enc.decrypt(encrypted1) == data
    assert enc.decrypt(encrypted2) == data


def test_unicode_data():
    """Test encryption/decryption with unicode characters."""
    enc = DataEncryptor(SECRET)
    data = {"name": "José", "emoji": "🔐", "chinese": "你好"}
    encrypted = enc.encrypt(data)
    decrypted = enc.decrypt(encrypted)
    assert decrypted == data
