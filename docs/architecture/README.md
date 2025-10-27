# 🏗️ Documentación de Arquitectura

Esta carpeta contiene la documentación técnica de la arquitectura del sistema **Lannister News Backend**.

---

## 📚 Contenido

### 📊 [COMPONENT_DIAGRAM.md](./COMPONENT_DIAGRAM.md)
**Diagrama de Componentes UML**

Documentación detallada de todos los componentes del sistema:
- 🎯 Capa de Presentación (NGINX, Clientes)
- 🔧 Capa de Aplicación (Django, Módulos)
- 🗄️ Capa de Persistencia (MySQL, MongoDB, Redis)
- 🌐 Servicios Externos (GNEWS API, HuggingFace)
- 🔐 Seguridad y Configuración

**Incluye:**
- Diagrama Mermaid completo de componentes
- Descripción detallada de cada módulo
- Flujos de datos principales
- Patrones de diseño implementados
- Tecnologías y versiones
- Métricas del sistema

**Ideal para:**
- Nuevos desarrolladores onboarding
- Revisiones de arquitectura
- Documentación técnica de referencia

---

### 🏛️ [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md)
**Visión General de la Arquitectura**

Documentación de alto nivel que incluye:
- 📐 Arquitectura en capas (Presentación → Aplicación → Persistencia)
- 🌐 Diagrama de despliegue AWS
- 🔄 Flujos de datos completos (Sequence diagrams)
- 📊 Arquitectura de datos (ER diagrams)
- 🎯 Decisiones arquitectónicas clave con justificaciones
- 📈 Estrategia de escalabilidad
- 🧪 Testing & CI/CD
- 📊 Monitoreo y observabilidad

**Incluye:**
- Diagramas Mermaid de arquitectura
- Modelo de datos relacional (MySQL)
- Modelo de datos NoSQL (MongoDB)
- Trade-offs y decisiones de diseño
- Stack tecnológico completo

**Ideal para:**
- Stakeholders técnicos
- Arquitectos de software
- Planificación de escalabilidad
- Presentaciones técnicas

---

### 📊 [VISUAL_DIAGRAMS.md](./VISUAL_DIAGRAMS.md)
**Diagramas Visuales Simplificados**

Diagramas optimizados para presentaciones rápidas:
- 🎯 Diagrama simplificado del sistema
- 🏗️ Stack tecnológico visual (mindmap)
- 🔄 Flujos principales de usuario
- 🌐 Infraestructura AWS simplificada
- 📊 Modelo de datos - relaciones clave
- 🎯 Módulos del sistema
- 🔐 Capas de seguridad
- 📈 Evolución y escalabilidad
- 🧪 Estrategia de testing
- 📊 Monitoreo del sistema

**Características:**
- Diagramas compactos y visuales
- Ideal para slides y presentaciones
- Quick reference para onboarding
- ADRs (Architecture Decision Records)

**Ideal para:**
- Presentaciones ejecutivas
- Onboarding rápido de nuevos miembros
- Revisiones de sprint
- Documentación visual

---

## 🎯 Propósito

Esta documentación tiene como objetivo:

1. **Facilitar Onboarding:** Nuevos desarrolladores entienden rápidamente la arquitectura
2. **Documentar Decisiones:** Registro de por qué se tomaron decisiones arquitectónicas
3. **Guiar Desarrollo:** Referencia para mantener consistencia arquitectónica
4. **Planificar Evolución:** Base para futuras mejoras y escalabilidad
5. **Comunicar Diseño:** Herramienta para presentaciones técnicas

---

## 📖 Cómo Usar Esta Documentación

### Para Desarrolladores Nuevos:
1. Empezar con [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) para entender el panorama general
2. Revisar [COMPONENT_DIAGRAM.md](./COMPONENT_DIAGRAM.md) para detalles de implementación
3. Consultar documentación de API en `../api/`

### Para Arquitectos:
1. Revisar [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md) para decisiones arquitectónicas
2. Evaluar trade-offs documentados
3. Planificar mejoras basadas en estrategias de escalabilidad

### Para DevOps:
1. Consultar diagrama de despliegue AWS en [ARCHITECTURE_OVERVIEW.md](./ARCHITECTURE_OVERVIEW.md)
2. Revisar configuraciones de seguridad
3. Ver guía de deployment en `../deployment/`

