# Generated by Django 2.2.2 on 2019-07-16 11:21

import django.db.models.deletion
from django.db import migrations, models

import base.utils


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_customerprofile_washerprofile_workerprofile'),
        ('stores', '0002_store_washer_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='image',
            field=models.ImageField(default=' ', upload_to=''),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='StoreImageItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('image', models.ImageField(upload_to=base.utils.generate_file_name)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='stores.Store')),
                ('washer_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.WasherProfile')),
            ],
            options={
                'ordering': ['-created_date'],
                'abstract': False,
            },
        ),
    ]