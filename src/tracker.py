import math
from collections import OrderedDict


class CentroidTracker:
    def __init__(self, max_disappeared=20, max_distance=35):
        self.next_object_id = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def register(self, centroid):
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1

    def deregister(self, object_id):
        del self.objects[object_id]
        del self.disappeared[object_id]

    def update(self, detections):
        # detections = [(x1,y1,x2,y2), ...]

        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects

        input_centroids = []
        for (x1, y1, x2, y2) in detections:
            cX = int((x1 + x2) / 2.0)
            cY = int((y1 + y2) / 2.0)
            input_centroids.append((cX, cY))

        # If no existing objects, register all
        if len(self.objects) == 0:
            for centroid in input_centroids:
                self.register(centroid)
            return self.objects

        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())

        used_detections = set()

        for object_id, obj_centroid in zip(object_ids, object_centroids):
            min_distance = float("inf")
            min_index = -1

            for i, centroid in enumerate(input_centroids):
                if i in used_detections:
                    continue

                dist = math.dist(obj_centroid, centroid)
                if dist < min_distance:
                    min_distance = dist
                    min_index = i

            if min_distance < self.max_distance:
                self.objects[object_id] = input_centroids[min_index]
                self.disappeared[object_id] = 0
                used_detections.add(min_index)
            else:
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)

        # Register new detections
        for i, centroid in enumerate(input_centroids):
            if i not in used_detections:
                self.register(centroid)

        return self.objects
