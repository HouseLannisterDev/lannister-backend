# 🤖 Guía Completa: ChatBot con IA para Noticias

Esta guía te ayudará a implementar un chatbot con inteligencia artificial entrenado con tus datos de noticias.

## 📋 Resumen de la Implementación

### Arquitectura del Sistema

```
📊 MongoDB (Noticias) → 🔄 Preprocesador → 🧠 Red Neuronal → 🤖 ChatBot → 🌐 API REST
```

### Componentes Creados

1. **`data_preprocessor.py`** - Convierte noticias en intents para entrenamiento
2. **`neural_network.py`** - Red neuronal con TensorFlow/Keras
3. **`models.py`** - Modelos Django para sesiones y mensajes
4. **`views.py`** - API REST para el chatbot
5. **`train_chatbot.py`** - Comando para entrenar el modelo

## 🚀 Pasos de Implementación

### 1. Instalar Dependencias

```bash
# En tu entorno virtual
pip install -r chatBot/requirements.txt

# Descargar datos de NLTK (primera vez)
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet')"
```

### 2. Configurar Django

Añade el chatBot a `INSTALLED_APPS` en `settings.py`:

```python
INSTALLED_APPS = [
    # ... tus apps existentes
    'chatBot',
]
```

Añade las URLs en `lannister_news_api/urls.py`:

```python
urlpatterns = [
    # ... tus URLs existentes
    path('api/chatbot/', include('chatBot.urls')),
]
```

### 3. Crear Migraciones

```bash
python manage.py makemigrations chatBot
python manage.py migrate
```

### 4. Entrenar el ChatBot

```bash
# Entrenar con 10,000 noticias (puede tomar 10-30 minutos)
python manage.py train_chatbot --news_limit 10000 --epochs 200

# Para entrenamientos más rápidos (desarrollo)
python manage.py train_chatbot --news_limit 1000 --epochs 50

# Para mejor precisión (producción)
python manage.py train_chatbot --news_limit 15000 --epochs 300
```

### 5. Probar el ChatBot

```bash
# Verificar estado del modelo
curl http://localhost:8000/api/chatbot/health/

# Enviar mensaje
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, qué noticias hay de política?"}'
```

## 📊 Datos Necesarios

### Mínimo Recomendado

- **5,000-10,000 noticias** para entrenamiento básico
- **Categorías variadas** (política, deportes, economía, etc.)
- **Títulos y descripciones** bien estructurados

### Óptimo

- **15,000+ noticias** para mejor precisión
- **10+ categorías** diferentes
- **Contenido completo** (maintext) de los artículos

## 🔧 Configuraciones Avanzadas

### Ajustar Hiperparámetros

```bash
# Más épocas para mejor aprendizaje
python manage.py train_chatbot --epochs 500

# Batch size más grande para GPU potente
python manage.py train_chatbot --batch_size 32

# Tasa de aprendizaje personalizada
python manage.py train_chatbot --learning_rate 0.005
```

### Arquitectura de Red Neuronal

El modelo usa esta arquitectura:

```
Entrada (N palabras) → Dense(256) → Dropout(0.5) → Dense(128) → Dropout(0.5) → Dense(64) → Dropout(0.3) → Salida(N intents)
```

Puedes modificar en `neural_network.py`:

- Número de capas
- Neuronas por capa
- Tasa de dropout
- Función de activación

## 📝 API Endpoints

### Principales

- `POST /api/chatbot/chat/` - Enviar mensaje al chatbot
- `GET /api/chatbot/history/` - Obtener historial de conversación
- `POST /api/chatbot/feedback/` - Enviar feedback sobre respuesta
- `GET /api/chatbot/stats/` - Estadísticas del chatbot
- `GET /api/chatbot/health/` - Verificar estado del modelo

### Ejemplo de Uso

```javascript
// Enviar mensaje
const response = await fetch("/api/chatbot/chat/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    message: "¿Qué noticias hay de deportes?",
    session_id: "optional-session-id",
  }),
});

const data = await response.json();
console.log(data.response); // Respuesta del chatbot
```

