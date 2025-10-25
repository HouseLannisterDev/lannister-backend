# 🚀 Guía de Despliegue AWS - Lannister Backend

## 📋 Información Necesaria ANTES de Empezar

**🔑 DATOS QUE NECESITAS PROPORCIONARME:**

### 1. Credenciales RDS MySQL (Ya existente)

- ✅ Host: `database-1.cpcimk2ikn91.sa-east-1.rds.amazonaws.com`
- ❓ **Usuario**: (necesito confirmación si es `admin`)
- ❓ **Contraseña**: (necesito la contraseña real)
- ❓ **Puerto**: (asumo 3306, confirmar)
- ❓ **Nombre BD**: (asumo `lannister_news`, confirmar)

### 2. MongoDB Atlas

- ❓ **URI de conexión completa**: `mongodb+srv://...`
- ❓ **Usuario y contraseña**
- ❓ **Nombre de la base de datos**

### 3. AWS Account Info

- ❓ **Access Key ID**
- ❓ **Secret Access Key**
- ❓ **Región preferida**: (recomiendo `sa-east-1` igual que tu RDS)

### 4. Dominio (opcional)

- ❓ **Dominio personalizado** o usar IP elástica de AWS

---

## 🏗️ PASO A PASO - DESPLIEGUE COMPLETO

### FASE 1: Preparación Local

#### 1.1 Construir imagen Docker

```bash
# En tu directorio del proyecto
cd /ruta/a/lannister-backend

# Construcción para pruebas locales
docker build -t lannister-backend:latest .

# Construcción optimizada para producción
docker build -f Dockerfile.prod -t lannister-backend:prod .
```

#### 1.2 Probar localmente (opcional)

```bash
# Crear archivo .env con datos reales
cp .env.example .env
# Editar .env con tus credenciales reales

# Probar container localmente
docker run -p 8000:80 --env-file .env lannister-backend:prod
```

### FASE 2: Configuración AWS

#### 2.1 Crear VPC y Subnets (si no tienes)

```bash
# Usando AWS CLI
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=lannister-vpc}]'

# Crear subnet pública
aws ec2 create-subnet --vpc-id vpc-xxxxxxxxx --cidr-block 10.0.1.0/24 --availability-zone sa-east-1a
```

#### 2.2 Crear Security Groups

```bash
# Security Group para Load Balancer
aws ec2 create-security-group --group-name lannister-alb-sg --description "Load Balancer Security Group" --vpc-id vpc-xxxxxxxxx

# Reglas ALB
aws ec2 authorize-security-group-ingress --group-id sg-xxxxxxxxx --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id sg-xxxxxxxxx --protocol tcp --port 443 --cidr 0.0.0.0/0

# Security Group para EC2
aws ec2 create-security-group --group-name lannister-web-sg --description "Web Server Security Group" --vpc-id vpc-xxxxxxxxx

# Reglas EC2 (HTTP desde ALB, SSH desde tu IP)
aws ec2 authorize-security-group-ingress --group-id sg-yyyyyyyyy --protocol tcp --port 80 --source-group sg-xxxxxxxxx
aws ec2 authorize-security-group-ingress --group-id sg-yyyyyyyyy --protocol tcp --port 22 --cidr TU_IP/32
```

#### 2.3 Crear ElastiCache Redis

```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id lannister-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1 \
  --security-group-ids sg-redis-id
```

### FASE 3: Lanzar EC2 Instance

#### 3.1 Crear EC2 Instance

```bash
# Buscar AMI Ubuntu más reciente
aws ec2 describe-images --owners 099720109477 --filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" --query 'Images[*].[ImageId,CreationDate]' --output table

# Lanzar instancia
aws ec2 run-instances \
  --image-id ami-xxxxxxxxx \
  --count 1 \
  --instance-type t3.medium \
  --key-name tu-key-pair \
  --security-group-ids sg-yyyyyyyyy \
  --subnet-id subnet-xxxxxxxxx \
  --associate-public-ip-address \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=lannister-backend}]'
```

#### 3.2 Configurar EC2 (conectar por SSH)

```bash
# Conectar a la instancia
ssh -i ~/.ssh/tu-key.pem ubuntu@tu-ip-publica

# Instalar Docker
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker ubuntu
sudo systemctl start docker
sudo systemctl enable docker

# Instalar AWS CLI
sudo apt install -y awscli

# Logout y volver a conectar para que tome efecto el grupo docker
exit
ssh -i ~/.ssh/tu-key.pem ubuntu@tu-ip-publica
```

### FASE 4: Desplegar Aplicación

#### 4.1 Subir código a EC2

