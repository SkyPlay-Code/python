import cv2
import mediapipe as mp
import numpy as np
import math
import time

# --- CONSTANTS ---
WIDTH, HEIGHT = 1280, 720
CYAN = (255, 255, 0)     # HUD Primary
TEAL = (200, 200, 0)     # HUD Secondary
RED = (0, 0, 255)
GREEN = (0, 255, 0)

# Tools & Colors Config
TOOLS = ["BRUSH", "RECT", "CIRCLE"]
COLORS = [(0, 255, 255), (0, 0, 255), (0, 255, 0), (255, 0, 255)] # Yellow, Red, Green, Purple
COLOR_NAMES = ["CYAN", "RED", "GREEN", "PURPLE"]

# --- SETUP MEDIAPIPE ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.6, min_tracking_confidence=0.6)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.6)

# --- DRAWING CLASS (simplified from previous) ---
class Shape:
    def __init__(self, type, params, color):
        self.type = type # 'RECT', 'CIRCLE', 'PATH'
        self.color = color
        self.params = params # [x, y, w, h] or [pts]
        self.grabbed = False
        self.offset = (0,0)

    def draw(self, img, is_hovered=False):
        c = (255, 255, 255) if is_hovered else self.color
        if self.type == 'RECT':
            x, y, w, h = self.params
            cv2.rectangle(img, (x, y), (x+w, y+h), c, 2)
            cv2.rectangle(img, (x, y), (x+w, y+h), self.color, -1 if not is_hovered else 2) # Solid if not selected
        elif self.type == 'CIRCLE':
            cx, cy, r = self.params
            cv2.circle(img, (cx, cy), r, c, 2)
            cv2.circle(img, (cx, cy), r, self.color, -1 if not is_hovered else 2)
        elif self.type == 'PATH':
            if len(self.params) > 1:
                pts = np.array(self.params, np.int32).reshape((-1, 1, 2))
                cv2.polylines(img, [pts], False, c, 5)

    def is_inside(self, x, y):
        if self.type == 'RECT':
            ox, oy, w, h = self.params
            return ox < x < ox+w and oy < y < oy+h
        elif self.type == 'CIRCLE':
            ox, oy, r = self.params
            return math.hypot(x-ox, y-oy) < r
        elif self.type == 'PATH':
            # Simplified bounding box for path
            xs = [p[0] for p in self.params]
            ys = [p[1] for p in self.params]
            return min(xs) < x < max(xs) and min(ys) < y < max(ys)
        return False

    def move(self, x, y):
        if self.type == 'RECT':
            self.params[0] = x - self.offset[0]
            self.params[1] = y - self.offset[1]
        elif self.type == 'CIRCLE':
            self.params[0] = x - self.offset[0]
            self.params[1] = y - self.offset[1]
        elif self.type == 'PATH':
            # Complex: Move all points relative to anchor
            dx = x - self.offset[0] - self.params[0][0] # calc delta based on first point
            dy = y - self.offset[1] - self.params[0][1]
            new_pts = []
            for p in self.params:
                new_pts.append((p[0]+dx, p[1]+dy))
            self.params = new_pts


# --- STATE VARIABLES ---
shapes = []
curr_tool_idx = 0
curr_color_idx = 0
selection_timer = 0
selection_trigger_limit = 15 # Frames to hold head tilt to switch
switch_lock = False

# Interaction Vars
drawing_anchor = None
curr_path = []
held_shape_idx = -1
active_r_pinch = False
active_l_pinch = False


