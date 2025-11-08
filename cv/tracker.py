# .\venv\Scripts\Activate.ps1

import cv2
import mediapipe as mp

# Initialize MediaPipe solutions
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh

# Drawing specifications for landmarks and connections
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

# Initialize the webcam
# If you have multiple cameras, you might need to change the '0' to '1' or '2'
cap = cv2.VideoCapture(0)

# Check if the webcam is opened correctly
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# Initialize MediaPipe Hands and Face Mesh models
with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands, \
    mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,  # Use refine_landmarks=True for more detailed facial landmarks (like iris)
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as face_mesh:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # Flip the image horizontally for a mirror-like view
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

        # To improve performance, mark the image as not writeable
        image.flags.writeable = False

        # Process the image with both models
        hand_results = hands.process(image)
        face_results = face_mesh.process(image)

        # Revert the image back to BGR for rendering
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Draw hand landmarks
        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS)

        # Draw face mesh landmarks
        if face_results.multi_face_landmarks:
            for face_landmarks in face_results.multi_face_landmarks:
                # Draw the full face mesh tesselation
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec)
                
                # Draw contours for eyes, eyebrows, lips etc.
                mp_drawing.draw_landmarks(
                    image=image,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=None, # No landmarks, just connections
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(80,255,80), thickness=1))


        # Display the resulting frame in a window
        cv2.imshow('Real-time Hand and Face Tracking', image)

        # Exit the loop when the 'q' key is pressed
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Release the webcam and destroy all windows
cap.release()
cv2.destroyAllWindows()