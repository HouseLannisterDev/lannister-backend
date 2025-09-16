# 📰 Lannister News API + 🤖 ChatBot con IA

API completa en Django/DRF con MySQL, Redis, web scraping de noticias y **ChatBot inteligente** entrenado con Machine Learning.

## 🌟 Características Principales

### 🔐 Sistema de Autenticación

- Autenticación basada en sesiones con cookies
- Gestión de usuarios y favoritos
- CSRF protection

### � Web Scraping de Noticias

- Scraping automático de múltiples fuentes
- Almacenamiento en MongoDB
- Categorización automática

### 🤖 **ChatBot con Inteligencia Artificial**

- **Red neuronal** entrenada con TensorFlow/Keras
- **Procesamiento de lenguaje natural** con NLTK
- **Respuestas contextuales** basadas en noticias reales
- **API REST** para integración con frontend
- **Entrenamiento automático** con datos de noticias

## 🚀 Instalación Rápida

### Opción 1: Instalación Automática (Recomendada)

```bash
git clone https://github.com/HouseLannisterDev/lannister-backend.git
cd lannister-backend
./install_chatbot.sh
```

### Opción 2: Instalación Manual

```bash
# 1. Entorno virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux
# .\venv\Scripts\Activate.ps1  # Windows

# 2. Dependencias
pip install -r requirements.txt
pip install tensorflow keras numpy scikit-learn nltk textblob

# 3. Configuración
cp .env.example .env
python manage.py migrate

# 4. Entrenar ChatBot
python manage.py train_chatbot --news_limit 2000 --epochs 200

# 5. Iniciar servidor
python manage.py runserver
```

## 🤖 Uso del ChatBot

### Entrenamiento

```bash
# Entrenamiento básico (5-10 min)
./train_chatbot.sh 1000 50

# Entrenamiento completo (15-30 min)
./train_chatbot.sh 2000 200

# Entrenamiento optimizado (30-60 min)
./train_chatbot.sh 5000 300
```

### Prueba Interactiva

```bash
./test_chatbot.sh
```

### API REST

```bash
# Health check
curl http://localhost:8000/api/chatbot/health/

# Enviar mensaje
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, qué noticias hay de deportes?"}'
```

## 📋 Requisitos del Sistema

### Software Necesario

- **Python 3.8+** (Recomendado: 3.10+)
- **MySQL 8** (para Django)
- **MongoDB** (para noticias)
- **Redis** (para cache y sesiones)
- **Git**

### Hardware Recomendado

- **RAM**: Mínimo 8GB (Recomendado: 16GB)
- **CPU**: Multinúcleo (para entrenamiento de IA)
- **Almacenamiento**: 5GB libres

## 🎯 Estructura del Proyecto

```
lannister-backend/
├── 🤖 chatBot/                 # ChatBot con IA
│   ├── models.py              # Modelos Django (sesiones, mensajes)
│   ├── neural_network.py      # Red neuronal con TensorFlow
│   ├── data_preprocessor.py   # Preprocesamiento de noticias
│   ├── views.py               # API REST del chatbot
│   └── management/commands/
│       └── train_chatbot.py   # Comando de entrenamiento
├── 📰 news/                   # Web scraping de noticias
├── 👥 users/                  # Gestión de usuarios
├── ⚙️ lannister_news_api/     # Configuración Django
├── 📖 DOCUMENTACION_CHATBOT.md # Documentación completa
├── 🚀 install_chatbot.sh      # Script de instalación
├── 🎯 train_chatbot.sh        # Script de entrenamiento
└── 🧪 test_chatbot.sh         # Script de pruebas
```

## 📡 Endpoints Principales

### 🔐 Autenticación

- Python 3.12/3.13
- MySQL 8
- Docker Desktop (opcional, para Redis)
- Git

## Setup rápido (dev)

````bash
git clone <repo>
cd lannister-backend

# entorno
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt

# variables de entorno
cp .env.example .env
# (ajusta credenciales si es necesario)

# Redis (Docker)
docker compose up -d

