# GUÍA DE SEGURIDAD Y BUENAS PRÁCTICAS
# =====================================

## ✅ Limpieza Completada

Este repositorio ha sido limpiado de archivos sensibles y configurado con buenas prácticas de seguridad.

## 🔒 Archivos Removidos del Repositorio

Los siguientes archivos fueron eliminados del historial de Git pero permanecen localmente (ignorados por `.gitignore`):

### Credenciales y Claves Privadas:
- ❌ `aws-deployment-scripts/lannister-backend-key.pem` - Clave SSH de AWS EC2
- ❌ `aws-deployment-scripts/rds-credentials.txt` - Credenciales de MySQL RDS

### Archivos Backup Innecesarios:
- ❌ `lannister_news_api/settings.py.backup`
- ❌ `docker-compose.yml.backup`
- ❌ `Dockerfile.backup`
- ❌ `API_Documentation.html.bak`
- ❌ `API_Documentation.md.bak`

### Archivos Compilados:
- ❌ Todos los directorios `__pycache__/`

## 📁 Archivos de Plantilla Creados

Para ayudarte a configurar el proyecto de forma segura:

1. **`.env.example`** - Plantilla de variables de entorno (ya existía, actualizada)
2. **`aws-deployment-scripts/rds-credentials.example.txt`** - Plantilla para credenciales RDS
3. **`aws-deployment-scripts/KEY_INSTRUCTIONS.md`** - Instrucciones para manejar claves SSH

## 🛡️ Cambios de Seguridad en Código

### `lannister_news_api/settings.py`:
- ✅ `SECRET_KEY` ahora usa variable de entorno
- ✅ `DEBUG` ahora usa variable de entorno (default: False en producción)
- ✅ `MYSQL_PASSWORD` sin valor por defecto hardcodeado
- ✅ `MYSQL_HOST` sin endpoint de RDS hardcodeado

## 📋 Pasos Siguientes

### 1. Crear tu archivo `.env` local:
```bash
cp .env.example .env
# Edita .env con tus credenciales reales
```

### 2. Configurar credenciales de RDS:
```bash
cd aws-deployment-scripts
cp rds-credentials.example.txt rds-credentials.txt
# Edita rds-credentials.txt con las credenciales reales
```

### 3. Configurar clave SSH de AWS (si la tienes):
```bash
# Copia tu clave .pem al directorio aws-deployment-scripts/
chmod 400 aws-deployment-scripts/lannister-backend-key.pem
```

### 4. Variables de entorno requeridas en producción:
```bash
# Mínimas requeridas:
SECRET_KEY=<genera-una-clave-segura>
DEBUG=False
MYSQL_PASSWORD=<password-real>
MYSQL_HOST=<endpoint-rds-real>
```

## ⚠️ IMPORTANTE - Próximos Pasos en Git

### Commit los cambios de limpieza:
```bash
git add .gitignore
git add aws-deployment-scripts/rds-credentials.example.txt
git add aws-deployment-scripts/KEY_INSTRUCTIONS.md
git add lannister_news_api/settings.py
git commit -m "🔒 Security: Remove sensitive files and improve security practices

- Remove .pem keys, credentials, and backup files from repo
- Update .gitignore to prevent future sensitive file commits
- Refactor settings.py to use environment variables
- Add template files for credentials and keys
- Remove hardcoded passwords and endpoints"
```

### ⚠️ CRÍTICO - Limpiar el Historial de Git

Los archivos sensibles fueron removidos del índice PERO siguen en el historial de Git. Para borrarlos completamente:

```bash
# ADVERTENCIA: Esto reescribe el historial de Git
# Solo hazlo si estás seguro y coordina con tu equipo

# Opción 1: Usar git filter-repo (recomendado)
git filter-repo --path aws-deployment-scripts/lannister-backend-key.pem --invert-paths
git filter-repo --path aws-deployment-scripts/rds-credentials.txt --invert-paths

# Opción 2: Usar BFG Repo Cleaner
bfg --delete-files lannister-backend-key.pem
bfg --delete-files rds-credentials.txt

# Después de limpiar:
git push --force origin feature/PruebasDespliegueAws
```

### 🔐 Si las credenciales ya fueron expuestas:

1. **Rotar inmediatamente:**
   - Cambiar password de MySQL en RDS
   - Generar nuevo par de claves SSH en AWS
   - Generar nuevo SECRET_KEY para Django

2. **Actualizar todos los servicios** con las nuevas credenciales

## 📝 Nuevas Reglas del Equipo

1. ✅ NUNCA hacer commit de archivos `.env`
2. ✅ NUNCA hacer commit de claves `.pem`, `.key`
3. ✅ NUNCA hardcodear credenciales en código
4. ✅ SIEMPRE usar variables de entorno para datos sensibles
5. ✅ SIEMPRE revisar `git status` antes de commit
6. ✅ Usar archivos `.example` para plantillas

## 🔍 Verificar Limpieza

```bash
# Verificar que archivos sensibles están ignorados:
git status

# Verificar que .gitignore está funcionando:
git check-ignore -v aws-deployment-scripts/*.pem
git check-ignore -v aws-deployment-scripts/rds-credentials.txt

# Buscar credenciales accidentales en código:
git grep -i "password\s*=" -- "*.py" | grep -v "models.py\|migrations"
git grep -i "secret" -- "*.py"
```

## 📚 Recursos Adicionales

- [GitHub: Removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [OWASP: Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)

---
**Fecha de limpieza:** 25 de octubre de 2025
**Responsable:** Equipo de Desarrollo Lannister
