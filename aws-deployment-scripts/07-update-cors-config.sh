#!/bin/bash

# =================================================================
# ACTUALIZAR CONFIGURACIÓN CORS EN SERVIDOR AWS
# =================================================================

set -e

echo "🔄 Actualizando configuración CORS en el servidor AWS..."

# Variables
SERVER="ubuntu@lannister-news.com"
KEY_PATH="aws-deployment-scripts/lannister-backend-key.pem"
PROJECT_PATH="/home/ubuntu/lannister-app/lannister-backend"

echo "📁 Copiando archivos de configuración al servidor..."

# Copiar el archivo settings.py actualizado
scp -i $KEY_PATH lannister_news_api/settings.py $SERVER:$PROJECT_PATH/lannister_news_api/

echo "🔄 Reiniciando contenedores Docker..."

# Conectar al servidor y reiniciar los contenedores
ssh -i $KEY_PATH $SERVER << 'EOF'
cd /home/ubuntu/lannister-app/lannister-backend

# Reconstruir y reiniciar los contenedores
docker-compose down
docker-compose up -d --build

# Verificar que los contenedores estén corriendo
echo "✅ Verificando estado de contenedores:"
docker-compose ps

# Verificar logs del contenedor web
echo "📋 Logs del contenedor web (últimas 10 líneas):"
docker-compose logs --tail=10 web
EOF

echo "🎉 Configuración CORS actualizada exitosamente!"
echo ""
echo "🔗 Dominios ahora permitidos:"
echo "- ✅ http://localhost:3000 (desarrollo local)"
echo "- ✅ https://develop.d168j68zix66ce.amplifyapp.com (Amplify)"
echo "- ✅ https://lannister-news.com (producción)"
echo "- ✅ Patrón regex para todos los subdominios de Amplify"
echo ""
echo "🧪 Prueba la conexión desde el frontend ahora!"