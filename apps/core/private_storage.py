from pathlib import Path

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateMediaStorage(FileSystemStorage):
    """Store sensitive uploads outside MEDIA_ROOT with no public URL."""

    def __init__(self, *args, **kwargs):
        # Resolve PRIVATE_MEDIA_ROOT lazily so settings overrides in tests and
        # deployments are respected; explicit locations remain useful in tests.
        kwargs.setdefault("location", None)
        kwargs.setdefault("base_url", None)
        super().__init__(*args, **kwargs)

    @property
    def location(self):
        configured_location = self._location or settings.PRIVATE_MEDIA_ROOT
        return str(Path(configured_location).resolve())

    def url(self, name):
        # Sensitive files must only be served through staff-authorized views.
        return ""
