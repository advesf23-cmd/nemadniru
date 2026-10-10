from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateMediaStorage(FileSystemStorage):
    """Store sensitive uploads outside MEDIA_ROOT.

    Existing files are read from MEDIA_ROOT as a compatibility fallback until
    they can be copied into PRIVATE_MEDIA_ROOT. New writes always use the
    private location. The fallback is deliberately read-only.
    """

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

    def exists(self, name):
        if super().exists(name):
            return True
        legacy_path = Path(settings.MEDIA_ROOT) / name
        return legacy_path.is_file()

    def _open(self, name, mode="rb"):
        try:
            return super()._open(name, mode)
        except FileNotFoundError:
            # Legacy files remain readable during migration, but are never
            # written to the public media directory.
            if mode != "rb":
                raise
            legacy_path = Path(settings.MEDIA_ROOT) / name
            if not legacy_path.is_file():
                raise
            return File(legacy_path.open(mode), name=name)
