"""
Theme system for MyPyGUI-NG.

This module provides pre-built CSS themes for consistent styling.
"""

import os
from pathlib import Path

__all__ = ['get_theme_css', 'list_themes', 'apply_theme']

_AVAILABLE_THEMES = {
    'bootstrap-lite': 'Bootstrap-inspired styling',
    'material-lite': 'Material Design inspired styling',
    'default': 'Default MyPyGUI styling'
}

def list_themes():
    """List all available themes."""
    return list(_AVAILABLE_THEMES.keys())

def get_theme_css(theme_name):
    """
    Get the CSS content for a specific theme.

    Args:
        theme_name (str): Name of the theme

    Returns:
        str: CSS content for the theme
    """
    if theme_name not in _AVAILABLE_THEMES:
        raise ValueError(f"Theme '{theme_name}' not found. Available: {list_themes()}")

    # Try to load from CSS file first
    css_file = Path(__file__).parent / f"{theme_name}.css"
    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            return f.read()

    # Fallback to built-in themes
    if theme_name == 'bootstrap-lite':
        return _get_bootstrap_lite_css()
    elif theme_name == 'material-lite':
        return _get_material_lite_css()
    else:  # default
        return _get_default_css()

def apply_theme(theme_name):
    """
    Apply a theme (placeholder for future implementation).

    Args:
        theme_name (str): Name of the theme to apply
    """
    print(f"🎨 Applying theme: {theme_name}")
    print("💡 Note: Theme system is under development.")
    print("   For now, include the CSS manually in your HTML.")
    css_content = get_theme_css(theme_name)
    return css_content

def _get_bootstrap_lite_css():
    """Bootstrap-inspired theme CSS."""
    return """
/* Bootstrap Lite Theme for MyPyGUI-NG */

/* Base styles */
* {
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    color: #212529;
    background-color: #fff;
    margin: 0;
    padding: 1rem;
}

/* Buttons */
.btn {
    display: inline-block;
    font-weight: 400;
    text-align: center;
    vertical-align: middle;
    user-select: none;
    border: 1px solid transparent;
    padding: 0.375rem 0.75rem;
    font-size: 1rem;
    line-height: 1.5;
    border-radius: 0.25rem;
    transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out;
    text-decoration: none;
    cursor: pointer;
}

.btn-primary {
    color: #fff;
    background-color: #007bff;
    border-color: #007bff;
}

.btn-primary:hover {
    background-color: #0056b3;
    border-color: #004085;
}

.btn-secondary {
    color: #fff;
    background-color: #6c757d;
    border-color: #6c757d;
}

.btn-secondary:hover {
    background-color: #545b62;
    border-color: #4e555b;
}

/* Cards */
.card {
    background-color: #fff;
    border: 1px solid rgba(0, 0, 0, 0.125);
    border-radius: 0.25rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    margin-bottom: 1rem;
}

.card-body {
    padding: 1.25rem;
}

.card-title {
    margin-bottom: 0.5rem;
    font-size: 1.25rem;
    font-weight: 500;
}

/* Grid system */
.row {
    display: flex;
    flex-wrap: wrap;
    margin-right: -15px;
    margin-left: -15px;
}

.col {
    flex-basis: 0;
    flex-grow: 1;
    max-width: 100%;
    padding-right: 15px;
    padding-left: 15px;
}

.col-auto {
    flex: 0 0 auto;
    width: auto;
    max-width: none;
}

/* Alerts */
.alert {
    padding: 0.75rem 1.25rem;
    margin-bottom: 1rem;
    border: 1px solid transparent;
    border-radius: 0.25rem;
}

.alert-info {
    color: #0c5460;
    background-color: #d1ecf1;
    border-color: #bee5eb;
}

.alert-success {
    color: #155724;
    background-color: #d4edda;
    border-color: #c3e6cb;
}

.alert-warning {
    color: #856404;
    background-color: #fff3cd;
    border-color: #ffeaa7;
}

.alert-danger {
    color: #721c24;
    background-color: #f8d7da;
    border-color: #f5c6cb;
}

/* Forms */
.form-control {
    display: block;
    width: 100%;
    padding: 0.375rem 0.75rem;
    font-size: 1rem;
    line-height: 1.5;
    color: #495057;
    background-color: #fff;
    border: 1px solid #ced4da;
    border-radius: 0.25rem;
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-control:focus {
    border-color: #80bdff;
    outline: 0;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-group {
    margin-bottom: 1rem;
}

.form-label {
    margin-bottom: 0.5rem;
    display: inline-block;
}

/* Utilities */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 1rem; }
.mt-4 { margin-top: 1.5rem; }
.mt-5 { margin-top: 3rem; }

.mb-1 { margin-bottom: 0.25rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 1rem; }
.mb-4 { margin-bottom: 1.5rem; }
.mb-5 { margin-bottom: 3rem; }

.p-1 { padding: 0.25rem; }
.p-2 { padding: 0.5rem; }
.p-3 { padding: 1rem; }
.p-4 { padding: 1.5rem; }
.p-5 { padding: 3rem; }

.bg-light { background-color: #f8f9fa; }
.bg-dark { background-color: #343a40; color: #fff; }
.bg-primary { background-color: #007bff; color: #fff; }
.bg-secondary { background-color: #6c757d; color: #fff; }
"""

