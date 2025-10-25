# Deploy Configuration - Lannister Backend

Esta carpeta contiene archivos de configuración para deployment y containerización.

## 📦 Archivos

### Docker
- **Dockerfile** - Dockerfile para desarrollo
- **Dockerfile.prod** - Dockerfile optimizado para producción
- **docker-compose.yml** - Orquestación de servicios con Docker Compose

### Nginx & Supervisor
- **nginx.conf** - Configuración de Nginx como reverse proxy
- **supervisord.conf** - Configuración de Supervisor para gestión de procesos

## 🐳 Uso de Docker

### Development:
```bash
docker build -f deploy/Dockerfile -t lannister-backend:dev .
docker-compose -f deploy/docker-compose.yml up
```

### Production:
```bash
docker build -f deploy/Dockerfile.prod -t lannister-backend:prod .
docker run -p 8000:8000 lannister-backend:prod
```

## 📝 Notas

- Los Dockerfiles asumen que se ejecutan desde la raíz del proyecto
- Asegúrate de tener un archivo `.env` configurado antes de ejecutar
- Para producción, usar `Dockerfile.prod` que está optimizado
