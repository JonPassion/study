"""
WhatsApp conversational interface for Study Buddy timetable management.
Full state machine with numbered options at every level.
"""
import logging
from datetime import datetime
from .models import StudySession, ConversationState
from .notifications import send_whatsapp_notification

logger = logging.getLogger(__name__)

SUBJECTS = [
    ('mathematics', 'Mathematics'),
    ('physics', 'Physics'),
    ('chemistry', 'Chemistry'),
    ('biology', 'Biology'),
    ('english', 'English'),
    ('history', 'History'),
    ('geography', 'Geography'),
    ('computer_science', 'Computer Science'),
    ('economics', 'Economics'),
    ('psychology', 'Psychology'),
    ('other', 'Other'),
]

DAYS = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
]

DAY_ORDER = {d[0]: i for i, d in enumerate(DAYS)}


def send_reply(to_number, message):
    send_whatsapp_notification(to_number, message)


def get_or_create_state(phone_number):
    state, _ = ConversationState.objects.get_or_create(
        phone_number=phone_number,
        defaults={'state': 'main_menu', 'context': {}}
    )
    return state


def set_state(conv, state, context=None):
    conv.state = state
    if context is not None:
        conv.context = context
    conv.save()


def main_menu_text():
    return (
        "📚 *Study Buddy — Main Menu*\n\n"
        "What would you like to do?\n\n"
        "1️⃣  View Timetable\n"
        "2️⃣  Add Session\n"
        "3️⃣  Edit Session\n"
        "4️⃣  Delete Session\n"
        "5️⃣  Enable / Disable Session\n"
        "0️⃣  Exit\n\n"
        "_Reply with a number._"
    )


def subjects_menu_text():
    lines = ["📖 *Choose a Subject:*\n"]
    for i, (_, label) in enumerate(SUBJECTS, 1):
        lines.append(f"{i}. {label}")
    lines.append("\n0. ↩️ Back to Main Menu")
    return "\n".join(lines)


def days_menu_text():
    lines = ["📅 *Choose a Day:*\n"]
    for i, (_, label) in enumerate(DAYS, 1):
        lines.append(f"{i}. {label}")
    lines.append("\n0. ↩️ Back to Main Menu")
    return "\n".join(lines)


def sessions_list_text(sessions, title="Your Sessions:"):
    if not sessions:
        return f"📭 No sessions found.\n\nReply *0* to go back to the Main Menu."
    lines = [f"📋 *{title}*\n"]
    for i, s in enumerate(sessions, 1):
        status = "✅" if s.is_active else "⛔"
        lines.append(
            f"{i}. {status} *{s.get_subject_name()}*\n"
            f"   {s.get_day_of_week_display()} · {s.start_time.strftime('%H:%M')} – {s.end_time.strftime('%H:%M')}"
        )
    lines.append("\n0. ↩️ Back to Main Menu")
    return "\n".join(lines)


def format_session(s):
    status = "✅ Active" if s.is_active else "⛔ Disabled"
    return (
        f"📖 Subject: *{s.get_subject_name()}*\n"
        f"📅 Day: *{s.get_day_of_week_display()}*\n"
        f"⏰ Time: *{s.start_time.strftime('%H:%M')} – {s.end_time.strftime('%H:%M')}*\n"
        f"🔔 Status: {status}"
    )


def parse_time(text):
    for fmt in ('%H:%M', '%H%M', '%I:%M %p', '%I%p'):
        try:
            return datetime.strptime(text.strip(), fmt).time()
        except ValueError:
            continue
    return None


