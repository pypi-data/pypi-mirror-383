const { St, GLib, Gio, Clutter } = imports.gi;
const Main = imports.ui.main;

// Multi-process support
let processWidgets = new Map();  // processId -> widget info
let mainContainer;
let pollTimeoutId;

const STATUS_DIR = GLib.get_home_dir() + '/.config/panelstatus';
const POLL_INTERVAL = 500;
const STALE_TIMEOUT = 30;  // Remove process if no update for 30 seconds
const MAX_PANEL_PERCENT = 0.40;  // Use max 40% of panel width

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function scanStatusFiles() {
    let files = [];
    try {
        let dir = Gio.File.new_for_path(STATUS_DIR);
        if (!dir.query_exists(null)) {
            return files;
        }

        let enumerator = dir.enumerate_children(
            'standard::name',
            Gio.FileQueryInfoFlags.NONE,
            null
        );

        let info;
        while ((info = enumerator.next_file(null))) {
            let name = info.get_name();
            // Match status.json or status-*.json
            if (name === 'status.json' || name.match(/^status-.*\.json$/)) {
                let processId = 'default';
                if (name !== 'status.json') {
                    processId = name.replace(/^status-/, '').replace(/\.json$/, '');
                }
                files.push({
                    path: STATUS_DIR + '/' + name,
                    processId: processId
                });
            }
        }
    } catch (e) {
        // Silent
    }

    return files;
}

function getAvailableWidth() {
    // Simple, safe approach: use a fixed maximum width
    // This avoids race conditions with measuring other widgets during layout
    // 400px is reasonable for status text without pushing indicators off-screen
    return 400;
}

function allocateWidths(processes) {
    let totalWeight = 0;
    let activeProcesses = [];

    // Calculate total weight
    for (let [processId, info] of processes.entries()) {
        totalWeight += info.weight;
        activeProcesses.push({id: processId, weight: info.weight});
    }

    if (totalWeight === 0 || activeProcesses.length === 0) {
        return new Map();
    }

    let availableWidth = getAvailableWidth();
    let allocations = new Map();

    // Distribute width based on weights
    for (let proc of activeProcesses) {
        let width = Math.floor((proc.weight / totalWeight) * availableWidth);
        allocations.set(proc.id, Math.max(100, width));  // Min 100px per process
    }

    return allocations;
}

// ============================================================================
// ANIMATION FUNCTIONS (per-process)
// ============================================================================

function createScrollAnimation(widgetInfo) {
    return function() {
        if (!widgetInfo.label1 || !widgetInfo.label2) {
            return GLib.SOURCE_REMOVE;
        }

        widgetInfo.scrollPosition = (widgetInfo.scrollPosition || 0) + 0.5;

        let labelWidth = widgetInfo.label1.width;
        if (labelWidth > 0 && widgetInfo.scrollPosition >= labelWidth) {
            widgetInfo.scrollPosition = 0;
        }

        widgetInfo.label1.set_translation(-widgetInfo.scrollPosition, 0, 0);
        widgetInfo.label2.set_translation(-widgetInfo.scrollPosition, 0, 0);

        return GLib.SOURCE_CONTINUE;
    };
}

function createProgressiveScrollAnimation(widgetInfo) {
    return function() {
        if (!widgetInfo.appendLabel || widgetInfo.appendAtEnd) {
            return GLib.SOURCE_REMOVE;
        }

        let distance = widgetInfo.appendMaxScroll - widgetInfo.appendScrollPos;
        let speed = 0.5;

        // Apply scrolling mode
        if (widgetInfo.appendScrollMode === 'instant') {
            widgetInfo.appendScrollPos = widgetInfo.appendMaxScroll;
            widgetInfo.appendAtEnd = true;
            widgetInfo.appendLabel.set_translation(-widgetInfo.appendScrollPos, 0, 0);
            return GLib.SOURCE_REMOVE;
        } else if (widgetInfo.appendScrollMode === 'smooth') {
            speed = 0.5 * (widgetInfo.appendScrollSpeed || 1.0);
        } else if (widgetInfo.appendScrollMode === 'adaptive') {
            let normalizedDistance = Math.min(distance / 200.0, 1.0);
            let minSpeed = widgetInfo.appendScrollMin || 0.3;
            let maxSpeed = widgetInfo.appendScrollMax || 3.0;
            speed = minSpeed + (maxSpeed - minSpeed) * normalizedDistance;
        }

        widgetInfo.appendScrollPos += speed;

        if (widgetInfo.appendScrollPos >= widgetInfo.appendMaxScroll) {
            widgetInfo.appendScrollPos = widgetInfo.appendMaxScroll;
            widgetInfo.appendAtEnd = true;
            widgetInfo.appendLabel.set_translation(-widgetInfo.appendScrollPos, 0, 0);
            return GLib.SOURCE_REMOVE;
        }

        widgetInfo.appendLabel.set_translation(-widgetInfo.appendScrollPos, 0, 0);
        return GLib.SOURCE_CONTINUE;
    };
}

