from django.test import TestCase
from django.urls import reverse


class PrivateFileDownloadAccessTests(TestCase):
    def test_anonymous_user_cannot_download_quote_attachment(self):
        url = reverse("dashboard:quote_attachment_download", kwargs={"pk": 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_cannot_download_resume(self):
        url = reverse("dashboard:application_resume_download", kwargs={"pk": 1})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
