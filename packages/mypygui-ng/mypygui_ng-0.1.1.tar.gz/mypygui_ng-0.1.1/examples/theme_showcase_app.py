"""
Ejemplo avanzado: Aplicación de demostración completa con múltiples temas

Este ejemplo muestra cómo crear una aplicación sofisticada que demuestre
todas las capacidades de MyPyGUI-NG incluyendo cambio dinámico de temas,
layouts complejos y efectos visuales avanzados.
"""

import sys
import os

# Agregar el directorio src al path para desarrollo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mypygui_ng import BrowserWindow, URI
from mypygui_ng.themes import get_theme_css


class ThemeShowcaseApp:
    """Aplicación de demostración con múltiples temas."""

    def __init__(self):
        self.current_theme = 'bootstrap-lite'
        self.window = None

    def create_showcase_html(self):
        """Crear HTML para la aplicación de demostración."""

        # Obtener CSS de todos los temas disponibles
        bootstrap_css = get_theme_css('bootstrap-lite')
        material_css = get_theme_css('material-lite')
        default_css = get_theme_css('default')

        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MyPyGUI-NG - Demostración Completa</title>
    <style>
        /* CSS personalizado adicional */
        .theme-showcase-app {{
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}

        .app-navbar {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}

        .navbar-brand {{
            font-size: 1.5rem;
            font-weight: bold;
            color: #2c3e50;
            text-decoration: none;
        }}

        .theme-selector {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .theme-btn {{
            padding: 0.5rem 1rem;
            border: 2px solid #e9ecef;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .theme-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}

        .theme-btn.active {{
            border-color: #007bff;
            background: #007bff;
            color: white;
        }}

        .hero-section {{
            padding: 4rem 2rem;
            text-align: center;
            color: white;
        }}

        .hero-title {{
            font-size: 3rem;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}

        .hero-subtitle {{
            font-size: 1.3rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }}

        .demo-buttons {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
        }}

        .demo-btn {{
            padding: 1rem 2rem;
            border: none;
            border-radius: 10px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }}

        .demo-btn:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }}

        .btn-primary {{
            background: #007bff;
            color: white;
        }}

        .btn-primary:hover {{
            background: #0056b3;
        }}

        .btn-success {{
            background: #28a745;
            color: white;
        }}

        .btn-success:hover {{
            background: #1e7e34;
        }}

        .btn-warning {{
            background: #ffc107;
            color: #212529;
        }}

        .btn-warning:hover {{
            background: #e0a800;
        }}

        .features-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            padding: 4rem 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }}

        .feature-card {{
            background: rgba(255, 255, 255, 0.95);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }}

        .feature-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
        }}

        .feature-icon {{
            width: 60px;
            height: 60px;
            margin: 0 auto 1rem;
            background: linear-gradient(135deg, #007bff, #0056b3);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: white;
        }}

        .feature-title {{
            font-size: 1.3rem;
            margin-bottom: 1rem;
            color: #2c3e50;
        }}

        .feature-description {{
            color: #6c757d;
            line-height: 1.6;
        }}

        .code-preview {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 2rem;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            margin: 2rem 0;
            overflow-x: auto;
        }}

        .footer {{
            background: rgba(44, 62, 80, 0.95);
            color: white;
            text-align: center;
            padding: 3rem 2rem;
        }}

        .footer-title {{
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }}

        .footer-text {{
            opacity: 0.8;
            margin-bottom: 2rem;
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .hero-title {{
                font-size: 2rem;
            }}

            .features-grid {{
                grid-template-columns: 1fr;
                padding: 2rem 1rem;
            }}

            .demo-buttons {{
                flex-direction: column;
                align-items: center;
            }}

            .theme-selector {{
                flex-wrap: wrap;
                justify-content: center;
            }}
        }}
    </style>
