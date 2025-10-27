# 🏗️ Diagrama de Componentes - Lannister Backend

**Sistema:** Lannister News API  
**Versión:** 2.0  
**Fecha:** 26 de octubre de 2025  
**Arquitectura:** Django REST Framework + Microservicios

---

## 📊 Diagrama de Componentes UML

```mermaid
graph TB
    subgraph "CAPA DE PRESENTACIÓN"
        A[Cliente Web/Mobile<br/>React Frontend]
        A -->|HTTPS/REST| B[NGINX<br/>Reverse Proxy<br/>SSL/TLS]
    end

    subgraph "CAPA DE APLICACIÓN - Django Backend"
        B -->|Forwarding| C[Django WSGI<br/>Gunicorn/uWSGI]
        
        C --> D[URL Router<br/>lannister_news_api/urls.py]
        
        D --> E[News Module<br/>news/]
        D --> F[Chatbot Module<br/>chatbot/]
        D --> G[Users Module<br/>users/]
        
        subgraph "NEWS COMPONENT"
            E --> E1[Views<br/>news/views.py]
            E1 --> E2[Services Layer<br/>news/services/]
            E2 --> E3[Repository<br/>news/repository.py]
            E3 --> E4[MongoDB Client<br/>mongo_client.py]
        end
        
        subgraph "CHATBOT COMPONENT"
            F --> F1[Views<br/>chatbot/views.py]
            F1 --> F2[Chatbot Factory<br/>chatbot_factory.py]
            F2 --> F3[Chatbot Service<br/>chatbot_service.py]
            
            F3 --> F4[FAQ Manager<br/>faqs_manager.py]
            F3 --> F5[Text Normalizer<br/>text_normalizer.py]
            F3 --> F6[Model Provider<br/>chat_model_provider.py]
            F3 --> F7[News Search Service<br/>news_search_service.py]
            F3 --> F8[Failover Manager<br/>failover_manager.py]
            
            F4 --> F9[(FAQs JSON<br/>faqs.json<br/>faqs_normalized.json)]
            F6 --> F10[(ML Model<br/>HuggingFace<br/>DistilBERT)]
            F7 --> E4
        end
        
        subgraph "USERS COMPONENT"
            G --> G1[Views<br/>users/views.py]
            G --> G2[Auth Views<br/>users/auth_views.py]
            
            G1 --> G3[User ViewSet<br/>CRUD Operations]
            G1 --> G4[Favorite ViewSet<br/>CRUD Operations]
            G2 --> G5[Authentication<br/>CSRF/Login/Logout]
            
            G3 --> G6[Serializers<br/>users/serializers.py]
            G4 --> G6
            G5 --> G6
        end
    end

    subgraph "CAPA DE MIDDLEWARE"
        C --> M1[CORS Middleware<br/>corsheaders]
        C --> M2[Security Middleware<br/>Django Security]
        C --> M3[Session Middleware<br/>Django Sessions]
        C --> M4[CSRF Middleware<br/>Django CSRF]
        C --> M5[Auth Middleware<br/>Django Auth]
    end

    subgraph "CAPA DE PERSISTENCIA"
        subgraph "AWS RDS MySQL"
            H1[(MySQL Database<br/>lannister_news)]
            H2[Users Table<br/>CustomUser]
            H3[Favorites Table]
            H4[ChatLogs Table]
            H5[Django Tables<br/>sessions/auth]
            
            H1 --> H2
            H1 --> H3
            H1 --> H4
            H1 --> H5
        end
        
        subgraph "MongoDB Atlas"
            I1[(MongoDB<br/>lannister_db)]
            I2[News Collection<br/>~10K documents]
            I3[Scraping Metadata<br/>Collection]
            
            I1 --> I2
            I1 --> I3
        end
        
        subgraph "AWS ElastiCache"
            J1[(Redis Cache<br/>Session Store)]
            J2[Session Data]
            J3[Cache Data]
            
            J1 --> J2
            J1 --> J3
        end
    end

    subgraph "CAPA DE SERVICIOS EXTERNOS"
        K1[News Scraper Service<br/>news/scripts/run_scraper.py]
        K2[GNEWS API<br/>External News Source]
        
        K1 -->|Fetch Articles| K2
        K1 -->|Insert| I2
    end

    subgraph "SEGURIDAD Y CONFIGURACIÓN"
        L1[Environment Variables<br/>.env]
        L2[Settings<br/>settings.py]
        L3[Secrets Management<br/>AWS Secrets Manager]
        
        L1 --> L2
        L3 --> L1
        
        L2 --> C
    end

    %% Conexiones de persistencia
    G6 --> H1
    E4 --> I1
    M3 --> J1
    
    %% Estilos
    classDef frontend fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef django fill:#092e20,stroke:#0c4b33,stroke-width:2px,color:#fff
    classDef database fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    classDef cache fill:#51cf66,stroke:#2f9e44,stroke-width:2px
    classDef external fill:#ffd43b,stroke:#f59f00,stroke-width:2px
    classDef security fill:#845ef7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    
    class A frontend
    class B,C,D,E,F,G,E1,E2,E3,F1,F2,F3,F4,F5,F6,F7,F8,G1,G2,G3,G4,G5,G6 django
    class H1,H2,H3,H4,H5,I1,I2,I3 database
    class J1,J2,J3 cache
    class K1,K2 external
    class L1,L2,L3 security
```

