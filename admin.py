# admin.py
import sqlite3
from getpass import getpass
from datetime import datetime
from database import get_connection, get_stations, verify_admin

def admin_login():
    print("\n🔐 ADMIN LOGIN")
    username = input("Username: ").strip()
    password = getpass("Password: ").strip()
    
    if not username or not password:
        print("❌ Both fields required")
        return False
    
    if verify_admin(username, password):
        print("✅ Login successful!")
        return True
    print("❌ Authentication failed")
    return False

def view_stations():
    stations = get_stations()
    if not stations:
        print("\n🚫 No stations found")
        return
    print("\n📍 Station List:")
    for name, distance in sorted(stations.items(), key=lambda x: x[1]):
        print(f"- {name}: {distance} km")

def add_station():
    name = input("\nEnter station name: ").strip()
    if not name:
        print("❌ Station name cannot be empty")
        return
    
    try:
        distance = int(input("Enter distance from origin (km): "))
        if distance < 0:
            raise ValueError
    except ValueError:
        print("❌ Invalid distance (must be ≥0)")
        return

    try:
        with get_connection() as conn:
            conn.execute("INSERT INTO stations VALUES (?, ?)", (name, distance))
            conn.commit()
            print(f"✅ Station '{name}' added successfully")
    except sqlite3.IntegrityError:
        print("❌ Station already exists")

def remove_station():
    name = input("\nEnter station name to remove: ").strip()
    with get_connection() as conn:
        c = conn.cursor()
        try:
            c.execute("DELETE FROM stations WHERE name = ?", (name,))
            if c.rowcount > 0:
                conn.commit()
                print(f"✅ Station '{name}' removed")
            else:
                print("❌ Station not found")
        except sqlite3.IntegrityError:
            print("❌ Cannot delete: Station has existing tickets")

def list_all_tickets():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT t.id, t.name, t.start_station, t.end_station, 
                    t.fare, t.timestamp, t.used, s1.distance, s2.distance
                    FROM tickets t
                    JOIN stations s1 ON t.start_station = s1.name
                    JOIN stations s2 ON t.end_station = s2.name
                    ORDER BY t.timestamp DESC''')
        
        tickets = c.fetchall()
        
        if not tickets:
            print("\n🚫 No tickets found")
            return
        
        print("\n📄 All Tickets:")
        print("-" * 85)
        print(f"{'ID':<5} {'Passenger':<20} {'Route':<25} {'Fare':<8} {'Date':<12} {'Status':<10}")
        print("-" * 85)
        
        for ticket in tickets:
            route = f"{ticket[2]} → {ticket[3]}"
            date = datetime.strptime(ticket[5], "%Y-%m-%d %H:%M:%S").strftime("%d-%b-%Y")
            status = "USED" if ticket[6] else "VALID"
            print(f"{ticket[0]:<5} {ticket[1][:18]:<20} {route[:23]:<25} ₹{ticket[4]:<7} {date:<12} {status:<10}")
        
        print("-" * 85)
        print(f"Total Tickets: {len(tickets)}")

def view_ticket_by_id():
    ticket_id = input("\nEnter Ticket ID: ").strip()
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT t.*, s1.distance, s2.distance 
                   FROM tickets t
                   JOIN stations s1 ON t.start_station = s1.name
                   JOIN stations s2 ON t.end_station = s2.name
                   WHERE t.id = ?''', (ticket_id,))
        
        ticket = c.fetchone()
        
        if ticket:
            print("\n🎫 Full Ticket Details:")
            print("-" * 40)
            print(f"ID: {ticket[0]}")
            print(f"Passenger: {ticket[1]}")
            print(f"Age: {ticket[2]}")
            print(f"Route: {ticket[3]} → {ticket[4]}")
            print(f"Distance: {abs(ticket[10] - ticket[9])} km")
            print(f"Fare: ₹{ticket[5]}")
            print(f"Purchase Time: {ticket[6]}")
            print(f"Status: {'Used' if ticket[8] else 'Valid'}")
            print(f"QR Hash: {ticket[7]}")
            print("-" * 40)
        else:
            print("\n❌ Ticket not found")

def ticket_management():
    while True:
        print("\n📑 TICKET MANAGEMENT")
        print("1. List All Tickets")
        print("2. Search by Ticket ID")
        print("3. Return to Admin Menu")
        
        choice = input("Enter choice: ")
        
        if choice == '1':
            list_all_tickets()
        elif choice == '2':
            view_ticket_by_id()
        elif choice == '3':
            break
        else:
            print("❌ Invalid choice")
        input("\nPress Enter to continue...")

def admin_panel():
    if not admin_login():
        return
    
    while True:
        print("\n🔐 ADMIN PANEL")
        print("1. Station Management")
        print("2. Ticket Management")
        print("3. Exit Admin Panel")
        
        choice = input("Enter choice: ")
        
        if choice == '1':
            while True:
                print("\n🚉 STATION MANAGEMENT")
                print("1. Add Station")
                print("2. Remove Station")
                print("3. View Stations")
                print("4. Return to Admin Menu")
                
                sub_choice = input("Enter choice: ")
                
                if sub_choice == '1':
                    add_station()
                elif sub_choice == '2':
                    remove_station()
                elif sub_choice == '3':
                    view_stations()
                elif sub_choice == '4':
                    break
                else:
                    print("❌ Invalid choice")
                input("\nPress Enter to continue...")
                
        elif choice == '2':
            ticket_management()
        elif choice == '3':
            break
        else:
            print("❌ Invalid choice")
        input("\nPress Enter to continue...")