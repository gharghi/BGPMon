# Generated by Django 3.0.dev20190224003410 on 2019-05-11 06:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main_app', '0007_auto_20190508_0031'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(default=0)),
                ('path', models.TextField()),
                ('wrong_prefix', models.CharField(max_length=60, null=True)),
                ('time', models.BigIntegerField()),
                ('asn', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.Asn')),
                ('prefix', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main_app.Prefix')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
