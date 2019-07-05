# Generated by Django 2.2.2 on 2019-07-05 20:07

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('name', models.CharField(max_length=128)),
                ('phone_number', models.CharField(max_length=32)),
                ('tax_office', models.CharField(max_length=128)),
                ('tax_number', models.CharField(max_length=128)),
                ('is_approved', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('config', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('latitude', models.FloatField(default=None, null=True)),
                ('longitude', models.FloatField(default=None, null=True)),
                ('rating', models.FloatField(default=None, null=True)),
                ('address', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='address.Address')),
            ],
            options={
                'ordering': ['-created_date'],
                'abstract': False,
            },
        ),
    ]