---

## 🎯 Descripción de Componentes Principales

### 1️⃣ **CAPA DE PRESENTACIÓN**

#### **Cliente Web/Mobile**
- **Tecnología:** React (Frontend)
- **Comunicación:** HTTPS/REST API
- **Endpoints:** Consume `/api/news/`, `/api/chatbot/`, `/api/users/`

#### **NGINX Reverse Proxy**
- **Función:** Balanceo de carga, SSL/TLS termination
- **Certificado:** Let's Encrypt (Auto-renovación)
- **Dominio:** `lannister-news.com`

---

### 2️⃣ **CAPA DE APLICACIÓN - Django Backend**

#### **Django WSGI Server**
- **Servidor:** Gunicorn/uWSGI
- **Workers:** Múltiples procesos para concurrencia
- **Gestión:** Supervisord para auto-restart

#### **URL Router**
- **Archivo:** `lannister_news_api/urls.py`
- **Función:** Enrutamiento de peticiones a módulos
- **Rutas:**
  - `/users/` → Users Module
  - `/news/` → News Module
  - `/chatbot/` → Chatbot Module

---

### 3️⃣ **MÓDULOS DE NEGOCIO**

#### **📰 NEWS MODULE** (`news/`)

**Componentes:**
- **Views** (`views.py`):
  - `get_news_view()` - Lista de noticias con filtros
  - `get_sources_view()` - Fuentes disponibles
  - `get_random_view()` - Noticias aleatorias
  - `get_section_view()` - Por categoría
  - `stats_view()` - Estadísticas del sistema

- **Services** (`services/`):
  - Lógica de negocio para scraping
  - Transformación de datos
  - Validaciones

- **Repository** (`repository.py`):
  - `insert_many_news()` - Inserción masiva
  - `get_news()` - Consultas filtradas
  - `get_random_news()` - Aleatorización
  - `ensure_indexes()` - Optimización MongoDB

**Responsabilidades:**
- ✅ Gestión de noticias
- ✅ Filtrado por categoría/fuente/fecha
- ✅ Paginación y límites
- ✅ Deduplicación por URL
- ✅ Estadísticas de sistema

---

#### **🤖 CHATBOT MODULE** (`chatbot/`)

**Arquitectura:** Factory Pattern + Dependency Injection

**Componentes:**

1. **Chatbot Factory** (`chatbot_factory.py`):
   - Patrón Factory para crear instancias
   - Inyección de dependencias
   - Singleton para modelo ML

