# Generated by Django 2.2.7 on 2020-05-09 20:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='CustomUser',
        ),
        migrations.DeleteModel(
            name='HealthcareFacility',
        ),
    ]