def handle_message(phone_number, message_text):
    """Main entry point — routes the message through the state machine."""
    text = message_text.strip()
    conv = get_or_create_state(phone_number)
    state = conv.state

    # Global trigger: "menu", "hi", "hello", "start" always resets to main menu
    if text.lower() in ('menu', 'hi', 'hello', 'start', 'help'):
        set_state(conv, 'main_menu', {})
        send_reply(phone_number, main_menu_text())
        return

    if state == 'main_menu':
        _handle_main_menu(conv, phone_number, text)

    elif state == 'add_subject':
        _handle_add_subject(conv, phone_number, text)

    elif state == 'add_custom_subject':
        _handle_add_custom_subject(conv, phone_number, text)

    elif state == 'add_day':
        _handle_add_day(conv, phone_number, text)

    elif state == 'add_start_time':
        _handle_add_start_time(conv, phone_number, text)

    elif state == 'add_end_time':
        _handle_add_end_time(conv, phone_number, text)

    elif state == 'add_confirm':
        _handle_add_confirm(conv, phone_number, text)

    elif state == 'edit_list':
        _handle_edit_list(conv, phone_number, text)

    elif state == 'edit_field':
        _handle_edit_field(conv, phone_number, text)

    elif state == 'edit_subject':
        _handle_edit_subject(conv, phone_number, text)

    elif state == 'edit_custom_subject':
        _handle_edit_custom_subject(conv, phone_number, text)

    elif state == 'edit_day':
        _handle_edit_day(conv, phone_number, text)

    elif state == 'edit_start_time':
        _handle_edit_start_time(conv, phone_number, text)

    elif state == 'edit_end_time':
        _handle_edit_end_time(conv, phone_number, text)

    elif state == 'edit_confirm':
        _handle_edit_confirm(conv, phone_number, text)

    elif state == 'delete_list':
        _handle_delete_list(conv, phone_number, text)

    elif state == 'delete_confirm':
        _handle_delete_confirm(conv, phone_number, text)

    elif state == 'toggle_list':
        _handle_toggle_list(conv, phone_number, text)

    else:
        set_state(conv, 'main_menu', {})
        send_reply(phone_number, main_menu_text())


# ──────────────────────────────────────────
# MAIN MENU
# ──────────────────────────────────────────

def _handle_main_menu(conv, phone, text):
    if text == '1':
        _do_view_timetable(conv, phone)
    elif text == '2':
        set_state(conv, 'add_subject', {})
        send_reply(phone, subjects_menu_text())
    elif text == '3':
        sessions = list(StudySession.objects.filter(phone_number__contains=phone[-9:]))
        if not sessions:
            sessions = list(StudySession.objects.all())
        set_state(conv, 'edit_list', {'session_ids': [s.id for s in sessions]})
        send_reply(phone, sessions_list_text(sessions, "Select a session to edit:"))
    elif text == '4':
        sessions = list(StudySession.objects.all())
        set_state(conv, 'delete_list', {'session_ids': [s.id for s in sessions]})
        send_reply(phone, sessions_list_text(sessions, "Select a session to delete:"))
    elif text == '5':
        sessions = list(StudySession.objects.all())
        set_state(conv, 'toggle_list', {'session_ids': [s.id for s in sessions]})
        send_reply(phone, sessions_list_text(sessions, "Select a session to enable/disable:"))
    elif text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, "👋 Goodbye! Reply *menu* anytime to return.")
    else:
        send_reply(phone, f"❓ Please reply with a number from the menu.\n\n{main_menu_text()}")


# ──────────────────────────────────────────
# VIEW TIMETABLE
# ──────────────────────────────────────────

def _do_view_timetable(conv, phone):
    sessions = list(StudySession.objects.all())
    if not sessions:
        send_reply(phone, "📭 No study sessions found.\n\nReply *menu* to return.")
        set_state(conv, 'main_menu', {})
        return

    grouped = {}
    for s in sessions:
        grouped.setdefault(s.day_of_week, []).append(s)

    lines = ["📅 *Your Full Timetable*\n"]
    for day_key, day_label in DAYS:
        day_sessions = grouped.get(day_key, [])
        if day_sessions:
            lines.append(f"━━ *{day_label}* ━━")
            for s in day_sessions:
                status = "✅" if s.is_active else "⛔"
                lines.append(
                    f"  {status} {s.get_subject_name()}\n"
                    f"      {s.start_time.strftime('%H:%M')} – {s.end_time.strftime('%H:%M')}"
                )

    lines.append("\nReply *menu* to return to the main menu.")
    set_state(conv, 'main_menu', {})
    send_reply(phone, "\n".join(lines))


# ──────────────────────────────────────────
# ADD SESSION FLOW
# ──────────────────────────────────────────

def _handle_add_subject(conv, phone, text):
    if text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, main_menu_text())
        return
    try:
        idx = int(text) - 1
        if 0 <= idx < len(SUBJECTS):
            subj_key, subj_label = SUBJECTS[idx]
            ctx = {'subject': subj_key, 'subject_label': subj_label}
            if subj_key == 'other':
                set_state(conv, 'add_custom_subject', ctx)
                send_reply(phone, "✏️ Enter the name of your custom subject:")
            else:
                set_state(conv, 'add_day', ctx)
                send_reply(phone, days_menu_text())
        else:
            raise ValueError
    except (ValueError, TypeError):
        send_reply(phone, f"❓ Please reply with a number between 1 and {len(SUBJECTS)}.\n\n{subjects_menu_text()}")


