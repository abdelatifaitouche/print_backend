# Generated by Django 4.2.20 on 2025-03-28 00:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_orderitem_file_path'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='file_path',
            new_name='file',
        ),
    ]
