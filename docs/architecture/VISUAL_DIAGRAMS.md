# 📊 Diagramas Visuales - Lannister Backend

**Quick Reference para Presentaciones**

---

## 🎯 Diagrama Simplificado del Sistema

```mermaid
graph LR
    A[👥 Usuarios] -->|HTTPS| B[🌐 NGINX<br/>SSL/TLS]
    B --> C[🐍 Django Backend]
    
    C --> D[(🗄️ MySQL<br/>Users/Sessions)]
    C --> E[(🍃 MongoDB<br/>News)]
    C --> F[(⚡ Redis<br/>Cache)]
    
    G[📡 Scraper] -->|Fetch| H[🌍 GNEWS API]
    G -->|Store| E
    
    C --> I[🤖 ML Model<br/>DistilBERT]
    
    style A fill:#e1f5ff,stroke:#01579b
    style B fill:#f3e5f5,stroke:#4a148c
    style C fill:#092e20,stroke:#0c4b33,color:#fff
    style D fill:#d32f2f,color:#fff
    style E fill:#00796b,color:#fff
    style F fill:#c62828,color:#fff
    style G fill:#ff6f00,color:#fff
    style H fill:#43a047,color:#fff
    style I fill:#5e35b1,color:#fff
```

---

## 🏗️ Stack Tecnológico Visual

```mermaid
mindmap
  root((Lannister<br/>Backend))
    Frontend
      React
      HTTPS
      CORS
    Backend
      Django 5.2.5
      DRF
      Python 3.12+
      Gunicorn
    Databases
      MySQL 8.0
        Users
        Sessions
        ChatLogs
      MongoDB 7.0
        News Collection
        10K Docs
      Redis 7.x
        Cache
        Sessions
    Cloud AWS
      EC2 t2.medium
      RDS MySQL
      ElastiCache
      Route 53
      Let's Encrypt
    AI/ML
      HuggingFace
      DistilBERT
      18 FAQs
      News Search
    Security
      HTTPS/TLS
      CSRF Protection
      CORS
      Secrets Manager
```

---

## 🔄 Flujo Principal: Usuario Consulta Noticias

```mermaid
graph TB
    A[Usuario abre app] -->|1. GET /news/| B[NGINX]
    B -->|2. Forward| C[Django Views]
    C -->|3. Query| D[Repository Layer]
    D -->|4. MongoDB Query| E[(MongoDB)]
    E -->|5. Resultados| D
    D -->|6. Transform| C
    C -->|7. JSON| B
    B -->|8. HTTPS| A
    
    style A fill:#e3f2fd,stroke:#1976d2
    style B fill:#f3e5f5,stroke:#7b1fa2
    style C fill:#e8f5e9,stroke:#388e3c
    style D fill:#fff3e0,stroke:#f57c00
    style E fill:#fce4ec,stroke:#c2185b
```

---

## 🤖 Flujo Principal: Chat con Chatbot

```mermaid
graph TB
    A[Usuario escribe mensaje] -->|1. POST /chatbot/| B[ChatbotView]
    B -->|2. Factory.create| C[ChatbotService]
    C -->|3. Normalize| D[TextNormalizer]
    D -->|4. Cleaned text| C
    C -->|5. Classify| E[ML Model<br/>DistilBERT]
    E -->|6. FAQ_ID + Score| C
    
    C -->|7a. FAQ?| F[FAQManager]
    F -->|Answer| C
    
    C -->|7b. News?| G[NewsSearch]
    G -->|Query| H[(MongoDB)]
    H -->|Articles| G
    G -->|Results| C
    
    C -->|8. Response| B
    B -->|9. JSON| A
    
    style A fill:#e1f5ff,stroke:#01579b
    style B fill:#c8e6c9,stroke:#388e3c
    style C fill:#fff9c4,stroke:#f57f17
    style E fill:#d1c4e9,stroke:#5e35b1
    style F fill:#ffccbc,stroke:#e64a19
    style G fill:#b2dfdb,stroke:#00796b
    style H fill:#ffcdd2,stroke:#c62828
```

---

## 👤 Flujo Principal: Autenticación de Usuario

