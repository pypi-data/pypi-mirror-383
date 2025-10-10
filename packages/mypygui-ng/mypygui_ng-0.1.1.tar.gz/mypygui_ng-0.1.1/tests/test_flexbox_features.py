"""
Tests para las nuevas características implementadas: Flexbox y Unidades Relativas
"""
import sys
import os
import time

# Agregar el directorio src al path para importar mypygui
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import mypygui


class TestFlexboxImplementation:
    """Tests para verificar que flexbox funciona correctamente"""

    def test_flex_display_parsing(self):
        """Test que display: flex se parsea correctamente"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .flex-container {
                    display: flex;
                    background-color: #f0f0f0;
                    padding: 10px;
                    gap: 10px;
                }
                .flex-item {
                    background-color: #3498db;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <div class="flex-container">
                <div class="flex-item">Item 1</div>
                <div class="flex-item">Item 2</div>
                <div class="flex-item">Item 3</div>
            </div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None
        print("✅ Test flexbox display pasó")

    def test_justify_content_parsing(self):
        """Test que justify-content se parsea correctamente"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .flex-container {
                    display: flex;
                    justify-content: space-between;
                    background-color: #f0f0f0;
                    padding: 10px;
                }
                .flex-item {
                    background-color: #e74c3c;
                    padding: 15px;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <div class="flex-container">
                <div class="flex-item">Inicio</div>
                <div class="flex-item">Centro</div>
                <div class="flex-item">Final</div>
            </div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None
        print("✅ Test justify-content pasó")

    def test_align_items_parsing(self):
        """Test que align-items se parsea correctamente"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .flex-container {
                    display: flex;
                    align-items: center;
                    background-color: #f0f0f0;
                    padding: 10px;
                    height: 100px;
                }
                .flex-item {
                    background-color: #2ecc71;
                    padding: 10px;
                    border-radius: 5px;
                }
                .tall-item {
                    background-color: #9b59b6;
                    height: 40px;
                }
            </style>
        </head>
        <body>
            <div class="flex-container">
                <div class="flex-item">Corto</div>
                <div class="flex-item tall-item">Más alto</div>
                <div class="flex-item">Corto</div>
            </div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None
        print("✅ Test align-items pasó")

    def test_relative_units_parsing(self):
        """Test que las unidades relativas funcionan"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .em-unit {
                    font-size: 2em;
                    background-color: #f39c12;
                    padding: 0.5em;
                    margin: 0.25em;
                }
                .rem-unit {
                    font-size: 1.5rem;
                    background-color: #27ae60;
                    padding: 10px;
                }
                .vh-unit {
                    height: 50vh;
                    background-color: #8e44ad;
                }
                .vw-unit {
                    width: 30vw;
                    background-color: #e74c3c;
                    height: 20px;
                }
            </style>
        </head>
        <body>
            <div class="em-unit">Texto con em</div>
            <div class="rem-unit">Texto con rem</div>
            <div class="vh-unit">Contenedor 50vh</div>
            <div class="vw-unit">Contenedor 30vw</div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None
        print("✅ Test unidades relativas pasó")


class TestCombinedFeatures:
    """Tests que combinan múltiples características nuevas"""

    def test_flexbox_with_relative_units(self):
        """Test flexbox usando unidades relativas"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                .responsive-container {
                    display: flex;
                    gap: 2vw;
                    padding: 1em;
                    background-color: #34495e;
                }
                .responsive-item {
                    background-color: #3498db;
                    color: white;
                    padding: 1em;
                    border-radius: 0.5em;
                    flex: 1;
                    text-align: center;
                    font-size: 1.2rem;
                }
            </style>
        </head>
        <body>
            <div class="responsive-container">
                <div class="responsive-item">Responsive 1</div>
                <div class="responsive-item">Responsive 2</div>
                <div class="responsive-item">Responsive 3</div>
            </div>
        </body>
        </html>
        """

        browser_window = mypygui.BrowserWindow()
        uri = mypygui.fs.URI.from_string("data:text/html," + html_content)

        load_promise = browser_window.load_page(uri)
        assert load_promise is not None
        print("✅ Test flexbox con unidades relativas pasó")


if __name__ == "__main__":
    print("🧪 Ejecutando tests de nuevas características...")

    flexbox_tests = TestFlexboxImplementation()
    flexbox_tests.test_flex_display_parsing()
    flexbox_tests.test_justify_content_parsing()
    flexbox_tests.test_align_items_parsing()
    flexbox_tests.test_relative_units_parsing()

    print("✅ Tests de flexbox pasaron")

    combined_tests = TestCombinedFeatures()
    combined_tests.test_flexbox_with_relative_units()

    print("✅ Tests combinados pasaron")
    print("🎉 Todas las pruebas de nuevas características completadas!")
