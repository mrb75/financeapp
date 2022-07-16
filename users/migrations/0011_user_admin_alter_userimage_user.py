# Generated by Django 4.0.6 on 2022-07-16 15:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_requestlog_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='admin',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subUsers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userimage',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to=settings.AUTH_USER_MODEL),
        ),
    ]
