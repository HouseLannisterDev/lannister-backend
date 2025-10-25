# Scripts - Lannister Backend

Esta carpeta contiene scripts de utilidad para desarrollo, deployment y testing.

## 📄 Scripts Disponibles

### Deployment
- **deploy-aws.sh** - Script principal para deployment en AWS
- **start-local.sh** - Iniciar servidor de desarrollo local

### Development Tools
- **chatbot_standalone_server.py** - Servidor standalone del chatbot para testing
- **debug_settings.py** - Script para debuggear configuración de Django
- **mongo_client.py** - Cliente de utilidad para MongoDB

## 🚀 Uso

### Iniciar servidor local:
```bash
./scripts/start-local.sh
```

### Deploy a AWS:
```bash
./scripts/deploy-aws.sh
```

### Servidor standalone del chatbot:
```bash
python scripts/chatbot_standalone_server.py
```

### Debug de configuración:
```bash
python scripts/debug_settings.py
```

## ⚠️ Permisos

Asegúrate de dar permisos de ejecución a los scripts shell:
```bash
chmod +x scripts/*.sh
```
