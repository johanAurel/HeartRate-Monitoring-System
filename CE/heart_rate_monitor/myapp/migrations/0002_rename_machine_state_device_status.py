# Generated by Django 5.1.2 on 2024-10-30 03:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='device',
            old_name='machine_state',
            new_name='status',
        ),
    ]