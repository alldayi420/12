# 📧 HP Field Service — Automated Follow-Up Email Agent

> An intelligent Python agent that automatically sends personalized customer follow-up emails when a work order is marked **Completed** in Microsoft Dynamics 365 Field Service Mobile.

---

## 🎯 The Problem

After a field technician closes a work order in Field Service Mobile, customers receive **no automatic confirmation**. This leads to:

- Customers calling in to confirm their ticket was resolved
- Technicians spending time on manual follow-up calls
- Missed opportunities to collect customer satisfaction feedback
- A less professional post-service experience

## ✅ The Solution

This agent runs continuously in the background and handles everything automatically:

```
Work Order Marked "Completed" in Field Service Mobile
                        ↓
        Agent detects the status change
                        ↓
     Pulls customer name, email, technician info
                        ↓
    Sends personalized branded follow-up email
                        ↓
     Marks work order so no duplicate is sent
```

---

## 🚀 Features

- **Fully automated** — runs on a configurable schedule (default: every 30 minutes)
- **Personalized emails** — includes customer name, work order number, technician name, completion date, and job summary
- **Duplicate prevention** — marks each work order after emailing so customers are never contacted twice
- **Professional HTML email** — HP-branded template, mobile-responsive
- **Optional survey link** — embed a satisfaction survey URL in every email
- **Full audit trail** — every action is logged to `agent.log`
- **Test mode** — run with fake data before connecting to live systems
- **No new software needed** — built entirely on Microsoft's existing stack (Dynamics 365 + Graph API)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              HP Field Service Mobile                │
│         (Technician marks work order Done)          │
└────────────────────────┬────────────────────────────┘
                         │  Status → Completed
                         ▼
┌─────────────────────────────────────────────────────┐
│              Dynamics 365 / Dataverse               │
│         Work Orders Table + Accounts Table          │
└────────────────────────┬────────────────────────────┘
                         │  OAuth2 (MSAL)
                         ▼
┌─────────────────────────────────────────────────────┐
│            Python Agent (agent.py)                  │
│  • Authenticates via Azure App Registration         │
│  • Queries completed, un-emailed work orders        │
│  • Fetches customer + technician details            │
│  • Composes personalized HTML email                 │
│  • Sends via Microsoft Graph API                    │
│  • Marks work order as emailed                      │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Project Structure

```
hp-fieldservice-email-agent/
├── agent.py            # Main agent — run this
├── config.py           # Credentials & settings (never commit real values)
├── email_composer.py   # Builds the branded HTML email
├── test_agent.py       # Test with fake data — no live system needed
├── requirements.txt    # Python dependencies
└── SETUP_GUIDE.md      # Full step-by-step setup instructions
```

---

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure credentials
Edit `config.py` with your Azure App Registration details:
```python
CLIENT_ID     = "your-azure-client-id"
CLIENT_SECRET = "your-azure-client-secret"
TENANT_ID     = "your-azure-tenant-id"
DYNAMICS_ORG  = "your-org-name"
SENDER_EMAIL  = "fieldservice@yourcompany.com"
```

Or use environment variables (recommended for production):
```bash
export FS_CLIENT_ID="your-client-id"
export FS_CLIENT_SECRET="your-client-secret"
export FS_TENANT_ID="your-tenant-id"
export FS_DYNAMICS_ORG="your-org-name"
export FS_SENDER_EMAIL="fieldservice@yourcompany.com"
```

### 3. Preview the email (no credentials needed)
```bash
python test_agent.py --preview-only
```
Opens a browser preview of exactly what the customer will receive.

### 4. Run a full test with fake data
```bash
python test_agent.py
```

### 5. Run the live agent
```bash
python agent.py
```

---

## 📧 Email Preview

The agent sends a clean, HP-branded HTML email that includes:

| Field | Source |
|-------|--------|
| Customer Name | Dynamics 365 Account record |
| Work Order # | Work Order record |
| Technician Name | Bookable Resource Booking |
| Completion Date | Work Order `msdyn_timeclosed` field |
| Job Summary | Work Order `msdyn_workordersummary` field |
| Survey Link | Configurable in `config.py` |

---

## 🔧 Prerequisites

| Requirement | Details |
|-------------|---------|
| Python | 3.10 or higher |
| Microsoft 365 | Office 365 mailbox for sending |
| Dynamics 365 | Field Service license |
| Azure | App Registration with API permissions |

### Required Azure API Permissions

| API | Permission | Type |
|-----|-----------|------|
| Dynamics CRM | `user_impersonation` | Delegated |
| Microsoft Graph | `Mail.Send` | Application |

---

## 🛠️ Setup Guide

See **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** for complete step-by-step instructions including:
- Creating the Azure App Registration
- Adding the required custom field to Dynamics 365
- Configuring the agent
- Running in production as a background service

---

## 📋 How It Detects Completed Work Orders

Field Service uses numeric status codes internally:

| Status | Code |
|--------|------|
| Unscheduled | 690970000 |
| Scheduled | 690970001 |
| In Progress | 690970002 |
| Completed | **690970004** |
| Canceled | 690970005 |

The agent queries for work orders where `msdyn_systemstatus = 690970004` AND the custom `msdyn_followupemailsent` field is not set — ensuring each customer is emailed exactly once.

---

## 🔒 Security Notes

- **Never commit real credentials** to this repository
- Use environment variables or Azure Key Vault for production secrets
- The `config.py` file in this repo contains only placeholder values
- Consider setting the GitHub repo to **Private** until deployed

---

## 📈 Business Impact

| Metric | Impact |
|--------|--------|
| Technician time saved | ~5 min per work order (no manual follow-up) |
| Customer experience | Professional closure on every service visit |
| CSAT opportunity | Built-in survey link drives feedback collection |
| Implementation time | < 1 day on existing Microsoft infrastructure |
| New software/licenses required | None |

---

## 🧰 Built With

- [Python 3.10+](https://python.org)
- [MSAL (Microsoft Authentication Library)](https://github.com/AzureAD/microsoft-authentication-library-for-python)
- [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/overview)
- [Dynamics 365 Web API](https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/overview)
- [schedule](https://github.com/dbader/schedule)

---

## 👤 Author

Built as a field services automation initiative to improve post-service customer communication and reduce manual technician workload.

---

*Built on Microsoft's existing Field Service and Power Platform stack — no new software or licenses required.*