def _get_material_lite_css():
    """Material Design inspired theme CSS."""
    return """
/* Material Lite Theme for MyPyGUI-NG */

/* Base styles */
* {
    box-sizing: border-box;
}

body {
    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.5;
    color: #212121;
    background-color: #fafafa;
    margin: 0;
    padding: 1rem;
}

/* Material Design Colors */
:root {
    --primary-color: #2196F3;
    --secondary-color: #FFC107;
    --success-color: #4CAF50;
    --error-color: #F44336;
    --background-color: #FAFAFA;
    --surface-color: #FFFFFF;
    --text-primary: #212121;
    --text-secondary: #757575;
}

/* Cards (Material Design Cards) */
.card {
    background-color: var(--surface-color);
    border-radius: 4px;
    box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.2), 0 1px 1px 0 rgba(0, 0, 0, 0.14), 0 1px 3px 0 rgba(0, 0, 0, 0.12);
    margin-bottom: 16px;
    transition: box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
    box-shadow: 0 4px 2px -2px rgba(0, 0, 0, 0.2), 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 2px 4px 0 rgba(0, 0, 0, 0.12);
}

.card-content {
    padding: 16px;
}

.card-title {
    margin: 0 0 8px 0;
    font-size: 1.25rem;
    font-weight: 500;
    color: var(--text-primary);
}

/* Buttons (Material Design Buttons) */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 36px;
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.0892857143em;
    text-decoration: none;
    cursor: pointer;
    transition: background-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    outline: none;
    position: relative;
    overflow: hidden;
}

.btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: currentColor;
    opacity: 0;
    transition: opacity 0.15s ease-in-out;
}

.btn:hover::before {
    opacity: 0.04;
}

.btn:focus {
    box-shadow: 0 0 0 0.2rem rgba(33, 150, 243, 0.5);
}

.btn-primary {
    background-color: var(--primary-color);
    color: #fff;
}

.btn-primary:hover {
    background-color: #1976D2;
}

.btn-secondary {
    background-color: #9E9E9E;
    color: #000;
}

.btn-secondary:hover {
    background-color: #757575;
}

/* Form elements (Material Design) */
.form-field {
    margin-bottom: 16px;
}

.form-input {
    width: 100%;
    padding: 16px 14px 14px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
    line-height: 1.5;
    color: var(--text-primary);
    background-color: var(--surface-color);
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-input:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.form-label {
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    padding: 16px 14px 14px;
    pointer-events: none;
    border: 1px solid transparent;
    color: #757575;
    font-size: 1rem;
    transition: transform 0.15s ease-in-out, color 0.15s ease-in-out;
    transform-origin: 0 100%;
}

.form-input:focus + .form-label,
.form-input:not(:placeholder-shown) + .form-label {
    transform: translateY(-50%) scale(0.75);
    color: var(--primary-color);
}

/* Chips */
.chip {
    display: inline-flex;
    align-items: center;
    padding: 8px 12px;
    border-radius: 16px;
    font-size: 0.875rem;
    background-color: #E3F2FD;
    color: #1976D2;
    margin: 4px;
}

.chip-primary {
    background-color: #E3F2FD;
    color: #1976D2;
}

.chip-secondary {
    background-color: #FFF3E0;
    color: #F57C00;
}

/* Grid system */
.grid {
    display: flex;
    flex-wrap: wrap;
    margin: -8px;
}

.grid-item {
    padding: 8px;
}

.grid-item-1 { flex: 0 0 8.333333%; max-width: 8.333333%; }
.grid-item-2 { flex: 0 0 16.666667%; max-width: 16.666667%; }
.grid-item-3 { flex: 0 0 25%; max-width: 25%; }
.grid-item-4 { flex: 0 0 33.333333%; max-width: 33.333333%; }
.grid-item-6 { flex: 0 0 50%; max-width: 50%; }
.grid-item-12 { flex: 0 0 100%; max-width: 100%; }

/* Utilities */
.text-primary { color: var(--primary-color); }
.text-secondary { color: var(--text-secondary); }
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.elevation-1 { box-shadow: 0 2px 1px -1px rgba(0, 0, 0, 0.2), 0 1px 1px 0 rgba(0, 0, 0, 0.14), 0 1px 3px 0 rgba(0, 0, 0, 0.12); }
.elevation-2 { box-shadow: 0 3px 1px -2px rgba(0, 0, 0, 0.2), 0 2px 2px 0 rgba(0, 0, 0, 0.14), 0 1px 5px 0 rgba(0, 0, 0, 0.12); }
.elevation-3 { box-shadow: 0 3px 3px -2px rgba(0, 0, 0, 0.2), 0 3px 4px 0 rgba(0, 0, 0, 0.14), 0 1px 8px 0 rgba(0, 0, 0, 0.12); }

.rounded-sm { border-radius: 4px; }
.rounded { border-radius: 8px; }
.rounded-lg { border-radius: 12px; }
.rounded-full { border-radius: 9999px; }

.m-0 { margin: 0; }
.m-1 { margin: 4px; }
.m-2 { margin: 8px; }
.m-3 { margin: 16px; }
.m-4 { margin: 24px; }
.m-5 { margin: 48px; }

.p-0 { padding: 0; }
.p-1 { padding: 4px; }
.p-2 { padding: 8px; }
.p-3 { padding: 16px; }
.p-4 { padding: 24px; }
.p-5 { padding: 48px; }
"""