def _handle_add_custom_subject(conv, phone, text):
    if not text:
        send_reply(phone, "✏️ Please enter the name of your subject:")
        return
    ctx = dict(conv.context)
    ctx['custom_subject'] = text
    set_state(conv, 'add_day', ctx)
    send_reply(phone, days_menu_text())


def _handle_add_day(conv, phone, text):
    if text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, main_menu_text())
        return
    try:
        idx = int(text) - 1
        if 0 <= idx < len(DAYS):
            day_key, day_label = DAYS[idx]
            ctx = dict(conv.context)
            ctx['day'] = day_key
            ctx['day_label'] = day_label
            set_state(conv, 'add_start_time', ctx)
            send_reply(phone, "⏰ Enter the *start time* (e.g. *09:00* or *14:30*):")
        else:
            raise ValueError
    except (ValueError, TypeError):
        send_reply(phone, f"❓ Please reply with a number between 1 and {len(DAYS)}.\n\n{days_menu_text()}")


def _handle_add_start_time(conv, phone, text):
    if text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, main_menu_text())
        return
    t = parse_time(text)
    if t is None:
        send_reply(phone, "❓ Invalid time format. Please use HH:MM (e.g. *09:00* or *14:30*):")
        return
    ctx = dict(conv.context)
    ctx['start_time'] = t.strftime('%H:%M')
    set_state(conv, 'add_end_time', ctx)
    send_reply(phone, "⏰ Enter the *end time* (e.g. *10:00* or *16:00*):")


def _handle_add_end_time(conv, phone, text):
    if text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, main_menu_text())
        return
    t = parse_time(text)
    if t is None:
        send_reply(phone, "❓ Invalid time format. Please use HH:MM (e.g. *10:00*):")
        return
    ctx = dict(conv.context)
    ctx['end_time'] = t.strftime('%H:%M')

    subject_label = ctx.get('custom_subject') or ctx.get('subject_label', '')
    summary = (
        f"📋 *Please confirm your new session:*\n\n"
        f"📖 Subject: *{subject_label}*\n"
        f"📅 Day: *{ctx['day_label']}*\n"
        f"⏰ Time: *{ctx['start_time']} – {ctx['end_time']}*\n\n"
        f"1. ✅ Confirm & Save\n"
        f"2. ❌ Cancel\n"
        f"0. ↩️ Main Menu"
    )
    set_state(conv, 'add_confirm', ctx)
    send_reply(phone, summary)


def _handle_add_confirm(conv, phone, text):
    if text == '1':
        ctx = conv.context
        subject = ctx.get('subject', 'other')
        custom_subject = ctx.get('custom_subject', '')
        day = ctx.get('day')
        start_time = datetime.strptime(ctx['start_time'], '%H:%M').time()
        end_time = datetime.strptime(ctx['end_time'], '%H:%M').time()

        session = StudySession.objects.create(
            subject=subject,
            custom_subject=custom_subject,
            day_of_week=day,
            start_time=start_time,
            end_time=end_time,
            phone_number=phone,
            is_active=True,
        )
        set_state(conv, 'main_menu', {})
        send_reply(phone,
            f"✅ *Session saved!*\n\n{format_session(session)}\n\n"
            f"Reply *menu* or type a number to continue.\n\n{main_menu_text()}"
        )
    elif text in ('2', '0'):
        set_state(conv, 'main_menu', {})
        send_reply(phone, f"❌ Cancelled.\n\n{main_menu_text()}")
    else:
        send_reply(phone, "Please reply *1* to confirm or *2* to cancel.")


# ──────────────────────────────────────────
# EDIT SESSION FLOW
# ──────────────────────────────────────────

def _handle_edit_list(conv, phone, text):
    if text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, main_menu_text())
        return
    session_ids = conv.context.get('session_ids', [])
    try:
        idx = int(text) - 1
        if 0 <= idx < len(session_ids):
            session_id = session_ids[idx]
            session = StudySession.objects.get(id=session_id)
            ctx = {'session_id': session_id}
            menu = (
                f"✏️ *Editing:* {session.get_subject_name()}\n"
                f"{format_session(session)}\n\n"
                f"*What would you like to change?*\n\n"
                f"1. Subject\n"
                f"2. Day\n"
                f"3. Start Time\n"
                f"4. End Time\n"
                f"0. ↩️ Back to Main Menu"
            )
            set_state(conv, 'edit_field', ctx)
            send_reply(phone, menu)
        else:
            raise ValueError
    except (ValueError, TypeError, StudySession.DoesNotExist):
        sessions = StudySession.objects.all()
        send_reply(phone, f"❓ Invalid choice.\n\n{sessions_list_text(list(sessions), 'Select a session to edit:')}")


