# Generated by Django 2.2.2 on 2019-07-12 13:24

from django.db import migrations, models
import django.db.models.deletion
import enumfields.fields
import reservations.enums


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('baskets', '0001_initial'),
        ('stores', '0002_store_washer_profile'),
        ('users', '0003_customerprofile_washerprofile_workerprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('status', enumfields.fields.EnumField(db_index=True, default='100', enum=reservations.enums.ReservationStatus, max_length=10)),
                ('period', models.PositiveSmallIntegerField()),
                ('start_datetime', models.DateTimeField(db_index=True)),
                ('end_datetime', models.DateTimeField(db_index=True)),
                ('total_amount', models.DecimalField(decimal_places=2, default=None, max_digits=6, null=True)),
                ('number', models.CharField(max_length=10, unique=True)),
                ('basket', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='baskets.Basket')),
                ('customer_profile', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.CustomerProfile')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='stores.Store')),
            ],
            options={
                'unique_together': {('start_datetime', 'store')},
            },
        ),
    ]
