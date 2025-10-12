import os

from django.conf import settings
from django.contrib.auth.models import User
from django.test import override_settings
from django.test.selenium import SeleniumTestCase, SeleniumTestCaseBase
from django.urls import reverse

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from aleksis.core.models import Person

pytestmark = pytest.mark.django_db

SeleniumTestCaseBase.external_host = os.environ.get("TEST_HOST", "") or None
SeleniumTestCaseBase.browsers = list(
    filter(bool, os.environ.get("TEST_SELENIUM_BROWSERS", "").split(","))
)
SeleniumTestCaseBase.selenium_hub = os.environ.get("TEST_SELENIUM_HUB", "") or None


@pytest.mark.usefixtures("celery_worker")
@override_settings(CELERY_BROKER_URL="memory://localhost//")
class SeleniumTests(SeleniumTestCase):
    serialized_rollback = True

    @classmethod
    def _screenshot(cls, filename):
        screenshot_path = os.environ.get("TEST_SCREENSHOT_PATH", None)
        if screenshot_path:
            os.makedirs(os.path.join(screenshot_path, cls.browser), exist_ok=True)
            return cls.selenium.save_screenshot(
                os.path.join(screenshot_path, cls.browser, filename)
            )
        else:
            return False

    def _login(self, username="admin", password="admin", with_screenshots=False):
        # Navigate to configured login page
        self.selenium.get(self.live_server_url + reverse(settings.LOGIN_URL))
        if with_screenshots:
            self._screenshot("login_default_superuser_blank.png")

        # Find login form input fields and enter defined credentials
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//label[contains(text(), "Login")]/../input'),
            )
        ).send_keys(username)
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//label[contains(text(), "Password")]/../input'),
            )
        ).send_keys(password)
        if with_screenshots:
            self._screenshot("login_default_superuser_filled.png")

        # Submit form by clicking django-two-factor-auth's Next button
        WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[contains(text(), "Login")]'),
            )
        ).click()
        if with_screenshots:
            self._screenshot("login_default_superuser_submitted.png")

    def _create_person(self, username="admin"):
        user = User.objects.get(username=username)
        person = Person.objects.create(user=user, first_name="Jane", last_name="Doe")
        return person

    @pytest.mark.skip(reason="broken")
    def test_index(self):
        self.selenium.get(self.live_server_url + "/")
        assert "AlekSIS" in self.selenium.title
        self._screenshot("index.png")

    def test_login_default_superuser(self):
        self._login("admin", "admin", with_screenshots=True)

        # Should redirect away from login page and not put up an alert about wrong credentials
        assert "Please enter a correct username and password." not in self.selenium.page_source

    # Deactivated for now as Selenium test infrastructure needs a complete rethinking
    # because of the new Vue frontend
    # def test_pdf_generation(self):
    #     self._login()
    #     self._create_person()
    #     self.selenium.get(self.live_server_url + reverse("test_pdf"))
    #     el = WebDriverWait(self.selenium, 20).until(lambda d: ".pdf" in self.selenium.current_url)
    #     self._screenshot("pdf.png")
