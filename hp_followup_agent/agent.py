"""
HP Field Service Follow-Up Email Agent
=======================================
Automatically sends personalized follow-up emails to customers
when a work order is marked as Completed in Dynamics 365 Field Service.

Author: Built for HP Field Services Automation
"""

import os
import json
import time
import logging
import schedule
import requests
from datetime import datetime, timedelta
from msal import ConfidentialClientApplication
from config import Config
from email_composer import compose_email

# ── Logging Setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


# ── Microsoft Authentication ──────────────────────────────────────────────────
def get_access_token():
    """Authenticate with Microsoft using OAuth2 client credentials."""
    app = ConfidentialClientApplication(
        client_id=Config.CLIENT_ID,
        client_credential=Config.CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{Config.TENANT_ID}"
    )
    result = app.acquire_token_for_client(
        scopes=[f"https://{Config.DYNAMICS_ORG}.api.crm.dynamics.com/.default"]
    )
    if "access_token" not in result:
        raise Exception(f"Authentication failed: {result.get('error_description')}")
    log.info("✅ Authenticated with Microsoft successfully.")
    return result["access_token"]


def get_graph_token():
    """Get a token specifically for Microsoft Graph (sending email)."""
    app = ConfidentialClientApplication(
        client_id=Config.CLIENT_ID,
        client_credential=Config.CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{Config.TENANT_ID}"
    )
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    if "access_token" not in result:
        raise Exception(f"Graph auth failed: {result.get('error_description')}")
    return result["access_token"]


# ── Dynamics 365 Queries ──────────────────────────────────────────────────────
def get_completed_work_orders(token):
    """
    Fetch work orders that are:
    - Status = Completed (msdyn_systemstatus = 690970004)
    - Follow-up email NOT yet sent (msdyn_followupemailsent != true)
    """
    base_url = f"https://{Config.DYNAMICS_ORG}.api.crm.dynamics.com/api/data/v9.2"
    headers = {
        "Authorization": f"Bearer {token}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    # Query: completed work orders where follow-up hasn't been sent
    # msdyn_systemstatus 690970004 = Completed in Dynamics 365 Field Service
    filter_query = (
        "msdyn_systemstatus eq 690970004 "
        "and (msdyn_followupemailsent ne true or msdyn_followupemailsent eq null)"
    )

    url = (
        f"{base_url}/msdyn_workorders"
        f"?$select=msdyn_workorderid,msdyn_name,msdyn_workordersummary,"
        f"msdyn_timeclosed,_msdyn_serviceaccount_value,msdyn_workordertype"
        f"&$filter={filter_query}"
        f"&$top=50"
    )

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        log.error(f"Failed to fetch work orders: {response.status_code} - {response.text}")
        return []

    data = response.json()
    work_orders = data.get("value", [])
    log.info(f"📋 Found {len(work_orders)} completed work order(s) needing follow-up.")
    return work_orders


def get_customer_details(token, account_id):
    """Fetch customer name and email from the linked Account record."""
    base_url = f"https://{Config.DYNAMICS_ORG}.api.crm.dynamics.com/api/data/v9.2"
    headers = {
        "Authorization": f"Bearer {token}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json"
    }

    url = (
        f"{base_url}/accounts({account_id})"
        f"?$select=name,emailaddress1,telephone1,primarycontactid"
    )

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        log.warning(f"Could not fetch account {account_id}: {response.status_code}")
        return None

    return response.json()


def get_technician_name(token, work_order_id):
    """Fetch the assigned technician name from the booking record."""
    base_url = f"https://{Config.DYNAMICS_ORG}.api.crm.dynamics.com/api/data/v9.2"
    headers = {
        "Authorization": f"Bearer {token}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json"
    }

    url = (
        f"{base_url}/bookableresourcebookings"
        f"?$select=name,_resource_value"
        f"&$filter=_msdyn_workorder_value eq {work_order_id}"
        f"&$expand=Resource($select=name)"
        f"&$top=1"
    )

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        bookings = response.json().get("value", [])
        if bookings and bookings[0].get("Resource"):
            return bookings[0]["Resource"]["name"]
    return "Your HP Technician"


def mark_followup_sent(token, work_order_id):
    """
    Mark the work order so we don't send a duplicate email.
    Updates a custom field: msdyn_followupemailsent = true
    (You'll need to add this field to your Work Order table in Field Service)
    """
    base_url = f"https://{Config.DYNAMICS_ORG}.api.crm.dynamics.com/api/data/v9.2"
    headers = {
        "Authorization": f"Bearer {token}",
        "OData-MaxVersion": "4.0",
        "OData-Version": "4.0",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    url = f"{base_url}/msdyn_workorders({work_order_id})"
    payload = {"msdyn_followupemailsent": True}

    response = requests.patch(url, headers=headers, json=payload)
    if response.status_code in [200, 204]:
        log.info(f"✅ Marked work order {work_order_id} as follow-up sent.")
    else:
        log.warning(f"Could not mark follow-up sent: {response.status_code}")


# ── Email Sending via Microsoft Graph ────────────────────────────────────────
def send_email(graph_token, to_email, to_name, subject, body_html):
    """Send email using Microsoft Graph API (Office 365)."""
    url = f"https://graph.microsoft.com/v1.0/users/{Config.SENDER_EMAIL}/sendMail"
    headers = {
        "Authorization": f"Bearer {graph_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body_html
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": to_email,
                        "name": to_name
                    }
                }
            ]
        },
        "saveToSentItems": True
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 202:
        log.info(f"📧 Email sent successfully to {to_email}")
        return True
    else:
        log.error(f"Failed to send email to {to_email}: {response.status_code} - {response.text}")
        return False


