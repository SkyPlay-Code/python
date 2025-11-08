import re             # Helps in checking whether the input matches a particular pattern, like email or phone number.
import random         # Used to generate random numbers, like for OTP or captcha.
import time           # Helps in working with time, like OTP expiry countdown.
from datetime import datetime  # Helps in dealing with dates, like date of birth.
import sys            # Used to exit/stop the program when too many wrong attempts happen.
import string         # Contains alphabets and digits, used for captcha generation.

# ---------------------------
# Helper Validation Functions
# ---------------------------

# This function checks if the given date of birth is valid and calculates the person's age.
def validate_dob(dob_str):
    try:
        # Convert the entered date (in DD/MM/YYYY format) into a date object
        dob = datetime.strptime(dob_str, "%d/%m/%Y")
        today = datetime.today()  # Get today's date

        # Calculate the age
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age  # Return the calculated age
    except ValueError:
        # If the entered date is invalid, return None
        return None

# Check if the phone number has exactly 10 digits and starts with 6, 7, 8, or 9
def validate_phone(phone):
    return bool(re.fullmatch(r"[6-9]\d{9}", phone))

# Check if the email address is in correct format like "abc@xyz.com"
def validate_email(email):
    return bool(re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email))

# Check if the Aadhaar number has exactly 12 digits
def validate_aadhar(aadhar):
    return bool(re.fullmatch(r"\d{12}", aadhar))

# Check if the Pincode has exactly 6 digits
def validate_pincode(pincode):
    return bool(re.fullmatch(r"\d{6}", pincode))

# Check if the license number follows a specific format like MH14 20240012345
def validate_license_no(license_no):
    return bool(re.fullmatch(r"[A-Z]{2}\d{2} \d{4}\d{7}", license_no))

# ---------------------------
# OTP Simulation Functions
# ---------------------------

# Generate a random 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Simulate the process of sending and verifying an OTP
def otp_verification(purpose):
    otp = generate_otp()  # Generate a new OTP
    print(f"\n🔐 {purpose} OTP has been sent! (Simulation: OTP = {otp})")

    expiry_time = time.time() + 30  # OTP expires after 30 seconds
    attempts = 3  # User gets 3 chances to enter the OTP correctly

    while attempts > 0:
        user_otp = input("Enter the 6-digit OTP: ").strip()

        # If the OTP is expired, restart the OTP process
        if time.time() > expiry_time:
            print("⏳ OTP expired! Generating a new OTP...")
            return otp_verification(purpose)

        # If entered OTP matches the generated OTP
        if user_otp == otp:
            print("✅ OTP verified successfully!\n")
            return True
        else:
            attempts -= 1  # Reduce remaining attempts
            print(f"❌ Incorrect OTP! Attempts left: {attempts}")

    # If 3 wrong attempts are made, stop the program
    print("🚫 Too many failed attempts! Session locked for security reasons.")
    sys.exit()

# ---------------------------
# Captcha Simulation Function
# ---------------------------

# Generate a random 5-character captcha made up of letters and numbers
def generate_captcha():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# Simulate the process of showing and verifying a captcha
def captcha_verification():
    print("\n=== Final Security Check: Captcha ===")
    attempts = 3
    while attempts > 0:
        captcha = generate_captcha()
        print(f"\nCaptcha: [ {captcha} ]")
        user_input = input("Enter the captcha exactly as shown: ").strip()

        if user_input == captcha:
            print("✅ Captcha verified successfully!\n")
            return True
        else:
            attempts -= 1
            print(f"❌ Incorrect captcha! Attempts left: {attempts}")

    # Stop the program after 3 wrong attempts
    print("🚫 Too many failed attempts! Session locked for security reasons.")
    sys.exit()

# ---------------------------
# Step 1: Personal Details
# ---------------------------

def input_personal_details():
    print("\n=== Step 1: Personal Details ===")

    full_name = input("Full Name: ").strip()  # User enters full name
    father_name = input("Father's / Mother's Name: ").strip()  # Parent's name

    # Date of Birth validation
    while True:
        dob = input("Date of Birth (DD/MM/YYYY): ").strip()
        age = validate_dob(dob)
        if age is None:  # If wrong date format
            print("❌ Invalid date format. Please try again.")
            continue
        if age < 18:  # Must be at least 18 years old
            print("❌ You must be at least 18 years old to apply for a permanent driving license!")
            continue
        break

    # Gender selection
    while True:
        gender = input("Gender (M/F/O): ").strip().upper()
        if gender in ['M', 'F', 'O']:
            break
        print("❌ Invalid input. Choose M, F, or O.")

    # Blood group selection
    valid_blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    while True:
        blood_group = input("Blood Group (e.g., A+, O-): ").strip().upper()
        if blood_group in valid_blood_groups:
            break
        print("❌ Invalid blood group. Choose from:", ", ".join(valid_blood_groups))

    nationality = input("Nationality: ").strip()

    # Return all details in a dictionary format
    return {
        "Full Name": full_name,
        "Father's/Mother's Name": father_name,
        "Date of Birth": dob,
        "Age": age,
        "Gender": gender,
        "Blood Group": blood_group,
        "Nationality": nationality
    }

