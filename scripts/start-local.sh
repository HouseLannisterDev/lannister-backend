#!/bin/bash

# Script para iniciar el entorno local de desarrollo
# ====================================================

set -e

echo "🚀 Iniciando entorno local de Lannister News..."
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker no está corriendo${NC}"
    echo "Por favor inicia Docker Desktop primero"
    exit 1
fi

# Cargar variables de entorno locales
if [ -f .env.local ]; then
    echo -e "${GREEN}✓${NC} Cargando configuración desde .env.local"
    export $(cat .env.local | grep -v '^#' | grep -v '^$' | xargs)
else
    echo -e "${YELLOW}⚠${NC} Archivo .env.local no encontrado, usando valores por defecto"
fi

# Iniciar contenedores de bases de datos
echo ""
echo "📦 Iniciando contenedores de bases de datos..."
docker compose --env-file .env.local up -d mysql mongo redis

# Esperar a que MySQL esté listo
echo ""
echo "⏳ Esperando a que MySQL esté listo..."
MAX_TRIES=30
TRIES=0
while ! docker exec lannister_mysql mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SELECT 1" > /dev/null 2>&1; do
    TRIES=$((TRIES + 1))
    if [ $TRIES -ge $MAX_TRIES ]; then
        echo -e "${RED}❌ MySQL no responde después de $MAX_TRIES intentos${NC}"
        exit 1
    fi
    echo -n "."
    sleep 2
done
echo -e "\n${GREEN}✓${NC} MySQL está listo"

# Esperar a que MongoDB esté listo
echo "⏳ Esperando a que MongoDB esté listo..."
MAX_TRIES=30
TRIES=0
until docker exec lannister_mongo mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; do
    TRIES=$((TRIES + 1))
    if [ $TRIES -ge $MAX_TRIES ]; then
        echo -e "${RED}❌ MongoDB no responde después de $MAX_TRIES intentos${NC}"
        exit 1
    fi
    echo -n "."
    sleep 2
done
echo -e "\n${GREEN}✓${NC} MongoDB está listo"

# Activar entorno virtual
echo ""
echo "🐍 Activando entorno virtual..."
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Error: Entorno virtual .venv no encontrado${NC}"
    echo "Ejecuta: python -m venv .venv"
    exit 1
fi
source .venv/bin/activate

# Aplicar migraciones
echo ""
echo "🔄 Aplicando migraciones de Django..."
python manage.py migrate

# Mostrar estado
echo ""
echo -e "${GREEN}✅ Entorno local iniciado correctamente${NC}"
echo ""
echo "📊 Servicios disponibles:"
echo "   - MySQL:   localhost:3306 (usuario: $MYSQL_USER)"
echo "   - MongoDB: localhost:27017"
echo "   - Redis:   localhost:6379"
echo ""
echo "🎯 Comandos útiles:"
echo "   - Iniciar servidor:    python manage.py runserver"
echo "   - Probar chatbot:      python chatbot/test_chatbot_local.py"
echo "   - Detener servicios:   docker compose down"
echo "   - Ver logs:            docker compose logs -f"
echo ""
echo "🧪 Para probar el chatbot con Postman:"
echo "   1. python manage.py runserver"
echo "   2. Importar: chatbot/Lannister_News_Chatbot.postman_collection.json"
echo "   3. Ejecutar requests a: http://localhost:8000/chatbot/"
echo ""
