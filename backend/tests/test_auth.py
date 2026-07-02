import pytest
from app.auth.password_utils import get_password_hash, verify_password

def test_password_hashing():
    """
    Unit test validating cryptography bcrypt helpers.
    """
    raw_pass = "secure_password_123"
    hashed = get_password_hash(raw_pass)
    
    # Hash should be distinct from original string
    assert hashed != raw_pass
    
    # Verify success
    assert verify_password(raw_pass, hashed) is True
    
    # Verify failure
    assert verify_password("wrong_password", hashed) is False
