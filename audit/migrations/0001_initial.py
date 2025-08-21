from django.db import migrations, models
import django.utils.timezone
from django.conf import settings
import audit.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(max_length=10)),
                ('path', models.TextField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('body', audit.fields.EncryptedTextField(blank=True, default='', classification='PII')),
                ('prev_hash', models.CharField(blank=True, max_length=64)),
                ('hash', models.CharField(blank=True, max_length=64)),
                ('user', models.ForeignKey(null=True, on_delete=models.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['timestamp']},
        ),
    ]
