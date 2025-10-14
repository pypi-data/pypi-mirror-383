from datetime import timedelta
from unittest import skipIf
from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils.timezone import now
from django_webtest import WebTest

from structuretimers.models import ScheduledNotification, Timer
from structuretimers.tasks import send_test_message_to_webhook

from .testdata.factory import (
    create_discord_webhook,
    create_notification_rule,
    create_timer,
    create_user,
)
from .testdata.fixtures import LoadTestDataMixin
from .utils import _is_aa4, add_permission_to_user_by_name

MODELS_PATH = "structuretimers.models"
FORMS_PATH = "structuretimers.forms"
TASKS_PATH = "structuretimers.tasks"

# TODO: Rewrite tests to work also with AA4


@patch(MODELS_PATH + "._task_calc_timer_distances_for_all_staging_systems", Mock())
@patch(MODELS_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
class TestUI(LoadTestDataMixin, WebTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user_basic = create_user(cls.character_1)

        cls.user_create = create_user(cls.character_2)
        cls.user_create = add_permission_to_user_by_name(
            "structuretimers.create_timer", cls.user_create
        )

    @patch(MODELS_PATH + ".STRUCTURETIMERS_NOTIFICATIONS_ENABLED", False)
    def setUp(self) -> None:
        self.timer_1 = create_timer(
            structure_name="Timer 1",
            date=now() + timedelta(hours=4),
            eve_character=self.character_2,
            eve_corporation=self.corporation_1,
            user=self.user_create,
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
        )
        self.timer_2 = create_timer(
            structure_name="Timer 2",
            date=now() - timedelta(hours=8),
            eve_character=self.character_2,
            eve_corporation=self.corporation_1,
            user=self.user_create,
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
        )
        self.timer_3 = create_timer(
            structure_name="Timer 3",
            date=now() - timedelta(hours=8),
            eve_character=self.character_2,
            eve_corporation=self.corporation_1,
            user=self.user_create,
            eve_solar_system=self.system_enaluri,
            structure_type=self.type_astrahus,
        )

    def test_should_add_new_timer(self):
        """
        when user has permissions
        then he can create a new timer
        """

        # login
        self.app.set_user(self.user_create)

        # user opens timerboard
        timerboard = self.app.get(reverse("structuretimers:timer_list"))
        self.assertEqual(timerboard.status_code, 200)

        # user clicks on "Add Timer"
        add_timer = timerboard.click(href=reverse("structuretimers:add"))
        self.assertEqual(add_timer.status_code, 200)

        # user enters data and clicks create
        form = add_timer.forms["add-timer-form"]
        form["structure_name"] = "Timer 4"
        form["eve_solar_system_2"].force_value([str(self.system_abune.id)])
        form["structure_type_2"].force_value([str(self.type_astrahus.id)])
        form["timer_type"] = Timer.Type.ANCHORING
        form["days_left"] = 1
        form["hours_left"] = 2
        form["minutes_left"] = 3
        response = form.submit()

        # assert results
        timer_date = now() + timedelta(days=1, hours=2, minutes=3)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("structuretimers:timer_list"))
        obj = Timer.objects.get(structure_name="Timer 4")
        self.assertEqual(obj.eve_solar_system, self.system_abune)
        self.assertEqual(obj.structure_type, self.type_astrahus)
        self.assertEqual(obj.timer_type, Timer.Type.ANCHORING)
        self.assertAlmostEqual(obj.date, timer_date, delta=timedelta(seconds=10))

    @skipIf(_is_aa4, "test is not compatible with AA4")
    def test_add_new_timer_without_permission(self):
        """
        given a user does not have permissions
        when trying to access page for adding new timers
        then the form is not shown
        """

        # login
        self.app.set_user(self.user_basic)

        # Add button not shown to user
        timerboard = self.app.get(reverse("structuretimers:timer_list"))
        with self.assertRaises(IndexError):
            timerboard.click(href=reverse("structuretimers:add"))

        # form is not shown
        response = self.app.get(reverse("structuretimers:add"))
        self.assertNotIn(
            "add-timer-form", response.forms
        )  # TODO: Change to test for HTTP error code, once available

    def test_edit_existing_timer(self):
        """
        when user has permissions
        then he can edit an existing timer
        """

        # login
        self.app.set_user(self.user_create)

        # user opens timerboard
        timerboard = self.app.get(reverse("structuretimers:timer_list"))
        self.assertEqual(timerboard.status_code, 200)

        # user clicks on "Edit Timer" for timer 1
        edit_timer = self.app.get(
            reverse("structuretimers:edit", args=[self.timer_1.pk])
        )
        self.assertEqual(edit_timer.status_code, 200)

        # user enters data and clicks create
        form = edit_timer.forms["add-timer-form"]
        form["owner_name"] = "The Boys"
        response = form.submit()
        self.timer_1.refresh_from_db()

        # assert results
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("structuretimers:timer_list"))
        self.assertEqual(self.timer_1.owner_name, "The Boys")

    @skipIf(_is_aa4, "test is not compatible with AA4")
    def test_edit_timer_without_permission_1(self):
        """
        given a user does not have permissions
        when trying to access page for timer edit
        then the form is not shown
        """

        # login
        self.app.set_user(self.user_basic)

        # user tries to access page for edit directly
        response = self.app.get(reverse("structuretimers:edit", args=[self.timer_1.pk]))
        self.assertNotIn(
            "add-timer-form", response.forms
        )  # TODO: Change to test for HTTP error code, once available

    @skipIf(_is_aa4, "test is not compatible with AA4")
    def test_edit_timer_of_others_without_permission_2(self):
        """
        given a user has permission to create tiemrs
        when trying to access page for timer edit of another user
        then the form is not shown
        """

        # login
        user_3 = create_user(self.character_3)
        user_3 = add_permission_to_user_by_name("structuretimers.create_timer", user_3)
        self.app.set_user(user_3)

        # user tries to access page for edit directly
        response = self.app.get(reverse("structuretimers:edit", args=[self.timer_1.pk]))
        self.assertNotIn(
            "add-timer-form", response.forms
        )  # TODO: Change to test for HTTP error code, once available

    @skipIf(_is_aa4, "test is not compatible with AA4")
    def test_edit_timer_of_others_with_manager_permission(self):
        """
        when a user has manager permission
        then he can edit timers of others
        """

        # login
        user_3 = create_user(self.character_3)
        user_3 = add_permission_to_user_by_name("structuretimers.manage_timer", user_3)
        self.app.set_user(user_3)

        # user opens timerboard
        timerboard = self.app.get(reverse("structuretimers:timer_list"))
        self.assertEqual(timerboard.status_code, 200)

        # user clicks on "Edit Timer" for timer 1
        edit_timer = self.app.get(
            reverse("structuretimers:edit", args=[self.timer_1.pk])
        )
        self.assertEqual(edit_timer.status_code, 200)

        # user enters data and clicks create
        form = edit_timer.forms["add-timer-form"]
        form["owner_name"] = "The Boys"
        response = form.submit()
        self.timer_1.refresh_from_db()

        # assert results
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("structuretimers:timer_list"))
        self.assertEqual(self.timer_1.owner_name, "The Boys")

    @skipIf(_is_aa4, "test is not compatible with AA4")
    def test_manager_tries_to_edit_corp_restricted_timer_of_others(self):
        """
        given a user has permission to create and manage timers
        when trying to access page for timer edit of a corp restricted timer
        from another corp
        then he the form is not shown
        """
        self.timer_3.visibility = Timer.Visibility.CORPORATION
        self.timer_3.save()

        # login
        user_3 = create_user(self.character_3)
        user_3 = add_permission_to_user_by_name("structuretimers.create_timer", user_3)
        user_3 = add_permission_to_user_by_name("structuretimers.manage_timer", user_3)
        self.app.set_user(user_3)

        # user tries to access page for edit directly
        response = self.app.get(reverse("structuretimers:edit", args=[self.timer_3.pk]))
        self.assertNotIn(
            "add-timer-form", response.forms
        )  # TODO: Change to test for HTTP error code, once available

    @skipIf(_is_aa4, "test is not compatible with AA4")
    def test_manager_tries_to_edit_opsec_timer_of_others(self):
        """
        given a user has permission to create and manage timers
        when trying to access page for timer edit of a opsec timer
        then the form is not shown
        """
        self.timer_3.is_opsec = True
        self.timer_3.save()

        # login
        user_3 = create_user(self.character_3)
        user_3 = add_permission_to_user_by_name("structuretimers.create_timer", user_3)
        user_3 = add_permission_to_user_by_name("structuretimers.manage_timer", user_3)
        self.app.set_user(user_3)

        # user tries to access page for edit directly
        response = self.app.get(reverse("structuretimers:edit", args=[self.timer_3.pk]))
        self.assertNotIn(
            "add-timer-form", response.forms
        )  # TODO: Change to test for HTTP error code, once available

    def test_delete_existing_timer_by_manager(self):
        """
        when user has manager permissions
        then he can delete an existing timer
        """

        # login
        user_3 = create_user(self.character_3)
        user_3 = add_permission_to_user_by_name("structuretimers.manage_timer", user_3)
        self.app.set_user(user_3)

        # user opens timerboard
        timerboard = self.app.get(reverse("structuretimers:timer_list"))
        self.assertEqual(timerboard.status_code, 200)

        # user clicks on "Delete Timer" for timer 2
        confirm_page = self.app.get(
            reverse("structuretimers:delete", args=[self.timer_2.pk])
        )
        self.assertEqual(confirm_page.status_code, 200)

        # user enters data and clicks create
        form = confirm_page.forms["confirm-delete-form"]
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("structuretimers:timer_list"))
        self.assertFalse(Timer.objects.filter(pk=self.timer_2.pk).exists())

    def test_delete_own_timer(self):
        """
        given a user has created a timer
        when trying to delete that time
        then timer is deleted
        """

        # login
        self.app.set_user(self.user_create)

        # user opens timerboard
        timerboard = self.app.get(reverse("structuretimers:timer_list"))
        self.assertEqual(timerboard.status_code, 200)

        # user clicks on "Delete Timer" for timer 2
        confirm_page = self.app.get(
            reverse("structuretimers:delete", args=[self.timer_2.pk])
        )
        self.assertEqual(confirm_page.status_code, 200)

        # user enters data and clicks create
        form = confirm_page.forms["confirm-delete-form"]
        response = form.submit()

        # assert results
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("structuretimers:timer_list"))
        self.assertFalse(Timer.objects.filter(pk=self.timer_2.pk).exists())

    @skipIf(_is_aa4, "test is not compatible with AA4")
    def test_delete_timer_without_permission(self):
        """
        given a user does not have manager permissions
        when trying to access page to delete timer of another user
        then the form is not shown
        """

        # login
        user_3 = create_user(self.character_3)
        user_3 = add_permission_to_user_by_name("structuretimers.create_timer", user_3)
        self.app.set_user(user_3)

        # user tries to access page for edit directly
        response = self.app.get(
            reverse("structuretimers:delete", args=[self.timer_2.pk])
        )
        self.assertNotIn(
            "add-timer-form", response.forms
        )  # TODO: Change to test for HTTP error code, once available