```bash
# Opción 1: Clonar desde GitHub (recomendado)
git clone https://github.com/HouseLannisterDev/lannister-backend.git
cd lannister-backend

# Opción 2: Transferir imagen Docker
# Desde tu máquina local:
docker save lannister-backend:prod | gzip > lannister-backend.tar.gz
scp -i ~/.ssh/tu-key.pem lannister-backend.tar.gz ubuntu@tu-ip-publica:/home/ubuntu/
# En EC2:
docker load < lannister-backend.tar.gz
```

#### 4.2 Configurar variables de entorno

```bash
# En EC2, crear archivo .env
nano .env

# Copiar contenido del .env.example y completar con datos reales:
# DJANGO_SECRET_KEY=tu_secreto_generado
# MYSQL_HOST=database-1.cpcimk2ikn91.sa-east-1.rds.amazonaws.com
# MYSQL_PASSWORD=tu_password_real
# MONGO_URI=mongodb+srv://...
# REDIS_URL=redis://tu-redis-endpoint:6379/1
# etc.
```

#### 4.3 Ejecutar aplicación

```bash
# Si construiste localmente y transferiste:
docker run -d --name lannister-app -p 80:80 --env-file .env lannister-backend:prod

# Si clonaste el repo:
docker build -f Dockerfile.prod -t lannister-backend:prod .
docker run -d --name lannister-app -p 80:80 --env-file .env lannister-backend:prod

# Verificar que está corriendo
docker ps
docker logs lannister-app
```

### FASE 5: Configurar Load Balancer (Opcional pero recomendado)

#### 5.1 Crear Application Load Balancer

```bash
aws elbv2 create-load-balancer \
  --name lannister-alb \
  --subnets subnet-xxxxxxxxx subnet-yyyyyyyyy \
  --security-groups sg-alb-id

# Crear target group
aws elbv2 create-target-group \
  --name lannister-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-xxxxxxxxx \
  --health-check-path /health

# Registrar EC2 instance en target group
aws elbv2 register-targets \
  --target-group-arn arn:aws:elasticloadbalancing:... \
  --targets Id=i-instance-id

# Crear listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

### FASE 6: Configurar dominio (Si aplica)

#### 6.1 Route 53 (si tienes dominio)

```bash
# Crear hosted zone
aws route53 create-hosted-zone --name tu-dominio.com --caller-reference $(date +%s)

# Crear record apuntando al ALB
aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch file://dns-record.json
```

### FASE 7: Verificación y Monitoreo

#### 7.1 Verificar aplicación

```bash
# Probar endpoint de salud
curl http://tu-ip-o-dominio/health

# Probar API
curl http://tu-ip-o-dominio/api/

# Ver logs
docker logs -f lannister-app
```

#### 7.2 Configurar CloudWatch (opcional)

```bash
# Instalar agente CloudWatch
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb
```

---

## 🔧 Comandos de Mantenimiento

### Actualizar aplicación

```bash
# Pull cambios del repo
git pull origin main

# Reconstruir imagen
docker build -f Dockerfile.prod -t lannister-backend:prod .

# Parar container actual
docker stop lannister-app
docker rm lannister-app

# Ejecutar nueva versión
docker run -d --name lannister-app -p 80:80 --env-file .env lannister-backend:prod
```

### Ver logs

```bash
docker logs -f lannister-app
docker exec -it lannister-app /bin/bash  # Acceso al container
```

### Backup de datos

```bash
# Backup automático de RDS se configura en AWS Console
# MongoDB Atlas tiene backup automático
```

---

## 💰 Estimación de Costos Mensuales (São Paulo)

- **EC2 t3.medium**: ~$30-40 USD/mes
- **ALB**: ~$18 USD/mes
- **ElastiCache t3.micro**: ~$12 USD/mes
- **RDS**: Ya lo tienes (costo actual)
- **Tráfico**: ~$5-10 USD/mes (depende del uso)

**Total estimado**: $65-80 USD/mes (sin contar RDS existente)

---

## ❓ Próximos Pasos

**¡DAME ESTOS DATOS Y EMPEZAMOS!**

1. ✅ Credenciales RDS (usuario/password)
2. ✅ URI MongoDB Atlas completa
3. ✅ AWS Access Keys
4. ✅ Confirmación de región (sa-east-1)
5. ✅ Tu IP pública (para SSH)

**¿Qué prefieres hacer primero?**

- A) Configurar todo paso a paso juntos
- B) Te envío los archivos y scripts completos
- C) Probar primero localmente con Docker

¡Dime qué datos tienes listos y continuamos! 🚀
