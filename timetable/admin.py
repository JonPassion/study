from django.contrib import admin
from django.contrib import messages
from .models import StudySession
from .notifications import send_reminder_notification


def send_test_notification(modeladmin, request, queryset):
    """Admin action to send a test notification for selected sessions."""
    sent = 0
    for session in queryset:
        if send_reminder_notification(session):
            sent += 1
    if sent:
        messages.success(request, f"Test notifications sent for {sent} session(s).")
    else:
        messages.warning(request, "No notifications sent. Check Twilio credentials.")


send_test_notification.short_description = "Send test notification"


@admin.register(StudySession)
class StudySessionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'day_of_week', 'start_time', 'end_time', 'phone_number', 'is_active', 'reminder_sent', 'start_sent']
    list_filter = ['day_of_week', 'subject', 'is_active']
    search_fields = ['phone_number', 'custom_subject']
    actions = [send_test_notification]
    list_editable = ['is_active']
    ordering = ['day_of_week', 'start_time']

    fieldsets = (
        ('Session Info', {
            'fields': ('subject', 'custom_subject', 'day_of_week', 'start_time', 'end_time')
        }),
        ('Contact & Status', {
            'fields': ('phone_number', 'is_active')
        }),
        ('Notification Status', {
            'fields': ('reminder_sent', 'start_sent'),
            'classes': ('collapse',),
        }),
    )
