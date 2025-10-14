# Printfxpy

[![PyPI version](https://badge.fury.io/py/printfxpy.svg)](https://badge.fury.io/py/printfxpy)
[![Downloads](https://pepy.tech/badge/printfxpy)](https://pepy.tech/project/printfxpy)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/Discord-Support%20Server-7289DA?style=flat&logo=discord)](https://discord.gg/MaWeRFxa)

A simple and colorful text printing library for Python.

## Support

Join our Discord server for support, questions, and community discussions:

[![Discord](https://img.shields.io/badge/Discord-Support%20Server-7289DA?style=flat&logo=discord)](https://discord.gg/MaWeRFxa)

## Features

- 🎨 Support for 16 different colors
- 🔤 Support for 8 different font styles (Bold, Italic, Underline, etc.)
- 🚀 Easy to use API
- 📦 Lightweight and dependency-free
- 🐍 Python 3.8+ support

## Installation

```bash
pip install printfxpy
```

## Quick Start

```python
from printfx import PrintFX

# Basic color printing
printer = PrintFX("RED")
printer.printfx("Hello World!")

# With font styles
bold_printer = PrintFX("GREEN", "BOLD")
bold_printer.printfx("Bold text")

# Runtime style changes
printer.printfx("Italic text", font_style="ITALIC")
printer.printfx("Underlined text", font_style="UNDERLINE")
```

## Available Colors

- `BLACK`, `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`, `WHITE`
- `BRIGHT_BLACK`, `BRIGHT_RED`, `BRIGHT_GREEN`, `BRIGHT_YELLOW`, `BRIGHT_BLUE`, `BRIGHT_MAGENTA`, `BRIGHT_CYAN`, `BRIGHT_WHITE`

## Available Font Styles

- `NORMAL` - Default text style
- `BOLD` - Bold text
- `DIM` - Dimmed text
- `ITALIC` - Italic text
- `UNDERLINE` - Underlined text
- `BLINK` - Blinking text
- `REVERSE` - Reversed colors
- `STRIKETHROUGH` - Strikethrough text

## Advanced Usage

```python
from printfx import PrintFX

# Create printer with default settings
printer = PrintFX("BLUE")

# Change color and style at runtime
printer.printfx("Red bold text", color="RED", font_style="BOLD")
printer.printfx("Green underlined text", color="GREEN", font_style="UNDERLINE")

# Combine multiple effects
printer.printfx("Magenta italic text", color="MAGENTA", font_style="ITALIC")
```