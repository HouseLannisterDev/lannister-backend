# 🎯 Guía Rápida: Probar Chatbot en Postman

## ✅ El Servidor Ya Está Corriendo

Tu chatbot standalone está activo en: **http://localhost:8001**

---

## 📥 Importar Colección en Postman

### Opción 1: Importar desde archivo
1. Abre Postman
2. Click en **"Import"** (botón arriba a la izquierda)
3. Selecciona el archivo: **`Postman_Standalone_Chatbot.json`**
4. Click **"Import"**

### Opción 2: Nueva colección manual
1. Click en **"New"** → **"HTTP"**
2. Método: **POST**
3. URL: `http://localhost:8001/chatbot`
4. Headers: `Content-Type: application/json`
5. Body → raw → JSON:
```json
{
  "question": "Dame noticias de deportes"
}
```

---

## 🧪 Ejemplos de Pruebas

### 1. Health Check (GET)
```
GET http://localhost:8001/health
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "message": "Lannister News Chatbot API"
}
```

---

### 2. Búsqueda de Noticias - Deportes (POST)
```
POST http://localhost:8001/chatbot
Content-Type: application/json

{
  "question": "Dame noticias de deportes"
}
```

**Respuesta esperada:**
```json
{
  "answer": "🔍 Búsqueda de noticias detectada...",
  "confidence": 0.79,
  "type": "news_search",
  "category": "detected"
}
```

✅ **Confianza: ~79%** (FAQ #18 detectado correctamente)

---

### 3. Búsqueda de Noticias - Tecnología
```json
{
  "question": "Muéstrame las últimas noticias de tecnología"
}
```

✅ **Confianza: ~78%**

---

### 4. Búsqueda de Noticias - Moda
```json
{
  "question": "Quiero ver noticias de moda"
}
```

✅ **Confianza: ~80%**

---

### 5. Búsqueda en Inglés
```json
{
  "question": "Show me the latest sports news"
}
```

✅ **Confianza: ~70%**

---

### 6. FAQ Regular - Saludo
```json
{
  "question": "Hola"
}
```

**Respuesta esperada:**
```json
{
  "answer": "¡Hola! Soy Wolff...",
  "confidence": 0.72,
  "type": "faq",
  "faq_id": 13,
  "domain": "saludos"
}
```

---

### 7. FAQ - ¿Qué es Lannister?
```json
{
  "question": "¿Qué es Lannister News?"
}
```

**Respuesta esperada:**
```json
{
  "answer": "Lannister News es una plataforma digital...",
  "confidence": 0.63,
  "type": "faq",
  "faq_id": 1,
  "domain": "informacion_plataforma"
}
```

---

### 8. Edge Case - Texto Aleatorio
```json
{
  "question": "asdfghjkl"
}
```

**Respuesta esperada:**
```json
{
  "answer": "Lo siento, no entendí. Por favor intenta con otra pregunta.",
  "confidence": 0.16,
  "type": "fallback"
}
```

---

## 📊 Entendiendo la Respuesta

### Campos del JSON Response:

- **`answer`**: Respuesta del chatbot en texto
- **`confidence`**: Nivel de confianza (0.0 a 1.0)
- **`type`**: Tipo de respuesta
  - `"faq"`: Respuesta de FAQ estática
  - `"news_search"`: Búsqueda de noticias detectada (FAQ #18)
  - `"fallback"`: No entendió la pregunta
- **`faq_id`**: ID del FAQ (1-18)
- **`domain`**: Categoría del FAQ
- **`category`** (solo news_search): Categoría detectada
- **`note`** (solo standalone): Nota sobre limitaciones

---

## 🎯 Qué Probar en Postman

### ✅ Casos de Éxito (Alta Confianza)
- [x] "Dame noticias de deportes" → **~79%**
- [x] "Muéstrame noticias de tecnología" → **~78%**
- [x] "Quiero ver noticias de moda" → **~80%**
- [x] "Hola" → **~72%**

### 🔍 Variaciones de Búsqueda
- "busco noticias deportivas"
- "necesito ver tech news"
- "últimas noticias de animales"
- "show me fashion news"

### ⚠️ Edge Cases
- "asdfghjkl" → Fallback
- "¿Cuál es el sentido de la vida?" → Fallback o FAQ genérico
- "pizza" → Confianza baja

---

## 🚀 Para Probar con MongoDB Real

Si quieres que la búsqueda de noticias devuelva resultados reales:

1. **Usar el servidor Django completo:**
   ```bash
   # Configurar MySQL local primero
   ./start-local.sh
   python manage.py runserver
   ```

2. **Probar en producción (AWS):**
   - URL: `https://lannister-news.com/chatbot/`
   - Mismo formato de request
   - MongoDB ya tiene datos

---

## 🛑 Detener el Servidor

```bash
# Encontrar el proceso
lsof -ti:8001

# Matarlo
kill -9 $(lsof -ti:8001)
```

O simplemente presiona `Ctrl+C` en la terminal donde corre.

---

## 📝 Notas Importantes

1. **Standalone vs Producción:**
   - Standalone: Solo detecta intención de búsqueda
   - Producción: Consulta MongoDB y devuelve noticias reales

2. **Confidence Threshold:**
   - **< 8%**: Respuesta fallback
   - **> 50%**: Respuesta confiable
   - **> 70%**: Alta confianza

3. **FAQ #18 es especial:**
   - Entrenado con 120 preguntas de búsqueda
   - Detecta intención, no ejecuta búsqueda en standalone
   - En producción, extrae categoría y consulta MongoDB

---

## ✅ Checklist de Pruebas

- [ ] Health check funciona
- [ ] Búsqueda de deportes detectada (>70%)
- [ ] Búsqueda de tecnología detectada (>70%)
- [ ] Búsqueda de moda detectada (>70%)
- [ ] Búsqueda en inglés funciona (>50%)
- [ ] FAQs regulares responden correctamente
- [ ] Edge cases devuelven fallback
- [ ] Confianza es consistente

---

**🎉 ¡Listo para probar en Postman!**

El servidor está corriendo. Solo importa la colección y empieza a hacer requests.
