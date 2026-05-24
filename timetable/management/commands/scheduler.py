import time
import logging
from django.core.management.base import BaseCommand
from timetable.tasks import check_upcoming_sessions

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run the study session notification scheduler'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Check interval in seconds (default: 60)'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        verbosity = options['verbosity']

        self.stdout.write(self.style.SUCCESS(
            f'Starting Study Buddy scheduler (checking every {interval} seconds)...'
        ))

        while True:
            try:
                if verbosity >= 2:
                    self.stdout.write(f'Checking for upcoming sessions...')
                check_upcoming_sessions()
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\nScheduler stopped.'))
                break
            except Exception as e:
                logger.error(f'Scheduler error: {e}')
                self.stderr.write(self.style.ERROR(f'Error: {e}'))

            time.sleep(interval)
