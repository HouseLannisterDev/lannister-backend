#!/usr/bin/env python3
"""
Script para generar secretos seguros para Lannister Backend
Uso: python scripts/generate_secrets.py
"""

import secrets
import string

def generate_django_secret_key():
    """Genera una SECRET_KEY compatible con Django"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*()-_=+[]{}|;:,.<>?'
    return ''.join(secrets.choice(chars) for _ in range(50))

def generate_password(length=32, use_special=True):
    """Genera un password seguro"""
    if use_special:
        chars = string.ascii_letters + string.digits + '!@#$%^&*'
    else:
        chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_token(length=32):
    """Genera un token alfanumérico"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def main():
    print("=" * 70)
    print("🔐 GENERADOR DE SECRETOS SEGUROS - Lannister Backend")
    print("=" * 70)
    print()
    
    print("📝 Django SECRET_KEY:")
    print("-" * 70)
    django_key = generate_django_secret_key()
    print(django_key)
    print()
    
    print("🗄️ MySQL Password (32 caracteres con símbolos):")
    print("-" * 70)
    mysql_pass = generate_password(32, use_special=True)
    print(mysql_pass)
    print()
    
    print("🔴 Redis Password (32 caracteres alfanuméricos):")
    print("-" * 70)
    redis_pass = generate_token(32)
    print(redis_pass)
    print()
    
    print("🔑 API Token (ejemplo, 32 caracteres):")
    print("-" * 70)
    api_token = generate_token(32)
    print(api_token)
    print()
    
    print("=" * 70)
    print("⚠️  INSTRUCCIONES:")
    print("=" * 70)
    print("1. Copia estos valores a tu archivo .env")
    print("2. NUNCA compartas estos secretos")
    print("3. NUNCA los agregues al control de versiones")
    print("4. Genera nuevos secretos para cada ambiente (dev, prod)")
    print()
    print("Ejemplo de .env:")
    print("-" * 70)
    print(f"SECRET_KEY={django_key}")
    print(f"MYSQL_PASSWORD={mysql_pass}")
    print(f"REDIS_PASSWORD={redis_pass}")
    print()
    print("✅ ¡Secretos generados exitosamente!")
    print()

if __name__ == "__main__":
    main()
