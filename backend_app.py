import random
import string
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import sqlite3

app = FastAPI()

# Database setup
conn = sqlite3.connect("complaints.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS complaints (
                    complaint_id TEXT PRIMARY KEY,
                    name TEXT,
                    phone_number TEXT,
                    email TEXT,
                    complaint_details TEXT,
                    created_at TEXT)''')
conn.commit()

class Complaint(BaseModel):
    name: str
    phone_number: str  # Changed to match frontend
    email: str
    complaint_details: str  # Changed to match frontend

def generate_complaint_id():
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=3))
    return f"{letters}{numbers}"  # Format: ABC123

@app.post("/complaints")
def create_complaint(complaint: Complaint):
    complaint_id = generate_complaint_id()
    print(complaint_id)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO complaints VALUES (?, ?, ?, ?, ?, ?)",
                  (complaint_id, complaint.name, complaint.phone_number,
                   complaint.email, complaint.complaint_details, created_at))
    conn.commit()
    
    return {"complaint_id": complaint_id}

@app.get("/complaints/{complaint_id}")
def get_complaint(complaint_id: str):
    cursor.execute("SELECT * FROM complaints WHERE complaint_id=?", (complaint_id.upper(),))
    if row := cursor.fetchone():
        return {
            "complaint_id": row[0],
            "name": row[1],
            "phone_number": row[2],
            "email": row[3],
            "complaint_details": row[4],
            "created_at": row[5]
        }
    raise HTTPException(404, "Complaint not found")

@app.get("/complaints")
def get_all_complaints():
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()
    return [
        {
            "complaint_id": row[0],
            "name": row[1],
            "phone_number": row[2],
            "email": row[3],
            "complaint_details": row[4],
            "created_at": row[5]
        }
        for row in complaints
    ]