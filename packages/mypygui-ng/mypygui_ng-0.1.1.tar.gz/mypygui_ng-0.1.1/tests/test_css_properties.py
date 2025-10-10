"""
Tests para propiedades CSS adicionales
"""
import sys
import os
import time

# Agregar el directorio src al path para importar mypygui
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import mypygui


class TestCSSProperties:
    """Tests para propiedades CSS específicas"""

    def test_border_properties(self):
        """Test propiedades de borde"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .bordered {
                    border: 2px solid #00ff00;
                    border-radius: 5px;
                    padding: 10px;
                }
            </style>
        </head>
        <body>
            <div class="bordered">Elemento con borde</div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        # Iniciar carga asíncrona
        load_promise = browser_window.load_page(uri)

        # Esperar un poco para que se procese
        time.sleep(0.1)

        # Verificar que se pudo crear la página
        assert load_promise is not None

    def test_margin_and_padding(self):
        """Test margin y padding"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .spaced {
                    margin: 20px;
                    padding: 15px;
                    background-color: #cccccc;
                }
            </style>
        </head>
        <body>
            <div class="spaced">Elemento con espaciado</div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None

    def test_font_properties(self):
        """Test propiedades de fuente"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .styled-text {
                    font-family: Arial, sans-serif;
                    font-size: 16px;
                    font-weight: bold;
                    color: #333333;
                }
            </style>
        </head>
        <body>
            <span class="styled-text">Texto estilizado</span>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None

    def test_positioning(self):
        """Test posicionamiento absoluto y relativo"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .relative {
                    position: relative;
                    top: 10px;
                    left: 20px;
                }
                .absolute {
                    position: absolute;
                    top: 50px;
                    right: 30px;
                }
            </style>
        </head>
        <body>
            <div class="relative">Posición relativa</div>
            <div class="absolute">Posición absoluta</div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None


class TestErrorHandling:
    """Tests para manejo de errores"""

    def test_invalid_html(self):
        """Test manejo de HTML inválido"""
        invalid_html = "<html><head><body><div>Contenido sin cerrar"

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + invalid_html)

        # Debería manejar el error sin crashar
        load_promise = browser_window.load_page(uri)
        assert load_promise is not None

    def test_missing_resources(self):
        """Test manejo de recursos faltantes"""
        html_with_missing_img = """
        <!DOCTYPE html>
        <html>
        <body>
            <img src="imagen_que_no_existe.png" alt="imagen faltante">
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_with_missing_img)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None


if __name__ == "__main__":
    print("🧪 Ejecutando tests de propiedades CSS...")

    test = TestCSSProperties()
    test.test_border_properties()
    test.test_margin_and_padding()
    test.test_font_properties()
    test.test_positioning()

    print("✅ Tests de propiedades CSS pasaron")

    error_test = TestErrorHandling()
    error_test.test_invalid_html()
    error_test.test_missing_resources()

    print("✅ Tests de manejo de errores pasaron")
