from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('audit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditlog',
            name='tsa_token',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
