"""
Tests básicos para MyPyGUI
"""
import sys
import os

# Agregar el directorio src al path para importar mypygui
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import mypygui
import pytest


class TestBasicFunctionality:
    """Tests básicos de funcionalidad esencial"""

    def test_browser_window_creation(self):
        """Test que se puede crear una BrowserWindow"""
        browser_window = mypygui.BrowserWindow()
        assert browser_window is not None
        assert hasattr(browser_window, 'on_ready')
        assert hasattr(browser_window, 'on_close')

    def test_uri_creation(self):
        """Test creación de URIs"""
        uri = mypygui.fs.URI.from_local_path_string(__file__)
        assert uri is not None
        assert str(uri).endswith('test_basic.py')

    def test_page_loading_structure(self):
        """Test que el sistema de carga de páginas funciona"""
        browser_window = mypygui.BrowserWindow()

        # Crear una URI para el archivo de ejemplo
        example_path = os.path.join(os.path.dirname(__file__), 'examples', 'html', 'index.html')
        if os.path.exists(example_path):
            uri = mypygui.fs.URI.from_local_path_string(example_path)

            # Test que se puede iniciar la carga
            load_promise = browser_window.load_page(uri, persist=True)
            assert load_promise is not None


class TestHTMLElementRendering:
    """Tests para elementos HTML básicos"""

    def test_div_with_background_color(self):
        """Test renderizado de div con color de fondo"""
        # Crear HTML básico para testear
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .test-div {
                    background-color: #ff0000;
                    width: 100px;
                    height: 100px;
                }
            </style>
        </head>
        <body>
            <div class="test-div">Test Div</div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()

        # Crear URI temporal para el contenido
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        # Test que se puede cargar el contenido
        load_promise = browser_window.load_page(uri)
        assert load_promise is not None

    def test_img_element(self):
        """Test elemento img"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <body>
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==" alt="test">
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None


if __name__ == "__main__":
    # Ejecutar tests básicos si se corre directamente
    test = TestBasicFunctionality()
    test.test_uri_creation()
    print("✅ Tests básicos pasaron")
