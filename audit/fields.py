from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet


class EncryptedTextField(models.TextField):
    """TextField that encrypts values at rest using Fernet."""

    def __init__(self, *args, classification=None, **kwargs):
        self.classification = classification
        super().__init__(*args, **kwargs)

    def _fernet(self):
        key = settings.FIELD_ENCRYPTION_KEY
        if isinstance(key, str):
            key = key.encode()
        return Fernet(key)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return value
        f = self._fernet()
        return f.encrypt(value.encode()).decode()

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        f = self._fernet()
        try:
            return f.decrypt(value.encode()).decode()
        except Exception:
            return value

    def to_python(self, value):
        if value is None or isinstance(value, str):
            return value
        f = self._fernet()
        try:
            return f.decrypt(value.encode()).decode()
        except Exception:
            return value
