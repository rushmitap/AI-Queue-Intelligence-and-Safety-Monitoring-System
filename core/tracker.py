from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2
import numpy as np
import math
from collections import deque

class PersonTracker:
    def __init__(self):
        self.tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0)
        self.history = {} # id -> deque of coordinates
        self.heatmap = None
        self.draw_bboxes = True
        self.draw_heatmap = False
        self.draw_lines = False
        
    def update(self, frame, detections, **kwargs):
        if not detections:
            return frame.copy(), 0, {
                "tracked_objects": [], 
                "centroids": [], 
                "frustrated_count": 0, 
                "is_disorganized": False
            }
            
        tracks = self.tracker.update_tracks(detections, frame=frame)
        
        tracked_count = 0
        drawn_frame = frame.copy()
        
        # Initialize heatmap if needed
        if self.heatmap is None or self.heatmap.shape[:2] != frame.shape[:2]:
            self.heatmap = np.zeros(frame.shape[:2], dtype=np.float32)
            
        centroids = []
        frustrated_ids = []
        tracked_objects = []
        
        # Decay heatmap slightly every frame
        self.heatmap *= 0.95
        
        for track in tracks:
            if not track.is_confirmed():
                continue
                
            tracked_count += 1
            track_id = track.track_id
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)
            cx = int((x1 + x2) / 2)
            cy = int(y2) # Use bottom of bounding box (feet) for centroids
            
            centroids.append((cx, cy))
            
            # Update history
            if track_id not in self.history:
                self.history[track_id] = deque(maxlen=20)
            self.history[track_id].append((cx, cy))
            
            # Check behavior
            history_q = self.history[track_id]
            if len(history_q) > 5:
                start_x, start_y = history_q[0]
                dist = math.hypot(cx - start_x, cy - start_y)
                if dist > 150: # Moving fast / erratic
                    frustrated_ids.append(track_id)
            
            # Update Heatmap
            if 0 <= cy < self.heatmap.shape[0] and 0 <= cx < self.heatmap.shape[1]:
                cv2.circle(self.heatmap, (cx, cy), 30, 2.0, -1)
            
            # Draw bbox
            if getattr(self, 'draw_bboxes', True):
                color = (0, 0, 255) if track_id in frustrated_ids else (255, 200, 0)
                cv2.rectangle(drawn_frame, (x1, y1), (x2, y2), color, 2)
                label = f"ID: {track_id}" + (" (FAST)" if track_id in frustrated_ids else "")
                cv2.putText(drawn_frame, label, (x1, max(0, y1 - 8)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            tracked_objects.append({
                "id": track_id,
                "bbox": [x1, y1, x2, y2],
                "centroid": (cx, cy),
                "is_fast": track_id in frustrated_ids
            })

        is_disorganized = False
        
        # Queue Structure Analysis (Require >= 4 people to define a line)
        if len(centroids) >= 4:
            pts = np.array(centroids)
            x, y = pts[:, 0], pts[:, 1]
            try:
                # Fit line: y = mx + c (or x = my + c if mostly vertical)
                z = np.polyfit(y, x, 1) 
                poly = np.poly1d(z)
                
                # Check mean squared error
                fit_x = poly(y)
                distances = np.abs(x - fit_x)
                avg_dist = np.mean(distances)
                
                is_disorganized = avg_dist > 90.0
                
                if getattr(self, 'draw_lines', False) and not is_disorganized:
                    y_min, y_max = np.min(y), np.max(y)
                    pt1 = (int(poly(y_min)), int(y_min))
                    pt2 = (int(poly(y_max)), int(y_max))
                    # Draw a transparent blue reference line
                    overlay = drawn_frame.copy()
                    cv2.line(overlay, pt1, pt2, (255, 150, 0), 10)
                    cv2.addWeighted(overlay, 0.4, drawn_frame, 0.6, 0, drawn_frame)
            except:
                pass

        # Render Heatmap
        if getattr(self, 'draw_heatmap', False):
            # Blur the accumulation mask
            blurred_heat = cv2.GaussianBlur(self.heatmap, (0, 0), sigmaX=30)
            # Normalize to 0-255
            heatmap_norm = np.clip(blurred_heat * 50, 0, 255).astype(np.uint8)
            # Apply color map
            heatmap_color = cv2.applyColorMap(heatmap_norm, cv2.COLORMAP_JET)
            
            # Blend where heatmap > 0
            mask = heatmap_norm > 5
            blended = cv2.addWeighted(drawn_frame, 0.5, heatmap_color, 0.5, 0)
            drawn_frame[mask] = blended[mask]
            
        tracker_data = {
            "centroids": centroids,
            "frustrated_count": len(frustrated_ids),
            "is_disorganized": is_disorganized,
            "tracked_objects": tracked_objects
        }
            
        return drawn_frame, tracked_count, tracker_data
