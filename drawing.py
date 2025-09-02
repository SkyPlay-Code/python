# .\venv\Scripts\Activate.ps1

import cv2
import mediapipe as mp
import numpy as np
import math

# Initialize MediaPipe solutions
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Drawing specifications for landmarks and connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# Initialize the webcam
url = "https://192.0.0.4:8080/video"
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# Create a blank canvas to draw on
canvas = None

# Initialize previous coordinates of the drawing finger
px, py = 0, 0

# --- Define colors and brush settings ---
colors = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'eraser': (0, 0, 0) # The eraser is just drawing with the background color
}
current_color = colors['red'] # Default color
brush_size = 15
eraser_size = 50

# --- Helper function to calculate distance ---
def get_distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

# Initialize MediaPipe Hands model for two hands
with mp_hands.Hands(
    min_detection_confidence=0.8,
    min_tracking_confidence=0.5,
    max_num_hands=2) as hands:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Initialize the canvas on the first frame
        if canvas is None:
            canvas = np.zeros_like(image)

        # Flip the image horizontally for a mirror-like view
        image = cv2.flip(image, 1)

        # Convert the BGR image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image with the Hands model
        results = hands.process(image_rgb)
        
        # Revert image to BGR for drawing
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)


        # Process hand landmarks
        if results.multi_hand_landmarks:
            
            # Iterate through each detected hand
            for hand_id, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Get handedness (Left or Right)
                handedness_info = results.multi_handedness[hand_id]
                hand_label = handedness_info.classification[0].label

                # --- Drawing Hand Logic (Right Hand) ---
                if hand_label == "Right":
                    # Draw landmarks for the right hand
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Get coordinates of the index finger and thumb
                    landmarks = hand_landmarks.landmark
                    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]

                    # Get image dimensions
                    h, w, _ = image.shape
                    
                    # Convert normalized coordinates to pixel coordinates
                    ix, iy = int(index_tip.x * w), int(index_tip.y * h)
                    
                    # Pinch gesture detection for drawing
                    if get_distance(index_tip, thumb_tip) < 0.08:
                        if px == 0 and py == 0:
                            px, py = ix, iy

                        # Use eraser size if color is eraser, otherwise use brush size
                        size = eraser_size if current_color == colors['eraser'] else brush_size
                        cv2.line(canvas, (px, py), (ix, iy), current_color, size)
                        px, py = ix, iy
                    else:
                        # Not pinching, so reset the previous coordinates
                        px, py = 0, 0

                # --- Color Selection Hand Logic (Left Hand) ---
                if hand_label == "Left":
                    # Draw landmarks for the left hand
                    mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Get coordinates of all fingertips and thumb
                    landmarks = hand_landmarks.landmark
                    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
                    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]

                    # Pinch gestures for color selection
                    if get_distance(thumb_tip, index_tip) < 0.08:
                        current_color = colors['red']
                    elif get_distance(thumb_tip, middle_tip) < 0.08:
                        current_color = colors['green']
                    elif get_distance(thumb_tip, ring_tip) < 0.08:
                        current_color = colors['blue']
                    elif get_distance(thumb_tip, pinky_tip) < 0.08:
                        current_color = colors['eraser']
        
        # --- UI Display ---
        # Draw a rectangle to show the current color
        color_preview_pos = (10, 10)
        cv2.rectangle(image, color_preview_pos, (color_preview_pos[0] + 50, color_preview_pos[1] + 50), current_color, -1)
        cv2.putText(image, "Color", (color_preview_pos[0], color_preview_pos[1] + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)


        # Combine the canvas and the camera feed
        # Create an inverted mask of the canvas
        img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, img_inv = cv2.threshold(img_gray, 1, 255, cv2.THRESH_BINARY_INV)
        img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)

        # Black-out the area of the drawing on the main image
        image = cv2.bitwise_and(image, img_inv)

        # Add the canvas drawing to the main image
        image = cv2.bitwise_or(image, canvas)

        # Display the resulting frame
        cv2.imshow('Two-Handed Virtual Drawing', image)

        # Exit the loop when the 'q' key is pressed
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Release the webcam and destroy all windows
cap.release()
cv2.destroyAllWindows()