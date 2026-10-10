# Generated for SEC-013: route sensitive uploads to private storage.
from django.db import migrations, models
import apps.core.private_storage


class Migration(migrations.Migration):

    dependencies = [
        ("contact", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="quoterequest",
            name="attachment",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="quotes/",
                storage=apps.core.private_storage.PrivateMediaStorage(),
                verbose_name="فایل پیوست (نقشه/مشخصات)",
            ),
        ),
        migrations.AlterField(
            model_name="jobapplication",
            name="resume",
            field=models.FileField(
                upload_to="careers/resumes/",
                storage=apps.core.private_storage.PrivateMediaStorage(),
                verbose_name="فایل رزومه",
            ),
        ),
    ]
