from securepipe import SecurePipe
import json
import time

def run_test(pipe, payload, expires_in=None, description=""):
    """
    Helper to encrypt, decrypt and validate payload with detailed logging
    """
    print("\n" + "="*80)
    print(f"TEST: {description}")
    print("="*80)
    print("Original Payload:", payload)
    
    # Step 1: Encrypt
    token = pipe.encrypt(payload, expires_in=expires_in)
    print("\n[ENCRYPTION]")
    print("Encrypted Token:", token)
    
    # Step 2: Decode metadata for inspection
    info = pipe.decode_token_info(token)
    print("\n[METADATA]")
    print("Salt (bytes):", info.get("salt"))
    print("UUID (bytes or None):", info.get("uuid"))
    print("Expires At:", info.get("expires_at"))
    
    # Step 3: Decrypt
    result = pipe.decrypt(token)
    print("\n[DECRYPTION]")
    print("Decrypted Result:", result)
    
    # Step 4: Assertions and status
    if expires_in:
        # Check if token is already expired
        now = time.time()
        if info.get("expires_at") and now > info["expires_at"] + pipe.tolerance:
            assert "error" in result and "Token expired" in result["error"], "Expiration test failed!"
            print("✅ Expiration correctly enforced (token expired)")
        else:
            # Validate successful decryption
            if payload == True or payload == False:
                assert result == str(payload), "Payload mismatch! Decryption failed before expiration."
            else:
                assert result == payload, "Payload mismatch! Decryption failed before expiration."
            print("✅ Decryption successful before expiration")
    else:
        # No expiration - validate successful decryption
        if payload == True or payload == False:
            assert result == str(payload), "Payload mismatch! Decryption failed."
        else:
            assert result == payload, "Payload mismatch! Decryption failed."
        print("✅ Decryption successful (no expiration)")
    
    print("="*80 + "\n")

def test_all_payload_types():
    print("\n" + "#"*80)
    print("TEST SUITE: All Payload Types, UUID, Expiration, Tolerance Variations")
    print("#"*80 + "\n")
    
    payloads = [
        {"msg": "hello world"},       # dict
        ["a", "b", "c"],              # list
        "Just a string",              # str
        12345,                        # int
        3.14159,                      # float
        True,                         # bool
        False                         # bool
    ]
    
    uuids = [None, "a1b2c3d4-e5f6-7890-1234-567890abcdef"]
    expirations = [None, 3]  # None or 3 seconds
    tolerances = [1, 2]  # Reduced to speed up tests
    
    for uuid_val in uuids:
        for tol in tolerances:
            pipe = SecurePipe(secret_key="super_secret_key_123", uuid=uuid_val, tolerance=tol)
            for payload in payloads:
                # Test without expiration
                desc = f"Payload={type(payload).__name__}, UUID={'set' if uuid_val else 'None'}, no expiration, tolerance={tol}"
                run_test(pipe, payload, expires_in=None, description=desc)
    
    # Separate expiration tests (only run a few to avoid long waits)
    print("\n" + "="*80)
    print("EXPIRATION TESTS (Limited to avoid long execution time)")
    print("="*80)
    
    # Test expiration with just one payload type
    test_payload = {"msg": "expiration test"}
    pipe = SecurePipe(secret_key="super_secret_key_123", uuid=None, tolerance=1)
    
    # Test 1: Token that hasn't expired yet
    print("\n[Test 1: Fresh token - should decrypt successfully]")
    token = pipe.encrypt(test_payload, expires_in=5)
    result = pipe.decrypt(token)
    assert result == test_payload, "Fresh token should decrypt successfully"
    print("✅ Fresh token decrypted successfully")
    
    # Test 2: Token that has expired
    print("\n[Test 2: Expired token - should fail]")
    expired_token = pipe.encrypt(test_payload, expires_in=2)
    print(f"Sleeping 4 seconds to ensure expiration (expires_in=2, tolerance=1)...")
    time.sleep(4)
    expired_result = pipe.decrypt(expired_token)
    
    if isinstance(expired_result, dict) and "error" in expired_result and "Token expired" in expired_result["error"]:
        print("✅ Expired token correctly rejected")
    else:
        print(f"❌ Expiration failed! Expected error but got: {expired_result}")

def test_wrong_key():
    print("\n" + "#"*80)
    print("TEST: Wrong Key Decryption")
    print("#"*80)
    
    pipe1 = SecurePipe(secret_key="key_one_2323232323")
    pipe2 = SecurePipe(secret_key="key_two_1212121212121")
    
    payload = {"message": "secret"}
    print("Encrypting with key_one")
    token = pipe1.encrypt(payload)
    print("Token:", token)
    
    print("Attempting decryption with key_two")
    result = pipe2.decrypt(token)
    
    if "error" in result:
        print("✅ Correctly failed to decrypt with wrong key:", result["error"])
    else:
        print("❌ Wrong key decryption test failed - decrypted:", result)

def test_decode_metadata():
    print("\n" + "#"*80)
    print("TEST: decode_token_info()")
    print("#"*80)
    
    pipe = SecurePipe(secret_key="super_secret_key_123")
    payload = {"msg": "metadata test"}
    token = pipe.encrypt(payload, expires_in=60)
    
    info = pipe.decode_token_info(token)
    print("Decoded Token Info:", info)
    
    assert "salt" in info and "expires_at" in info, "decode_token_info failed"
    print("✅ decode_token_info test passed")

if __name__ == "__main__":
    test_all_payload_types()
    test_wrong_key()
    test_decode_metadata()
    print("\n🎉 All tests completed!")