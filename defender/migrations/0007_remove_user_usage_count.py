# Generated by Django 5.1.6 on 2025-03-05 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('defender', '0006_user_valid_until'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='usage_count',
        ),
    ]
