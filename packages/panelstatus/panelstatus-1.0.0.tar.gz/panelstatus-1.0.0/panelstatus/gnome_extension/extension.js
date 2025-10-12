const { St, GLib, Gio, Clutter } = imports.gi;
const Main = imports.ui.main;

let panelButton;
let container;
let pollTimeoutId;
let animTimeoutId;

// State
let currentMode = null;

// Scroll state
let scrollPosition = 0;
let label1, label2, scrollBox;
// Static state
let staticLabel;

const STATUS_FILE = GLib.get_home_dir() + '/.config/panelstatus/status.json';
const POLL_INTERVAL = 500;

function scrollText() {
    if (!label1 || !label2) {
        return GLib.SOURCE_REMOVE;
    }

    scrollPosition += 0.5;

    let labelWidth = label1.width;
    if (labelWidth > 0 && scrollPosition >= labelWidth) {
        scrollPosition = 0;
    }

    label1.set_translation(-scrollPosition, 0, 0);
    label2.set_translation(-scrollPosition, 0, 0);

    return GLib.SOURCE_CONTINUE;
}

function buildScrollDisplay(text, color, scrollSpeed, pixelsPerFrame, width) {
    clearDisplay();
    currentMode = 'scroll';

    scrollBox = new St.BoxLayout({
        clip_to_allocation: true,
        width: width || 150,
    });

    label1 = new St.Label({
        text: text,
        y_align: Clutter.ActorAlign.CENTER,
    });

    label2 = new St.Label({
        text: text,
        y_align: Clutter.ActorAlign.CENTER,
    });

    if (color) {
        label1.style = `color: ${color};`;
        label2.style = `color: ${color};`;
    }

    scrollBox.add_child(label1);
    scrollBox.add_child(label2);
    container.add_child(scrollBox);

    animTimeoutId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, scrollSpeed || 16, scrollText);
}

function buildStaticDisplay(text, color) {
    clearDisplay();
    currentMode = 'static';

    staticLabel = new St.Label({
        text: text || '',
        y_align: Clutter.ActorAlign.CENTER,
    });

    if (color) {
        staticLabel.style = `color: ${color};`;
    }

    container.add_child(staticLabel);
}

function clearDisplay() {
    if (animTimeoutId) {
        GLib.source_remove(animTimeoutId);
        animTimeoutId = null;
    }

    if (container) {
        container.destroy_all_children();
    }

    label1 = null;
    label2 = null;
    scrollBox = null;
    staticLabel = null;
    scrollPosition = 0;
}

function readStatus() {
    try {
        let file = Gio.File.new_for_path(STATUS_FILE);

        if (!file.query_exists(null)) {
            if (currentMode !== null) {
                clearDisplay();
                currentMode = null;
            }
            return GLib.SOURCE_CONTINUE;
        }

        let [success, contents] = file.load_contents(null);
        if (!success) {
            return GLib.SOURCE_CONTINUE;
        }

        let data = JSON.parse(imports.byteArray.toString(contents));
        let mode = data.mode || 'static';

        // Always rebuild when mode changes
        if (mode !== currentMode) {
            if (mode === 'scroll') {
                buildScrollDisplay(
                    data.text || '',
                    data.color || null,
                    data.scroll_speed || 16,
                    data.pixels_per_frame || 0.5,
                    data.width || 150
                );
            } else {
                buildStaticDisplay(data.text || '', data.color || null);
            }
        }

    } catch (e) {
        // Silent
    }

    return GLib.SOURCE_CONTINUE;
}

function init() {
}

function enable() {
    panelButton = new St.Bin({
        style_class: 'panel-button',
    });

    container = new St.BoxLayout({
        y_align: Clutter.ActorAlign.CENTER,
    });

    panelButton.set_child(container);
    Main.panel._rightBox.insert_child_at_index(panelButton, 0);

    pollTimeoutId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, POLL_INTERVAL, readStatus);
    readStatus();
}

function disable() {
    clearDisplay();

    if (pollTimeoutId) {
        GLib.source_remove(pollTimeoutId);
        pollTimeoutId = null;
    }

    if (panelButton) {
        Main.panel._rightBox.remove_child(panelButton);
        panelButton.destroy();
        panelButton = null;
    }

    container = null;
    currentMode = null;
}
