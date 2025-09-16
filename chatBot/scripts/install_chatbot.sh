#!/bin/bash

# 🤖 Script de Instalación Automática del ChatBot con IA
# Para sistema macOS/Linux

set -e  # Salir si hay algún error

echo "🚀 Iniciando instalación del ChatBot con IA..."
echo "================================================"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar Python
log_info "Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_success "Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version | cut -d' ' -f2)
    log_success "Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD="python"
else
    log_error "Python no encontrado. Instala Python 3.8+ primero."
    exit 1
fi

# Verificar versión mínima de Python
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    log_error "Se requiere Python 3.8+. Versión encontrada: $PYTHON_VERSION"
    exit 1
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    log_info "Creando entorno virtual..."
    $PYTHON_CMD -m venv venv
    log_success "Entorno virtual creado"
else
    log_warning "Entorno virtual ya existe"
fi

# Activar entorno virtual
log_info "Activando entorno virtual..."
source venv/bin/activate
log_success "Entorno virtual activado"

# Actualizar pip
log_info "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias base
log_info "Instalando dependencias base de Django..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    log_success "Dependencias base instaladas"
else
    log_warning "requirements.txt no encontrado, instalando dependencias básicas..."
    pip install django djangorestframework django-cors-headers pymongo requests beautifulsoup4
fi

# Instalar dependencias de Machine Learning
log_info "Instalando dependencias de Machine Learning..."
pip install tensorflow keras numpy scikit-learn nltk textblob pandas matplotlib
log_success "Dependencias de ML instaladas"

# Descargar datos de NLTK
log_info "Descargando datos de NLTK..."
$PYTHON_CMD -c "
import nltk
import ssl
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('wordnet', quiet=True)
print('Datos de NLTK descargados')
"
log_success "Datos de NLTK descargados"

# Verificar estructura de archivos
log_info "Verificando estructura del proyecto..."

