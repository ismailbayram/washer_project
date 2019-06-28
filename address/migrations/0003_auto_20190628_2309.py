# Generated by Django 2.2.2 on 2019-06-28 20:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0002_country_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='address.City'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='address',
            name='country',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.PROTECT, to='address.Country'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='address',
            name='township',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='address.Township'),
            preserve_default=False,
        ),
    ]
