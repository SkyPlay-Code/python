import cv2
import mediapipe as mp # type: ignore
import numpy as np
from collections import deque

# The get_face_triangulation function is no longer needed.

# --- A Class to Stabilize Landmarks over Time ---
class LandmarkStabilizer:
    """A class to smooth landmarks over a time window to reduce jitter."""
    def __init__(self, num_landmarks, window_size=3):
        self.window_size = window_size
        self.landmark_history = [deque(maxlen=window_size) for _ in range(num_landmarks)]

    def update(self, landmarks):
        for i, lm in enumerate(landmarks):
            self.landmark_history[i].append([lm.x, lm.y, lm.z])

    def get_stable_landmarks(self):
        stable_landmarks = np.zeros((len(self.landmark_history), 3))
        for i in range(len(self.landmark_history)):
            if self.landmark_history[i]:
                stable_landmarks[i] = np.mean(self.landmark_history[i], axis=0)
        return stable_landmarks

# --- Main Application ---
def main():
    # THE DEFINITIVE FIX: Get the triangulation data directly from the FaceMesh class
    face_triangulation = mp.solutions.face_mesh.FACEMESH_TESSELATION

    if not face_triangulation:
        print("Error: Could not load face triangulation data.")
        return

    # --- Initialization ---
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
        
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    num_landmarks = 478
    stabilizer = LandmarkStabilizer(num_landmarks, window_size=5)

    coverage_map = np.zeros(num_landmarks)
    captured_landmarks = []
    visited_angles = set()

    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_mesh.FaceMesh(
            max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:

        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image = cv2.flip(image, 1)
            results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            instruction_text = "Slowly rotate your head to scan your face"

            if results.multi_face_landmarks:
                landmarks_mp = results.multi_face_landmarks[0].landmark
                stabilizer.update(landmarks_mp)
                stable_landmarks = stabilizer.get_stable_landmarks()

                nose_tip = stable_landmarks[1]
                chin = stable_landmarks[152]
                forehead = stable_landmarks[10]

                face_vector = forehead - chin
                yaw = face_vector[0]
                pitch = face_vector[1]

                angle_bin = (round(yaw, 1), round(pitch, 1))

                if angle_bin not in visited_angles:
                    visited_angles.add(angle_bin)
                    coverage_map += 0.1
                    np.clip(coverage_map, 0, 1.0, out=coverage_map)
                    captured_landmarks.append(stable_landmarks.copy())
                    print(f"Captured new angle: Yaw={yaw:.2f}, Pitch={pitch:.2f}. Total captures: {len(captured_landmarks)}")

                for i in range(num_landmarks):
                    pt = stable_landmarks[i]
                    coverage = coverage_map[i]

                    if coverage < 0.4: color = (0, 0, 255) # Red
                    elif coverage < 0.8: color = (0, 255, 255) # Yellow
                    else: color = (0, 255, 0) # Green

                    x, y = int(pt[0] * w), int(pt[1] * h)
                    cv2.circle(image, (x, y), 2, color, -1)

            else:
                instruction_text = "Please position your face in the frame"

            overall_progress = np.mean(coverage_map)
            progress_text = f"Scan Progress: {overall_progress:.0%}"
            cv2.putText(image, instruction_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.putText(image, progress_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(image, "Press 'q' to finish", (w - 250, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            cv2.imshow('LiDAR-Style Face Scanner', image)

            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    if captured_landmarks:
        print(f"\nScan finished. Captured {len(captured_landmarks)} unique keyframes.")
        print("Fusing point cloud into final high-accuracy model...")

        final_landmarks = np.mean(captured_landmarks, axis=0)
        final_landmarks[:, 1] = -final_landmarks[:, 1] # Negate Y for correct 3D orientation

        save_as_obj(final_landmarks, face_triangulation)
    else:
        print("\nScan was cancelled. No data captured.")

def save_as_obj(landmarks, edges, filename="lidar_scan_model.obj"):
    """Saves the 3D landmarks and tesselation edges as OBJ."""
    print(f"\n--- Writing final model to {filename} ---")

    with open(filename, 'w') as f:
        f.write("# 3D Face Scan (Wireframe)\n\n")
        for v in landmarks:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")
        f.write("\n")
        for e in edges:
            f.write(f"l {e[0]+1} {e[1]+1}\n")   # 'l' = line in OBJ
    print("Successfully saved model.")


if __name__ == '__main__':
    main()