#!/bin/bash

# =================================================================
# Script de Despliegue para AWS EC2 - Lannister Backend
# =================================================================

echo "🚀 Iniciando despliegue en AWS EC2..."

# 1. Actualizar sistema
echo "📦 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# 2. Instalar Python 3.11+ y dependencias
echo "🐍 Instalando Python y dependencias..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git

# 3. Crear usuario para la aplicación (opcional pero recomendado)
echo "👤 Configurando usuario de aplicación..."
sudo useradd -m -s /bin/bash lannister || echo "Usuario ya existe"

# 4. Clonar repositorio
echo "📥 Clonando repositorio..."
cd /home/lannister
sudo -u lannister git clone https://github.com/HouseLannisterDev/lannister-backend.git
cd lannister-backend

# 5. Crear entorno virtual
echo "🔧 Creando entorno virtual..."
sudo -u lannister python3 -m venv .venv
sudo -u lannister ./.venv/bin/pip install --upgrade pip

# 6. Instalar dependencias
echo "📚 Instalando dependencias Python..."
sudo -u lannister ./.venv/bin/pip install -r requirements.txt
sudo -u lannister ./.venv/bin/pip install gunicorn

# 7. Configurar variables de entorno
echo "⚙️ Configurando variables de entorno..."
sudo -u lannister cp .env.example .env
echo "⚠️  IMPORTANTE: Editar /home/lannister/lannister-backend/.env con credenciales reales"

# 8. Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
sudo -u lannister ./.venv/bin/python manage.py collectstatic --noinput
sudo -u lannister ./.venv/bin/python manage.py migrate

# 9. Crear superusuario
echo "👑 Crear superusuario (opcional)..."
echo "Ejecutar manualmente: sudo -u lannister ./.venv/bin/python manage.py createsuperuser"

echo "✅ Despliegue base completado!"
echo "📝 Próximos pasos:"
echo "   1. Editar /home/lannister/lannister-backend/.env"
echo "   2. Configurar Gunicorn service"
echo "   3. Configurar Nginx"
echo "   4. Configurar SSL (certbot)"