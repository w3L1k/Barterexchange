
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='external_image_url',
            field=models.URLField(blank=True),
        ),
    ]
