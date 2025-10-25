#!/bin/bash
# Script de despliegue automatizado para AWS
# Ejecutar: ./deploy-aws.sh

set -e  # Salir si hay errores

echo "🚀 Iniciando despliegue Lannister Backend en AWS..."

# Variables (editar con tus valores)
AWS_REGION="sa-east-1"
EC2_INSTANCE_TYPE="t3.medium"
KEY_PAIR_NAME="lannister-key"  # Crear en AWS Console
APP_NAME="lannister-backend"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Verificar dependencias
check_dependencies() {
    log "Verificando dependencias..."
    
    if ! command -v aws &> /dev/null; then
        error "AWS CLI no está instalado. Instalar desde: https://aws.amazon.com/cli/"
    fi
    
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado. Instalar desde: https://docker.com"
    fi
    
    # Verificar credenciales AWS
    if ! aws sts get-caller-identity &> /dev/null; then
        error "Credenciales AWS no configuradas. Ejecutar: aws configure"
    fi
    
    log "✅ Dependencias verificadas"
}

# Construir imagen Docker
build_docker() {
    log "Construyendo imagen Docker..."
    
    if [ ! -f "Dockerfile.prod" ]; then
        error "Dockerfile.prod no encontrado"
    fi
    
    docker build -f Dockerfile.prod -t ${APP_NAME}:prod . || error "Error construyendo imagen"
    
    log "✅ Imagen Docker construida: ${APP_NAME}:prod"
}

# Crear VPC si no existe
create_vpc() {
    log "Verificando/Creando VPC..."
    
    # Buscar VPC existente
    VPC_ID=$(aws ec2 describe-vpcs \
        --filters "Name=tag:Name,Values=${APP_NAME}-vpc" \
        --query 'Vpcs[0].VpcId' \
        --output text 2>/dev/null)
    
    if [ "$VPC_ID" = "None" ] || [ -z "$VPC_ID" ]; then
        log "Creando nueva VPC..."
        VPC_ID=$(aws ec2 create-vpc \
            --cidr-block 10.0.0.0/16 \
            --tag-specifications "ResourceType=vpc,Tags=[{Key=Name,Value=${APP_NAME}-vpc}]" \
            --query 'Vpc.VpcId' \
            --output text)
        
        # Habilitar DNS
        aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames
        aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support
    fi
    
    log "✅ VPC ID: $VPC_ID"
    echo $VPC_ID > .vpc_id
}

# Crear subnets
create_subnets() {
    log "Creando subnets..."
    VPC_ID=$(cat .vpc_id)
    
    # Subnet pública
    SUBNET_ID=$(aws ec2 create-subnet \
        --vpc-id $VPC_ID \
        --cidr-block 10.0.1.0/24 \
        --availability-zone ${AWS_REGION}a \
        --tag-specifications "ResourceType=subnet,Tags=[{Key=Name,Value=${APP_NAME}-public-subnet}]" \
        --query 'Subnet.SubnetId' \
        --output text)
    
    # Habilitar IP pública automática
    aws ec2 modify-subnet-attribute --subnet-id $SUBNET_ID --map-public-ip-on-launch
    
    log "✅ Subnet ID: $SUBNET_ID"
    echo $SUBNET_ID > .subnet_id
}

# Crear Internet Gateway
create_igw() {
    log "Creando Internet Gateway..."
    VPC_ID=$(cat .vpc_id)
    
    IGW_ID=$(aws ec2 create-internet-gateway \
        --tag-specifications "ResourceType=internet-gateway,Tags=[{Key=Name,Value=${APP_NAME}-igw}]" \
        --query 'InternetGateway.InternetGatewayId' \
        --output text)
    
    # Adjuntar a VPC
    aws ec2 attach-internet-gateway --vpc-id $VPC_ID --internet-gateway-id $IGW_ID
    
    # Crear route table
    ROUTE_TABLE_ID=$(aws ec2 create-route-table \
        --vpc-id $VPC_ID \
        --tag-specifications "ResourceType=route-table,Tags=[{Key=Name,Value=${APP_NAME}-rt}]" \
        --query 'RouteTable.RouteTableId' \
        --output text)
    
    # Agregar ruta a internet
    aws ec2 create-route --route-table-id $ROUTE_TABLE_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
    
    # Asociar subnet
    SUBNET_ID=$(cat .subnet_id)
    aws ec2 associate-route-table --subnet-id $SUBNET_ID --route-table-id $ROUTE_TABLE_ID
    
    log "✅ Internet Gateway configurado"
}

# Crear Security Groups
create_security_groups() {
    log "Creando Security Groups..."
    VPC_ID=$(cat .vpc_id)
    
    # SG para EC2
    EC2_SG_ID=$(aws ec2 create-security-group \
        --group-name ${APP_NAME}-web-sg \
        --description "Security group for web server" \
        --vpc-id $VPC_ID \
        --query 'GroupId' \
        --output text)
    
    # Reglas para EC2 SG
    aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
    aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0
    aws ec2 authorize-security-group-ingress --group-id $EC2_SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
    
    log "✅ Security Group creado: $EC2_SG_ID"
    echo $EC2_SG_ID > .sg_id
}

