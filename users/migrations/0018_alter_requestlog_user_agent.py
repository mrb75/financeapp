# Generated by Django 4.0.6 on 2022-09-20 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_user_commission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestlog',
            name='user_agent',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
