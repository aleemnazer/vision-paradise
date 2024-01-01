import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
    Base model that includes uuid and default created / updated timestamps.
    """
    standard_fields = ["id", "display_id", "created_at", "updated_at"]

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_("created at")
    )
    updated_at = models.DateTimeField(
        auto_now=True, db_index=True, verbose_name=_("updated at")
    )

    id = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4, verbose_name=_("id")
    )

    display_id = models.CharField(
        max_length=6, editable=False, default="------", verbose_name=_("display id")
    )

    def save(self, *args, **kwargs):
        if self.id is None:
            self.id = uuid.uuid4().hex
        self.display_id = str(self.id)[:6].upper()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return self.display_id

