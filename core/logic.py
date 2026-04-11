from collections import deque

class CrowdLogic:
    def __init__(self, history_size=5):
        self.history = deque(maxlen=history_size)
    
    def get_risk_level(self, count):
        if count <= 5: return "LOW"
        elif count <= 12: return "MEDIUM"
        else: return "HIGH"
        
    def analyze_zones(self, centroids, frame_width):
        # 3 zones: Left, Center, Right
        z_w = frame_width / 3
        zones = {"Left": 0, "Center": 0, "Right": 0}
        
        for (cx, cy) in centroids:
            if cx < z_w: zones["Left"] += 1
            elif cx < z_w * 2: zones["Center"] += 1
            else: zones["Right"] += 1
            
        zone_risks = {}
        for z, c in zones.items():
            if c <= 2: zone_risks[z] = "LOW"
            elif c <= 5: zone_risks[z] = "MEDIUM"
            else: zone_risks[z] = "HIGH"
            
        return zones, zone_risks

    def generate_suggestions(self, count, growth, risk_level, tracker_data):
        suggestions = []
        if risk_level == "HIGH":
            suggestions.append("Open additional counters")
        if growth >= 3:
            suggestions.append("Redirect crowd to relief zones")
            
        if tracker_data.get("is_disorganized"):
            suggestions.append("Queue disorder: Deploy line managers")
            
        if tracker_data.get("frustrated_count", 0) > 0:
            suggestions.append("Address fast-moving/frustrated individuals")
            
        if not suggestions:
            suggestions.append("System operating normally")
            
        return suggestions

    def analyze_frame(self, count, tracker_data, frame_width=640):
        self.history.append(count)
        
        if len(self.history) == self.history.maxlen:
            growth = self.history[-1] - self.history[0]
        else:
            growth = 0
            
        risk_level = self.get_risk_level(count)
        
        # Risk Score Calculation (0-100)
        score = min(count * 5, 100)
        if growth >= 3: score = min(score + 20, 100)
        if tracker_data.get("is_disorganized"): score = min(score + 10, 100)
        if tracker_data.get("frustrated_count", 0) > 0: score = min(score + 15, 100)
        
        zones, zone_risks = self.analyze_zones(tracker_data.get("centroids", []), frame_width)
        suggestions = self.generate_suggestions(count, growth, risk_level, tracker_data)
        
        # Predict next interval
        prediction = max(0, count + int(growth))
        predicted_risk = self.get_risk_level(prediction)
        
        alerts = []
        explanation = []
        if risk_level == "HIGH":
            alerts.append("Overcrowding likely")
        if growth >= 3:
            alerts.append("Rapid crowd increase detected")
        if tracker_data.get("is_disorganized"):
            alerts.append("Queue completely disorganized")
            
        return {
            "count": count,
            "risk_score": score,
            "risk_level": risk_level,
            "growth": growth,
            "alerts": alerts,
            "explanation": "Please review AI Suggestions.",
            "zones": zones,
            "zone_risks": zone_risks,
            "suggestions": suggestions,
            "prediction": prediction,
            "predicted_risk": predicted_risk
        }
