"""
Unit tests for Django app "api" views/outputs
"""

import base64
import json
import uuid

from mock import patch, MagicMock
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from api.models.configuration import (
    Model,
    Model_User,
    Scenario,
    Abstract_Tech,
    Loc_Tech,
    Location,
    Technology
)
from api.models.outputs import Run
from taskmeta.models import CeleryTask


class BuildViewTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="my-username",
            email="my-email@example.com",
            password="my-password"
        )
        self.model = Model.objects.create(name="my-model")
        self.model_user = Model_User.objects.create(
            model=self.model,
            user=self.user,
            can_edit=True
        )
        self.scenario = Scenario.objects.create(
            name="my-scenario",
            model=self.model
        )
        self.client.login(username="my-username", password="my-password")
    
    def tearDown(self):
        self.client.logout()
    
    @staticmethod
    def get_async_result():
        result = MagicMock()
        result.id = str(uuid.uuid4())
        return result

    @patch("api.task.build_model")
    def test_build(self, build_model):
        build_model.side_effect = self.get_async_result
        data = {
            "model_uuid": str(self.model.uuid),
            "scenario_id": self.scenario.id,
            "start_date": "2015-01-01",
            "end_date": "2015-01-02"
        }
        response = self.client.get(reverse("build"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            "status": "Success",
            "model_uuid": str(self.model.uuid),
            "scenario_id": self.scenario.id,
            "year": 2015,
        })

        runs = Run.objects.all()
        self.assertEqual(len(runs), 1)


class OptimizeViewTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="my-username",
            email="my-email@example.com",
            password="my-password"
        )
        self.model = Model.objects.create(name="my-model")
        self.model_user = Model_User.objects.create(
            model=self.model,
            user=self.user,
            can_edit=True
        )
        self.scenario = Scenario.objects.create(
            name="my-scenario",
            model=self.model
        )
        self.run = Run.objects.create(
            scenario=self.scenario,
            subset_time="2015-01-01 2015-01-02",
            year=2015,
            status="",
            message="run message",
            inputs_path="/this/is/inputs",
            logs_path="",
            outputs_path="",
            plots_path="",
            model=self.model
        )
        self.client.login(username="my-username", password="my-password")
    
    def tearDown(self):
        self.client.logout()
    
    @staticmethod
    def get_async_result():
        result = MagicMock()
        result.id = str(uuid.uuid4())
        return result

    @patch("api.tasks.run_model")
    def test_optimize(self, run_model):
        run_model.side_effect = self.get_async_result
        data = {
            "model_uuid": str(self.model.uuid),
            "run_id": self.run.id
        }
        response = self.client.post(reverse("optimize"), data=data)
        self.assertEqual(response.status_code, 200)


class DeleteRunViewTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="my-username",
            email="my-email@example.com",
            password="my-password"
        )
        self.model = Model.objects.create(name="my-model")
        self.model_user = Model_User.objects.create(
            model=self.model,
            user=self.user,
            can_edit=True
        )
        self.scenario = Scenario.objects.create(
            name="my-scenario",
            model=self.model
        )
        self.run = Run.objects.create(
            scenario=self.scenario,
            subset_time="2015-01-01 2015-01-02",
            year=2015,
            status="",
            message="run message",
            inputs_path="/this/is/inputs",
            logs_path="",
            outputs_path="",
            plots_path="",
            model=self.model
        )
        self.client.login(username="my-username", password="my-password")
    
    def tearDown(self):
        self.client.logout()
    
    def test_delete_run(self):
        data = {
            "model_uuid": str(self.model.uuid),
            "run_id": self.run.id
        }
        response = self.client.post(reverse("delete_run"), data=data)
        self.assertEqual(response.status_code, 302)


class UpdateRunDescriptionViewTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="my-username",
            email="my-email@example.com",
            password="my-password"
        )
        self.model = Model.objects.create(name="my-model")
        self.model_user = Model_User.objects.create(
            model=self.model,
            user=self.user,
            can_edit=True
        )
        self.scenario = Scenario.objects.create(
            name="my-scenario",
            model=self.model
        )
        self.run = Run.objects.create(
            scenario=self.scenario,
            subset_time="2015-01-01 2015-01-02",
            year=2015,
            status="",
            message="run message",
            inputs_path="/this/is/inputs",
            logs_path="",
            outputs_path="",
            plots_path="",
            model=self.model
        )
        self.client.login(username="my-username", password="my-password")
    
    def tearDown(self):
        self.client.logout()
    
    def test_update_run_description(self):
        data = {
            "model_uuid": str(self.model.uuid),
            "id": self.run.id,
            "value": "this is new run description."
        }
        response = self.client.post(reverse("update_run_description"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"this is new run description.")


class DownloadViewTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="my-username",
            email="my-email@example.com",
            password="my-password"
        )
        self.model = Model.objects.create(name="my-model")
        self.model_user = Model_User.objects.create(
            model=self.model,
            user=self.user,
            can_edit=True
        )
        self.client.login(username="my-username", password="my-password")
    
    def tearDown(self):
        self.client.logout()
    
    def test_download(self):
        data = {
            "path": "../data/test-timeseries.csv",
            "model_uuid": str(self.model.uuid)
        }
        response = self.client.get(reverse("download"), data=data)
        self.assertEqual(response.status_code, 200)

    def test_download__file_not_existing(self):
        data = {
            "path": "../data/unknown.csv",
            "model_uuid": str(self.model.uuid)
        }
        response = self.client.get(reverse("download"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"message": "Not Found!"})
