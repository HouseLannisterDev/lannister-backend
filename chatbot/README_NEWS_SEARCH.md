# 🤖 Chatbot con Búsqueda de Noticias - Lannister News

## 📋 Descripción

Este chatbot ahora es **híbrido**: responde FAQs estáticas Y busca noticias dinámicamente en MongoDB.

### ✨ Nuevas Características

1. **FAQ #18**: Detecta preguntas como "dame noticias de deportes"
2. **Búsqueda en MongoDB**: Consulta noticias reales por categoría
3. **Respuestas dinámicas**: Retorna noticias con título, descripción y enlace
4. **Bilingüe**: Funciona en español e inglés

---

## 🏗️ Arquitectura

```
Usuario: "dame noticias de tecnología"
    ↓
ChatbotService
    ↓
BERT clasifica → FAQ #18 (busqueda_noticias)
    ↓
NewsSearchService
    ↓
- Extrae categoría: "tecnologia"
- Consulta MongoDB
- Formatea respuesta
    ↓
Retorna 5 noticias de tecnología
```

---

## 🚀 Entrenar el Modelo

### 1. Instalar dependencias (si no las tienes)

```bash
pip install transformers torch scikit-learn
```

### 2. Ejecutar entrenamiento

```bash
python chatbot/train_chatbot.py
```

**Esto va a:**
- Cargar las 18 FAQs (incluyendo la nueva de búsqueda de noticias)
- Entrenar BERT por 8 épocas
- Guardar el modelo en `chatbot/faq_model_2/`
- Mostrar accuracy final (~85%+)

**⏱️ Tiempo estimado:**
- CPU: ~15-20 minutos
- GPU: ~3-5 minutos

---

## 🧪 Probar el Chatbot

### Opción 1: Desde la API

```bash
# Iniciar servidor
python manage.py runserver

# En otra terminal, probar:
curl -X POST http://localhost:8000/chatbot/ \
  -H "Content-Type: application/json" \
  -d '{"question": "dame noticias de deportes"}'
```

### Opción 2: Desde Python

```python
from chatbot.services.chatbot_factory import ChatbotFactory

service = ChatbotFactory.create()
result = service.get_answer("muéstrame tecnología")

print(result["answer"])
print(f"Tipo: {result['type']}")  # "news_search"
print(f"Categoría: {result['category']}")  # "tecnologia"
```

---

## 📊 Categorías Soportadas

El chatbot puede buscar noticias en:

1. **deportes** (sports)
2. **moda** (fashion)
3. **tecnologia** (technology)
4. **animales** (animals)
5. **judiciales** (judicial)

### Ejemplos de preguntas:

**Español:**
- "dame noticias de deportes"
- "muéstrame moda"
- "quiero ver tecnología"
- "últimas de animales"
- "búscame judiciales"

**Inglés:**
- "give me sports news"
- "show me fashion"
- "i want to see tech news"
- "latest animals"
- "search judicial"

---

## 🔧 Archivos Modificados

### Nuevos archivos:
- `chatbot/services/news_search_service.py` - Servicio de búsqueda
- `chatbot/train_chatbot.py` - Script de entrenamiento

### Archivos actualizados:
- `chatbot/faqs/faqs.json` - FAQ #18 agregada
- `chatbot/faqs/faqs_normalized.json` - FAQ #18 normalizada
- `chatbot/services/chatbot_service.py` - Integración de búsqueda
- `chatbot/views.py` - Respuesta expandida con metadata

---

## 📝 Formato de Respuesta

### FAQ Normal

```json
{
  "question": "¿Qué es Lannister News?",
  "answer": "Lannister News es una plataforma...",
  "confidence": 0.952,
  "type": "faq",
  "category": null,
  "news_count": null
}
```

### Búsqueda de Noticias

```json
{
  "question": "dame noticias de deportes",
  "answer": "📰 Aquí tienes las últimas noticias de DEPORTES:\n\n**1. Título noticia**\n   Descripción...\n   🔗 [Leer más](url)",
  "confidence": 0.891,
  "type": "news_search",
  "category": "deportes",
  "news_count": 5
}
```

---

## ⚙️ Configuración

### Ajustar umbral de confianza

En `lannister_news_api/settings.py`:

```python
FALLOVER_THRESHOLD = 0.60  # Mínimo 60% de confianza
```

### Cambiar número de noticias

En `chatbot/services/news_search_service.py`:

```python
def search_news(self, category: str, limit: int = 5):  # Cambiar limit
```

---

## 🐛 Solución de Problemas

### Error: "No module named 'transformers'"
```bash
pip install transformers torch
```

### Error: "No se encontraron noticias"
- Verifica que MongoDB tenga noticias en esa categoría
- Verifica la conexión a MongoDB en settings.py

### Accuracy bajo después de entrenar
- Asegúrate de que `faqs_normalized.json` esté correctamente lematizado
- Aumenta el número de épocas en `train_chatbot.py`
- Considera agregar más preguntas de ejemplo

---

## 📈 Próximas Mejoras

- [ ] Filtros por fecha (últimas 24h, última semana)
- [ ] Búsqueda por palabras clave específicas
- [ ] Contexto conversacional (recordar preguntas previas)
- [ ] Integración con GPT para respuestas más naturales
- [ ] A/B testing de respuestas

---

## 👥 Equipo

Desarrollado por: Stiven Pabón, Wilson Moreno, Samuel Arango, Sergio Sanabria
