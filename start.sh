#!/bin/bash
echo "Starting Study Buddy..."

python manage.py migrate --run-syncdb 2>&1

echo "Starting notification scheduler in background..."
python manage.py scheduler --interval 60 &
SCHEDULER_PID=$!

echo "Scheduler running (PID: $SCHEDULER_PID)"
echo "Starting Django server on 0.0.0.0:5000..."

python manage.py runserver 0.0.0.0:5000

kill $SCHEDULER_PID 2>/dev/null
