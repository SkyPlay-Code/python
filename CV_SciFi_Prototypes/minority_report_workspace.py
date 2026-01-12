import cv2
import mediapipe as mp
import numpy as np
import math
import random

# --- CONFIG ---
WIDTH, HEIGHT = 1280, 720
BG_COLOR = (10, 10, 20)      # Deep Cyber Blue/Black
GRID_COLOR = (50, 100, 100)  # Tron Grid lines
PINCH_THRESH = 40            # Pixel dist to trigger "Grab"
FRICTION = 0.85              # Physics friction (0.0 - 1.0)
THROW_FORCE = 0.5            # Multiplier for throw speed

# --- ASSETS GEN (Cyberpunk UI colors) ---
COLORS = [
    (0, 255, 255), # Cyan
    (255, 0, 255), # Magenta
    (0, 255, 0),   # Neon Green
    (0, 165, 255)  # Orange
]

# --- CLASSES ---

class Hologram:
    def __init__(self, x, y, w, h, content_type):
        self.rect = [x, y, w, h] # x, y, w, h
        self.color = random.choice(COLORS)
        self.type = content_type
        # Physics props
        self.vx = 0
        self.vy = 0
        self.grabbed = False
        self.scaling = False
        
        # Smooth Scale logic
        self.initial_w = w
        self.initial_h = h
        
        # Fake Content Data
        self.data_points = np.random.randint(h//2, h, 20)

    def update_physics(self):
        # If let go, slide (Inertia)
        if not self.grabbed and not self.scaling:
            self.rect[0] += self.vx
            self.rect[1] += self.vy
            self.vx *= FRICTION
            self.vy *= FRICTION
            
            # Stop if very slow
            if abs(self.vx) < 0.5: self.vx = 0
            if abs(self.vy) < 0.5: self.vy = 0

    def draw(self, canvas, overlay_alpha):
        x, y, w, h = map(int, self.rect)
        
        # Determine Draw Color (Highlight if grabbed)
        c = (255, 255, 255) if self.grabbed else self.color
        
        # 1. Glass Pane Background (Translucent)
        sub_img = overlay_alpha[y:y+h, x:x+w]
        white_rect = np.full(sub_img.shape, self.color, dtype=np.uint8)
        res = cv2.addWeighted(sub_img, 0.7, white_rect, 0.3, 1.0)
        overlay_alpha[y:y+h, x:x+w] = res
        
        # 2. Border & Corners
        cv2.rectangle(canvas, (x, y), (x+w, y+h), c, 2)
        len_corner = 20
        cv2.line(canvas, (x,y), (x+len_corner, y), c, 4)
        cv2.line(canvas, (x,y), (x, y+len_corner), c, 4)
        cv2.line(canvas, (x+w,y+h), (x+w-len_corner, y+h), c, 4)
        cv2.line(canvas, (x+w,y+h), (x+w, y+h-len_corner), c, 4)
        
        # 3. Content (Fake UI)
        if self.type == "DATA":
            # Draw fake graph
            for i in range(len(self.data_points)-1):
                pt1 = (x + int(i * (w/20)), y + h - (self.data_points[i] - h//2))
                pt2 = (x + int((i+1) * (w/20)), y + h - (self.data_points[i+1] - h//2))
                # Normalize points to fit scaled window
                norm_pt1 = (int(x + i * (w/20)), int(y + (self.data_points[i]/150)*h))
                norm_pt2 = (int(x + (i+1) * (w/20)), int(y + (self.data_points[i+1]/150)*h))
                
                # Simple centered text for stability
                cv2.putText(canvas, "DATA STREAM", (x+10, y+30), cv2.FONT_HERSHEY_PLAIN, 1.5, c, 1)
                cv2.line(canvas, (x, y+h//2), (x+w, y+h//2), c, 1)
        
        elif self.type == "IMAGE":
            cv2.circle(canvas, (x+w//2, y+h//2), int(h/3), c, 2)
            cv2.line(canvas, (x,y), (x+w, y+h), c, 1)
            cv2.line(canvas, (x+w,y), (x, y+h), c, 1)
            cv2.putText(canvas, "IMG_FILE_09", (x+10, y+h-10), cv2.FONT_HERSHEY_PLAIN, 1, c, 1)

    def is_hover(self, mx, my):
        x, y, w, h = self.rect
        return x < mx < x + w and y < my < y + h

    def set_pos(self, mx, my, offset_x, offset_y):
        self.rect[0] = mx - offset_x
        self.rect[1] = my - offset_y

    def scale(self, factor):
        # Center scaling (math heavy)
        cx = self.rect[0] + self.rect[2]/2
        cy = self.rect[1] + self.rect[3]/2
        
        new_w = max(50, self.rect[2] * factor)
        new_h = max(50, self.rect[3] * factor)
        
        self.rect[0] = cx - new_w/2
        self.rect[1] = cy - new_h/2
        self.rect[2] = new_w
        self.rect[3] = new_h

# --- MAIN ENGINE ---

def draw_cyber_grid(img, tick):
    """ Procedural Grid Background """
    h, w, c = img.shape
    img[:] = BG_COLOR # Fill BG
    
    # Moving vertical lines
    gap = 60
    shift = int(tick % gap)
    
    for x in range(shift, w, gap):
        alpha = 0.2
        if x % (gap*4) == shift: alpha = 0.4 # Brighter major lines
        color = tuple(int(c * 255) for c in (alpha, alpha, alpha)) # Greyish
        cv2.line(img, (x, 0), (x, h), GRID_COLOR, 1)
    
    # Horizontal lines (Floor perception)
    for y in range(h//2, h, 40):
        cv2.line(img, (0, y), (w, y), GRID_COLOR, 1)

    # Sun / Horizon
    cv2.circle(img, (w//2, h//2 - 50), 100, (30, 30, 0), -1) 
    cv2.blur(img, (3,3), img)

def main():
    # Setup Models
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.6, max_num_hands=2)
    
    mp_selfie = mp.solutions.selfie_segmentation
    segmenter = mp_selfie.SelfieSegmentation(model_selection=1) # 1 = landscape mode (more robust)

    address = "http://192.0.0.4:8080/video"
    cap = cv2.VideoCapture(address)
    cap.set(3, WIDTH)
    cap.set(4, HEIGHT)

    # Windows Store
    windows = [
        Hologram(100, 200, 250, 150, "DATA"),
        Hologram(800, 200, 200, 200, "IMAGE"),
        Hologram(500, 400, 300, 100, "DATA"),
    ]

    tick = 0
    drag_offset = (0,0)
    dragged_obj = None
    
    # Multi-hand Scale State
    scaling_obj = None
    init_scale_dist = 0

    print("--- HOLODECK INITIALIZED ---")

    while True:
        tick += 1
        success, raw_img = cap.read()
        if not success: break
        
        # 1. SEGMENTATION & BACKGROUND (The "Holodeck" effect)
        raw_img = cv2.flip(raw_img, 1)
        rgb_img = cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB)
        
        # Get Mask
        seg_result = segmenter.process(rgb_img)
        condition = np.stack((seg_result.segmentation_mask,) * 3, axis=-1) > 0.6
        
        # Create Background
        bg_image = np.zeros_like(raw_img)
        draw_cyber_grid(bg_image, tick * 2) # Animate grid
        
        # Composite: Person + Sci-Fi BG
        final_scene = np.where(condition, raw_img, bg_image)
        
        # 2. HAND PROCESSING
        hand_result = hands.process(rgb_img)
        
        r_pinch, r_pos = False, None
        l_pinch, l_pos = False, None
        
        hands_list = [] # Store logical hands [(label, x, y, is_pinch), ...]

        if hand_result.multi_hand_landmarks:
            for hand_lms, handedness in zip(hand_result.multi_hand_landmarks, hand_result.multi_handedness):
                label = handedness.classification[0].label # Right / Left
                
                # 8 = Index Tip, 4 = Thumb Tip
                ix, iy = int(hand_lms.landmark[8].x * WIDTH), int(hand_lms.landmark[8].y * HEIGHT)
                tx, ty = int(hand_lms.landmark[4].x * WIDTH), int(hand_lms.landmark[4].y * HEIGHT)
                
                # Pinch Detection
                dist = math.hypot(ix-tx, iy-ty)
                is_pinch = dist < PINCH_THRESH
                center = ((ix+tx)//2, (iy+ty)//2)
                
                hands_list.append({'label': label, 'pos': center, 'pinch': is_pinch, 'idx_tip':(ix,iy)})

                # Visualize Finger interactions
                color = (0, 255, 0) if is_pinch else (200, 200, 200)
                cv2.circle(final_scene, center, 8, color, -1)
                if is_pinch:
                     cv2.line(final_scene, (ix, iy), (tx, ty), (0, 255, 255), 2)

                # Set global helper vars for logic
                if label == "Right": r_pos, r_pinch = center, is_pinch
                if label == "Left":  l_pos, l_pinch = center, is_pinch

        # 3. INTERACTION LOGIC
        
        # SCALING (Two hands pinching same object OR just two hands pinching generally)
        if r_pinch and l_pinch and r_pos and l_pos:
            curr_dist = math.hypot(r_pos[0]-l_pos[0], r_pos[1]-l_pos[1])
            
            # Find center point between hands
            mid_x, mid_y = (r_pos[0]+l_pos[0])//2, (r_pos[1]+l_pos[1])//2
            cv2.line(final_scene, r_pos, l_pos, (255, 255, 0), 1, cv2.LINE_AA) # Connect hands
            
            if not scaling_obj:
                # Find which object is roughly between hands or targeted by one
                for w_obj in reversed(windows): # check top first
                    # Loose check: is the midpoint inside or near the object?
                    if w_obj.is_hover(mid_x, mid_y):
                        scaling_obj = w_obj
                        init_scale_dist = curr_dist
                        w_obj.scaling = True
                        w_obj.grabbed = False # Override grab
                        dragged_obj = None    # Override drag
                        break
            elif scaling_obj:
                # Calculate scale delta
                ratio = 1.0
                if init_scale_dist > 0:
                    ratio = 1.0 + (curr_dist - init_scale_dist) / 400.0 # dampening factor
                    scaling_obj.scale(ratio)
                    init_scale_dist = curr_dist # Reset for relative scaling next frame
                    
                    cv2.putText(final_scene, "RE-SIZING", (mid_x-30, mid_y-20), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), 1)

        else:
            # RESET SCALE STATE
            if scaling_obj: 
                scaling_obj.scaling = False
                scaling_obj = None

            # DRAGGING (Single Hand)
            # Prioritize Right Hand for simple demo logic, but could do loop
            active_hand = None
            if r_pinch: active_hand = r_pos
            elif l_pinch: active_hand = l_pos
            
            if active_hand:
                hx, hy = active_hand
                
                # New Grab
                if not dragged_obj:
                    for w_obj in reversed(windows):
                        if w_obj.is_hover(hx, hy):
                            dragged_obj = w_obj
                            dragged_obj.grabbed = True
                            # Record Offset so it doesn't snap to center
                            drag_offset = (hx - w_obj.rect[0], hy - w_obj.rect[1])
                            
                            # Nullify inertia
                            dragged_obj.vx = 0
                            dragged_obj.vy = 0
                            break
                
                # Continuing Grab
                elif dragged_obj:
                    # History for "Throwing" calculation
                    prev_x, prev_y = dragged_obj.rect[0], dragged_obj.rect[1]
                    
                    # Update Pos
                    dragged_obj.set_pos(hx, hy, drag_offset[0], drag_offset[1])
                    
                    # Calculate velocity for next frame (Instant velocity)
                    dragged_obj.vx = (dragged_obj.rect[0] - prev_x) * THROW_FORCE
                    dragged_obj.vy = (dragged_obj.rect[1] - prev_y) * THROW_FORCE
                    
                    # Draw Tether line
                    cv2.line(final_scene, active_hand, (int(dragged_obj.rect[0]+drag_offset[0]), int(dragged_obj.rect[1]+drag_offset[1])), (0, 100, 255), 1)

            else:
                # RELEASE
                if dragged_obj:
                    dragged_obj.grabbed = False
                    dragged_obj = None

        # 4. PHYSICS & CLEANUP
        for w_obj in windows:
            w_obj.update_physics()
            
            # Boundary checks - Bounce
            if w_obj.rect[0] < 0: w_obj.vx = abs(w_obj.vx)
            if w_obj.rect[0] + w_obj.rect[2] > WIDTH: w_obj.vx = -abs(w_obj.vx)
            if w_obj.rect[1] < 0: w_obj.vy = abs(w_obj.vy)
            if w_obj.rect[1] + w_obj.rect[3] > HEIGHT: w_obj.vy = -abs(w_obj.vy)

            # Draw Window
            w_obj.draw(final_scene, final_scene)

        # 5. UI Stats
        cv2.putText(final_scene, f"HANDS: {len(hands_list)}", (20, 30), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 255, 0), 2)
        if dragged_obj: cv2.putText(final_scene, "ACTION: DRAG", (20, 50), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 165, 255), 2)
        if scaling_obj: cv2.putText(final_scene, "ACTION: SCALE", (20, 50), cv2.FONT_HERSHEY_PLAIN, 1.2, (255, 0, 255), 2)
        
        cv2.imshow("HOLO-DECK", final_scene)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()