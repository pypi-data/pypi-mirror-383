from unittest.mock import patch

import requests_mock

from django.test import TestCase, override_settings

from memberaudit import tasks
from memberaudit.core import esi_status
from memberaudit.tests.testdata.esi_client_stub import esi_stub
from memberaudit.tests.testdata.load_entities import load_entities
from memberaudit.tests.testdata.load_eveuniverse import load_eveuniverse
from memberaudit.tests.testdata.load_locations import load_locations
from memberaudit.tests.utils import (
    create_memberaudit_character,
    reset_celery_once_locks,
)

MANAGERS_PATH = "memberaudit.managers"
MODELS_PATH = "memberaudit.models"
TASKS_PATH = "memberaudit.tasks"


# TODO: Replace esi_stubs with http request mocks
@patch(MANAGERS_PATH + ".character_sections_1.data_retention_cutoff", lambda: None)
@patch(MANAGERS_PATH + ".character_sections_2.data_retention_cutoff", lambda: None)
@patch(MANAGERS_PATH + ".character_sections_3.data_retention_cutoff", lambda: None)
@patch("app_utils.esi._esi", esi_stub)
@patch(MANAGERS_PATH + ".character_sections_1.esi", esi_stub)
@patch(MANAGERS_PATH + ".character_sections_2.esi", esi_stub)
@patch(MANAGERS_PATH + ".character_sections_3.esi", esi_stub)
@patch(MANAGERS_PATH + ".general.esi", esi_stub)
@requests_mock.Mocker()
@override_settings(
    CELERY_ALWAYS_EAGER=True,
    CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
    APP_UTILS_OBJECT_CACHE_DISABLED=True,
)
class TestTasksIntegration(TestCase):
    fixtures = ["disable_analytics.json"]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        load_eveuniverse()
        load_entities()
        load_locations()
        reset_celery_once_locks()
        esi_status.clear_cache()

    def test_should_update_all_characters(self, requests_mocker):
        # given
        character_1001 = create_memberaudit_character(1001)
        requests_mocker.register_uri(
            "GET",
            url="https://esi.evetech.net/status.json?version=latest",
            json=[
                {
                    "endpoint": "esi-mail",
                    "method": "get",
                    "route": "/characters/{character_id}/mail/",
                    "status": "green",
                    "tags": ["Mail"],
                }
            ],
        )
        requests_mocker.register_uri(
            "GET",
            url="https://esi.evetech.net/latest/status/",
            headers={
                "X-Esi-Error-Limit-Remain": "40",
                "X-Esi-Error-Limit-Reset": "30",
            },
            json={
                "players": 12345,
                "server_version": "1132976",
                "start_time": "2017-01-02T12:34:56Z",
            },
        )
        # when
        tasks.update_all_characters()
        # then
        self.assertTrue(character_1001.is_update_status_ok())
