import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

DB_PATH = Path.home() / ".orbyt" / "emails.db"


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            subject TEXT,
            sender TEXT,
            date TEXT,
            category TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def insert_email(email_id: str, subject: str, sender: str, date: str, category: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO emails (id, subject, sender, date, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (email_id, subject, sender, date, category))
    
    conn.commit()
    conn.close()


def get_all_emails() -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM emails ORDER BY date DESC')
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(row) for row in rows]


def get_stats() -> Dict[str, int]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM emails
        GROUP BY category
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    stats = {
        "Application Sent": 0,
        "Interview": 0,
        "Offer": 0,
        "Rejection": 0
    }
    
    for category, count in rows:
        if category in stats:
            stats[category] = count
    
    return stats


def get_detailed_stats() -> Dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM emails
        GROUP BY category
    ''')
    
    rows = cursor.fetchall()
    
    stats = {
        "Application Sent": 0,
        "Interview": 0,
        "Offer": 0,
        "Rejection": 0
    }
    
    for category, count in rows:
        if category in stats:
            stats[category] = count
    
    total = sum(stats.values())
    applications = stats["Application Sent"]
    interviews = stats["Interview"]
    offers = stats["Offer"]
    rejections = stats["Rejection"]
    
    interview_rate = (interviews / total * 100) if total > 0 else 0
    offer_rate = (offers / total * 100) if total > 0 else 0
    rejection_rate = (rejections / total * 100) if total > 0 else 0
    interview_to_offer_rate = (offers / interviews * 100) if interviews > 0 else 0
    
    closed = interviews + offers + rejections
    pending = applications
    pending_rate = (pending / total * 100) if total > 0 else 0
    
    conn.close()
    
    return {
        "total_applications": total,
        "total_interviews": interviews,
        "total_offers": offers,
        "total_rejections": rejections,
        "interview_rate": interview_rate,
        "offer_rate": offer_rate,
        "rejection_rate": rejection_rate,
        "interview_to_offer_rate": interview_to_offer_rate,
        "pending_applications": pending,
        "closed_applications": closed,
        "pending_rate": pending_rate
    }


def get_monthly_breakdown() -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            strftime('%Y-%m', date) as month,
            category,
            COUNT(*) as count
        FROM emails
        WHERE date IS NOT NULL AND date != ''
        GROUP BY month, category
        ORDER BY month DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    monthly_data = {}
    
    for month, category, count in rows:
        if not month:
            continue
            
        if month not in monthly_data:
            monthly_data[month] = {
                "month": month,
                "applications": 0,
                "interviews": 0,
                "offers": 0,
                "rejections": 0
            }
        
        if category == "Application Sent":
            monthly_data[month]["applications"] = count
        elif category == "Interview":
            monthly_data[month]["interviews"] = count
        elif category == "Offer":
            monthly_data[month]["offers"] = count
        elif category == "Rejection":
            monthly_data[month]["rejections"] = count
    
    result = []
    for month, data in sorted(monthly_data.items(), reverse=True):
        total = data["applications"] + data["interviews"] + data["offers"] + data["rejections"]
        interview_rate = (data["interviews"] / total * 100) if total > 0 else 0
        
        result.append({
            "month": month,
            "applications": data["applications"],
            "interviews": data["interviews"],
            "offers": data["offers"],
            "rejections": data["rejections"],
            "interview_rate": interview_rate
        })
    
    return result


def email_exists(email_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT 1 FROM emails WHERE id = ?', (email_id,))
    exists = cursor.fetchone() is not None
    
    conn.close()
    return exists

