import cv2
import mediapipe as mp
import numpy as np
import math
import random
from collections import deque

class EtherealParticles:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, velocity_x, velocity_y, color):
        """Spawns particles that drift based on eye movement momentum"""
        for _ in range(5):  # Emit burst
            p = {
                'x': x,
                'y': y,
                'vx': velocity_x * -0.5 + random.uniform(-2, 2), # Drag effect
                'vy': velocity_y * -0.5 + random.uniform(-2, 2),
                'life': 1.0,
                'decay': random.uniform(0.02, 0.06),
                'color': color,
                'size': random.uniform(1, 3)
            }
            self.particles.append(p)

    def update_and_draw(self, canvas):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= p['decay']
            
            if p['life'] <= 0:
                self.particles.remove(p)
                continue
                
            # Fade out
            alpha = p['life']
            radius = int(p['size'] * alpha)
            if radius < 1: radius = 1
            
            # Draw glow
            color = p['color'] # BGR tuple
            # Modulate intensity by alpha
            faded_color = (int(color[0]*alpha), int(color[1]*alpha), int(color[2]*alpha))
            
            cv2.circle(canvas, (int(p['x']), int(p['y'])), radius, faded_color, -1)

class SoulMirror:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.cap = cv2.VideoCapture(0)
        
        # Art State
        self.particles = EtherealParticles()
        self.history_left = deque(maxlen=20) # For smooth trails
        self.history_right = deque(maxlen=20)
        
        # Indices for landmarks
        self.LEFT_PUPIL = 468
        self.RIGHT_PUPIL = 473
        
        # Color Cycle
        self.hue = 0

    def get_coords(self, landmark, w, h):
        return int(landmark.x * w), int(landmark.y * h)

    def draw_mandala(self, img, center, radius, hue_offset):
        """Draws a rotating geometric pattern around the eye"""
        x, y = center
        
        # Calculate rotating vertices
        time_val = cv2.getTickCount() / cv2.getTickFrequency()
        num_points = 6
        
        points = []
        for i in range(num_points):
            angle = (2 * math.pi * i / num_points) + (time_val * 2)
            px = int(x + radius * math.cos(angle))
            py = int(y + radius * math.sin(angle))
            points.append([px, py])
            
        points = np.array(points, np.int32)
        
        # Color based on hue
        hsv_color = np.uint8([[[ (self.hue + hue_offset) % 180, 200, 255 ]]])
        bgr_color = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]
        color_tuple = (int(bgr_color[0]), int(bgr_color[1]), int(bgr_color[2]))

        # Draw hexagon
        cv2.polylines(img, [points], True, color_tuple, 1, cv2.LINE_AA)
        
        # Draw connecting lines to center
        for pt in points:
            cv2.line(img, (x, y), tuple(pt), color_tuple, 1, cv2.LINE_AA)

    def run(self):
        cv2.namedWindow('Soul Mirror', cv2.WINDOW_NORMAL)
        
        # Initialize canvas (black)
        ret, frame = self.cap.read()
        h, w, c = frame.shape
        # Create a persistent canvas for trails
        trail_canvas = np.zeros((h, w, c), np.uint8)

        with self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7) as face_mesh:
            
            while self.cap.isOpened():
                success, frame = self.cap.read()
                if not success: break
                
                # Mirror for intuitiveness
                frame = cv2.flip(frame, 1)
                
                # Make the camera feed dark/ethereal (Desaturate and Darken)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR) # Back to 3 channels
                frame_bg = (gray * 0.2).astype(np.uint8) # Dark ghostly background
                
                # Fade the trail canvas (old trails disappear slowly)
                # We multiply by < 1.0 to dim existing pixels
                trail_canvas = cv2.addWeighted(trail_canvas, 0.85, np.zeros_like(trail_canvas), 0, 0)
                
                # Inference
                results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        # 1. Get Coordinates
                        left_pt = self.get_coords(face_landmarks.landmark[self.LEFT_PUPIL], w, h)
                        right_pt = self.get_coords(face_landmarks.landmark[self.RIGHT_PUPIL], w, h)
                        
                        # 2. Update History
                        self.history_left.append(left_pt)
                        self.history_right.append(right_pt)
                        
                        # 3. Calculate Velocity (simple delta)
                        if len(self.history_left) > 2:
                            prev_x, prev_y = self.history_left[-2]
                            dx = left_pt[0] - prev_x
                            dy = left_pt[1] - prev_y
                            
                            # 4. Color Generation (Rainbow Cycle)
                            self.hue = (self.hue + 2) % 180
                            hsv = np.uint8([[[self.hue, 255, 255]]])
                            color_main = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0]
                            c_tuple = (int(color_main[0]), int(color_main[1]), int(color_main[2]))
                            
                            # 5. Emit Particles (Physics)
                            speed = math.hypot(dx, dy)
                            if speed > 2: # Only emit if moving
                                self.particles.emit(left_pt[0], left_pt[1], dx, dy, c_tuple)
                                self.particles.emit(right_pt[0], right_pt[1], dx, dy, c_tuple)

                            # 6. Draw Mandala Geometry (on current frame layer)
                            mandala_layer = np.zeros_like(frame_bg)
                            
                            # Connecting beam
                            cv2.line(mandala_layer, left_pt, right_pt, c_tuple, 1, cv2.LINE_AA)
                            
                            # Rotating Hexagons
                            radius_l = 20 + int(speed * 2) # Gets bigger when moving fast
                            self.draw_mandala(mandala_layer, left_pt, radius_l, 0)
                            self.draw_mandala(mandala_layer, right_pt, radius_l, 30)
                            
                            # Add Mandala Glow to trail canvas
                            # This stamps the shape into the "long exposure" layer
                            cv2.addWeighted(trail_canvas, 1.0, mandala_layer, 0.5, 0, trail_canvas)

                # Update particles
                particle_layer = np.zeros_like(frame_bg)
                self.particles.update_and_draw(particle_layer)
                
                # --- FINAL COMPOSITION ---
                # 1. Start with Ghostly Background
                final = frame_bg
                
                # 2. Add the Long Exposure Trails (Linear Dodge for glow effect)
                final = cv2.add(final, trail_canvas)
                
                # 3. Add Particles on top (crisp)
                final = cv2.add(final, particle_layer)
                
                cv2.imshow('Soul Mirror', final)
                
                key = cv2.waitKey(5) & 0xFF
                if key == 27: # ESC
                    break
                if key == ord('c'): # Clear trails
                    trail_canvas = np.zeros_like(trail_canvas)
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = SoulMirror()
    app.run()