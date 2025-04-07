# Generated by Django 5.1.6 on 2025-03-19 10:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defender', '0007_remove_user_usage_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='announcement',
            name='name',
        ),
        migrations.RemoveField(
            model_name='announcement',
            name='phonenumber',
        ),
        migrations.AddField(
            model_name='announcement',
            name='userId',
            field=models.CharField(default='unknown', max_length=100, verbose_name='아이디'),
        ),
    ]
