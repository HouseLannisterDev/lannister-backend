#!/bin/bash

# =================================================================
# CONFIGURACIÓN DE MONITOREO CLOUDWATCH PARA LANNISTER NEWS
# =================================================================

set -e

echo "🔍 Configurando monitoreo CloudWatch para Lannister News..."

# Configuración
INSTANCE_ID="i-0123456789abcdef0"  # Actualizar con tu Instance ID real
RDS_DB_IDENTIFIER="database-1"      # Tu RDS identifier
REGION="sa-east-1"
SNS_TOPIC_NAME="lannister-news-alerts"
EMAIL="tu-email@ejemplo.com"        # Actualizar con tu email

# =================================================================
# 1. CREAR TOPIC SNS PARA ALERTAS
# =================================================================

echo "📧 Creando topic SNS para notificaciones..."

SNS_TOPIC_ARN=$(aws sns create-topic \
    --name $SNS_TOPIC_NAME \
    --region $REGION \
    --query 'TopicArn' \
    --output text)

echo "✅ Topic SNS creado: $SNS_TOPIC_ARN"

# Suscribir email al topic
aws sns subscribe \
    --topic-arn $SNS_TOPIC_ARN \
    --protocol email \
    --notification-endpoint $EMAIL \
    --region $REGION

echo "📨 Suscripción de email creada. Revisa tu correo y confirma la suscripción."

# =================================================================
# 2. ALARMAS PARA EC2
# =================================================================

echo "🖥️ Configurando alarmas para EC2..."

# CPU Utilization - Alta
aws cloudwatch put-metric-alarm \
    --alarm-name "EC2-Lannister-HighCPU" \
    --alarm-description "Alerta cuando CPU > 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions $SNS_TOPIC_ARN \
    --dimensions Name=InstanceId,Value=$INSTANCE_ID \
    --region $REGION

# Memory Utilization (requiere CloudWatch Agent)
aws cloudwatch put-metric-alarm \
    --alarm-name "EC2-Lannister-HighMemory" \
    --alarm-description "Alerta cuando Memoria > 85%" \
    --metric-name mem_used_percent \
    --namespace CWAgent \
    --statistic Average \
    --period 300 \
    --threshold 85 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions $SNS_TOPIC_ARN \
    --dimensions Name=InstanceId,Value=$INSTANCE_ID \
    --region $REGION

# Disk Usage
aws cloudwatch put-metric-alarm \
    --alarm-name "EC2-Lannister-HighDisk" \
    --alarm-description "Alerta cuando Disco > 85%" \
    --metric-name disk_used_percent \
    --namespace CWAgent \
    --statistic Average \
    --period 300 \
    --threshold 85 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --alarm-actions $SNS_TOPIC_ARN \
    --dimensions Name=InstanceId,Value=$INSTANCE_ID,Name=device,Value=/dev/xvda1,Name=fstype,Value=ext4,Name=path,Value=/ \
    --region $REGION

# Instance Status Check
aws cloudwatch put-metric-alarm \
    --alarm-name "EC2-Lannister-StatusCheckFailed" \
    --alarm-description "Alerta cuando falla el status check" \
    --metric-name StatusCheckFailed \
    --namespace AWS/EC2 \
    --statistic Maximum \
    --period 60 \
    --threshold 0 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions $SNS_TOPIC_ARN \
    --dimensions Name=InstanceId,Value=$INSTANCE_ID \
    --region $REGION

echo "✅ Alarmas EC2 configuradas"

# =================================================================
# 3. ALARMAS PARA RDS
# =================================================================

echo "🗄️ Configurando alarmas para RDS..."

# CPU Utilization RDS
aws cloudwatch put-metric-alarm \
    --alarm-name "RDS-Lannister-HighCPU" \
    --alarm-description "Alerta cuando RDS CPU > 80%" \
    --metric-name CPUUtilization \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions $SNS_TOPIC_ARN \
    --dimensions Name=DBInstanceIdentifier,Value=$RDS_DB_IDENTIFIER \
    --region $REGION

# Database Connections
aws cloudwatch put-metric-alarm \
    --alarm-name "RDS-Lannister-HighConnections" \
    --alarm-description "Alerta cuando conexiones > 15" \
    --metric-name DatabaseConnections \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 15 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions $SNS_TOPIC_ARN \
    --dimensions Name=DBInstanceIdentifier,Value=$RDS_DB_IDENTIFIER \
    --region $REGION

