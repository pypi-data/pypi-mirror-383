from django.contrib.auth.models import Group, Permission
from rest_framework import serializers
from django_countries.serializers import CountryFieldMixin

from ichec_django_core.models import PortalMember, Organization, Address


class PortalMemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PortalMember
        fields = [
            "url",
            "username",
            "email",
            "first_name",
            "last_name",
            "id",
            "phone",
            "organizations",
            "is_facility_member",
            "profile_url",
        ]
        read_only_fields = ["is_facility_member", "profile_url"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name", "id"]


class PermissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Permission
        fields = ["url", "id", "codename"]


class OrganizationSerializer(CountryFieldMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
        fields = ["name", "acronym", "description", "address", "website", "id", "url"]


class AddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Address
        fields = [
            "line1",
            "line2",
            "line3",
            "city",
            "region",
            "postcode",
            "country",
            "id",
            "url",
        ]
