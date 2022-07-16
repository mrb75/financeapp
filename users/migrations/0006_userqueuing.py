# Generated by Django 4.0.6 on 2022-07-16 11:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bills', '0004_rename_user_billproduct_customer_product_products'),
        ('users', '0005_notification_notificationtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserQueuing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_visit', models.DateTimeField()),
                ('description', models.TextField(blank=True, max_length=2000, null=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('coworker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userQueues', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userQueues', to='bills.product')),
            ],
            options={
                'ordering': ['date_created'],
            },
        ),
    ]