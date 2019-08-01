# Generated by Django 2.2.2 on 2019-08-01 13:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('stores', '0001_initial'),
        ('users', '0003_customerprofile_smsmessage_washerprofile_workerprofile'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stores.Store'),
        ),
        migrations.AddField(
            model_name='product',
            name='washer_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.WasherProfile'),
        ),
        migrations.AlterUniqueTogether(
            name='productprice',
            unique_together={('product', 'car_type')},
        ),
    ]
