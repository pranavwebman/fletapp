# ESP Control Hub ⚡💡🌀

**ESP Control Hub** is a colorful, modern, mobile-first control center built in Python with **Flet** for ESP32, ESP8266, and other microcontrollers exposing HTTP REST endpoints. Designed specifically for Android smartphones, it provides seamless direct local HTTP device control without cloud dependencies or logins.

---

## 🌟 Key Features

* **Mobile-First Android UI**: Designed specifically for portrait phone screens with touch-friendly controls, responsive grids, and scrollable keyboard-safe forms.
* **Colorful & Modern Visual Language**: Light mode default with full support for Dark & System themes, rounded cards, visual state badges, and smooth animations.
* **Direct Local Control**: Sends asynchronous HTTP requests (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) directly from phone to ESP over Wi-Fi without cloud servers.
* **Custom Controls**:
  * **Action Button**: Single tap action execution.
  * **Toggle Button**: Distinct `ON` and `OFF` endpoints with dynamic state toggling.
  * **Momentary Button**: Press-and-hold trigger model.
* **Live "Test Endpoint" Feature**: Test HTTP request endpoints directly inside the control editor before saving.
* **Rich Icon Picker & Color Palette**: Select from Material icons and vibrant accent colors.
* **Device Management**: Group controls under target ESP devices (e.g. `192.168.1.42`) or use standalone custom URLs.
* **Category Filtering & Search**: Organize controls into Bedroom, Living Room, Workshop, etc., and search instantly by control or device name.
* **Local Persistence**: Full JSON-based local storage surviving app restarts.
* **Import & Export**: Easily back up or share your configuration JSON across devices.

---

## 📱 Screenshots & Visual Design

* **Home Screen**: Greeting banner, active network indicator, search bar, category filter chips, and responsive control card grid.
* **Control Cards**: Real-time loading indicator (`⟳`), success checkmark (`✓`), or friendly error alert (`✕`).
* **Add / Edit Screen**: Scrollable form with live endpoint testing.

---

## 🚀 Quick Start & Installation

### Requirements

* **Python 3.10+**
* `flet` (>= 0.20.0)
* `httpx` (>= 0.27.0)

### Installation Steps

1. Clone the repository or extract project files:
   ```bash
   git clone https://github.com/your-username/esp-control-hub.git
   cd esp-control-hub
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   flet run main.py
   ```

---

## 🤖 Running & Building for Android

### Testing on Android Device via Flet App

1. Install the **Flet app** from Google Play Store.
2. Run Flet in server mode on your computer (on the same local Wi-Fi):
   ```bash
   flet run main.py --port 8550 --host 0.0.0.0
   ```
3. Open the Flet app on Android and scan the QR code or enter `http://<YOUR_COMPUTER_IP>:8550`.

### Building Native Android APK

To build a standalone `.apk` for Android using Flet CLI:

1. Ensure **Flutter SDK** and **Android Studio SDK** are installed and configured in your environment.
2. Run the build command:
   ```bash
   flet build apk
   ```
3. The generated APK file will be located in `build/apk/app-release.apk`.

> **Note on Android Networking**: Flet automatically packages `android.permission.INTERNET` and `android.permission.ACCESS_NETWORK_STATE` into the `AndroidManifest.xml`, ensuring local HTTP requests to ESP devices work without restrictions.

---

## 🔌 MicroPython Sample ESP32 Server

Include this simple MicroPython script on your ESP32 or ESP8266 to test endpoints immediately:

```python
# main.py (MicroPython for ESP32)
import network
import socket
import machine

# Setup GPIO 2 (Built-in LED)
led = machine.Pin(2, machine.Pin.OUT)
led.off()

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('YOUR_WIFI_SSID', 'YOUR_WIFI_PASSWORD')

while not wlan.isconnected():
    pass

print('ESP32 Web Server Running on:', wlan.ifconfig()[0])

# Start Socket Server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode('utf-8')

    if 'GET /on' in request:
        led.on()
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nON"
    elif 'GET /off' in request:
        led.off()
        response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOFF"
    elif 'GET /status' in request:
        state_str = "ON" if led.value() == 1 else "OFF"
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n{state_str}"
    else:
        response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\n404 Not Found"

    conn.send(response)
    conn.close()
```

---

## 📖 How to Use

### 1. Add an ESP Device
1. Open the **Devices** tab in the bottom navigation bar.
2. Tap **Add Device**.
3. Enter Name (e.g., `Living Room ESP32`) and Host IP (e.g., `192.168.1.42`).
4. Tap **Save**.

### 2. Create a Control
1. Open the **Add** tab (or tap **Add Control** on Home screen).
2. Set Control Name (e.g., `Ceiling Light`).
3. Select Control Type (`Action` or `Toggle`).
4. Select Target Device or enter Custom URL.
5. Set ON Endpoint (e.g., `/on`) and OFF Endpoint if toggle (`/off`).
6. (Optional) Use **Test Endpoint** to test live communication.
7. Tap **Save Control**.

---

## 📦 Import / Export JSON Format

Configurations are exported as human-readable JSON:

```json
{
  "version": 1,
  "config": {
    "theme_mode": "light",
    "default_timeout": 5,
    "user_name": "Pranav"
  },
  "devices": [
    {
      "id": "device-uuid-1",
      "name": "Living Room ESP32",
      "host": "192.168.1.42",
      "port": 80,
      "description": "ESP32 DevBoard"
    }
  ],
  "controls": [
    {
      "id": "control-uuid-1",
      "name": "Bedroom Light",
      "icon": "lightbulb",
      "color": "#2196F3",
      "control_type": "toggle",
      "device_id": "device-uuid-1",
      "on_endpoint": "/on",
      "off_endpoint": "/off",
      "http_method": "GET"
    }
  ]
}
```

---

## 🛠 Troubleshooting & Common Networking Issues

* **"Could not reach the ESP device. Connection timed out."**
  * Ensure your Android smartphone and ESP microcontroller are connected to the exact same 2.4GHz Wi-Fi network.
  * Check that your Wi-Fi router does not have "AP Isolation" or "Client Isolation" enabled.
  * Verify the IP address assigned to the ESP device in your router settings.
* **"Connection refused"**
  * Verify that the port configured (default `80`) matches the socket server port in your ESP code.
* **"HTTP 404 Endpoint Not Found"**
  * Check for leading or trailing slashes in your endpoint configuration (`/on` vs `on`).

---

## 📂 Project Architecture

```
esp_control_hub/
├── main.py
├── requirements.txt
├── README.md
├── models/
│   ├── app_config.py
│   ├── category.py
│   ├── control.py
│   └── device.py
├── services/
│   ├── http_service.py
│   ├── import_export_service.py
│   └── storage_service.py
├── components/
│   ├── color_picker.py
│   ├── control_card.py
│   ├── dialogs.py
│   └── icon_picker.py
├── screens/
│   ├── devices.py
│   ├── editor.py
│   ├── home.py
│   └── settings.py
├── utils/
│   ├── constants.py
│   └── validation.py
└── tests/
    └── test_app.py
```

---

## 📄 License

MIT License. Designed with ❤️ for IoT and ESP enthusiasts.
