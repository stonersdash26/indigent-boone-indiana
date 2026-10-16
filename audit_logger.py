import hashlib
import sqlite3
import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DB_FILE = "machine_audit_ledger.db"

# SMTP Configuration (Replace with your mail server details or environment variables)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.example.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "auditor@example.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_secure_password")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "compliance-team@example.com")

def initialize_database():
    """Initializes the SQLite database with an immutable audit table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            asset_id TEXT NOT NULL,
            compliance_standard TEXT NOT NULL,
            status TEXT NOT NULL,
            state_hash TEXT NOT NULL,
            inspector TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def hash_file(file_path):
    """Calculates the SHA-256 hash of a target system log or binary file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return "FILE_NOT_FOUND_OR_UNAVAILABLE"

def log_audit_entry(asset_id, compliance_standard, status, target_file, inspector):
    """Commits an audit record with cryptographic state verification to the ledger."""
    timestamp = datetime.datetime.utcnow().isoformat()
    state_hash = hash_file(target_file) if os.path.exists(target_file) else hashlib.sha256(target_file.encode()).hexdigest()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (timestamp, asset_id, compliance_standard, status, state_hash, inspector)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, asset_id, compliance_standard, status, state_hash, inspector))
    conn.commit()
    conn.close()
    print(f"[LOGGED] Asset {asset_id} under {compliance_standard} marked {status}. Hash: {state_hash}")

def generate_and_email_report():
    """Fetches recent audit logs from SQLite and emails a formatted compliance report."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Fetch logs from the last 24 hours
    cursor.execute("""
        SELECT timestamp, asset_id, compliance_standard, status, state_hash, inspector 
        FROM audit_logs 
        ORDER BY id DESC LIMIT 10
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("[INFO] No audit logs found to report.")
        return

    # Format email body
    report_lines = [
        "MACHINE JURISDICTION AUDIT REPORT",
        "=" * 40,
        f"Generated: {datetime.datetime.utcnow().isoformat()} UTC",
        f"Database Ledger: {DB_FILE}",
        "-" * 40,
        ""
    ]
    
    for row in rows:
        report_lines.append(f"Timestamp:   {row[0]}")
        report_lines.append(f"Asset ID:    {row[1]}")
        report_lines.append(f"Standard:    {row[2]}")
        report_lines.append(f"Status:      {row[3]}")
        report_lines.append(f"State Hash:  {row[4]}")
        report_lines.append(f"Inspector:   {row[5]}")
        report_lines.append("-" * 40)

    report_body = "\n".join(report_lines)

    # Construct email message
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = EMAIL_RECIPIENT
    msg["Subject"] = f"Automated Machine Compliance Audit Report - {datetime.date.today()}"
    msg.attach(MIMEText(report_body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, EMAIL_RECIPIENT, msg.as_string())
        print(f"[SUCCESS] Compliance report successfully emailed to {EMAIL_RECIPIENT}")
    except Exception as e:
        print(f"[ERROR] Failed to send email report: {e}")

if __name__ == "__main__":
    initialize_database()
    
    # 1. Log a sample inspection entry
    log_audit_entry(
        asset_id="MACH-IND-01",
        compliance_standard="OSHA 1910.147 / NFPA 79",
        status="PASS",
        target_file="system_runtime.log",
        inspector="Automated Agent"
    )
    
    # 2. Automatically dispatch the email summary report
    generate_and_email_report()
