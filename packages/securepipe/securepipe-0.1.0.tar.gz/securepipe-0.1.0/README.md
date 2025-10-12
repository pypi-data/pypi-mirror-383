````markdown
# SecurePipe

**SecurePipe** is a Python library for **multi-layered encryption**, optional **token expiration**, and **tamper-proof data integrity**. It combines **PBKDF2 key derivation**, **dual Fernet encryption**, **HMAC verification**, and optional **UUID-based secondary keys** to provide a highly secure way to encrypt and transmit sensitive data.

---

## Features

- **Dual-layer encryption**:
  - First layer: Secret key + random salt.
  - Second layer: Secret key + UUID (user-supplied or auto-generated).
- **Optional token expiration** with configurable **grace period**.
- **HMAC-SHA256** signature to detect any tampering.
- **UUID support** for additional security.
- **Helper method** `decode_token_info()` to inspect token metadata.
- Supports **dict, list, str, int, float, and bool payloads**.
- Fully self-contained **base64 JSON token**.


---

## Quick Reference Table: Encrypt vs Decrypt Parameters

| Scenario                     | UUID Provided? | Expiration Provided? | Encrypt Parameters   | Decrypt Parameters | Notes                                                                                                          |
| ---------------------------- | -------------- | -------------------- | -------------------- | ------------------ | -------------------------------------------------------------------------------------------------------------- |
| **Basic**                    | No             | No                   | `data`               | `token`            | Auto-generates UUID internally. Token does not expire.                                                         |
| **Basic + Expiration**       | No             | Yes                  | `data`, `expires_in` | `token`            | Token expires after `expires_in` + grace period (default 30s). UUID auto-generated.                            |
| **Custom UUID**              | Yes            | No                   | `data`               | `token` + `uuid`   | Must provide the same UUID for decryption. Token does not expire.                                              |
| **Custom UUID + Expiration** | Yes            | Yes                  | `data`, `expires_in` | `token` + `uuid`   | Decryption requires UUID. Token expires after `expires_in` + grace period.                                     |
| **Auto UUID + Expiration**   | No             | Yes                  | `data`, `expires_in` | `token`            | UUID embedded in token automatically; token expiration enforced.                                               |
| **Decode Metadata Only**     | Any            | Any                  | `token`              | —                  | Use `decode_token_info(token)` to inspect salt, UUID (if auto-generated), and `expires_at` without decryption. |

**Legend / Notes:**

* `data` → The payload to encrypt (supports `dict`, `list`, `str`, `int`, `float`, `bool`)
* `token` → Base64 JSON token returned by `encrypt()`
* `uuid` → Optional secondary key for extra security
* `expires_in` → Optional token lifetime in seconds
* **Grace period** → Configurable during `SecurePipe` initialization (`tolerance` parameter, default 30s)

---

### Example Usages for Table Scenarios

```python
# 1. Basic
pipe = SecurePipe("secret")
token = pipe.encrypt({"msg": "hello"})
data = pipe.decrypt(token)

# 2. Basic + Expiration
if tolerance of expiraton is not given default is 30 seconds
pipe = SecurePipe("secret", tolerance=30)
token = pipe.encrypt({"msg": "hello"}, expires_in=60)
data = pipe.decrypt(token)

# 3. Custom UUID
uuid_val = "b5c92caa-e6b3-4b39-b5b1-27e1a6e0fdf2"
pipe = SecurePipe("secret", uuid=uuid_val)
token = pipe.encrypt({"msg": "secure"})
pipe2 = SecurePipe("secret", uuid=uuid_val)
data = pipe2.decrypt(token)

# 4. Decode Metadata
info = pipe.decode_token_info(token)
print(info)
```

---


## Installation
# To use the Library
```bash
pip install securepipe
```

# Example usage: https://github.com/Josewathome/securepipe/blob/main/Example_usage.py

## for Local Dev


```bash
pip install cryptography
````

Include `secure_pipe.py` in your project.

---

## Supported Payloads

SecurePipe accepts the following payload types:

| Type    | Notes                                   |
| ------- | --------------------------------------- |
| `dict`  | Converted to JSON string for encryption |
| `list`  | Converted to JSON string                |
| `str`   | Directly encrypted                      |
| `int`   | Converted to string before encryption   |
| `float` | Converted to string                     |
| `bool`  | Converted to string ("True"/"False")    |

> All payloads are serialized to strings internally before encryption.

---

## Usage Examples

### 1. Basic Usage (No UUID, No Expiration)

```python
from secure_pipe import SecurePipe

pipe = SecurePipe(secret_key="my_secret")
token = pipe.encrypt({"message": "classified"})

