import secrets

# Generate a random 256-bit (32 bytes) secret key
jwt_secret_key = secrets.token_hex(32)
print(f"JWT Secret Key: {jwt_secret_key}")
