#!/bin/bash

# 🎨 Setup Script - Diagram Tools Installation
# Instala herramientas para generar diagramas de arquitectura

set -e

echo "🎨 Lannister Backend - Diagram Tools Setup"
echo "==========================================="
echo ""

# Detectar OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "📍 Sistema detectado: ${MACHINE}"
echo ""

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Instalar D2 Lang (RECOMENDADO)
echo "🔹 1/3 Instalando D2 Lang..."
if command_exists d2; then
    echo "   ✅ D2 ya está instalado: $(d2 --version)"
else
    if [ "${MACHINE}" == "Mac" ]; then
        if command_exists brew; then
            brew install d2
            echo "   ✅ D2 instalado con Homebrew"
        else
            echo "   ⚠️  Homebrew no encontrado. Instalar manualmente:"
            echo "      curl -fsSL https://d2lang.com/install.sh | sh"
        fi
    elif [ "${MACHINE}" == "Linux" ]; then
        curl -fsSL https://d2lang.com/install.sh | sh
        echo "   ✅ D2 instalado"
    else
        echo "   ⚠️  OS no soportado automáticamente"
        echo "      Descargar de: https://github.com/terrastruct/d2/releases"
    fi
fi
echo ""

# 2. Instalar PlantUML
echo "🔹 2/3 Instalando PlantUML..."
if command_exists plantuml; then
    echo "   ✅ PlantUML ya está instalado"
else
    if [ "${MACHINE}" == "Mac" ]; then
        if command_exists brew; then
            brew install plantuml
            echo "   ✅ PlantUML instalado con Homebrew"
        else
            echo "   ⚠️  Homebrew no encontrado"
        fi
    elif [ "${MACHINE}" == "Linux" ]; then
        if command_exists apt-get; then
            sudo apt-get update
            sudo apt-get install -y plantuml
            echo "   ✅ PlantUML instalado con apt"
        else
            echo "   ⚠️  Usar package manager de tu distro"
        fi
    fi
fi
echo ""

# 3. Instalar Docker (para Structurizr Lite)
echo "🔹 3/3 Verificando Docker..."
if command_exists docker; then
    echo "   ✅ Docker ya está instalado: $(docker --version)"
else
    echo "   ⚠️  Docker no encontrado"
    echo "      Instalar desde: https://docs.docker.com/get-docker/"
fi
echo ""

# 4. Instalar VS Code Extensions (opcional)
echo "📦 Extensiones de VS Code (opcional):"
if command_exists code; then
    echo "   Instalando extensiones..."
    code --install-extension jebbs.plantuml 2>/dev/null && echo "   ✅ PlantUML extension" || echo "   ⚠️  PlantUML extension (ya instalada o error)"
    code --install-extension terrastruct.d2 2>/dev/null && echo "   ✅ D2 extension" || echo "   ⚠️  D2 extension (ya instalada o error)"
else
    echo "   ℹ️  VS Code no encontrado. Extensiones disponibles en:"
    echo "      - PlantUML: jebbs.plantuml"
    echo "      - D2: terrastruct.d2"
fi
echo ""

# Resumen
echo "✅ Setup completado!"
echo ""
echo "🚀 Quick Start:"
echo "   # Generar diagrama con D2 (recomendado)"
echo "   cd docs/architecture/exportable"
echo "   d2 lannister_components.d2 output.svg"
echo ""
echo "   # Generar diagrama con PlantUML"
echo "   plantuml lannister_components.puml"
echo ""
echo "   # Ejecutar Structurizr Lite"
echo "   docker run -it --rm -p 8080:8080 -v \$(pwd):/usr/local/structurizr structurizr/lite"
echo ""
echo "📚 Documentación completa: docs/architecture/exportable/README.md"
