import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('gigs', '0003_gigticketlink'),
    ]

    operations = [
        migrations.AddField(
            model_name='gigs',
            name='referral_code',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Kode Referral / Promo'),
        ),
    ]
