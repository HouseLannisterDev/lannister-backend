#!/bin/bash

# Script para crear instancia RDS MySQL para Lannister Backend
# Región: sa-east-1 (São Paulo)

echo "🗄️ Creando instancia RDS MySQL para Lannister Backend..."

# Variables de configuración
REGION="sa-east-1"
DB_INSTANCE_IDENTIFIER="lannister-mysql-db"
DB_NAME="lannister_news"
DB_USERNAME="admin"

# 🔒 SEGURIDAD: Password debe pasarse como variable de entorno
# Usar: export DB_PASSWORD="tu-password-seguro" antes de ejecutar este script
# O pasar como argumento: ./02-create-rds-mysql.sh "tu-password-seguro"
if [ -z "$DB_PASSWORD" ]; then
    if [ -n "$1" ]; then
        DB_PASSWORD="$1"
    else
        echo "❌ ERROR: DB_PASSWORD no está configurado"
        echo "Opciones:"
        echo "  1. Exportar variable: export DB_PASSWORD='tu-password-seguro'"
        echo "  2. Pasar como argumento: ./02-create-rds-mysql.sh 'tu-password-seguro'"
        exit 1
    fi
fi

DB_INSTANCE_CLASS="db.t3.micro"  # Capa gratuita elegible
ALLOCATED_STORAGE=20
STORAGE_TYPE="gp2"
ENGINE="mysql"
ENGINE_VERSION="8.0.35"
SUBNET_GROUP_NAME="lannister-db-subnet-group"
PARAMETER_GROUP_NAME="lannister-mysql-params"
SECURITY_GROUP_NAME="lannister-rds-sg"

# 1. Crear Security Group para RDS
echo "🔒 Creando Security Group para RDS..."
RDS_SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name $SECURITY_GROUP_NAME \
    --description "Security group for Lannister RDS MySQL" \
    --region $REGION \
    --query 'GroupId' \
    --output text 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ Security Group para RDS creado: $RDS_SECURITY_GROUP_ID"
    
    # Permitir acceso MySQL desde EC2 (puerto 3306)
    # Primero obtener el security group de EC2
    EC2_SG_ID=$(aws ec2 describe-security-groups \
        --group-names "lannister-backend-sg" \
        --region $REGION \
        --query 'SecurityGroups[0].GroupId' \
        --output text 2>/dev/null)
    
    if [ "$EC2_SG_ID" != "None" ] && [ -n "$EC2_SG_ID" ]; then
        aws ec2 authorize-security-group-ingress \
            --group-id $RDS_SECURITY_GROUP_ID \
            --protocol tcp \
            --port 3306 \
            --source-group $EC2_SG_ID \
            --region $REGION
        echo "✅ Acceso MySQL desde EC2 configurado"
    else
        echo "⚠️ No se encontró security group de EC2, permitiendo acceso desde cualquier IP (TEMPORAL)"
        aws ec2 authorize-security-group-ingress \
            --group-id $RDS_SECURITY_GROUP_ID \
            --protocol tcp \
            --port 3306 \
            --cidr 0.0.0.0/0 \
            --region $REGION
    fi
else
    # Si ya existe, obtener el ID
    RDS_SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
        --group-names $SECURITY_GROUP_NAME \
        --region $REGION \
        --query 'SecurityGroups[0].GroupId' \
        --output text)
    echo "✅ Security Group para RDS ya existe: $RDS_SECURITY_GROUP_ID"
fi

# 2. Obtener subnets disponibles para crear subnet group
echo "🌐 Configurando subnet group para RDS..."
SUBNET_IDS=$(aws ec2 describe-subnets \
    --region $REGION \
    --filters "Name=availability-zone,Values=${REGION}a,${REGION}b,${REGION}c" \
    --query 'Subnets[].SubnetId' \
    --output text)

# Convertir a array
SUBNET_ARRAY=($SUBNET_IDS)

# Crear DB Subnet Group
aws rds create-db-subnet-group \
    --db-subnet-group-name $SUBNET_GROUP_NAME \
    --db-subnet-group-description "Subnet group for Lannister MySQL DB" \
    --subnet-ids ${SUBNET_ARRAY[@]} \
    --region $REGION 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ DB Subnet Group creado: $SUBNET_GROUP_NAME"
else
    echo "✅ DB Subnet Group ya existe: $SUBNET_GROUP_NAME"
fi