# Free Storage Space (menos de 2GB)
aws cloudwatch put-metric-alarm \
    --alarm-name "RDS-Lannister-LowStorage" \
    --alarm-description "Alerta cuando storage < 2GB" \
    --metric-name FreeStorageSpace \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 2000000000 \
    --comparison-operator LessThanThreshold \
    --evaluation-periods 1 \
    --alarm-actions $SNS_TOPIC_ARN \
    --dimensions Name=DBInstanceIdentifier,Value=$RDS_DB_IDENTIFIER \
    --region $REGION

# Read/Write Latency
aws cloudwatch put-metric-alarm \
    --alarm-name "RDS-Lannister-HighLatency" \
    --alarm-description "Alerta cuando latencia > 0.2s" \
    --metric-name ReadLatency \
    --namespace AWS/RDS \
    --statistic Average \
    --period 300 \
    --threshold 0.2 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions $SNS_TOPIC_ARN \
    --dimensions Name=DBInstanceIdentifier,Value=$RDS_DB_IDENTIFIER \
    --region $REGION

echo "✅ Alarmas RDS configuradas"

# =================================================================
# 4. ALARMAS PERSONALIZADAS PARA LA APLICACIÓN
# =================================================================

echo "🚀 Configurando alarmas personalizadas..."

# HTTP 5xx Errors (si usas ALB)
# aws cloudwatch put-metric-alarm \
#     --alarm-name "HTTP-Lannister-5xxErrors" \
#     --alarm-description "Alerta por errores 5xx" \
#     --metric-name HTTPCode_Target_5XX_Count \
#     --namespace AWS/ApplicationELB \
#     --statistic Sum \
#     --period 300 \
#     --threshold 10 \
#     --comparison-operator GreaterThanThreshold \
#     --evaluation-periods 2 \
#     --alarm-actions $SNS_TOPIC_ARN \
#     --dimensions Name=LoadBalancer,Value=app/lannister-news-alb/xxxxx \
#     --region $REGION

echo "🎉 Configuración de CloudWatch completada!"

# =================================================================
# 5. CREAR DASHBOARD
# =================================================================

echo "📊 Creando dashboard personalizado..."

DASHBOARD_BODY='{
    "widgets": [
        {
            "type": "metric",
            "x": 0,
            "y": 0,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/EC2", "CPUUtilization", "InstanceId", "'$INSTANCE_ID'" ],
                    [ "CWAgent", "mem_used_percent", "InstanceId", "'$INSTANCE_ID'" ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "'$REGION'",
                "title": "EC2 - CPU y Memoria",
                "period": 300
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 0,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "'$RDS_DB_IDENTIFIER'" ],
                    [ ".", "DatabaseConnections", ".", "." ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "'$REGION'",
                "title": "RDS - CPU y Conexiones",
                "period": 300
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 6,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "CWAgent", "disk_used_percent", "InstanceId", "'$INSTANCE_ID'", "device", "/dev/xvda1", "fstype", "ext4", "path", "/" ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "'$REGION'",
                "title": "EC2 - Uso de Disco",
                "period": 300
            }
        },
        {
            "type": "metric",
            "x": 12,
            "y": 6,
            "width": 12,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/RDS", "FreeStorageSpace", "DBInstanceIdentifier", "'$RDS_DB_IDENTIFIER'" ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "'$REGION'",
                "title": "RDS - Storage Libre",
                "period": 300
            }
        }
    ]
}'

aws cloudwatch put-dashboard \
    --dashboard-name "Lannister-News-Dashboard" \
    --dashboard-body "$DASHBOARD_BODY" \
    --region $REGION

echo "✅ Dashboard creado: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#dashboards:name=Lannister-News-Dashboard"

# =================================================================
# RESUMEN
# =================================================================

echo ""
echo "🎉 MONITOREO CLOUDWATCH CONFIGURADO EXITOSAMENTE!"
echo ""
echo "📊 Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#dashboards:name=Lannister-News-Dashboard"
echo "🔔 Topic SNS: $SNS_TOPIC_ARN"
echo "📧 Email configurado: $EMAIL"
echo ""
echo "ALARMAS CONFIGURADAS:"
echo "- ✅ EC2 CPU > 80%"
echo "- ✅ EC2 Memoria > 85%"
echo "- ✅ EC2 Disco > 85%"
echo "- ✅ EC2 Status Check fallos"
echo "- ✅ RDS CPU > 80%"
echo "- ✅ RDS Conexiones > 15"
echo "- ✅ RDS Storage < 2GB"
echo "- ✅ RDS Latencia > 0.2s"
echo ""
echo "🔍 Próximos pasos:"
echo "1. Confirma la suscripción en tu email"
echo "2. Instala CloudWatch Agent para métricas avanzadas"
echo "3. Revisa el dashboard en la consola AWS"