# Generated by Django 4.0.6 on 2022-09-22 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_alter_requestlog_user_agent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestlog',
            name='url',
            field=models.CharField(max_length=255, null=True),
        ),
    ]