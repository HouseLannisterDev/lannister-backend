#!/bin/bash

# Script para crear instancia EC2 para el backend Lannister
# Región: sa-east-1 (São Paulo)

echo "🚀 Creando instancia EC2 para Lannister Backend en sa-east-1..."

# Variables de configuración
REGION="sa-east-1"
INSTANCE_TYPE="t3.large"  # 2 vCPU, 8GB RAM, 50GB almacenamiento - óptimo para Django + ML
KEY_NAME="lannister-backend-key"
SECURITY_GROUP_NAME="lannister-backend-sg"
INSTANCE_NAME="lannister-backend-server"

# 1. Crear par de claves si no existe
echo "📝 Verificando/creando par de claves..."
aws ec2 describe-key-pairs --key-names $KEY_NAME --region $REGION 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Creando nuevo par de claves: $KEY_NAME"
    aws ec2 create-key-pair \
        --key-name $KEY_NAME \
        --region $REGION \
        --query 'KeyMaterial' \
        --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
    echo "✅ Par de claves creado y guardado en ${KEY_NAME}.pem"
else
    echo "✅ Par de claves $KEY_NAME ya existe"
fi

# 2. Crear Security Group
echo "🔒 Creando Security Group..."
SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name $SECURITY_GROUP_NAME \
    --description "Security group for Lannister Backend" \
    --region $REGION \
    --query 'GroupId' \
    --output text 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Security Group creado: $SECURITY_GROUP_ID"
    
    # Agregar reglas de seguridad
    echo "📋 Configurando reglas de seguridad..."
    
    # SSH (puerto 22)
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    # HTTP (puerto 80)
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    # HTTPS (puerto 443)
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    # Django (puerto 8000) - temporal para testing
    aws ec2 authorize-security-group-ingress \
        --group-id $SECURITY_GROUP_ID \
        --protocol tcp \
        --port 8000 \
        --cidr 0.0.0.0/0 \
        --region $REGION
    
    echo "✅ Reglas de seguridad configuradas"
else
    # Si ya existe, obtener el ID
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
        --group-names $SECURITY_GROUP_NAME \
        --region $REGION \
        --query 'SecurityGroups[0].GroupId' \
        --output text)
    echo "✅ Security Group ya existe: $SECURITY_GROUP_ID"
fi

# 3. Obtener AMI ID de Ubuntu 22.04 LTS más reciente
echo "🔍 Obteniendo AMI ID de Ubuntu 22.04 LTS..."
AMI_ID=$(aws ec2 describe-images \
    --owners 099720109477 \
    --filters \
        "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
        "Name=state,Values=available" \
    --region $REGION \
    --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
    --output text)

echo "✅ AMI ID encontrado: $AMI_ID"

# 4. Script de inicialización (User Data)
USER_DATA_SCRIPT='#!/bin/bash
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
'

# 5. Crear instancia EC2
echo "🚀 Lanzando instancia EC2..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --user-data "$USER_DATA_SCRIPT" \
    --region $REGION \
    --block-device-mappings '[
        {
            "DeviceName": "/dev/sda1",
            "Ebs": {
                "VolumeSize": 50,
                "VolumeType": "gp3",
                "DeleteOnTermination": true,
                "Encrypted": true
            }
        }
    ]' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=$INSTANCE_NAME}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Instancia EC2 creada: $INSTANCE_ID"

# 6. Esperar que la instancia esté running
echo "⏳ Esperando que la instancia esté en estado 'running'..."
aws ec2 wait instance-running --instance-ids $INSTANCE_ID --region $REGION

# 7. Obtener IP pública
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids $INSTANCE_ID \
    --region $REGION \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo ""
echo "🎉 ¡Instancia EC2 creada exitosamente!"
echo "📋 Detalles:"
echo "   - Instance ID: $INSTANCE_ID"
echo "   - IP Pública: $PUBLIC_IP"
echo "   - Key Pair: ${KEY_NAME}.pem"
echo "   - Security Group: $SECURITY_GROUP_ID"
echo ""
echo "🔑 Para conectarte por SSH:"
echo "   ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP"
echo ""
echo "⏳ La instancia tardará unos 3-5 minutos en completar la inicialización."
echo "   Puedes verificar el progreso con:"
echo "   ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'tail -f /var/log/cloud-init-output.log'"