import sqlite3
import hashlib

def initialize_database():
    conn = sqlite3.connect('metro.db')
    c = conn.cursor()
    
    c.execute("DROP TABLE IF EXISTS stations")
    c.execute("DROP TABLE IF EXISTS tickets")
    c.execute("DROP TABLE IF EXISTS admins")
    
    c.execute('''CREATE TABLE stations (
                name TEXT PRIMARY KEY,
                distance INTEGER NOT NULL CHECK(distance >= 0)
              )''')
    
    c.execute('''CREATE TABLE tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK(age BETWEEN 0 AND 120),
                start_station TEXT NOT NULL,
                end_station TEXT NOT NULL,
                fare INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                qr_hash TEXT UNIQUE,
                used BOOLEAN DEFAULT 0,
                FOREIGN KEY(start_station) REFERENCES stations(name),
                FOREIGN KEY(end_station) REFERENCES stations(name)
              )''')
    
    c.execute('''CREATE TABLE admins (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
              )''')
    
    default_password = "admin123"
    hashed_password = hashlib.sha256(default_password.encode()).hexdigest()
    c.execute("INSERT INTO admins VALUES (?, ?)", ('admin', hashed_password))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_database()
    print("✅ Database initialized successfully")