from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import StudySession, NotificationLog
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
        messages.warning(request, "No notifications sent. Check Meta WhatsApp credentials.")


send_test_notification.short_description = "Send test notification via WhatsApp"


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


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = [
        'sent_at', 'phone_number', 'notification_type_badge',
        'status_badge', 'short_message', 'meta_message_id', 'session'
    ]
    list_filter = ['status', 'notification_type', 'sent_at']
    search_fields = ['phone_number', 'message', 'meta_message_id', 'error_detail']
    readonly_fields = [
        'phone_number', 'notification_type', 'message', 'status',
        'meta_message_id', 'error_detail', 'session', 'sent_at'
    ]
    ordering = ['-sent_at']
    date_hierarchy = 'sent_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def notification_type_badge(self, obj):
        colours = {
            'reminder': '#f39c12',
            'start': '#27ae60',
            'whatsapp_reply': '#2980b9',
            'test': '#8e44ad',
            'other': '#7f8c8d',
        }
        colour = colours.get(obj.notification_type, '#7f8c8d')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            colour, obj.get_notification_type_display()
        )
    notification_type_badge.short_description = 'Type'

    def status_badge(self, obj):
        colours = {
            'success': '#27ae60',
            'failed': '#e74c3c',
            'dry_run': '#95a5a6',
        }
        colour = colours.get(obj.status, '#7f8c8d')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            colour, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def short_message(self, obj):
        return obj.message[:80] + ('…' if len(obj.message) > 80 else '')
    short_message.short_description = 'Message'
