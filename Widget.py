import sys
import requests
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

CITY_NAME = None
COORDS = None



#  GPS via browser trick

class LocationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global COORDS

        if self.path.startswith("/coords?"):
            try:
                query = self.path.split("?")[1]
                params = dict(q.split("=") for q in query.split("&"))
                lat = float(params.get("lat", 0))
                lon = float(params.get("lon", 0))

                COORDS = (lat, lon)

                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Location received. You can close this tab.")
            except Exception:
                self.send_error(400, "Bad request")

        elif self.path in ["/", "/index.html"]:
            html = """
            <html>
            <body style='text-align:center; font-family:sans-serif;'>
              <h2>Getting your location (: </h2>
              <img src='https://media.giphy.com/media/pVXyJy2k7WO1n49bGg/giphy.gif' width='300' alt='Loading GIF'>
              <p>Fetching your GPS now. Nothing is stored on servers or devices.</p>
            <script>
            navigator.geolocation.getCurrentPosition(function(pos){
                fetch(`http://localhost:8000/coords?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}`);
            });
            </script>
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        elif self.path == "/loading.gif":
            try:
                with open("loading.gif", "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-type", "image/gif")
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, "loading.gif not found")

        else:
            self.send_error(404, "Not found")


def start_gps_server():
    server = HTTPServer(("localhost", 8000), LocationHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()


def request_gps():
    # Open the local web server page (serves HTML + optional local GIF)
    webbrowser.open("http://localhost:8000/")



#  IP fallback

def get_location_from_ip():
    try:
        r = requests.get("http://ip-api.com/json/", timeout=5)
        data = r.json()
        if data["status"] == "success":
            return data["lat"], data["lon"], f"{data['city']} {data['country']}"
    except:
        pass
    return None, None, None



#  Weather API

def get_weather(lat, lon):
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )

        r = requests.get(url, timeout=5)
        data = r.json()

        if "current_weather" in data:
            return data["current_weather"]

    except:
        pass

    return None



# Icon

def get_icon(code):
    icon_map = {
        0: "01d", 1: "02d", 2: "03d", 3: "04d",
        45: "50d", 48: "50d",
        51: "09d", 61: "10d",
        71: "13d",
        95: "11d"
    }

    icon_code = icon_map.get(code, "03d")
    url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"

    try:
        r = requests.get(url, timeout=5)
        pix = QPixmap()
        pix.loadFromData(r.content)
        return pix
    except:
        return None



# App
 
class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Weather")
        self.setGeometry(100, 100, 400, 340)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.city_label = QLabel("Detecting location...", self)
        self.city_label.setGeometry(30, 10, 300, 50)
        self.city_label.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        self.city_label.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel(self)
        self.icon_label.setGeometry(130, 60, 130, 130)

        self.weather_label = QLabel("Starting...", self)
        self.weather_label.setGeometry(30, 200, 300, 100)
        self.weather_label.setStyleSheet("color: white; font-size: 16px;")
        self.weather_label.setAlignment(Qt.AlignCenter)

        self.offset = QPoint()

        # Start GPS server + request
        start_gps_server()
        request_gps()

        QTimer.singleShot(2000, self.load_weather)

    def load_weather(self):
        global COORDS, CITY_NAME

        lat = lon = None

        # 1️⃣ Try GPS
        if COORDS:
            lat, lon = COORDS
            CITY_NAME = "Your Location (GPS)"

        # 2️⃣ Fallback to IP
        if lat is None:
            lat, lon, CITY_NAME = get_location_from_ip()

        # 3️⃣ Final fallback
        if lat is None:
            lat, lon = 56.1629, 10.2039
            CITY_NAME = "Berlin"

        self.city_label.setText(CITY_NAME)

        weather = get_weather(lat, lon)

        if weather:
            temp = weather["temperature"]
            wind = weather["windspeed"]
            code = weather["weathercode"]

            self.weather_label.setText(f"🌡 {temp}°C\n💨 {wind} km/h")

            icon = get_icon(code)
            if icon:
                self.icon_label.setPixmap(icon)
        else:
            self.weather_label.setText("Failed to load weather")

        QTimer.singleShot(600000, self.load_weather)

    # Drag window
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.offset = e.pos()

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            self.move(self.pos() + e.pos() - self.offset)



#  Run

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec_())