required_files=(
    "manage.py"
    "chatBot/models.py"
    "chatBot/neural_network.py"
    "chatBot/data_preprocessor.py"
    "chatBot/views.py"
    "chatBot/management/commands/train_chatbot.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    log_success "Todos los archivos necesarios están presentes"
else
    log_error "Archivos faltantes:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    exit 1
fi

# Verificar MongoDB
log_info "Verificando conexión a MongoDB..."
$PYTHON_CMD -c "
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lannister_news_api.settings')
django.setup()

try:
    from mongo_client import get_mongo_client
    db = get_mongo_client()
    count = db.news.count_documents({})
    print(f'✅ MongoDB conectado. Noticias disponibles: {count}')
    if count == 0:
        print('⚠️  No hay noticias en la base de datos.')
        print('   Ejecuta el scraper primero para obtener datos.')
    sys.exit(0)
except Exception as e:
    print(f'❌ Error conectando a MongoDB: {e}')
    print('   Verifica la configuración en settings.py')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    log_success "MongoDB verificado"
else
    log_error "Error con MongoDB. Verifica la configuración."
fi

# Crear migraciones
log_info "Aplicando migraciones de Django..."
$PYTHON_CMD manage.py makemigrations chatBot 2>/dev/null || true
$PYTHON_CMD manage.py migrate
log_success "Migraciones aplicadas"

# Crear archivo de configuración de ejemplo
log_info "Creando archivo de configuración de ejemplo..."
cat > .env.example << 'EOF'
# Configuración del ChatBot con IA

# Django
DJANGO_SECRET_KEY=tu-clave-secreta-super-segura
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# MySQL (para Django)
MYSQL_DB=lannister_news
MYSQL_USER=tu_usuario
MYSQL_PASSWORD=tu_password
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306

# MongoDB (para noticias)
MONGO_NAME=lannister_news
MONGO_HOST=localhost
MONGO_PORT=27017
# Si usas MongoDB Atlas:
# MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/dbname

# Configuración del Scraper
NEWS_SOURCES=cnn.com,bbc.com,elpais.com
NEWS_REQ_DELAY_MIN=3
NEWS_REQ_DELAY_MAX=8
NEWS_MAX_RETRIES=3
EOF
log_success "Archivo .env.example creado"

# Crear script de inicio rápido
log_info "Creando script de inicio rápido..."
cat > start_chatbot.sh << 'EOF'
#!/bin/bash

# Script de inicio rápido del ChatBot
echo "🤖 Iniciando ChatBot con IA..."

# Activar entorno virtual
source venv/bin/activate

# Verificar modelo entrenado
if [ ! -f "chatbot_model.h5" ]; then
    echo "⚠️  Modelo no encontrado. Iniciando entrenamiento..."
    python manage.py train_chatbot --news_limit 1000 --epochs 50
else
    echo "✅ Modelo encontrado"
fi

# Iniciar servidor
echo "🚀 Iniciando servidor en http://localhost:8000"
python manage.py runserver 8000
EOF

chmod +x start_chatbot.sh
log_success "Script de inicio creado: ./start_chatbot.sh"

# Crear script de entrenamiento
log_info "Creando script de entrenamiento..."
cat > train_chatbot.sh << 'EOF'
#!/bin/bash

# Script de entrenamiento del ChatBot
echo "🧠 Entrenando ChatBot con IA..."

# Activar entorno virtual
source venv/bin/activate

# Parámetros por defecto
NEWS_LIMIT=${1:-2000}
EPOCHS=${2:-200}
BATCH_SIZE=${3:-8}

echo "📊 Parámetros de entrenamiento:"
echo "   - Noticias: $NEWS_LIMIT"
echo "   - Épocas: $EPOCHS"
echo "   - Batch size: $BATCH_SIZE"

# Ejecutar entrenamiento
python manage.py train_chatbot \
    --news_limit $NEWS_LIMIT \
    --epochs $EPOCHS \
    --batch_size $BATCH_SIZE

echo "✅ Entrenamiento completado"
echo "💡 Usa ./start_chatbot.sh para iniciar el servidor"
EOF

chmod +x train_chatbot.sh
log_success "Script de entrenamiento creado: ./train_chatbot.sh"

# Crear script de prueba
log_info "Creando script de prueba..."
cat > test_chatbot.sh << 'EOF'
#!/bin/bash

# Script de prueba del ChatBot
echo "🧪 Probando ChatBot..."

# Activar entorno virtual
source venv/bin/activate

# Verificar estado
echo "1. Verificando archivos del modelo..."
if [ -f "chatbot_model.h5" ] && [ -f "words.pkl" ] && [ -f "classes.pkl" ]; then
    echo "   ✅ Archivos del modelo encontrados"
else
    echo "   ❌ Archivos del modelo faltantes"
    echo "   💡 Ejecuta ./train_chatbot.sh primero"
    exit 1
fi

# Prueba interactiva
echo "2. Iniciando prueba interactiva..."
echo "   (Escribe 'quit' para salir)"
python test_chatbot.py --interactive
EOF

chmod +x test_chatbot.sh
log_success "Script de prueba creado: ./test_chatbot.sh"

# Resumen final
echo ""
echo "🎉 ¡Instalación completada exitosamente!"
echo "================================================"
log_success "ChatBot con IA configurado correctamente"
echo ""
echo "📝 Próximos pasos:"
echo ""
echo "1. 📊 Entrenar el modelo:"
echo "   ./train_chatbot.sh"
echo ""
echo "2. 🚀 Iniciar el chatbot:"
echo "   ./start_chatbot.sh"
echo ""
echo "3. 🧪 Probar interactivamente:"
echo "   ./test_chatbot.sh"
echo ""
echo "4. 🌐 API REST disponible en:"
echo "   http://localhost:8000/api/chatbot/"
echo ""
echo "📖 Documentación completa:"
echo "   DOCUMENTACION_CHATBOT.md"
echo ""
log_info "¡Tu ChatBot con IA está listo para entrenar!"
