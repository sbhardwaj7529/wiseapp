import json
import logging
from datetime import timedelta, datetime
from operator import rshift
from unittest import result
from django.utils import timezone
from os import path, environ
from turtle import position

from django.http import HttpResponse, StreamingHttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseServerError
from rest_framework.views import APIView
from django.http import JsonResponse
from django.db import IntegrityError
from rest_framework import serializers
from .custom_exceptions import *

from django.views.decorators.csrf import csrf_exempt
import time
import traceback
import pytz
import requests

from .models import Student, Teacher, Test, Question, Choice, Score


class Teachers(APIView):

    def get(self, request, *args, **kwargs):
        """
        Returns the list of teachers in the system
        rtype: json cotaining list of teachers with their id, username, first_name, last_name, department
        """

        try:
            teachers = list(Teacher.objects.all().values('id', 'username', 'first_name', 'last_name', 'department'))

            json_response = {
                "teachers": teachers
            }

            return JsonResponse(json_response, status=200)

        except Exception as e:
            print(e)
            raise InternalServerError()


class Students(APIView):

    def get(self, request, *args, **kwargs):
        """
        Returns the list of students in the system
        output: json cotaining list of teachers with their id, username, first_name, last_name, roll_no, class_name, section
        """

        try:
            students = list(Student.objects.all().values('id', 'username','first_name', 'last_name', 'roll_no', 'class_name', 'section'))

            json_response = {
                "students": students
            }

            return JsonResponse(json_response, status=200)

        except Exception as e:
            print(e)
            raise InternalServerError()

class AllTestsPerTeacher(APIView):

    def get(self, request, *args, **kwargs):
        """
        API overview:--
        Returns the list of tests created by a particular teacher
        inputs: user_id of teacher
        output: json containing the list of tests with their id, name, created_on, start_time, duration, marks_awarded_per_correct_ans, marks_deducted_per_incorrect_ans
        """

        try:
            user_id = request.query_params.get('user_id', None)
            if user_id is None or len(Teacher.objects.filter(id=int(user_id))) == 0:
                return HttpResponseBadRequest("Error: please supply correct user_id")
            tests = list(Test.objects.filter(created_by__id=int(user_id)).values('id', 'name','created_on', 'start_time', 'duration', 'marks_awarded_per_correct_ans', 'marks_deducted_per_incorrect_ans'))

            json_response = {
                "tests": tests
            }

            return JsonResponse(json_response, status=200)

        except Exception as e:
            print(e)
            raise InternalServerError()


class CreateTest(APIView):
    def post(self, request, *args, **kwargs):
        """
        API Overview:--
        Creates the test using the supplied input parameters.
        Inputs:
            1. user_id of the teacher
            2. test_name for the test
            3. start_time of the test
            4. duration of the test in minutes
            5. marks_awarded_per_correct_ans in interger type
            6. marks_deducted_per_incorrect_ans in interger type 

        Output:
            id of the newly created test
        
        """

        try:
            data = request.data
            user_id = data.get('user_id', None)
            if user_id is None or len(Teacher.objects.filter(id=int(user_id))) == 0:
                return HttpResponseBadRequest("Error: please supply correct user_id")
            test_name = data.get('test_name',None)
            if test_name is None:
                return HttpResponseBadRequest("Error: please supply test_name")
            if len(Test.objects.filter(name=test_name)) > 0:
                return HttpResponseBadRequest("Error: Test with this test_name already exists")
            start_time = data.get('start_time', None)
            if start_time is None:
                return HttpResponseBadRequest("Error: please supply start_time") 
            try:           
                start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
            except:
                return HttpResponseBadRequest("Error: please provide start_time in format %Y-%m-%dT%H:%M:%S") 
            duration = data.get('duration', None)
            if duration is None:
                return HttpResponseBadRequest("Error: please supply duration")             
            marks_awarded_per_correct_ans = data.get('marks_awarded_per_correct_ans', None)
            if marks_awarded_per_correct_ans is None:
                return HttpResponseBadRequest("Error: please supply marks_awarded_per_correct_ans")             
            marks_deducted_per_incorrect_ans = data.get('marks_deducted_per_incorrect_ans', None)
            if marks_deducted_per_incorrect_ans is None:
                return HttpResponseBadRequest("Error: please supply marks_deducted_per_incorrect_ans")             
            created_by = Teacher.objects.get(id=int(user_id))
            created_on = datetime.now().replace(tzinfo=pytz.UTC)
            test = Test(name=test_name, start_time=start_time, duration=duration,\
                marks_awarded_per_correct_ans= marks_awarded_per_correct_ans,marks_deducted_per_incorrect_ans= marks_deducted_per_incorrect_ans ,\
                    created_by=created_by, created_on=created_on)
            test.save()
            questions = data.get('questions', None)
            for question in questions:
                question_obj = Question(question_text=question['question_text'], test = test, pub_date= datetime.now().replace(tzinfo=pytz.UTC))
                question_obj.save()
                choice_1 = Choice(question=question_obj, choice=question['choice_1']['text'], is_correct=question['choice_1']['is_correct'], position=1)
                choice_1.save()
                choice_2 = Choice(question=question_obj, choice=question['choice_2']['text'], is_correct=question['choice_2']['is_correct'], position=2)
                choice_2.save()
                choice_3 = Choice(question=question_obj, choice=question['choice_3']['text'], is_correct=question['choice_3']['is_correct'], position=3)
                choice_3.save()
                choice_4 = Choice(question=question_obj, choice=question['choice_4']['text'], is_correct=question['choice_4']['is_correct'], position=4)
                choice_4.save()
                                                
            json_response = {
                "id": test.id
            }

            return JsonResponse(json_response, status=200)

        except Exception as e:
            print(e)
            raise InternalServerError()


