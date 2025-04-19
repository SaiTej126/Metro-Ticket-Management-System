# ticketing.py
import qrcode
import os
import sys
from datetime import datetime
from database import get_connection, get_stations, insert_ticket

BASE_FARE_PER_KM = 3
MINIMUM_FARE = 5

def calculate_fare(start, end, age):
    stations = get_stations()
    
    if start not in stations or end not in stations:
        raise ValueError("Invalid station names")
    if start == end:
        raise ValueError("Start and end stations cannot be same")
    
    distance = abs(stations[end] - stations[start])
    base_fare = distance * BASE_FARE_PER_KM
    fare = max(base_fare, MINIMUM_FARE)
    
    if not (0 <= age <= 120):
        raise ValueError("Age must be between 0-120")
    
    if age <= 5:
        return 0
    elif age >= 60:
        return fare // 2
    return fare

def generate_qr_code(passenger, start, end):
    try:
        # Create safe directory path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        qr_dir = os.path.join(base_dir, "qrcodes")
        os.makedirs(qr_dir, exist_ok=True)
        
        # Generate clean filename
        sanitized_name = "".join([c if c.isalnum() else "_" for c in passenger['name']])
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{sanitized_name}_{start}_{end}_{timestamp}.png"
        img_path = os.path.join(qr_dir, filename)
        
        # Create perfectly formatted ticket data
        ticket_data = (
            "METRO TICKET\n"
            "----------------\n"
            f"Name: {passenger['name']}\n"
            f"Age: {passenger['age']}\n"
            f"From: {start}\n"
            f"To: {end}\n"
            f"Fare: ₹{passenger['fare']}\n"
            f"Date: {datetime.now().strftime('%d-%b-%Y %I:%M %p')}\n"
            "----------------"
        )
        
        # Generate high-quality QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(ticket_data)
        qr.make(fit=True)
        
        # Save QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(img_path)
        
        return img_path, filename
        
    except Exception as e:
        print(f"\n❌ QR Generation Error: {str(e)}")
        return None, None

def generate_ticket(passengers, start, end):
    total_fare = sum(p['fare'] for p in passengers)
    
    # Print receipt header
    print("\n" + "═" * 60)
    print("★ METRO TICKET RECEIPT ★".center(60))
    print("═" * 60)
    print(f" Date:       {datetime.now().strftime("%d-%b-%Y %I:%M %p")}")
    print(f" Boarding:   {start}")
    print(f" Destination:{end}")
    print("─" * 60)
    print(f" {'No.':<4} {'Passenger Name':<20} {'Age':<5} {'Fare':<10} {'QR File':<25}")
    print("─" * 60)
    
    qr_files = []
    with get_connection() as conn:
        for idx, p in enumerate(passengers, 1):
            try:
                qr_path, qr_filename = generate_qr_code(p, start, end)
                if qr_path and qr_filename:
                    qr_files.append(qr_path)
                    insert_ticket(p['name'], p['age'], start, end, p['fare'], qr_path)
                    print(f" {idx:<4} {p['name'][:18]:<20} {p['age']:<5} ₹{p['fare']:<9} {qr_filename[:24]}")
                else:
                    print(f" {idx:<4} [ERROR] Failed to generate ticket")
            except Exception as e:
                print(f" {idx:<4} [ERROR] Ticket processing failed: {str(e)}")

    # Auto-open QR codes
    print("\n" + "═" * 60)
    print(" QR CODE AUTOMATICALLY OPENED IN YOUR DEVICE ".center(60, "~"))
    for path in qr_files:
        try:
            if os.path.exists(path):
                if sys.platform.startswith('win'):
                    os.startfile(path)
                elif sys.platform == "darwin":
                    os.system(f"open '{path}'")
                else:
                    os.system(f"xdg-open '{path}'")
        except Exception as e:
            print(f" ❌ Failed to open QR code: {str(e)}")

    # Print footer
    print("═" * 60)
    print(f" TOTAL FARE: ₹{total_fare}".rjust(60))
    print("═" * 60)
    print(" Note: QR codes saved in 'qrcodes' folder ".center(60))
    print("═" * 60 + "\n")

