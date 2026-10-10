from pathlib import Path
import zipfile

from django import forms

from .models import QuoteRequest, JobApplication


MAX_RESUME_SIZE = 5 * 1024 * 1024
MAX_QUOTE_ATTACHMENT_SIZE = 10 * 1024 * 1024

_DOC_OLE_SIGNATURE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def _validate_upload(upload, *, allowed_extensions, max_size, label):
    if not upload:
        return upload

    extension = Path(upload.name).suffix.lower()
    if extension not in allowed_extensions:
        raise forms.ValidationError(
            f"نوع فایل {label} مجاز نیست. فایل PDF، DOC یا DOCX انتخاب کنید."
        )
    if upload.size > max_size:
        max_mb = max_size // (1024 * 1024)
        raise forms.ValidationError(f"حجم فایل {label} نباید بیشتر از {max_mb} مگابایت باشد.")

    # Check file signatures as well as the user-supplied extension/content type.
    header = upload.read(16)
    upload.seek(0)

    valid = False
    if extension == ".pdf":
        valid = header.startswith(b"%PDF-")
    elif extension == ".doc":
        valid = header.startswith(_DOC_OLE_SIGNATURE)
    elif extension == ".docx":
        try:
            with zipfile.ZipFile(upload) as archive:
                valid = "word/document.xml" in archive.namelist()
        except (zipfile.BadZipFile, OSError):
            valid = False
        finally:
            upload.seek(0)
    elif extension in {".jpg", ".jpeg"}:
        valid = header.startswith(b"\xff\xd8\xff")
    elif extension == ".png":
        valid = header.startswith(b"\x89PNG\r\n\x1a\n")

    if not valid:
        raise forms.ValidationError(
            f"محتوای فایل {label} با پسوند آن مطابقت ندارد یا فایل معتبر نیست."
        )
    return upload


class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = [
            "full_name", "company_name", "phone", "email",
            "project_type", "budget_range", "description", "attachment",
        ]

    def clean_attachment(self):
        return _validate_upload(
            self.cleaned_data.get("attachment"),
            allowed_extensions={".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png"},
            max_size=MAX_QUOTE_ATTACHMENT_SIZE,
            label="پیوست استعلام",
        )


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ["position", "full_name", "email", "phone", "resume", "cover_letter"]

    def clean_resume(self):
        return _validate_upload(
            self.cleaned_data.get("resume"),
            allowed_extensions={".pdf", ".doc", ".docx"},
            max_size=MAX_RESUME_SIZE,
            label="رزومه",
        )
