# PanelStatus 📊

**Dead simple GNOME panel status updates** - Inspired by ggplot2's ease of use

Display static text, scrolling messages, and more in your GNOME top panel with just one line of Python!

## Installation

```python
from panelstatus import install_extension, restart_shell

# Install the GNOME extension
install_extension()

# Restart GNOME Shell automatically
restart_shell()
```

Or use the command line:
```bash
pip install panelstatus
python3 -c "from panelstatus import install_extension, restart_shell; install_extension(); restart_shell()"
```

## Features

✨ **Static text** - Show status messages
🎬 **Smooth scrolling** - Perfect for long messages
🎨 **Colors** - Named colors or custom hex codes
⚡ **Fast** - Minimal overhead, smooth 60fps animations
🐍 **Pythonic** - Simple, intuitive API
📦 **Self-installing** - Extension installs with one function call!
🔀 **Multi-process** - Multiple apps can display simultaneously with automatic space allocation

## Quick Start

```python
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

### Log Feed (Streaming Logs)

```python
# Perfect for continuous log updates!
status.feed("Server started")
status.feed("Connected to database")
status.feed("Ready on port 8080")

# Shows: "Server started | Connected to database | Ready on port 8080" (scrolling)

# Customize separator and buffer size
status.feed("Log line", max_lines=10, separator=" • ")
```

### Progressive Append (Smart Scrolling)

```python
# Accumulates text, stays static until too long, then scrolls to end
status.append("Starting...")
status.append("Step 1 complete")
status.append("Step 2 complete")
status.append("All done!")

# Three scrolling modes:

# 1. INSTANT - Jump immediately to new content (best for alerts)
status.append("Error occurred!", scroll_mode="instant", color="red")

# 2. SMOOTH - Zen-like constant scrolling (default, best for ambience)
status.append("Processing...", scroll_mode="smooth", scroll_speed=0.5)

# 3. ADAPTIVE - Speed up when behind, slow down when caught up
#              (best for progress tracking)
status.append("Task complete", scroll_mode="adaptive",
              scroll_min=0.5, scroll_max=4.0, color="green")
```

**Choosing the right scroll mode:**

| Mode | Behavior | Best For | Example Use Case |
|------|----------|----------|------------------|
| `instant` | Jumps immediately to new content | Real-time alerts, monitoring | Error notifications, system alerts |
| `smooth` | Constant zen-like scrolling | Ambient displays, background processes | Build progress, server status |
| `adaptive` | Speeds up when behind, slows when caught up | Progress tracking, log streaming | Test results, batch processing |

### Context Manager (Auto-clear)

```python
with status.show("Working...", color="blue"):
    # Your code here
    do_something()
# Status automatically cleared!
```

### Multi-Process Support

Multiple applications can display status simultaneously with automatic space allocation:

```python
# Process 1: Build system
build_status = Status(id="build")
build_status.set_weight(2.0)  # Gets 2x space
build_status.append("Compiling...", color="blue")

# Process 2: Test runner
test_status = Status(id="tests")
test_status.set_weight(1.0)  # Default weight
test_status.append("Running tests...", color="green")

# They appear side-by-side: [Compiling...] [Running tests...]
```

**Space Allocation:**
- Extension uses max 40% of panel width by default
- Space divided among processes based on weights
- Automatic cleanup after 30s of inactivity
- Dynamic reallocation when processes start/stop

## API Reference

### `Status(id=None)`
Create a status controller instance.

**Args:**
- `id` (str, optional): Unique process identifier for multi-process support. If None (default), uses singleton mode.

**Example:**
```python
# Single process (default)
from panelstatus import status
status.set("Working...")

# Multi-process
build = Status(id="build")
tests = Status(id="tests")
```

### `set_weight(weight)`
Set space allocation weight for multi-process display.

**Args:**
- `weight` (float): Space allocation multiplier (default 1.0). Higher = more space.

**Example:**
```python
build_status = Status(id="build")
build_status.set_weight(2.0)  # Gets 2x space
```

### `install_extension()`
Install the GNOME Shell extension (one-time setup).

```python
from panelstatus import install_extension
install_extension()
```

### `restart_shell()`
Restart GNOME Shell to reload extensions (X11 only).

```python
from panelstatus import restart_shell
restart_shell()
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

### `status.feed(text, color=None, max_lines=5, separator=" | ", speed=1.0, width=200)`
Add text to a rolling log feed.

**Args:**
- `text` (str): Log line to add
- `color` (str, optional): Color name or hex code
- `max_lines` (int, optional): Buffer size (default 5)
- `separator` (str, optional): Text between lines (default " | ")
- `speed` (float, optional): Scroll speed multiplier
- `width` (int, optional): Display width in pixels

### `status.append(text, color=None, separator=" ", width=300, scroll_mode="smooth", scroll_speed=1.0, scroll_min=0.3, scroll_max=3.0)`
Append text progressively with configurable scrolling behavior.

Text stays static until it exceeds the panel width, then scrolls to the end and stops. Adding more text resumes scrolling.

**Args:**
- `text` (str): Text to append
- `color` (str, optional): Color name or hex code
- `separator` (str, optional): Text between appends (default " ")
- `width` (int, optional): Display width in pixels (default 300)
- `scroll_mode` (str, optional): Scrolling behavior - "instant", "smooth", or "adaptive" (default "smooth")
- `scroll_speed` (float, optional): Speed multiplier for smooth mode (default 1.0)
- `scroll_min` (float, optional): Minimum speed for adaptive mode (default 0.3)
- `scroll_max` (float, optional): Maximum speed for adaptive mode (default 3.0)

**Scroll Modes:**
- `"instant"`: Jump immediately to show new content (best for real-time alerts)
- `"smooth"`: Constant zen-like scrolling (best for ambient displays)
- `"adaptive"`: Variable speed - accelerates when far behind, slows when caught up (best for progress tracking)

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
