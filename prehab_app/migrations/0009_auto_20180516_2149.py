# Generated by Django 2.0.2 on 2018-05-16 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prehab_app', '0008_auto_20180501_2012'),
    ]

    operations = [
        migrations.AddField(
            model_name='patienttaskschedule',
            name='date',
            field=models.DateTimeField(db_column='date', default=None, null=True),
        ),
        migrations.AlterField(
            model_name='patienttaskschedule',
            name='status',
            field=models.IntegerField(choices=[(1, 'Pending'), (2, 'Completed'), (3, 'Not Completed')], default=1),
        ),
    ]