class AssignTest(APIView):
    def post(self, request, *args, **kwargs):
        """
        API overview:-- 
        Assigns tests to students using the supplied input parameters
        Inputs:
            1. user_id of the teacher
            2. A list of tests where each item has:
                a. test_id of the test
                b. student_id of student to whom this test will be assigned
        Output:
            The count of successful test assignment operations
        """

        try:
            data = request.data
            user_id = data.get('user_id', None)
            if user_id is None or len(Teacher.objects.filter(id=int(user_id))) == 0:
                return HttpResponseBadRequest("Error: please supply correct user_id")

            tests = data.get('tests', None)
            if tests is None:
                return HttpResponseBadRequest("Error: please supply tests")    

            count = 0
            for test in tests:
                if len(Test.objects.filter(id=int(test['test_id']))) == 0:
                    return HttpResponseBadRequest(f"Error: Test with test_id {test['test_id']} doesn't exist")
                if len(Student.objects.filter(id=int(test['student_id']))) == 0:
                    return HttpResponseBadRequest(f"Error: Student with student_id {test['student_id']} doesn't exist")
                test_obj = Test.objects.get(id=int(test['test_id']))
                test_obj.assigned_to.add(int(test['student_id']))
                test_obj.save()
                count += 1

            json_response = {
                "successful_count": count
            }

            return JsonResponse(json_response, status=200)

        except Exception as e:
            print(e)
            raise InternalServerError()

class AssignedTestsPerStudent(APIView):
    def get(self, request, *args, **kwargs):
        """
        API overview:
        Returns the list of tests that has been assigned to a particualr student
        Input: user_id of the student
        Output: list of assigned tests for this student, where each test has id, name, created_on, start_time, duration, marks_awarded_per_correct_ans, marks_deducted_per_incorrect_ans
        """

        try:
            user_id = request.query_params.get('user_id', None)
            if user_id is None or len(Student.objects.filter(id=int(user_id))) == 0:
                return HttpResponseBadRequest("Error: please supply correct user_id")
            tests = list(Student.objects.get(id=int(user_id)).assigned_tests.values('id', 'name','created_on', 'start_time', 'duration', 'marks_awarded_per_correct_ans', 'marks_deducted_per_incorrect_ans'))

            json_response = {
                "tests": tests
            }

            return JsonResponse(json_response, status=200)

        except Exception as e:
            print(e)
            raise InternalServerError()



class OpenTest(APIView):
    def get(self, request, pk=None, format=None):
        """
        API overviews:--
        Returns the list of questions of a particular test. If students tries to use this api before start_time, error is returned.
        Inputs:
            1. user_id of the student
            2. test_id supplied as pk (i.e. directly after assigned_tests/ in URI)
        Outputs:
            The list of questions where each question has id, question_text, choices
        """

        try:
            user_id = request.query_params.get('user_id', None)
            if user_id is None or len(Student.objects.filter(id=int(user_id))) == 0:
                return HttpResponseBadRequest("Error: please supply correct user_id")            
            
            test_id = pk
            if test_id is None:
                return HttpResponseBadRequest("Error: please supply test_id after assigned_tests/") 
            if len(Test.objects.filter(pk=pk)) != 1:
                return HttpResponseBadRequest(f"Error: Test with test_id {test_id} doesn't exist") 

            test = Test.objects.get(pk=pk)

            if len(Student.objects.filter(id=int(user_id))) != 1:
                return HttpResponseBadRequest(f"Error: User with user_id {user_id} doesn't exist")

            if int(user_id) not in test.assigned_to.all().values_list('id',flat=True):
                return HttpResponseBadRequest(f"Error: Test with test_id {test_id} isn't assigned to user with user_id {user_id}")

            if datetime.now().replace(tzinfo=pytz.UTC) < test.start_time:
                return HttpResponseBadRequest("Error: Can't open test before specified start_time")

            result = list()
            questions = test.questions.all()
            for question in questions:
                choices = list(question.choices.all().values('id','choice', 'position'))
                q_list = {}
                q_list['id'] = question.id
                q_list['question_text'] = question.question_text
                q_list['choices'] = choices
                result.append(q_list)


            json_response = {
                "questions": result
            }

            return JsonResponse(json_response, status=200)

        except Exception as e:
            print(e)
            raise InternalServerError()


