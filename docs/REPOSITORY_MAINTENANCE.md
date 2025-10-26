# 🧹 Repository Maintenance Guide

## Archivos que NO deben estar en el repositorio

### 🔒 Credenciales y Secretos
- ❌ Archivos `.env` con credenciales reales
- ❌ Claves privadas (`.pem`, `.key`)
- ❌ Archivos de credenciales (`*credentials*.txt`)
- ❌ Tokens de API hardcodeados
- ✅ **Usar:** `.env.example` y `*credentials.example.txt`

### 📁 Archivos Generados
- ❌ `__pycache__/`
- ❌ `*.pyc`, `*.pyo`
- ❌ Archivos compilados (`.so`, `.egg`)
- ❌ HTML generado desde Markdown
- ❌ Logs de deployment
- ✅ **Estos deben generarse localmente**

### 💻 Configuraciones Personales
- ❌ `.vscode/` (configuración personal del IDE)
- ❌ `.idea/` (JetBrains IDEs)
- ❌ `.DS_Store` (macOS)
- ✅ **Cada desarrollador configura su IDE localmente**

### 📦 Dependencias
- ❌ `node_modules/`
- ❌ `.venv/`, `venv/`, `env/`
- ✅ **Usar:** `requirements.txt`, `package.json`

### 📊 Logs y Temporales
- ❌ `*.log`
- ❌ `deployment-logs/`
- ❌ Archivos temporales (`.tmp`, `.temp`, `.swp`)
- ✅ **Logs solo en producción/staging, no en repo**

---

## ✅ Archivos que SÍ deben estar en el repositorio

### 📝 Código Fuente
- ✅ Todos los archivos `.py`
- ✅ Archivos de configuración (`settings.py` sin secretos)
- ✅ Scripts de deployment (sin credenciales)

### 📚 Documentación
- ✅ `README.md`
- ✅ Documentación en `docs/`
- ✅ Guías de deployment (sin credenciales)
- ✅ Archivos `.md` (Markdown)
- ❌ Archivos `.html` generados desde `.md`

### 🔧 Configuración
- ✅ `requirements.txt`
- ✅ `.gitignore`
- ✅ `.env.example` (plantilla)
- ✅ `docker-compose.yml`
- ✅ `Dockerfile`

### 📋 Plantillas
- ✅ Archivos `.example`
- ✅ Archivos `.template`
- ✅ Configuraciones de referencia

---

## 🧹 Mantenimiento Regular

### Limpieza Mensual

```bash
# 1. Verificar archivos grandes
git ls-files -z | xargs -0 du -h | sort -hr | head -20

# 2. Buscar archivos ignorados pero trackeados
git ls-files -i --exclude-standard

# 3. Buscar posibles secretos
git grep -i "password\|secret\|key" -- "*.py" "*.sh" | grep -v ".example\|.template"

# 4. Verificar tamaño del repo
du -sh .git
```

### Antes de cada commit

```bash
# Verificar qué se va a commitear
git status

# Revisar cambios línea por línea
git diff --cached

# Verificar que no haya secretos
git diff --cached | grep -i "password\|secret\|key\|token"
```

---

## 🔍 Auditoría de Seguridad

### Escaneo con SonarQube
```bash
# Ejecutar antes de merge a main
sonar-scanner
```

### Buscar credenciales hardcodeadas
```bash
# Python files
grep -r "password\s*=\s*['\"]" --include="*.py" .

# Environment variables with defaults
grep -r "os\.getenv.*['\"].*['\"]" --include="*.py" .

# Shell scripts
grep -r "PASSWORD=" --include="*.sh" .
```

### Verificar archivos ignorados
```bash
# Ver qué archivos están siendo ignorados
git check-ignore -v *

# Ver archivos sensibles específicos
git check-ignore -v .env *.pem *credentials*.txt
```

---

## 📏 Límites Recomendados

| Tipo | Límite | Acción si se excede |
|------|--------|---------------------|
| Archivo individual | 1 MB | Usar Git LFS o almacenamiento externo |
| Modelo ML | 100 MB | Usar Git LFS o S3/external storage |
| Repositorio total | 1 GB | Limpiar historial o reorganizar |
| Commits por día | < 50 | Revisar flujo de trabajo |

---

## 🚀 Optimización del Repositorio

### Si el repo es muy grande (> 1GB)

```bash
# 1. Identificar archivos grandes en historial
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  sed -n 's/^blob //p' | \
  sort --numeric-sort --key=2 --reverse | \
  head -20

# 2. Usar Git LFS para archivos grandes
git lfs track "*.safetensors"
git lfs track "*.bin"
git lfs track "*.h5"

# 3. Limpiar historial de archivos removidos
git filter-repo --strip-blobs-bigger-than 10M
```

---

## 📋 Checklist Pre-Commit

- [ ] No hay archivos `.env` con credenciales reales
- [ ] No hay claves `.pem` o `.key`
- [ ] No hay passwords hardcodeados
- [ ] No hay logs de deployment
- [ ] No hay configuraciones personales de IDE
- [ ] Archivos grandes (<1MB) o usando Git LFS
- [ ] `.gitignore` actualizado
- [ ] Código formateado correctamente
- [ ] Tests pasan ✅

---

## 🆘 En caso de commit accidental de secretos

```bash
# 1. Si NO has hecho push
git reset HEAD~1
# Editar archivos
git add .
git commit -m "mensaje corregido"

# 2. Si YA hiciste push
# Ver SECURITY_CLEANUP.md para proceso completo
# Incluye: git filter-repo, rotación de credenciales, etc.
```

---

**Última actualización:** 26 de octubre de 2025  
**Responsable:** Equipo Lannister Dev
