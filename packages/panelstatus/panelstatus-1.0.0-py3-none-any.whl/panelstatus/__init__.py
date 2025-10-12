"""
PanelStatus - Dead simple status bar updates for GNOME

Usage:
    from panelstatus import status

    status.set("Processing...")
    status.set("Done!", color="green")
    status.clear()
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from contextlib import contextmanager

__version__ = "1.0.0"
__all__ = ["status", "Status", "install_extension"]


class Status:
    """Simple status bar controller"""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "panelstatus"
        self.status_file = self.config_dir / "status.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Color presets (like ggplot2 themes!)
        self.colors = {
            "red": "#ff6b6b",
            "green": "#51cf66",
            "blue": "#339af0",
            "yellow": "#ffd43b",
            "orange": "#ff922b",
            "purple": "#9775fa",
            "gray": "#adb5bd",
            "white": "#ffffff",
        }

    def set(self, text, color=None):
        """
        Set static status text with optional color

        Args:
            text: Status message to display
            color: Color name or hex code (e.g., "green" or "#00ff00")

        Example:
            status.set("Processing...")
            status.set("Complete!", color="green")
        """
        data = {"mode": "static", "text": text}

        if color:
            # Support color names or hex codes
            data["color"] = self.colors.get(color, color)

        self._write(data)

    def scroll(self, text, color=None, speed=1.0, width=150):
        """
        Set scrolling text (for long messages)

        Args:
            text: Text to scroll
            color: Color name or hex code
            speed: Scroll speed multiplier (1.0 = default, 2.0 = faster)
            width: Display width in pixels (default 150)

        Example:
            status.scroll("This is a long message that scrolls smoothly...")
            status.scroll("Welcome!", color="blue", speed=0.5)
        """
        # Pad text to ensure it always scrolls
        padded_text = text + "     "

        # Calculate scroll parameters
        scroll_speed = int(16 / speed)  # Lower = faster
        pixels_per_frame = 0.5 * speed

        data = {
            "mode": "scroll",
            "text": padded_text,
            "scroll_speed": scroll_speed,
            "pixels_per_frame": pixels_per_frame,
            "width": width,
        }

        if color:
            data["color"] = self.colors.get(color, color)

        self._write(data)

    def clear(self):
        """Remove status from panel"""
        if self.status_file.exists():
            self.status_file.unlink()

    def _write(self, data):
        """Write status data to file"""
        with open(self.status_file, 'w') as f:
            json.dump(data, f)

    @contextmanager
    def show(self, text, color=None):
        """
        Context manager - auto-clears when done

        Example:
            with status.show("Processing..."):
                # do work
                pass
            # Status automatically cleared!
        """
        self.set(text, color)
        try:
            yield self
        finally:
            self.clear()


# Global instance for easy access (like ggplot2's global state)
status = Status()


def install_extension():
    """
    Install the GNOME Shell extension for panelstatus

    This copies the extension files to ~/.local/share/gnome-shell/extensions/
    and enables the extension.

    Example:
        from panelstatus import install_extension
        install_extension()
    """
    # Get the extension files from the package
    extension_dir = Path(__file__).parent / 'gnome_extension'

    # Target directory
    target_dir = Path.home() / ".local/share/gnome-shell/extensions/panelstatus@custom"

    print(f"Installing GNOME extension to {target_dir}...")

    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy files
    for file in extension_dir.glob("*"):
        shutil.copy(file, target_dir / file.name)
        print(f"  ✓ Copied {file.name}")

    print("\nEnabling extension...")

    # Enable the extension
    try:
        subprocess.run(
            ["gnome-extensions", "enable", "panelstatus@custom"],
            check=True,
            capture_output=True,
            text=True
        )
        print("  ✓ Extension enabled")
    except subprocess.CalledProcessError:
        # Extension might not be detected yet, need to restart shell
        print("  ⚠ Extension installed but not enabled yet")
        print("  → Press Alt+F2, type 'r', press Enter to restart GNOME Shell")
        print("  → Then run: gnome-extensions enable panelstatus@custom")
        return False

    print("\n✓ Installation complete!")
    print("\nYou may need to restart GNOME Shell:")
    print("  Press Alt+F2, type 'r', press Enter")
    print("\nThen test it:")
    print("  from panelstatus import status")
    print("  status.set('Hello!', color='green')")

    return True
