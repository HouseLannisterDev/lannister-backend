# 🚀 Guía de Despliegue AWS - Lannister Backend

## 📋 Requisitos Previos

Antes de comenzar, necesitas:

1. **AWS CLI configurado** con credenciales que tengan permisos para:

   - EC2 (crear instancias, security groups, key pairs)
   - RDS (crear instancias, security groups, subnet groups)
   - VPC (acceso a subnets por defecto)

2. **Git** para clonar el repositorio

3. **Acceso a MongoDB** (Atlas recomendado)

## 🚀 Despliegue Automático (Opción Recomendada)

### Paso 1: Preparar scripts

```bash
# Dale permisos de ejecución a todos los scripts
chmod +x aws-deployment-scripts/*.sh
```

### Paso 2: Ejecutar despliegue completo

```bash
# Ejecutar script maestro que hace todo automáticamente
cd aws-deployment-scripts
./00-deploy-all.sh
```

Este script ejecutará automáticamente:

1. ✅ Creación de instancia EC2 con Docker
2. ✅ Creación de RDS MySQL (opcional)
3. ✅ Configuración del backend con Docker
4. ✅ Configuración de Nginx como proxy reverso
5. ✅ Ejecución de migraciones de Django

### Paso 3: Configurar HTTPS (Opcional)

```bash
# Si tienes un dominio personalizado
./04-setup-ssl.sh <IP_PUBLICA> <CLAVE_PRIVADA> <TU_DOMINIO>
```

## 🔧 Despliegue Manual (Paso a Paso)

Si prefieres ejecutar cada paso manualmente:

### 1. Crear instancia EC2

```bash
./01-create-ec2-instance.sh
```

- Crea instancia EC2 t3.medium en sa-east-1
- Instala Docker, Docker Compose, Git
- Configura security groups
- Genera par de claves SSH

### 2. Crear RDS MySQL (si no tienes uno)

```bash
./02-create-rds-mysql.sh
```

- Crea instancia RDS MySQL t3.micro
- Configura security groups para acceso desde EC2
- Genera credenciales seguras

### 3. Desplegar backend

```bash
./03-deploy-backend.sh <IP_PUBLICA> <ARCHIVO_CLAVE>
```

- Clona el repositorio
- Configura variables de entorno
- Construye y ejecuta contenedores Docker
- Ejecuta migraciones de Django

### 4. Configurar SSL (opcional)

```bash
./04-setup-ssl.sh <IP_PUBLICA> <ARCHIVO_CLAVE> <DOMINIO>
```

## 🔧 Configuración Manual

### Variables de Entorno Importantes

Edita el archivo `.env` en el servidor:

```bash
ssh -i lannister-backend-key.pem ubuntu@<IP_PUBLICA>
cd /home/lannister/app
nano .env
```

Variables críticas:

```env
# Django
DJANGO_SECRET_KEY=your-super-secret-production-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=tu-ip-publica,tu-dominio.com

# MySQL (RDS)
MYSQL_HOST=tu-rds-endpoint.amazonaws.com
MYSQL_PORT=3306
MYSQL_DB=lannister_news
MYSQL_USER=admin
MYSQL_PASSWORD=tu-password-seguro

# MongoDB Atlas
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/lannister_news

# Redis
REDIS_URL=redis://127.0.0.1:6379/1
```

### Comandos Útiles Post-Despliegue

```bash
# Conectar por SSH
ssh -i lannister-backend-key.pem ubuntu@<IP_PUBLICA>

# Ver logs de la aplicación
docker-compose -f docker-compose.prod.yml logs -f app

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml restart

# Acceder al contenedor de Django
docker-compose -f docker-compose.prod.yml exec app bash

# Crear superusuario de Django
docker-compose -f docker-compose.prod.yml exec app python manage.py createsuperuser

# Ejecutar migraciones
docker-compose -f docker-compose.prod.yml exec app python manage.py migrate

# Colectar archivos estáticos
docker-compose -f docker-compose.prod.yml exec app python manage.py collectstatic --noinput
```