def main():
    global shapes, curr_tool_idx, curr_color_idx, selection_timer, switch_lock, drawing_anchor, held_shape_idx, active_r_pinch, active_l_pinch
    address = "http://192.0.0.4:8080/video"
    cap = cv2.VideoCapture(address)
    cap.set(3, WIDTH)
    cap.set(4, HEIGHT)

    print("--- JARVIS MODE ACTIVATED ---")
    print("RIGHT HAND PINCH: Draw")
    print("LEFT HAND PINCH:  Move")
    print("HEAD TILT RIGHT:  Next Tool")
    print("HEAD TILT LEFT:   Next Color")
    print("MOUTH OPEN:       Clear Screen")

    while True:
        success, img = cap.read()
        if not success: break
        img = cv2.flip(img, 1)
        
        # Create overlays
        hud = np.zeros_like(img) # The Futuristic Interface Layer
        
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 1. PROCESS FACEMESH (The Menu System)
        res_face = face_mesh.process(rgb)
        
        head_angle_x = 0
        mouth_open_dist = 0
        face_center = (0,0)

        if res_face.multi_face_landmarks:
            for face_lms in res_face.multi_face_landmarks:
                # -- GEOMETRY CALCS --
                # Nose tip (1), Top Head (10), Chin (152), Left Cheek(234), Right Cheek(454)
                # Left Iris (468), Right Iris (473) *Requires refine_landmarks=True
                
                h, w, c = img.shape
                nose_tip = face_lms.landmark[1]
                face_center = (int(nose_tip.x * w), int(nose_tip.y * h))
                
                # Draw Basic HUD Circle
                cv2.circle(hud, face_center, 60, CYAN, 1)
                cv2.ellipse(hud, face_center, (70, 70), 0, 0, 180, TEAL, 2)
                
                # -- EYE TRACKING LINES (DECORATIVE) --
                l_eye = face_lms.landmark[33] # Inner eye corner
                r_eye = face_lms.landmark[263] 
                lex, ley = int(l_eye.x * w), int(l_eye.y * h)
                rex, rey = int(r_eye.x * w), int(r_eye.y * h)
                cv2.line(hud, (lex, ley), (face_center[0]-20, face_center[1]-20), CYAN, 1)
                cv2.line(hud, (rex, rey), (face_center[0]+20, face_center[1]-20), CYAN, 1)
                
                # -- CALCULATE HEAD POSE (Approximate) --
                # Determine looking left/right based on nose x vs mean(ears x)
                l_ear_x = face_lms.landmark[234].x
                r_ear_x = face_lms.landmark[454].x
                mid_x = (l_ear_x + r_ear_x) / 2
                
                # "100" is a sensitivity multiplier
                val_turning = (nose_tip.x - mid_x) * 100 
                
                # Mouth Distance (Upper lip 13, Lower lip 14)
                up_lip = face_lms.landmark[13].y
                low_lip = face_lms.landmark[14].y
                mouth_open_dist = (low_lip - up_lip) * 100

                # -- MENU LOGIC --
                threshold_turn = 4.0
                
                # LEFT TILT -> CHANGE COLOR
                if val_turning < -threshold_turn:
                    selection_timer += 1
                    cv2.putText(hud, f"<< COLOR >> {int((selection_timer/selection_trigger_limit)*100)}%", (face_center[0]-200, face_center[1]), cv2.FONT_HERSHEY_PLAIN, 2, COLORS[curr_color_idx], 2)
                    if selection_timer > selection_trigger_limit and not switch_lock:
                        curr_color_idx = (curr_color_idx + 1) % len(COLORS)
                        switch_lock = True
                        selection_timer = 0
                
                # RIGHT TILT -> CHANGE TOOL
                elif val_turning > threshold_turn:
                    selection_timer += 1
                    cv2.putText(hud, f">> TOOL << {int((selection_timer/selection_trigger_limit)*100)}%", (face_center[0]+80, face_center[1]), cv2.FONT_HERSHEY_PLAIN, 2, CYAN, 2)
                    if selection_timer > selection_trigger_limit and not switch_lock:
                        curr_tool_idx = (curr_tool_idx + 1) % len(TOOLS)
                        switch_lock = True
                        selection_timer = 0
                
                else:
                    # Reset lock when head returns to center
                    selection_timer = 0
                    switch_lock = False

                # MOUTH OPEN -> CLEAR ALL
                if mouth_open_dist > 5:
                    cv2.putText(hud, "CLEARING...", (face_center[0]-50, face_center[1]+100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, RED, 2)
                    if mouth_open_dist > 8: # Really open
                        shapes = []

        # 2. PROCESS HANDS (Interaction)
        res_hands = hands.process(rgb)
        
        # Defaults
        r_idx = None
        l_idx = None
        r_pinch = False
        l_pinch = False
        
        if res_hands.multi_hand_landmarks:
            for hand_lms, handedness in zip(res_hands.multi_hand_landmarks, res_hands.multi_handedness):
                label = handedness.classification[0].label
                h, w, c = img.shape
                
                # Landmarks
                idx_x, idx_y = int(hand_lms.landmark[8].x * w), int(hand_lms.landmark[8].y * h)
                th_x, th_y = int(hand_lms.landmark[4].x * w), int(hand_lms.landmark[4].y * h)
                dist = math.hypot(idx_x - th_x, idx_y - th_y)
                is_pinch = dist < 40
                
                if label == "Right":
                    r_idx = (idx_x, idx_y)
                    r_pinch = is_pinch
                    # Draw Stylized Cursor
                    color = COLORS[curr_color_idx]
                    cv2.line(hud, r_idx, (r_idx[0]+10, r_idx[1]+10), color, 2)
                    cv2.line(hud, r_idx, (r_idx[0]-10, r_idx[1]-10), color, 2)
                    cv2.line(hud, r_idx, (r_idx[0]+10, r_idx[1]-10), color, 2)
                    cv2.line(hud, r_idx, (r_idx[0]-10, r_idx[1]+10), color, 2)
                    
                else: # Left
                    l_idx = (idx_x, idx_y)
                    l_pinch = is_pinch
                    cv2.circle(hud, l_idx, 20, (200,200,200), 1) # Grab cursor
                    
        # --- LOGIC CORE ---
        
        # A. RIGHT HAND DRAWING
        tool = TOOLS[curr_tool_idx]
        color = COLORS[curr_color_idx]
        
        if r_idx:
            rx, ry = r_idx
            
            if r_pinch and not active_r_pinch:
                # START DRAW
                active_r_pinch = True
                if tool == "BRUSH":
                    shapes.append(Shape("PATH", [(rx,ry)], color))
                else:
                    drawing_anchor = (rx, ry)
            
            elif r_pinch and active_r_pinch:
                # DRAG
                if tool == "BRUSH":
                    if shapes: shapes[-1].params.append((rx,ry))
                elif tool == "RECT" and drawing_anchor:
                    # Draw temporary Preview on HUD
                    cv2.rectangle(hud, drawing_anchor, (rx, ry), color, 1)
                elif tool == "CIRCLE" and drawing_anchor:
                    rad = int(math.hypot(rx-drawing_anchor[0], ry-drawing_anchor[1]))
                    cv2.circle(hud, drawing_anchor, rad, color, 1)
                    
            elif not r_pinch and active_r_pinch:
                # RELEASE
                active_r_pinch = False
                if tool == "RECT" and drawing_anchor:
                    w = rx - drawing_anchor[0]
                    h = ry - drawing_anchor[1]
                    shapes.append(Shape("RECT", [min(drawing_anchor[0], rx), min(drawing_anchor[1], ry), abs(w), abs(h)], color))
                elif tool == "CIRCLE" and drawing_anchor:
                    rad = int(math.hypot(rx-drawing_anchor[0], ry-drawing_anchor[1]))
                    shapes.append(Shape("CIRCLE", [drawing_anchor[0], drawing_anchor[1], rad], color))
                drawing_anchor = None

        # B. LEFT HAND MOVING
        if l_idx:
            lx, ly = l_idx
            
            if l_pinch and not active_l_pinch:
                # ATTEMPT GRAB
                active_l_pinch = True
                # Find top-most shape under hand
                for i in range(len(shapes)-1, -1, -1):
                    if shapes[i].is_inside(lx, ly):
                        held_shape_idx = i
                        # Calculate grab offset
                        s = shapes[i]
                        if s.type == "RECT" or s.type == "CIRCLE":
                            s.offset = (lx - s.params[0], ly - s.params[1])
                        elif s.type == "PATH":
                             s.offset = (lx - s.params[0][0], ly - s.params[0][1])
                        break
            
            elif l_pinch and active_l_pinch:
                if held_shape_idx != -1:
                    shapes[held_shape_idx].move(lx, ly)
                    cv2.line(hud, l_idx, (int(face_center[0]), int(face_center[1])), TEAL, 1) # Connection line to Face
            
            elif not l_pinch:
                active_l_pinch = False
                held_shape_idx = -1

        # --- DRAW FINAL ---
        
        # 1. Background Shapes
        for i, shape in enumerate(shapes):
            shape.draw(img, is_hovered=(i==held_shape_idx))
            
        # 2. Status UI (Top Corner)
        cv2.putText(img, f"TOOL: {tool}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, CYAN, 2)
        cv2.putText(img, f"COLOR: {COLOR_NAMES[curr_color_idx]}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS[curr_color_idx], 2)
        
        # 3. Add HUD Overlay (Add transparent glow)
        img = cv2.add(img, hud)
        
        cv2.imshow("JARVIS MODE", img)
        if cv2.waitKey(1) == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()