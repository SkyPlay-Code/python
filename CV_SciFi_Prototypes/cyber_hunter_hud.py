import cv2
import mediapipe as mp
import numpy as np
import math
import random

# --- CONFIGURATION ---
WIDTH, HEIGHT = 1280, 720

# Palette
C_NEON_GREEN = (50, 255, 50)
C_HOLO_CYAN  = (255, 255, 0)   # OpenCV uses BGR
C_ALERT_RED  = (50, 50, 255)
C_DEEP_VOID  = (10, 10, 10)
C_WHITE      = (240, 240, 240)

# Face Landmarks (MediaPipe Iris/Face Mesh)
L_EYE_IDX = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
R_EYE_IDX = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
LIPS_IDX  = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

class CyberHUD:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # System State
        self.combat_mode = False
        self.boot_sequence = 0
        self.frame_count = 0
        
        # Squint Logic (Hysteresis to prevent flickering)
        self.squint_frame_counter = 0
        self.squint_threshold_frames = 8  # Frames to hold squint before toggle
        self.last_eye_openness = 2.0
        
        # Animation Variables
        self.rotation_angle = 0
        self.scanline_offset = 0
        self.glitch_intensity = 0
        
        # Pre-generated Scanline Mask (Optimization)
        self.scan_mask = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        self.scan_mask[::4, :] = (0, 40, 0) # Dark green lines every 4th row

    def get_landmarks_array(self, img, landmarks, indices):
        h, w, _ = img.shape
        return np.array([(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in indices], np.int32)

    def apply_chromatic_aberration(self, img, intensity=5):
        """Splits channels and shifts them to create a glitch effect."""
        if intensity == 0: return img
        
        b, g, r = cv2.split(img)
        
        # Shift Blue channel left, Red channel right
        b_shifted = np.roll(b, intensity, axis=1)
        r_shifted = np.roll(r, -intensity, axis=1)
        
        # Fill gaps caused by roll with black
        b_shifted[:, :intensity] = 0
        r_shifted[:, -intensity:] = 0
        
        return cv2.merge([b_shifted, g, r_shifted])

    def draw_tech_circle(self, img, center, radius, color, thick=1, dashed=False):
        """Draws a rotating tech circle/reticle."""
        if dashed:
            # Draw dashed segments
            n_segments = 8
            angle_step = 360 / n_segments
            gap = 10
            rot = (self.frame_count * 2) % 360
            for i in range(n_segments):
                start_angle = i * angle_step + rot
                end_angle = (i + 1) * angle_step - gap + rot
                cv2.ellipse(img, center, (radius, radius), 0, start_angle, end_angle, color, thick)
        else:
            cv2.circle(img, center, radius, color, thick)

    def render_hunter_vision(self, img):
        """High performance Night/Thermal Vision look."""
        # 1. Heavy Green Tint
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Contrast Stretch
        gray = cv2.equalizeHist(gray)
        
        # 3. Edge Detection (Optimized: Downscale -> Canny -> Upscale)
        small = cv2.resize(gray, (WIDTH//2, HEIGHT//2))
        edges = cv2.Canny(small, 40, 120)
        edges = cv2.resize(edges, (WIDTH, HEIGHT))
        
        # 4. Construct the Hunter Image
        # Create a Green-dominant image
        hunter_view = np.zeros_like(img)
        hunter_view[:, :, 1] = gray  # Green channel gets the grayscale detail
        
        # Add White Edges
        edge_layer = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        # Composite
        final = cv2.addWeighted(hunter_view, 0.8, edge_layer, 1.0, 0)
        
        # Add Scanlines
        final = cv2.add(final, self.scan_mask)
        
        return final

    def render_hud_overlay(self, img, face_lms):
        h, w, c = img.shape
        lms = face_lms.landmark
        
        # Colors change based on mode
        primary_color = C_ALERT_RED if self.combat_mode else C_HOLO_CYAN
        
        # 1. CENTER TARGETING RETICLE (Locked to Nose Tip)
        nose_tip = (int(lms[1].x * w), int(lms[1].y * h))
        
        # Animated Reticle
        radius = 60 + int(math.sin(self.frame_count * 0.1) * 5) # Breathing effect
        self.draw_tech_circle(img, nose_tip, radius, primary_color, 1, dashed=True)
        self.draw_tech_circle(img, nose_tip, radius + 10, primary_color, 1, dashed=False)
        
        # Center dot
        cv2.circle(img, nose_tip, 3, C_WHITE, -1)
        
        # 2. SIDE DATA STREAMS
        y_start = 150
        for i in range(5):
            # Random hex data
            txt = f"0x{random.randint(1000,9999)}"
            # Right side
            cv2.putText(img, txt, (w - 120, y_start + (i*30)), cv2.FONT_HERSHEY_PLAIN, 1, primary_color, 1)
            # Left side (Mirror)
            cv2.putText(img, txt, (50, y_start + (i*30)), cv2.FONT_HERSHEY_PLAIN, 1, primary_color, 1)

        # 3. MOUTH ENERGY CORE
        mouth_top = lms[13].y
        mouth_bot = lms[14].y
        mouth_openness = abs(mouth_top - mouth_bot) * 100
        
        lip_pts = self.get_landmarks_array(img, lms, LIPS_IDX)
        
        if mouth_openness > 2.0:
            # Dynamic Energy Ball
            rect = cv2.boundingRect(lip_pts)
            center_mouth = (rect[0]+rect[2]//2, rect[1]+rect[3]//2)
            
            # The louder you scream (wider mouth), the bigger the energy
            energy_rad = int(mouth_openness * 8)
            
            # Draw "Core"
            if self.combat_mode:
                cv2.circle(img, center_mouth, energy_rad, C_ALERT_RED, -1)
                cv2.circle(img, center_mouth, energy_rad-5, C_WHITE, -1)
            else:
                cv2.circle(img, center_mouth, energy_rad, C_HOLO_CYAN, 2)
                
            # Connect mouth corners to HUD
            cv2.line(img, tuple(lip_pts[0]), (50, y_start + 150), primary_color, 1)
            cv2.line(img, tuple(lip_pts[10]), (w - 50, y_start + 150), primary_color, 1)

    def process(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, WIDTH)
        cap.set(4, HEIGHT)
        
        print("SYSTEM START... SQUINT TO TOGGLE COMBAT MODE")
        
        while True:
            success, img = cap.read()
            if not success: break
            
            self.frame_count += 1
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(img_rgb)
            
            # --- 1. BOOT SEQUENCE EFFECT ---
            if self.boot_sequence < 50:
                self.boot_sequence += 1
                cv2.putText(img, "INITIALIZING NEURAL LINK...", (50, HEIGHT//2), cv2.FONT_HERSHEY_SIMPLEX, 1, C_NEON_GREEN, 2)
                # Add random static noise
                noise = np.random.randint(0, 50, (HEIGHT, WIDTH, 3), dtype='uint8')
                img = cv2.add(img, noise)
                cv2.imshow("CYBER_HUD_V2", img)
                cv2.waitKey(1)
                continue

            # --- 2. LOGIC UPDATE ---
            is_face_detected = False
            
            if results.multi_face_landmarks:
                is_face_detected = True
                face_lms = results.multi_face_landmarks[0]
                lms = face_lms.landmark
                
                # SQUINT DETECTION LOGIC
                # Eye 1
                l_h = abs(lms[159].y - lms[145].y)
                # Eye 2
                r_h = abs(lms[386].y - lms[374].y)
                avg_eye = (l_h + r_h) * 1000 # Scaling up
                
                # Logic: If eyes are narrow (< 15) count up. Else count down.
                # Threshold depends on distance, 15 is a generic 'close-ish' value
                if avg_eye < 16: 
                    self.squint_frame_counter += 1
                else:
                    self.squint_frame_counter = max(0, self.squint_frame_counter - 1)
                
                # Trigger switch
                if self.squint_frame_counter > self.squint_threshold_frames:
                    self.combat_mode = not self.combat_mode
                    self.squint_frame_counter = 0 # Reset
                    self.glitch_intensity = 20 # Spike glitch on switch
            
            # --- 3. RENDER BASE LAYER ---
            if self.combat_mode:
                img = self.render_hunter_vision(img)
                overlay_color = C_ALERT_RED
                status_msg = "COMBAT PROTOCOL: ENGAGED"
            else:
                # Slight blue tint for normal mode
                overlay_color = C_HOLO_CYAN
                status_msg = "SYSTEM: ONLINE"
            
            # --- 4. RENDER HUD ELEMENTS ---
            if is_face_detected:
                self.render_hud_overlay(img, face_lms)
            
            # --- 5. POST-PROCESSING (Glitches & UI) ---
            # Glitch decay
            if self.glitch_intensity > 0:
                img = self.apply_chromatic_aberration(img, self.glitch_intensity)
                self.glitch_intensity -= 2
            
            # Top Bar UI
            cv2.rectangle(img, (0,0), (WIDTH, 40), C_DEEP_VOID, -1)
            cv2.putText(img, status_msg, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, overlay_color, 2)
            cv2.putText(img, f"FPS: {int(cv2.getTickFrequency() / (cv2.getTickCount() - self.last_tick) * 10) if hasattr(self, 'last_tick') else 0}", 
                        (WIDTH-150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, C_WHITE, 1)
            
            # Bottom Scanline Bar
            cv2.line(img, (0, HEIGHT-10), (WIDTH, HEIGHT-10), overlay_color, 2)
            
            self.last_tick = cv2.getTickCount()
            cv2.imshow("CYBER_HUD_V2", img)
            
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = CyberHUD()
    app.process()