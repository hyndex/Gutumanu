from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tracking', '0003_aijob'),
    ]

    operations = [
        migrations.CreateModel(
            name='InferenceRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_name', models.CharField(max_length=100)),
                ('score', models.FloatField()),
                ('latency_ms', models.FloatField()),
                ('accuracy', models.FloatField(blank=True, null=True)),
                ('drift', models.FloatField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='runs', to='tracking.aijob')),
            ],
        ),
    ]