// ============================================================================
// WIDGET CREATION (per-process)
// ============================================================================

function createProcessWidget(processId, data, allocatedWidth) {
    let widgetInfo = processWidgets.get(processId);

    if (!widgetInfo) {
        // Create new widget container with strict constraints
        widgetInfo = {
            processId: processId,
            container: new St.BoxLayout({
                style_class: 'panel-button',
                y_align: Clutter.ActorAlign.CENTER,
                clip_to_allocation: true,
                style: `width: ${allocatedWidth}px; max-width: ${allocatedWidth}px;`,
                x_expand: false,
            }),
            mode: null,
            dataHash: null,
            weight: 1.0,
            allocatedWidth: allocatedWidth
        };
        processWidgets.set(processId, widgetInfo);
        mainContainer.add_child(widgetInfo.container);
    } else {
        // Update container width with CSS
        widgetInfo.container.style = `width: ${allocatedWidth}px; max-width: ${allocatedWidth}px;`;
        widgetInfo.allocatedWidth = allocatedWidth;
    }

    // Update metadata
    if (data._meta) {
        widgetInfo.weight = data._meta.weight || 1.0;
        widgetInfo.lastUpdate = data._meta.timestamp || (Date.now() / 1000);
    }

    let mode = data.mode || 'static';
    let dataHash = JSON.stringify(data);

    // Check if rebuild needed
    if (mode === widgetInfo.mode && dataHash === widgetInfo.dataHash) {
        // Just update width if changed
        updateWidgetWidth(widgetInfo, allocatedWidth);
        return;
    }

    widgetInfo.mode = mode;
    widgetInfo.dataHash = dataHash;

    // Clear old content
    clearProcessWidget(widgetInfo);

    // Build based on mode
    if (mode === 'scroll') {
        buildScrollDisplay(widgetInfo, data, allocatedWidth);
    } else if (mode === 'append') {
        buildAppendDisplay(widgetInfo, data, allocatedWidth);
    } else {
        buildStaticDisplay(widgetInfo, data, allocatedWidth);
    }
}

function clearProcessWidget(widgetInfo) {
    if (widgetInfo.animTimeoutId) {
        GLib.source_remove(widgetInfo.animTimeoutId);
        widgetInfo.animTimeoutId = null;
    }

    if (widgetInfo.container) {
        widgetInfo.container.destroy_all_children();
    }

    // Clear widget references
    widgetInfo.label1 = null;
    widgetInfo.label2 = null;
    widgetInfo.scrollBox = null;
    widgetInfo.staticLabel = null;
    widgetInfo.appendLabel = null;
    widgetInfo.appendBox = null;
    widgetInfo.scrollPosition = 0;
}

function updateWidgetWidth(widgetInfo, width) {
    // Update container width with CSS
    if (widgetInfo.container) {
        widgetInfo.container.style = `width: ${width}px; max-width: ${width}px;`;
    }

    // Update inner box widths with CSS
    if (widgetInfo.scrollBox) {
        widgetInfo.scrollBox.style = `width: ${width}px; max-width: ${width}px;`;
    } else if (widgetInfo.appendBox) {
        widgetInfo.appendBox.style = `width: ${width}px; max-width: ${width}px;`;
    }
}

