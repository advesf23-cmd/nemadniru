import tempfile
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.contact.models import JobApplication, JobPosition, QuoteRequest


class PrivateFileDownloadAccessTests(TestCase):
    def setUp(self):
        self.temp_media = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_media.cleanup)
        self.settings_override = override_settings(
            MEDIA_ROOT=str(Path(self.temp_media.name) / "media"),
            PRIVATE_MEDIA_ROOT=str(Path(self.temp_media.name) / "private"),
        )
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)

        self.user_model = get_user_model()
        self.staff_user = self.user_model.objects.create_user(
            username="security-test-staff",
            password="test-only-password-123",
            role=self.user_model.ROLE_ADMIN,
            is_staff=True,
        )
        self.position = JobPosition.objects.create(
            title="Test position",
            description="Test description",
        )
        self.application = JobApplication.objects.create(
            position=self.position,
            full_name="Test Applicant",
            email="applicant@example.com",
            phone="09120000000",
            resume=SimpleUploadedFile(
                "resume.pdf",
                b"%PDF-1.4\nprivate resume test",
                content_type="application/pdf",
            ),
        )
        self.quote = QuoteRequest.objects.create(
            full_name="Test Customer",
            phone="09121111111",
            description="Test quote request",
            attachment=SimpleUploadedFile(
                "quote.pdf",
                b"%PDF-1.4\nprivate quote test",
                content_type="application/pdf",
            ),
        )

    def test_anonymous_user_cannot_download_quote_attachment(self):
        url = reverse("dashboard:quote_attachment_download", kwargs={"pk": self.quote.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_anonymous_user_cannot_download_resume(self):
        url = reverse("dashboard:application_resume_download", kwargs={"pk": self.application.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_staff_user_can_download_quote_attachment(self):
        self.client.force_login(self.staff_user)
        url = reverse("dashboard:quote_attachment_download", kwargs={"pk": self.quote.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertEqual(b"".join(response.streaming_content), b"%PDF-1.4\nprivate quote test")

    def test_staff_user_can_download_resume(self):
        self.client.force_login(self.staff_user)
        url = reverse("dashboard:application_resume_download", kwargs={"pk": self.application.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Cache-Control"], "private, no-store")
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertEqual(b"".join(response.streaming_content), b"%PDF-1.4\nprivate resume test")

    def test_staff_user_gets_404_when_quote_attachment_file_is_missing(self):
        self.client.force_login(self.staff_user)
        Path(self.quote.attachment.path).unlink()
        url = reverse("dashboard:quote_attachment_download", kwargs={"pk": self.quote.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_staff_user_gets_404_when_resume_file_is_missing(self):
        self.client.force_login(self.staff_user)
        Path(self.application.resume.path).unlink()
        url = reverse("dashboard:application_resume_download", kwargs={"pk": self.application.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
