from django.db import models


class StudySession(models.Model):
    SUBJECT_CHOICES = [
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

    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    custom_subject = models.CharField(max_length=100, blank=True, help_text='Fill this if subject is "Other"')
    day_of_week = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    phone_number = models.CharField(max_length=20, help_text='Include country code e.g. +1234567890')
    is_active = models.BooleanField(default=True, help_text='Enable/disable notifications for this session')
    reminder_sent = models.BooleanField(default=False)
    start_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Study Session'
        verbose_name_plural = 'Study Sessions'

    def __str__(self):
        subject_display = self.custom_subject if self.subject == 'other' and self.custom_subject else self.get_subject_display()
        return f"{subject_display} - {self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}"

    def get_subject_name(self):
        if self.subject == 'other' and self.custom_subject:
            return self.custom_subject
        return self.get_subject_display()


class ConversationState(models.Model):
    phone_number = models.CharField(max_length=30, unique=True)
    state = models.CharField(max_length=50, default='main_menu')
    context = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number} → {self.state}"
