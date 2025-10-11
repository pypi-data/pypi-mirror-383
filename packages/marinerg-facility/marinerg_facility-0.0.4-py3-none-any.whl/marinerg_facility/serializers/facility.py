from rest_framework import serializers
from django_countries.serializers import CountryFieldMixin

from marinerg_facility.models import Facility


class FacilitySerializer(CountryFieldMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Facility
        fields = [
            "name",
            "acronym",
            "description",
            "address",
            "website",
            "id",
            "url",
            "is_active",
            "is_partner",
            "members",
            "image_url",
        ]
        read_only_fields = ["image_url"]