2. **Chatbot Service** (`chatbot_service.py`):
   - **Motor principal:** Pipeline de clasificación
   - **Híbrido:** FAQ + Búsqueda de noticias
   - **Tecnología:** HuggingFace Transformers (DistilBERT)

3. **Servicios Auxiliares:**
   - **FAQ Manager** (`faqs_manager.py`): Gestión de respuestas predefinidas
   - **Text Normalizer** (`text_normalizer.py`): Limpieza y normalización
   - **Model Provider** (`chat_model_provider.py`): Singleton para modelo ML
   - **News Search Service** (`news_search_service.py`): Búsqueda en MongoDB
   - **Failover Manager** (`failover_manager.py`): Respuestas de respaldo
   - **Logging Manager** (`logging_manager.py`): Registro de interacciones

**Flujo de Procesamiento:**
```
Usuario → POST /api/chatbot/
    ↓
ChatbotView (views.py)
    ↓
ChatbotFactory.create()
    ↓
ChatbotService.get_answer()
    ↓
┌─────────────────────────┐
│ 1. Text Normalizer      │ → Normaliza pregunta
│ 2. Model Classification │ → DistilBERT predice FAQ
│ 3. FAQ Manager          │ → Obtiene respuesta
│ 4. News Search (si FAQ#18)│ → Busca noticias
│ 5. Failover Manager     │ → Respuesta genérica si falla
└─────────────────────────┘
    ↓
Respuesta JSON con metadata
```

**Responsabilidades:**
- ✅ Clasificación de intenciones con ML
- ✅ Respuestas predefinidas (18 FAQs)
- ✅ Búsqueda de noticias inteligente
- ✅ Detección de idioma
- ✅ Normalización de texto (lemmatización)
- ✅ Logging de conversaciones

---

#### **👥 USERS MODULE** (`users/`)

**Componentes:**

1. **User ViewSet** (`views.py`):
   - CRUD de usuarios
   - Gestión de perfiles
   - REST API completo

2. **Favorite ViewSet** (`views.py`):
   - Gestión de favoritos
   - Relación User → URLs guardadas

3. **Auth Views** (`auth_views.py`):
   - `csrf()` - Token CSRF
   - `login_view()` - Autenticación
   - `logout_view()` - Cierre de sesión
   - `me()` - Usuario actual

4. **Serializers** (`serializers.py`):
   - Serialización Django REST Framework
   - Validaciones de datos

**Modelos de Datos:**
- **CustomUser:** Extiende AbstractUser con `date_of_birth` y `age`
- **Favorite:** Relación usuario → URL (unique constraint)

**Responsabilidades:**
- ✅ Autenticación y autorización
- ✅ Gestión de sesiones
- ✅ CSRF protection
- ✅ Favoritos de usuarios
- ✅ Perfiles de usuario

---

### 4️⃣ **CAPA DE MIDDLEWARE**

#### **Middleware Stack:**
1. **CORS Middleware** (`corsheaders`):
   - Permite requests cross-origin
   - Configurado para `lannister-news.com`

2. **Security Middleware**:
   - X-Frame-Options
   - X-Content-Type-Options
   - Strict-Transport-Security (HSTS)

3. **Session Middleware**:
   - Gestión de sesiones en Redis
   - Timeout configurable

4. **CSRF Middleware**:
   - Protección contra CSRF
   - Tokens por sesión

5. **Auth Middleware**:
   - Autenticación de usuarios
   - Permisos y roles

---

### 5️⃣ **CAPA DE PERSISTENCIA**

#### **🗄️ AWS RDS MySQL**
- **Engine:** MySQL 8.0
- **Región:** sa-east-1 (São Paulo)
- **Uso:** Datos relacionales

**Tablas:**
- `users_customuser` - Usuarios del sistema
- `users_favorite` - Favoritos por usuario
- `chatbot_chatlog` - Logs de conversaciones
- `django_session` - Sesiones activas
- Django auth tables (auth_user, auth_permission, etc.)

**Características:**
- ✅ Transacciones ACID
- ✅ Relaciones FK con integridad referencial
- ✅ Charset UTF8MB4
- ✅ Backups automáticos

