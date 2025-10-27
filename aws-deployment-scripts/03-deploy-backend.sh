#!/bin/bash

# Script para configurar el servidor EC2 con el backend Lannister
# Ejecutar DESPUÉS de que la instancia EC2 esté lista

# Verificar parámetros
if [[ $# -ne 2 ]]; then
    echo "Uso: $0 <IP_PUBLICA_EC2> <ARCHIVO_CLAVE_PRIVADA>"
    echo "Ejemplo: $0 54.123.45.67 lannister-backend-key.pem"
    exit 1
fi

PUBLIC_IP=$1
KEY_FILE=$2

echo "🚀 Configurando servidor EC2 para Lannister Backend..."
echo "   - IP: $PUBLIC_IP"
echo "   - Clave: $KEY_FILE"

# Verificar que el archivo de clave existe
if [[ ! -f "$KEY_FILE" ]]; then
    echo "❌ Error: No se encuentra el archivo de clave privada: $KEY_FILE">&2
    exit 1
fi

# Función para ejecutar comandos remotos
run_remote() {
    ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP "$@"
}

# Función para copiar archivos
copy_file() {
    scp -i "$KEY_FILE" -o StrictHostKeyChecking=no "$1" ubuntu@$PUBLIC_IP:"$2"
}

# 1. Verificar que el servidor esté listo
echo "⏳ Verificando que el servidor esté listo..."
for i in {1..30}; do
    if run_remote "echo 'Server ready'" 2>/dev/null; then
        echo "✅ Servidor listo para configuración"
        break
    fi
    if [[ $i -eq 30 ]]; then
        echo "❌ Timeout: El servidor no responde después de 5 minutos"
        exit 1
    fi
    echo "   Intento $i/30 - Esperando 10 segundos..."
    sleep 10
done

# 2. Verificar que Docker esté instalado
echo "🐳 Verificando instalación de Docker..."
run_remote "docker --version && docker-compose --version"

# 3. Clonar el repositorio (necesitarás proporcionar el token o configurar SSH)
echo "📥 Clonando repositorio..."
REPO_URL="https://github.com/HouseLannisterDev/lannister-backend.git"
run_remote "cd /home/lannister/app && git clone $REPO_URL ."

# 4. Crear archivo .env con las variables de producción
echo "⚙️ Configurando variables de entorno..."

# Leer credenciales RDS si existen
if [[ -f "rds-credentials.txt" ]]; then
    source rds-credentials.txt
    echo "✅ Credenciales RDS cargadas"
else
    echo "⚠️ No se encontraron credenciales RDS, usando valores por defecto"
    DB_ENDPOINT="localhost"
    DB_PORT="3306"
    DB_NAME="lannister_news"
    DB_USERNAME="admin"
    DB_PASSWORD="defaultpass"
fi

# Crear archivo .env
cat > /tmp/.env << EOF
# Django Configuration
DJANGO_SECRET_KEY=your-super-secret-production-key-here-change-this
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=$PUBLIC_IP,localhost,127.0.0.1

# MySQL Database (RDS)
MYSQL_HOST=$DB_ENDPOINT
MYSQL_PORT=$DB_PORT
MYSQL_DB=$DB_NAME
MYSQL_USER=$DB_USERNAME
MYSQL_PASSWORD=$DB_PASSWORD

# Redis Configuration
REDIS_URL=redis://127.0.0.1:6379/1

# MongoDB Configuration (usa tu URI existente)
MONGO_NAME=lannister_news
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_URI=mongodb://localhost:27017/lannister_news

# Session Configuration
SESSION_COOKIE_AGE=604800
DJANGO_TIME_ZONE=America/Bogota

# News Scraper Configuration
NEWS_SOURCES=https://example.com/feed
NEWS_PROXIES=
NEWS_USER_AGENTS=Mozilla/5.0 (compatible; LannisterBot/1.0)
NEWS_REQ_DELAY_MIN=3
NEWS_REQ_DELAY_MAX=8
NEWS_MAX_RETRIES=3

# Chatbot Configuration
FAQ_PATH=/app/chatbot/faqs/faqs.json
FAQ_NORMALIZED_PATH=/app/chatbot/faqs/faqs_normalized.json
FALLOVER_THRESHOLD=0.08
FALLOVER_MESSAGE=Lo siento, no entendí. Por favor intenta con otra pregunta.
FAQ_MODEL_PATH=/app/chatbot/faq_model_2
EOF

# Copiar archivo .env al servidor
copy_file "/tmp/.env" "/home/lannister/app/.env"
run_remote "sudo chown lannister:lannister /home/lannister/app/.env"

# 5. Crear docker-compose.prod.yml optimizado para producción
echo "🐳 Creando configuración Docker para producción..."
cat > /tmp/docker-compose.prod.yml << 'EOF'
version: "3.9"

services:
  app:
    build: 
      context: .
      dockerfile: Dockerfile.prod
    container_name: lannister_backend
    restart: unless-stopped
    environment:
      - DJANGO_SETTINGS_MODULE=lannister_news_api.settings
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    depends_on:
      - redis
    networks:
      - lannister_network

  redis:
    image: redis:7-alpine
    container_name: lannister_redis
    restart: unless-stopped
    ports:
      - "127.0.0.1:6379:6379"
    networks:
      - lannister_network

  nginx:
    image: nginx:alpine
    container_name: lannister_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_volume:/var/www/static:ro
      - media_volume:/var/www/media:ro
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app
    networks:
      - lannister_network

volumes:
  static_volume:
  media_volume:

networks:
  lannister_network:
    driver: bridge
EOF

copy_file "/tmp/docker-compose.prod.yml" "/home/lannister/app/docker-compose.prod.yml"

# 6. Crear Dockerfile.prod optimizado
echo "📦 Creando Dockerfile de producción..."
cat > /tmp/Dockerfile.prod << 'EOF'
# Multi-stage build para optimizar tamaño
FROM python:3.13-slim as builder

# Instalar dependencias de compilación
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Etapa de producción
FROM python:3.13-slim

# Instalar solo dependencias de runtime
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar dependencias de Python desde builder
COPY --from=builder /root/.local /root/.local

WORKDIR /app

# Copiar código de aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/staticfiles /app/media

# Crear usuario no-root
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Configurar PATH para dependencias de Python
ENV PATH=/root/.local/bin:$PATH

# Ejecutar colecta de archivos estáticos
USER appuser
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Usar Gunicorn en producción
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "lannister_news_api.wsgi:application"]
EOF

copy_file "/tmp/Dockerfile.prod" "/home/lannister/app/Dockerfile.prod"

# 7. Crear configuración de Nginx
echo "🌐 Configurando Nginx..."
cat > /tmp/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream app {
        server app:8000;
    }

    server {
        listen 80;
        server_name _;

        client_max_body_size 20M;

        location /static/ {
            alias /var/www/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /var/www/media/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 300s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }
    }
}
EOF

