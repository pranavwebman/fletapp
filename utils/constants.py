# Constants for ESP Control Hub

APP_NAME = "ESP Control Hub"
APP_VERSION = "1.0.0"

# Color Palette for Controls
COLOR_PALETTE = [
    {"name": "Blue", "hex": "#2196F3"},
    {"name": "Purple", "hex": "#9C27B0"},
    {"name": "Green", "hex": "#4CAF50"},
    {"name": "Orange", "hex": "#FF9800"},
    {"name": "Red", "hex": "#F44336"},
    {"name": "Pink", "hex": "#E91E63"},
    {"name": "Teal", "hex": "#009688"},
    {"name": "Yellow", "hex": "#FFC107"},
    {"name": "Cyan", "hex": "#00BCD4"},
    {"name": "Indigo", "hex": "#3F51B5"},
    {"name": "Deep Orange", "hex": "#FF5722"},
    {"name": "Amber", "hex": "#FFC107"}
]

# Preset Categories
DEFAULT_CATEGORIES = [
    {"id": "all", "name": "All", "icon": "grid_view", "order": 0},
    {"id": "bedroom", "name": "Bedroom", "icon": "bed", "order": 1},
    {"id": "living_room", "name": "Living Room", "icon": "weekend", "order": 2},
    {"id": "workshop", "name": "Workshop", "icon": "build", "order": 3},
    {"id": "kitchen", "name": "Kitchen", "icon": "countertops", "order": 4}
]

# Material Icons list for Icon Picker
AVAILABLE_ICONS = [
    {"name": "Light", "icon": "lightbulb"},
    {"name": "Fan", "icon": "air"},
    {"name": "Power", "icon": "power_settings_new"},
    {"name": "Door", "icon": "door_front_door"},
    {"name": "Lock", "icon": "lock"},
    {"name": "TV", "icon": "tv"},
    {"name": "Computer", "icon": "computer"},
    {"name": "Router", "icon": "router"},
    {"name": "Alarm", "icon": "alarm"},
    {"name": "Temperature", "icon": "thermostat"},
    {"name": "Water", "icon": "water_drop"},
    {"name": "Garage", "icon": "garage"},
    {"name": "Home", "icon": "home"},
    {"name": "Workshop", "icon": "build"},
    {"name": "Tools", "icon": "handyman"},
    {"name": "Camera", "icon": "videocam"},
    {"name": "Music", "icon": "music_note"},
    {"name": "Settings", "icon": "settings"},
    {"name": "Plus", "icon": "add"},
    {"name": "Play", "icon": "play_arrow"},
    {"name": "Stop", "icon": "stop"},
    {"name": "Arrow", "icon": "arrow_forward"},
    {"name": "Toggle", "icon": "toggle_on"},
    {"name": "Lightning", "icon": "flash_on"},
    {"name": "Outlet", "icon": "outlet"},
    {"name": "Sensors", "icon": "sensors"},
    {"name": "Microchip", "icon": "memory"},
    {"name": "Wi-Fi", "icon": "wifi"}
]

HTTP_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]
CONTROL_TYPES = [
    {"label": "Action (Single tap)", "value": "action"},
    {"label": "Toggle (ON/OFF state)", "value": "toggle"},
    {"label": "Momentary (Press/Release)", "value": "momentary"}
]
