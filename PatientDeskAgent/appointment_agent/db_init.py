import sqlite3
import datetime
import pandas as pd
import os

# Define the path for the SQLite database
db_path = "db/appointment_schedule_constant.db"

def initialize_database():
    """Initializes the SQLite database with some dummy appointment data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Drop table if it exists to start fresh
    cursor.execute("DROP TABLE IF EXISTS appointment_schedule")

    # Create table
    cursor.execute("""
        CREATE TABLE appointment_schedule (
            "index" INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT,
            appointment_type TEXT,
            patient TEXT
        )
    """)

    # Generate dummy data
    appointments_data = []
    today = datetime.date.today()
    
    appointment_types = [
        "Adult physicals", "Pediatric physicals", "Follow-up appointments",
        "Sick visits", "Flu shots", "Other vaccinations", "Allergy shots",
        "B12 injections", "Diabetes management", "Hypertension management",
        "Asthma management", "Chronic pain management", "Initial mental health consultations",
        "Follow-up mental health appointments", "Therapy sessions", "Blood draws",
        "Urine tests", "EKGs", "Biopsies", "Medication management",
        "Wart removals", "Skin tag removals", "Ear wax removals"
    ]

    for i in range(1, 10): # Next 9 days
        for appt_type in appointment_types:
            for hour in [9, 10, 11, 13, 14, 15]: # Some morning and afternoon slots
                dt = datetime.datetime(today.year, today.month, today.day, hour, 0, 0) + datetime.timedelta(days=i)
                appointments_data.append({'datetime': dt.isoformat(), 'appointment_type': appt_type, 'patient': None})
                
    # Add some specific flu shot appointments for December 2025 as per user's tool example
    for day in range(7, 14): # December 7-13, 2025
        for hour in [8, 9, 10, 11, 12, 13, 14, 15]:
            dt = datetime.datetime(2025, 12, day, hour, 0, 0)
            appointments_data.append({'datetime': dt.isoformat(), 'appointment_type': 'Flu shots', 'patient': None})


    df = pd.DataFrame(appointments_data)
    df.to_sql('appointment_schedule', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path} with {len(df)} appointments.")

if __name__ == "__main__":
    # Ensure the 'db' directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    initialize_database()