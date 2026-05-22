"""
config.py — HP Field Service Agent Configuration
=================================================
Fill in your credentials here before running the agent.
Keep this file PRIVATE — never share or commit to Git.
"""

import os


class Config:
    # ── Microsoft Azure App Registration ──────────────────────────────────────
    # You'll get these from Azure Portal > App Registrations
    # See SETUP_GUIDE.md for step-by-step instructions

    CLIENT_ID = os.getenv("FS_CLIENT_ID", "YOUR_AZURE_APP_CLIENT_ID")
    CLIENT_SECRET = os.getenv("FS_CLIENT_SECRET", "YOUR_AZURE_APP_CLIENT_SECRET")
    TENANT_ID = os.getenv("FS_TENANT_ID", "YOUR_AZURE_TENANT_ID")

    # ── Dynamics 365 Environment ───────────────────────────────────────────────
    # Found in: Field Service > Settings > About (or your Dynamics URL)
    # Example: if your URL is https://contoso.crm.dynamics.com
    # then DYNAMICS_ORG = "contoso"

    DYNAMICS_ORG = os.getenv("FS_DYNAMICS_ORG", "YOUR_ORG_NAME")

    # ── Email Sender ───────────────────────────────────────────────────────────
    # The Office 365 email address that sends the follow-up emails
    # The Azure app needs Mail.Send permission for this mailbox

    SENDER_EMAIL = os.getenv("FS_SENDER_EMAIL", "fieldservice@yourcompany.com")

    # ── Agent Behavior ─────────────────────────────────────────────────────────
    # How often to check for newly completed work orders (in minutes)
    CHECK_INTERVAL_MINUTES = int(os.getenv("FS_CHECK_INTERVAL", "30"))

    # Optional: Survey link to include in follow-up emails
    SURVEY_URL = os.getenv("FS_SURVEY_URL", "")

    # Optional: Support phone number shown in emails
    SUPPORT_PHONE = os.getenv("FS_SUPPORT_PHONE", "1-800-HP-SUPPORT")

    # Optional: Support email shown in emails
    SUPPORT_EMAIL = os.getenv("FS_SUPPORT_EMAIL", "support@hp.com")
