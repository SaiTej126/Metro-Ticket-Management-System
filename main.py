import re
from admin import admin_panel, view_stations
from ticketing import calculate_fare, generate_ticket

def display_header():
    print("\n" + "=" * 40)
    print(" METRO TICKETING SYSTEM ".center(40, "★"))
    print("=" * 40)

def validate_name(name):
    name = name.strip()
    if not name:
        return False, "❌ Name cannot be empty"
    if len(name) > 50:
        return False, "❌ Name too long (max 50 chars)"
    if not re.match(r"^[A-Za-z\s\-'.]+$", name):
        return False, "❌ Invalid characters"
    return True, ""

def buy_tickets():
    from database import get_stations
    stations = get_stations()
    
    if len(stations) < 2:
        print("❌ Not enough stations. Contact admin.")
        return
    
    # Get ticket count
    while True:
        try:
            num_tickets = int(input("\nNumber of tickets (1-4): "))
            if 1 <= num_tickets <= 4:
                break
            print("❌ Please enter 1-4 tickets")
        except ValueError:
            print("❌ Invalid number")
    
    # Show stations
    view_stations()
    
    # Select stations
    while True:
        start = input("\nBoarding station: ").strip()
        end = input("Destination station: ").strip()
        
        if start not in stations or end not in stations:
            print("❌ Invalid stations")
        elif start == end:
            print("❌ Same stations")
        else:
            break
    
    passengers = []
    for i in range(num_tickets):
        print(f"\nPassenger {i+1}:")
        
        # Name validation
        while True:
            name = input("Name: ").strip()
            valid, msg = validate_name(name)
            if valid: break
            print(msg)
        
        # Age validation
        while True:
            try:
                age = int(input("Age: "))
                if 0 <= age <= 120: break
                print("❌ Age 0-120")
            except ValueError:
                print("❌ Invalid age")
        
        # Calculate fare
        try:
            fare = calculate_fare(start, end, age)
            passengers.append({'name': name, 'age': age, 'fare': fare})
        except ValueError as e:
            print(f"❌ Error: {e}")
            return
    
    # Confirm purchase
    if input("\nConfirm purchase? (y/n): ").lower() == 'y':
        generate_ticket(passengers, start, end)
        print("✅ Tickets issued")
    else:
        print("❌ Transaction cancelled")
    input("\nPress Enter to continue...")

def main():
    while True:
        display_header()
        print("1. View Stations")
        print("2. Buy Tickets")
        print("3. Admin Login")
        print("4. Exit System")
        
        choice = input("\nYour choice: ")
        
        if choice == '1':
            view_stations()
        elif choice == '2':
            buy_tickets()
        elif choice == '3':
            admin_panel()
        elif choice == '4':
            print("\nThank you for using Metro Services!")
            break
        else:
            print("❌ Invalid choice")
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()