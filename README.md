# Widget GPS + Weather (PyQt + local browser geo)

This small app launches a local web server (`localhost:8000`) and opens a browser tab to request geolocation. It then fetches weather data for that location and displays it in a frameless PyQt window.

## Features

- `LocationHandler` HTTP server:
  - `/` or `/index.html`: serves an HTML page with embedded GPS request + animated GIF.
  - `/coords?lat=<lat>&lon=<lon>`: receives location and stores it in `COORDS`.
  - `/loading.gif`: serves local `loading.gif` from widget folder.
- `WeatherApp`:
  - attempts GPS first; falls back to IP-based location and hardcoded Berlin.
  - displays city, temperature, wind speed, and icon from Open-Meteo + OpenWeather icons.

## How to run

1. Place `loading.gif` in the same folder as `widget.py`:
   - `d:/python_jeg_ved_ikke/widget/loading.gif`
2. Start the app from the repo root:
   - `python widget/widget.py`
3. Allow location access in the browser popup.
4. The app window updates after your location is captured.

## Customizing the GIF

- To use the Giphy cat loading animation, the server is configured with:
  - `https://media.giphy.com/media/pVXyJy2k7WO1n49bGg/giphy.gif`
- To use local GIF, place `loading.gif` in `widget/` and the `/loading.gif` handler will serve it.

## Notes

- The code uses `requests` and `PyQt5`.
- If location fails (no permission), fallback is IP geolocation.
- For a full static asset server, add simple extension handling in `LocationHandler`.
