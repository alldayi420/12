"""
test_agent.py — Test the Email Agent Without Live Dynamics 365
==============================================================
Run this to validate your email template and sending logic
using FAKE work order data. Great for demos!

Usage:
    python test_agent.py
"""

import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.dirname(__file__))

from email_composer import compose_email
from config import Config
import requests
from msal import ConfidentialClientApplication


# ── Fake Work Order Data for Demo ─────────────────────────────────────────────
FAKE_WORK_ORDERS = [
    {
        "work_order_number": "WO-2024-00142",
        "customer_name": "Riverside Medical Center",
        "customer_email": Config.SENDER_EMAIL,  # Send to yourself for testing
        "technician": "James Carter",
        "summary": "Replaced faulty power supply unit on HP LaserJet Pro MFP. "
                   "Performed full diagnostic and print calibration. System is "
                   "fully operational.",
        "completed_date": "2024-11-15T14:30:00Z"
    },
    {
        "work_order_number": "WO-2024-00143",
        "customer_name": "Greenfield Law Associates",
        "customer_email": Config.SENDER_EMAIL,
        "technician": "Maria Santos",
        "summary": "Installed firmware update on 3 HP workstations. Configured "
                   "new network printer driver. Verified connectivity across all "
                   "devices in the office.",
        "completed_date": "2024-11-15T16:00:00Z"
    }
]


def get_graph_token_for_test():
    """Authenticate for email sending."""
    app = ConfidentialClientApplication(
        client_id=Config.CLIENT_ID,
        client_credential=Config.CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{Config.TENANT_ID}"
    )
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    if "access_token" not in result:
        raise Exception(f"Auth failed: {result.get('error_description')}")
    return result["access_token"]


def send_test_email(graph_token, to_email, to_name, subject, body_html):
    """Send a test email via Microsoft Graph."""
    url = f"https://graph.microsoft.com/v1.0/users/{Config.SENDER_EMAIL}/sendMail"
    headers = {
        "Authorization": f"Bearer {graph_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": {
            "subject": f"[TEST] {subject}",
            "body": {"contentType": "HTML", "content": body_html},
            "toRecipients": [{"emailAddress": {"address": to_email, "name": to_name}}]
        },
        "saveToSentItems": True
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code == 202


def preview_email_html():
    """Save the email as HTML so you can open it in a browser."""
    wo = FAKE_WORK_ORDERS[0]
    _, body_html = compose_email(
        customer_name=wo["customer_name"],
        work_order_number=wo["work_order_number"],
        summary=wo["summary"],
        technician=wo["technician"],
        completed_date=wo["completed_date"]
    )
    preview_path = os.path.join(os.path.dirname(__file__), "email_preview.html")
    with open(preview_path, "w") as f:
        f.write(body_html)
    print(f"\n📄 Email preview saved to: {preview_path}")
    print("   Open it in your browser to see exactly how it looks!\n")


def run_full_test():
    """Send test emails for all fake work orders."""
    print("\n" + "=" * 60)
    print("  HP Field Service Agent — TEST MODE")
    print("=" * 60)

    print("\n[1/3] Generating email preview...")
    preview_email_html()

    print("[2/3] Authenticating with Microsoft...")
    try:
        token = get_graph_token_for_test()
        print("  ✅ Authentication successful!\n")
    except Exception as e:
        print(f"  ❌ Auth failed: {e}")
        print("\n  Make sure your config.py has valid credentials.")
        print("  See SETUP_GUIDE.md for instructions.\n")
        return

    print("[3/3] Sending test emails...")
    for wo in FAKE_WORK_ORDERS:
        subject, body_html = compose_email(
            customer_name=wo["customer_name"],
            work_order_number=wo["work_order_number"],
            summary=wo["summary"],
            technician=wo["technician"],
            completed_date=wo["completed_date"]
        )
        success = send_test_email(
            token,
            wo["customer_email"],
            wo["customer_name"],
            subject,
            body_html
        )
        status = "✅ Sent" if success else "❌ Failed"
        print(f"  {status} → {wo['customer_name']} ({wo['work_order_number']})")

    print("\n" + "=" * 60)
    print("  Test complete! Check your inbox for the test emails.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Just preview the email (no credentials needed)
    if "--preview-only" in sys.argv:
        preview_email_html()
    else:
        run_full_test()
