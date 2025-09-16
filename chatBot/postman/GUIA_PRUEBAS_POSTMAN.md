# 📬 Guía de Pruebas Postman - Lannister ChatBot

## 🚀 URLs y Endpoints

### **Base URL Local**: `http://localhost:8000`

### **Endpoints Disponibles**:

| Método | Endpoint                 | Descripción                         |
| ------ | ------------------------ | ----------------------------------- |
| `GET`  | `/api/chatbot/health/`   | Verificar estado del chatbot        |
| `POST` | `/api/chatbot/chat/`     | Enviar mensaje al chatbot           |
| `POST` | `/api/chatbot/feedback/` | Enviar feedback sobre respuesta     |
| `GET`  | `/api/chatbot/history/`  | Obtener historial de conversaciones |
| `GET`  | `/api/chatbot/stats/`    | Obtener estadísticas de uso         |

---

## 🔧 Configuración en Postman

### 1. **Importar Archivos**:

- `Lannister_Chatbot_Tests.json` - Colección de pruebas
- `Local_Environment.postman_environment.json` - Entorno local
- `Production_Environment.postman_environment.json` - Entorno producción

### 2. **Seleccionar Entorno**:

- Para desarrollo: "Lannister ChatBot - Local"
- Para producción: "Lannister ChatBot - Production"

---

## 📝 Ejemplos de Mensajes para Probar

### **1. Health Check**

```
GET /api/chatbot/health/
```

**Respuesta esperada**:

```json
{
  "status": "healthy",
  "chatbot": "operational"
}
```

### **2. Chat Básico**

```
POST /api/chatbot/chat/
Content-Type: application/json

{
  "message": "hola"
}
```

### **3. Sentimientos - Noticias Negativas** 😔

```json
{
  "message": "dame malas noticias"
}
```

**Intent esperado**: `sentiment_negative`

### **4. Sentimientos - Noticias Positivas** 😊

```json
{
  "message": "dame buenas noticias"
}
```

**Intent esperado**: `sentiment_positive`

### **5. Categorías de Noticias** 📰

#### Deportes ⚽

```json
{
  "message": "noticias de deportes"
}
```

#### Tecnología 💻

```json
{
  "message": "últimas noticias de tecnología"
}
```

#### Moda 👗

```json
{
  "message": "qué hay de moda"
}
```

#### Judiciales ⚖️

```json
{
  "message": "noticias judiciales"
}
```

#### Animales 🐾

```json
{
  "message": "noticias sobre animales"
}
```

### **6. Funciones Especiales**

#### Ayuda

```json
{
  "message": "ayuda"
}
```

#### Despedida

```json
{
  "message": "adiós"
}
```

### **7. Chat con Sesión**

```json
{
  "message": "dame noticias de deportes",
  "session_id": "test-session-123"
}
```

---

## 📊 Feedback y Estadísticas

### **Enviar Feedback**

```
POST /api/chatbot/feedback/
Content-Type: application/json

{
  "message_id": 1,
  "rating": 5,
  "comment": "Excelente respuesta, muy útil"
}
```

### **Ver Historial**

```
GET /api/chatbot/history/?session_id=test-session-123
GET /api/chatbot/history/?limit=10
```

### **Ver Estadísticas**

```
GET /api/chatbot/stats/
```

---

## 🎯 Respuestas Esperadas

### **Estructura de Respuesta del Chat**:

```json
{
  "response": "😊 Aquí tienes noticias positivas:\n\n**1. Título de la noticia**\n📝 Descripción...\n🔗 **Leer más:** https://...\n📍 **Fuente:** Nombre del medio",
  "intent": "sentiment_positive",
  "confidence": 0.85,
  "session_id": "uuid-generado",
  "message_id": 123
}
```

### **Campos de la Respuesta**:

- `response`: Texto formateado con noticias y enlaces
- `intent`: Intent detectado por la IA
- `confidence`: Nivel de confianza (0.0 - 1.0)
- `session_id`: ID de sesión para seguimiento
- `message_id`: ID único del mensaje

---

## 🚦 Códigos de Estado

| Código | Descripción                |
| ------ | -------------------------- |
| `200`  | Éxito                      |
| `400`  | Error en la solicitud      |
| `500`  | Error interno del servidor |

---

## 🧪 Secuencia de Pruebas Recomendada

### **Prueba Básica (5 min)**:

1. Health Check
2. Saludo: "hola"
3. Consulta simple: "noticias de deportes"
4. Despedida: "adiós"

### **Prueba de Sentimientos (10 min)**:

1. "dame malas noticias"
2. "dame buenas noticias"
3. "noticias tristes"
4. "noticias positivas"

### **Prueba Completa (20 min)**:

1. Todas las categorías de noticias
2. Diferentes variaciones de consultas
3. Pruebas de feedback
4. Verificación de historial
5. Revisión de estadísticas

---

## 💡 Tips para Pruebas

### **Variables de Entorno**:

- `{{base_url}}` - URL base del servidor
- `{{session_id}}` - ID de sesión único

### **Mensajes de Prueba Adicionales**:

```
"qué noticias hay"
"cuéntame algo sobre tecnología"
"hay noticias de fútbol"
"me siento triste, dame algo bueno"
"noticias optimistas"
"algo malo que haya pasado"
```

### **Verificar**:

- ✅ Intent correcto para cada tipo de consulta
- ✅ Respuestas con formato correcto (títulos, links, fuentes)
- ✅ Diferentes noticias para sentimientos positivos vs negativos
- ✅ Confianza alta (>0.7) para consultas claras

---

**¡Listo para probar tu chatbot! 🤖💪**
