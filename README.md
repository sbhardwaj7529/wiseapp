# wiseapp
## Project structure
1. `wiseapp/myenv/` directory contains the files that can be used to create a virtual python environment to run this project.
2. `wiseapp/shivam_wiseapp.postman_collection.json` is the postman collection of APIs that can be imported in Postman for testing the APIs of this project.
3. `wiseapp/WiseTestPlatform/` directory contains the files corresponding to the django project that hosts all the django apps of this project.
    - `wiseapp/WiseTestPlatform/db.sqlite3` is the resident sqlite based in-built DB that's shipped with python. We'd be using this DB as the relational database for our project.
    - `wiseapp/WiseTestPlatform/manage.py` is the django related file used to run management commands. We'll be primarily using it to start the django server etc.
    -  `wiseapp/WiseTestPlatform/WiseTestPlatform/` contains files like `settings.py`, `asgi.py`, `urls.py` etc. The file `urls.py` is of the main relevant file to us here as it contains the list of main endpoints that we'll be exposing as part of our project.
    - `wiseapp/WiseTestPlatform/WiseTestApp/` contains many files. But the ones relevant to us are:
      * `models.py` file which contains all the models relevant to our app. A model in django is just a mapping of a python class to a corresponding DB table, where the fields of the class correspond to column of the table.
      * `urls.py` file which contains the mapping of our API functions to the endpoints (URIs) exposed as part of this prject. The contents of this file are imported by the main `urls.py` present in `wiseapp/WiseTestPlatform/WiseTestPlatform/` directory.
      * `api.py` file which contains the definitions of all the APIs that we have exposed as part of this project. The stuff in `urls.py` maps the endpoints (URIs) the classes/functions of this file.
      
## How to setup this project
1. Clone this repo in your local machine by running `git clone git@github.com:sbhardwaj7529/wiseapp.git`
2. Ensure that you have python3 installed in your local machine.
3. `cd` into the newly cloned repository and start the python virtual environment by running `source myenv/bin/activate`
4. Then run `cd WiseTestPlatform` once, and run `python manage.py runserver` to start the django server. By default, the port is 8000. Thus the app is exposed at `http://localhost:8000`
5. Import the postman collection present in the root directory of this project to Postman for APIs testing.

## Database Schema and models.py
#### Model `User`
1. Implicit field `id`: autoincrementing Integer type value, primary_key
2. Field `username`: CharField type value, max_length `200`, allowed to be `null`
3. Field `first_name`
4. Field `last_name`
5. Field `email`

#### Model `Student` inheriting `User`
1. Field `roll_no`: Integer type value, allowed to be `null` [P.S.: I know I shouldn't have allowed null, and should've kept unique constraint. :P]
2. Field `class_name`: CharField type value, max_length `200`, allowed to be `null`
3. Field `section`: CharField type value, max_length `200`, allowed to be `null`

#### Model `Teacher` inheriting `User`
1. Field `department`: CharField type value, max_length `200`, allowed to be `null`
2. Field `joining_year`: DateTime type value, allowed to be `null`
3. Implicit field `id`: autoincrementing Integer type value, primary_key