"""
@patch(MODELS_PATH+ ".sleep", new=lambda x: x)
@patch(MODELS_PATH+ ".dhooks_lite.Webhook.execute")
class TestSendNotifications(LoadTestDataMixin, TestCase):
    def setUp(self) -> None:
        self.webhook = create_discord_webhook(
            name="Dummy", url="http://www.example.com"
        )
        self.rule = NotificationRule.objects.create(minutes=NotificationRule.MINUTES_0)
        self.rule.webhooks.add(self.webhook)

    def test_normal(self, mock_execute):
        create_timer(
            structure_name="Test_1",
            eve_solar_system=self.system_abune,
            structure_type=self.type_raitaru,
            date=now() + timedelta(seconds=2),
        )
        sleep(3)
        self.assertEqual(mock_execute.call_count, 1)
"""


@override_settings(CELERY_ALWAYS_EAGER=True)
@patch(MODELS_PATH + ".sleep", new=lambda x: x)
@patch(TASKS_PATH + ".notify", spec=True)
@patch(MODELS_PATH + ".dhooks_lite.Webhook.execute", spec=True)
class TestTestMessageToWebhook(LoadTestDataMixin, TestCase):
    def setUp(self) -> None:
        self.webhook = create_discord_webhook()
        self.user = create_user(self.character_1)

    def test_without_user(self, mock_execute, mock_notify):
        send_test_message_to_webhook.delay(webhook_pk=self.webhook.pk)
        self.assertEqual(mock_execute.call_count, 1)
        self.assertFalse(mock_notify.called)

    def test_with_user(self, mock_execute, mock_notify):
        send_test_message_to_webhook.delay(
            webhook_pk=self.webhook.pk, user_pk=self.user.pk
        )
        self.assertEqual(mock_execute.call_count, 1)
        self.assertTrue(mock_notify.called)


@override_settings(CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
@patch(MODELS_PATH + "._task_calc_timer_distances_for_all_staging_systems", Mock())
class TestTimerSave(LoadTestDataMixin, TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.webhook = create_discord_webhook()

    def test_schedule_notifications_for_new_timers_2(self):
        # when
        create_notification_rule()
        timer = create_timer(
            date=now() + timedelta(hours=4),
            eve_solar_system=self.system_abune,
            structure_type=self.type_astrahus,
            enabled_notifications=True,
        )
        # then
        self.assertTrue(ScheduledNotification.objects.filter(timer=timer).exists())