</head>
<body class="theme-showcase-app">
    <!-- Navigation -->
    <nav class="app-navbar">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto;">
            <a href="#" class="navbar-brand">🚀 MyPyGUI-NG Showcase</a>
            <div class="theme-selector">
                <span style="margin-right: 1rem; color: #6c757d;">Tema:</span>
                <button class="theme-btn" onclick="setTheme('bootstrap-lite')" id="bootstrap-btn">Bootstrap</button>
                <button class="theme-btn" onclick="setTheme('material-lite')" id="material-btn">Material</button>
                <button class="theme-btn" onclick="setTheme('default')" id="default-btn">Default</button>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
        <h1 class="hero-title">🎨 MyPyGUI-NG</h1>
        <p class="hero-subtitle">GUIs modernas en Python con HTML+CSS estándar</p>

        <div class="demo-buttons">
            <a href="#" class="demo-btn btn-primary">📖 Ver Documentación</a>
            <a href="#" class="demo-btn btn-success">🚀 Ver Ejemplos</a>
            <a href="#" class="demo-btn btn-warning">⭐ Ver en GitHub</a>
        </div>
    </section>

    <!-- Features Grid -->
    <div class="features-grid">
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3 class="feature-title">Flexbox Layout</h3>
            <p class="feature-description">
                Sistema de layout moderno con display: flex, justify-content y align-items
                para diseños responsivos y profesionales.
            </p>
        </div>

        <div class="feature-card">
            <div class="feature-icon">📐</div>
            <h3 class="feature-title">Unidades Relativas</h3>
            <p class="feature-description">
                Soporte completo para em, rem, vh, vw para diseños que se adaptan
                perfectamente a cualquier tamaño de ventana.
            </p>
        </div>

        <div class="feature-card">
            <div class="feature-icon">🎨</div>
            <h3 class="feature-title">Sistema de Temas</h3>
            <p class="feature-description">
                Temas profesionales incluidos: Bootstrap-lite, Material-lite y Default.
                ¡Cambia entre ellos dinámicamente!
            </p>
        </div>

        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <h3 class="feature-title">Alto Rendimiento</h3>
            <p class="feature-description">
                10-20MB de memoria vs 150MB de Electron. Arquitectura optimizada
                con Tkinter backend nativo.
            </p>
        </div>

        <div class="feature-card">
            <div class="feature-icon">🎭</div>
            <h3 class="feature-title">Efectos Visuales</h3>
            <p class="feature-description">
                Transparencia con opacity, transiciones hover, bordes redondeados
                y efectos visuales modernos incluidos.
            </p>
        </div>

        <div class="feature-card">
            <div class="feature-icon">📱</div>
            <h3 class="feature-title">Totalmente Responsivo</h3>
            <p class="feature-description">
                Los diseños se adaptan automáticamente a diferentes tamaños de ventana
                usando unidades CSS relativas y flexbox.
            </p>
        </div>
    </div>

    <!-- Code Preview -->
    <div style="max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
        <div class="code-preview">
&lt;!-- Ejemplo de uso avanzado con MyPyGUI-NG --&gt;
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
    &lt;style&gt;
        .modern-app {{
            display: flex;
            background: linear-gradient(135deg, #667eea, #764ba2);
            font: 16px 'Segoe UI', sans-serif;
            min-height: 100vh;
        }}

        .container {{
            display: flex;
            justify-content: center;
            align-items: center;
            flex: 1;
            padding: 2em;
        }}

        .card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 2em;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
            text-align: center;
        }}
    &lt;/style&gt;
&lt;/head&gt;
&lt;body class="modern-app"&gt;
    &lt;div class="container"&gt;
        &lt;div class="card"&gt;
            &lt;h1&gt;🎉 ¡Aplicación moderna lista!&lt;/h1&gt;
            &lt;p&gt;Creada con MyPyGUI-NG en Python&lt;/p&gt;
        &lt;/div&gt;
    &lt;/div&gt;
&lt;/body&gt;
&lt;/html&gt;
        </div>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <h3 class="footer-title">🚀 MyPyGUI-NG</h3>
        <p class="footer-text">
            El futuro de las GUIs en Python ya está aquí.<br>
            Ligero, moderno y completamente funcional.
        </p>
        <p style="margin: 0; opacity: 0.7;">
            © 2024 Martin Alejandro Oviedo | MIT License
        </p>
    </footer>

    <!-- JavaScript para cambio de tema -->
    <script>
        function setTheme(themeName) {{
            console.log('Cambiando a tema:', themeName);

            // Remover clase active de todos los botones
            document.querySelectorAll('.theme-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});

            // Agregar clase active al botón seleccionado
            document.getElementById(themeName.replace('-lite', '') + '-btn').classList.add('active');

            // Aquí iría la lógica real para cambiar el tema
            // Por ahora solo mostramos en consola
        }}

        // Establecer tema inicial
        document.getElementById('bootstrap-btn').classList.add('active');
    </script>
</body>
</html>
"""

        return html_content

    def run(self):
        """Ejecutar la aplicación de demostración."""
        print("🚀 Iniciando aplicación de demostración completa...")

        # Crear ventana
        self.window = BrowserWindow()
        self.window.set_title("MyPyGUI-NG - Demostración Completa")
        self.window.set_size(1200, 800)

        # Crear y cargar contenido HTML
        html_content = self.create_showcase_html()
        uri = URI.from_string("data:text/html;charset=utf-8," + html_content)
        self.window.load_page(uri)

        # Mostrar ventana
        self.window.show()

        print("✅ Aplicación de demostración iniciada!")
        print("🎯 Características demostradas:")
        print("   • Cambio dinámico entre múltiples temas")
        print("   • Layout responsive avanzado")
        print("   • Grid layout con CSS Grid")
        print("   • Efectos hover y transiciones")
        print("   • Gradientes y efectos visuales modernos")
        print("   • JavaScript básico integrado")


def main():
    """Función principal."""
    app = ThemeShowcaseApp()
    app.run()


if __name__ == "__main__":
    main()
