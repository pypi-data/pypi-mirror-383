"""
Interactive demo for MyPyGUI-NG capabilities.

This module provides an easy way to showcase MyPyGUI features.
Run with: python -m mypygui_ng.demo
"""

import os
import sys
import webbrowser
from pathlib import Path

def run_demo():
    """
    Launch the interactive demo in a browser window.
    """
    # Get the path to the showcase file
    current_dir = Path(__file__).parent
    showcase_path = current_dir / ".." / "examples" / "html" / "showcase_complete.html"

    if not showcase_path.exists():
        print("❌ Showcase demo file not found!")
        print(f"Expected at: {showcase_path}")
        return

    showcase_url = f"file://{showcase_path.absolute()}"

    print("🚀 Launching MyPyGUI-NG Interactive Demo...")
    print(f"📂 Opening: {showcase_path}")
    print("💡 Note: This is a static HTML showcase of capabilities.")
    print("   For live demos, run the example Python scripts in examples/")

    try:
        webbrowser.open(showcase_url)
        print("✅ Demo launched successfully!")
        print("🎯 Check your browser for the interactive showcase.")
    except Exception as e:
        print(f"❌ Failed to launch demo: {e}")
        print(f"💡 Try opening manually: {showcase_path}")

def print_capabilities():
    """Print current MyPyGUI capabilities."""
    print("\n🎯 MyPyGUI-NG Current Capabilities:")
    print("=" * 50)
    print("✅ Layout & Structure:")
    print("   • HTML rendering with Tkinter backend")
    print("   • Modern flexbox layout (display: flex)")
    print("   • Responsive design (em, rem, vh, vw)")
    print("   • CSS Grid support (basic)")

    print("\n✅ Visual & Styling:")
    print("   • Complete color support (hex, named, rgb)")
    print("   • Opacity and transparency effects")
    print("   • Font shorthand (font: size family)")
    print("   • Border radius and styling")
    print("   • Box shadows (planned)")

    print("\n✅ Positioning & Spacing:")
    print("   • Margin and padding (full support)")
    print("   • Position properties (absolute, relative, fixed)")
    print("   • Z-index layering")
    print("   • Aspect ratio support")

    print("\n✅ Typography:")
    print("   • Font family, size, weight, variant")
    print("   • Text alignment and decoration")
    print("   • Line height and spacing")
    print("   • Font shorthand support")

    print("\n🔄 Coming Soon:")
    print("   • SVG support for vector icons")
    print("   • Theme system (Bootstrap-lite, Material-lite)")
    print("   • Animation and transitions")
    print("   • Box shadows and gradients")
    print("   • @font-face support")

    print("\n🚀 Performance:")
    print("   • Lightweight (~10-20MB vs Electron's 100-200MB)")
    print("   • Async architecture with service handlers")
    print("   • Efficient CSS parsing and validation")
    print("   • Minimal dependencies")

if __name__ == "__main__":
    print_capabilities()
    print("\n" + "="*50)
    run_demo()
