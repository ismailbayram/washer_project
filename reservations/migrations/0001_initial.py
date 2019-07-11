# Generated by Django 2.2.2 on 2019-07-11 13:11

from django.db import migrations, models
import django.db.models.deletion
import enumfields.fields
import reservations.enums


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0003_customerprofile_washerprofile_workerprofile'),
        ('stores', '0002_store_washer_profile'),
        ('baskets', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('status', enumfields.fields.EnumField(enum=reservations.enums.ReservationStatus, max_length=10)),
                ('period', models.PositiveSmallIntegerField()),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('total_amount', models.DecimalField(decimal_places=2, default=None, max_digits=6, null=True)),
                ('number', models.CharField(max_length=12)),
                ('basket', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='baskets.Basket')),
                ('customer_profile', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.CustomerProfile')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stores.Store')),
            ],
            options={
                'ordering': ['-created_date'],
                'abstract': False,
            },
        ),
    ]