# ── Main Agent Loop ───────────────────────────────────────────────────────────
def run_agent():
    """Main agent function — runs on a schedule."""
    log.info("=" * 60)
    log.info("🤖 HP Follow-Up Email Agent — Starting Run")
    log.info("=" * 60)

    try:
        # 1. Authenticate
        dynamics_token = get_access_token()
        graph_token = get_graph_token()

        # 2. Find completed work orders
        work_orders = get_completed_work_orders(dynamics_token)

        if not work_orders:
            log.info("✨ No pending follow-ups. Agent going back to sleep.")
            return

        # 3. Process each work order
        sent_count = 0
        for wo in work_orders:
            work_order_id = wo.get("msdyn_workorderid")
            work_order_num = wo.get("msdyn_name", "N/A")
            summary = wo.get("msdyn_workordersummary", "Service completed")
            account_id = wo.get("_msdyn_serviceaccount_value")
            closed_time = wo.get("msdyn_timeclosed", datetime.now().isoformat())

            log.info(f"🔧 Processing Work Order: {work_order_num}")

            if not account_id:
                log.warning(f"  ⚠️  No account linked to WO {work_order_num}. Skipping.")
                continue

            # 4. Get customer details
            customer = get_customer_details(dynamics_token, account_id)
            if not customer:
                log.warning(f"  ⚠️  Could not fetch customer for WO {work_order_num}. Skipping.")
                continue

            customer_email = customer.get("emailaddress1")
            customer_name = customer.get("name", "Valued Customer")

            if not customer_email:
                log.warning(f"  ⚠️  No email address for {customer_name}. Skipping.")
                continue

            # 5. Get technician name
            technician = get_technician_name(dynamics_token, work_order_id)

            # 6. Compose personalized email
            subject, body_html = compose_email(
                customer_name=customer_name,
                work_order_number=work_order_num,
                summary=summary,
                technician=technician,
                completed_date=closed_time
            )

            # 7. Send the email
            success = send_email(graph_token, customer_email, customer_name, subject, body_html)

            # 8. Mark as sent so we don't duplicate
            if success:
                mark_followup_sent(dynamics_token, work_order_id)
                sent_count += 1

        log.info(f"✅ Run complete. {sent_count}/{len(work_orders)} follow-up emails sent.")

    except Exception as e:
        log.error(f"❌ Agent error: {e}", exc_info=True)


# ── Scheduler ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("🚀 HP Field Service Follow-Up Email Agent Starting...")
    log.info(f"📅 Checking for completed work orders every {Config.CHECK_INTERVAL_MINUTES} minutes.")

    # Run immediately on start
    run_agent()

    # Then run on schedule
    schedule.every(Config.CHECK_INTERVAL_MINUTES).minutes.do(run_agent)

    while True:
        schedule.run_pending()
        time.sleep(30)
