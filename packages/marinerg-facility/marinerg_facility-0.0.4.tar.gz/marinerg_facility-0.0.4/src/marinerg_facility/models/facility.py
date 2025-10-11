from django.db import models

from ichec_django_core.models import Organization


class Facility(Organization):

    is_active = models.BooleanField(default=True)
    is_partner = models.BooleanField(default=False)
    image = models.ImageField(blank=True, null=True)

    class Meta:
        verbose_name = "Facility"
        verbose_name_plural = "Facilities"

    @property
    def image_url(self):
        if self.image:
            return "image"
        else:
            return None