# Migraciones
py manage.py migrate
py manage.py migrate sessions

# Usuario admin (opcional)
py manage.py createsuperuser

# Run
py manage.py runserver

### 🔐 Autenticación
```http
GET  /users/auth/csrf/         # Obtener token CSRF
POST /users/auth/login/        # Iniciar sesión
GET  /users/auth/me/           # Estado de sesión
POST /users/auth/logout/       # Cerrar sesión
````

### 👥 Usuarios

```http
GET  /users/                   # Listar usuarios
POST /users/                   # Crear usuario
GET  /users/{id}/              # Obtener usuario
PATCH/PUT/DELETE /users/{id}/  # Modificar/eliminar usuario
```

### 🤖 ChatBot con IA

```http
POST /api/chatbot/chat/        # Enviar mensaje al chatbot
GET  /api/chatbot/history/     # Historial de conversación
POST /api/chatbot/feedback/    # Feedback de respuesta
GET  /api/chatbot/stats/       # Estadísticas del chatbot
GET  /api/chatbot/health/      # Estado del modelo de IA
```

### 📰 Noticias

```http
GET  /news/                    # Listar noticias
GET  /news/random/             # Noticias aleatorias
GET  /news/sources/            # Fuentes disponibles
```

## 🧠 Capacidades del ChatBot

### 📊 Datos de Entrenamiento

- Entrenado con **2,000+ noticias reales**
- **5 categorías principales**: Deportes, Tecnología, Animales, Judiciales, Moda
- **Precisión del modelo**: 89%+
- **Tiempo de respuesta**: <50ms

### 💬 Tipos de Consultas

- **Saludos**: "Hola", "Buenos días"
- **Búsqueda por categoría**: "Noticias de deportes"
- **Búsqueda general**: "Últimas noticias"
- **Ayuda**: "¿Qué puedes hacer?"
- **Despedidas**: "Adiós", "Gracias"

### 🎯 Respuestas Inteligentes

- **Noticias específicas** de tu base de datos
- **Clasificación automática** de intenciones
- **Confianza medible** en cada respuesta
- **Gestión de sesiones** para contexto
- **Feedback de usuarios** para mejora continua

## 📖 Documentación Completa

Para información detallada sobre instalación, configuración, entrenamiento y resolución de problemas:

📚 **[DOCUMENTACION_CHATBOT.md](DOCUMENTACION_CHATBOT.md)**

## 🔄 Scripts de Automatización

### 🚀 Instalación y Setup

```bash
./install_chatbot.sh           # Instalación completa automatizada
```

### 🧠 Entrenamiento

```bash
./train_chatbot.sh             # Entrenamiento con parámetros por defecto
./train_chatbot.sh 3000 300 16 # Entrenamiento personalizado (noticias, épocas, batch_size)
```

### 🧪 Pruebas

```bash
./test_chatbot.sh              # Prueba interactiva del chatbot
./start_chatbot.sh             # Inicio rápido del servidor
```

## 🔧 Desarrollo y Mantenimiento

### Reentrenamiento Automático

```bash
# Reentrenar semanalmente con nuevas noticias
python manage.py train_chatbot --news_limit 3000 --epochs 200
```

### Monitoreo del Modelo

```bash
# Verificar estado del chatbot
curl http://localhost:8000/api/chatbot/health/

