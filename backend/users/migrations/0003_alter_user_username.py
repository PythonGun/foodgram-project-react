# Generated by Django 3.2.15 on 2022-08-18 15:45

from django.db import migrations, models

import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20220818_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[users.validators.validate_username]),
        ),
    ]
