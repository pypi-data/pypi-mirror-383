from rest_framework import viewsets, permissions

from ichec_django_core.view_sets import ObjectFileDownloadView, ObjectFileUploadView

from marinerg_facility.models import Facility
from marinerg_facility.serializers import FacilitySerializer


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def get_queryset(self):
        queryset = Facility.objects.all()
        member_id = self.request.query_params.get("user")
        if member_id is not None:
            queryset = queryset.filter(members__id=member_id)
        return queryset


class FacilityImageDownloadView(ObjectFileDownloadView):
    model = Facility
    file_field = "image"


class FacilityImageUploadView(ObjectFileUploadView):
    model = Facility
    queryset = Facility.objects.all()
    file_field = "image"
