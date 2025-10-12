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

__version__ = "1.1.0"
__all__ = ["status", "Status", "install_extension", "restart_shell"]


class Status:
    """Simple status bar controller"""

    def __init__(self, id=None):
        """
        Initialize status controller

        Args:
            id: Unique identifier for this process (default: None, uses singleton)
                If specified, allows multiple processes to display simultaneously

        Example:
            # Single process (default)
            status = Status()

            # Multi-process
            build_status = Status(id="build")
            test_status = Status(id="tests")
        """
        self.config_dir = Path.home() / ".config" / "panelstatus"
        self.process_id = id

        if id:
            self.status_file = self.config_dir / f"status-{id}.json"
        else:
            self.status_file = self.config_dir / "status.json"

        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Process-specific settings
        self._weight = 1.0  # Space allocation weight

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

        # Feed buffer for log streaming
        self._feed_buffer = []
        self._feed_max_lines = 5
        self._feed_separator = " | "

        # Append buffer for progressive text
        self._append_buffer = ""
        self._append_separator = " "

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

    def scroll(self, text, color=None, speed=1.0, width=None):
        """
        Set scrolling text (for long messages)

        Args:
            text: Text to scroll
            color: Color name or hex code
            speed: Scroll speed multiplier (1.0 = default, 2.0 = faster)
            width: Display width in pixels (default: auto, ~600px)
                   Set larger if text gets truncated

        Example:
            status.scroll("This is a long message that scrolls smoothly...")
            status.scroll("Welcome!", color="blue", speed=0.5)

            # For very long text, increase width
            status.scroll("Very long text...", width=800)
        """
        # Pad text to ensure it always scrolls
        padded_text = text + "     "

        # Calculate scroll parameters
        scroll_speed = int(16 / speed)  # Lower = faster
        pixels_per_frame = 0.5 * speed

        # Auto-size width if not specified (generous default)
        if width is None:
            # Estimate ~8 pixels per character, minimum 400px
            # No maximum - viewport grows with text to prevent truncation
            estimated_width = max(400, len(text) * 8)
            width = estimated_width

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
        self._feed_buffer = []
        self._append_buffer = ""

    def feed(self, text, color=None, max_lines=None, separator=None, speed=1.0, width=None):
        """
        Add text to a rolling feed (perfect for logs!)

        Each call appends a new line to the feed. The feed maintains
        the last N lines and scrolls them continuously.

        Args:
            text: New line to add to the feed
            color: Color name or hex code
            max_lines: Maximum lines to keep in buffer (default 5)
            separator: String between lines (default " | ")
            speed: Scroll speed multiplier (default 1.0)
            width: Display width in pixels (default: auto-sized)

        Example:
            # Stream logs
            status.feed("Starting server...")
            status.feed("Connected to database")
            status.feed("Server ready on port 8080")

            # The panel shows: "Starting server... | Connected to database | Server ready on port 8080"
        """
        # Add to buffer
        self._feed_buffer.append(str(text))

        # Trim to max lines
        max_lines = max_lines or self._feed_max_lines
        if len(self._feed_buffer) > max_lines:
            self._feed_buffer = self._feed_buffer[-max_lines:]

        # Join and scroll
        separator = separator or self._feed_separator
        feed_text = separator.join(self._feed_buffer)

        self.scroll(feed_text, color=color, speed=speed, width=width)

    def append(self, text, color=None, separator=None, width=None,
               scroll_mode="smooth", scroll_speed=1.0, scroll_min=0.3, scroll_max=3.0):
        """
        Append text progressively with configurable scrolling behavior

        Text stays static until it exceeds the panel width, then scrolls
        to the end and stops. Adding more text resumes scrolling.

        Args:
            text: Text to append
            color: Color name or hex code
            separator: String between appends (default " ")
            width: Display width in pixels (default 300)
            scroll_mode: Scrolling behavior (default "smooth")
                - "instant": Jump immediately to new content
                - "smooth": Constant zen-like scrolling (current default)
                - "adaptive": Accelerate when far behind, slow when caught up
            scroll_speed: Speed multiplier for "smooth" mode (default 1.0)
            scroll_min: Minimum speed for "adaptive" mode (default 0.3)
            scroll_max: Maximum speed for "adaptive" mode (default 3.0)

        Examples:
            # Zen-like smooth scrolling (default)
            status.append("Task complete", scroll_mode="smooth", scroll_speed=0.5)

            # Instant jump to new content
            status.append("Error!", scroll_mode="instant")

            # Adaptive: speeds up when behind, slows down when caught up
            status.append("Processing...", scroll_mode="adaptive",
                         scroll_min=0.5, scroll_max=5.0)
        """
        # Add to buffer
        separator = separator or self._append_separator
        if self._append_buffer:
            self._append_buffer += separator + str(text)
        else:
            self._append_buffer = str(text)

        # Send to extension
        data = {
            "mode": "append",
            "text": self._append_buffer,
            "width": width or 300,
            "scroll_mode": scroll_mode,
            "scroll_speed": scroll_speed,
            "scroll_min": scroll_min,
            "scroll_max": scroll_max,
        }

        if color:
            data["color"] = self.colors.get(color, color)

        self._write(data)

    def set_weight(self, weight):
        """
        Set space allocation weight for multi-process display

        Higher weight = more panel space. Default is 1.0.

        Args:
            weight: Space weight (e.g., 2.0 = double space, 0.5 = half space)

        Example:
            build_status = Status(id="build")
            build_status.set_weight(2.0)  # Gets 2x space of other processes
        """
        self._weight = max(0.1, float(weight))

    def _write(self, data):
        """Write status data to file with metadata"""
        import time

        # Add metadata
        data['_meta'] = {
            'weight': self._weight,
            'timestamp': time.time(),
            'process_id': self.process_id or 'default'
        }

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
    print("\nRestart GNOME Shell to activate:")
    print("  from panelstatus import restart_shell")
    print("  restart_shell()")
    print("\nThen test it:")
    print("  from panelstatus import status")
    print("  status.set('Hello!', color='green')")

    return True


def restart_shell():
    """
    Restart GNOME Shell to reload extensions

    This is necessary after installing or updating the extension.
    Works on X11 (restarts shell) and Wayland (shows instructions).

    Example:
        from panelstatus import install_extension, restart_shell
        install_extension()
        restart_shell()
    """
    # Check session type
    session_type = os.environ.get("XDG_SESSION_TYPE", "").lower()

    if session_type == "x11":
        print("Restarting GNOME Shell (X11)...")
        try:
            subprocess.run(
                ["killall", "-SIGQUIT", "gnome-shell"],
                check=True,
                capture_output=True
            )
            print("✓ GNOME Shell restarted!")
            print("  Wait 3-5 seconds for it to reload...")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠ Could not restart shell: {e}")
            print("  Manually: Press Alt+F2, type 'r', press Enter")
            return False
    elif session_type == "wayland":
        print("GNOME Shell restart on Wayland:")
        print("  → Log out and log back in")
        print("  (Wayland doesn't support in-session restarts)")
        return False
    else:
        print("Could not detect session type")
        print("  Try: Press Alt+F2, type 'r', press Enter")
        return False
