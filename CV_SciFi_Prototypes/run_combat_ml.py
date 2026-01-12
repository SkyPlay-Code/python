import cv2
import mediapipe as mp
import numpy as np
import pickle
import time

# --- CONFIG ---
MODEL_FILE = "combat_model.pkl"
PROB_THRESHOLD = 0.65  # 65% Confidence required to trigger

# Colors
C_RED = (0, 0, 255)
C_CYAN = (255, 255, 0)
C_GREEN = (0, 255, 0)

def extract_features(landmarks):
    """ MUST MATCH TRAINING FEATURE EXTRACTION EXACTLY """
    lms = landmarks.landmark
    center_x = (lms[11].x + lms[12].x) / 2
    center_y = (lms[11].y + lms[12].y) / 2
    
    features = []
    relevant_indices = [11, 12, 13, 14, 15, 16]
    for i in relevant_indices:
        features.append(lms[i].x - center_x)
        features.append(lms[i].y - center_y)
        features.append(lms[i].z)
        features.append(lms[i].visibility)
    
    features.append(np.linalg.norm([lms[15].x - lms[11].x, lms[15].y - lms[11].y]))
    features.append(np.linalg.norm([lms[16].x - lms[12].x, lms[16].y - lms[12].y]))
    return features

def main():
    # Load Model
    try:
        with open(MODEL_FILE, 'rb') as f:
            model = pickle.load(f)
        print("Model Loaded Successfully.")
    except:
        print("ERROR: Run train_combat.py first!")
        return

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    
    # State tracking
    last_action = "PASSIVE"
    action_color = C_GREEN
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)
        
        # HUD Base
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (300, 150), (10, 10, 10), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        if results.pose_landmarks:
            # 1. Extract Features
            feats = extract_features(results.pose_landmarks)
            
            # 2. Predict (reshaped to single sample)
            feats_array = np.array(feats).reshape(1, -1)
            prediction = model.predict(feats_array)[0]
            probs = model.predict_proba(feats_array)[0]
            confidence = np.max(probs)
            
            # 3. Logic
            if confidence > PROB_THRESHOLD:
                if prediction == 2: # PUNCH
                    last_action = "COMBAT: STRIKE"
                    action_color = C_RED
                    # Visual flare
                    cv2.rectangle(frame, (0,0), (w,h), C_RED, 5)
                elif prediction == 3: # WAVE
                    last_action = "NOISE / WAVE"
                    action_color = C_CYAN
                else:
                    last_action = "PASSIVE"
                    action_color = C_GREEN
            
            # Draw Skeleton
            mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # --- Draw HUD ---
            cv2.putText(frame, "AI ANALYSIS:", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 1)
            cv2.putText(frame, last_action, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, action_color, 2)
            
            # Probability Bar
            bar_width = int(confidence * 200)
            cv2.rectangle(frame, (20, 110), (20 + bar_width, 120), action_color, -1)
            cv2.rectangle(frame, (20, 110), (220, 120), (255,255,255), 1)
            cv2.putText(frame, f"{confidence*100:.0f}%", (230, 120), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), 1)

        cv2.imshow("ML Combat Analyzer", frame)
        if cv2.waitKey(1) == ord('q'): break
        
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()