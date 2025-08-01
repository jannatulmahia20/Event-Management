# Generated by Django 5.1.2 on 2025-07-16 20:00

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_event_location_alter_event_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='participants',
            field=models.ManyToManyField(blank=True, related_name='rsvp_events', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='Participant',
        ),
    ]
