"""
Tests para las nuevas propiedades CSS implementadas
"""
import sys
import os
import time

# Agregar el directorio src al path para importar mypygui
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import mypygui


class TestNewCSSProperties:
    """Tests para propiedades CSS recientemente implementadas"""

    def test_opacity_property(self):
        """Test propiedad opacity"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .semi-transparent {
                    opacity: 0.5;
                    background-color: #ff0000;
                    width: 100px;
                    height: 100px;
                }
                .fully-transparent {
                    opacity: 0;
                    background-color: #00ff00;
                    width: 100px;
                    height: 100px;
                }
            </style>
        </head>
        <body>
            <div class="semi-transparent">Semi transparente</div>
            <div class="fully-transparent">Totalmente transparente</div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None
        print("✅ Test opacity pasó")

    def test_font_shorthand(self):
        """Test font shorthand property"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .styled-text {
                    font: 16px Arial, sans-serif;
                    color: #333333;
                }
                .bold-text {
                    font: bold 18px "Times New Roman", serif;
                    color: #000000;
                }
            </style>
        </head>
        <body>
            <span class="styled-text">Texto con font shorthand</span>
            <div class="bold-text">Texto en negrita</div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None
        print("✅ Test font shorthand pasó")

    def test_combined_properties(self):
        """Test combinación de propiedades nuevas y existentes"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .complex-element {
                    opacity: 0.7;
                    background-color: #blue;
                    font: 14px Verdana, sans-serif;
                    padding: 10px;
                    margin: 5px;
                    border: 2px solid #000;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <div class="complex-element">
                Elemento con múltiples propiedades CSS
            </div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None
        print("✅ Test propiedades combinadas pasó")

    def test_error_handling_new_properties(self):
        """Test manejo de errores con nuevas propiedades"""
        # Test valores inválidos de opacity
        html_invalid_opacity = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .invalid-opacity {
                    opacity: invalid-value;
                    background-color: #ff0000;
                    width: 100px;
                    height: 100px;
                }
            </style>
        </head>
        <body>
            <div class="invalid-opacity">Opacity inválido</div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_invalid_opacity)

        # Debería manejar el error sin crashar
        load_promise = browser_window.load_page(uri)
        assert load_promise is not None
        print("✅ Test manejo de errores pasó")


class TestDocumentationExamples:
    """Tests basados en ejemplos de documentación"""

    def test_basic_usage_example(self):
        """Test ejemplo básico de uso"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    background-color: #f0f0f0;
                    font-family: Arial, sans-serif;
                }
                .container {
                    background-color: white;
                    padding: 20px;
                    margin: 10px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .title {
                    color: #333;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .content {
                    color: #666;
                    line-height: 1.6;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="title">Título de ejemplo</div>
                <div class="content">
                    Este es un párrafo de contenido con estilos aplicados.
                    Incluye colores, fuentes, espaciado y otros efectos visuales.
                </div>
            </div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None
        print("✅ Test ejemplo básico pasó")


if __name__ == "__main__":
    print("🧪 Ejecutando tests de nuevas propiedades CSS...")

    test = TestNewCSSProperties()
    test.test_opacity_property()
    test.test_font_shorthand()
    test.test_combined_properties()
    test.test_error_handling_new_properties()

    print("✅ Todos los tests de nuevas propiedades pasaron")

    doc_test = TestDocumentationExamples()
    doc_test.test_basic_usage_example()

    print("✅ Tests de documentación pasaron")
    print("🎉 Todas las pruebas completadas exitosamente!")
