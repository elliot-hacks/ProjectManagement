# Generated by Django 5.0.6 on 2024-06-16 08:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_comment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='comments',
        ),
    ]