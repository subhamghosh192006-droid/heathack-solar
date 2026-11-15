# HeatHack Solar — YOLO-World Obstacle Detection Server

This local microservice runs a pretrained **YOLO-World** model (`yolov8s-worldv2.pt`) for detecting rooftop obstacles (water tanks, stair headhouses/mumties, AC units, vents, satellite dishes, and solar water heaters).

---

## 🚀 Setup & Launch (Windows)

```cmd
cd server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8000
```

> **Note:** The first run downloads the YOLO-World model weights automatically and may install the CLIP/torchvision dependencies, which requires an active internet connection and git.

---

## 📡 API Endpoints

- `GET /health`
  Returns `{"status": "ok"}`
- `POST /detect`
  Accepts a multipart file upload (`file: image/*`).
  Returns detected obstacle bounding boxes normalized to $[0, 1]$ (top-left origin):
  ```json
  {
    "model": "yolo-world",
    "time_ms": 78,
    "obstacles": [
      {
        "label": "water tank",
        "score": 0.824,
        "x": 0.68,
        "y": 0.12,
        "w": 0.18,
        "h": 0.22
      }
    ]
  }
  ```

---

## 🧪 Testing

Test the running server on any rooftop image:
```cmd
python test_detect.py ..\docs\workflow_diagram.jpg
```
An annotated image copy (`<filename>_detected.jpg`) will be saved next to the input image.
