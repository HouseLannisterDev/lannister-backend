# 🎨 README - Exportable Formats

Esta carpeta contiene el diagrama de componentes de **Lannister Backend** en múltiples formatos para usar en diferentes herramientas.

---

## 📁 Archivos Disponibles

| Archivo | Formato | Herramienta | Uso |
|---------|---------|-------------|-----|
| `lannister_components.puml` | PlantUML | [PlantUML](https://plantuml.com/) | Diagrama text-based, Git-friendly |
| `lannister_components.d2` | D2 Lang | [D2](https://d2lang.com/) | Diagramas modernos y hermosos |
| `lannister_components.dsl` | Structurizr DSL | [Structurizr](https://structurizr.com/) | C4 Model architecture |

---

## 🚀 Quick Start

### 1. PlantUML (.puml)

**Online (más fácil):**
```bash
# Ir a http://www.plantuml.com/plantuml/
# Copiar y pegar el contenido de lannister_components.puml
```

**Local:**
```bash
# Instalar PlantUML
brew install plantuml

# Generar imagen
plantuml lannister_components.puml
# Genera: lannister_components.png
```

**VS Code:**
```bash
# Instalar extensión PlantUML
code --install-extension jebbs.plantuml

# Abrir .puml y presionar Alt+D para preview
```

---

### 2. D2 Lang (.d2) - **RECOMENDADO** ⭐

**Instalación:**
```bash
# macOS
brew install d2

# Linux
curl -fsSL https://d2lang.com/install.sh | sh

# Windows
# Descargar de https://github.com/terrastruct/d2/releases
```

**Generar diagrama:**
```bash
# SVG (mejor calidad)
d2 lannister_components.d2 output.svg

# PNG
d2 lannister_components.d2 output.png

# Live preview con auto-reload
d2 --watch lannister_components.d2
```

**Resultado:** Diagrama hermoso y profesional 🎨

---

### 3. Structurizr DSL (.dsl)

**Opción 1: Structurizr Lite (Docker)**
```bash
# Crear carpeta para workspace
mkdir structurizr-workspace
cp lannister_components.dsl structurizr-workspace/workspace.dsl

# Ejecutar Structurizr Lite
docker run -it --rm -p 8080:8080 \
  -v $(pwd)/structurizr-workspace:/usr/local/structurizr \
  structurizr/lite

# Abrir navegador
open http://localhost:8080
```

**Opción 2: Structurizr Cloud**
1. Ir a https://structurizr.com/
2. Crear cuenta gratis
3. Crear workspace
4. Pegar contenido de `lannister_components.dsl`

---

## 🎯 ¿Cuál Usar?

### Para Documentación en Git: **PlantUML**
- ✅ Text-based (Git diff funciona)
- ✅ Versionable
- ✅ Ampliamente soportado

### Para Presentaciones: **D2 Lang** ⭐
- ✅ Diagramas hermosos y modernos
- ✅ Exporta SVG/PNG de alta calidad
- ✅ Sintaxis clara y legible

### Para Arquitectura C4: **Structurizr DSL**
- ✅ Estándar de arquitectura
- ✅ Múltiples niveles (System → Container → Component)
- ✅ Ideal para documentación formal

---

## 📊 Comparación Rápida

```
PlantUML:  ████████░░ 8/10 (maduro, amplio soporte)
D2 Lang:   ██████████ 10/10 (moderno, hermoso, fácil)
C4/DSL:    ████████░░ 8/10 (estándar, completo, pero complejo)
```

---

## 🎨 Ejemplos de Salida

### D2 Lang Output:
```bash
d2 lannister_components.d2 diagram.svg
# Genera SVG con:
# - Colores personalizados
# - Formas (cilindros para DBs, nubes para externos)
# - Notas y anotaciones
# - Layout automático optimizado
```

### PlantUML Output:
```bash
plantuml lannister_components.puml
# Genera PNG con:
# - Diagrama UML estándar
# - Paquetes agrupados
# - Relaciones claras
# - Notas informativas
```

---

## 🛠️ Personalización

### Cambiar colores en D2:
```d2
myComponent: {
  style.fill: "#ff6b6b"     # Color de fondo
  style.stroke: "#c92a2a"   # Color de borde
  style.font-color: "#fff"  # Color de texto
}
```

### Cambiar colores en PlantUML:
```plantuml
skinparam component {
    BackgroundColor LightBlue
    BorderColor DarkBlue
}
```

---

## 📚 Recursos Adicionales

### D2 Lang:
- **Documentación:** https://d2lang.com/tour/intro
- **Playground:** https://play.d2lang.com/
- **GitHub:** https://github.com/terrastruct/d2

### PlantUML:
- **Documentación:** https://plantuml.com/component-diagram
- **Online Editor:** http://www.plantuml.com/plantuml/
- **VS Code Extension:** https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml

### Structurizr:
- **C4 Model:** https://c4model.com/
- **DSL Guide:** https://github.com/structurizr/dsl
- **Lite Docker:** https://hub.docker.com/r/structurizr/lite

---

## 🔄 Workflow Recomendado

1. **Editar:** Modifica el archivo `.d2` o `.puml` en tu editor favorito
2. **Preview:** Usa `d2 --watch` o extensión de VS Code
3. **Commit:** Guarda el archivo text-based en Git
4. **Export:** Genera PNG/SVG para presentaciones

```bash
# Ejemplo completo
vim lannister_components.d2
d2 --watch lannister_components.d2  # preview live
git add lannister_components.d2
git commit -m "docs: update component diagram"
d2 lannister_components.d2 presentation.svg  # para slides
```

---

## 🎯 Tips

1. **VS Code Extensions:**
   - PlantUML: `jebbs.plantuml`
   - D2: `terrastruct.d2`

2. **Auto-export en CI/CD:**
   ```yaml
   # .github/workflows/docs.yml
   - name: Generate diagrams
     run: |
       d2 docs/architecture/exportable/*.d2
       plantuml docs/architecture/exportable/*.puml
   ```

3. **Live collaboration:**
   - Usar Structurizr Cloud para equipos
   - Compartir link de diagrama

---

**Creado:** 27 de octubre de 2025  
**Formato favorito:** D2 Lang 🎨  
**Mantenido por:** HouseLannisterDev Team
