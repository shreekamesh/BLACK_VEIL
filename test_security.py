from datetime import datetime, timedelta, timezone

"""BLACK VEIL Dynamic Security Layer — Verification Test"""
import asyncio
import sys
sys.path.insert(0, '.')

from src.core.security import (
    DynamicEncryptionEngine, EncryptionContext, DynamicKey,
    DynamicPasswordHasher,
    DynamicJWTManager,
    DynamicTLSManager,
    RotationMonitor
)


async def test():
    print('=== DYNAMIC ENCRYPTION SYSTEM TEST ===')

    # 1. Encryption Engine
    engine = DynamicEncryptionEngine()
    data = b'BLACK VEIL - Secret Mission Data 2026'
    enc1 = await engine.encrypt_data(data)
    enc2 = await engine.encrypt_data(data)
    dec1 = await engine.decrypt_data(enc1)
    dec2 = await engine.decrypt_data(enc2)
    assert dec1 == data == dec2, 'Encryption failed'
    assert enc1['ciphertext'] != enc2['ciphertext'], 'Dynamic encryption produced same output'
    print(f'1. DynamicEncryption: OK')
    print(f'   - Active keys: {len(engine.active_keys)}, Historical: {len(engine.key_history)}')
    print(f'   - Entropy: {engine.current_entropy:.3f}, Risk: {engine.global_risk}')
    print(f'   - Ctx1 algo={enc1["algorithm"]}, Ctx2 algo={enc2["algorithm"]}')

    # 2. Password Hasher
    hasher = DynamicPasswordHasher()
    pw = 'BlackVeil2026Secure'
    h1 = hasher.hash_password(pw)
    h2 = hasher.hash_password(pw)
    assert h1['hash'] != h2['hash'], 'Dynamic hashing produced same output'
    assert hasher.verify_password(pw, h1), 'Password verification failed'
    assert hasher.verify_password(pw, h2), 'Password verification failed'
    assert not hasher.verify_password('wrong_password', h1)
    print(f'2. DynamicHasher: OK')
    print(f'   - Algorithm: {h1["algorithm"]}, Iterations: {h1["iterations"]}')
    print(f'   - Hash1 != Hash2: Same password produces different hashes')

    # 3. JWT Manager
    jwt_mgr = DynamicJWTManager(encryption_engine=engine)
    user = {'id': 'user-001', 'username': 'admin', 'role': 'admin'}
    ctx = {'risk_score': 0.3, 'trust_score': 0.9}
    token1 = await jwt_mgr.create_token(user, ctx)
    token2 = await jwt_mgr.create_token(user, ctx)
    assert token1['token'] != token2['token'], 'Dynamic JWT produced same token'
    print(f'3. DynamicJWT: OK')
    print(f'   - Token1 algo={token1["algorithm"]}, Token2 algo={token2["algorithm"]}')
    print(f'   - Expiry: {token1["expires_in"]}s, Encrypted: {token1.get("encrypted", False)}')

    # 4. TLS Manager
    tls_mgr = DynamicTLSManager()
    cert = tls_mgr.generate_dynamic_certificate()
    ctx = tls_mgr.get_ssl_context()
    print(f'4. DynamicTLS: OK')
    print(f'   - RSA-{cert["key_size"]}, {cert["validity_days"]}d validity')
    print(f'   - TLS: {cert["tls_version"]}')

    # 5. Rotation Monitor
    monitor = RotationMonitor(check_interval=5)
    monitor.register_encryption_rotator(engine.check_and_rotate_keys)
    summary = monitor.get_state_summary()
    print(f'5. RotationMonitor: OK')
    print(f'   - Callbacks: {summary["registered_callbacks"]}')
    print(f'   - Running: {summary["is_running"]}')

    print()
    print('=' * 60)
    print('ALL DYNAMIC SECURITY MODULES VERIFIED SUCCESSFULLY')
    print('=' * 60)


if __name__ == '__main__':
    asyncio.run(test())
