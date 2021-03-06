import json

from django.test import TestCase, Client
from rest_framework.test import APIClient

from prehab_app.models import User, Role


class TestSuit(TestCase):
    fixtures = (
        'constraint_types.json',
        'meal_constraint_type.json',
        'meals.json',
        'roles.json',
        'tasks.json',
        'users.json'
    )

    def setUp(self):
        self.client = Client()

        self.admin_role = Role.objects.get(pk=1)
        self.doctor_role = Role.objects.get(pk=2)
        self.patient_role = Role.objects.get(pk=3)

        self.admin_user = User.objects.get(pk=1)
        self.doctor_user = User.objects.get(pk=2)
        self.patient_user = User.objects.get(pk=3)

        self.admin_jwt = self.get_jwt_from_login('admin', 'admin', platform='web')
        self.doctor_jwt = self.get_jwt_from_login('doctor', 'doctor', platform='web')
        self.patient_jwt = self.get_jwt_from_login('patient', 'patient', platform='mobile')

        # Set Task Schedule and prehab
        body = {
            "title": "New Task Schedule",
            "number_of_weeks": 2,
            "weeks": [
                {
                    "week_number": 1,
                    "tasks": [
                        {
                            "task_id": 1,
                            "times_per_week": 5
                        },
                        {
                            "task_id": 2,
                            "times_per_week": 3
                        },
                        {
                            "task_id": 3,
                            "times_per_week": 2,
                            "repetition_number": 10
                        }
                    ]
                },

                {
                    "week_number": 2,
                    "tasks": [
                        {
                            "task_id": 1,
                            "times_per_week": 1
                        },
                        {
                            "task_id": 2,
                            "times_per_week": 12
                        },
                        {
                            "task_id": 3,
                            "times_per_week": 3,
                            "repetition_number": 20
                        }
                    ]
                }
            ]
        }
        self.http_request('post', '/api/schedule/task/full/', body, 'admin')

        body = {
            "patient_id": 3,
            "init_date": "22-05-2018",
            "surgery_date": "06-06-2018",
            "task_schedule_id": 1
        }
        self.http_request('post', '/api/prehab/', body, 'admin')

        # MArk 1 as done
        body = {
            "patient_task_schedule_id": 16,
            "completed": True,
            "difficulties": True,
            "notes": "Doi me as costas"
        }
        self.http_request('post', '/api/patient/schedule/task/done/', body, 'patient')

    def get_jwt_from_login(self, username, password, platform='web'):
        headers = {'HTTP_PLATFORM': platform}
        url = '/api/login/'
        body = {'username': username, 'password': password}

        return self.client.post(url, json.dumps(body), **headers, format='json',
                                content_type='application/json').json()['data']['jwt']

    def http_request(self, method, url, body=None, auth_user=None, custom_headers=None, platform='web'):
        if not url.endswith('/'):
            url += '/'

        headers = {'HTTP_PLATFORM': platform}

        if auth_user in ('admin', 'Admin') or auth_user is None:
            headers = {**headers, 'HTTP_JWT': self.admin_jwt}
        elif auth_user in ('doctor', 'Doctor'):
            headers = {**headers, 'HTTP_JWT': self.doctor_jwt}
        elif auth_user in ('patient', 'Patient'):
            headers = {**headers, 'HTTP_JWT': self.patient_jwt}

        # if custom_auth is not None:
        #     jwt = self.get_jwt_from_login(custom_auth['username'], custom_auth['password'])
        #     headers = {'HTTP_JWT': jwt}

        if custom_headers is not None:
            headers = {**headers, **custom_headers}

        if body is None:
            body = dict()

        client = APIClient()

        if method == 'get' or method == 'GET':
            response = client.get(url, **headers)
        elif method == 'post' or method == 'POST':
            response = self.client.post(url, json.dumps(body), **headers, format='json',
                                        content_type='application/json')
        elif method == 'put' or method == 'PUT':
            response = self.client.put(url, json.dumps(body), **headers, format='json', content_type='application/json')
        elif method == 'delete' or method == 'DELETE':
            response = self.client.delete(url, json.dumps(body), **headers, format='json',
                                          content_type='application/json')
        else:
            response = None

        return response
