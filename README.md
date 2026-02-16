# Bird Counting and Weight Estimation (Prototype)

**Author:** N R TEJA PRAKASH  
**Email :** tejaprakash5164@gmail.com 
**Date:** 16 February 2026


## Overview
This project implements a computer vision prototype to analyze a fixed-camera poultry farm CCTV video.  

The system performs:  
- Bird detection  
- Stable bird counting over time using tracking IDs  
- Bird weight estimation using a visual proxy  

This solution is designed as an **prototype**, focusing on clarity, robustness, and explainability.  

---

## Input
- Fixed-camera poultry CCTV video  
- Daylight conditions  
- Static background  
- Birds with slow, random motion


Input video link - https://drive.google.com/drive/folders/109VK-xY85_zi-S4z6c4lq3yRSR0zJ7Oi?usp=sharing

---

## Output
1. **Annotated video** with:  
    - Bounding boxes  
    - Unique bird IDs  
    - Bird count per frame  
    - Average weight index  

2. **JSON file** containing frame-wise analytics → `outputs/output.json`  

3. **Interactive API endpoints** (replaces manual frame input):
    - Request specific frame data or full summary via HTTP.  
    - Returns JSON responses.

Due to the size constraints of the output video file which is 2 gb ,the size is constrained to 150mb due to which there may be few quality issues.The output files are uploaded in the google drive
link - https://drive.google.com/drive/folders/1v8TmwfD1Dl0W7lH19-SZvL9jlUyJ2H-T?usp=drive_link
---

## Approach

### 1. Bird Detection
- YOLOv8 is used for object detection.  
- Detection is filtered and tuned for small bird sizes.  

### 2. Bird Tracking
- A centroid-based tracker assigns stable IDs.  
- IDs persist across frames unless birds disappear for a long duration.  

### 3. Bird Counting
- Bird count is derived from active tracked IDs per frame.  

### 4. Weight Estimation (Proxy)
- Real weight cannot be measured from video.  
- A **weight index** is computed using bounding box area.  
- Average weight index per frame is reported.  

---

## JSON Output Structure
```json
{
  "video_name": "input_video.mp4",
  "fps": 19.8,
  "total_frames": 5545,
  "frames": [
    {
      "frame": 1,
      "bird_count": 42,
      "avg_weight_index": 1832
    }
  ]
}
````

**Frame-specific JSON** example: `outputs/frame_123.json`

```json
{
  "frame": 123,
  "bird_count": 40,
  "avg_weight_index": 1800
}
```

---

## Folder Structure

```
project/
│
├─ data/
│   └─ input_video.mp4
├─ outputs/
│   ├─ detection_output.mp4
│   ├─ output.json
│   ├─ test_output.json
│   └─ frame_<frame_number>.json
├─ src/
│   ├─ detect.py
│   └─ tracker.py
└─ run_pipeline_api.py
```

---

## Requirements

* Python 3.8+
* OpenCV: `pip install opencv-python`
* FastAPI: `pip install fastapi uvicorn`
* `src/detect.py` (BirdDetector)
* `src/tracker.py` (CentroidTracker)

---

## Usage

### 1. Run the pipeline & API server

```bash
python run_pipeline_api.py
```

* The script will first **process the video**, generate the annotated video and `output.json`.
* Then it will **start the FastAPI server** at:

```
http://0.0.0.0:8000
```

or locally:

```
http://127.0.0.1:8000
```

> ⚠️ Keep the terminal running — the server is waiting for HTTP requests.

---

### 2. Access API Endpoints

1. **Get full video summary**

Open a browser or use curl/Postman:

```
http://127.0.0.1:8000/summary
```

or in terminal:

```bash
curl http://127.0.0.1:8000/summary
```

Returns JSON with all frames, bird counts, and weight indexes.

2. **Get data for a specific frame**

Example for frame 100:

```
http://127.0.0.1:8000/frame/100
```

or in terminal:

```bash
curl http://127.0.0.1:8000/frame/100
```

Returns JSON:

```json
{
  "frame": 100,
  "bird_count": 38,
  "avg_weight_index": 1795
}
```

---

### 3. Video & JSON Outputs

* Annotated video → `outputs/detection_output.mp4`
* Full frame-wise JSON → `outputs/output.json`
* Optional frame-specific JSON → `outputs/frame_<frame_number>.json`

> In a deployed API setup, clients can query specific frames instead of manually opening files.

---




