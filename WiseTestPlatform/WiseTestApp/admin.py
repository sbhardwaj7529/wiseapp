from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Score)
