# 🔒 COMANDOS DE PRUEBA HTTPS - LANNISTER NEWS API

## ✅ ENDPOINTS FUNCIONANDO CON HTTPS

### 📰 NEWS ENDPOINTS (sin /api/)
```bash
# Estadísticas del sistema
curl https://lannister-news.com/news/stats/

# Lista de fuentes
curl https://lannister-news.com/news/sources/

# Noticias aleatorias
curl "https://lannister-news.com/news/random/?limit=3"

# Filtrar noticias por tema
curl "https://lannister-news.com/news/?q=deportes&limit=5"

# Filtrar por fuente específica
curl "https://lannister-news.com/news/?source=ELTIEMPO.COM&limit=3"

# Noticias por sección
curl https://lannister-news.com/news/section/tecnologia/
```

### 🤖 CHATBOT ENDPOINTS (/chatbot/chatbot/)
```bash
# Pregunta al chatbot
curl -X POST https://lannister-news.com/chatbot/chatbot/ \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Qué noticias tienes hoy?"}'

# Pregunta sobre el equipo
curl -X POST https://lannister-news.com/chatbot/chatbot/ \
  -H "Content-Type: application/json" \
  -d '{"question": "¿Quiénes son?"}'
```

### 👥 USER ENDPOINTS (con /api/)
```bash
# Obtener token CSRF
curl https://lannister-news.com/api/users/auth/csrf/

# Lista de usuarios
curl https://lannister-news.com/api/users/

# Login (requiere usuario válido)
curl -X POST https://lannister-news.com/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'
```

## 🌐 PRUEBAS EN NAVEGADOR
- https://lannister-news.com/news/stats/
- https://lannister-news.com/news/sources/
- https://lannister-news.com/news/

## 📊 RESULTADO ESPERADO DE STATS
```json
{
  "total_docs": 1024,
  "unique_sources": 12,
  "cap_docs": 10000,
  "remaining_until_cap": 8976,
  "inserted_last_24h": 0
}
```

## 🎯 RESUMEN DE CONFIGURACIÓN
- ✅ Dominio: lannister-news.com
- ✅ SSL: Let's Encrypt (renovación automática)
- ✅ Nginx: Reverse proxy configurado
- ✅ Django: ALLOWED_HOSTS actualizado
- ✅ Docker: Contenedores funcionando

**Fecha de configuración:** 17 de octubre de 2025  
**Estado:** 🟢 Totalmente funcional con HTTPS