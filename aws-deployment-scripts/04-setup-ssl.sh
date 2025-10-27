#!/bin/bash

# Script para configurar Let's Encrypt SSL en el servidor
# Ejecutar DESPUÉS del despliegue básico

if [[ $# -ne 3 ]]; then
    echo "Uso: $0 <IP_PUBLICA_EC2> <ARCHIVO_CLAVE_PRIVADA> <DOMINIO>"
    echo "Ejemplo: $0 54.123.45.67 lannister-backend-key.pem api.lannister.com"
    exit 1
fi

PUBLIC_IP=$1
KEY_FILE=$2
DOMAIN=$3

echo "🔒 Configurando HTTPS con Let's Encrypt para $DOMAIN..."

# Función para ejecutar comandos remotos
run_remote() {
    ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP "$@"
}

# 1. Instalar Certbot
echo "📦 Instalando Certbot..."
run_remote "sudo apt-get update && sudo apt-get install -y certbot python3-certbot-nginx"

# 2. Parar Nginx temporalmente
echo "⏸️ Deteniendo Nginx temporalmente..."
run_remote "cd /home/lannister/app && docker-compose -f docker-compose.prod.yml stop nginx"

# 3. Obtener certificado SSL
echo "🔑 Obteniendo certificado SSL para $DOMAIN..."
run_remote "sudo certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN"

# 4. Crear nueva configuración Nginx con SSL
echo "🌐 Configurando Nginx con SSL..."
cat > /tmp/nginx-ssl.conf << EOF
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream app {
        server app:8000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name $DOMAIN;
        return 301 https://\$server_name\$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name $DOMAIN;

        ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
        
        # SSL Configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

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
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_connect_timeout 300s;
            proxy_send_timeout 300s;
            proxy_read_timeout 300s;
        }
    }
}
EOF

# Copiar nueva configuración
scp -i "$KEY_FILE" -o StrictHostKeyChecking=no /tmp/nginx-ssl.conf ubuntu@$PUBLIC_IP:/home/lannister/app/nginx.conf

# 5. Actualizar docker-compose para montar certificados
echo "🐳 Actualizando Docker Compose para SSL..."
cat > /tmp/docker-compose-ssl.yml << EOF
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
      - /etc/letsencrypt:/etc/letsencrypt:ro
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

scp -i "$KEY_FILE" -o StrictHostKeyChecking=no /tmp/docker-compose-ssl.yml ubuntu@$PUBLIC_IP:/home/lannister/app/docker-compose.prod.yml

# 6. Reiniciar servicios con SSL
echo "🔄 Reiniciando servicios con SSL..."
run_remote "cd /home/lannister/app && docker-compose -f docker-compose.prod.yml up -d"

# 7. Configurar renovación automática
echo "🔄 Configurando renovación automática de certificados..."
run_remote "sudo crontab -l 2>/dev/null | { cat; echo '0 12 * * * /usr/bin/certbot renew --quiet && cd /home/lannister/app && docker-compose -f docker-compose.prod.yml restart nginx'; } | sudo crontab -"

echo ""
echo "🎉 ¡HTTPS configurado exitosamente!"
echo "📋 Información:"
echo "   - Dominio: $DOMAIN"
echo "   - URL HTTPS: https://$DOMAIN"
echo "   - Certificado válido por 90 días"
echo "   - Renovación automática configurada"
echo ""
echo "⚠️ Recuerda actualizar ALLOWED_HOSTS en Django para incluir: $DOMAIN"

# Limpiar archivos temporales
rm -f /tmp/nginx-ssl.conf /tmp/docker-compose-ssl.yml
