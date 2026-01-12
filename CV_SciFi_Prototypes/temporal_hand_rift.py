import cv2
import mediapipe as mp
import numpy as np
from collections import deque

class TimeRipper:
    def __init__(self):
        # MediaPipe Setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        # Time Travel Settings
        self.BUFFER_SIZE = 60  # 60 frames @ 30fps ~= 2 seconds lag
        self.frame_buffer = deque(maxlen=self.BUFFER_SIZE)
        
    def apply_time_distortion_filter(self, frame):
        """
        Gives the 'past' frame a sci-fi look (Purple/Blue tint + Contrast)
        so it looks like a tear in reality, not just lag.
        """
        # Convert to HSV to shift color
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # Shift Hue towards purple/blue (add constant)
        h = (h + 40).astype(np.uint8) 
        # Increase Saturation for neon look
        s = cv2.add(s, 50)
        
        final_hsv = cv2.merge((h, s, v))
        colored_frame = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        
        # Add a ripple/blur effect (optional, keeps it dreamy)
        return cv2.GaussianBlur(colored_frame, (5, 5), 0)

    def run(self):
        address = "http://192.0.0.4:8080/video" 
        cap = cv2.VideoCapture(address)
        cap.set(3, 1280)
        cap.set(4, 720)
        
        print("Opening Time Rift...")
        print("Wave your hand to reveal the past.")

        while cap.isOpened():
            success, frame = cap.read()
            if not success: break

            # 1. Pre-processing
            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            
            # 2. Manage Time Buffer
            # We save the CLEAN original frame into history
            self.frame_buffer.append(frame.copy())
            
            # We need the buffer to be full before the effect works well
            if len(self.frame_buffer) < self.BUFFER_SIZE:
                cv2.putText(frame, f"Charging Flux Capacitor... {len(self.frame_buffer)}/{self.BUFFER_SIZE}", 
                           (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow('Time Ripper', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'): break
                continue

            # Retrieve the "Past" frame (The oldest one in our buffer)
            past_frame_raw = self.frame_buffer[0]
            past_frame_styled = self.apply_time_distortion_filter(past_frame_raw)

            # 3. Create the Hand Mask
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            
            # Create a black canvas for the mask
            mask = np.zeros((h, w), dtype=np.uint8)
            
            if results.multi_hand_landmarks:
                for hand_lms in results.multi_hand_landmarks:
                    # Collect all landmark points
                    points = []
                    for lm in hand_lms.landmark:
                        px, py = int(lm.x * w), int(lm.y * h)
                        points.append([px, py])
                    
                    points = np.array(points, dtype=np.int32)
                    
                    # Calculate Convex Hull (the outer boundary of the hand)
                    hull = cv2.convexHull(points)
                    
                    # Draw the hull on the mask (White shape on Black background)
                    cv2.fillConvexPoly(mask, hull, 255)
            
            # 4. Refine Mask (Make it sci-fi soft)
            # Dilate: Make the hole slightly bigger than the hand
            kernel = np.ones((20, 20), np.uint8)
            mask = cv2.dilate(mask, kernel, iterations=1)
            
            # Blur: Soften edges so it looks like mist/energy
            mask_blurred = cv2.GaussianBlur(mask, (51, 51), 0)
            
            # 5. Composite the Layers
            # We need to normalize mask to 0.0 - 1.0 range for float math
            mask_norm = mask_blurred.astype(float) / 255.0
            
            # Expand dimensions to match RGB channels (h, w, 1) -> (h, w, 3)
            mask_norm = np.stack([mask_norm]*3, axis=2)
            
            # Formula: (Past * Mask) + (Present * (1 - Mask))
            # Where mask is white, show Past. Where black, show Present.
            composite = (past_frame_styled.astype(float) * mask_norm) + \
                        (frame.astype(float) * (1.0 - mask_norm))
            
            final_output = composite.astype(np.uint8)

            # UI
            cv2.putText(final_output, "TIME RIFT ACTIVE: -2.0s", (30, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)

            cv2.imshow('Time Ripper', final_output)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = TimeRipper()
    app.run()