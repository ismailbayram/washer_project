# Generated by Django 2.2.2 on 2019-07-08 18:23

import baskets.enums
from django.db import migrations, models
import django.db.models.deletion
import enumfields.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0003_customerprofile_washerprofile_workerprofile'),
        ('products', '0002_product_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('status', enumfields.fields.EnumField(enum=baskets.enums.BasketStatus, max_length=10)),
                ('customer_profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='users.CustomerProfile')),
            ],
            options={
                'ordering': ['-created_date'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BasketItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('basket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='baskets.Basket')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='products.Product')),
            ],
            options={
                'ordering': ['-created_date'],
                'abstract': False,
            },
        ),
    ]
