import math

# --- Helper function for input validation ---
def get_positive_float_input(prompt):
    """Prompts user for a positive floating-point number and validates the input."""
    while True:
        try:
            value_str = input(prompt)
            value = float(value_str)
            if value <= 0:
                print("Input must be a positive number. Please try again.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")
        except EOFError:
            print("\nInput stream closed. Exiting.")
            exit()

# --- Calculation functions for each shape ---

def calculate_sphere():
    """Calculates properties for a sphere."""
    print("\n--- Sphere Calculations ---")
    radius = get_positive_float_input("Enter the radius of the sphere: ")

    volume = (4/3) * math.pi * (radius ** 3)
    surface_area = 4 * math.pi * (radius ** 2) # For a sphere, surface area and total surface area are the same
    diameter = 2 * radius # Often considered the 'diagonal' in a simple sense

    print(f"\nResults for Sphere (Radius = {radius}):")
    print(f"  Volume: {volume:.4f}")
    print(f"  Surface Area: {surface_area:.4f}")
    print(f"  Total Surface Area: {surface_area:.4f}") # Same as Surface Area for sphere
    print(f"  Diameter (often considered diagonal): {diameter:.4f}") # Sphere doesn't have a space diagonal in the same way as polyhedra

def calculate_cube():
    """Calculates properties for a cube."""
    print("\n--- Cube Calculations ---")
    side = get_positive_float_input("Enter the side length of the cube: ")

    volume = side ** 3
    face_surface_area = side ** 2 # Area of one face
    total_surface_area = 6 * face_surface_area # Area of all 6 faces
    diagonal = side * math.sqrt(3) # Space diagonal

    print(f"\nResults for Cube (Side = {side}):")
    print(f"  Volume: {volume:.4f}")
    print(f"  Face Surface Area: {face_surface_area:.4f}")
    print(f"  Total Surface Area: {total_surface_area:.4f}")
    print(f"  Space Diagonal: {diagonal:.4f}")

def calculate_cuboid():
    """Calculates properties for a cuboid."""
    print("\n--- Cuboid Calculations ---")
    length = get_positive_float_input("Enter the length of the cuboid: ")
    width = get_positive_float_input("Enter the width of the cuboid: ")
    height = get_positive_float_input("Enter the height of the cuboid: ")

    volume = length * width * height
    lateral_surface_area = 2 * height * (length + width) # Area of the four side faces
    total_surface_area = 2 * ((length * width) + (length * height) + (width * height)) # Area of all 6 faces
    diagonal = math.sqrt((length ** 2) + (width ** 2) + (height ** 2)) # Space diagonal

    print(f"\nResults for Cuboid (Length = {length}, Width = {width}, Height = {height}):")
    print(f"  Volume: {volume:.4f}")
    print(f"  Lateral Surface Area: {lateral_surface_area:.4f}")
    print(f"  Total Surface Area: {total_surface_area:.4f}")
    print(f"  Space Diagonal: {diagonal:.4f}")

def calculate_cylinder():
    """Calculates properties for a cylinder."""
    print("\n--- Cylinder Calculations ---")
    radius = get_positive_float_input("Enter the radius of the cylinder's base: ")
    height = get_positive_float_input("Enter the height of the cylinder: ")

    volume = math.pi * (radius ** 2) * height
    lateral_surface_area = 2 * math.pi * radius * height # Area of the curved surface
    total_surface_area = (2 * math.pi * (radius ** 2)) + lateral_surface_area # Area of two bases + lateral area

    print(f"\nResults for Cylinder (Radius = {radius}, Height = {height}):")
    print(f"  Volume: {volume:.4f}")
    print(f"  Lateral Surface Area: {lateral_surface_area:.4f}")
    print(f"  Total Surface Area: {total_surface_area:.4f}")
    print("  Diagonal: Not a standard calculation for a cylinder.")

def calculate_hemisphere():
    """Calculates properties for a hemisphere."""
    print("\n--- Hemisphere Calculations ---")
    radius = get_positive_float_input("Enter the radius of the hemisphere: ")

    volume = (2/3) * math.pi * (radius ** 3) # Half the volume of a sphere
    curved_surface_area = 2 * math.pi * (radius ** 2) # Half the surface area of a sphere
    total_surface_area = curved_surface_area + (math.pi * (radius ** 2)) # Curved area + area of the base circle

    print(f"\nResults for Hemisphere (Radius = {radius}):")
    print(f"  Volume: {volume:.4f}")
    print(f"  Curved Surface Area: {curved_surface_area:.4f}")
    print(f"  Total Surface Area: {total_surface_area:.4f}")
    print("  Diagonal: Not a standard calculation for a hemisphere.")

def calculate_cone():
    """Calculates properties for a cone."""
    print("\n--- Cone Calculations ---")
    radius = get_positive_float_input("Enter the radius of the cone's base: ")
    height = get_positive_float_input("Enter the height of the cone: ")

    slant_height = math.sqrt((radius ** 2) + (height ** 2)) # Calculate slant height
    volume = (1/3) * math.pi * (radius ** 2) * height
    lateral_surface_area = math.pi * radius * slant_height # Area of the curved surface
    total_surface_area = (math.pi * (radius ** 2)) + lateral_surface_area # Area of base circle + lateral area

    print(f"\nResults for Cone (Radius = {radius}, Height = {height}):")
    print(f"  Slant Height: {slant_height:.4f}")
    print(f"  Volume: {volume:.4f}")
    print(f"  Lateral Surface Area: {lateral_surface_area:.4f}")
    print(f"  Total Surface Area: {total_surface_area:.4f}")
    print("  Diagonal: Not a standard calculation for a cone.")

# --- Main program loop ---
def main():
    """Displays the menu and handles user shape selection."""
    while True:
        print("\n--- Geometric Property Calculator ---")
        print("Select a shape:")
        print("1. Sphere")
        print("2. Cube")
        print("3. Cuboid")
        print("4. Cylinder")
        print("5. Hemisphere")
        print("6. Cone")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            calculate_sphere()
        elif choice == '2':
            calculate_cube()
        elif choice == '3':
            calculate_cuboid()
        elif choice == '4':
            calculate_cylinder()
        elif choice == '5':
            calculate_hemisphere()
        elif choice == '6':
            calculate_cone()
        elif choice == '7':
            print("\nExiting the calculator. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

        # Ask if the user wants to perform another calculation
        if choice != '7':
            while True:
                another_calculation = input("\nPerform another calculation? (yes/no): ").lower()
                if another_calculation in ["yes", "no"]:
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")
            if another_calculation == 'no':
                print("\nExiting the calculator. Goodbye!")
                break


# --- How to run this script ---
# Save this code as a Python file (e.g., geometric_calculator.py).
# Open a terminal or command prompt.
# Navigate to the directory where you saved the file.
# Run the script using the command: python geometric_calculator.py
# The program will then start in your terminal, presenting the menu.
# -----------------------------

# Run the main function when the script is executed
if __name__ == "__main__":
    main()