import cv2
import numpy as np

class BirdDetector:
    def __init__(self):
        self.bg = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=25,
            detectShadows=False
        )

        # ROI as percentage of frame 
        self.roi_top = 0.25
        self.roi_bottom = 0.95

        self.scale = 0.5  #  CRITICAL: downscale factor

    def detect(self, frame):
        h, w, _ = frame.shape

        # --- ROI CROP ---
        y1 = int(h * self.roi_top)
        y2 = int(h * self.roi_bottom)
        roi = frame[y1:y2, :]

        # --- DOWNSCALE ---
        roi_small = cv2.resize(
            roi, None, fx=self.scale, fy=self.scale, interpolation=cv2.INTER_AREA
        )

        fg = self.bg.apply(roi_small)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel, iterations=1)
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, kernel, iterations=1)

        contours, _ = cv2.findContours(
            fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        detections = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 40 or area > 400:
                continue

            x, y, w_box, h_box = cv2.boundingRect(cnt)

            aspect = w_box / float(h_box)
            if aspect < 0.6 or aspect > 1.8:
                continue

            # Scale back to original frame
            x1 = int(x / self.scale)
            y1b = int(y / self.scale) + y1
            x2 = int((x + w_box) / self.scale)
            y2b = int((y + h_box) / self.scale) + y1

            detections.append((x1, y1b, x2, y2b))

        return detections
