# Generated by Django 4.0 on 2022-06-27 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WiseTestApp', '0005_student_teacher_remove_appuser_user_ptr_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='roll_no',
            field=models.IntegerField(help_text='Roll number of student', null=True),
        ),
    ]
