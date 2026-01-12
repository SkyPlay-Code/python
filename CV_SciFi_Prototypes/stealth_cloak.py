import cv2
import mediapipe as mp
import numpy as np
import time

class PredatorCloak:
    def __init__(self):
        # Initialize MediaPipe solutions
        self.mp_selfie = mp.solutions.selfie_segmentation
        self.mp_face_mesh = mp.solutions.face_mesh
        
        # Settings
        self.LIP_DIST_THRESHOLD = 3.0  # Pixel distance threshold (needs normalization in logic)
        self.DISTORTION_STRENGTH = 15  # How much the light "bends"
        
        # State variables
        self.background_buffer = None
        self.is_cloaked = False
        
        # Camera setup
        address = "http://192.0.0.4:8080/video"
        self.cap = cv2.VideoCapture(address)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def get_lip_distance(self, face_landmarks, img_h, img_w):
        """
        Calculate distance between upper inner lip (13) and lower inner lip (14).
        We normalize this by face height to account for camera proximity.
        """
        # Landmark indices for lips
        UPPER_LIP = 13
        LOWER_LIP = 14
        FOREHEAD = 10
        CHIN = 152

        u_lip = face_landmarks.landmark[UPPER_LIP]
        l_lip = face_landmarks.landmark[LOWER_LIP]
        
        # Convert to pixels
        u_pos = np.array([u_lip.x * img_w, u_lip.y * img_h])
        l_pos = np.array([l_lip.x * img_w, l_lip.y * img_h])
        
        # Get face height for normalization
        top = face_landmarks.landmark[FOREHEAD].y * img_h
        bottom = face_landmarks.landmark[CHIN].y * img_h
        face_height = bottom - top
        
        raw_distance = np.linalg.norm(u_pos - l_pos)
        
        # Normalized ratio (distance / face_height) * 100 for easier tuning
        if face_height > 0:
            return (raw_distance / face_height) * 100
        return 100

    def apply_glass_shader(self, background, user_frame, mask):
        """
        Creates the 'Predator' effect.
        1. Takes the background.
        2. Creates a displacement map based on the user's current movement/pixels.
        3. Remaps the background pixels to look like they are bending.
        """
        h, w = background.shape[:2]
        
        # Create a displacement map using the user's frame converted to grayscale
        # This makes the "invisibility" ripple based on your actual clothes/texture
        gray_user = cv2.cvtColor(user_frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate gradients (direction of change in intensity)
        # This simulates light refraction angles
        flow_x = cv2.Sobel(gray_user, cv2.CV_32F, 1, 0, ksize=3)
        flow_y = cv2.Sobel(gray_user, cv2.CV_32F, 0, 1, ksize=3)
        
        # Normalize and scale gradients
        # We use a noise factor to make it shimmer
        noise = np.random.normal(0, 2, (h, w)).astype(np.float32)
        
        # Create the mapping grid
        grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
        
        # Displace the grid coordinates based on the user's image gradients
        # The (mask > 0.5) ensures we only calculate heavy math where the user is
        map_x = grid_x.astype(np.float32)
        map_y = grid_y.astype(np.float32)
        
        # Apply distortion only where the mask is active
        # We divide by 255 to normalize the Sobel output, then multiply by strength
        offset_x = (flow_x / 255.0) * self.DISTORTION_STRENGTH + noise
        offset_y = (flow_y / 255.0) * self.DISTORTION_STRENGTH + noise
        
        # Mask needs to be resized to match flow if segmentation output is different, 
        # but here they match frame size.
        # Apply the offset only to the masked area
        
        # Extract boolean mask for indexing
        binary_mask = mask > 0.8
        
        map_x[binary_mask] += offset_x[binary_mask]
        map_y[binary_mask] += offset_y[binary_mask]
        
        # Remap allows us to pick pixels from 'background' using the new coordinates
        # borderMode=cv2.BORDER_REFLECT helps blend edges
        distorted_bg = cv2.remap(background, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        
        return distorted_bg

    def run(self):
        print("Initializing Predator Cloak...")
        print("1. Press 'r' to capture/reset the background (Step out of frame first!).")
        print("2. Seal your lips tight to activate the cloak.")
        print("3. Press 'q' to quit.")

        # Setup MediaPipe instances
        with self.mp_selfie.SelfieSegmentation(model_selection=1) as selfie_seg, \
             self.mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True) as face_mesh:
            
            while self.cap.isOpened():
                success, frame = self.cap.read()
                if not success:
                    break

                # Flip for mirror effect
                frame = cv2.flip(frame, 1)
                h, w, _ = frame.shape
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # ---------------------------
                # 1. Background Management
                # ---------------------------
                key = cv2.waitKey(1) & 0xFF
                if key == ord('r') or self.background_buffer is None:
                    self.background_buffer = frame.copy()
                    print("Background Captured!")
                    continue
                if key == ord('q'):
                    break

                # ---------------------------
                # 2. Logic: Face Trigger
                # ---------------------------
                # Default state
                activate_cloak = False
                
                # Analyze Face
                face_results = face_mesh.process(rgb_frame)
                
                if face_results.multi_face_landmarks:
                    for landmarks in face_results.multi_face_landmarks:
                        # Calculate lip seal
                        score = self.get_lip_distance(landmarks, h, w)
                        
                        # Threshold check (Lower score = tighter lips)
                        # Typical open mouth is > 5.0, closed is < 1.0 depending on normalization
                        if score < 1.5: 
                            activate_cloak = True
                            
                        # Debug visual (optional: draw a dot on lips)
                        # cv2.circle(frame, (int(landmarks.landmark[13].x*w), int(landmarks.landmark[13].y*h)), 2, (0,255,0), -1)

                # ---------------------------
                # 3. Segmentation & Shader
                # ---------------------------
                if activate_cloak:
                    # Get the mask
                    seg_results = selfie_seg.process(rgb_frame)
                    mask = seg_results.segmentation_mask
                    
                    # Smooth the mask to reduce jitter
                    mask = cv2.GaussianBlur(mask, (13, 13), 0)

                    # Generate the "Predator" Refraction
                    distorted_layer = self.apply_glass_shader(self.background_buffer, frame, mask)
                    
                    # Composite: 
                    # Where mask is 1 (User), show Distorted Layer
                    # Where mask is 0 (Bg), show Real Frame (or Stored BG, but Real Frame is better for dynamic lights)
                    
                    # Convert mask to 3 channels
                    mask_3d = np.stack((mask,) * 3, axis=-1)
                    
                    # Linear blend
                    output_frame = (distorted_layer * mask_3d) + (self.background_buffer * (1.0 - mask_3d))
                    
                    # Add a cool UI indicator
                    cv2.putText(output_frame, "ACTIVE: REFRACTION CLOAK", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                else:
                    output_frame = frame
                    cv2.putText(output_frame, "INACTIVE - SEAL LIPS TO CLOAK", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                cv2.imshow('Predator Cloak', output_frame.astype(np.uint8))

        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = PredatorCloak()
    app.run()