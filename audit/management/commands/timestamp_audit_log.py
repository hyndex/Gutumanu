from django.core.management.base import BaseCommand
from audit.models import AuditLog
from rfc3161_client import TimestampRequestBuilder, decode_timestamp_response
import requests

class Command(BaseCommand):
    help = "Timestamp audit log entries using an RFC3161 Time Stamping Authority"

    def add_arguments(self, parser):
        parser.add_argument('--tsa', required=True, help='URL of the RFC3161 TSA')

    def handle(self, *args, **options):
        tsa_url = options['tsa']
        for entry in AuditLog.objects.filter(tsa_token__isnull=True).order_by('timestamp'):
            builder = TimestampRequestBuilder().data(bytes.fromhex(entry.hash))
            req = builder.build()
            resp = requests.post(
                tsa_url,
                data=req.dump(),
                headers={'Content-Type': 'application/timestamp-query'},
                timeout=10,
            )
            resp.raise_for_status()
            entry.tsa_token = resp.content
            entry.save(update_fields=['tsa_token'])
            self.stdout.write(f'Timestamped entry {entry.pk}')