# ---------------------------
# Step 2: Contact Information
# ---------------------------

def input_contact_info():
    print("\n=== Step 2: Contact Information ===")

    # Mobile number validation
    while True:
        mobile = input("Mobile Number (+91): ").strip()
        if validate_phone(mobile):
            break
        print("❌ Invalid phone number. Must be 10 digits starting with 6-9.")

    # OTP verification for mobile number
    otp_verification("Mobile")

    # Email validation
    while True:
        email = input("Email Address: ").strip()
        if validate_email(email):
            break
        print("❌ Invalid email format.")

    # Address details
    street_address = input("Permanent Address - Street: ").strip()
    city = input("City: ").strip()
    state = input("State: ").strip()

    # Pincode validation
    while True:
        pincode = input("Pincode: ").strip()
        if validate_pincode(pincode):
            break
        print("❌ Invalid pincode. Must be 6 digits.")

    return {
        "Mobile Number": mobile,
        "Email": email,
        "Address": f"{street_address}, {city}, {state}, {pincode}"
    }

# ---------------------------
# Step 3: Aadhaar Verification
# ---------------------------

def input_identity_proof():
    print("\n=== Step 3: Aadhaar Verification ===")
    while True:
        aadhar = input("Aadhar Card Number (12 digits): ").strip()
        if validate_aadhar(aadhar):
            break
        print("❌ Invalid Aadhar number. Must be 12 digits.")

    # OTP verification for Aadhaar
    otp_verification("Aadhaar")

    return {"Aadhar": aadhar}

# ---------------------------
# Step 4: License Details
# ---------------------------

def input_license_details():
    print("\n=== Step 4: License Details ===")

    # Choose type of application
    while True:
        applying_for = input("Applying for (L = Learner, P = Permanent, R = Renewal): ").strip().upper()
        if applying_for in ['L', 'P', 'R']:
            break
        print("❌ Invalid option. Choose L, P, or R.")

    # Choose vehicle type
    vehicle_types = ['MCWG', 'MCWOG', 'LMV', 'HMV']
    print("Vehicle Types: ", ", ".join(vehicle_types))
    while True:
        vehicle_type = input("Enter vehicle type (e.g., LMV): ").strip().upper()
        if vehicle_type in vehicle_types:
            break
        print("❌ Invalid vehicle type. Choose from:", ", ".join(vehicle_types))

    # Previous license number (optional)
    prev_license = input("Previous License Number (if any, else leave blank): ").strip()
    if prev_license and not validate_license_no(prev_license):
        print("❌ Invalid license format! Example: MH14 20240012345")

    return {
        "Applying For": applying_for,
        "Vehicle Type": vehicle_type,
        "Previous License": prev_license if prev_license else "N/A"
    }

# ---------------------------
# Step 5: Declaration + Captcha
# ---------------------------

def input_declaration():
    print("\n=== Step 5: Declaration ===")

    # Final captcha check before confirmation
    captcha_verification()

    # User must confirm the correctness of entered data
    while True:
        declaration = input("Do you declare that all the above information is correct? (Y/N): ").strip().upper()
        if declaration == 'Y':
            break
        print("❌ You must accept the declaration to proceed.")
    return {"Declaration Accepted": "Yes"}

# ---------------------------
# Final Summary
# ---------------------------

def summary_form(data):
    print("\n=====================================")
    print("          APPLICATION SUMMARY         ")
    print("=====================================")
    for section, details in data.items():
        print(f"\n{section}:")
        for key, value in details.items():
            print(f"  {key}: {value}")
    print("\n✅ Form successfully completed! Please submit it at your nearest RTO.")

# ---------------------------
# Main Program
# ---------------------------

def main():
    print("Welcome to the Driving License Application Portal\n")

    # Call each step one by one
    personal_details = input_personal_details()
    contact_info = input_contact_info()
    identity_proof = input_identity_proof()
    license_details = input_license_details()
    declaration = input_declaration()

    # Combine all data into one summary
    all_data = {
        "Personal Details": personal_details,
        "Contact Information": contact_info,
        "Identity Proof": identity_proof,
        "License Details": license_details,
        "Declaration": declaration
    }

    # Display final summary
    summary_form(all_data)

# Start the program
if __name__ == "__main__":
    main()