class SubmitAnswers(APIView):
    def post(self, request, *args, **kwargs):
        """
        API overview:--
        Submits the answers for questions. Error is returned if user submits after test duration ends. If all validations pass
        then marks are increased/decreased based upon specifiec test parameters, and finally score corresponding to this student 
        and test are saved.
        Input:
            1. user_id of student
            2. test_id of the test
            3. dict of answers where each answer has:
                a. question_id
                b. chosen_choice_id
        Output:
            count of answers for which marks were calculated (increased/decreased) before finally being saved as score.
        """

        try:
            data = request.data
            user_id = data.get('user_id', None)
            if user_id is None or len(Student.objects.filter(id=int(user_id))) == 0:
                return HttpResponseBadRequest("Error: please supply correct user_id")
            user = Student.objects.get(id=int(user_id))
            
            test_id = data.get('test_id', None)
            if test_id is None:
                return HttpResponseBadRequest("Error: please supply test_id") 
            if len(Test.objects.filter(id=int(test_id))) != 1:
                return HttpResponseBadRequest(f"Error: Test with test_id {test_id} doesn't exist") 
            test = Test.objects.get(id=int(test_id))

            answers = data.get('answers', None)
            if answers is None or len(answers)==0:
                return HttpResponseBadRequest("Error: please supply answers as well")

            
            if len(Score.objects.filter(user__id=int(user_id), test__id=int(test_id))) == 0:
                score = Score(user=user, test=test, marks = 0)
            else:
                score = Score.objects.get(user__id=int(user_id), test__id=int(test_id))
            
            if datetime.now().replace(tzinfo=pytz.UTC) > test.start_time+timedelta(minutes=test.duration):
                return HttpResponseBadRequest("Error: Can't submit test after test duration is over")

            count = 0
            for answer in answers:
                if len(Question.objects.filter(id=int(answer['question_id']), test=test)) == 0:
                    return HttpResponseBadRequest(f"Error: Question with id {int(answer['question_id'])} either doesn't exist or doesn't belong to this test.")
                question = Question.objects.get(id=int(answer['question_id']), test=test)
                if question.choices.get(is_correct=True).id == int(answer['chosen_choice_id']):
                    score.marks += test.marks_awarded_per_correct_ans
                else:
                    score.marks -= test.marks_deducted_per_incorrect_ans
                count += 1
            score.save()

            json_response = {
                "insertion_successful_count": count
            }

            return JsonResponse(json_response,status=200)

        except Exception as e:
            print(e)
            raise InternalServerError()

class AllScores(APIView):
    def get(self, request, *args, **kwargs):
        """
        API overview:--
        Returns the json containing scores for all students.
        Output:
            a json containing list of scores where each score has id, user__id, user__first_name, user__last_name, test__id, test__name, marks
        """

        try:

            scores = list(Score.objects.all().values('id', 'user__id', 'user__first_name', 'user__last_name','test__id', 'test__name', 'marks'))

            json_response = {
                "scores": scores
            }

            return JsonResponse(json_response, status=200)

        except Exception as e:
            print(e)
            raise InternalServerError()

class ScorePerStudent(APIView):
    def get(self, request, pk=None, format=None):
        """
        API overview:--
        Returns the json containing scores for a particular student
        Input: student_id of the student as pk (i.e. directly after scores/ in URI)
        Output:
            a json containing list of scores for a particualr student where each score has id, user__id, user__first_name, user__last_name, test__id, test__name, marks
        """        

        try:

            student_id = pk
            if student_id is None:
                return HttpResponseBadRequest("Error: please supply student_id after scores/") 
            if len(Student.objects.filter(pk=pk)) != 1:
                return HttpResponseBadRequest(f"Error: Test with student_id {student_id} doesn't exist") 

            scores = list(Score.objects.get(id=int(student_id)).values('id', 'user__id', 'user__first_name', 'user__last_name','test__id', 'test__name', 'marks'))

            json_response = {
                "scores": scores
            }

            return JsonResponse(json_response, status=200)

        except Exception as e:
            print(e)
            raise InternalServerError()

    
