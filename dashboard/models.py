from django.db import models
from django.contrib.auth.models import User

class TranslatedDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Optional for now
    original_file = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True)

class Section(models.Model):
    document = models.ForeignKey(TranslatedDocument, on_delete=models.CASCADE, related_name='sections')
    original_json = models.JSONField(blank=True, null=True)      # <-- Add this
    translated_json = models.JSONField(blank=True, null=True)