#### Model `Test`
1. Field `name`: CharField type value, max_length `200`, allowed to be `null` [Note: Ideally, I wouldn't have allowed null, and applied unique constraint.]
2. Field `start_time`: DateTimeField type value, `null` not allowed
3. Field `duration`: IntegerField type value, represents number of minutes, `null` nort allowed
4. Field `marks_awarded_per_correct_ans`: IntegerField type value, `null` not allowed
5. Field `marks_deducted_per_incorrect_ans`: IntegerField type value, `null` not allowed
6. Field `created_by`: ForeignKey to `Teacher`, can be reverse queried from `Teacher` object using `tests`, `CASCADE` ON DELETE
7. Field `created_on`: DateTimeField type value, `null` not allowed
8. Field `assigned_to`: ManyToManyField to `Student`, can be reverse queried from `Student` object using `assigned_tests`
9. Implicit field `id`: autoincrementing Integer type value, primary_key

#### Model `Question`
1. Field `question_text`: CharField type value, `null` not allowed, max_length `200`
2. Field `test`: ForeignKey to `Test`, can be reverse queried from `Test` object using `questions`, `CASCADE` ON DELETE
3. Field `pub_date`: DateTimeField type value, `null` not allowed
4. Implicit field `id`: autoincrementing Integer type value, primary_key

#### Model `Choice`
1. Field `question`: ForeignKey to `Question`, can be reverse queried from `Question` using `choices`, `CASCADE` ON DELETE
2. Field `choice`: represent the text of the choice, CharField type value, `null` not allowed, max_length `200`
3. Field `position`: represent the position of the ordering of the choice in comparison to other choices, Integer type value
4. Field `is_correct`: BooleanField value
5. Implicit field `id`: autoincrementing Integer type value, primary_key

Important constraints:
1. `question` and `choice` are unique together to disallow duplicated choice per question
2. `question` and `position` are unique together to disallow duplicated position per question 

#### Model `Score`
1. Field `user`: ForeignKey to `Student`, can be reverse queried from `Student` using `scores`, `CASCADE` ON DELETE
2. Field `test`: ForeignKey to `Test`, can be reverse queried from `Test` using `scores`, `CASCADE` ON DELETE
3. Field `marks`: IntegerField value, can't be `null`
4. Implicit field `id`: autoincrementing Integer type value, primary_key

Important constraints:
1. `user` and `test` are unique together to disallow duplicated test per user

## API contracts
### GET `http://localhost:8000/wisetestapp/teachers/`
    Returns the list of teachers in the system
    Output: json cotaining list of teachers with their id, username, first_name, last_name, department
    
    Sample Output:
    {
        "teachers": [
            {
                "id": 5,
                "username": "walterwhite",
                "first_name": "Walter",
                "last_name": "White",
                "department": "Chemistry"
            }
        ]
    }

### GET `http://localhost:8000/wisetestapp/students/`
    Returns the list of students in the system
    output: json cotaining list of teachers with their id, username, first_name, last_name, roll_no, class_name, section

    Sample Output:
    {
        "students": [
            {
                "id": 4,
                "username": "jessepinkman",
                "first_name": "Jesse",
                "last_name": "Pinkman",
                "roll_no": 1,
                "class_name": "Chemistry 101",
                "section": "A"
            },
            {
                "id": 6,
                "username": "galeboetticher",
                "first_name": "Gale",
                "last_name": "Boetticher",
                "roll_no": 2,
                "class_name": "Chemistry 101",
                "section": "A"
            }
        ]
    }        


### POST `http://localhost:8000/wisetestapp/tests/`

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

    Sample Input:
    {
        "user_id": "5",
        "test_name": "My Fifth test",
        "start_time": "2022-06-25T15:00:00",
        "duration": "60",
        "marks_awarded_per_correct_ans": "1",
        "marks_deducted_per_incorrect_ans": "0",
        "questions": [
            {
                "question_text": "What is the symbol for Hydrogen in periodic table",
                "choice_1": {"text": "Na", "is_correct": false},
                "choice_2":  {"text": "K", "is_correct": false},
                "choice_3":  {"text": "H", "is_correct": true},
                "choice_4":  {"text": "He", "is_correct": false}
            }
        ]
    }

    Sample Output:
    {
        "id": 5
    }


### GET `http://localhost:8000/wisetestapp/tests_per_teacher/`
    Returns the list of tests created by a particular teacher
    inputs: user_id of teacher
    output: json containing the list of tests with their id, name, created_on, start_time, duration, marks_awarded_per_correct_ans, marks_deducted_per_incorrect_ans

    Sample Input:
    /?user_id=5

    Sample Output:
    {
        "tests": [
            {
                "id": 4,
                "name": "My Fourth test",
                "created_on": "2022-06-27T13:29:59.301Z",
                "start_time": "2022-06-25T15:00:00Z",
                "duration": 60,
                "marks_awarded_per_correct_ans": 1,
                "marks_deducted_per_incorrect_ans": 0
            }
        ]
    }

### POST `http://localhost:8000/wisetestapp/assign_tests/`
    Assigns tests to students using the supplied input parameters
    Inputs:
        1. user_id of the teacher
        2. A list of tests where each item has:
            a. test_id of the test
            b. student_id of student to whom this test will be assigned
    Output:
        The count of successful test assignment operations
     
    Sample Input:
    {
        "user_id": "5",
        "tests" : [
            {
                "test_id": "4",
                "student_id": "4"
            },
            {
                "test_id": "4",
                "student_id": "6"
            }        

        ]
    }

    Sample Output:
    {
        "successful_count": 2
    }

### GET `http://localhost:8000/wisetestapp/assigned_tests/`
    Returns the list of tests that has been assigned to a particualr student
    Input: user_id of the student
    Output: list of assigned tests for this student, where each test has id, name, created_on, start_time, duration, marks_awarded_per_correct_ans, marks_deducted_per_incorrect_ans

    Sample Input:
    /?user_id=4

    Sample Output:
    {
        "tests": [
            {
                "id": 4,
                "name": "My Fourth test",
                "created_on": "2022-06-27T13:29:59.301Z",
                "start_time": "2022-06-25T15:00:00Z",
                "duration": 60,
                "marks_awarded_per_correct_ans": 1,
                "marks_deducted_per_incorrect_ans": 0
            }
        ]
    }

### GET `http://localhost:8000/wisetestapp/assigned_tests/<int: pk>/`
    Returns the list of questions of a particular test. If students tries to use this api before start_time, error is returned.
    Inputs:
        1. user_id of the student
        2. test_id supplied as pk (i.e. directly after assigned_tests/ in URI)
    Outputs:
        The list of questions where each question has id, question_text, choices

    Sample Input:
    ?user_id=4

    Sample Output:
    {
        "questions": [
            {
                "id": 4,
                "question_text": "What is the symbol for Hydrogen in periodic table",
                "choices": [
                    {
                        "id": 13,
                        "choice": "Na",
                        "position": 1
                    },
                    {
                        "id": 14,
                        "choice": "K",
                        "position": 2
                    },
                    {
                        "id": 15,
                        "choice": "H",
                        "position": 3
                    },
                    {
                        "id": 16,
                        "choice": "He",
                        "position": 4
                    }
                ]
            }
        ]
    }

### POST `http://localhost:8000/wisetestapp/submission/`
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

    Sample Input:
    {
        "user_id": "4",
        "test_id": "4",
        "answers" : [
            {
                "question_id": "4",
                "chosen_choice_id": "15"
            }
        ]
    }

    Sample Output:
    {
        "insertion_successful_count": 1
    }

### GET `http://localhost:8000/wisetestapp/scores/`
    Returns the json containing scores for all students.
    Output:
        a json containing list of scores where each score has id, user__id, user__first_name, user__last_name, test__id, test__name, marks

    Sample Output:
    {
        "scores": [
            {
                "id": 1,
                "user__id": 4,
                "user__first_name": "Jesse",
                "user__last_name": "Pinkman",
                "test__id": 4,
                "test__name": "My Fourth test",
                "marks": 1
            }
        ]
    }

### GET `http://localhost:8000/wisetestapp/scores/<int: pk>/`
    Returns the json containing scores for a particular student
    Input: student_id of the student as pk (i.e. directly after scores/ in URI)
    Output:
        a json containing list of scores for a particualr student where each score has id, user__id, user__first_name, user__last_name, test__id, test__name, marks

    Sample Output:
    {
        "scores": [
            {
                "id": 1,
                "user__id": 4,
                "user__first_name": "Jesse",
                "user__last_name": "Pinkman",
                "test__id": 4,
                "test__name": "My Fourth test",
                "marks": 1
            }
        ]
    }
