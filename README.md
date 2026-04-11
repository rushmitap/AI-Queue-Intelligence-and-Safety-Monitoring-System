# 🛡️ AI Queue Intelligence & Safety Monitoring System

An AI-powered computer vision system that analyzes queue behavior from video footage to improve crowd management, reduce wait times, and enhance public safety.

---

## 🚀 Overview

This project uses **computer vision and motion analysis** to monitor queues in real time. It detects people, estimates wait times, analyzes crowd density, and identifies disruptive behaviors like **line-cutting, pushing, and aggression**.

Built for an AI hackathon, this system demonstrates how intelligent automation can transform queue management in real-world environments.

---

## 🔍 Features

### 👥 Queue Detection
- Detects and counts people in a queue
- Identifies queue structure and formation
- Labels individuals (Person 1, Person 2, etc.)

### ⏱️ Wait Time Estimation
- Calculates approximate wait time
- Uses movement speed and queue flow analysis

### 📊 Crowd Density Monitoring
- Classifies crowd levels (Normal / High)
- Detects overcrowding risks

### 🚨 Behavior Detection (USP)
- Detects:
  - Line cutting
  - Pushing / sudden movements
  - Aggressive behavior
- Generates real-time alerts
- Maintains behavior logs

### 📈 Smart Dashboard
- Live metrics display
- Alert feed system
- Incident timeline visualization

---

## 🧠 Tech Stack

- **Frontend:** HTML, CSS, JavaScript  
- **Concepts Used:**
  - Computer Vision  
  - Motion Tracking  
  - Behavior Analysis  

- **Models (Conceptual / Extendable):**
  - YOLO (Object Detection)
  - Pose Estimation
  - Tracking Algorithms (e.g., DeepSORT)

---

## 📹 How It Works

1. Upload a queue video
2. System processes video frames
3. Detects people and tracks movement
4. Analyzes:
   - Queue formation
   - Movement speed
   - Crowd density
   - Behavioral anomalies
5. Displays results in an interactive dashboard

---

## 📊 Output Includes

- 👥 Number of people in queue  
- ⏱️ Estimated wait time  
- 📊 Crowd density status  
- 🚨 Behavior alerts  
- 📜 Detection logs  
- 📈 Incident timeline  

---

## 🎯 Use Cases

- Airports & Railway Stations  
- Shopping Malls  
- Stadiums & Events  
- Ticket Counters  
- Public Safety Monitoring  

---

## 🌟 Unique Selling Point

This system goes beyond traditional crowd monitoring by integrating **behavior intelligence**, enabling detection of real-world issues like queue violations and aggressive actions.

---

## 🔮 Future Scope

- Real-time CCTV integration  
- Backend integration (FastAPI)  
- Cloud deployment  
- Advanced deep learning models  
- Mobile/web app dashboard  
- Multi-camera support  

---

## ⚙️ Installation & Setup

```bash
# Clone the repository
git clone https://github.com/your-username/your-repo-name.git

# Navigate to project folder
cd your-repo-name

# Open index.html in browser
