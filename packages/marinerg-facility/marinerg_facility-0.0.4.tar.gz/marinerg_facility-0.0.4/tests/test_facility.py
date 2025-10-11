import tempfile
import json

from rest_framework import status
from django.contrib.auth.models import User

from ichec_django_core.models import Address
from marinerg_facility.models import Facility

from ichec_django_core.utils.test_utils import (
    AuthAPITestCase,
    setup_default_users_and_groups,
    add_group_permissions,
    generate_image,
)


class TestFacilityViewTests(AuthAPITestCase):
    def setUp(self):
        self.url = "/api/facilities/"
        setup_default_users_and_groups()

        add_group_permissions(
            "consortium_admins",
            Facility,
            ["change_facility", "add_facility"],
        )

        add_group_permissions(
            "consortium_admins",
            Address,
            ["change_address", "add_address"],
        )

    def test_list_not_authenticated(self):
        self.assert_401(self.do_list())

    def test_detail_not_authenticated(self):
        self.assert_401(self.detail(1))

    def test_list_authenticated(self):
        self.assert_200(self.authenticated_list("regular_user"))

    def test_create_not_authenticated(self):
        data = {"name": "My Facility"}
        self.assert_401(self.create(data))

    def test_create_authenticated_no_permission(self):
        data = {"name": "My Facility"}
        self.assert_403(self.authenticated_create("regular_user", data))

    def create_address(self):
        address = {"line1": "1234 Street", "region": "Region", "country": "IE"}

        user = User.objects.get(username="consortium_admin")
        self.client.force_authenticate(user=user)
        response = self.client.post("/api/addresses/", address, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.force_authenticate(user=None)
        return response.data["url"]

    def test_create_authenticated_permission(self):
        address = self.create_address()
        data = {
            "name": "My Facility",
            "address": address,
            "members": [],
        }
        self.assert_201(self.authenticated_create("consortium_admin", data))

    def test_create_with_image_authenticated_permission(self):
        image = generate_image()
        tmp_file = tempfile.NamedTemporaryFile(suffix=".png")
        image.save(tmp_file, format="PNG")

        tmp_file.seek(0)

        address = self.create_address()

        data = {
            "name": "My Facility",
            "address": address,
            "members": [],
        }

        response = self.authenticated_create("consortium_admin", data)
        self.assert_201(response)

        resource_id = json.loads(response.content)["id"]
        self.assert_204(
            self.authenticated_put_file(
                "consortium_admin",
                resource_id,
                "image",
                {"file": tmp_file},
                "test_image.png",
            )
        )
