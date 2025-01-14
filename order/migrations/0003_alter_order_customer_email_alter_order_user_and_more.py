# Generated by Django 4.2 on 2025-01-13 10:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication_app', '0001_initial'),
        ('order', '0002_alter_order_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customer_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='authentication_app.customer'),
        ),
        migrations.AlterField(
            model_name='order',
            name='vendor_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]