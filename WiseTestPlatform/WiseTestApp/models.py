from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User



class Student(User):
    roll_no = models.IntegerField(null=True, help_text="Roll number of student")
    class_name = models.CharField(null=True, max_length=200)
    section = models.CharField(null=True, max_length=200)


class Teacher(User):
    department = models.CharField(null=True, max_length=200)
    joining_year = models.DateTimeField(null=True, help_text="Time at which teacher joined")


class Test(models.Model):
    name = models.CharField(null=True, max_length=200)
    start_time = models.DateTimeField(null=False, help_text="Time at which test will start")
    duration = models.IntegerField(null=False, help_text="Duration in Minutes")
    marks_awarded_per_correct_ans = models.IntegerField(null=False, help_text="Marks awarded per correct answer")
    marks_deducted_per_incorrect_ans = models.IntegerField(null=False, help_text="Marks deducted per incorrect answer")
    created_by = models.ForeignKey("Teacher", related_name="tests", on_delete=models.CASCADE)
    created_on = models.DateTimeField(null=False, help_text="Time at which test was created")
    assigned_to = models.ManyToManyField("Student", blank=True, related_name="assigned_tests")

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    test = models.ForeignKey("Test", related_name="questions", on_delete=models.CASCADE)
    pub_date = models.DateTimeField(null=False, help_text='date published')

class Choice(models.Model):
    question = models.ForeignKey("Question", related_name="choices", on_delete=models.CASCADE)
    choice = models.CharField("Choice", max_length=200)
    position = models.IntegerField("position")
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = [
            # no duplicated choice per question
            ("question", "choice"), 
            # no duplicated position per question 
            ("question", "position") 
        ]
        ordering = ("position",)

class Score(models.Model):
    user = models.ForeignKey("Student", related_name="scores", on_delete=models.CASCADE)
    test = models.ForeignKey("Test", related_name="scores", on_delete=models.CASCADE)
    marks = models.IntegerField(null=False, help_text="Marks in interger type")
    class Meta:
        unique_together = [
            # no duplicated test per user
            ("user", "test"), 
        ]