---

#### **🍃 MongoDB Atlas**
- **Cluster:** Dedicated M10 (o similar)
- **Región:** Multi-región
- **Uso:** Almacenamiento de noticias (NoSQL)

**Colecciones:**

1. **news** (~10,000 documentos):
```javascript
{
  _id: ObjectId,
  title: String,
  description: String,
  url: String (unique index),
  source_domain: String,
  category: String, // Deportes, Judiciales, Moda, Tecnología, Animales
  image: String,
  date_publish: String (ISO),
  scraped_at: DateTime
}
```

2. **scraping_metadata**:
```javascript
{
  key: String (unique),
  value: Mixed,
  updated_at: DateTime
}
```

**Índices:**
- `url` (unique) - Deduplicación
- `date_publish` - Consultas por fecha
- `source_domain` - Filtrado por fuente
- `category` - Filtrado por categoría

---

#### **⚡ AWS ElastiCache (Redis)**
- **Engine:** Redis 7.x
- **Región:** sa-east-1
- **Uso:** Caché y sesiones

**Datos almacenados:**
- Session data (Django sessions)
- Cache de queries frecuentes
- Temporary data

**Configuración:**
- TTL: 7 días (sesiones)
- Eviction policy: LRU

---

### 6️⃣ **SERVICIOS EXTERNOS**

#### **News Scraper Service**
- **Archivo:** `news/scripts/run_scraper.py`
- **Función:** Scraping automatizado de noticias
- **Fuente:** GNEWS API
- **Frecuencia:** Configurable (cron/manual)

**Parámetros:**
- **Categorías:** Deportes, Judiciales, Moda, Tecnología, Animales
- **Límite:** 200 artículos/categoría/ejecución
- **Cap total:** 10,000 documentos
- **Ventana temporal:** Último año (365 días)

**Flujo:**
```
run_scraper.py → GNEWS API → Transform → MongoDB (news collection)
```

---

### 7️⃣ **SEGURIDAD Y CONFIGURACIÓN**

#### **Environment Variables** (`.env`)
```bash
# Django
SECRET_KEY=<generated-secret>
DEBUG=False

# MySQL
MYSQL_DB=lannister_news
MYSQL_USER=admin
MYSQL_PASSWORD=<secure-password>
MYSQL_HOST=<rds-endpoint>.sa-east-1.rds.amazonaws.com
MYSQL_PORT=3306

# Redis
REDIS_URL=redis://<elasticache-endpoint>:6379/1

# MongoDB
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/lannister_db

# Session
SESSION_COOKIE_AGE=604800
```

#### **AWS Secrets Manager**
- Gestión centralizada de secretos
- Rotación automática de contraseñas
- Integración con aplicación

#### **Settings** (`settings.py`)
- Configuración centralizada
- Validación de variables requeridas
- Fail-fast para secretos faltantes

---

## 🔄 Flujos de Datos Principales

### **Flujo 1: Consulta de Noticias**
```
Cliente → NGINX → Django → News Views → Repository → MongoDB → Response
```

### **Flujo 2: Chat con Chatbot**
```
Cliente → NGINX → Django → Chatbot Views → Factory → Service
    ↓
[Normalizer → Model (ML) → FAQ Manager] ó [News Search → MongoDB]
    ↓
Response con metadata
```

### **Flujo 3: Autenticación de Usuario**
```
Cliente → NGINX → Django → Auth Views → Django Auth → MySQL
    ↓
Session → Redis Cache
    ↓
Session Cookie → Cliente
```

### **Flujo 4: Scraping de Noticias**
```
Cron/Manual → run_scraper.py → GNEWS API → Transform → MongoDB
    ↓
Logs → Deployment Logs
```

---

## 📦 Dependencias entre Componentes

### **Alta Cohesión:**
- Cada módulo (news, chatbot, users) es independiente
- Servicios encapsulados con responsabilidades únicas
- Repository pattern separa lógica de negocio y persistencia

