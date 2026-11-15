import os
import time
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLOWorld

app = FastAPI(title="HeatHack Solar YOLO-World Obstacle Detector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLASSES = [
    "water tank",
    "stair headhouse",
    "air conditioner unit",
    "satellite dish",
    "roof vent",
    "solar water heater",
]

CONF = float(os.getenv("CONF", 0.15))

# Load model once at startup
try:
    model = YOLOWorld("yolov8s-worldv2.pt")
except Exception as e:
    print(f"[YOLO-World] Warning loading yolov8s-worldv2.pt ({e}), attempting yolov8s-world.pt...")
    model = YOLOWorld("yolov8s-world.pt")

model.set_classes(CLASSES)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Could not decode image")

    t0 = time.perf_counter()
    results = model.predict(img, imgsz=640, conf=CONF, verbose=False)
    time_ms = int((time.perf_counter() - t0) * 1000)

    obstacles = []
    if results and len(results) > 0:
        result = results[0]
        boxes = result.boxes
        if boxes is not None and len(boxes) > 0:
            xyxyn = boxes.xyxyn.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            clss = boxes.cls.cpu().numpy()
            names = result.names

            for box, conf_score, cls_id in zip(xyxyn, confs, clss):
                xmin, ymin, xmax, ymax = box
                w = float(xmax - xmin)
                h = float(ymax - ymin)
                label = names[int(cls_id)] if int(cls_id) in names else str(int(cls_id))
                obstacles.append({
                    "label": label,
                    "score": round(float(conf_score), 4),
                    "x": max(0.0, min(1.0, round(float(xmin), 4))),
                    "y": max(0.0, min(1.0, round(float(ymin), 4))),
                    "w": max(0.0, min(1.0, round(w, 4))),
                    "h": max(0.0, min(1.0, round(h, 4))),
                })

    return {
        "model": "yolo-world",
        "time_ms": time_ms,
        "obstacles": obstacles,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
