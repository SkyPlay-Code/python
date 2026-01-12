import cv2
import mediapipe as mp
import numpy as np
import time
from threading import Thread

# --- CONFIGURATION & AESTHETICS ---
WIDTH, HEIGHT = 1280, 720

# Color Palette (Cyberpunk / High-Sec)
COLOR_VOID = (10, 10, 12)       # Almost black, slight blue tint
COLOR_MESH = (0, 255, 128)      # Spring Green (Wireframe)
COLOR_CONTOUR = (0, 200, 255)   # Cyan (Outer Edge)
COLOR_EYES = (0, 0, 0)          # Blacked out eyes (or change to glowing)
COLOR_TEXT = (100, 255, 100)    # HUD Text

# Mask Physics
EXPANSION_RATIO = 1.20          # Expand the void 20% beyond the face to prevent leaks
VERTICAL_OFFSET = -20           # Shift mask up to cover forehead

# --- HIGH PERFORMANCE CAMERA THREAD ---
class FastWebcam:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.stream.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Minimizes internal buffer lag
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while not self.stopped:
            grabbed, frame = self.stream.read()
            if grabbed:
                self.frame = frame
            else:
                self.stopped = True

    def read(self):
        return self.frame.copy() if self.frame is not None else None

    def release(self):
        self.stopped = True
        self.stream.release()

# --- MATH UTILITIES ---
def get_scaled_hull(face_landmarks, w, h, scale=1.1, offset_y=0):
    """
    Creates a Convex Hull around the face and scales it outward 
    to create a 'safety zone' that blocks background biometrics.
    """
    # 1. Extract all landmark points
    coords = np.array([(lm.x * w, lm.y * h) for lm in face_landmarks.landmark], dtype=np.float32)
    
    # 2. Get the convex hull (the rubber band around the points)
    hull_indices = cv2.convexHull(coords, returnPoints=False)
    hull_points = coords[hull_indices[:,0]]
    
    # 3. Calculate Centroid
    centroid = np.mean(hull_points, axis=0)
    
    # 4. Expand points away from centroid
    vectors = hull_points - centroid
    expanded_points = centroid + (vectors * scale)
    
    # 5. Apply Vertical Offset
    expanded_points[:, 1] += offset_y
    
    return expanded_points.astype(np.int32)

def main():
    # Initialize Systems
    cam = FastWebcam(0)
    time.sleep(0.5) # Warmup

    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    # High-Speed Config: Refine landmarks OFF if speed is priority, ON for better eyes
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=2,
        refine_landmarks=True, 
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7
    )

    # Feature Indices
    # Extract set indices for eyes to draw solid "Visor" eyes
    LEFT_EYE = list(set(i for s in mp_face_mesh.FACEMESH_LEFT_EYE for i in s))
    RIGHT_EYE = list(set(i for s in mp_face_mesh.FACEMESH_RIGHT_EYE for i in s))
    LIPS = list(set(i for s in mp_face_mesh.FACEMESH_LIPS for i in s))

    print("--- SYSTEM ARMED: BIOMETRIC SCRAMBLER ACTIVE ---")

    while True:
        frame = cam.read()
        if frame is None: continue

        # 1. Prepare Image
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 2. AI Processing
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            for i, landmarks in enumerate(results.multi_face_landmarks):
                
                # --- STEP A: THE VOID (Privacy Layer) ---
                # We calculate a hull larger than the face to ensure coverage
                void_poly = get_scaled_hull(landmarks, w, h, scale=EXPANSION_RATIO, offset_y=VERTICAL_OFFSET)
                
                # Draw the black void. This deletes the face pixels.
                cv2.fillPoly(frame, [void_poly], COLOR_VOID)
                
                # Draw a "tech" border around the void
                cv2.polylines(frame, [void_poly], True, COLOR_CONTOUR, 2, cv2.LINE_AA)

                # --- STEP B: THE MESH (Aesthetic Layer) ---
                # We draw the mesh *inside* the void. 
                # This brings back the cool factor of the original script.
                
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None, # No dots, just lines
                    connection_drawing_spec=mp_drawing_styles.DrawingSpec(color=COLOR_MESH, thickness=1, circle_radius=1)
                )

                # --- STEP C: FEATURES (Humanity Layer) ---
                # Explicitly redraw eyes/mouth so expressions are visible
                
                def draw_feat(indices, color, fill=False):
                    pts = np.array([(landmarks.landmark[idx].x * w, landmarks.landmark[idx].y * h) for idx in indices], dtype=np.int32)
                    hull = cv2.convexHull(pts)
                    if fill:
                        cv2.fillPoly(frame, [hull], color) # Solid eyes (Scary/Cool)
                    else:
                        cv2.polylines(frame, [hull], True, color, 1, cv2.LINE_AA)

                # Draw solid black eyes inside the mesh (looks very cyber)
                # Or change fill=False for wireframe eyes
                draw_feat(LEFT_EYE, COLOR_VOID, fill=True) 
                draw_feat(RIGHT_EYE, COLOR_VOID, fill=True)
                
                # Draw wireframe outlines for definition
                draw_feat(LEFT_EYE, COLOR_CONTOUR, fill=False)
                draw_feat(RIGHT_EYE, COLOR_CONTOUR, fill=False)
                draw_feat(LIPS, COLOR_CONTOUR, fill=False)

                # --- STEP D: INFO HUD (Original Flavor) ---
                # Add the "ID" hash back, but lock it to the forehead
                forehead_pt = landmarks.landmark[10] # Top center
                fx, fy = int(forehead_pt.x * w), int(forehead_pt.y * h)
                
                # Generate a consistent fake ID based on face location to avoid flickering numbers
                face_id = f"SUBJ-{i+1}: 0x{(fx+fy)*999:04X}"
                cv2.putText(frame, face_id, (fx-60, fy-50), cv2.FONT_HERSHEY_PLAIN, 1, COLOR_TEXT, 1)

        # Global HUD
        cv2.putText(frame, "ENCRYPTION: ACTIVE", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_MESH, 2)
        
        cv2.imshow("Biometric Void Scrambler", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()