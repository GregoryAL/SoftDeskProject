from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from API.models import Contributors, Projects


class ProjectPermissions(BasePermission):


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


#class ContributorsPermissions(BasePermission):

    #def has_permission(self, request, view):


    #def has_object_permission(self, request, view, obj):
        #project = self.contributors_project_id
        #projectContributors = []
        #projectContributorsPermissions = Contributors.objects.filter(contributors_project_id=project)
        #for projectContributorPermission in projectContributorsPermissions:
            #projectContributors.append(projectContributorPermission.contributors_user_id)
        #projectOwnerPermission = Contributors.objects.filter(contributors_project_id=project).filter(permission='C')
        #for projectOwnerPerm in projectOwnerPermission:
            #projectOwner = projectOwnerPerm.contributors_user_id
        #if request.method in permissions.SAFE_METHODS and request.user in projectContributors:
            #return True
        #if request.method not in permissions.SAFE_METHODS and request.user == projectOwner:
            #return True