## 🎯 Tipos de Preguntas que Maneja

### Categorías Automáticas

- **Política**: "noticias de política", "qué pasa con el gobierno"
- **Deportes**: "noticias de fútbol", "resultados deportivos"
- **Economía**: "noticias económicas", "inflación"
- **Tecnología**: "noticias de tech", "inteligencia artificial"
- **Salud**: "noticias de salud", "COVID"

### Intents Generales

- **Saludo**: "hola", "buenos días"
- **Despedida**: "adiós", "gracias"
- **Búsqueda**: "últimas noticias", "qué está pasando"

## 🔄 Reentrenamiento

### Cuándo Reentrenar

- **Cada semana** con nuevas noticias
- Cuando la **precisión baje** < 80%
- Al agregar **nuevas categorías**
- Cuando el **feedback sea negativo** consistentemente

### Script de Reentrenamiento Automático

```python
# scripts/retrain_chatbot.py
import schedule
import time
from django.core.management import call_command

def retrain_weekly():
    call_command('train_chatbot', '--news_limit', '12000', '--epochs', '200')

schedule.every().week.do(retrain_weekly)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

## 📈 Monitoreo y Métricas

### Métricas Importantes

- **Precisión del modelo** (>80% recomendado)
- **Tiempo de respuesta** (<1 segundo)
- **Feedback de usuarios** (rating promedio >3.5)
- **Cobertura de intents** (% de mensajes con confianza >0.5)

### Dashboard de Métricas

```python
# En Django admin o tu dashboard
def get_chatbot_metrics():
    stats = ChatMessage.objects.aggregate(
        avg_confidence=Avg('confidence'),
        avg_response_time=Avg('response_time')
    )

    feedback_avg = ChatFeedback.objects.aggregate(
        avg_rating=Avg('rating')
    )

    return {
        'precision': stats['avg_confidence'],
        'speed': stats['avg_response_time'],
        'satisfaction': feedback_avg['avg_rating']
    }
```

## 🚨 Resolución de Problemas

### Errores Comunes

1. **"Modelo no cargado"**

   - Verifica que `chatbot_model.h5` existe
   - Reentrena el modelo con `train_chatbot`

2. **"Precisión muy baja"**

   - Aumenta número de noticias de entrenamiento
   - Aumenta épocas de entrenamiento
   - Verifica calidad de los datos

3. **"Respuestas irrelevantes"**
   - Mejora categorización de noticias
   - Añade más patrones a los intents
   - Revisa el preprocesamiento de texto

### Logs Útiles

```python
# En settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'chatbot.log',
        },
    },
    'loggers': {
        'chatBot': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## 🎨 Frontend Integration

### HTML/JS Simple

```html
<div id="chatbot">
  <div id="messages"></div>
  <input type="text" id="messageInput" placeholder="Escribe tu pregunta..." />
  <button onclick="sendMessage()">Enviar</button>
</div>

<script>
  async function sendMessage() {
    const input = document.getElementById("messageInput");
    const message = input.value.trim();

    if (!message) return;

    const response = await fetch("/api/chatbot/chat/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    displayMessage(message, data.response);
    input.value = "";
  }
</script>
```

## 🔮 Mejoras Futuras

### Nivel Intermedio

- **Análisis de sentimientos** en respuestas
- **Personalización** por usuario
- **Sugerencias automáticas** de preguntas

### Nivel Avanzado

- **Modelo transformer** (BERT, GPT)
- **Respuestas con contexto** de conversaciones previas
- **Integración con APIs externas** (weather, stocks)
- **Chatbot multimodal** (imágenes, audio)

## 📚 Recursos Adicionales

- [TensorFlow Guide](https://www.tensorflow.org/guide)
- [NLTK Documentation](https://www.nltk.org/)
- [Django REST Framework](https://www.django-rest-framework.org/)

¡Tu chatbot está listo para entrenar con tus 10,000+ noticias! 🚀
