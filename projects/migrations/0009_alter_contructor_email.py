# Generated by Django 5.0.6 on 2024-06-17 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_contructor_contructor_attachments_contructor_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contructor',
            name='email',
            field=models.EmailField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]