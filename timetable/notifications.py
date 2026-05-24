import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_whatsapp_notification(to_number, message):
    """Send a WhatsApp notification via Twilio."""
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    from_number = settings.TWILIO_WHATSAPP_NUMBER

    if not account_sid or not auth_token:
        logger.warning("Twilio credentials not configured. Message not sent.")
        logger.info(f"[DRY RUN] Would send to {to_number}: {message}")
        return False

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)

        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'

        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        logger.info(f"Message sent successfully. SID: {msg.sid}")
        return True
    except ImportError:
        logger.error("Twilio package not installed. Run: pip install twilio")
        return False
    except Exception as e:
        logger.error(f"Failed to send WhatsApp notification: {e}")
        return False


def send_reminder_notification(session):
    """Send a 5-minute reminder notification for a study session."""
    subject_name = session.get_subject_name()
    message = (
        f"Study Buddy Reminder: Your {subject_name} session starts in 5 minutes! "
        f"({session.start_time.strftime('%H:%M')} - {session.end_time.strftime('%H:%M')}). "
        f"Get ready!"
    )
    return send_whatsapp_notification(session.phone_number, message)


def send_start_notification(session):
    """Send a notification when a study session starts."""
    subject_name = session.get_subject_name()
    message = (
        f"Study Buddy: Time to start your {subject_name} session! "
        f"({session.start_time.strftime('%H:%M')} - {session.end_time.strftime('%H:%M')}). "
        f"Good luck!"
    )
    return send_whatsapp_notification(session.phone_number, message)
