# PanelStatus 📊

**Dead simple GNOME panel status updates** - Inspired by ggplot2's ease of use

Display static text, scrolling messages, and more in your GNOME top panel with just one line of Python!

## Installation

```python
# From the library directory
import sys
sys.path.insert(0, '/home/maxime/panelstatus-lib')
from panelstatus import install_extension

# Install the GNOME extension
install_extension()

# Restart GNOME Shell (Alt+F2, type 'r', press Enter)
```

Or use the command line:
```bash
cd ~/panelstatus-lib
python3 -c "from panelstatus import install_extension; install_extension()"
```

## Features

✨ **Static text** - Show status messages
🎬 **Smooth scrolling** - Perfect for long messages
🎨 **Colors** - Named colors or custom hex codes
⚡ **Fast** - Minimal overhead, smooth 60fps animations
🐍 **Pythonic** - Simple, intuitive API
📦 **Self-installing** - Extension installs with one function call!

## Quick Start

```python
import sys
sys.path.insert(0, '/home/maxime/panelstatus-lib')
from panelstatus import status

# Static text
status.set("Processing...", color="blue")

# Scrolling text
status.scroll("This is a long message that scrolls smoothly!")

# Clear
status.clear()
```

## Usage

### Basic Static Status

```python
from panelstatus import status

status.set("Processing...")
status.set("Done!", color="green")
status.clear()
```

### Scrolling Text

```python
# For long messages
status.scroll("This is a long message that scrolls smoothly across your panel! ")

# With color
status.scroll("Welcome to my app!", color="blue")

# Control speed (1.0 = default, 2.0 = 2x faster, 0.5 = slower)
status.scroll("Slow scroll...", speed=0.5)
status.scroll("Fast scroll!", speed=2.0)

# Adjust display width
status.scroll("Custom width", width=200)
```

### Switch Between Modes

```python
import time

status.set("Starting task...", color="yellow")
time.sleep(2)

status.scroll("Processing lots of data... this might take a while...")
time.sleep(5)

status.set("Complete!", color="green")
```

### Colors

**Named colors:**
- `red`, `green`, `blue`
- `yellow`, `orange`, `purple`
- `gray`, `white`

**Custom hex codes:**
```python
status.set("Custom", color="#ff00ff")
```

### Context Manager (Auto-clear)

```python
with status.show("Working...", color="blue"):
    # Your code here
    do_something()
# Status automatically cleared!
```

## API Reference

### `install_extension()`
Install the GNOME Shell extension (one-time setup).

```python
from panelstatus import install_extension
install_extension()
```

### `status.set(text, color=None)`
Display static text in the panel.

**Args:**
- `text` (str): Message to display
- `color` (str, optional): Color name or hex code

### `status.scroll(text, color=None, speed=1.0, width=150)`
Display scrolling text (perfect for long messages).

**Args:**
- `text` (str): Message to scroll
- `color` (str, optional): Color name or hex code
- `speed` (float, optional): Scroll speed multiplier (default 1.0)
- `width` (int, optional): Display width in pixels (default 150)

### `status.clear()`
Remove status from panel.

### `status.show(text, color=None)`
Context manager that auto-clears when done.

## Real-World Examples

**Long-running task:**
```python
from panelstatus import status
import requests

status.scroll("Downloading data from API... ")
data = requests.get("https://api.example.com/data").json()

status.set("Processing...", color="yellow")
results = process(data)

status.set("Complete! ✓", color="green")
```

**Build script:**
```python
status.set("Building...", color="blue")
os.system("npm run build")
status.set("Build complete!", color="green")
```

**Training progress:**
```python
for epoch in range(100):
    status.scroll(f"Training epoch {epoch}/100... ", color="orange")
    train_model(epoch)

status.set("Training complete!", color="green")
```

## Philosophy

Like **ggplot2 made plotting simple**, PanelStatus makes status updates trivial:

- ✅ **Simple API** - Just `status.set()` or `status.scroll()` and go
- ✅ **Sensible defaults** - Works beautifully out of the box
- ✅ **Minimal boilerplate** - No complex setup or configuration
- ✅ **Pythonic** - Feels natural and intuitive
- ✅ **Versatile** - Static text, scrolling, colors, auto-clear
- ✅ **Self-contained** - Extension bundles with the library

## Try the Demo

Run the example to see all features:
```bash
python3 ~/panelstatus-lib/example.py
```

Watch your panel for static messages, smooth scrolling, and color changes!

---

**Enjoy simple status updates!** 🎉