---

## 🔗 Documentación Relacionada

| Documento | Ubicación | Descripción |
|-----------|-----------|-------------|
| **API Documentation** | `../api/API_Documentation.md` | Endpoints, requests, responses |
| **Deployment Guide** | `../deployment/DEPLOY_AWS_GUIDE.md` | Guía de despliegue en AWS |
| **Security Guide** | `../security/SECRETS_MANAGEMENT.md` | Gestión de secretos y seguridad |
| **Testing Guide** | `../testing/POSTMAN_TESTING_GUIDE.md` | Pruebas con Postman |
| **Repository Maintenance** | `../REPOSITORY_MAINTENANCE.md` | Mantenimiento del repositorio |

---

## 📊 Diagramas Disponibles

### En COMPONENT_DIAGRAM.md:
- ✅ Diagrama de componentes completo (Mermaid)
- ✅ Flujos de datos principales
- ✅ Dependencias entre componentes

### En ARCHITECTURE_OVERVIEW.md:
- ✅ Arquitectura en capas (Mermaid)
- ✅ Diagrama de despliegue AWS (Mermaid)
- ✅ Flujo de datos completo - Sequence Diagram (Mermaid)
- ✅ Modelo de datos relacional - ER Diagram (Mermaid)
- ✅ Modelo de datos NoSQL (JavaScript/JSON)

### En VISUAL_DIAGRAMS.md:
- ✅ Diagrama simplificado del sistema (Mermaid)
- ✅ Stack tecnológico visual - Mindmap (Mermaid)
- ✅ Flujo: Usuario consulta noticias (Mermaid)
- ✅ Flujo: Chat con chatbot (Mermaid)
- ✅ Flujo: Autenticación - Sequence Diagram (Mermaid)
- ✅ Infraestructura AWS simplificada (Mermaid)
- ✅ Modelo de datos - Relaciones clave (Mermaid)
- ✅ Módulos del sistema (Mermaid)
- ✅ Capas de seguridad (Mermaid)
- ✅ Escalabilidad - Evolución del sistema (Mermaid)
- ✅ Testing Strategy (Mermaid)
- ✅ Monitoreo del sistema - Mindmap (Mermaid)
- ✅ ADRs - Decisiones arquitectónicas resumidas

---

## 🛠️ Tecnologías Documentadas

- **Backend:** Django 5.2.5, Django REST Framework
- **Databases:** MySQL 8.0 (RDS), MongoDB 7.0 (Atlas), Redis 7.x (ElastiCache)
- **ML/AI:** HuggingFace Transformers, DistilBERT
- **Infrastructure:** AWS (EC2, RDS, ElastiCache, Route 53)
- **Security:** Let's Encrypt, AWS Security Groups
- **Servers:** NGINX, Gunicorn, Supervisord

---

## 📝 Convenciones de Diagramas

Todos los diagramas usan **Mermaid.js** para compatibilidad con:
- GitHub (renderizado automático)
- VS Code (extensiones Mermaid)
- Documentación web (MkDocs, Docusaurus)

### Código de Colores:
- 🔵 **Azul:** Componentes de aplicación (Django)
- 🔴 **Rojo:** Bases de datos
- 🟢 **Verde:** Servicios externos
- 🟣 **Morado:** Seguridad y configuración
- 🟠 **Naranja:** Infraestructura AWS

---

## 🔄 Mantenimiento

Esta documentación debe actualizarse cuando:
- ✅ Se agregan nuevos módulos o componentes
- ✅ Se cambia la arquitectura de datos
- ✅ Se modifican decisiones arquitectónicas
- ✅ Se actualiza el stack tecnológico
- ✅ Se cambia la infraestructura AWS

**Responsable:** Equipo de Desarrollo  
**Frecuencia de Revisión:** Cada sprint o cambio mayor

---

## 📞 Contacto

Para preguntas sobre arquitectura:
- **Team Lead:** HouseLannisterDev
- **Email:** soporte@lannister-news.com
- **Repository:** https://github.com/HouseLannisterDev/lannister-backend

---

**Última Actualización:** 26 de octubre de 2025  
**Versión:** 2.0  
**Estado:** ✅ Actualizado y Completo
