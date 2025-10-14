import secrets, time, threading, smtplib, ssl
from email.message import EmailMessage
import tkinter as tk
from tkinter import simpledialog, messagebox

# ----------------------------
# Backend + default SMTP
# ----------------------------
class EmailOtpBackend:
    def __init__(self, ttl=5):
        self.ttl = ttl * 60
        self.storage = {}
        self.lock = threading.Lock()

        # Default Gmail SMTP setup (use an App Password)
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 465  # SSL port for Gmail
        self.smtp_user = "veripysender@gmail.com"
        self.smtp_pass = "ufcv dbxo hoiv cvwc"  # App password (not your login password)

    def _new_code(self):
        return f"{secrets.randbelow(10**6):06d}"

    def _generate_html(self, code):
        # Your long HTML template (kept compact here)
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Verification Code</title>
  <style>
    body {{ font-family: Inter, sans-serif; background:#f1f5f9; padding:30px; }}
    .card {{ max-width:560px; margin:auto; background:white; padding:28px; border-radius:12px; }}
    .code {{ font-family: 'Roboto Mono', monospace; font-size:44px; color:#1a73e8; letter-spacing:8px; background:#f8fafc; padding:18px; border-radius:8px; }}
  </style>
</head>
<body>
  <div class="card">
    <h2>VeriPy Verification</h2>
    <p>Your verification code:</p>
    <div class="code">{code}</div>
    <p>This code will expire in {self.ttl//60} minutes. Do not share it.</p>
  </div>
</body>
</html>
"""

    def send_email(self, to_email, code):
        msg = EmailMessage()
        msg["Subject"] = "Your VeriPy Code"
        msg["From"] = self.smtp_user
        msg["To"] = to_email
        msg.set_content(f"Your code is {code}")
        msg.add_alternative(self._generate_html(code), subtype="html")

        try:
            # Try SSL first (Gmail recommended)
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context) as server:
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            print(f"[INFO] Sent verification email to {to_email}")
        except Exception as e1:
            # fallback to STARTTLS attempt
            print(f"[WARN] SSL send failed: {e1}")
            print("[INFO] Retrying using STARTTLS...")
            try:
                with smtplib.SMTP(self.smtp_host, 587) as server:
                    server.starttls(context=ssl.create_default_context())
                    server.login(self.smtp_user, self.smtp_pass)
                    server.send_message(msg)
                print(f"[INFO] Sent verification email to {to_email} (STARTTLS)")
            except Exception as e2:
                # final fallback: debug print so dev can continue
                print(f"[ERROR] Email send failed: {e2}")
                print(f"[DEBUG] Code for {to_email}: {code}")

    def start_flow(self, email):
        flow_id = secrets.token_urlsafe(16)
        code = self._new_code()
        expires = time.time() + self.ttl
        with self.lock:
            self.storage[flow_id] = {
                "email": email,
                "code": code,
                "expires": expires,
                "attempts": 0,
            }
        self.send_email(email, code)
        return flow_id

    def verify_flow(self, flow_id, code):
        with self.lock:
            record = self.storage.get(flow_id)
            if not record:
                return False, "Flow not found"
            if time.time() > record["expires"]:
                self.storage.pop(flow_id, None)
                return False, "OTP expired"
            if record["attempts"] >= 5:
                self.storage.pop(flow_id, None)
                return False, "Too many attempts"
            record["attempts"] += 1
            if secrets.compare_digest(record["code"], str(code)):
                self.storage.pop(flow_id, None)
                return True, "Verified!"
            return False, "Incorrect code"


# ----------------------------
# Modes (GUI + CLI supported)
# ----------------------------
def cli_mode(backend, email, flow_id):
    for _ in range(5):
        code = input("Enter code: ").strip()
        ok, msg = backend.verify_flow(flow_id, code)
        if ok:
            print("✅ Verified!")
            return True
        print("❌", msg)
    print("❌ Verification failed")
    return False

def gui_mode(backend, email, flow_id):
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("VeriPy", f"A code has been sent to {email}.")
    for _ in range(5):
        code = simpledialog.askstring("VeriPy", "Enter verification code:")
        if code is None:
            root.destroy()
            return False
        ok, msg = backend.verify_flow(flow_id, code)
        if ok:
            messagebox.showinfo("VeriPy", "✅ Verified!")
            root.destroy()
            return True
        messagebox.showerror("VeriPy", msg)
    messagebox.showerror("VeriPy", "❌ Verification failed.")
    root.destroy()
    return False


# ----------------------------
# VeriMail API + default()
# ----------------------------
_backend = EmailOtpBackend()
_mode = "gui"  # default to gui (you can change with default("cli"))

class VeriMail:
    def __init__(self, email):
        self.email = email
        self.flow_id = _backend.start_flow(email)
        print(f"A verification code has been sent to {email}.")

    def verify_code(self, code_input: str = None):
        """Verify the code; if code_input is None, prompt based on _mode."""
        global _mode
        if code_input:
            ok, msg = _backend.verify_flow(self.flow_id, code_input)
            if ok:
                print("✅ Verified!")
                return True
            print("❌", msg)
            return False

        # no code given — prompt using selected mode
        if _mode == "cli":
            return cli_mode(_backend, self.email, self.flow_id)
        else:
            return gui_mode(_backend, self.email, self.flow_id)

def verimail(email):
    return VeriMail(email)

def default(mode: str):
    """Set default mode: 'cli' or 'gui' (case-insensitive)."""
    global _mode
    m = (mode or "").lower()
    if m not in ("cli", "gui"):
        raise ValueError("Mode must be 'cli' or 'gui'")
    _mode = m