copy_file "/tmp/nginx.conf" "/home/lannister/app/nginx.conf"

# 8. Agregar Gunicorn a requirements si no está
echo "📋 Actualizando requirements.txt..."
run_remote "cd /home/lannister/app && echo 'gunicorn==21.2.0' >> requirements.txt"

# 9. Construir y ejecutar contenedores
echo "🏗️ Construyendo y ejecutando aplicación..."
run_remote "cd /home/lannister/app && docker-compose -f docker-compose.prod.yml up -d --build"

# 10. Ejecutar migraciones de Django
echo "🗄️ Ejecutando migraciones de Django..."
sleep 30  # Esperar que los contenedores estén listos
run_remote "cd /home/lannister/app && docker-compose -f docker-compose.prod.yml exec -T app python manage.py migrate"

# 11. Crear superusuario de Django (opcional)
echo "👤 ¿Quieres crear un superusuario de Django? (y/n)"
read -p "Respuesta: " create_superuser
if [[ "$create_superuser" = "y" ]] || [[ "$create_superuser" = "Y" ]]; then
    echo "Ejecuta el siguiente comando manualmente en el servidor:"
    echo "ssh -i $KEY_FILE ubuntu@$PUBLIC_IP 'cd /home/lannister/app && docker-compose -f docker-compose.prod.yml exec app python manage.py createsuperuser'"
fi

# 12. Verificar estado de la aplicación
echo "🔍 Verificando estado de la aplicación..."
run_remote "cd /home/lannister/app && docker-compose -f docker-compose.prod.yml ps"

echo ""
echo "🎉 ¡Configuración del servidor completada!"
echo "📋 Información del despliegue:"
echo "   - IP del servidor: $PUBLIC_IP"
echo "   - URL de la aplicación: http://$PUBLIC_IP"
echo "   - URL del admin de Django: http://$PUBLIC_IP/admin/"
echo ""
echo "🔧 Comandos útiles:"
echo "   - Ver logs: ssh -i $KEY_FILE ubuntu@$PUBLIC_IP 'cd /home/lannister/app && docker-compose -f docker-compose.prod.yml logs -f'"
echo "   - Reiniciar app: ssh -i $KEY_FILE ubuntu@$PUBLIC_IP 'cd /home/lannister/app && docker-compose -f docker-compose.prod.yml restart'"
echo "   - Acceder al contenedor: ssh -i $KEY_FILE ubuntu@$PUBLIC_IP 'cd /home/lannister/app && docker-compose -f docker-compose.prod.yml exec app bash'"
echo ""
echo "⚠️ Recuerda:"
echo "   1. Actualizar tu URI de MongoDB en el .env"
echo "   2. Configurar un dominio si es necesario"
echo "   3. Configurar HTTPS con Let's Encrypt"
echo "   4. Hacer backup de la base de datos regularmente"

# Limpiar archivos temporales
rm -f /tmp/.env /tmp/docker-compose.prod.yml /tmp/Dockerfile.prod /tmp/nginx.conf
