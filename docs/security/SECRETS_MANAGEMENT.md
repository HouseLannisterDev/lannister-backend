# 🔐 Gestión de Secretos - Lannister Backend

Esta guía explica cómo manejar secretos y credenciales de forma segura en el proyecto.

## ⚠️ Reglas Fundamentales

1. **NUNCA** hardcodear secretos en el código
2. **SIEMPRE** usar variables de entorno
3. **NUNCA** commitear archivos `.env` con credenciales reales
4. **SIEMPRE** rotar secretos comprometidos inmediatamente

## 🔑 Secretos Requeridos

### Django SECRET_KEY

**Propósito:** Criptografía, firmas, tokens de sesión, etc.

**Generar nueva clave:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Configurar en .env:**
```bash
SECRET_KEY=tu-clave-generada-aqui-muy-larga-y-aleatoria
```

**❌ INCORRECTO:**
```python
# settings.py
SECRET_KEY = "p7!v8w@r2$k1z#x6b9q4t0s5e3u8l1m0c2d7f6g5h4j3k2l1"  # ¡NO HACER ESTO!
```

**✅ CORRECTO:**
```python
# settings.py
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")
```

### MySQL Password

**Propósito:** Conexión a base de datos RDS

**Generar password seguro:**
```bash
# Opción 1: OpenSSL
openssl rand -base64 32

# Opción 2: Python
python -c "import secrets; import string; chars = string.ascii_letters + string.digits + '!@#$%^&*'; print(''.join(secrets.choice(chars) for _ in range(32)))"
```

**Configurar en .env:**
```bash
MYSQL_PASSWORD=tu-password-generado-muy-seguro
```

**Para scripts de AWS:**
```bash
# Opción 1: Variable de entorno
export DB_PASSWORD="tu-password-seguro"
./aws-deployment-scripts/02-create-rds-mysql.sh

# Opción 2: Argumento
./aws-deployment-scripts/02-create-rds-mysql.sh "tu-password-seguro"
```

## 📋 Checklist de Seguridad

### Antes de Desarrollo
- [ ] Copiar `.env.example` a `.env`
- [ ] Generar `SECRET_KEY` única
- [ ] Configurar credenciales de desarrollo seguras
- [ ] Verificar que `.env` está en `.gitignore`

### Antes de Deployment
- [ ] Generar nuevas credenciales para producción
- [ ] NO reutilizar credenciales de desarrollo
- [ ] Configurar variables de entorno en servidor
- [ ] Verificar que NO hay secretos hardcodeados (ejecutar SonarQube)

### Después de Compromiso
- [ ] Rotar TODOS los secretos inmediatamente
- [ ] Cambiar passwords en servicios (RDS, Redis, etc.)
- [ ] Generar nueva `SECRET_KEY`
- [ ] Actualizar `.env` en todos los ambientes
- [ ] Revisar logs de acceso

## 🛠️ Herramientas

### Verificar Secretos Hardcodeados

**SonarQube:**
```bash
# Ejecutar análisis de SonarQube
sonar-scanner
```

**Grep manual:**
```bash
# Buscar posibles secretos en el código
grep -r "password\s*=\s*['\"]" --include="*.py" .
grep -r "SECRET_KEY\s*=\s*['\"]" --include="*.py" .
```

### Generar Múltiples Secretos

```python
# generate_secrets.py
from django.core.management.utils import get_random_secret_key
import secrets
import string

print("=== Secretos Generados ===\n")

# Django SECRET_KEY
print("Django SECRET_KEY:")
print(get_random_secret_key())
print()

# MySQL Password (32 caracteres)
chars = string.ascii_letters + string.digits + '!@#$%^&*'
mysql_pass = ''.join(secrets.choice(chars) for _ in range(32))
print("MySQL Password:")
print(mysql_pass)
print()

# Redis Password (32 caracteres alfanuméricos)
redis_pass = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
print("Redis Password:")
print(redis_pass)
```

**Ejecutar:**
```bash
python scripts/generate_secrets.py
```

## 🔒 Mejores Prácticas

### Variables de Entorno en Producción

**AWS EC2 (systemd):**
```ini
# /etc/systemd/system/lannister-backend.service
[Service]
Environment="SECRET_KEY=tu-secret-key-aqui"
Environment="MYSQL_PASSWORD=tu-mysql-password"
```

**Docker:**
```bash
# docker run
docker run -e SECRET_KEY="..." -e MYSQL_PASSWORD="..." lannister-backend

# docker-compose.yml
services:
  backend:
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
```

**AWS Secrets Manager (Recomendado para producción):**
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='sa-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# En settings.py
secrets = get_secret('lannister-backend/production')
SECRET_KEY = secrets['SECRET_KEY']
MYSQL_PASSWORD = secrets['MYSQL_PASSWORD']
```

### Rotación de Secretos

**Frecuencia recomendada:**
- `SECRET_KEY`: Cada 90 días o al detectar compromiso
- Passwords DB: Cada 90 días o al detectar compromiso
- Claves API: Según política del proveedor

**Proceso de rotación:**
1. Generar nuevo secreto
2. Actualizar en AWS Secrets Manager / .env
3. Reiniciar aplicación
4. Verificar funcionamiento
5. Revocar secreto anterior

## 📚 Referencias

- [Django Security Settings](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [SonarQube Security Rules](https://rules.sonarsource.com/python/tag/security)

---

**Última actualización:** 26 de octubre de 2025