## 🏗️ Arquitectura del Despliegue

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Internet      │───▶│   Load Balancer   │───▶│   EC2 Instance  │
│   (Port 80/443) │    │   (Nginx)        │    │   (Django App)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌─────────────────┐              │
                       │   RDS MySQL     │◀─────────────┤
                       │   (Database)    │              │
                       └─────────────────┘              │
                                                         │
                       ┌─────────────────┐              │
                       │  MongoDB Atlas  │◀─────────────┤
                       │  (NoSQL Data)   │              │
                       └─────────────────┘              │
                                                         │
                       ┌─────────────────┐              │
                       │   Redis Cache   │◀─────────────┘
                       │   (Sessions)    │
                       └─────────────────┘
```

## 📊 Monitoreo y Mantenimiento

### Verificar Estado de Servicios

```bash
# Estado de contenedores
docker-compose -f docker-compose.prod.yml ps

# Uso de recursos
docker stats

# Espacio en disco
df -h

# Memoria y CPU
htop
```

### Backup de Base de Datos

```bash
# Backup manual de MySQL
docker-compose -f docker-compose.prod.yml exec app python manage.py dbbackup

# Configurar backup automático en RDS
aws rds modify-db-instance \
    --db-instance-identifier lannister-mysql-db \
    --backup-retention-period 7 \
    --preferred-backup-window "03:00-04:00"
```

### Actualizar Aplicación

```bash
# 1. Conectar al servidor
ssh -i lannister-backend-key.pem ubuntu@<IP_PUBLICA>

# 2. Ir al directorio de la app
cd /home/lannister/app

# 3. Obtener últimos cambios
git pull origin main

# 4. Reconstruir y reiniciar
docker-compose -f docker-compose.prod.yml up -d --build

# 5. Ejecutar migraciones si es necesario
docker-compose -f docker-compose.prod.yml exec app python manage.py migrate
```

## 🔒 Seguridad

### Configuraciones de Seguridad Implementadas

1. **Firewall (Security Groups)**:

   - Solo puertos necesarios abiertos (22, 80, 443, 8000)
   - RDS solo accesible desde EC2

2. **SSL/TLS**:

   - Certificados Let's Encrypt gratuitos
   - Renovación automática configurada

3. **Docker**:

   - Usuario no-root en contenedores
   - Volúmenes para persistencia de datos

4. **Django**:
   - DEBUG=False en producción
   - SECRET_KEY segura
   - ALLOWED_HOSTS configurado

### Recomendaciones Adicionales

1. **Configurar fail2ban** para protección SSH
2. **Actualizar regularmente** el sistema operativo
3. **Monitorear logs** de aplicación y sistema
4. **Configurar alertas** de CloudWatch
5. **Implementar WAF** si es necesario

## 🆘 Solución de Problemas

### Problemas Comunes

1. **Aplicación no responde**:

   ```bash
   # Verificar logs
   docker-compose -f docker-compose.prod.yml logs app

   # Reiniciar servicios
   docker-compose -f docker-compose.prod.yml restart
   ```

2. **Error de base de datos**:

   ```bash
   # Verificar conexión a RDS
   docker-compose -f docker-compose.prod.yml exec app python manage.py dbshell

   # Verificar configuración
   docker-compose -f docker-compose.prod.yml exec app python manage.py check --deploy
   ```

3. **Error de SSL**:

   ```bash
   # Verificar certificado
   sudo certbot certificates

   # Renovar manualmente
   sudo certbot renew
   ```

4. **Espacio en disco**:

   ```bash
   # Limpiar contenedores no usados
   docker system prune -a

   # Limpiar logs
   sudo journalctl --vacuum-time=7d
   ```

## 📞 Soporte

Si tienes problemas durante el despliegue:

1. Revisa los logs en `deployment-logs/`
2. Verifica las credenciales de AWS
3. Asegúrate de que los puertos estén abiertos
4. Confirma que MongoDB Atlas esté accesible

Para obtener ayuda específica, proporciona:

- Logs de error completos
- Configuración de variables de entorno (sin contraseñas)
- Descripción detallada del problema

¡Tu backend Lannister estará funcionando en AWS en pocos minutos! 🚀
