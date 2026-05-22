"""
email_composer.py — Personalized Email Generator
==================================================
Builds a professional, branded HTML follow-up email
for each completed Field Service work order.
"""

from datetime import datetime
from config import Config


def format_date(iso_string):
    """Convert ISO datetime string to a friendly format."""
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except Exception:
        return iso_string


def compose_email(customer_name, work_order_number, summary, technician, completed_date):
    """
    Compose a personalized follow-up email.

    Returns:
        tuple: (subject_line, html_body)
    """

    subject = f"Your HP Service Visit is Complete — Work Order #{work_order_number}"

    formatted_date = format_date(completed_date)
    first_name = customer_name.split()[0] if customer_name else "Valued Customer"

    survey_section = ""
    if Config.SURVEY_URL:
        survey_section = f"""
        <tr>
          <td style="padding: 0 40px 30px 40px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="background:#f0f7ff; border-left:4px solid #0096d6;
                           padding:20px 24px; border-radius:4px;">
                  <p style="margin:0 0 12px 0; font-size:15px; color:#1a1a1a; font-weight:600;">
                    How did we do?
                  </p>
                  <p style="margin:0 0 16px 0; font-size:14px; color:#555;">
                    Your feedback helps us improve our service for every customer.
                    It only takes 60 seconds.
                  </p>
                  <a href="{Config.SURVEY_URL}"
                     style="display:inline-block; background:#0096d6; color:#ffffff;
                            text-decoration:none; padding:10px 24px; border-radius:4px;
                            font-size:14px; font-weight:600;">
                    Share Your Feedback →
                  </a>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        """

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Service Complete — HP Field Services</title>
</head>
<body style="margin:0; padding:0; background:#f5f5f5; font-family:'Segoe UI',Arial,sans-serif;">

  <!-- Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5; padding:30px 0;">
    <tr>
      <td align="center">

        <!-- Email Card -->
        <table width="600" cellpadding="0" cellspacing="0"
               style="background:#ffffff; border-radius:8px;
                      box-shadow:0 2px 8px rgba(0,0,0,0.08); overflow:hidden;">

          <!-- HP Header -->
          <tr>
            <td style="background:#0096d6; padding:28px 40px;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td>
                    <span style="font-size:28px; font-weight:700; color:#ffffff;
                                 letter-spacing:-0.5px;">hp</span>
                    <span style="font-size:13px; color:rgba(255,255,255,0.8);
                                 margin-left:12px; text-transform:uppercase;
                                 letter-spacing:1px;">Field Services</span>
                  </td>
                  <td align="right">
                    <span style="background:rgba(255,255,255,0.2); color:#fff;
                                 font-size:12px; padding:4px 10px; border-radius:20px;">
                      ✓ Service Complete
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Greeting -->
          <tr>
            <td style="padding:36px 40px 24px 40px;">
              <p style="margin:0 0 8px 0; font-size:22px; font-weight:600; color:#1a1a1a;">
                Hi {first_name},
              </p>
              <p style="margin:0; font-size:15px; color:#555; line-height:1.6;">
                Great news — your recent HP service visit has been successfully completed.
                Here's a summary of what was done.
              </p>
            </td>
          </tr>

          <!-- Work Order Summary Box -->
          <tr>
            <td style="padding:0 40px 30px 40px;">
              <table width="100%" cellpadding="0" cellspacing="0"
                     style="border:1px solid #e5e5e5; border-radius:6px; overflow:hidden;">

                <!-- Box Header -->
                <tr>
                  <td colspan="2"
                      style="background:#f8f8f8; padding:14px 20px;
                             border-bottom:1px solid #e5e5e5;">
                    <span style="font-size:12px; text-transform:uppercase;
                                 letter-spacing:1px; color:#888; font-weight:600;">
                      Work Order Details
                    </span>
                  </td>
                </tr>

                <!-- Work Order Number -->
                <tr>
                  <td style="padding:14px 20px; border-bottom:1px solid #f0f0f0;
                             font-size:13px; color:#888; width:40%;">
                    Work Order #
                  </td>
                  <td style="padding:14px 20px; border-bottom:1px solid #f0f0f0;
                             font-size:14px; color:#1a1a1a; font-weight:600;">
                    {work_order_number}
                  </td>
                </tr>

                <!-- Technician -->
                <tr>
                  <td style="padding:14px 20px; border-bottom:1px solid #f0f0f0;
                             font-size:13px; color:#888;">
                    Technician
                  </td>
                  <td style="padding:14px 20px; border-bottom:1px solid #f0f0f0;
                             font-size:14px; color:#1a1a1a;">
                    {technician}
                  </td>
                </tr>

                <!-- Completed Date -->
                <tr>
                  <td style="padding:14px 20px; border-bottom:1px solid #f0f0f0;
                             font-size:13px; color:#888;">
                    Completed On
                  </td>
                  <td style="padding:14px 20px; border-bottom:1px solid #f0f0f0;
                             font-size:14px; color:#1a1a1a;">
                    {formatted_date}
                  </td>
                </tr>

                <!-- Summary -->
                <tr>
                  <td style="padding:14px 20px; font-size:13px; color:#888;
                             vertical-align:top;">
                    Summary
                  </td>
                  <td style="padding:14px 20px; font-size:14px; color:#1a1a1a;
                             line-height:1.6;">
                    {summary or "Service completed successfully."}
                  </td>
                </tr>

              </table>
            </td>
          </tr>

          <!-- Survey Section (optional) -->
          {survey_section}

          <!-- Support Section -->
          <tr>
            <td style="padding:0 40px 30px 40px;">
              <p style="margin:0 0 8px 0; font-size:14px; color:#555; line-height:1.6;">
                If you have any questions about the work performed or need additional
                assistance, our support team is ready to help.
              </p>
              <p style="margin:0; font-size:14px; color:#555;">
                📞 <a href="tel:{Config.SUPPORT_PHONE}"
                      style="color:#0096d6; text-decoration:none;">
                  {Config.SUPPORT_PHONE}
                </a>
                &nbsp;&nbsp;|&nbsp;&nbsp;
                ✉️ <a href="mailto:{Config.SUPPORT_EMAIL}"
                       style="color:#0096d6; text-decoration:none;">
                  {Config.SUPPORT_EMAIL}
                </a>
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f8f8f8; padding:20px 40px;
                       border-top:1px solid #e5e5e5;">
              <p style="margin:0; font-size:12px; color:#aaa; line-height:1.6;">
                This is an automated notification from HP Field Services.
                Please do not reply directly to this email.
                <br>
                © {datetime.now().year} HP Inc. All rights reserved.
              </p>
            </td>
          </tr>

        </table>
        <!-- End Email Card -->

      </td>
    </tr>
  </table>

</body>
</html>
"""

    return subject, html_body
