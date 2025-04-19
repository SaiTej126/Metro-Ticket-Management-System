import sqlite3
import hashlib
import json
from datetime import datetime

def get_connection():
    conn = sqlite3.connect('metro.db')
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_stations():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT name, distance FROM stations ORDER BY distance ASC")
        return {row[0]: row[1] for row in c.fetchall()}

def verify_admin(username, password):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT password_hash FROM admins WHERE username = ?", (username,))
        result = c.fetchone()
        if result:
            input_hash = hashlib.sha256(password.encode()).hexdigest()
            return input_hash == result[0]
        return False

def insert_ticket(name, age, start, end, fare, qr_hash):
    with get_connection() as conn:
        sanitized_name = name.strip()[:50]
        conn.execute('''INSERT INTO tickets 
                      (name, age, start_station, end_station, fare, qr_hash)
                      VALUES (?, ?, ?, ?, ?, ?)''', 
                    (sanitized_name, age, start, end, fare, qr_hash))
        conn.commit()

def get_ticket_details(ticket_id):
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM tickets WHERE id = ?''', (ticket_id,))
        return c.fetchone()