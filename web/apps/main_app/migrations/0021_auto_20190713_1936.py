# Generated by Django 3.0.dev20190224003410 on 2019-07-13 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0020_auto_20190713_1930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notifications',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]