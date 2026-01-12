import cv2
import mediapipe as mp
import numpy as np
import time
import random

class WeepingAngel:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        self.cap = cv2.VideoCapture(0)
        # Check if camera opened successfully
        if not self.cap.isOpened():
            print("Error: Could not access the webcam.")
            exit()

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Landmark Indices
        self.LEFT_EYE_TOP = 386
        self.LEFT_EYE_BOTTOM = 374
        self.LEFT_EYE_LEFT = 263
        self.LEFT_EYE_RIGHT = 362
        self.LEFT_IRIS_CENTER = 468
        
        self.RIGHT_EYE_TOP = 159
        self.RIGHT_EYE_BOTTOM = 145
        self.RIGHT_EYE_LEFT = 33
        self.RIGHT_EYE_RIGHT = 133
        self.RIGHT_IRIS_CENTER = 473
        
        # Game Balance Variables
        self.start_distance = 50.0   # Meters away starting
        self.max_distance = 200.0    # WIN CONDITION
        self.caught_distance = 0.0   # LOSE CONDITION
        
        self.angel_speed = 4.0       # How fast it attacks (meters/frame)
        self.retreat_speed = 0.4     # How fast you run backward (meters/frame)
        
        self.current_distance = self.start_distance
        
        # State
        self.game_active = False
        self.calibrated = False
        self.game_over_state = None  # "WIN" or "LOSE"
        self.blink_threshold = 0.015
        self.start_calibration_time = 0

    def get_eye_ratio(self, mesh_points, top, bottom, left, right):
        p_top = np.array([mesh_points[top].x, mesh_points[top].y])
        p_bot = np.array([mesh_points[bottom].x, mesh_points[bottom].y])
        p_left = np.array([mesh_points[left].x, mesh_points[left].y])
        p_right = np.array([mesh_points[right].x, mesh_points[right].y])
        h_dist = np.linalg.norm(p_left - p_right)
        v_dist = np.linalg.norm(p_top - p_bot)
        return h_dist, v_dist

    def get_gaze_relative(self, mesh_points, left_idx, right_idx, iris_idx):
        p_left = mesh_points[left_idx].x
        p_right = mesh_points[right_idx].x
        p_iris = mesh_points[iris_idx].x
        eye_width = abs(p_left - p_right)
        if eye_width == 0: return 0.5
        min_x = min(p_left, p_right)
        return (p_iris - min_x) / eye_width

    def draw_hud(self, frame, safe, reason):
        h, w, _ = frame.shape
        
        # 1. VISUAL INTERFERENCE (Noise increases as distance drops)
        if self.current_distance < 100:
            danger_factor = 1.0 - (self.current_distance / 100.0)
            noise = np.zeros((h, w, 3), dtype=np.uint8)
            cv2.randn(noise, 0, 50)
            alpha = max(0, min(danger_factor * 0.8, 0.9)) # Cap noise
            frame = cv2.addWeighted(frame, 1.0 - alpha, noise, alpha, 0)
        
        # 2. STATUS BARS
        # Draw Background for bar
        cv2.rectangle(frame, (50, 50), (w-50, 100), (30,30,30), -1)
        
        # Calculate Progress ratio (0% at 0m, 100% at 200m)
        progress = self.current_distance / self.max_distance
        progress = max(0, min(progress, 1.0))
        
        bar_w = w - 100
        fill_w = int(bar_w * progress)
        
        # Color transitions from Red (Close) -> Yellow -> Green (Safe)
        if self.current_distance < 30:
            bar_color = (0, 0, 255) # Red
        elif self.current_distance > 150:
            bar_color = (0, 255, 0) # Green
        else:
            bar_color = (0, 255, 255) # Yellow

        cv2.rectangle(frame, (50, 50), (50 + fill_w, 100), bar_color, -1)
        
        # Markers
        cv2.line(frame, (50 + int(bar_w * (self.caught_distance/self.max_distance)), 45), 
                        (50 + int(bar_w * (self.caught_distance/self.max_distance)), 105), (255,255,255), 2)
        
        # Text Overlay
        dist_text = f"DISTANCE: {int(self.current_distance)}m / {int(self.max_distance)}m (ESCAPE)"
        cv2.putText(frame, dist_text, (60, 85), cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,0), 2)
        cv2.putText(frame, dist_text, (60, 85), cv2.FONT_HERSHEY_DUPLEX, 1, (255,255,255), 1)

        # Status Status
        if safe:
            msg = "QUANTUM LOCKED: RETREATING..."
            col = (0, 255, 0)
        else:
            msg = f"VULNERABLE: {reason}"
            col = (0, 0, 255)
            
        cv2.putText(frame, msg, (50, 150), cv2.FONT_HERSHEY_TRIPLEX, 1.2, (0,0,0), 5)
        cv2.putText(frame, msg, (50, 150), cv2.FONT_HERSHEY_TRIPLEX, 1.2, col, 2)
        
        # Helper text
        cv2.putText(frame, "Keep eyes OPEN to back away. Blink and it moves closer.", 
                   (50, h-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2)
                   
        return frame

    def run(self):
        while True:
            # Handle Game Over Screen
            if self.game_over_state is not None:
                dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
                
                if self.game_over_state == "LOSE":
                    cv2.putText(dummy_frame, "THE ANGELS HAVE THE PHONE BOX", (50, 360), cv2.FONT_HERSHEY_DUPLEX, 2, (0,0,255), 3)
                    cv2.putText(dummy_frame, "YOU DIED IN THE PAST", (300, 450), cv2.FONT_HERSHEY_PLAIN, 2, (100,100,255), 2)
                else:
                    cv2.putText(dummy_frame, "ESCAPED!", (450, 360), cv2.FONT_HERSHEY_DUPLEX, 3, (0,255,0), 4)
                    cv2.putText(dummy_frame, "The TARDIS dematerialized safely.", (250, 450), cv2.FONT_HERSHEY_PLAIN, 2, (200,255,200), 2)

                cv2.putText(dummy_frame, "Press 'r' to replay or 'q' to quit", (350, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 1)
                cv2.imshow("Weeping Angel", dummy_frame)
                
                key = cv2.waitKey(1)
                if key == ord('r'):
                    self.game_over_state = None
                    self.current_distance = self.start_distance
                    self.calibrated = False # Reset calibration for fair replay
                    self.start_calibration_time = 0
                    time.sleep(1)
                elif key == ord('q'):
                    break
                continue

            # Active Gameplay
            ret, frame = self.cap.read()
            if not ret: break
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # --- CALIBRATION (Start of game) ---
            if not self.calibrated:
                if self.start_calibration_time == 0: self.start_calibration_time = time.time()
                elapsed = time.time() - self.start_calibration_time
                
                overlay = frame.copy()
                cv2.rectangle(overlay, (0,0), (w, h), (0,0,0), -1)
                cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
                
                if elapsed < 3.0:
                    cv2.putText(frame, "CALIBRATION: OPEN EYES WIDE", (250, 360), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
                
                # Sample the "Open" eye state
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                res = self.face_mesh.process(rgb)
                
                if res.multi_face_landmarks:
                    pts = res.multi_face_landmarks[0].landmark
                    _, l_v = self.get_eye_ratio(pts, self.LEFT_EYE_TOP, self.LEFT_EYE_BOTTOM, self.LEFT_EYE_LEFT, self.LEFT_EYE_RIGHT)
                    _, r_v = self.get_eye_ratio(pts, self.RIGHT_EYE_TOP, self.RIGHT_EYE_BOTTOM, self.RIGHT_EYE_LEFT, self.RIGHT_EYE_RIGHT)
                    
                    if elapsed > 1.0:
                         # Set threshold to 55% of your max open width
                        self.blink_threshold = ((l_v + r_v) / 2) * 0.55
                
                if elapsed > 3.0:
                    self.calibrated = True
                    print(f"Game Started. Threshold: {self.blink_threshold}")

                cv2.imshow("Weeping Angel", frame)
                cv2.waitKey(1)
                continue
                
            # --- MAIN LOGIC ---
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)
            
            safe = True
            reason = ""
            
            if results.multi_face_landmarks:
                pts = results.multi_face_landmarks[0].landmark
                
                # Check Blink
                _, l_v = self.get_eye_ratio(pts, self.LEFT_EYE_TOP, self.LEFT_EYE_BOTTOM, self.LEFT_EYE_LEFT, self.LEFT_EYE_RIGHT)
                _, r_v = self.get_eye_ratio(pts, self.RIGHT_EYE_TOP, self.RIGHT_EYE_BOTTOM, self.RIGHT_EYE_LEFT, self.RIGHT_EYE_RIGHT)
                if ((l_v + r_v) / 2) < self.blink_threshold:
                    safe = False
                    reason = "BLINK"

                # Check Gaze (looking left/right away from screen)
                l_r = self.get_gaze_relative(pts, self.LEFT_EYE_LEFT, self.LEFT_EYE_RIGHT, self.LEFT_IRIS_CENTER)
                r_r = self.get_gaze_relative(pts, self.RIGHT_EYE_LEFT, self.RIGHT_EYE_RIGHT, self.RIGHT_IRIS_CENTER)
                avg_gaze = (l_r + r_r) / 2
                if avg_gaze < 0.40 or avg_gaze > 0.60:
                    safe = False
                    reason = "LOOKED AWAY"
            else:
                safe = False
                reason = "NO VISUAL"
                
            # --- MECHANICS UPDATE ---
            if safe:
                # If staring, you gain distance (simulating backing away)
                self.current_distance += self.retreat_speed
            else:
                # If blinking, distance closes RAPIDLY
                self.current_distance -= self.angel_speed
                
            # Render HUD
            frame = self.draw_hud(frame, safe, reason)
            
            # --- CHECK WIN/LOSE ---
            if self.current_distance <= self.caught_distance:
                self.game_over_state = "LOSE"
                # Jumpscare sound logic would go here
            
            if self.current_distance >= self.max_distance:
                self.game_over_state = "WIN"

            cv2.imshow("Weeping Angel", frame)
            if cv2.waitKey(1) == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    game = WeepingAngel()
    game.run()