def _handle_edit_field(conv, phone, text):
    if text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, main_menu_text())
        return
    ctx = dict(conv.context)
    if text == '1':
        set_state(conv, 'edit_subject', ctx)
        send_reply(phone, subjects_menu_text())
    elif text == '2':
        set_state(conv, 'edit_day', ctx)
        send_reply(phone, days_menu_text())
    elif text == '3':
        set_state(conv, 'edit_start_time', ctx)
        send_reply(phone, "⏰ Enter the new *start time* (e.g. *09:00*):")
    elif text == '4':
        set_state(conv, 'edit_end_time', ctx)
        send_reply(phone, "⏰ Enter the new *end time* (e.g. *10:30*):")
    else:
        send_reply(phone, "❓ Please reply with *1*, *2*, *3*, *4*, or *0* to go back.")


def _handle_edit_subject(conv, phone, text):
    if text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, main_menu_text())
        return
    try:
        idx = int(text) - 1
        if 0 <= idx < len(SUBJECTS):
            subj_key, subj_label = SUBJECTS[idx]
            ctx = dict(conv.context)
            ctx['new_subject'] = subj_key
            ctx['new_subject_label'] = subj_label
            if subj_key == 'other':
                set_state(conv, 'edit_custom_subject', ctx)
                send_reply(phone, "✏️ Enter the name of your custom subject:")
            else:
                ctx['new_custom_subject'] = ''
                _send_edit_confirm(conv, phone, ctx)
        else:
            raise ValueError
    except (ValueError, TypeError):
        send_reply(phone, f"❓ Invalid choice.\n\n{subjects_menu_text()}")


def _handle_edit_custom_subject(conv, phone, text):
    ctx = dict(conv.context)
    ctx['new_custom_subject'] = text
    ctx['new_subject_label'] = text
    _send_edit_confirm(conv, phone, ctx)


def _handle_edit_day(conv, phone, text):
    if text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, main_menu_text())
        return
    try:
        idx = int(text) - 1
        if 0 <= idx < len(DAYS):
            day_key, day_label = DAYS[idx]
            ctx = dict(conv.context)
            ctx['new_day'] = day_key
            ctx['new_day_label'] = day_label
            _send_edit_confirm(conv, phone, ctx)
        else:
            raise ValueError
    except (ValueError, TypeError):
        send_reply(phone, f"❓ Invalid choice.\n\n{days_menu_text()}")


def _handle_edit_start_time(conv, phone, text):
    if text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, main_menu_text())
        return
    t = parse_time(text)
    if t is None:
        send_reply(phone, "❓ Invalid time. Use HH:MM (e.g. *09:00*):")
        return
    ctx = dict(conv.context)
    ctx['new_start_time'] = t.strftime('%H:%M')
    _send_edit_confirm(conv, phone, ctx)


def _handle_edit_end_time(conv, phone, text):
    if text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, main_menu_text())
        return
    t = parse_time(text)
    if t is None:
        send_reply(phone, "❓ Invalid time. Use HH:MM (e.g. *10:30*):")
        return
    ctx = dict(conv.context)
    ctx['new_end_time'] = t.strftime('%H:%M')
    _send_edit_confirm(conv, phone, ctx)


def _send_edit_confirm(conv, phone, ctx):
    try:
        session = StudySession.objects.get(id=ctx['session_id'])
    except StudySession.DoesNotExist:
        set_state(conv, 'main_menu', {})
        send_reply(phone, f"⚠️ Session not found.\n\n{main_menu_text()}")
        return

    subject_label = ctx.get('new_subject_label') or session.get_subject_name()
    day_label = ctx.get('new_day_label') or session.get_day_of_week_display()
    start_time = ctx.get('new_start_time') or session.start_time.strftime('%H:%M')
    end_time = ctx.get('new_end_time') or session.end_time.strftime('%H:%M')

    summary = (
        f"📋 *Confirm your changes:*\n\n"
        f"📖 Subject: *{subject_label}*\n"
        f"📅 Day: *{day_label}*\n"
        f"⏰ Time: *{start_time} – {end_time}*\n\n"
        f"1. ✅ Save Changes\n"
        f"2. ❌ Cancel\n"
        f"0. ↩️ Main Menu"
    )
    set_state(conv, 'edit_confirm', ctx)
    send_reply(phone, summary)


