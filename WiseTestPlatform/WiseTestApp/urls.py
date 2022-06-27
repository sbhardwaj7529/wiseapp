from django.urls import path


from .api import Teachers, Students, AllTestsPerTeacher, CreateTest, AssignTest, AssignedTestsPerStudent, OpenTest, SubmitAnswers, ScorePerStudent, AllScores

urlpatterns = [
    path('teachers/', Teachers.as_view()),
    path('students/', Students.as_view()),
    path('tests_per_teacher/', AllTestsPerTeacher.as_view()),
    path('tests/', CreateTest.as_view()),
    path('assign_tests/', AssignTest.as_view()),
    path('assigned_tests/', AssignedTestsPerStudent.as_view()),
    path('assigned_tests/<int:pk>/', OpenTest.as_view()),
    path('submission/', SubmitAnswers.as_view()),
    path('scores/', AllScores.as_view()),
    path('scores/<int:pk>/', ScorePerStudent.as_view()),    
]