print("Token:", token)
data = pipe.decrypt(token)
print("Decrypted:", data)
```

### 2. Using a Custom UUID

```python
uuid_value = "b5c92caa-e6b3-4b39-b5b1-27e1a6e0fdf2"
pipe = SecurePipe(secret_key="my_secret", uuid=uuid_value)

token = pipe.encrypt({"agent": "007"})
print("Token:", token)

# Decrypt requires the same UUID
pipe2 = SecurePipe(secret_key="my_secret", uuid=uuid_value)
data = pipe2.decrypt(token)
print("Decrypted:", data)
```

### 3. Token Expiration (Optional)

```python
pipe = SecurePipe(secret_key="my_secret", tolerance=30)  # 30s grace period
token = pipe.encrypt({"msg": "temporary"}, expires_in=60)  # expires in 60 seconds

data = pipe.decrypt(token)
print(data)  # Returns {"error": "Token expired"} if beyond grace period
```

### 4. Decode Token Metadata (Without Decrypting)

```python
info = pipe.decode_token_info(token)
print(info)
```

**Output Example:**

```python
{
  "salt": b'\x8b\xad\xcf\xde...',   # 16-byte random salt
  "uuid": b'\x01\x23\x45\x67...',   # Only if auto-generated
  "expires_at": 1697018400          # Unix timestamp
}
```

---

## How It Works

### 1. **First Layer Encryption**

* Converts input to string (JSON if dict/list).
* Generates a **16-byte random salt**.
* Derives a **32-byte key** using PBKDF2-HMAC-SHA256.
* Encrypts with **Fernet symmetric encryption**.

### 2. **Second Layer Encryption (Optional UUID)**

* Uses a UUID (user-supplied or generated) to derive a second encryption key.
* Encrypts the first layer again.

### 3. **Optional Token Expiration**

* If `expires_in` is provided, adds `"expires_at"` timestamp (Unix time).
* Decryption checks expiration against the current time + **grace period** (configurable, default 30 seconds).

### 4. **Integrity HMAC**

* Generates HMAC-SHA256 using the secret key over the JSON payload.
* Any modification of the token (salt, UUID, data, or expiration) invalidates the HMAC.

### 5. **Encoding**

* Payload (encrypted data, salt, UUID if generated, expiration) is JSON-encoded.
* Entire token, along with HMAC, is base64-encoded to form the final string.

---

## Optional: Decode Token Metadata

The `decode_token_info()` method allows safe inspection of the token without decrypting the data:

```python
info = pipe.decode_token_info(token)
print(info)
```

Returns dictionary with:

* `salt`: 16-byte salt used in first encryption
* `uuid`: UUID bytes (if generated)
* `expires_at`: expiration timestamp (if used)

---

## UML-style Diagram

```
Input Data (dict/list/str/etc)
        |
        v
+----------------------+
| Layer 1: Encryption  |  <-- Derived from secret key + random salt
+----------------------+
        |
        v
+----------------------+
| Layer 2: Encryption  |  <-- Derived from secret key + UUID
+----------------------+
        |
        v
+----------------------+
| Add Expiration (opt) |  <-- expires_at (optional)
+----------------------+
        |
        v
+----------------------+
| Add HMAC Signature   |  <-- Using secret key
+----------------------+
        |
        v
+----------------------+
| Base64 JSON Token    |
+----------------------+
        |
        v
      Output Token
```

---

## Security Features

| Layer                               | Purpose                                                    |
| ----------------------------------- | ---------------------------------------------------------- |
| **PBKDF2 Key Derivation**           | Slows brute-force attacks using 100,000 iterations         |
| **Fernet Encryption**               | Authenticated symmetric encryption for confidentiality     |
| **Dual Encryption (Secret + UUID)** | Adds a second key layer for extra security                 |
| **HMAC-SHA256**                     | Detects tampering with payload or metadata                 |
| **Optional Expiration + Tolerance** | Ensures time-limited access with configurable grace period |

---

## Class Interface

```python
class SecurePipe:
    def __init__(self, secret_key: str, uuid: str | None = None, tolerance: int = 30)
        # Initialize with optional UUID and tolerance (seconds)

    def encrypt(self, data, expires_in: int | None = None) -> str
        # Encrypt data; optional expires_in in seconds

    def decrypt(self, token: str)
        # Verify HMAC, check expiration, decrypt layers

    def decode_token_info(self, token: str)
        # Extract salt, uuid, expires_at without decrypting
```

---

## Notes

* UUID, if provided, is **not embedded** in token — decryption requires the same UUID.
* If UUID is not provided, it is auto-generated and embedded.
* Expiration is optional; if not provided, token is valid indefinitely.
* HMAC signature ensures **tamper-proof integrity**.
* Grace period ensures a small buffer for network or clock differences.

---

## Dependencies

* Python 3.10+
* `cryptography` library

Install:

```bash
pip install cryptography
```

---

## License

MIT License — free to use and modify.


```