### **Bajo Acoplamiento:**
- Comunicación a través de interfaces bien definidas
- Factory pattern para gestión de dependencias
- Inyección de dependencias en chatbot services

### **Patrones de Diseño Implementados:**
- ✅ **Repository Pattern** (news/repository.py)
- ✅ **Factory Pattern** (chatbot_factory.py)
- ✅ **Singleton Pattern** (chat_model_provider.py)
- ✅ **Dependency Injection** (chatbot services)
- ✅ **Strategy Pattern** (failover_manager.py)
- ✅ **Template Method** (Django Class-Based Views)

---

## 🚀 Tecnologías y Versiones

| Componente | Tecnología | Versión |
|------------|------------|---------|
| **Backend Framework** | Django | 5.2.5 |
| **API Framework** | Django REST Framework | 3.14+ |
| **Python** | Python | 3.12+ |
| **WSGI Server** | Gunicorn | Latest |
| **Proxy** | NGINX | 1.18+ |
| **Database (SQL)** | MySQL | 8.0 |
| **Database (NoSQL)** | MongoDB | 7.0 |
| **Cache** | Redis | 7.x |
| **ML Framework** | HuggingFace Transformers | 4.35+ |
| **ML Model** | DistilBERT | Base Uncased |
| **Process Manager** | Supervisord | 4.2+ |
| **SSL/TLS** | Let's Encrypt | Auto-renew |

---

## 📊 Métricas del Sistema

### **Capacidad:**
- **Noticias:** ~10,000 documentos (cap configurable)
- **Usuarios:** Ilimitado (limitado por RDS)
- **FAQs:** 18 intenciones predefinidas
- **Categorías:** 5 (Deportes, Judiciales, Moda, Tecnología, Animales)

### **Performance:**
- **Response Time:** < 200ms (promedio)
- **Chatbot Inference:** < 500ms
- **Cache Hit Rate:** > 80%

### **Disponibilidad:**
- **Uptime Target:** 99.5%
- **SSL/TLS:** Activo 24/7
- **Auto-scaling:** AWS RDS + ElastiCache

---

## 🛡️ Seguridad

### **Implementado:**
- ✅ HTTPS/TLS obligatorio (Let's Encrypt)
- ✅ CSRF Protection (Django Middleware)
- ✅ CORS configurado para dominios específicos
- ✅ Secrets en variables de entorno (no hardcoded)
- ✅ SQL Injection protection (Django ORM)
- ✅ XSS protection (Django templates)
- ✅ Session security (HTTPOnly, Secure cookies)
- ✅ Rate limiting (configurable)

### **Recomendado:**
- 🔄 AWS WAF para protección DDoS
- 🔄 MFA para usuarios admin
- 🔄 Audit logging centralizado

---

## 📝 Notas de Implementación

1. **Modelo ML almacenado localmente** (4.4 GB):
   - Ubicación: `chatbot/faq_model_2/`
   - Consideración futura: Git LFS

2. **MongoDB Atlas** gestiona índices automáticamente:
   - Índice único en `url` previene duplicados
   - Índices compuestos para queries frecuentes

3. **Redis como session backend**:
   - Engine: `django.contrib.sessions.backends.cached_db`
   - Fallback a DB si Redis falla

4. **Scraper ejecutado manualmente o via cron**:
   - Script independiente: `news/scripts/run_scraper.py`
   - No ejecutado automáticamente en producción

---

## 🔗 Referencias

- **API Documentation:** `docs/api/API_Documentation.md`
- **Security Guide:** `docs/security/SECRETS_MANAGEMENT.md`
- **Testing Guide:** `docs/testing/POSTMAN_TESTING_GUIDE.md`
- **Deployment Guide:** `docs/deployment/DEPLOY_AWS_GUIDE.md`
- **Repository Maintenance:** `docs/REPOSITORY_MAINTENANCE.md`

---

**Actualizado:** 26 de octubre de 2025  
**Mantenido por:** HouseLannisterDev Team  
**Contacto:** soporte@lannister-news.com