# Ver estadísticas de uso
curl http://localhost:8000/api/chatbot/stats/
```

### Backup del Modelo

```bash
# Crear backup de archivos del modelo
mkdir backup_$(date +%Y%m%d)
cp chatbot_model.h5 words.pkl classes.pkl intents_spanish.json backup_$(date +%Y%m%d)/
```

## 📌 Estructura de Ramas en Git

Para garantizar un desarrollo organizado y eficiente, utilizamos **Git Flow** como estrategia de control de versiones. Este flujo nos permite mantener la estabilidad del código en producción mientras facilitamos el desarrollo de nuevas funcionalidades.

---

## 🔹 Ramas Principales (Persistentes)

Estas ramas **nunca se eliminan** y representan los estados clave del proyecto.

### `main` (Producción)

✅ Contiene la versión estable y en producción del sistema.
✅ Solo se actualiza mediante **merge desde `develop`** cuando se lanza una versión final.
✅ No se realizan desarrollos directos en esta rama.

```sh
# Fusionar cambios de develop a main cuando una versión está lista
git checkout main
git merge develop
```

---

### `develop` (Desarrollo)

✅ Contiene el código en desarrollo y pruebas.
✅ Recibe los cambios de las ramas `feature/*`.
✅ Se mantiene siempre funcional para evitar bloqueos en el equipo.

```sh
# Crear una nueva rama de desarrollo desde develop
git checkout develop
```

---

## 🌱 Ramas Temporales (Se eliminan al finalizar)

Estas ramas son **temporales** y se crean según la necesidad.

### `feature/*` (Nuevas Funcionalidades)

📌 Se crean desde `develop` para desarrollar nuevas funcionalidades.
📌 Una vez terminadas, se fusionan en `develop` y se eliminan.

```sh
# Crear una nueva rama para una funcionalidad
git checkout develop
git checkout -b feature/nueva-funcionalidad
```

Después de finalizar el desarrollo:

```sh
git checkout develop
git merge feature/nueva-funcionalidad
git branch -d feature/nueva-funcionalidad
```

---

### `hotfix/*` (Correcciones Urgentes en Producción)

📌 Se crean desde `main` para corregir errores críticos.
📌 Se fusionan en `main` y `develop` y luego se eliminan.

```sh
# Crear una rama hotfix para corregir un error crítico
git checkout main
git checkout -b hotfix/fix-login
```

Después de aplicar el fix:

```sh
git checkout main
git merge hotfix/fix-login
git checkout develop
git merge hotfix/fix-login
git branch -d hotfix/fix-login
```

---

### `release/*` (Preparación de Nueva Versión)

📌 Se crean desde `develop` cuando se prepara una nueva versión para producción.
📌 Se usa para **pruebas finales** y ajustes antes de lanzar la versión.
📌 Se fusiona en `main` y `develop` y luego se elimina.

```sh
# Crear una rama de versión
 git checkout develop
 git checkout -b release/v1.0.0
```

Después de pruebas y ajustes:

```sh
git checkout main
git merge release/v1.0.0
git tag v1.0.0  # Etiquetar la versión
git checkout develop
git merge release/v1.0.0
git branch -d release/v1.0.0
```

---

## 🎯 Resumen Visual del Flujo de Ramas

```plaintext
  main  <-- (Código estable y en producción)
   │
   ├── develop  <-- (Código en desarrollo)
   │      │
   │      ├── feature/nueva-funcionalidad  <-- (Rama para nuevas funcionalidades)
   │      │
   │      ├── feature/otra-funcionalidad
   │
   ├── release/v1.0.0  <-- (Preparación de versión para producción)
   │
   ├── hotfix/fix-crash  <-- (Corrección urgente en producción)
```

---

## 🔥 Beneficios de esta forma de trabajo:

✅ **Organización clara:** Cada tipo de cambio tiene su propia rama.
✅ **Menos errores en producción:** Se prueban los cambios antes de fusionarlos en `main`.
✅ **Trabajo en equipo optimizado:** Varios desarrolladores pueden trabajar simultáneamente.
✅ **Facilidad para revertir cambios:** Si un error se introduce, se puede volver a una versión estable fácilmente.

---

## 📝 Reglas Generales del Equipo

📌 **Nunca** hagas commits directamente en `main` o `develop`.
📌 Cada feature, fix o release debe estar en su propia rama.
📌 Usa nombres descriptivos para las ramas (`feature/login`, `hotfix/fix-email`).
📌 Antes de hacer un merge, asegúrate de actualizar tu rama con los últimos cambios de `develop`.

```sh
git pull origin develop
```

📌 Realiza **Pull Requests** en GitHub antes de fusionar cambios en `develop`.
📌 Usa `git tag` para marcar versiones en producción (`v1.0.0`).

---
