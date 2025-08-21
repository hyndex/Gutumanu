from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import hashlib

from .fields import EncryptedTextField


class AuditLog(models.Model):
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    method = models.CharField(max_length=10)
    path = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    body = EncryptedTextField(blank=True, default='', classification='PII')
    prev_hash = models.CharField(max_length=64, blank=True)
    hash = models.CharField(max_length=64, blank=True)
    tsa_token = models.BinaryField(null=True, blank=True)

    class Meta:
        ordering = ['timestamp']

    def save(self, *args, **kwargs):
        if self.pk:
            update_fields = kwargs.get('update_fields')
            if not update_fields or set(update_fields) != {'tsa_token'}:
                raise ValueError("AuditLog entries are immutable")
            return super().save(*args, **kwargs)
        if not self.prev_hash:
            last = AuditLog.objects.order_by('-timestamp').first()
            self.prev_hash = last.hash if last else ''
        data = f"{self.prev_hash}{self.user_id}{self.method}{self.path}{self.timestamp}{self.body}".encode('utf-8')
        self.hash = hashlib.sha256(data).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.timestamp} {self.method} {self.path}"
