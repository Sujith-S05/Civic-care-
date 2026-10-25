"""
SMS notifications sent to the citizen who filed a complaint.

Runs in one of two modes:
- DEMO MODE (default): no Twilio credentials configured, so the message is
  just printed to the server console/log. This lets the whole app run and
  be demoed end-to-end without needing a paid SMS account.
- LIVE MODE: TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN / TWILIO_FROM_NUMBER are
  set in .env, so real SMS are sent via Twilio's API.

To go live: `pip install twilio`, create a Twilio trial account, and set the
three TWILIO_* variables in backend/.env.
"""
from config import settings


def send_sms(to_phone: str, message: str) -> bool:
    if not to_phone:
        print(f"[SMS SKIPPED] No phone number on file for this citizen. Message was: {message}")
        return False

    if not (settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_FROM_NUMBER):
        print(f"[SMS DEMO MODE] To: {to_phone} | Message: {message}")
        return True

    try:
        from twilio.rest import Client  # imported lazily so the package is only needed in live mode
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=settings.TWILIO_FROM_NUMBER, to=to_phone)
        print(f"[SMS SENT] To: {to_phone}")
        return True
    except Exception as exc:
        print(f"[SMS FAILED] To: {to_phone} | Error: {exc}")
        return False


def notify_status_change(citizen_phone: str, citizen_name: str, complaint_title: str, status: str) -> None:
    message = (
        f"CivicCare: Hi {citizen_name}, your complaint '{complaint_title}' "
        f"status is now: {status}."
    )
    send_sms(citizen_phone, message)


def notify_resolved(citizen_phone: str, citizen_name: str, complaint_title: str) -> None:
    message = (
        f"CivicCare: Hi {citizen_name}, your complaint '{complaint_title}' "
        f"has been RESOLVED. Thank you for reporting this civic issue."
    )
    send_sms(citizen_phone, message)
