# 🤖 ChatBot con IA para Noticias - Documentación Completa

## 📋 Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación de Dependencias](#instalación-de-dependencias)
3. [Configuración Inicial](#configuración-inicial)
4. [Entrenamiento del Modelo](#entrenamiento-del-modelo)
5. [Ejecución del ChatBot](#ejecución-del-chatbot)
6. [API Endpoints](#api-endpoints)
7. [Resolución de Problemas](#resolución-de-problemas)
8. [Mantenimiento](#mantenimiento)

## 🔧 Requisitos del Sistema

### Software Necesario

- **Python 3.8+** (Recomendado: Python 3.10 o superior)
- **MongoDB** (con datos de noticias)
- **MySQL** (para Django)
- **Git** (para control de versiones)

### Hardware Recomendado

- **RAM**: Mínimo 8GB (Recomendado: 16GB)
- **Almacenamiento**: 5GB libres
- **CPU**: Multinúcleo (El entrenamiento puede ser intensivo)

### Verificar Versiones

```bash
python --version          # Debe ser 3.8+
mongod --version          # Verificar MongoDB
mysql --version           # Verificar MySQL
```

## 📦 Instalación de Dependencias

### 1. Clonar el Repositorio

```bash
git clone https://github.com/HouseLannisterDev/lannister-backend.git
cd lannister-backend
```

### 2. Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate
# En Windows:
venv\Scripts\activate
```

### 3. Instalar Dependencias Base de Django

```bash
pip install -r requirements.txt
```

### 4. Instalar Dependencias de Machine Learning

```bash
pip install tensorflow keras numpy scikit-learn nltk textblob pandas matplotlib
```

### 5. Descargar Datos de NLTK

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('wordnet')"
```

### 6. Instalar Corpus de TextBlob (Opcional)

```bash
python -m textblob.download_corpora
```

## ⚙️ Configuración Inicial

### 1. Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Django
DJANGO_SECRET_KEY=tu-clave-secreta-aqui
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# MySQL
MYSQL_DB=lannister_news
MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_password
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306

# MongoDB
MONGO_NAME=lannister_news
MONGO_HOST=localhost
MONGO_PORT=27017
# O si usas MongoDB Atlas:
# MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/dbname

# News Scraper
NEWS_SOURCES=cnn.com,bbc.com,elpais.com
NEWS_REQ_DELAY_MIN=3
NEWS_REQ_DELAY_MAX=8
NEWS_MAX_RETRIES=3
```

### 2. Configurar Base de Datos

```bash
# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 3. Verificar Datos en MongoDB

```bash
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lannister_news_api.settings')
django.setup()

from mongo_client import get_mongo_client
db = get_mongo_client()
count = db.news.count_documents({})
print(f'📊 Total de noticias en MongoDB: {count}')

if count == 0:
    print('⚠️  No hay noticias. Ejecuta el scraper primero.')
else:
    print('✅ Datos listos para entrenamiento')
"
```

## 🧠 Entrenamiento del Modelo

### 1. Entrenamiento Básico (Desarrollo)

```bash
# Entrenamiento rápido para pruebas (5-10 minutos)
python manage.py train_chatbot --news_limit 1000 --epochs 50 --batch_size 8
```

### 2. Entrenamiento Estándar (Producción)

```bash
# Entrenamiento completo (15-30 minutos)
python manage.py train_chatbot --news_limit 2000 --epochs 200 --batch_size 8
```

### 3. Entrenamiento Optimizado (Mejor Precisión)

```bash
# Entrenamiento con todos los datos (30-60 minutos)
python manage.py train_chatbot --news_limit 5000 --epochs 300 --batch_size 16
```

### 4. Parámetros del Comando de Entrenamiento

```bash
python manage.py train_chatbot [opciones]

Opciones:
  --news_limit INTEGER    # Número máximo de noticias a procesar (default: 10000)
  --epochs INTEGER        # Número de épocas de entrenamiento (default: 200)
  --batch_size INTEGER    # Tamaño del lote (default: 8)
  --learning_rate FLOAT   # Tasa de aprendizaje (default: 0.01)
  --force                 # Forzar reentrenamiento
```

### 5. Métricas de Éxito

El entrenamiento debe mostrar:

- **Precisión final**: > 80% (Objetivo: > 85%)
- **Precisión de validación**: > 75%
- **Pérdida final**: < 0.5 (Objetivo: < 0.3)

### 6. Archivos Generados

Después del entrenamiento exitoso:

```
chatbot_model.h5        # Modelo de red neuronal entrenado
words.pkl              # Vocabulario procesado
classes.pkl            # Clasificaciones/intents
intents_spanish.json   # Intents generados desde las noticias
```

## 🚀 Ejecución del ChatBot

### 1. Prueba Interactiva (Línea de Comandos)

```bash
# Probar chatbot en modo consola
python test_chatbot.py --interactive
```

### 2. Servidor API REST

```bash
# Iniciar servidor Django
python manage.py runserver 8000

# El chatbot estará disponible en:
# http://localhost:8000/api/chatbot/
```

### 3. Verificar Estado del ChatBot

```bash
# Health check
curl http://localhost:8000/api/chatbot/health/

# Respuesta esperada:
{
  "status": "healthy",
  "model_loaded": true,
  "test_response": "¡Hola! Soy tu asistente..."
}
```

## 🔌 API Endpoints

### Endpoints Principales

#### 1. Chat Principal

```http
POST /api/chatbot/chat/
Content-Type: application/json

{
  "message": "Hola, qué noticias hay de deportes?",
  "session_id": "opcional-session-id"
}
```

**Respuesta:**

```json
{
  "response": "Aquí tienes las últimas noticias deportivas...",
  "session_id": "248288d0-d361-48af-b29b-48b90ca1c4e8",
  "message_id": 1,
  "intent": "deportes",
  "confidence": 0.89,
  "response_time": 0.022
}
```

#### 2. Historial de Chat

```http
GET /api/chatbot/history/?session_id=SESSION_ID&limit=20
```

#### 3. Feedback del Usuario

```http
POST /api/chatbot/feedback/
Content-Type: application/json

{
  "message_id": 1,
  "rating": 5,
  "feedback_text": "Respuesta muy útil"
}
```

#### 4. Estadísticas

```http
GET /api/chatbot/stats/
```

#### 5. Health Check

```http
GET /api/chatbot/health/
```

### Ejemplos de Uso

#### JavaScript/Frontend

```javascript
// Enviar mensaje al chatbot
async function sendMessage(message, sessionId = null) {
  const response = await fetch("/api/chatbot/chat/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      session_id: sessionId,
    }),
  });

  return await response.json();
}

// Ejemplo de uso
sendMessage("Hola, qué noticias hay?").then((data) => {
  console.log("Bot:", data.response);
  console.log("Confianza:", data.confidence);
});
```

#### Python/Backend

```python
import requests

# Enviar mensaje
response = requests.post('http://localhost:8000/api/chatbot/chat/',
                        json={'message': 'Últimas noticias de tecnología'})
data = response.json()
print(f"Bot: {data['response']}")
```

#### cURL

```bash
# Enviar mensaje
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Noticias de política"}'

# Ver estadísticas
curl http://localhost:8000/api/chatbot/stats/
```

## 🐛 Resolución de Problemas

### Problemas Comunes

#### 1. Error: "No module named 'tensorflow'"

```bash
# Solución
pip install tensorflow keras numpy
```

#### 2. Error: "NLTK data not found"

```bash
# Solución
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet')"
```

#### 3. Error: "No se puede conectar a MongoDB"

```bash
# Verificar MongoDB
mongod --version
mongo --eval "db.adminCommand('listCollections')"

# Verificar configuración en settings.py
python -c "
from django.conf import settings
print(settings.MONGO_DB)
"
```

#### 4. Error: "Precisión muy baja (< 50%)"

**Posibles causas:**

- Pocos datos de entrenamiento
- Datos de mala calidad
- Épocas insuficientes

**Soluciones:**

```bash
# Más datos
python manage.py train_chatbot --news_limit 3000

# Más épocas
python manage.py train_chatbot --epochs 300

# Verificar calidad de datos
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lannister_news_api.settings')
django.setup()
from chatBot.data_preprocessor import NewsDataPreprocessor
processor = NewsDataPreprocessor()
stats = processor.get_news_statistics()
print(stats)
"
```

#### 5. Error: "Model not found"

```bash
# Reentrenar modelo
python manage.py train_chatbot --force

# Verificar archivos
ls -la *.h5 *.pkl *.json
```

### Logs y Debugging

#### Activar Logs Detallados

En `settings.py`:

```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'chatbot.log',
        },
    },
    'loggers': {
        'chatBot': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
```

#### Ver Logs en Tiempo Real

```bash
tail -f chatbot.log
```

## 🔄 Mantenimiento

### 1. Reentrenamiento Periódico

#### Reentrenamiento Semanal (Recomendado)

```bash
# Crear script de reentrenamiento
cat > retrain_weekly.sh << 'EOF'
#!/bin/bash
cd /ruta/a/lannister-backend
source venv/bin/activate
python manage.py train_chatbot --news_limit 3000 --epochs 150
EOF

chmod +x retrain_weekly.sh

# Programar con cron (cada domingo a las 2 AM)
echo "0 2 * * 0 /ruta/a/retrain_weekly.sh" | crontab -
```

#### Reentrenamiento Automático con Nuevas Noticias

```python
# scripts/auto_retrain.py
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lannister_news_api.settings')
django.setup()

from mongo_client import get_mongo_client
from django.core.management import call_command

def should_retrain():
    db = get_mongo_client()

    # Verificar si hay noticias nuevas en la última semana
    week_ago = datetime.now() - timedelta(days=7)
    new_count = db.news.count_documents({
        'scraped_at': {'$gte': week_ago}
    })

    return new_count > 100  # Reentrenar si hay más de 100 noticias nuevas

if should_retrain():
    print("🔄 Iniciando reentrenamiento automático...")
    call_command('train_chatbot', '--news_limit', '3000', '--epochs', '200')
    print("✅ Reentrenamiento completado")
else:
    print("ℹ️ No se requiere reentrenamiento")
```

### 2. Monitoreo de Rendimiento

#### Script de Monitoreo

```python
# scripts/monitor_chatbot.py
import requests
import time
from datetime import datetime

def monitor_chatbot():
    try:
        # Health check
        response = requests.get('http://localhost:8000/api/chatbot/health/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {datetime.now()}: ChatBot healthy")
            return True
        else:
            print(f"❌ {datetime.now()}: ChatBot unhealthy - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {datetime.now()}: Error - {e}")
        return False

# Monitoreo continuo
while True:
    monitor_chatbot()
    time.sleep(300)  # Cada 5 minutos
```

### 3. Backup del Modelo

#### Backup Automático

```bash
# Crear backup del modelo entrenado
backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $backup_dir
cp chatbot_model.h5 words.pkl classes.pkl intents_spanish.json $backup_dir/
echo "✅ Backup creado en $backup_dir"
```

### 4. Actualización de Dependencias

#### Verificar Actualizaciones

```bash
pip list --outdated

# Actualizar dependencias críticas
pip install --upgrade tensorflow keras numpy
```

## 📊 Métricas y Análisis

### Dashboard de Métricas

```python
# Acceder a métricas vía API
import requests

stats = requests.get('http://localhost:8000/api/chatbot/stats/').json()
print(f"Total mensajes: {stats['total_messages']}")
print(f"Sesiones activas: {stats['active_sessions']}")
print(f"Tiempo promedio respuesta: {stats['avg_response_time']}s")
```

### Análisis de Uso

```python
# scripts/analyze_usage.py
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lannister_news_api.settings')
django.setup()

from chatBot.models import ChatMessage
from django.db.models import Count, Avg

# Intents más utilizados
popular_intents = ChatMessage.objects.values('intent').annotate(
    count=Count('id')
).order_by('-count')[:10]

print("📊 Intents más populares:")
for intent in popular_intents:
    print(f"  {intent['intent']}: {intent['count']} mensajes")

# Confianza promedio por intent
confidence_by_intent = ChatMessage.objects.values('intent').annotate(
    avg_confidence=Avg('confidence')
).order_by('-avg_confidence')

print("\n📈 Confianza promedio por intent:")
for item in confidence_by_intent:
    print(f"  {item['intent']}: {item['avg_confidence']:.2f}")
```

## 🎯 Optimización de Rendimiento

### 1. Optimización del Modelo

```python
# En neural_network.py, experimenta con:
- Más capas: Dense(512), Dense(256), Dense(128)
- Diferentes activaciones: 'relu', 'tanh', 'sigmoid'
- Ajustar dropout: 0.3, 0.5, 0.7
- Learning rate: 0.001, 0.01, 0.1
```

### 2. Cache de Respuestas

```python
# En settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# En views.py
from django.core.cache import cache

def get_cached_response(message):
    cache_key = f"chatbot:{hash(message)}"
    return cache.get(cache_key)

def cache_response(message, response):
    cache_key = f"chatbot:{hash(message)}"
    cache.set(cache_key, response, 3600)  # 1 hora
```

### 3. Optimización de Base de Datos

```python
# Índices recomendados en MongoDB
db.news.createIndex({"category": 1})
db.news.createIndex({"scraped_at": -1})
db.news.createIndex({"source_domain": 1})
```

---

## 🚀 Inicio Rápido (Resumen)

Para usuarios que ya tienen el entorno configurado:

```bash
# 1. Activar entorno
source venv/bin/activate

# 2. Instalar dependencias ML (primera vez)
pip install tensorflow keras numpy scikit-learn nltk textblob

# 3. Descargar datos NLTK (primera vez)
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet')"

# 4. Aplicar migraciones (primera vez)
python manage.py makemigrations chatBot
python manage.py migrate

# 5. Entrenar modelo
python manage.py train_chatbot --news_limit 2000 --epochs 200

# 6. Iniciar servidor
python manage.py runserver 8000

# 7. Probar
curl http://localhost:8000/api/chatbot/health/
```

**¡Tu ChatBot con IA está listo para funcionar!** 🤖✨