```mermaid
sequenceDiagram
    actor U as Usuario
    participant F as Frontend
    participant N as NGINX
    participant D as Django
    participant DB as MySQL
    participant R as Redis
    
    U->>F: Ingresa credenciales
    F->>N: POST /auth/login/
    N->>D: Forward request
    D->>DB: Validar usuario
    DB-->>D: Usuario válido ✓
    D->>R: Crear sesión
    R-->>D: Session ID
    D-->>N: Set-Cookie: sessionid
    N-->>F: 200 OK + Cookie
    F-->>U: Login exitoso
    
    Note over U,R: Sesión activa por 7 días
```

---

## 🌐 Infraestructura AWS - Vista Simplificada

```mermaid
graph TB
    subgraph Internet
        A[Usuarios]
    end
    
    subgraph "AWS Region: sa-east-1"
        B[Route 53<br/>DNS]
        
        subgraph "Public Subnet"
            C[EC2 Instance<br/>Ubuntu 22.04]
            D[NGINX<br/>Let's Encrypt]
            E[Django App<br/>Gunicorn]
        end
        
        subgraph "Private Subnet"
            F[(RDS MySQL<br/>db.t3.micro)]
            G[(ElastiCache<br/>Redis)]
        end
        
        H[Security<br/>Groups]
    end
    
    subgraph "External Cloud"
        I[(MongoDB Atlas)]
        J[GNEWS API]
    end
    
    A -->|HTTPS| B
    B --> C
    C --> D
    D --> E
    E --> F
    E --> G
    E --> I
    E -.->|Scraper| J
    
    H -.->|Protect| C
    H -.->|Protect| F
    H -.->|Protect| G
    
    style A fill:#fff,stroke:#000
    style C fill:#ff9800,color:#fff
    style F fill:#1976d2,color:#fff
    style G fill:#f44336,color:#fff
    style I fill:#00c853,color:#fff
```

---

## 📊 Modelo de Datos - Relaciones Clave

```mermaid
graph LR
    A[CustomUser] -->|1:N| B[Favorite]
    A -->|Genera| C[ChatLog]
    A -->|Tiene| D[Session]
    
    E[News MongoDB] -.->|Referenciado por| B
    E -.->|Buscado en| C
    
    style A fill:#1976d2,color:#fff
    style B fill:#388e3c,color:#fff
    style C fill:#f57c00,color:#fff
    style D fill:#7b1fa2,color:#fff
    style E fill:#00796b,color:#fff
```

---

## 🎯 Módulos del Sistema

```mermaid
graph TB
    subgraph "Backend Core"
        A[Django 5.2.5]
    end
    
    subgraph "Business Modules"
        B[📰 News Module]
        C[🤖 Chatbot Module]
        D[👥 Users Module]
    end
    
    subgraph "News Services"
        E[News Repository]
        F[News Scraper]
        G[News Views]
    end
    
    subgraph "Chatbot Services"
        H[ChatbotService]
        I[FAQManager]
        J[ModelProvider]
        K[NewsSearchService]
        L[TextNormalizer]
        M[FailoverManager]
    end
    
    subgraph "User Services"
        N[UserViewSet]
        O[FavoriteViewSet]
        P[AuthViews]
    end
    
    A --> B & C & D
    B --> E & F & G
    C --> H
    H --> I & J & K & L & M
    D --> N & O & P
    
    style A fill:#092e20,color:#fff
    style B fill:#1976d2,color:#fff
    style C fill:#388e3c,color:#fff
    style D fill:#f57c00,color:#fff
```

---

## 🔐 Capas de Seguridad

```mermaid
graph TB
    A[Usuario] -->|HTTPS| B[Capa 1: SSL/TLS<br/>Let's Encrypt]
    B -->|Encrypted| C[Capa 2: NGINX<br/>Headers de Seguridad]
    C -->|Headers| D[Capa 3: Django Middleware<br/>CORS + CSRF]
    D -->|Validated| E[Capa 4: Authentication<br/>Sessions + Permissions]
    E -->|Authorized| F[Capa 5: Database<br/>Security Groups]
    
    style A fill:#e3f2fd,stroke:#1976d2
    style B fill:#c8e6c9,stroke:#388e3c
    style C fill:#fff9c4,stroke:#f57f17
    style D fill:#f3e5f5,stroke:#7b1fa2
    style E fill:#ffccbc,stroke:#e64a19
    style F fill:#b2dfdb,stroke:#00796b
```