def _get_default_css():
    """Default MyPyGUI theme CSS."""
    return """
/* Default MyPyGUI Theme */

* {
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #fff;
    margin: 0;
    padding: 1rem;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

.card {
    background-color: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 4px;
    background-color: #007bff;
    color: white;
    text-decoration: none;
    cursor: pointer;
    font-size: 0.875rem;
    transition: background-color 0.2s;
}

.btn:hover {
    background-color: #0056b3;
}

.btn-secondary {
    background-color: #6c757d;
}

.btn-secondary:hover {
    background-color: #545b62;
}

.form-group {
    margin-bottom: 1rem;
}

.form-input {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: 1rem;
}

.form-input:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.alert {
    padding: 0.75rem;
    border-radius: 4px;
    margin-bottom: 1rem;
}

.alert-info {
    background-color: #d1ecf1;
    color: #0c5460;
    border: 1px solid #bee5eb;
}

.alert-success {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 1rem; }

.mb-1 { margin-bottom: 0.25rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-3 { margin-bottom: 1rem; }

.d-flex { display: flex; }
.justify-center { justify-content: center; }
.align-center { align-items: center; }
.gap-1 { gap: 0.25rem; }
.gap-2 { gap: 0.5rem; }
.gap-3 { gap: 1rem; }
"""
