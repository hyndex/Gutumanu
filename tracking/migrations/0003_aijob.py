from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('tracking', '0002_canonical_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('status', models.CharField(max_length=20, default='pending')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
