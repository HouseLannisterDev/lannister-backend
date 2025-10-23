# 🧪 Guía de Pruebas del Chatbot

## 📋 Preparación

### 1. Asegúrate de tener el modelo entrenado

```bash
# Si aún no has entrenado:
source .venv/bin/activate
python chatbot/train_chatbot.py
```

### 2. Verifica que MongoDB esté corriendo

```bash
# Si usas Docker:
docker compose up -d

# O verifica tu conexión MongoDB en settings.py
```

---

## 🖥️ Opción 1: Pruebas Locales (Sin Servidor)

### Ejecutar script de prueba

```bash
source .venv/bin/activate
python chatbot/test_chatbot_local.py
```

### Opciones disponibles:

1. **Probar FAQs estáticas** - Prueba preguntas como "¿Qué es Lannister News?"
2. **Probar búsqueda de noticias** - Prueba "dame noticias de deportes"
3. **Probar todo** - Ejecuta todas las pruebas
4. **Modo interactivo** - Escribe tus propias preguntas

---

## 🌐 Opción 2: Pruebas con Servidor (Localhost)

### 1. Iniciar el servidor Django

```bash
source .venv/bin/activate
python manage.py runserver
```

El servidor estará en: `http://localhost:8000`

### 2. Probar con curl

#### FAQ Estática:
```bash
curl -X POST http://localhost:8000/chatbot/ \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Qué es Lannister News?"}'
```

#### Búsqueda de Noticias:
```bash
curl -X POST http://localhost:8000/chatbot/ \
  -H "Content-Type: application/json" \
  -d '{"question": "dame noticias de deportes"}'
```

#### Respuesta esperada:
```json
{
  "question": "dame noticias de deportes",
  "answer": "📰 Aquí tienes las últimas noticias de DEPORTES:\n\n**1. Título...**",
  "confidence": 0.891,
  "type": "news_search",
  "category": "deportes",
  "news_count": 5
}
```

---

## 📮 Opción 3: Pruebas con Postman

### 1. Importar colección

1. Abre Postman
2. Click en **Import**
3. Selecciona el archivo: `chatbot/Lannister_News_Chatbot.postman_collection.json`
4. La colección se importará con **20+ pruebas predefinidas**

### 2. Estructura de la colección

```
📁 Lannister News - Chatbot API
  📁 FAQs Estáticas (6 pruebas)
     ├─ ¿Qué es Lannister News?
     ├─ Saludo en español
     ├─ Clasificación de noticias
     ├─ Equipo desarrollador
     ├─ Actualización de noticias
     └─ FAQ en inglés
  
  📁 Búsqueda de Noticias (8 pruebas)
     ├─ Noticias de Deportes (ES)
     ├─ Noticias de Moda (ES)
     ├─ Noticias de Tecnología (ES)
     ├─ Noticias de Animales (ES)
     ├─ Noticias Judiciales (ES)
     ├─ Sports News (EN)
     ├─ Fashion News (EN)
     └─ Tech News (EN)
  
  📁 Casos Edge (4 pruebas)
     ├─ Pregunta vacía
     ├─ Pregunta fuera de dominio
     ├─ Pregunta muy larga
     └─ Sin especificar categoría
```

### 3. Ejecutar todas las pruebas

1. Click derecho en la colección
2. **Run collection**
3. Click **Run**
4. Verás resultados de todas las pruebas

---

## ✅ Checklist de Pruebas

### FAQs Estáticas
- [ ] Pregunta sobre la plataforma (español)
- [ ] Pregunta sobre la plataforma (inglés)
- [ ] Saludos
- [ ] Agradecimientos
- [ ] Despedidas
- [ ] Clasificación de noticias
- [ ] Equipo desarrollador

### Búsqueda de Noticias
- [ ] Deportes (español)
- [ ] Moda (español)
- [ ] Tecnología (español)
- [ ] Animales (español)
- [ ] Judiciales (español)
- [ ] Sports (inglés)
- [ ] Fashion (inglés)
- [ ] Technology (inglés)

### Casos Edge
- [ ] Pregunta vacía → Error 400
- [ ] Pregunta fuera de dominio → Fallback message
- [ ] Pregunta muy larga → Respuesta válida
- [ ] Búsqueda sin categoría → Solicita especificar

---

## 📊 Verificación de Resultados

### Respuesta FAQ (type: "faq")
```json
{
  "question": "hola",
  "answer": "¡Hola! Soy Wolff...",
  "confidence": 0.95,
  "type": "faq",
  "category": null,
  "news_count": null
}
```

### Respuesta Búsqueda (type: "news_search")
```json
{
  "question": "dame noticias de deportes",
  "answer": "📰 Aquí tienes las últimas noticias...",
  "confidence": 0.89,
  "type": "news_search",
  "category": "deportes",
  "news_count": 5
}
```

### Métricas a Verificar:
- ✅ **Confidence > 0.60**: Buena predicción
- ✅ **Type correcto**: "faq" o "news_search"
- ✅ **Category presente**: Solo en news_search
- ✅ **News_count > 0**: Si hay noticias en MongoDB

---

## 🐛 Solución de Problemas

### "No module named 'chatbot'"
```bash
# Verifica que estés en el directorio raíz
cd /path/to/lannister-backend
source .venv/bin/activate
```

### "Connection refused" en MongoDB
```bash
# Verifica que MongoDB esté corriendo
docker ps  # Si usas Docker
# O revisa settings.py → MONGO_DB
```

### Confidence muy bajo (<0.50)
- El modelo necesita más entrenamiento
- Agregar más preguntas de ejemplo
- Aumentar épocas en train_chatbot.py

### No encuentra noticias
```bash
# Verifica que haya noticias en MongoDB
python manage.py shell
>>> from news.repository import get_random_news
>>> news = get_random_news(limit=5, category="deportes")
>>> print(len(news))
```

---

## 📝 Ejemplos de Pruebas Manuales

### Test 1: FAQ Básica
**Input**: "¿Qué es Lannister News?"
**Expected**: 
- type: "faq"
- confidence > 0.80
- answer contiene "plataforma digital"

### Test 2: Búsqueda Simple
**Input**: "dame noticias de deportes"
**Expected**:
- type: "news_search"
- category: "deportes"
- news_count: 5
- answer contiene "📰"

### Test 3: Multiidioma
**Input**: "give me tech news"
**Expected**:
- type: "news_search"
- category: "tecnologia"
- answer en inglés

### Test 4: Edge Case
**Input**: "muéstrame noticias"
**Expected**:
- type: "faq"
- answer solicita especificar categoría

---

## 🎯 Criterios de Éxito

✅ **FAQs**: Accuracy > 85%
✅ **News Search**: Category detection > 90%
✅ **Response Time**: < 2 segundos
✅ **Error Handling**: Sin crashes
✅ **Multiidioma**: Funciona en ES/EN

---

## 📞 Soporte

Si encuentras errores:
1. Verifica los logs del servidor
2. Revisa `chatbot/models.py` → ChatLog para debugging
3. Consulta `chatbot/README_NEWS_SEARCH.md`

---

¡Listo para probar! 🚀
