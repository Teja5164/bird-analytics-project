import json
import cv2
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from src.detect import BirdDetector
from src.tracker import CentroidTracker

VIDEO_PATH = Path("data/input_video.mp4")
OUTPUT_VIDEO_PATH = Path("outputs/detection_output.mp4")
OUTPUT_VIDEO_PATH.parent.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(str(VIDEO_PATH))
if not cap.isOpened():
    raise RuntimeError("Could not open input video")

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(
    str(OUTPUT_VIDEO_PATH),
    fourcc,
    fps,
    (width, height)
)

detector = BirdDetector()
tracker = CentroidTracker()

frame_idx = 0
frame_data = []

# Process the video and save outputs
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1
    detections = detector.detect(frame)
    objects = tracker.update(detections)

    weights = []
    for (x1, y1, x2, y2) in detections:
        area = (x2 - x1) * (y2 - y1)
        weights.append(area)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

    avg_weight = int(sum(weights) / len(weights)) if weights else 0

    for obj_id, (cx, cy) in objects.items():
        cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)
        cv2.putText(
            frame,
            f"ID {obj_id}",
            (cx - 10, cy - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    cv2.rectangle(frame, (10, 10), (600, 100), (255, 255, 255), -1)
    cv2.putText(frame, f"Frame: {frame_idx}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(frame, f"Bird Count: {len(objects)}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(frame, f"Avg Weight Index: {avg_weight}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    frame_data.append({
        "frame": frame_idx,
        "bird_count": len(objects),
        "avg_weight_index": avg_weight
    })

    writer.write(frame)

cap.release()
writer.release()
print("Detection + weight estimation video generated")

# Save overall JSON
json_output_path = Path("outputs/output.json")
with open(json_output_path, "w") as f:
    json.dump({
        "video_name": VIDEO_PATH.name,
        "fps": fps,
        "total_frames": frame_idx,
        "frames": frame_data
    }, f, indent=4)
print("JSON output generated at outputs/output.json")

# ---------------- FASTAPI SETUP ----------------
app = FastAPI(title="Bird Detection API")

@app.get("/frame/{frame_number}")
def get_frame_data(frame_number: int):
    if frame_number < 1 or frame_number > frame_idx:
        raise HTTPException(status_code=404, detail=f"Frame {frame_number} out of range (1-{frame_idx})")
    frame_info = next((f for f in frame_data if f["frame"] == frame_number), None)
    return JSONResponse(content=frame_info)

@app.get("/summary")
def get_video_summary():
    summary = {
        "video_name": VIDEO_PATH.name,
        "fps": fps,
        "total_frames": frame_idx,
        "frames": frame_data
    }
    return JSONResponse(content=summary)

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
