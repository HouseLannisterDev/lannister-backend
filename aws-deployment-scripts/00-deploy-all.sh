#!/bin/bash

# Script principal para desplegar completo Lannister Backend en AWS
# Ejecuta todos los pasos en orden

echo "🚀 DESPLIEGUE COMPLETO LANNISTER BACKEND EN AWS"
echo "=============================================="
echo ""

# Verificar que AWS CLI esté configurado
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ Error: AWS CLI no está configurado o las credenciales son inválidas">&2
    echo "   Ejecuta: aws configure"
    exit 1
fi

echo "✅ AWS CLI configurado correctamente"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "   - Account ID: $ACCOUNT_ID"
echo ""

# Crear directorio para logs
mkdir -p deployment-logs

# PASO 1: Crear instancia EC2
echo "📋 PASO 1: Creando instancia EC2..."
./01-create-ec2-instance.sh 2>&1 | tee deployment-logs/01-ec2-creation.log

if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
    echo "❌ Error en la creación de EC2. Ver log: deployment-logs/01-ec2-creation.log">&2
    exit 1
fi

# Extraer IP pública del log
PUBLIC_IP=$(grep "IP Pública:" deployment-logs/01-ec2-creation.log | awk '{print $3}')
if [[ -z "$PUBLIC_IP" ]]; then
    echo "❌ No se pudo obtener la IP pública de la instancia EC2"
    exit 1
fi

echo "✅ EC2 creado exitosamente - IP: $PUBLIC_IP"
echo ""

# PASO 2: Crear RDS MySQL (solo si no existe una configuración previa)
echo "📋 PASO 2: ¿Crear nueva instancia RDS MySQL? (y/n)"
echo "   (Si ya tienes una instancia RDS, presiona 'n' y proporciona los datos manualmente)"
read -p "Respuesta: " create_rds

if [[ "$create_rds" = "y" ]] || [[ "$create_rds" = "Y" ]]; then
    echo "Creando instancia RDS MySQL..."
    ./02-create-rds-mysql.sh 2>&1 | tee deployment-logs/02-rds-creation.log
    
    if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
        echo "❌ Error en la creación de RDS. Ver log: deployment-logs/02-rds-creation.log">&2
        exit 1
    fi
    echo "✅ RDS MySQL creado exitosamente"
else
    echo "⚠️ Usando instancia RDS existente"
    echo "   Asegúrate de que el archivo rds-credentials.txt esté presente con los datos correctos"
fi

echo ""

# PASO 3: Configurar variables de entorno para MongoDB
echo "📋 PASO 3: Configuración de MongoDB"
echo "Por favor proporciona la URI de conexión a MongoDB Atlas:"
read -p "MongoDB URI: " MONGO_URI

if [[ -z "$MONGO_URI" ]]; then
    echo "⚠️ No se proporcionó URI de MongoDB, usando configuración local"
    MONGO_URI="mongodb://localhost:27017/lannister_news"
fi

# Actualizar .env con MongoDB URI
if [[ -f "/tmp/.env" ]]; then
    sed -i.bak "s|MONGO_URI=.*|MONGO_URI=$MONGO_URI|" /tmp/.env
else
    echo "MONGO_URI=$MONGO_URI" > /tmp/mongo-config.txt
fi

echo "✅ Configuración de MongoDB guardada"
echo ""

# PASO 4: Esperar a que EC2 esté completamente listo
echo "📋 PASO 4: Esperando que EC2 complete la inicialización..."
echo "   Esto puede tomar entre 3-5 minutos..."

for i in {1..20}; do
    if ssh -i lannister-backend-key.pem -o StrictHostKeyChecking=no -o ConnectTimeout=10 ubuntu@$PUBLIC_IP "echo 'ready'" > /dev/null 2>&1; then
        echo "✅ EC2 listo para el despliegue"
        break
    fi
    if [[ $i -eq 20 ]]; then
        echo "❌ Timeout: EC2 no está respondiendo después de 10 minutos"
        echo "   Puedes intentar el despliegue manualmente con:"
        echo "   ./03-deploy-backend.sh $PUBLIC_IP lannister-backend-key.pem"
        exit 1
    fi
    echo "   Intento $i/20 - Esperando 30 segundos..."
    sleep 30
done

echo ""

# PASO 5: Desplegar backend
echo "📋 PASO 5: Desplegando backend en EC2..."
./03-deploy-backend.sh $PUBLIC_IP lannister-backend-key.pem 2>&1 | tee deployment-logs/03-backend-deployment.log

if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
    echo "❌ Error en el despliegue del backend. Ver log: deployment-logs/03-backend-deployment.log">&2
    exit 1
fi

echo ""
echo "🎉 ¡DESPLIEGUE COMPLETADO EXITOSAMENTE!"
echo "======================================"
echo ""
echo "📋 Resumen del despliegue:"
echo "   - IP Pública EC2: $PUBLIC_IP"
echo "   - URL de la aplicación: http://$PUBLIC_IP"
echo "   - URL del admin: http://$PUBLIC_IP/admin/"
echo "   - MongoDB URI: $MONGO_URI"
echo ""
echo "📁 Archivos generados:"
echo "   - lannister-backend-key.pem (clave privada SSH)"
echo "   - rds-credentials.txt (credenciales de base de datos)"
echo "   - deployment-logs/ (logs del despliegue)"
echo ""
echo "🔧 Próximos pasos:"
echo "   1. Probar la aplicación en: http://$PUBLIC_IP"
echo "   2. Crear superusuario de Django si es necesario"
echo "   3. Configurar dominio personalizado"
echo "   4. Configurar HTTPS con certificado SSL"
echo "   5. Configurar backup automático de RDS"
echo ""
echo "🔗 Comandos útiles:"
echo "   - Conectar SSH: ssh -i lannister-backend-key.pem ubuntu@$PUBLIC_IP"
echo "   - Ver logs: ssh -i lannister-backend-key.pem ubuntu@$PUBLIC_IP 'cd /home/lannister/app && docker-compose -f docker-compose.prod.yml logs -f'"
echo "   - Reiniciar: ssh -i lannister-backend-key.pem ubuntu@$PUBLIC_IP 'cd /home/lannister/app && docker-compose -f docker-compose.prod.yml restart'"
echo ""
echo "💾 ¡Guarda estos datos de forma segura!"
