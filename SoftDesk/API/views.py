import http

import django.db.utils
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken
from API.serializers import SignupSerializer, \
    ProjectsListSerializer, \
    ProjectsDetailSerializer, \
    UsersSerializer, IssuesListSerializer, IssuesDetailSerializer

from API.models import Projects, Users, Contributors, Issues

from API.permissions import ProjectPermissions


class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


def get_token_info(token_str):
    access_token_obj = AccessToken(token_str)
    user_id = access_token_obj['user_id']
    user = Users.objects.get(id=user_id)
    return Response(user)



class SignupView(generics.CreateAPIView):

    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer


class ProjectsViewset(MultipleSerializerMixin, ModelViewSet):

    serializer_class = ProjectsListSerializer
    detail_serializer_class = ProjectsDetailSerializer
    permission_classes = [IsAuthenticated, ProjectPermissions]

    def get_queryset(self):
        queryset = Projects.objects.all()
        project_id = self.request.GET.get('projects_id')
        if project_id:
            queryset = queryset.filter(projects_id=project_id)
        return queryset

    def perform_create(self, serializer):
        project = serializer.save(project_author_user_id=self.request.user)
        contributor = Contributors.objects.create(
            contributors_user_id=self.request.user,
            contributors_project_id=project,
            permission='C',
            role='A'
        )

    @action(detail=True, methods=['post'])
    def disable(self, request, pk):
        self.get_object().disable()
        return Response()


class ProjectContributorsViewset(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UsersSerializer

    queryset = Contributors.objects.all().select_related(
        'contributors_project_id'
    )


    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("project_pk")
        project_contributors = []
        project_contributors_req = Contributors.objects.filter(contributors_project_id=project_id)
        for project_contributor in project_contributors_req:
            project_contributors.append(project_contributor.contributors_user_id)
        if self.request.user in project_contributors:
            try:
                project = Projects.objects.get(id=project_id)
            except Projects.DoesNotExist:
                raise NotFound("Il n'y a pas de projet avec cet ID")
            return self.queryset.filter(contributors_project_id=project)
        else:
            raise PermissionDenied()

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_pk")
        project = Projects.objects.get(id=project_id)

        project_owner_req = Contributors.objects.filter(
            Q(contributors_project_id=project),
            Q(permission='C'))
        for project_owner_r in project_owner_req:
            project_owner = project_owner_r.contributors_user_id
        project_owner_id = project_owner.pk
        if self.request.user == project_owner:
            try :
                contributor = serializer.save(contributors_project_id=project, permission='L')
            except django.db.utils.IntegrityError:
                raise Exception("Cet utilisateur a deja été ajouté au projet")
        else:
            raise PermissionDenied()

    def perform_destroy(self, serializer):
        project_id = self.kwargs.get("project_pk")
        project = Projects.objects.get(id=project_id)
        contributor_id = self.kwargs.get("pk")
        contributor = get_object_or_404(Contributors, id=contributor_id)

        project_owner_req = Contributors.objects.filter(
            Q(contributors_project_id=project),
            Q(permission='C'))
        for project_owner_r in project_owner_req:
            project_owner = project_owner_r.contributors_user_id
        if self.request.user == project_owner:
            contributor.delete()
        else:
            raise PermissionDenied()


class ProjectIssuesViewer(MultipleSerializerMixin, ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = IssuesListSerializer
    detail_serializer_class = IssuesDetailSerializer

    queryset = Issues.objects.all().select_related(
        'issue_project_id'
    )

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("project_pk")
        project = Projects.objects.get(id=project_id)
        project_contributors = []
        project_contributors_req = Contributors.objects.filter(contributors_project_id=project_id)
        for project_contributor in project_contributors_req:
            project_contributors.append(project_contributor.contributors_user_id)
        if self.request.user in project_contributors:
            try:
                issues = Issues.objects.get(issue_project_id=project_id)
            except Projects.DoesNotExist:
                raise NotFound("Il n'y a pas de projet avec cet ID")
            return self.queryset.filter(issue_project_id=project)
        else:
            raise PermissionDenied()

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_pk")
        project = Projects.objects.get(id=project_id)
        project_contributors = []
        project_contributors_req = Contributors.objects.filter(contributors_project_id=project)
        for project_contributor in project_contributors_req:
            project_contributors.append(project_contributor.contributors_user_id)
        if self.request.user in project_contributors:
            try :
                issue = serializer.save(issue_project_id=project, issue_author_user_id=self.request.user,
                                        issue_assignee_user_id=self.request.user)
            except django.db.utils.IntegrityError:
                raise Exception("Ce problème a deja été ajouté au projet")
        else:
            raise PermissionDenied()
