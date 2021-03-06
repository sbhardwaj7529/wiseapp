# Generated by Django 4.0 on 2022-06-27 08:07

from datetime import datetime, tzinfo
from django.db import migrations, models
import django.db.models.deletion
from pytz import timezone
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('WiseTestApp', '0002_test_usertype_remove_question_choice_a_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='created_by',
            field=models.ForeignKey(default=999, on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='WiseTestApp.appuser'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='test',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime.now(), help_text='Time at which test was created'),
            preserve_default=False,
        ),
    ]
