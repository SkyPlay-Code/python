import math
import os
import sys
import time

class SpinningDonut:
    """
    A class for rendering a spinning ASCII donut that correctly adapts to terminal size
    and maintains a stable, centered position.
    """
    def __init__(self, target_fps=30):
        """
        Initializes the SpinningDonut object.

        Args:
            target_fps (int): The desired frames per second for the animation.
        """
        # Constants for rendering
        self.ASPECT_RATIO_CORRECTION = 0.5
        self.LUMINANCE_SCALE = 8
        self.THETA_SPACING = 0.07
        self.PHI_SPACING = 0.02
        
        self.A = 0  # Rotation angle around X-axis
        self.B = 0  # Rotation angle around Z-axis
        
        # Optimized rotation speeds for a pleasant animation
        self.rot_speed_a = 0.04
        self.rot_speed_b = 0.02
        
        self.target_fps = target_fps
        self.frame_time = 1 / self.target_fps

        # Donut geometry constants
        self.R1 = 1  # Radius of the donut's tube
        self.R2 = 2  # Distance from center of donut to center of tube
        self.K2 = 5  # Distance from viewer to the 2D projection plane
        
        # Characters for illumination, from dark to bright
        self.illumination = ".,-~:;=!*#$@"
        
        # Set initial dimensions. These will be updated dynamically in the main loop.
        self.width, self.height = self._get_terminal_size()
        self._update_dimensions()

    def _get_terminal_size(self):
        """Helper method to get terminal size, with a fallback."""
        try:
            return os.get_terminal_size()
        except OSError:
            return 80, 24 # A common default if size can't be determined

    def _update_dimensions(self):
        """Recalculates screen-dependent parameters when terminal size changes."""
        self.screen_size = self.width * self.height
        
        # Buffers for screen characters and their depth
        self.output_buffer = [' '] * self.screen_size
        self.z_buffer = [0.0] * self.screen_size
        
        # K1: Scaling factor for projection, based on terminal width for proper fitting
        self.K1 = self.width * self.K2 * 3 / (8 * (self.R1 + self.R2))
    
    def render_frame(self):
        """Renders a single frame of the donut animation."""
        # Reset buffers for the new frame
        self.output_buffer = [' '] * self.screen_size
        self.z_buffer = [0.0] * self.screen_size
        
        # Precompute sines and cosines for efficiency
        cosA, sinA = math.cos(self.A), math.sin(self.A)
        cosB, sinB = math.cos(self.B), math.sin(self.B)
        
        # Loop through the surface of the torus
        theta = 0
        while theta < 2 * math.pi:
            costheta, sintheta = math.cos(theta), math.sin(theta)
            phi = 0
            while phi < 2 * math.pi:
                cosphi, sinphi = math.cos(phi), math.sin(phi)
                
                # --- 3D Coordinate Calculation ---
                circlex = self.R2 + self.R1 * costheta
                circley = self.R1 * sintheta

                x = circlex * (cosB * cosphi + sinA * sinB * sinphi) - circley * cosA * sinB
                y = circlex * (sinB * cosphi - sinA * cosB * sinphi) + circley * cosA * cosB
                z = self.K2 + cosA * circlex * sinphi + circley * sinA
                ooz = 1 / z if z != 0 else 0

                # --- 2D Projection ---
                # This projects the 3D point (x,y,z) onto the 2D screen
                xp = int(self.width / 2 + self.K1 * ooz * x)
                # IMPORTANT: Correcting for aspect ratio by multiplying y-coordinate projection.
                # Terminal characters are taller than they are wide. This makes the donut circular.
                yp = int(self.height / 2 - 0.5 * self.K1 * ooz * y)

                # --- Illumination ---
                # Calculates lighting based on surface normal relative to a light source
                L = cosphi * costheta * sinB - cosA * costheta * sinphi - sinA * sintheta + cosB * (cosA * sintheta - costheta * sinA * sinphi)
                
                if L > 0 and 0 <= xp < self.width and 0 <= yp < self.height:
                    idx = xp + self.width * yp
                    if ooz > self.z_buffer[idx]:
                        self.z_buffer[idx] = ooz
                        luminance_index = min(int(L * 8), len(self.illumination) - 1)
                        self.output_buffer[idx] = self.illumination[luminance_index]

                phi += 0.02
            theta += 0.07

    def run(self):
        """Starts the main animation loop."""
        # Hide cursor for a clean display
        sys.stdout.write("\x1b[?25l")
        sys.stdout.flush()

        last_width, last_height = -1, -1

        try:
            while True:
                frame_start_time = time.time()
                
                # Check for terminal resize and update dimensions if necessary
                current_width, current_height = self._get_terminal_size()
                if current_width != last_width or current_height != last_height:
                    self.width, self.height = current_width, current_height
                    self._update_dimensions()
                    last_width, last_height = current_width, current_height

                # Render all the math for the frame
                self.render_frame()
                
                # --- BUG FIX: PROPER PRINTING LOGIC ---
                # First, clear the screen and move cursor to the top-left
                sys.stdout.write("\x1b[2J\x1b[H")

                # Second, build the frame string with manual newlines
                frame_string = ""
                for i in range(self.height):
                    start_index = i * self.width
                    end_index = start_index + self.width
                    frame_string += "".join(self.output_buffer[start_index:end_index]) + "\n"
                
                # Third, print the entire reconstructed frame at once
                sys.stdout.write(frame_string)
                sys.stdout.flush()
                
                # Update rotation angles
                self.A += self.rot_speed_a
                self.B += self.rot_speed_b

                # Maintain a stable frame rate
                time_elapsed = time.time() - frame_start_time
                sleep_duration = self.frame_time - time_elapsed
                if sleep_duration > 0:
                    time.sleep(sleep_duration)

        except KeyboardInterrupt:
            # Restore cursor on exit
            sys.stdout.write("\x1b[?25h")
            sys.stdout.flush()
            print("\nDonut animation stopped.")

if __name__ == "__main__":
    donut = SpinningDonut(target_fps=60)
    donut.run()