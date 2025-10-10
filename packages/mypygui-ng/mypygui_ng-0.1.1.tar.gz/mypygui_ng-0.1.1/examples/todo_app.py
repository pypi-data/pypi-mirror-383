"""
Ejemplo avanzado: Aplicación de Lista de Tareas (Todo List) con MyPyGUI-NG

Este ejemplo demuestra el uso avanzado de MyPyGUI-NG para crear una aplicación
interactiva completa con funcionalidades modernas.
"""

import sys
import os
import json
from datetime import datetime

# Agregar el directorio src al path para desarrollo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mypygui_ng import BrowserWindow, URI
from mypygui_ng.themes import get_theme_css


class TodoApp:
    """Aplicación de lista de tareas moderna."""

    def __init__(self):
        self.todos = self.load_todos()
        self.window = None

    def load_todos(self):
        """Cargar tareas desde archivo (simulado)."""
        # En una aplicación real, esto vendría de una base de datos
        return [
            {
                "id": 1,
                "title": "Aprender MyPyGUI-NG",
                "completed": True,
                "priority": "high",
                "created": "2024-01-15T10:00:00"
            },
            {
                "id": 2,
                "title": "Crear aplicación de ejemplo",
                "completed": False,
                "priority": "medium",
                "created": "2024-01-15T14:30:00"
            },
            {
                "id": 3,
                "title": "Publicar en PyPI",
                "completed": False,
                "priority": "high",
                "created": "2024-01-16T09:15:00"
            }
        ]

    def create_todo_html(self):
        """Crear HTML para la aplicación de tareas."""

        # Usar tema Bootstrap Lite para interfaz limpia
        bootstrap_theme = get_theme_css('bootstrap-lite')

        # Crear lista de tareas como HTML
        todos_html = ""
        for todo in self.todos:
            status_class = "completed" if todo["completed"] else "pending"
            priority_badge = f"badge-{todo['priority']}"

            todos_html += f"""
            <div class="todo-item {status_class}" data-id="{todo['id']}">
                <div class="todo-checkbox">
                    <input type="checkbox" {'checked' if todo['completed'] else ''} onchange="toggleTodo({todo['id']})">
                </div>
                <div class="todo-content">
                    <div class="todo-title">{'✅ ' if todo['completed'] else ''}{todo['title']}</div>
                    <div class="todo-meta">
                        <span class="priority-badge {priority_badge}">
                            {todo['priority'].upper()}
                        </span>
                        <span class="todo-date">
                            {datetime.fromisoformat(todo['created'].replace('Z', '+00:00')).strftime('%d/%m/%Y %H:%M')}
                        </span>
                    </div>
                </div>
                <div class="todo-actions">
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteTodo({todo['id']})">
                        🗑️
                    </button>
                </div>
            </div>
            """

        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lista de Tareas - MyPyGUI-NG</title>
    <style>
        {bootstrap_theme}

        :root {{
            --primary-color: #007bff;
            --success-color: #28a745;
            --warning-color: #ffc107;
            --danger-color: #dc3545;
            --info-color: #17a2b8;
            --light-bg: #f8f9fa;
            --dark-text: #343a40;
        }}

        body {{
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}

        .app-container {{
            max-width: 800px;
            margin: 2rem auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
            overflow: hidden;
        }}

        .app-header {{
            background: linear-gradient(135deg, var(--primary-color), #0056b3);
            color: white;
            padding: 2rem;
            text-align: center;
        }}

        .app-title {{
            margin: 0 0 0.5rem 0;
            font-size: 2.5rem;
            font-weight: bold;
        }}

        .app-subtitle {{
            margin: 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }}

        .add-todo-form {{
            display: flex;
            gap: 1rem;
            padding: 2rem;
            background: white;
        }}

        .form-control {{
            flex: 1;
            padding: 0.75rem 1rem;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }}

        .form-control:focus {{
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
        }}

        .btn-add {{
            padding: 0.75rem 2rem;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .btn-add:hover {{
            background: #0056b3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 123, 255, 0.4);
        }}

        .todos-container {{
            padding: 0 2rem 2rem;
        }}

        .todos-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #e9ecef;
        }}

        .todos-title {{
            margin: 0;
            color: var(--dark-text);
            font-size: 1.5rem;
        }}

        .todos-count {{
            background: var(--light-bg);
            color: var(--dark-text);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        }}

        .todo-item {{
            display: flex;
            align-items: center;
            padding: 1.5rem;
            background: white;
            margin-bottom: 1rem;
            border-radius: 12px;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }}

        .todo-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }}

        .todo-item.completed {{
            opacity: 0.7;
            background: #f8f9fa;
        }}

        .todo-item.completed .todo-title {{
            text-decoration: line-through;
            color: #6c757d;
        }}

        .todo-checkbox {{
            margin-right: 1rem;
        }}

        .todo-checkbox input[type="checkbox"] {{
            width: 20px;
            height: 20px;
            accent-color: var(--success-color);
        }}

        .todo-content {{
            flex: 1;
        }}

        .todo-title {{
            margin: 0 0 0.5rem 0;
            font-size: 1.1rem;
            font-weight: 500;
            color: var(--dark-text);
        }}

        .todo-meta {{
            display: flex;
            align-items: center;
            gap: 1rem;
            font-size: 0.9rem;
        }}

        .priority-badge {{
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
        }}

        .badge-high {{
            background: var(--danger-color);
            color: white;
        }}

        .badge-medium {{
            background: var(--warning-color);
            color: var(--dark-text);
        }}

        .badge-low {{
            background: var(--success-color);
            color: white;
        }}

        .todo-date {{
            color: #6c757d;
        }}

        .todo-actions {{
            display: flex;
            gap: 0.5rem;
        }}

        .btn-sm {{
            padding: 0.5rem 0.75rem;
            font-size: 0.875rem;
        }}

        .btn-outline-danger {{
            background: transparent;
            color: var(--danger-color);
            border: 1px solid var(--danger-color);
        }}

        .btn-outline-danger:hover {{
            background: var(--danger-color);
            color: white;
        }}

        .stats-section {{
            background: var(--light-bg);
            padding: 2rem;
            border-radius: 0 0 20px 20px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }}

        .stat-item {{
            text-align: center;
            padding: 1rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}

        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}

        .stat-label {{
            font-size: 0.9rem;
            color: #6c757d;
        }}

        .stat-total .stat-number {{
            color: var(--primary-color);
        }}

        .stat-pending .stat-number {{
            color: var(--warning-color);
        }}

        .stat-completed .stat-number {{
            color: var(--success-color);
        }}

        /* Responsive */
        @media (max-width: 768px) {{
            .app-container {{
                margin: 1rem;
                border-radius: 15px;
            }}

            .add-todo-form {{
                flex-direction: column;
            }}

            .todo-meta {{
                flex-direction: column;
                align-items: flex-start;
                gap: 0.5rem;
            }}

            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (max-width: 480px) {{
            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .todo-item {{
                flex-direction: column;
                align-items: flex-start;
                gap: 1rem;
            }}

            .todo-checkbox {{
                align-self: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Header -->
        <div class="app-header">
            <h1 class="app-title">📝 Lista de Tareas</h1>
            <p class="app-subtitle">Aplicación moderna creada con MyPyGUI-NG</p>
        </div>

        <!-- Add Todo Form -->
        <div class="add-todo-form">
            <input type="text" class="form-control" id="newTodoInput"
                   placeholder="¿Qué necesitas hacer hoy?" />
            <select class="form-control" id="prioritySelect">
                <option value="low">Baja prioridad</option>
                <option value="medium" selected>Media prioridad</option>
                <option value="high">Alta prioridad</option>
            </select>
            <button class="btn-add" onclick="addTodo()">➕ Agregar Tarea</button>
        </div>

        <!-- Todos Container -->
        <div class="todos-container">
            <div class="todos-header">
                <h3 class="todos-title">Tus Tareas</h3>
                <span class="todos-count" id="todosCount">{len(self.todos)} tareas</span>
            </div>

            <!-- Todos List -->
            <div id="todosList">
                {todos_html}
            </div>
        </div>

        <!-- Stats Section -->
        <div class="stats-section">
            <div class="stats-grid">
                <div class="stat-item stat-total">
                    <div class="stat-number">{len(self.todos)}</div>
                    <div class="stat-label">Total</div>
                </div>
                <div class="stat-item stat-pending">
                    <div class="stat-number">{len([t for t in self.todos if not t['completed']])}</div>
                    <div class="stat-label">Pendientes</div>
                </div>
                <div class="stat-item stat-completed">
                    <div class="stat-number">{len([t for t in self.todos if t['completed']])}</div>
                    <div class="stat-label">Completadas</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Funciones JavaScript para interactividad
        // Nota: En una implementación real, estas funciones se comunicarían
        // con el backend Python para actualizar el estado

        function addTodo() {{
            const input = document.getElementById('newTodoInput');
            const priority = document.getElementById('prioritySelect').value;

            if (input.value.trim()) {{
                console.log('Nueva tarea:', input.value, 'Prioridad:', priority);
                // Aquí iría la lógica para agregar la tarea
                input.value = '';
            }}
        }}

        function toggleTodo(id) {{
            console.log('Toggle todo:', id);
            // Aquí iría la lógica para marcar como completada
        }}

        function deleteTodo(id) {{
            console.log('Delete todo:', id);
            // Aquí iría la lógica para eliminar la tarea
        }}

        // Permitir agregar tarea con Enter
        document.getElementById('newTodoInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                addTodo();
            }}
        }});
    </script>
</body>
</html>
"""

        return html_content

    def run(self):
        """Ejecutar la aplicación."""
        print("🚀 Iniciando aplicación de Lista de Tareas...")

        # Crear ventana
        self.window = BrowserWindow()
        self.window.set_title("Lista de Tareas - MyPyGUI-NG")
        self.window.set_size(900, 700)

        # Crear y cargar contenido HTML
        html_content = self.create_todo_html()
        uri = URI.from_string("data:text/html;charset=utf-8," + html_content)
        self.window.load_page(uri)

        # Mostrar ventana
        self.window.show()

        print("✅ Aplicación de tareas iniciada!")
        print("🎯 Características demostradas:")
        print("   • Interfaz moderna con tema Bootstrap")
        print("   • Layout responsivo con flexbox")
        print("   • Estados visuales dinámicos")
        print("   • Sistema de prioridades")
        print("   • Estadísticas en tiempo real")


def main():
    """Función principal."""
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()