---

## 📈 Escalabilidad: Evolución del Sistema

```mermaid
graph TB
    subgraph "FASE 1: MVP Actual"
        A1[1 EC2 Instance]
        A2[RDS Single]
        A3[ElastiCache Single]
        A4[MongoDB Atlas]
    end
    
    subgraph "FASE 2: Scaling Vertical"
        B1[EC2 t2.large]
        B2[Más Workers]
        B3[RDS Replica]
    end
    
    subgraph "FASE 3: Scaling Horizontal"
        C1[Load Balancer]
        C2[Multiple EC2s]
        C3[RDS Multi-AZ]
        C4[Redis Cluster]
        C5[MongoDB Sharding]
    end
    
    A1 --> B1
    A2 --> B3
    B1 --> C1
    B1 --> C2
    B3 --> C3
    A3 --> C4
    A4 --> C5
    
    style A1 fill:#4caf50,color:#fff
    style B1 fill:#ff9800,color:#fff
    style C1 fill:#f44336,color:#fff
```

---

## 🧪 Testing Strategy

```mermaid
graph TB
    A[Testing Pyramid]
    
    A --> B[Unit Tests<br/>Services, Models, Utils]
    A --> C[Integration Tests<br/>Views, Repository, DB]
    A --> D[E2E Tests<br/>Postman Collections]
    
    B --> E[pytest<br/>Django TestCase]
    C --> F[Django Client<br/>Test DB]
    D --> G[Postman Newman<br/>CI/CD]
    
    style A fill:#1976d2,color:#fff
    style B fill:#388e3c,color:#fff
    style C fill:#f57c00,color:#fff
    style D fill:#7b1fa2,color:#fff
```

---

## 📊 Monitoreo del Sistema

```mermaid
mindmap
  root((Monitoring))
    Logs
      Application Logs
        Django Logging
        Error Tracking
      Access Logs
        NGINX access.log
        Request Metrics
      System Logs
        Deployment Logs
        Scraper Logs
    Metrics
      EC2 Metrics
        CPU Usage
        Memory Usage
        Disk I/O
      Database Metrics
        RDS Connections
        Query Performance
      Cache Metrics
        Redis Hit Rate
        Evictions
    Alerts
      Performance
        CPU > 80%
        Memory > 90%
      Errors
        HTTP 5xx > 10/min
        DB Errors
      Security
        Failed Logins
        Suspicious Activity
```

---

## 🎯 Decisiones Arquitectónicas (ADRs)

### 1️⃣ Monolito Modular vs Microservicios
**Decisión:** Monolito modular  
**Razón:** Simplicidad, menos costo, suficiente para escala actual  
**Trade-off:** Menos flexibilidad, pero más fácil de mantener

### 2️⃣ Base de Datos Híbrida
**Decisión:** MySQL + MongoDB  
**Razón:** SQL para relaciones, NoSQL para documentos flexibles  
**Trade-off:** Complejidad, pero mejor performance

### 3️⃣ ML Local vs API Externa
**Decisión:** Modelo local (HuggingFace)  
**Razón:** Sin costo por request, privacidad, latencia < 500ms  
**Trade-off:** 4.4 GB en disco, requiere recursos de servidor

### 4️⃣ Redis para Sesiones
**Decisión:** Redis como session backend  
**Razón:** In-memory > Disk, escalable  
**Trade-off:** Requiere ElastiCache, pero mejora performance

---

**Para más detalles técnicos:**
- [COMPONENT_DIAGRAM.md](./COMPONENT_DIAGRAM.md) - Diagrama completo de componentes
- [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) - Arquitectura detallada

---

**Última Actualización:** 26 de octubre de 2025  
**Ideal para:** Presentaciones, Onboarding Rápido, Revisiones de Arquitectura
