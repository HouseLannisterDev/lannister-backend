#!/bin/bash
# Actualizar sistema
apt-get update
apt-get upgrade -y

# Instalar Docker
apt-get install -y ca-certificates curl gnupg lsb-release
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Instalar Docker Compose standalone
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Instalar Git
apt-get install -y git

# Crear usuario para la aplicación
useradd -m -s /bin/bash lannister
usermod -aG docker lannister

# Instalar AWS CLI
apt-get install -y awscli

# Instalar Nginx
apt-get install -y nginx

# Crear directorio para la aplicación
mkdir -p /home/lannister/app
chown -R lannister:lannister /home/lannister/app

echo "✅ Servidor inicializado correctamente" > /home/lannister/init-complete.log