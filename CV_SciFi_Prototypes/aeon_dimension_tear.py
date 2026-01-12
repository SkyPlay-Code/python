import cv2
import mediapipe as mp
import numpy as np
import time

# --- AESTHETIC CONFIG ---
RIFT_COLOR = (255, 0, 255)   # Magenta for the rift edges
CYBER_COLOR = (0, 255, 255)  # Cyan for the hidden world
TEXT_COLOR = (0, 255, 0)
WIDTH, HEIGHT = 1280, 720

# Performance: Downscale factor for the Cyber effect (2 = 1/2 size, 4 = 1/4 size)
# Higher number = Faster performance + "Blockier" glitch look
FX_SCALE = 3 

class AeonRift:
    def __init__(self):
        # MediaPipe Setup
        self.mp_hands = mp.solutions.hands
        self.mp_face = mp.solutions.face_detection
        
        # Increased confidence to stop Hand-as-Face false positives
        self.hands = self.mp_hands.Hands(
            max_num_hands=2, 
            model_complexity=0, # 0 is faster, 1 is more accurate
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.face = self.mp_face.FaceDetection(min_detection_confidence=0.8)
        
        # State
        self.mask_layer = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
        self.prev_points = {} # Stores {hand_id: (x, y)} for smooth line drawing
        self.start_time = time.time()
        
    def generate_cyber_dimension_optimized(self, img):
        """
        Generates the effect on a smaller image to save FPS, then upscales it.
        """
        h, w = img.shape[:2]
        small_h, small_w = h // FX_SCALE, w // FX_SCALE
        
        # 1. Downscale
        small_img = cv2.resize(img, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
        
        # 2. Edge Detection (Faster on small image)
        gray = cv2.cvtColor(small_img, cv2.COLOR_BGR2GRAY)
        # Less blur needed on small image
        edges = cv2.Canny(gray, 100, 200) 
        
        # 3. Create Cyber Layer
        cyber_small = np.zeros_like(small_img)
        cyber_small[edges > 0] = CYBER_COLOR
        
        # 4. Upscale back to full resolution (Nearest Neighbor keeps it sharp/techy)
        cyber_full = cv2.resize(cyber_small, (w, h), interpolation=cv2.INTER_NEAREST)
        
        return cyber_full

    def draw_tech_ui(self, img, bbox, fps):
        if not bbox: return
        x, y, w, h = bbox
        l, t = 30, 2
        color = (100, 255, 100)
        
        # Corners
        cv2.line(img, (x, y), (x + l, y), color, t)
        cv2.line(img, (x, y), (x, y + l), color, t)
        cv2.line(img, (x+w, y+h), (x+w-l, y+h), color, t)
        cv2.line(img, (x+w, y+h), (x+w, y+h-l), color, t)
        
        text_x = x + w + 10
        # Only draw if text fits on screen
        if text_x < WIDTH - 100:
            cv2.putText(img, f"TARGET: LOCKED", (text_x, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, TEXT_COLOR, 1)
            cv2.putText(img, f"FPS: {int(fps)}", (text_x, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, TEXT_COLOR, 1)

    def run(self):
        cap = cv2.VideoCapture(0)
        cap.set(3, WIDTH)
        cap.set(4, HEIGHT)
        
        prev_time = 0
        
        print("--- SYSTEM ONLINE ---")
        print("Use RIGHT HAND (Index) to TEAR.")
        print("Use LEFT HAND (Open) to HEAL.")
        
        while True:
            success, frame = cap.read()
            if not success: break
            
            # 1. Flip immediately (Mirror view)
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            
            # 2. Generate Background (Optimized)
            cyber_frame = self.generate_cyber_dimension_optimized(frame)
            
            # 3. Tracking
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res_hands = self.hands.process(rgb)
            res_face = self.face.process(rgb)
            
            # 4. Hand Logic
            current_hand_points = {} # To track presence in this frame
            
            if res_hands.multi_hand_landmarks and res_hands.multi_handedness:
                # Zip allows us to get the landmark AND the label (Left/Right)
                for hand_landmarks, handedness in zip(res_hands.multi_hand_landmarks, res_hands.multi_handedness):
                    
                    # MediaPipe Logic: In a flipped (mirror) image:
                    # Label "Left" = User's RIGHT hand
                    # Label "Right" = User's LEFT hand
                    label = handedness.classification[0].label 
                    
                    # Coordinates of Index Finger Tip (8)
                    ix = int(hand_landmarks.landmark[8].x * w)
                    iy = int(hand_landmarks.landmark[8].y * h)
                    
                    # Store current point
                    current_hand_points[label] = (ix, iy)
                    
                    # --- TEARING LOGIC (User's Right Hand -> MP Label "Left") ---
                    if label == "Left": 
                        brush_size = 40
                        
                        # Smooth Drawing: Line from prev point to current
                        if label in self.prev_points:
                            prev_pt = self.prev_points[label]
                            dist = np.hypot(ix - prev_pt[0], iy - prev_pt[1])
                            
                            # If moved too far (glitch), don't draw line
                            if dist < 300: 
                                cv2.line(self.mask_layer, prev_pt, (ix, iy), 255, brush_size)
                        
                        # Draw circle at current tip to fill gaps
                        cv2.circle(self.mask_layer, (ix, iy), int(brush_size/2), 255, -1)
                        
                        # Sparkles
                        cv2.circle(frame, (ix, iy), 10, RIFT_COLOR, -1)

                    # --- HEALING LOGIC (User's Left Hand -> MP Label "Right") ---
                    elif label == "Right":
                        heal_size = 80
                        cv2.circle(self.mask_layer, (ix, iy), heal_size, 0, -1)
                        cv2.circle(frame, (ix, iy), heal_size, (0, 255, 0), 2)
            
            # Update history for smooth drawing
            self.prev_points = current_hand_points

            # 5. Compositing
            # Blur mask slightly for organic edges
            mask_blur = cv2.GaussianBlur(self.mask_layer, (25, 25), 0)
            
            # Convert mask to 3 channels (0.0 to 1.0)
            mask_3ch = cv2.cvtColor(mask_blur, cv2.COLOR_GRAY2BGR) / 255.0
            
            # Blend: Final = Cyber * mask + Reality * (1-mask)
            # Use float blending for smooth alpha
            frame_float = frame.astype(float)
            cyber_float = cyber_frame.astype(float)
            
            img_final = (cyber_float * mask_3ch + frame_float * (1.0 - mask_3ch)).astype(np.uint8)
            
            # Draw Neon Borders on the tear
            _, thresh = cv2.threshold(mask_blur, 100, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(img_final, contours, -1, RIFT_COLOR, 3)

            # 6. Face UI
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time)
            prev_time = curr_time
            
            if res_face.detections:
                for detection in res_face.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    bbox = int(bboxC.xmin * w), int(bboxC.ymin * h), \
                           int(bboxC.width * w), int(bboxC.height * h)
                    self.draw_tech_ui(img_final, bbox, fps)

            # UI Text
            cv2.putText(img_final, "AEON RIFT v2.0", (20, h-30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            
            cv2.imshow('Aeon Rift Interface', img_final)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = AeonRift()
    app.run()