# 3. Crear Parameter Group personalizado para MySQL
echo "⚙️ Creando Parameter Group para MySQL..."
aws rds create-db-parameter-group \
    --db-parameter-group-name $PARAMETER_GROUP_NAME \
    --db-parameter-group-family mysql8.0 \
    --description "Custom parameter group for Lannister MySQL" \
    --region $REGION 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Parameter Group creado: $PARAMETER_GROUP_NAME"
    
    # Configurar parámetros optimizados para Django
    aws rds modify-db-parameter-group \
        --db-parameter-group-name $PARAMETER_GROUP_NAME \
        --parameters \
            "ParameterName=innodb_buffer_pool_size,ParameterValue={DBInstanceClassMemory*3/4},ApplyMethod=pending-reboot" \
            "ParameterName=max_connections,ParameterValue=200,ApplyMethod=pending-reboot" \
            "ParameterName=innodb_file_per_table,ParameterValue=1,ApplyMethod=pending-reboot" \
        --region $REGION
    echo "✅ Parámetros de MySQL configurados"
else
    echo "✅ Parameter Group ya existe: $PARAMETER_GROUP_NAME"
fi

# 4. Crear instancia RDS
echo "🚀 Creando instancia RDS MySQL..."
aws rds create-db-instance \
    --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
    --db-instance-class $DB_INSTANCE_CLASS \
    --engine $ENGINE \
    --engine-version $ENGINE_VERSION \
    --master-username $DB_USERNAME \
    --master-user-password $DB_PASSWORD \
    --allocated-storage $ALLOCATED_STORAGE \
    --storage-type $STORAGE_TYPE \
    --db-name $DB_NAME \
    --vpc-security-group-ids $RDS_SECURITY_GROUP_ID \
    --db-subnet-group-name $SUBNET_GROUP_NAME \
    --db-parameter-group-name $PARAMETER_GROUP_NAME \
    --backup-retention-period 7 \
    --storage-encrypted \
    --deletion-protection \
    --region $REGION \
    --tags \
        "Key=Name,Value=Lannister MySQL Database" \
        "Key=Environment,Value=Production" \
        "Key=Project,Value=Lannister-Backend"

if [ $? -eq 0 ]; then
    echo "✅ Instancia RDS MySQL creación iniciada: $DB_INSTANCE_IDENTIFIER"
    
    # 5. Esperar que la instancia esté disponible
    echo "⏳ Esperando que la instancia RDS esté disponible (esto puede tomar 10-15 minutos)..."
    aws rds wait db-instance-available \
        --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
        --region $REGION
    
    # 6. Obtener endpoint de la base de datos
    DB_ENDPOINT=$(aws rds describe-db-instances \
        --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
        --region $REGION \
        --query 'DBInstances[0].Endpoint.Address' \
        --output text)
    
    DB_PORT=$(aws rds describe-db-instances \
        --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
        --region $REGION \
        --query 'DBInstances[0].Endpoint.Port' \
        --output text)
    
    echo ""
    echo "🎉 ¡Instancia RDS MySQL creada exitosamente!"
    echo "📋 Detalles de conexión:"
    echo "   - Endpoint: $DB_ENDPOINT"
    echo "   - Puerto: $DB_PORT"
    echo "   - Base de datos: $DB_NAME"
    echo "   - Usuario: $DB_USERNAME"
    echo "   - Contraseña: $DB_PASSWORD"
    echo ""
    echo "🔧 Variables de entorno para Django:"
    echo "   export MYSQL_HOST=$DB_ENDPOINT"
    echo "   export MYSQL_PORT=$DB_PORT"
    echo "   export MYSQL_DB=$DB_NAME"
    echo "   export MYSQL_USER=$DB_USERNAME"
    echo "   export MYSQL_PASSWORD=$DB_PASSWORD"
    echo ""
    echo "📝 Guarda estos datos de forma segura!"
    
    # Guardar credenciales en archivo
    cat > rds-credentials.txt << EOF
# Credenciales RDS MySQL para Lannister Backend
DB_ENDPOINT=$DB_ENDPOINT
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USERNAME=$DB_USERNAME
DB_PASSWORD=$DB_PASSWORD

# Variables de entorno para .env
MYSQL_HOST=$DB_ENDPOINT
MYSQL_PORT=$DB_PORT
MYSQL_DB=$DB_NAME
MYSQL_USER=$DB_USERNAME
MYSQL_PASSWORD=$DB_PASSWORD
EOF
    
    echo "💾 Credenciales guardadas en: rds-credentials.txt"
    
else
    echo "❌ Error al crear la instancia RDS"
    exit 1
fi