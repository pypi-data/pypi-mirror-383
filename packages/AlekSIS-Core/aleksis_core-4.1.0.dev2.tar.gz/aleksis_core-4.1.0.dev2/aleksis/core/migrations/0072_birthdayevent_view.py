import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0071_constrain_calendar_event_starting_before_ending'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(
            """
            -- Create view for BirthdayEvents
            CREATE VIEW core_birthdayevent AS
                SELECT id,
                id AS person_id,
                date_of_birth AS dt_start,
                'YEARLY' AS rrule
                FROM core_person
                WHERE date_of_birth IS NOT NULL;
            """
        ),
    ]
