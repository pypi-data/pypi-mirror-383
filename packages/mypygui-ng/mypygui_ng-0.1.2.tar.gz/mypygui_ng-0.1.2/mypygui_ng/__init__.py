"""
MyPyGUI-NG: Modern GUIs for Python using HTML+CSS

A lightweight alternative to Electron that renders HTML/CSS in Python applications.

Main features:
- HTML/CSS rendering engine
- Modern layout with Flexbox support
- Responsive design with relative units (em, rem, vh, vw)
- Visual effects (opacity, transitions)
- Typography (font shorthand)
- SVG support (planned)
- Theme system (planned)
"""

__version__ = "0.1.1"
__author__ = "Martin Alejandro Oviedo"
__email__ = "martin@oviedo.com.ar"

# Main API exports
try:
    from .browser_window import BrowserWindow
    from .core.fs.uri import URI
    from .core.asynchronous import async_tools
    from .core.services import ServiceProvider
    from .page import Page
    from .page.objects.dom import DOMNode
    from .page.objects.render_tree import RenderNode
    from .themes import apply_theme, get_theme_css, list_themes

except ImportError as e:
    import warnings
    warnings.warn(f"Failed to import some modules: {e}")

# Convenience imports
__all__ = [
    'BrowserWindow',
    'URI',
    'Page',
    'DOMNode',
    'RenderNode',
    'ServiceProvider',
    'async_tools',
    'apply_theme',
    'get_theme_css',
    'list_themes',
    '__version__',
    '__author__',
    '__email__'
]

# Demo functionality
def demo():
    """
    Launch the interactive demo showcasing MyPyGUI capabilities.

    Usage:
        python -m mypygui_ng.demo
        # or
        from mypygui_ng import demo; demo()
    """
    try:
        from .demo import run_demo
        run_demo()
    except ImportError as e:
        print(f"Demo not available: {e}")
        print("Run 'pip install mypygui-ng[demo]' to include demo dependencies")

# Theme system (placeholder for future implementation)
class Theme:
    """Theme management system for MyPyGUI applications."""

    _current_theme = None
    _available_themes = {}

    @classmethod
    def use(cls, theme_name):
        """Apply a theme to the application."""
        if theme_name not in cls._available_themes:
            raise ValueError(f"Theme '{theme_name}' not found")
        cls._current_theme = theme_name
        print(f"Applied theme: {theme_name}")

    @classmethod
    def available_themes(cls):
        """List all available themes."""
        return list(cls._available_themes.keys())

# Theme system integration
try:
    from .themes import get_theme_css, list_themes, apply_theme
    __all__.extend(['get_theme_css', 'list_themes', 'apply_theme'])
except ImportError:
    # Themes not available
    pass