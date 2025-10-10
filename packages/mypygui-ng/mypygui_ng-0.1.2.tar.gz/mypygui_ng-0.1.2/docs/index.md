# MyPyGUI-NG

**🐍✨ GUIs modernas en Python con HTML+CSS estándar**

**🚀 Ligero como Tkinter, moderno como la web, 10× más liviano que Electron**

MyPyGUI-NG trae las tecnologías web modernas a las aplicaciones de escritorio Python. Crea interfaces de usuario hermosas y responsivas usando HTML y CSS familiares, renderizados nativamente en Python sin dependencia de navegadores web.

## 🔥 Características Principales

- **🎯 Flexbox Layout** - Diseños responsivos modernos con `display: flex`
- **📐 Unidades Relativas** - Soporte completo para `em`, `rem`, `vh`, `vw`
- **🎨 Efectos Visuales** - `opacity`, transiciones hover, animaciones suaves
- **✍️ Tipografía** - `font` shorthand y estilos de texto avanzados
- **🎨 Sistema de Temas** - Temas Bootstrap-lite y Material-lite pre-construidos
- **⚡ Ligero** - 10-20MB vs 100-200MB de memoria de Electron
- **🔧 Integración Fácil** - Sintaxis HTML/CSS estándar en aplicaciones Python

## 📦 Instalación

```bash
pip install mypygui-ng
```

## 🚀 Inicio Rápido

```python
from mypygui_ng import BrowserWindow, URI

# Crear ventana
window = BrowserWindow()

# Cargar contenido HTML moderno
html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            margin: 0; padding: 2em;
        }
        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 50vh;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 2em;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 ¡Hola MyPyGUI-NG!</h1>
    </div>
</body>
</html>
"""

# Cargar y mostrar
uri = URI.from_string("data:text/html," + html_content)
window.load_page(uri)
window.show()
```

## 🎭 ¿Por Qué MyPyGUI-NG?

| Característica | Electron | PyQt/PySide | Tkinter | MyPyGUI-NG |
|---|---|---|---|---|
| **Memoria** | 150MB | 50-80MB | 5-10MB | **10-20MB** |
| **CSS moderno** | ✅ Completo | ❌ Limitado | ❌ Básico | ✅ **Funcional** |
| **Lenguaje** | JavaScript | C++ bindings | Python | **Python nativo** |
| **Curva aprendizaje** | Media | Alta | Baja | **Muy baja** |

## 🎨 Ejemplos Destacados

### Layout Moderno con Flexbox
```css
.modern-layout {
    display: flex;           /* ✨ Layout moderno */
    justify-content: center; /* ✨ Alineación perfecta */
    align-items: center;     /* ✨ Centrado vertical */
    gap: 2vw;                /* ✨ Espaciado relativo */
}
```

### Diseño Responsivo
```css
.responsive-card {
    width: 30vw;      /* ✨ Se adapta a la ventana */
    padding: 1em;     /* ✨ Escalable */
    font-size: 1.2rem; /* ✨ Relativo al contenedor */
}
```

### Sistema de Temas
```python
from mypygui_ng.themes import get_theme_css

# Aplicar temas profesionales
bootstrap_css = get_theme_css('bootstrap-lite')
material_css = get_theme_css('material-lite')
```

## 🔮 Próximas Características

- **🎨 SVG Support** - Íconos vectoriales nativos
- **📦 Box Shadows** - Sombras de caja y texto
- **🌈 Gradientes** - Gradientes lineales y radiales
- **🎬 Animaciones** - Transiciones y transformaciones
- **🔤 @font-face** - Carga de fuentes personalizadas

## 🤝 Únete a la Comunidad

MyPyGUI-NG es un proyecto open-source. ¡Tu contribución es bienvenida!

- **[GitHub Repository](https://github.com/Dragon-KK/mypygui)** - Código fuente y issues
- **[Discusiones](https://github.com/Dragon-KK/mypygui/discussions)** - Ideas y preguntas
- **[Issues](https://github.com/Dragon-KK/mypygui/issues)** - Reportar bugs o solicitar características

---

*"MyPyGUI-NG: Porque las aplicaciones Python modernas merecen GUIs modernas."* 🚀