function buildStaticDisplay(widgetInfo, data, width) {
    let style = `max-width: ${width}px;`;

    if (data.color) {
        style += ` color: ${data.color};`;
    }

    widgetInfo.staticLabel = new St.Label({
        text: data.text || '',
        y_align: Clutter.ActorAlign.CENTER,
        style: style
    });
    widgetInfo.staticLabel.clutter_text.ellipsize = 0;  // No ellipsis

    widgetInfo.container.add_child(widgetInfo.staticLabel);
}

function buildScrollDisplay(widgetInfo, data, width) {
    // Constrain to allocated width to prevent overflow
    let boxWidth = Math.min(data.width || width, width);

    widgetInfo.scrollBox = new St.BoxLayout({
        clip_to_allocation: true,
        style: `width: ${boxWidth}px; max-width: ${boxWidth}px;`,
    });

    // Create labels with explicit width constraint
    widgetInfo.label1 = new St.Label({
        text: data.text || '',
        y_align: Clutter.ActorAlign.CENTER,
        style: `max-width: ${boxWidth * 3}px;`,  // Allow 3x for scrolling
    });
    widgetInfo.label1.clutter_text.ellipsize = 0;

    widgetInfo.label2 = new St.Label({
        text: data.text || '',
        y_align: Clutter.ActorAlign.CENTER,
        style: `max-width: ${boxWidth * 3}px;`,  // Allow 3x for scrolling
    });
    widgetInfo.label2.clutter_text.ellipsize = 0;

    if (data.color) {
        widgetInfo.label1.style = `max-width: ${boxWidth * 3}px; color: ${data.color};`;
        widgetInfo.label2.style = `max-width: ${boxWidth * 3}px; color: ${data.color};`;
    }

    widgetInfo.scrollBox.add_child(widgetInfo.label1);
    widgetInfo.scrollBox.add_child(widgetInfo.label2);
    widgetInfo.container.add_child(widgetInfo.scrollBox);

    widgetInfo.scrollPosition = 0;
    widgetInfo.animTimeoutId = GLib.timeout_add(
        GLib.PRIORITY_DEFAULT,
        data.scroll_speed || 16,
        createScrollAnimation(widgetInfo)
    );
}

function buildAppendDisplay(widgetInfo, data, width) {
    let wasAtEnd = widgetInfo.appendAtEnd;
    let oldScrollPos = widgetInfo.appendScrollPos || 0;

    // Store scroll parameters
    widgetInfo.appendScrollMode = data.scroll_mode || 'smooth';
    widgetInfo.appendScrollSpeed = data.scroll_speed || 1.0;
    widgetInfo.appendScrollMin = data.scroll_min || 0.3;
    widgetInfo.appendScrollMax = data.scroll_max || 3.0;

    // Constrain to allocated width to prevent overflow
    let boxWidth = Math.min(data.width || width, width);

    widgetInfo.appendBox = new St.BoxLayout({
        clip_to_allocation: true,
        style: `width: ${boxWidth}px; max-width: ${boxWidth}px;`,
    });

    let labelStyle = `max-width: ${boxWidth * 3}px;`;
    if (data.color) {
        labelStyle += ` color: ${data.color};`;
    }

    widgetInfo.appendLabel = new St.Label({
        text: data.text || '',
        y_align: Clutter.ActorAlign.CENTER,
        style: labelStyle,
    });
    widgetInfo.appendLabel.clutter_text.ellipsize = 0;

    widgetInfo.appendBox.add_child(widgetInfo.appendLabel);
    widgetInfo.container.add_child(widgetInfo.appendBox);

    // Wait for layout
    GLib.idle_add(GLib.PRIORITY_DEFAULT, () => {
        let labelWidth = widgetInfo.appendLabel.width;
        let boxWidth = widgetInfo.appendBox.width;

        widgetInfo.appendMaxScroll = Math.max(0, labelWidth - boxWidth);

        if (widgetInfo.appendMaxScroll === 0) {
            widgetInfo.appendScrollPos = 0;
            widgetInfo.appendAtEnd = true;
        } else {
            if (wasAtEnd || oldScrollPos >= widgetInfo.appendMaxScroll) {
                widgetInfo.appendScrollPos = oldScrollPos;
                widgetInfo.appendAtEnd = false;
                widgetInfo.animTimeoutId = GLib.timeout_add(
                    GLib.PRIORITY_DEFAULT,
                    16,
                    createProgressiveScrollAnimation(widgetInfo)
                );
            } else {
                widgetInfo.appendScrollPos = Math.min(oldScrollPos, widgetInfo.appendMaxScroll);
                if (widgetInfo.appendScrollPos >= widgetInfo.appendMaxScroll) {
                    widgetInfo.appendAtEnd = true;
                } else {
                    widgetInfo.appendAtEnd = false;
                    widgetInfo.animTimeoutId = GLib.timeout_add(
                        GLib.PRIORITY_DEFAULT,
                        16,
                        createProgressiveScrollAnimation(widgetInfo)
                    );
                }
            }
            widgetInfo.appendLabel.set_translation(-widgetInfo.appendScrollPos, 0, 0);
        }

        return GLib.SOURCE_REMOVE;
    });
}

