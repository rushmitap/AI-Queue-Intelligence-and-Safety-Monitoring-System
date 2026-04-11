from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
import cv2
import threading
import time
import os
import uvicorn
import httpx

from core.detection import PersonDetector
from core.tracker import PersonTracker
from core.logic import CrowdLogic
from api.database import init_db, insert_stat, get_recent_stats

app = FastAPI(title="Q-Safe AI API")

# Global state
class VideoProcessor:
    def __init__(self):
        self.active = False
        self.cap = None
        self.latest_frame = None
        self.latest_stats = {
            "count": 0,
            "risk_score": 0,
            "risk_level": "LOW",
            "growth": 0,
            "alerts": [],
            "explanation": "System initialized"
        }
        self.thread = None
        self.detector = PersonDetector("yolov8n.pt")
        self.tracker = PersonTracker()
        self.logic = CrowdLogic()

    def start(self, source=0):
        if self.active:
            self.stop()
        
        self.active = True
        self.cap = cv2.VideoCapture(source)
        self.thread = threading.Thread(target=self.process_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.active = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if self.cap:
            self.cap.release()
            
    def process_loop(self):
        frame_counter = 0
        while self.active and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
                
            # Resize for performance if needed
            frame = cv2.resize(frame, (640, 480))
            
            # Detect
            detections = self.detector.detect(frame)
            
            # Track
            drawn_frame, count, tracker_data = self.tracker.update(frame, detections)
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', drawn_frame)
            if ret:
                self.latest_frame = buffer.tobytes()
                
            # Logic & db
            stats = self.logic.analyze_frame(count, tracker_data)
            self.latest_stats = stats
            
            # Throttle DB writes to once per 10 frames (~3 fps at 30fps)
            frame_counter += 1
            if frame_counter % 10 == 0:
                insert_stat(stats)
            
            # small sleep to prevent 100% CPU lock if processing is too fast
            time.sleep(0.01)

processor = VideoProcessor()

@app.on_event("startup")
def startup():
    # Make sure data folder exists
    os.makedirs("data", exist_ok=True)
    init_db()

@app.get("/")
def read_root():
    return {"status": "active", "system": "Q-Safe AI"}

@app.post("/start")
def start_system(source: str = "0"):
    src = int(source) if source.isdigit() else source
    processor.start(src)
    return {"message": f"Started processing source: {source}"}

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    # Save the file to disk temporarily
    os.makedirs("data", exist_ok=True)
    file_location = f"data/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    processor.start(file_location)
    return {"info": f"file '{file.filename}' uploaded and processing started."}

@app.post("/stop")
def stop_system():
    processor.stop()
    return {"message": "Stopped processing"}

@app.get("/stats")
def get_stats():
    return processor.latest_stats

@app.get("/history")
def get_history(limit: int = 50):
    return get_recent_stats(limit)

def generate_frames():
    while True:
        if processor.latest_frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + processor.latest_frame + b'\r\n')
        else:
            time.sleep(0.1)

@app.get("/feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")
