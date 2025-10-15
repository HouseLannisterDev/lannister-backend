#!/bin/bash

# Script para limpiar espacio en disco en el servidor EC2
# Ejecutar cuando se necesite liberar espacio

if [ $# -ne 2 ]; then
    echo "Uso: $0 <IP_PUBLICA_EC2> <ARCHIVO_CLAVE_PRIVADA>"
    echo "Ejemplo: $0 54.123.45.67 lannister-backend-key.pem"
    exit 1
fi

PUBLIC_IP=$1
KEY_FILE=$2

echo "🧹 Limpiando espacio en disco del servidor EC2..."
echo "   - IP: $PUBLIC_IP"

# Función para ejecutar comandos remotos
run_remote() {
    ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP "$@"
}

# 1. Mostrar uso actual de disco
echo "📊 Uso actual de disco:"
run_remote "df -h"

echo ""
echo "🧹 Iniciando limpieza..."

# 2. Limpiar contenedores Docker no utilizados
echo "🐳 Limpiando contenedores Docker no utilizados..."
run_remote "docker system prune -af --volumes"

# 3. Limpiar caché de apt
echo "📦 Limpiando caché de paquetes..."
run_remote "sudo apt-get clean && sudo apt-get autoremove -y"

# 4. Limpiar logs del sistema
echo "📄 Limpiando logs del sistema..."
run_remote "sudo journalctl --vacuum-time=7d"

# 5. Limpiar archivos temporales
echo "🗑️ Limpiando archivos temporales..."
run_remote "sudo rm -rf /tmp/* /var/tmp/*"

# 6. Limpiar logs de Docker si existen
echo "🐳 Limpiando logs de Docker..."
run_remote "sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log"

# 7. Limpiar caché de pip si existe
echo "🐍 Limpiando caché de pip..."
run_remote "rm -rf ~/.cache/pip/*"

# 8. Verificar directorios que ocupan más espacio
echo "📊 Directorios que más espacio ocupan:"
run_remote "sudo du -sh /* 2>/dev/null | sort -hr | head -10"

echo ""
echo "📊 Uso de disco después de la limpieza:"
run_remote "df -h"

echo ""
echo "✅ Limpieza completada!"
echo ""
echo "💡 Consejos adicionales para optimizar espacio:"
echo "   1. Configurar rotación automática de logs Docker"
echo "   2. Usar volúmenes externos para datos grandes"
echo "   3. Implementar backup y limpieza automática"
echo ""
echo "🔧 Para configurar rotación de logs Docker automática:"
echo "   ssh -i $KEY_FILE ubuntu@$PUBLIC_IP"
echo "   sudo nano /etc/docker/daemon.json"
echo "   Agregar:"
echo '   {'
echo '     "log-driver": "json-file",'
echo '     "log-opts": {'
echo '       "max-size": "10m",'
echo '       "max-file": "3"'
echo '     }'
echo '   }'