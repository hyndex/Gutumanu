# Gutumanu 🚀
*The Ultimate (Under Construction) Tracking System*

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourusername/gutumanu/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/yourusername/gutumanu/releases)

---

## Overview
Welcome to **Gutumanu** – a next‑gen, production‑ready tracking system built with Django and powered by modern web APIs! 😎  
**Gutumanu** is designed for parents who want to keep their kids safe *and* have a little fun with technology (ethically, of course!).  
*Disclaimer:* This project is for **ethical use only**. Always respect privacy and follow legal guidelines! ⚖️

---

## Features
- **Real‑Time Tracking** 📍  
  - **Location Logs:** Uses the Geolocation API to capture latitude, longitude, and accuracy.
  - **IP Logging:** Records IP address details.
  - **Device Information:** Captures user agent, platform, screen dimensions, etc.
  - **Sensor Data:** (Accelerometer, Gyroscope, Ambient Light, etc.) via DeviceMotion events.
  - **Photo Capture:** Snapshots from the device’s camera (with permission).
  - **Permission Logging:** Records which permissions are granted or denied (geolocation, camera, microphone, notifications, and more).

- **Configurable Update Intervals** ⏱️  
  - Each child/device can have its own update interval (default is 60 seconds).

- **Auto‑Update Mechanism** 🔄  
  - The client-side JavaScript checks for updates from the server and reloads if a new version is available.

- **Interactive Django Admin** 🛠️  
  - Manage all tracking logs through an easy-to-use admin interface.
  - Inlines for quick navigation between location logs, device info, sensor data, photo captures, and permission statuses.
  - "View on Map" links to quickly see the latest GPS coordinates in Google Maps.

---

## Getting Started
### Prerequisites
- Python 3.8+
- [Django](https://www.djangoproject.com/) (and dependencies)
- Virtual environment (recommended)

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/gutumanu.git
   cd gutumanu
   ```

2. **Set up your virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(If you don’t have a requirements.txt, simply install Django: `pip install django`)*

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (for Django admin):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Visit the Landing Page:**  
   Open your mobile Chrome (or any browser) and navigate to:  
   `http://localhost:8000/tracking/placeholder/`  
   This page loads the tracking script and prompts for necessary permissions.

8. **Access Django Admin:**  
   Visit `http://localhost:8000/admin/` to manage your data.

---

## How It Works
- **Client-Side:**  
  The `tracking.js` file (in `tracking/static/tracking/js/tracking.js`) auto‑generates a unique device ID (stored in localStorage) and begins capturing data using modern web APIs. It gracefully handles missing permissions or unsupported APIs and even auto‑updates if a new version is available!

- **Server-Side:**  
  Django views receive JSON and multipart data, log events into models (in `tracking/models.py`), and serve an interactive admin interface for reviewing data.

- **Ethical Boundaries:**  
  **Gutumanu** is strictly for parental use – tracking should only occur with proper permissions and for safeguarding purposes. Misuse for spying or unethical monitoring is **strongly condemned**! 🚫

---

## Future Plans & Roadmap 🌟
- **Mobile App Development:**  
  We plan to develop a companion mobile app (iOS/Android) for more robust, background tracking capabilities and push notifications. Imagine a sleek app that even your kids might say "Wow, Mom/Dad is super tech-savvy!" (But please use responsibly 😅).

- **Real‑Time Communication with Sockets:**  
  Integration of Django Channels and WebSockets to push real‑time updates, notifications, and live tracking data directly to the admin dashboard.

- **Advanced Analytics & Reporting:**  
  Custom dashboards with charts (via Chart.js or React‑Leaflet) to visualize tracking history, safe zone breaches, and more.

- **Geofencing & Alerts:**  
  Define safe zones and trigger immediate alerts (via email/SMS or push notifications) when a device exits a designated area.

- **Enhanced Security:**  
  Implementation of OAuth or token‑based authentication for API endpoints, HTTPS enforcement, and advanced logging for auditing purposes.

- **Plugin‑like Extensibility:**  
  Modular architecture to allow easy integration of future features and plugins (think: custom sensors, third‑party integrations, etc.).

---

## A Little Comedy 😄
Remember, **Gutumanu** is here to make your life easier – not to become a “Big Brother” system! Keep it ethical and legal. And if your kids ever ask, "Mom, why are you tracking me?" just reply with, "Because Gutumanu said so!" 😉  
*(But seriously, always have an honest conversation with your family about digital safety.)*

---

## Contributing
We welcome contributions, feature suggestions, and bug fixes! Feel free to fork the repository and submit pull requests. Please follow ethical guidelines when proposing changes.

---

## License
This project is open‑source under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Stay safe, code responsibly, and enjoy Gutumanu! 🚀🎉
