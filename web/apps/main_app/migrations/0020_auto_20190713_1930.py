# Generated by Django 3.0.dev20190224003410 on 2019-07-13 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0019_notifications_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifications',
            name='status',
            field=models.IntegerField(default=0),
        ),
    ]
