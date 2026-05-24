import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

META_API_URL = "https://graph.facebook.com/v19.0/{phone_number_id}/messages"


def _log(phone_number, message, status, notification_type='other',
         meta_message_id='', error_detail='', session=None):
    try:
        from .models import NotificationLog
        NotificationLog.objects.create(
            phone_number=phone_number,
            notification_type=notification_type,
            message=message,
            status=status,
            meta_message_id=meta_message_id,
            error_detail=error_detail,
            session=session,
        )
    except Exception as e:
        logger.error(f"Failed to write notification log: {e}")


def send_whatsapp_notification(to_number, message, notification_type='other', session=None):
    """Send a WhatsApp notification via Meta WhatsApp Cloud API."""
    access_token = settings.META_WHATSAPP_ACCESS_TOKEN
    phone_number_id = settings.META_WHATSAPP_PHONE_NUMBER_ID

    if not access_token or not phone_number_id:
        logger.warning("Meta WhatsApp credentials not configured. Message not sent.")
        logger.info(f"[DRY RUN] Would send to {to_number}: {message}")
        _log(to_number, message, 'dry_run', notification_type, session=session)
        return False

    clean_number = to_number.strip().replace('whatsapp:', '').lstrip('+')

    url = META_API_URL.format(phone_number_id=phone_number_id)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": clean_number,
        "type": "text",
        "text": {"body": message}
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        msg_id = data.get("messages", [{}])[0].get("id", "")
        logger.info(f"Message sent successfully via Meta. ID: {msg_id}")
        _log(to_number, message, 'success', notification_type,
             meta_message_id=msg_id, session=session)
        return True
    except requests.exceptions.HTTPError as e:
        error_detail = f"{e.response.status_code} — {e.response.text}"
        logger.error(f"Meta API HTTP error: {error_detail}")
        _log(to_number, message, 'failed', notification_type,
             error_detail=error_detail, session=session)
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send WhatsApp notification via Meta: {e}")
        _log(to_number, message, 'failed', notification_type,
             error_detail=str(e), session=session)
        return False


def send_reminder_notification(session):
    """Send a 5-minute reminder notification for a study session."""
    subject_name = session.get_subject_name()
    message = (
        f"Study Buddy Reminder: Your {subject_name} session starts in 5 minutes! "
        f"({session.start_time.strftime('%H:%M')} - {session.end_time.strftime('%H:%M')}). "
        f"Get ready!"
    )
    return send_whatsapp_notification(
        session.phone_number, message,
        notification_type='reminder', session=session
    )


def send_start_notification(session):
    """Send a notification when a study session starts."""
    subject_name = session.get_subject_name()
    message = (
        f"Study Buddy: Time to start your {subject_name} session! "
        f"({session.start_time.strftime('%H:%M')} - {session.end_time.strftime('%H:%M')}). "
        f"Good luck!"
    )
    return send_whatsapp_notification(
        session.phone_number, message,
        notification_type='start', session=session
    )
