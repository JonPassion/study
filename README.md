# Study Buddy - Django Application

A lightweight Django application that helps you stay on track with your study schedule by sending automated WhatsApp notifications.

## Features

- **Study Session Management**: Create and manage study sessions with subjects, times, and days
- **Automated Notifications**: Get WhatsApp reminders 5 minutes before your study sessions
- **Admin Interface**: Easy-to-use Django admin for managing your schedule
- **Twilio Integration**: Reliable WhatsApp messaging via Twilio API
- **Background Scheduler**: Automated checking for upcoming sessions

## Quick Start

### 1. Setup Virtual Environment

```bash
python3 -m venv study_buddy_env
source study_buddy_env/bin/activate  # On Windows: study_buddy_env\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### 4. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run the Application

**Start Django Development Server:**
```bash
python manage.py runserver
```

**Start the Scheduler (in a separate terminal):**
```bash
python manage.py scheduler
```

## Usage

### 1. Access Admin Interface

Navigate to `http://localhost:8000/admin/` and login with your superuser credentials.

### 2. Add Study Sessions

1. Click on "Study sessions" in the admin
2. Click "Add study session"
3. Fill in the details:
   - **Subject**: Choose from predefined subjects or select "Other" for custom subjects
   - **Day of Week**: Select the day for your study session
   - **Start Time** and **End Time**: Set your study session duration
   - **Phone Number**: Include country code (e.g., +1234567890)
   - **Is Active**: Enable/disable notifications for this session

### 3. Test Notifications

You can test notifications by:
- Selecting sessions in the admin and choosing "Send test notification" from the action dropdown
- Or using the management command:
  ```bash
  python manage.py shell
  >>> from timetable.tasks import send_test_message
  >>> send_test_message("+1234567890", "Test message from Study Buddy!")
  ```

## Twilio Setup

### 1. Create Twilio Account

1. Sign up at [Twilio](https://www.twilio.com/)
2. Get your Account SID and Auth Token from the dashboard
3. Set up the WhatsApp Sandbox

### 2. WhatsApp Sandbox Setup

1. Go to Twilio Console → Messaging → Try it out → Send a WhatsApp message
2. Follow the instructions to join the sandbox
3. Your phone number will be whitelisted for testing

### 3. Update Settings

Add your Twilio credentials to your `.env` file or update `settings.py`:

```python
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'
```

## Scheduler Options

The scheduler command accepts several options:

```bash
# Run with custom check interval (default: 60 seconds)
python manage.py scheduler --interval 30

# Run in verbose mode
python manage.py scheduler --verbosity 2
```

## Project Structure

```
study_buddy/
├── manage.py
├── requirements.txt
├── README.md
├── study_buddy/          # Django project settings
├── timetable/            # Main app
│   ├── models.py        # StudySession model
│   ├── admin.py         # Django admin configuration
│   ├── notifications.py # Twilio integration
│   ├── tasks.py         # Background task logic
│   └── management/commands/
│       └── scheduler.py # Management command for scheduler
└── study_buddy_env/     # Virtual environment
```

## How It Works

1. **Study Sessions**: You create study sessions in the Django admin
2. **Scheduler**: The management command runs continuously, checking every minute
3. **Notifications**: When a session is about to start (5 minutes before), it sends a WhatsApp reminder
4. **Start Notification**: When the session begins, it sends a "time to start" message

## Development

### Running Tests

```bash
python manage.py test
```

### Adding New Features

1. Add new models in `timetable/models.py`
2. Update admin in `timetable/admin.py`
3. Add new notification types in `timetable/notifications.py`
4. Extend scheduler logic in `timetable/management/commands/scheduler.py`

## Troubleshooting

### Common Issues

1. **Twilio Credentials Not Working**
   - Verify your Account SID and Auth Token
   - Check that your phone number is whitelisted in the WhatsApp Sandbox
   - Ensure phone numbers include country codes

2. **Scheduler Not Running**
   - Make sure you're running the scheduler command in a separate terminal
   - Check that the Django settings are properly configured

3. **No Notifications Being Sent**
   - Verify that study sessions are marked as "Is Active"
   - Check the scheduler output for any error messages
   - Ensure the current day and time match your session schedule

### Logs

The scheduler provides detailed logs about:
- When it checks for sessions
- Which notifications are being sent
- Any errors that occur

## Production Deployment

For production use:

1. Use a proper task queue like Celery with Redis/RabbitMQ instead of the simple scheduler
2. Set up proper environment variables for Twilio credentials
3. Configure Django settings for production
4. Use a process manager like supervisor or systemd to keep the scheduler running
5. Set up proper logging and monitoring

## License

This project is open source and available under the MIT License.
# study
