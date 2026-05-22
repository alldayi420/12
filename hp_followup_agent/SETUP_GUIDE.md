# HP Field Service Follow-Up Email Agent
## Complete Setup Guide

---

## What This Agent Does

Every 30 minutes, this script:
1. Connects to Dynamics 365 Field Service
2. Finds any work orders just marked **Completed**
3. Looks up the customer's email address
4. Sends them a professional follow-up email automatically
5. Marks the work order so it doesn't get emailed twice

---

## Step 1 — Install Python

Download Python 3.10+ from https://python.org
Make sure to check "Add Python to PATH" during install.

Then install the required libraries:
```bash
pip install -r requirements.txt
```

---

## Step 2 — Create a Microsoft Azure App Registration

This gives the script permission to read Dynamics 365 and send email.

1. Go to https://portal.azure.com
2. Search for **"App Registrations"** and click it
3. Click **"New Registration"**
   - Name: `FieldService-EmailAgent`
   - Supported account types: Single tenant
   - Click **Register**
4. Copy the **Application (client) ID** → this is your `CLIENT_ID`
5. Copy the **Directory (tenant) ID** → this is your `TENANT_ID`

### Create a Client Secret:
1. In your app registration, click **"Certificates & Secrets"**
2. Click **"New client secret"**
3. Set expiration to 24 months
4. Click **Add**
5. Copy the **Value** immediately → this is your `CLIENT_SECRET`
   ⚠️ You can only see it once!

### Add API Permissions:
1. Click **"API Permissions"** → **"Add a permission"**
2. Add these permissions:

| API | Permission | Type |
|-----|-----------|------|
| Dynamics CRM | user_impersonation | Delegated |
| Microsoft Graph | Mail.Send | Application |

3. Click **"Grant admin consent"** (requires admin rights)

---

## Step 3 — Add a Custom Field to Work Orders

The agent uses a field called `msdyn_followupemailsent` to track which
work orders have been emailed. You need to add this in Field Service:

1. Go to Field Service → Settings → Customizations
2. Click **"Customize the System"**
3. Expand Entities → **Work Order** → Fields
4. Click **"New Field"**
   - Display Name: `Follow-up Email Sent`
   - Field Name: `msdyn_followupemailsent`
   - Data Type: `Two Options` (Yes/No)
5. Save and Publish

---

## Step 4 — Configure the Agent

Open `config.py` and fill in your values:

```python
CLIENT_ID     = "paste-your-client-id-here"
CLIENT_SECRET = "paste-your-client-secret-here"
TENANT_ID     = "paste-your-tenant-id-here"
DYNAMICS_ORG  = "your-org-name"  # from your Dynamics URL
SENDER_EMAIL  = "fieldservice@yourcompany.com"
```

Or set them as environment variables (more secure):
```bash
export FS_CLIENT_ID="your-client-id"
export FS_CLIENT_SECRET="your-client-secret"
export FS_TENANT_ID="your-tenant-id"
export FS_DYNAMICS_ORG="your-org-name"
export FS_SENDER_EMAIL="fieldservice@yourcompany.com"
```

---

## Step 5 — Test It First!

### Preview the email (no credentials needed):
```bash
python test_agent.py --preview-only
```
This saves `email_preview.html` — open it in your browser.

### Send real test emails to yourself:
```bash
python test_agent.py
```
This sends emails using FAKE work order data so you can verify
everything looks right before connecting to live data.

---

## Step 6 — Run the Agent

```bash
python agent.py
```

The agent will:
- Run immediately on start
- Check every 30 minutes for newly completed work orders
- Log everything to `agent.log`

To change the check frequency, update `CHECK_INTERVAL_MINUTES` in config.py.

---

## Running Continuously (Production)

### On Windows — Run as a background service:
```bash
# Install as a Windows service using NSSM (Non-Sucking Service Manager)
# Download from nssm.cc, then:
nssm install HPFieldServiceAgent python agent.py
nssm start HPFieldServiceAgent
```

### On Mac/Linux — Run with a screen session:
```bash
screen -S hp-agent
python agent.py
# Press Ctrl+A then D to detach
```

---

## Files in This Project

```
hp_followup_agent/
├── agent.py          ← Main agent (run this)
├── config.py         ← Your credentials and settings
├── email_composer.py ← Builds the HTML email
├── test_agent.py     ← Test without live data
├── requirements.txt  ← Python dependencies
└── SETUP_GUIDE.md    ← This file
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Auth failed | Double-check CLIENT_ID, SECRET, TENANT_ID in config.py |
| No work orders found | Verify a work order is actually set to "Completed" status |
| Email not sending | Confirm Mail.Send permission is granted and SENDER_EMAIL is correct |
| Field not found | Make sure you added the custom field in Step 3 |

Check `agent.log` for detailed error messages.

---

## Questions?

This agent was built to demonstrate automated customer communication
for HP Field Services using Microsoft Dynamics 365 and Power Platform.
