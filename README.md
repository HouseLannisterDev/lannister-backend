# 🦁 Lannister News API

API REST desarrollada con Django/DRF + MySQL + Redis para gestión de noticias, usuarios y chatbot inteligente.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalación Rápida](#-instalación-rápida)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Documentación](#-documentación)
- [Flujo de Trabajo Git](#-flujo-de-trabajo-git)

## ✨ Características

- 🔐 Autenticación con sesiones persistentes (Redis)
- 📰 API REST para gestión de noticias
- 👥 Gestión de usuarios y favoritos
- 🤖 Chatbot inteligente con búsqueda de noticias
- 🐳 Containerización con Docker
- ☁️ Deployment en AWS (EC2, RDS, ElastiCache)

## 🛠️ Requisitos

- Python 3.12+
- MySQL 8.0+
- Redis 6.0+
- Docker Desktop (opcional)
- Git

## 🚀 Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/HouseLannisterDev/lannister-backend.git
cd lannister-backend

# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Iniciar Redis (Docker)
docker-compose -f deploy/docker-compose.yml up -d

# Migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Iniciar servidor de desarrollo
python manage.py runserver
```

## 📁 Estructura del Proyecto

```
lannister-backend/
├── 📄 manage.py                    # Django management
├── 📄 requirements.txt             # Dependencias Python
├── 📁 docs/                        # 📚 Documentación completa
│   ├── api/                        # Documentación de APIs
│   ├── deployment/                 # Guías de deployment
│   ├── testing/                    # Guías de testing
│   └── security/                   # Documentación de seguridad
├── 📁 scripts/                     # 🔧 Scripts de utilidad
│   ├── deploy-aws.sh              # Deploy a AWS
│   ├── start-local.sh             # Inicio local
│   └── chatbot_standalone_server.py
├── 📁 deploy/                      # 🐳 Configuración deployment
│   ├── Dockerfile                  # Docker development
│   ├── Dockerfile.prod             # Docker production
│   ├── docker-compose.yml          # Orquestación servicios
│   ├── nginx.conf                  # Configuración Nginx
│   └── supervisord.conf            # Configuración Supervisor
├── 📁 aws-deployment-scripts/      # Scripts específicos AWS
├── 📁 lannister_news_api/          # Django project settings
├── 📁 users/                       # App de usuarios
├── 📁 news/                        # App de noticias
├── 📁 chatbot/                     # App de chatbot
└── 📁 .venv/                       # Entorno virtual (local)
```

## 🔌 API Endpoints Principales

### Autenticación (Sesiones)
```http
GET  /users/auth/csrf/     # Obtener token CSRF
POST /users/auth/login/    # Login (requiere X-CSRFToken)
GET  /users/auth/me/       # Estado de sesión
POST /users/auth/logout/   # Cerrar sesión
```

### Usuarios
```http
GET    /users/           # Listar usuarios
POST   /users/           # Crear usuario
GET    /users/{id}/      # Detalle usuario
PATCH  /users/{id}/      # Actualizar usuario
DELETE /users/{id}/      # Eliminar usuario
```

### Favoritos
```http
GET    /users/favorites/      # Listar favoritos
POST   /users/favorites/      # Agregar favorito
DELETE /users/favorites/{id}/ # Eliminar favorito
```

### Chatbot
```http
POST /chatbot/chat/      # Enviar mensaje al chatbot
POST /chatbot/search/    # Buscar noticias
```

> 📖 Para documentación completa de la API, ver [docs/api/API_Documentation.md](./docs/api/API_Documentation.md)

## 📚 Documentación

### 🏗️ Arquitectura
- **[Diagrama de Componentes](./docs/architecture/COMPONENT_DIAGRAM.md)** - Componentes UML y detalles técnicos
- **[Arquitectura General](./docs/architecture/ARCHITECTURE_OVERVIEW.md)** - Visión de alto nivel y despliegue AWS

### 📖 Guías Técnicas
- **[Documentación de API](./docs/api/API_Documentation.md)** - Endpoints y ejemplos completos
- **[Guía de Deployment AWS](./docs/deployment/DEPLOY_AWS_GUIDE.md)** - Deploy paso a paso en AWS
- **[Guía de Testing](./docs/testing/POSTMAN_TESTING_GUIDE.md)** - Testing con Postman
- **[Seguridad](./docs/security/SECURITY_CLEANUP.md)** - Mejores prácticas de seguridad
- **[Mantenimiento del Repositorio](./docs/REPOSITORY_MAINTENANCE.md)** - Guía de mantenimiento

## 🐳 Docker

### Development:
```bash
docker-compose -f deploy/docker-compose.yml up
```

### Production:
```bash
docker build -f deploy/Dockerfile.prod -t lannister-backend:prod .
docker run -p 8000:8000 lannister-backend:prod
```

## 📌 Flujo de Trabajo Git

Utilizamos **Git Flow** para mantener el código organizado y estable.

### Ramas Principales (Persistentes)

- **`main`** - Código en producción (estable)
- **`develop`** - Código en desarrollo (integración continua)

### Ramas Temporales

- **`feature/*`** - Nuevas funcionalidades (desde `develop`)
- **`hotfix/*`** - Correcciones urgentes (desde `main`)
- **`release/*`** - Preparación de versiones (desde `develop`)

### Ejemplo: Nueva Funcionalidad
```bash
# Crear feature desde develop
git checkout develop
git checkout -b feature/nueva-funcionalidad

# Desarrollar y commit
git add .
git commit -m "feat: descripción de la funcionalidad"

# Merge a develop
git checkout develop
git merge feature/nueva-funcionalidad
git branch -d feature/nueva-funcionalidad
```

### Reglas del Equipo
- ✅ **Nunca** commit directo en `main` o `develop`
- ✅ Usar nombres descriptivos para ramas
- ✅ Pull Requests para merge a `develop`
- ✅ Tags para versiones (`v1.0.0`)

## 👥 Equipo

**House Lannister Dev Team**

## 📝 Licencia

Este proyecto es privado y propiedad de House Lannister Development.

---

<p align="center">Made with ❤️ by House Lannister Dev Team</p>
