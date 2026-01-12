import cv2
import mediapipe as mp
import numpy as np
from ultralytics import YOLO
import math
import time
from collections import deque

# --- CONFIGURATION (TUNE THESE) ---
WIDTH, HEIGHT = 1280, 720

# MOVEMENT PHYSICS
SENSITIVITY_X = 2.5   # Lower = More stable, Higher = Less head movement needed
SENSITIVITY_Y = 3.0   
DEADZONE = 5          # Pixels of head movement to ignore (removes resting jitter)
SNAP_RADIUS = 150     # Pixel distance to "magnetize" to objects

# VISUALS
COLOR_HUD = (255, 200, 0)   # Amber/Yellow (Classic Terminator)
COLOR_LOCK = (0, 0, 255)    # Red
COLOR_SAFE = (0, 255, 0)    # Green

# DATA FEED
DATA_DB = {
    'person': ["TARGET: HUMAN", "PULSE: 80 BPM", "THREAT: VARIABLE"],
    'cup': ["OBJECT: CONTAINER", "CONTENTS: H2O", "TEMP: 22C"],
    'cell phone': ["DEVICE: MOBILE", "NETWORK: 5G", "ENCRYPTION: HIGH"],
    'bottle': ["OBJECT: VESSEL", "MATERIAL: PLASTIC", "RECYCLABLE: YES"],
    'default': ["SCANNING...", "COMPOSITION: SOLID", "ANALYSIS: PENDING"]
}

class DynamicSmoother:
    """ 
    Adaptive smoothing. 
    If you move fast -> Low smoothing (Responsive).
    If you move slow -> High smoothing (Precision/No Jitter).
    """
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.last_x, self.last_y = x, y
        
    def update(self, target_x, target_y):
        # Calculate speed of intended movement
        dist = math.hypot(target_x - self.last_x, target_y - self.last_y)
        
        # Dynamic Alpha: 
        # High distance = High Alpha (0.7) -> Fast follow
        # Low distance = Low Alpha (0.05) -> Heavy smoothing
        alpha = min(0.8, max(0.05, dist / 100.0))
        
        self.x = self.x * (1 - alpha) + target_x * alpha
        self.y = self.y * (1 - alpha) + target_y * alpha
        
        self.last_x, self.last_y = self.x, self.y
        return int(self.x), int(self.y)

print(">>> SYSTEMS INITIALIZING...")
print(">>> LOAD YOLOv8...")
model = YOLO("yolov8n.pt") 

print(">>> LOAD MEDIAPIPE...")
mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(max_num_faces=1, refine_landmarks=True)

