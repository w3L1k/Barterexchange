
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0002_listing_external_image_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='listing',
            name='estimated_value',
        ),
    ]
