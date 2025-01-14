<<<<<<< HEAD
# Generated by Django 4.2 on 2025-01-13 08:24
=======
# Generated by Django 4.2 on 2025-01-13 06:58
>>>>>>> 088fd83c1a22ee0c7329756b6547b95e63685e74

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vendor_name', models.CharField(max_length=100)),
                ('vendor_phone', models.CharField(max_length=15)),
                ('vendor_email', models.EmailField(max_length=254, unique=True)),
                ('vendor_address', models.TextField()),
                ('store_name', models.CharField(max_length=100)),
                ('store_address', models.TextField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='vendor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=100)),
                ('customer_phone', models.CharField(max_length=15)),
                ('customer_email', models.EmailField(max_length=254, unique=True)),
                ('customer_address', models.TextField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='customer_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
