from ultralytics import YOLO

class PersonDetector:
    def __init__(self, model_path="yolov8n.pt"):
        # Load the specified YOLO model
        self.model = YOLO(model_path)
        self.classes = [0] # 0 is 'person' in COCO dataset

    def detect(self, frame):
        """
        Detects people in the given frame.
        Returns a list of detections formatted for deep_sort_realtime:
        [ ([left, top, w, h], confidence, class_id), ... ]
        """
        results = self.model.predict(source=frame, classes=self.classes, verbose=False)
        detections = []
        
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # get box coordinates [left, top, right, bottom]
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                w = x2 - x1
                h = y2 - y1
                conf = box.conf[0].cpu().numpy()
                
                # Append in expected format: ([left, top, w, h], confidence, detection_class)
                detections.append(([x1, y1, w, h], float(conf), 'person'))
                
        return detections
