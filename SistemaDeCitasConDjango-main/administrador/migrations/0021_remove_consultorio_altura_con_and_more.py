# Generated by Django 5.1.4 on 2025-01-03 01:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrador', '0020_remove_profesional_lugar_profesional_lugares'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consultorio',
            name='altura_con',
        ),
        migrations.RemoveField(
            model_name='consultorio',
            name='nota_con',
        ),
    ]