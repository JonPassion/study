import logging
from datetime import datetime, timedelta
from django.utils import timezone
from .notifications import send_whatsapp_notification, send_reminder_notification, send_start_notification

logger = logging.getLogger(__name__)


def check_upcoming_sessions():
    """Check for upcoming study sessions and send notifications."""
    from .models import StudySession

    now = timezone.localtime(timezone.now())
    current_day = now.strftime('%A').lower()
    current_time = now.time()

    reminder_time = (now + timedelta(minutes=5)).time()

    logger.info(f"Checking sessions at {now.strftime('%Y-%m-%d %H:%M:%S')} ({current_day})")

    active_sessions = StudySession.objects.filter(
        day_of_week=current_day,
        is_active=True
    )

    for session in active_sessions:
        if not session.reminder_sent:
            if current_time <= session.start_time <= reminder_time:
                logger.info(f"Sending 5-min reminder for: {session}")
                if send_reminder_notification(session):
                    session.reminder_sent = True
                    session.save(update_fields=['reminder_sent'])

        if not session.start_sent:
            session_start = datetime.combine(now.date(), session.start_time)
            now_dt = datetime.combine(now.date(), current_time)
            diff = abs((now_dt - session_start).total_seconds())
            if diff <= 30:
                logger.info(f"Sending start notification for: {session}")
                if send_start_notification(session):
                    session.start_sent = True
                    session.save(update_fields=['start_sent'])

    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if (now - midnight).total_seconds() < 120:
        reset_daily_flags()


def reset_daily_flags():
    """Reset daily sent flags at midnight."""
    from .models import StudySession
    count = StudySession.objects.filter(
        reminder_sent=True
    ).update(reminder_sent=False)
    count2 = StudySession.objects.filter(
        start_sent=True
    ).update(start_sent=False)
    logger.info(f"Reset {count} reminder flags and {count2} start flags for new day.")


def send_test_message(phone_number, message="Test message from Study Buddy!"):
    """Send a test WhatsApp message."""
    return send_whatsapp_notification(phone_number, message)
