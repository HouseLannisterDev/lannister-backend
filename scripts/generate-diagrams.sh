#!/bin/bash

# 🎨 Generate Diagrams - Auto-generation script
# Genera todos los diagramas en diferentes formatos

set -e

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎨 Lannister Backend - Diagram Generator${NC}"
echo "==========================================="
echo ""

# Directorio base
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EXPORTABLE_DIR="$PROJECT_ROOT/docs/architecture/exportable"
OUTPUT_DIR="$PROJECT_ROOT/docs/architecture/generated"

# Crear directorio de salida
mkdir -p "$OUTPUT_DIR"

cd "$EXPORTABLE_DIR"

# Función para verificar si un comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Contador de éxitos
SUCCESS_COUNT=0
FAIL_COUNT=0

# 1. Generar con D2 Lang
echo -e "${YELLOW}🔹 Generando con D2 Lang...${NC}"
if command_exists d2; then
    # SVG (mejor calidad)
    if d2 lannister_components.d2 "$OUTPUT_DIR/lannister_components_d2.svg" 2>/dev/null; then
        echo -e "   ${GREEN}✅ SVG generado: generated/lannister_components_d2.svg${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "   ${RED}❌ Error generando SVG${NC}"
        ((FAIL_COUNT++))
    fi
    
    # PNG
    if d2 lannister_components.d2 "$OUTPUT_DIR/lannister_components_d2.png" 2>/dev/null; then
        echo -e "   ${GREEN}✅ PNG generado: generated/lannister_components_d2.png${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "   ${RED}❌ Error generando PNG${NC}"
        ((FAIL_COUNT++))
    fi
else
    echo -e "   ${YELLOW}⚠️  D2 no instalado. Instalar con: brew install d2${NC}"
    ((FAIL_COUNT+=2))
fi
echo ""

# 2. Generar con PlantUML
echo -e "${YELLOW}🔹 Generando con PlantUML...${NC}"
if command_exists plantuml; then
    # PNG
    if plantuml -tpng lannister_components.puml -o "$OUTPUT_DIR" 2>/dev/null; then
        echo -e "   ${GREEN}✅ PNG generado: generated/lannister_components.png${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "   ${RED}❌ Error generando PNG${NC}"
        ((FAIL_COUNT++))
    fi
    
    # SVG
    if plantuml -tsvg lannister_components.puml -o "$OUTPUT_DIR" 2>/dev/null; then
        echo -e "   ${GREEN}✅ SVG generado: generated/lannister_components.svg${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "   ${RED}❌ Error generando SVG${NC}"
        ((FAIL_COUNT++))
    fi
else
    echo -e "   ${YELLOW}⚠️  PlantUML no instalado. Instalar con: brew install plantuml${NC}"
    ((FAIL_COUNT+=2))
fi
echo ""

# 3. Información sobre Structurizr
echo -e "${YELLOW}🔹 Structurizr DSL${NC}"
echo -e "   ℹ️  Para usar Structurizr DSL:"
echo -e "      ${BLUE}docker run -it --rm -p 8080:8080 -v \$(pwd):/usr/local/structurizr structurizr/lite${NC}"
echo -e "   Luego abrir: ${BLUE}http://localhost:8080${NC}"
echo ""

# 4. Resumen
echo "==========================================="
echo -e "${GREEN}✅ Generaciones exitosas: $SUCCESS_COUNT${NC}"
if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "${RED}❌ Generaciones fallidas: $FAIL_COUNT${NC}"
fi
echo ""

if [ $SUCCESS_COUNT -gt 0 ]; then
    echo -e "${GREEN}🎉 Diagramas generados en: docs/architecture/generated/${NC}"
    echo ""
    echo "📁 Archivos generados:"
    ls -lh "$OUTPUT_DIR" 2>/dev/null | grep -E '\.(png|svg)$' | awk '{print "   - " $9 " (" $5 ")"}'
else
    echo -e "${RED}⚠️  No se generaron diagramas. Instalar herramientas primero:${NC}"
    echo -e "   ${BLUE}./scripts/setup-diagram-tools.sh${NC}"
fi

echo ""
echo "📚 Ver documentación: docs/architecture/exportable/README.md"