def _handle_edit_confirm(conv, phone, text):
    if text == '1':
        ctx = conv.context
        try:
            session = StudySession.objects.get(id=ctx['session_id'])
        except StudySession.DoesNotExist:
            set_state(conv, 'main_menu', {})
            send_reply(phone, f"⚠️ Session not found.\n\n{main_menu_text()}")
            return

        if 'new_subject' in ctx:
            session.subject = ctx['new_subject']
            session.custom_subject = ctx.get('new_custom_subject', '')
        if 'new_day' in ctx:
            session.day_of_week = ctx['new_day']
        if 'new_start_time' in ctx:
            session.start_time = datetime.strptime(ctx['new_start_time'], '%H:%M').time()
        if 'new_end_time' in ctx:
            session.end_time = datetime.strptime(ctx['new_end_time'], '%H:%M').time()
        session.save()

        set_state(conv, 'main_menu', {})
        send_reply(phone,
            f"✅ *Session updated!*\n\n{format_session(session)}\n\n{main_menu_text()}"
        )
    elif text in ('2', '0'):
        set_state(conv, 'main_menu', {})
        send_reply(phone, f"❌ Changes cancelled.\n\n{main_menu_text()}")
    else:
        send_reply(phone, "Please reply *1* to save or *2* to cancel.")


# ──────────────────────────────────────────
# DELETE SESSION FLOW
# ──────────────────────────────────────────

def _handle_delete_list(conv, phone, text):
    if text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, main_menu_text())
        return
    session_ids = conv.context.get('session_ids', [])
    try:
        idx = int(text) - 1
        if 0 <= idx < len(session_ids):
            session_id = session_ids[idx]
            session = StudySession.objects.get(id=session_id)
            ctx = {'session_id': session_id}
            confirm_msg = (
                f"🗑️ *Delete this session?*\n\n"
                f"{format_session(session)}\n\n"
                f"1. ✅ Yes, Delete\n"
                f"2. ❌ No, Cancel\n"
                f"0. ↩️ Main Menu"
            )
            set_state(conv, 'delete_confirm', ctx)
            send_reply(phone, confirm_msg)
        else:
            raise ValueError
    except (ValueError, TypeError, StudySession.DoesNotExist):
        sessions = list(StudySession.objects.all())
        send_reply(phone, f"❓ Invalid choice.\n\n{sessions_list_text(sessions, 'Select a session to delete:')}")


def _handle_delete_confirm(conv, phone, text):
    if text == '1':
        ctx = conv.context
        try:
            session = StudySession.objects.get(id=ctx['session_id'])
            name = session.get_subject_name()
            session.delete()
            set_state(conv, 'main_menu', {})
            send_reply(phone, f"🗑️ *{name}* session deleted.\n\n{main_menu_text()}")
        except StudySession.DoesNotExist:
            set_state(conv, 'main_menu', {})
            send_reply(phone, f"⚠️ Session not found.\n\n{main_menu_text()}")
    elif text in ('2', '0'):
        set_state(conv, 'main_menu', {})
        send_reply(phone, f"❌ Deletion cancelled.\n\n{main_menu_text()}")
    else:
        send_reply(phone, "Please reply *1* to delete or *2* to cancel.")


# ──────────────────────────────────────────
# TOGGLE SESSION FLOW
# ──────────────────────────────────────────

def _handle_toggle_list(conv, phone, text):
    if text == '0':
        set_state(conv, 'main_menu', {})
        send_reply(phone, main_menu_text())
        return
    session_ids = conv.context.get('session_ids', [])
    try:
        idx = int(text) - 1
        if 0 <= idx < len(session_ids):
            session_id = session_ids[idx]
            session = StudySession.objects.get(id=session_id)
            session.is_active = not session.is_active
            session.save(update_fields=['is_active'])
            new_status = "✅ Enabled" if session.is_active else "⛔ Disabled"
            set_state(conv, 'main_menu', {})
            send_reply(phone,
                f"🔔 *{session.get_subject_name()}* is now *{new_status}*.\n\n{main_menu_text()}"
            )
        else:
            raise ValueError
    except (ValueError, TypeError, StudySession.DoesNotExist):
        sessions = list(StudySession.objects.all())
        send_reply(phone, f"❓ Invalid choice.\n\n{sessions_list_text(sessions, 'Select a session to enable/disable:')}")
