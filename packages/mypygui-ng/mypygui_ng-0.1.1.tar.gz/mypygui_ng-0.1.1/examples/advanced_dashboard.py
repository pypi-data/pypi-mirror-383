"""
Ejemplo avanzado: Dashboard administrativo moderno con MyPyGUI-NG

Este ejemplo muestra cómo crear una aplicación de dashboard completa usando
características avanzadas como flexbox, temas y diseño responsivo.
"""

import sys
import os

# Agregar el directorio src al path para desarrollo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mypygui_ng import BrowserWindow, URI
from mypygui_ng.themes import get_theme_css


def create_dashboard_html():
    """Crear HTML para dashboard administrativo."""

    # Usar tema Material Lite para apariencia profesional
    material_theme = get_theme_css('material-lite')

    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Administrativo - MyPyGUI-NG</title>
    <style>
        {material_theme}

        :root {{
            --primary-color: #2196F3;
            --success-color: #4CAF50;
            --warning-color: #FF9800;
            --danger-color: #F44336;
            --text-primary: #212121;
            --text-secondary: #757575;
            --background-color: #FAFAFA;
        }}

        body {{
            margin: 0;
            padding: 0;
            font-family: 'Roboto', sans-serif;
            background-color: var(--background-color);
        }}

        /* Header */
        .header {{
            background: linear-gradient(135deg, var(--primary-color), #1976D2);
            color: white;
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}

        .header-content {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .logo-icon {{
            width: 40px;
            height: 40px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }}

        .user-info {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .avatar {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        /* Main Layout */
        .main-container {{
            display: flex;
            min-height: calc(100vh - 80px);
            max-width: 1200px;
            margin: 0 auto;
            gap: 2rem;
            padding: 2rem;
        }}

        /* Sidebar */
        .sidebar {{
            width: 280px;
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            height: fit-content;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .nav-item {{
            display: flex;
            align-items: center;
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            color: var(--text-primary);
        }}

        .nav-item:hover {{
            background-color: #E3F2FD;
            color: var(--primary-color);
        }}

        .nav-item.active {{
            background-color: var(--primary-color);
            color: white;
        }}

        .nav-icon {{
            margin-right: 0.75rem;
            font-size: 1.2rem;
        }}

        /* Content Area */
        .content {{
            flex: 1;
            background: white;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}

        .content-header {{
            margin-bottom: 2rem;
        }}

        .content-title {{
            margin: 0 0 0.5rem 0;
            color: var(--text-primary);
            font-size: 1.8rem;
        }}

        .content-subtitle {{
            color: var(--text-secondary);
            margin: 0;
        }}

        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: linear-gradient(135deg, var(--primary-color), #1976D2);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
        }}

        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}

        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}

        /* Recent Activity */
        .activity-section {{
            margin-top: 2rem;
        }}

        .activity-list {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}

        .activity-item {{
            display: flex;
            align-items: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid var(--primary-color);
        }}

        .activity-icon {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: var(--primary-color);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
        }}

        .activity-content {{
            flex: 1;
        }}

        .activity-title {{
            margin: 0 0 0.25rem 0;
            font-weight: 500;
        }}

        .activity-time {{
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .main-container {{
                flex-direction: column;
                padding: 1rem;
            }}

            .sidebar {{
                width: 100%;
            }}

            .header-content {{
                flex-direction: column;
                gap: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <div class="logo-icon">📊</div>
                <div>
                    <h1 style="margin: 0; font-size: 1.5rem;">Admin Dashboard</h1>
                    <p style="margin: 0; opacity: 0.9;">Panel de control moderno</p>
                </div>
            </div>
            <div class="user-info">
                <span>👋 Bienvenido, Admin</span>
                <div class="avatar">A</div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <div class="main-container">
        <!-- Sidebar Navigation -->
        <aside class="sidebar">
            <nav>
                <a href="#" class="nav-item active">
                    <span class="nav-icon">🏠</span>
                    Dashboard
                </a>
                <a href="#" class="nav-item">
                    <span class="nav-icon">👥</span>
                    Usuarios
                </a>
                <a href="#" class="nav-item">
                    <span class="nav-icon">📦</span>
                    Productos
                </a>
                <a href="#" class="nav-item">
                    <span class="nav-icon">📊</span>
                    Analytics
                </a>
                <a href="#" class="nav-item">
                    <span class="nav-icon">⚙️</span>
                    Configuración
                </a>
            </nav>
        </aside>

        <!-- Main Content Area -->
        <main class="content">
            <div class="content-header">
                <h2 class="content-title">Dashboard General</h2>
                <p class="content-subtitle">Resumen de actividad del sistema</p>
            </div>

            <!-- Stats Cards -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">1,234</div>
                    <div class="stat-label">Usuarios Totales</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">856</div>
                    <div class="stat-label">Sesiones Activas</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">92%</div>
                    <div class="stat-label">Uptime del Sistema</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">47</div>
                    <div class="stat-label">Nuevos Registros</div>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="activity-section">
                <h3>Actividad Reciente</h3>
                <div class="activity-list">
                    <div class="activity-item">
                        <div class="activity-icon">👤</div>
                        <div class="activity-content">
                            <h4 class="activity-title">Nuevo usuario registrado</h4>
                            <span class="activity-time">hace 5 minutos</span>
                        </div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-icon">📦</div>
                        <div class="activity-content">
                            <h4 class="activity-title">Producto actualizado</h4>
                            <span class="activity-time">hace 12 minutos</span>
                        </div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-icon">⚙️</div>
                        <div class="activity-content">
                            <h4 class="activity-title">Configuración modificada</h4>
                            <span class="activity-time">hace 1 hora</span>
                        </div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-icon">📊</div>
                        <div class="activity-content">
                            <h4 class="activity-title">Reporte generado</h4>
                            <span class="activity-time">hace 2 horas</span>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>
</body>
</html>
"""

    return html_content


def main():
    """Función principal para ejecutar el dashboard."""
    print("🚀 Iniciando Dashboard Administrativo con MyPyGUI-NG...")

    # Crear ventana
    window = BrowserWindow()
    window.set_title("Dashboard Administrativo - MyPyGUI-NG")
    window.set_size(1400, 900)

    # Crear contenido HTML
    html_content = create_dashboard_html()

    # Cargar página
    uri = URI.from_string("data:text/html;charset=utf-8," + html_content)
    window.load_page(uri)

    # Mostrar ventana
    window.show()

    print("✅ Dashboard iniciado exitosamente!")
    print("🎯 Características demostradas:")
    print("   • Layout responsive con flexbox")
    print("   • Tema Material Design")
    print("   • Grid layout moderno")
    print("   • Efectos visuales avanzados")
    print("   • Diseño profesional completo")


if __name__ == "__main__":
    main()
