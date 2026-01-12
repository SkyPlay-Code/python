import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# --- CONFIG ---
CLASS_MAP = {1: "PASSIVE", 2: "PUNCH", 3: "WAVE/NOISE"}
DATA_FILE = "combat_data.csv"
MODEL_FILE = "combat_model.pkl"

def extract_features(landmarks):
    """
    Extracts purely relative coordinates (invariant to camera distance).
    We use the center of shoulders as the (0,0) reference point.
    """
    # 11=Left Shoulder, 12=Right Shoulder
    # 13=Left Elbow, 14=Right Elbow
    # 15=Left Wrist, 16=Right Wrist
    
    lms = landmarks.landmark
    
    # Calculate Center Point (Midpoint of Shoulders)
    center_x = (lms[11].x + lms[12].x) / 2
    center_y = (lms[11].y + lms[12].y) / 2
    
    features = []
    # We only care about upper body for punching: 11 to 16
    relevant_indices = [11, 12, 13, 14, 15, 16]
    
    for i in relevant_indices:
        # Relative Position (X, Y, Z, Visibility)
        features.append(lms[i].x - center_x)
        features.append(lms[i].y - center_y)
        features.append(lms[i].z) 
        features.append(lms[i].visibility)
        
    # Also add Distance between Wrist and Shoulder (Extension factor)
    # Left Arm Ext
    features.append(np.linalg.norm([lms[15].x - lms[11].x, lms[15].y - lms[11].y]))
    # Right Arm Ext
    features.append(np.linalg.norm([lms[16].x - lms[12].x, lms[16].y - lms[12].y]))
        
    return features

def main():
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, model_complexity=1)
    cap = cv2.VideoCapture(0)
    
    data = []
    print("--- TRAINING MODE ---")
    print("HOLD '1' for PASSIVE (Stance)")
    print("HOLD '2' for PUNCH (Action)")
    print("HOLD '3' for WAVE (False Positive)")
    print("PRESS 'ESC' to Train & Save")

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)
        
        status_text = "WAITING..."
        color = (200, 200, 200)
        
        key = cv2.waitKey(1)
        
        if results.pose_landmarks:
            # Draw Skeleton
            mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            features = extract_features(results.pose_landmarks)
            
            # Record Data based on Key Press
            class_id = None
            if key == ord('1'):
                class_id = 1 # Passive
                status_text = "RECORDING: PASSIVE"
                color = (0, 255, 0)
            elif key == ord('2'):
                class_id = 2 # Punch
                status_text = "RECORDING: PUNCH"
                color = (0, 0, 255)
            elif key == ord('3'):
                class_id = 3 # Wave
                status_text = "RECORDING: WAVE"
                color = (0, 255, 255)
                
            if class_id:
                row = features + [class_id]
                data.append(row)
        
        # UI
        cv2.putText(frame, f"SAMPLES: {len(data)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        cv2.putText(frame, status_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        cv2.imshow("Trainer", frame)
        if key == 27: # ESC
            break
            
    cap.release()
    cv2.destroyAllWindows()
    
    # --- TRAINING PHASE ---
    if len(data) > 50:
        print("Training Model...")
        df = pd.DataFrame(data)
        
        # Split Features (X) and Target (y)
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X_train, y_train)
        
        score = model.score(X_test, y_test)
        print(f"Model Accuracy: {score*100:.2f}%")
        
        with open(MODEL_FILE, 'wb') as f:
            pickle.dump(model, f)
            print(f"Model Saved to {MODEL_FILE}")
    else:
        print("Not enough data collected.")

if __name__ == "__main__":
    main()