// ============================================================================
// MAIN POLLING LOOP
// ============================================================================

function updateAllProcesses() {
    try {
        let currentTime = Date.now() / 1000;
        let statusFiles = scanStatusFiles();
        let activeProcesses = new Map();

        // Read all status files
        for (let fileInfo of statusFiles) {
            try {
                let file = Gio.File.new_for_path(fileInfo.path);
                if (!file.query_exists(null)) {
                    continue;
                }

                let [success, contents] = file.load_contents(null);
                if (!success) {
                    continue;
                }

                let data = JSON.parse(imports.byteArray.toString(contents));

                // Check if stale
                let timestamp = data._meta ? data._meta.timestamp : currentTime;
                if (currentTime - timestamp > STALE_TIMEOUT) {
                    continue;  // Skip stale processes
                }

                activeProcesses.set(fileInfo.processId, {
                    data: data,
                    weight: data._meta ? data._meta.weight : 1.0
                });
            } catch (e) {
                // Skip this file
            }
        }

        // Remove stale widgets
        for (let processId of processWidgets.keys()) {
            if (!activeProcesses.has(processId)) {
                let widgetInfo = processWidgets.get(processId);
                clearProcessWidget(widgetInfo);
                if (widgetInfo.container) {
                    mainContainer.remove_child(widgetInfo.container);
                    widgetInfo.container.destroy();
                }
                processWidgets.delete(processId);
            }
        }

        // Allocate space
        let allocations = allocateWidths(activeProcesses);

        // Update/create widgets
        for (let [processId, processData] of activeProcesses.entries()) {
            let allocatedWidth = allocations.get(processId) || 150;
            createProcessWidget(processId, processData.data, allocatedWidth);
        }

        // Update main container width based on active processes
        if (activeProcesses.size > 0) {
            let maxWidth = getAvailableWidth();
            if (mainContainer) {
                mainContainer.style = `width: ${maxWidth}px; max-width: ${maxWidth}px;`;
            }
        } else {
            // No active processes, collapse to 0 width
            if (mainContainer) {
                mainContainer.style = `width: 0px; max-width: 0px;`;
            }
        }

    } catch (e) {
        // Silent
    }

    return GLib.SOURCE_CONTINUE;
}

// ============================================================================
// EXTENSION LIFECYCLE
// ============================================================================

function init() {
}

function enable() {
    mainContainer = new St.BoxLayout({
        style_class: 'panel-button',
        y_align: Clutter.ActorAlign.CENTER,
        x_expand: false,
        clip_to_allocation: true,
        style: 'width: 0px; max-width: 0px;',  // Start with 0 width
    });

    Main.panel._rightBox.insert_child_at_index(mainContainer, 0);

    pollTimeoutId = GLib.timeout_add(GLib.PRIORITY_DEFAULT, POLL_INTERVAL, updateAllProcesses);
    updateAllProcesses();
}

function disable() {
    // Clean up all process widgets
    for (let widgetInfo of processWidgets.values()) {
        clearProcessWidget(widgetInfo);
        if (widgetInfo.container) {
            widgetInfo.container.destroy();
        }
    }
    processWidgets.clear();

    if (pollTimeoutId) {
        GLib.source_remove(pollTimeoutId);
        pollTimeoutId = null;
    }

    if (mainContainer) {
        Main.panel._rightBox.remove_child(mainContainer);
        mainContainer.destroy();
        mainContainer = null;
    }
}
