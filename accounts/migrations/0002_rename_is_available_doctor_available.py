# Generated by Django 5.0.4 on 2024-05-04 07:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='doctor',
            old_name='is_available',
            new_name='available',
        ),
    ]