# Lanzar EC2 instance
launch_ec2() {
    log "Lanzando EC2 instance..."
    
    SUBNET_ID=$(cat .subnet_id)
    SG_ID=$(cat .sg_id)
    
    # Obtener AMI más reciente de Ubuntu
    AMI_ID=$(aws ec2 describe-images \
        --owners 099720109477 \
        --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" \
        --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' \
        --output text)
    
    log "Usando AMI: $AMI_ID"
    
    # Crear user data script
    cat > user_data.sh << 'EOF'
#!/bin/bash
apt-get update
apt-get install -y docker.io docker-compose-plugin awscli git
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

# Instalar Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
EOF

    # Lanzar instancia
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --count 1 \
        --instance-type $EC2_INSTANCE_TYPE \
        --key-name $KEY_PAIR_NAME \
        --security-group-ids $SG_ID \
        --subnet-id $SUBNET_ID \
        --user-data file://user_data.sh \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${APP_NAME}-server}]" \
        --query 'Instances[0].InstanceId' \
        --output text)
    
    log "✅ EC2 Instance lanzada: $INSTANCE_ID"
    echo $INSTANCE_ID > .instance_id
    
    # Esperar que esté running
    log "Esperando que la instancia esté lista..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
    
    # Obtener IP pública
    PUBLIC_IP=$(aws ec2 describe-instances \
        --instance-ids $INSTANCE_ID \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)
    
    log "✅ IP Pública: $PUBLIC_IP"
    echo $PUBLIC_IP > .public_ip
    
    rm -f user_data.sh
}

# Desplegar aplicación
deploy_app() {
    PUBLIC_IP=$(cat .public_ip)
    log "Desplegando aplicación en $PUBLIC_IP..."
    
    warning "ESPERANDO 2 MINUTOS para que termine la configuración inicial..."
    sleep 120
    
    # Verificar conexión SSH
    ssh -o StrictHostKeyChecking=no -i ~/.ssh/${KEY_PAIR_NAME}.pem ubuntu@$PUBLIC_IP "echo 'SSH funcionando'" || error "No se puede conectar por SSH"
    
    # Transferir archivos necesarios
    scp -i ~/.ssh/${KEY_PAIR_NAME}.pem -r . ubuntu@$PUBLIC_IP:/home/ubuntu/app/
    
    # Ejecutar comandos remotos
    ssh -i ~/.ssh/${KEY_PAIR_NAME}.pem ubuntu@$PUBLIC_IP << 'ENDSSH'
cd /home/ubuntu/app
docker build -f Dockerfile.prod -t lannister-backend:prod .
docker run -d --name lannister-app -p 80:80 --env-file .env lannister-backend:prod
docker ps
ENDSSH

    log "✅ Aplicación desplegada exitosamente!"
}

# Cleanup en caso de error
cleanup() {
    log "Limpiando archivos temporales..."
    rm -f .vpc_id .subnet_id .sg_id .instance_id .public_ip user_data.sh
}

# Función principal
main() {
    trap cleanup EXIT
    
    check_dependencies
    build_docker
    create_vpc
    create_subnets
    create_igw
    create_security_groups
    launch_ec2
    deploy_app
    
    PUBLIC_IP=$(cat .public_ip)
    
    echo
    log "🎉 ¡DESPLIEGUE COMPLETADO!"
    log "🌐 Tu aplicación está disponible en: http://$PUBLIC_IP"
    log "🔧 SSH: ssh -i ~/.ssh/${KEY_PAIR_NAME}.pem ubuntu@$PUBLIC_IP"
    echo
    warning "¡No olvides configurar tu archivo .env con las credenciales reales!"
    warning "¡Configura un dominio y SSL para producción!"
}

# Verificar argumentos
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Uso: $0 [opciones]"
    echo
    echo "Este script despliega automáticamente la aplicación Lannister Backend en AWS"
    echo
    echo "Prerrequisitos:"
    echo "  - AWS CLI configurado (aws configure)"
    echo "  - Docker instalado"
    echo "  - Key pair creado en AWS (${KEY_PAIR_NAME}.pem en ~/.ssh/)"
    echo "  - Archivo .env configurado"
    echo
    echo "El script creará:"
    echo "  - VPC con subnet pública"
    echo "  - Security Groups"
    echo "  - Internet Gateway"
    echo "  - EC2 instance con Docker"
    echo "  - Despliegue de la aplicación"
    exit 0
fi

# Verificar que existe el key pair
if [ ! -f ~/.ssh/${KEY_PAIR_NAME}.pem ]; then
    error "Key pair no encontrado: ~/.ssh/${KEY_PAIR_NAME}.pem"
fi

# Verificar que existe .env
if [ ! -f .env ]; then
    warning "Archivo .env no encontrado. Copiando desde .env.example..."
    cp .env.example .env
    error "Configura el archivo .env con tus credenciales reales y ejecuta de nuevo"
fi

# Ejecutar
main