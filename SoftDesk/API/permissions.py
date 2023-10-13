from rest_framework import permissions
from rest_framework.permissions import BasePermission
from API.models import Contributors


class ProjectPermissions(BasePermission):

    """ Permission used to manage the project """
    def has_object_permission(self, request, view, obj):
        contrib = []
        contributorspermissions = Contributors.objects.filter(contributors_project_id=obj)
        for contributorperm in contributorspermissions:
            contrib.append(contributorperm.contributors_user_id)
        ownerpermissions = Contributors.objects.filter(contributors_project_id=obj).filter(permission='C')
        for ownerpermission in ownerpermissions:
            owner = ownerpermission.contributors_user_id
        if request.method in permissions.SAFE_METHODS and request.user in contrib:
            return True
        if request.method not in permissions.SAFE_METHODS and request.user == owner:
            return True