cursor_physics = DynamicSmoother(WIDTH//2, HEIGHT//2)

def draw_corner_rect(img, pts, color, t=2, l=20):
    """ Draws a Sci-Fi bracket style rectangle """
    x1, y1, x2, y2 = pts
    # Top Left
    cv2.line(img, (x1, y1), (x1 + l, y1), color, t)
    cv2.line(img, (x1, y1), (x1, y1 + l), color, t)
    # Top Right
    cv2.line(img, (x2, y1), (x2 - l, y1), color, t)
    cv2.line(img, (x2, y1), (x2, y1 + l), color, t)
    # Bottom Left
    cv2.line(img, (x1, y2), (x1 + l, y2), color, t)
    cv2.line(img, (x1, y2), (x1, y2 - l), color, t)
    # Bottom Right
    cv2.line(img, (x2, y2), (x2 - l, y2), color, t)
    cv2.line(img, (x2, y2), (x2, y2 - l), color, t)

def main():
    # address = "http://192.0.0.4:8080/video"
    cap = cv2.VideoCapture(0)
    cap.set(3, WIDTH)
    cap.set(4, HEIGHT)
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Calibration State
    calib_frames = []
    base_nose_vector = (0, 0)
    is_calibrated = False
    calib_progress = 0

    while True:
        success, img = cap.read()
        if not success: break
        img = cv2.flip(img, 1) # Mirror

        # Create overlay layer
        hud = np.zeros_like(img)
        
        # 1. FACE TRACKING (CONTROL SYSTEM)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(img_rgb)
        
        target_x, target_y = WIDTH//2, HEIGHT//2 # Default
        face_found = False

        if results.multi_face_landmarks:
            face_found = True
            lms = results.multi_face_landmarks[0].landmark
            
            # Using Nose Tip (4) and Center of Head (168/6)
            # This creates a joystick vector
            nose = lms[4] 
            anchor = lms[6] 
            
            nx, ny = nose.x * WIDTH, nose.y * HEIGHT
            ax, ay = anchor.x * WIDTH, anchor.y * HEIGHT
            
            # Raw Vector (How far is nose from center of face?)
            vec_x = nx - ax
            vec_y = ny - ay

            # --- CALIBRATION ROUTINE ---
            if not is_calibrated:
                # Accumulate data
                cv2.rectangle(hud, (WIDTH//2-100, HEIGHT//2-100), (WIDTH//2+100, HEIGHT//2+100), COLOR_HUD, 1)
                cv2.putText(hud, f"CALIBRATING... {calib_progress}%", (WIDTH//2-100, HEIGHT//2-120), font, 0.6, COLOR_HUD, 2)
                cv2.putText(hud, "KEEP HEAD STILL AND LOOK AT SCREEN", (WIDTH//2-180, HEIGHT//2+130), font, 0.6, (255,255,255), 1)
                
                calib_frames.append((vec_x, vec_y))
                calib_progress = int((len(calib_frames) / 30) * 100)
                
                if len(calib_frames) > 30:
                    # Calculate average "Resting" vector
                    avg_x = sum(v[0] for v in calib_frames) / len(calib_frames)
                    avg_y = sum(v[1] for v in calib_frames) / len(calib_frames)
                    base_nose_vector = (avg_x, avg_y)
                    is_calibrated = True
                    print(f">>> CALIBRATED: {base_nose_vector}")
            
            # --- CONTROL LOGIC ---
            else:
                # 1. Subtract Calibration (Zero the joystick)
                rel_x = vec_x - base_nose_vector[0]
                rel_y = vec_y - base_nose_vector[1]
                
                # 2. Apply Deadzone (Ignore micro-jitters)
                if abs(rel_x) < DEADZONE: rel_x = 0
                if abs(rel_y) < DEADZONE: rel_y = 0
                
                # 3. Map to Screen (Scale factor)
                # We use a multiplier to map small head moves to full screen width
                move_x = rel_x * SENSITIVITY_X * 15 # Multiplier tuned for 720p
                move_y = rel_y * SENSITIVITY_Y * 20 
                
                target_x = (WIDTH // 2) + int(move_x)
                target_y = (HEIGHT // 2) + int(move_y)
                
                # 4. Clamp to Screen
                target_x = max(0, min(WIDTH, target_x))
                target_y = max(0, min(HEIGHT, target_y))

        # Update Cursor Physics (Even if face lost, it stays in place)
        cx, cy = cursor_physics.update(target_x, target_y)

        # 2. OBJECT DETECTION (YOLO)
        # Skip frames for performance if needed, but modern GPU/CPU handles v8n fine
        yolo_res = model(img, stream=True, verbose=False, conf=0.5)
        
        objects = []
        for r in yolo_res:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                name = model.names[cls]
                conf = float(box.conf[0])
                objects.append({'box':(x1,y1,x2,y2), 'name':name, 'conf':conf})

        # 3. HUD LOGIC & RENDERING
        locked_target = None
        min_dist = SNAP_RADIUS
        
        for obj in objects:
            x1, y1, x2, y2 = obj['box']
            obj_cx, obj_cy = (x1+x2)//2, (y1+y2)//2
            
            # Check distance to cursor
            dist = math.hypot(obj_cx - cx, obj_cy - cy)
            
            if dist < min_dist:
                min_dist = dist
                locked_target = obj
        
        # Draw Objects
        for obj in objects:
            is_locked = (obj == locked_target)
            color = COLOR_LOCK if is_locked else (50, 50, 50) # Dim if not locked
            
            x1, y1, x2, y2 = obj['box']
            draw_corner_rect(hud, (x1,y1,x2,y2), color, t=2 if is_locked else 1)
            
            if is_locked:
                # Magnetic Snap Visual: Draw line from cursor to object center
                cv2.line(hud, (cx, cy), ((x1+x2)//2, (y1+y2)//2), COLOR_LOCK, 1)
                
                # Render Data Block
                lines = DATA_DB.get(obj['name'], DATA_DB['default'])
                text_y = y1 - 10
                for line in lines:
                    cv2.putText(hud, line, (x2 + 5, text_y), font, 0.5, COLOR_HUD, 1)
                    text_y += 20
            else:
                # Passive Label
                cv2.putText(hud, f"{obj['name']} {int(obj['conf']*100)}%", (x1, y1-5), font, 0.5, (100,100,100), 1)

        # 4. DRAW CURSOR SYSTEM
        if is_calibrated:
            # Outer Ring
            cv2.circle(hud, (cx, cy), 25, COLOR_HUD, 1)
            # Center Dot
            cv2.circle(hud, (cx, cy), 3, COLOR_LOCK if locked_target else COLOR_HUD, -1)
            # Crosshair
            cv2.line(hud, (cx-35, cy), (cx+35, cy), COLOR_HUD, 1)
            cv2.line(hud, (cx, cy-35), (cx, cy+35), COLOR_HUD, 1)
            
            # Coordinates
            cv2.putText(hud, f"X:{cx} Y:{cy}", (cx+30, cy+30), font, 0.4, COLOR_HUD, 1)

            # Reset prompt
            cv2.putText(hud, "[R] RE-CALIBRATE", (20, HEIGHT-30), font, 0.6, (200,200,200), 1)
        
        # 5. COMPOSITE
        # Add "Scanlines" or "Grid" for aesthetic
        # (Optional: Draw a grid)
        cv2.line(hud, (WIDTH//2, 0), (WIDTH//2, HEIGHT), (20,20,20), 1)
        cv2.line(hud, (0, HEIGHT//2), (WIDTH, HEIGHT//2), (20,20,20), 1)

        final = cv2.add(img, hud)
        
        # Darken the real world to make HUD pop
        final = cv2.addWeighted(final, 0.8, np.zeros_like(final), 0.2, 0)

        cv2.imshow("TERMINATOR HUD v4.0", final)
        
        key = cv2.waitKey(1)
        if key == ord('q'): break
        if key == ord('r'): # Reset calibration
            is_calibrated = False
            calib_frames = []
            calib_progress = 0

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()