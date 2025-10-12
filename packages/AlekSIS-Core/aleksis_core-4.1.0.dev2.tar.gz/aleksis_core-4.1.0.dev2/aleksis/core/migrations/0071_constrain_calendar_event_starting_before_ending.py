from django.db import migrations, models
from django.db.models import F, Q

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0070_oauth_token_checksum'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='calendarevent',
            constraint=models.CheckConstraint(condition=Q(datetime_end__gte=F('datetime_start')),
                                              name="datetime_start_before_end"
            ),
        ),
        migrations.AddConstraint(
            model_name='calendarevent',
            constraint=models.CheckConstraint(condition=Q(date_end__gte=F('date_start')),
                                              name="date_start_before_end"
            ),
        ),
    ]
