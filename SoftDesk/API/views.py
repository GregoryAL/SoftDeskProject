import django.db.utils
from django.core.exceptions import PermissionDenied
from django.db.models import Q
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
    UsersSerializer, IssuesListSerializer, IssuesDetailSerializer, CommentsListSerializer, CommentsDetailSerializer

from API.models import Projects, Users, Contributors, Issues, Comments

from API.permissions import ProjectPermissions


class MultipleSerializerMixin:

    """ View used to manage the detail view if an id is provided """

    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()

    def get_token_info(token_str):

        """ View used to get tokens after successful login """

        access_token_obj = AccessToken(token_str)
        user_id = access_token_obj['user_id']
        user = Users.objects.get(id=user_id)
        return Response(user)


class SignupView(generics.CreateAPIView):

    """ view used to sign up """

    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer


class ProjectsViewset(MultipleSerializerMixin, ModelViewSet):

    """ view used to manage projects """

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
        Contributors.objects.create(
            contributors_user_id=self.request.user,
            contributors_project_id=project,
            permission='CP',
            role='AU'
        )


class ProjectContributorsViewset(ModelViewSet):

    """ view used to manage contributors """

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
            project_query = self.queryset.filter(contributors_project_id=project)
            for project_object in project_query:
                proj_obj_permission = project_object.permission
            return proj_obj_permission
        else:
            raise PermissionDenied()

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_pk")
        project = Projects.objects.get(id=project_id)

        project_owner_req = Contributors.objects.filter(
            Q(contributors_project_id=project),
            Q(permission='CP'))
        for project_owner_r in project_owner_req:
            project_owner = project_owner_r.contributors_user_id
        if self.request.user == project_owner:
            try:
                serializer.save(contributors_project_id=project, permission='LI')
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

    """ View used to manage Project issues """

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
        issue_id = self.kwargs.get('pk')
        queryset = Issues.objects.all().filter(issue_project_id=project)
        for project_contributor in project_contributors_req:
            project_contributors.append(project_contributor.contributors_user_id)
        if self.request.user in project_contributors:
            if issue_id:
                queryset = queryset.filter(id=issue_id)
            return queryset
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
            try:
                serializer.save(issue_project_id=project, issue_author_user_id=self.request.user,
                                issue_assignee_user_id=self.request.user)
            except django.db.utils.IntegrityError:
                raise Exception("Ce problème a deja été ajouté au projet")
        else:
            raise PermissionDenied()

    def perform_destroy(self, serializer):
        issue_id = self.kwargs.get("pk")
        issue = get_object_or_404(Issues, id=issue_id)
        assignated_user_id = issue.issue_assignee_user_id.pk
        issue_creator = get_object_or_404(Users, id=assignated_user_id)
        if self.request.user == issue_creator:
            issue.delete()
        else:
            raise PermissionDenied()

    def perform_update(self, serializer):
        issue_id = self.kwargs.get("pk")
        issue = get_object_or_404(Issues, id=issue_id)
        assignated_user_id = issue.issue_assignee_user_id.pk
        issue_creator = get_object_or_404(Users, id=assignated_user_id)
        if self.request.user == issue_creator:
            serializer.save()
        else:
            raise PermissionDenied()


class IssueCommentsViewer(MultipleSerializerMixin, ModelViewSet):

    """ View used to manage Comment's issues """

    permission_classes = [IsAuthenticated, ]
    serializer_class = CommentsListSerializer
    detail_serializer_class = CommentsDetailSerializer

    queryset = Comments.objects.all().select_related(
        'comments_issue_id'
    )

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("project_pk")
        project_contributors = []
        project_contributors_req = Contributors.objects.filter(contributors_project_id=project_id)
        issue_id = self.kwargs.get('issues_pk')
        issue = Issues.objects.get(id=issue_id)
        comment_id = self.kwargs.get('pk')
        queryset = Comments.objects.all().filter(comments_issue_id=issue)

        for project_contributor in project_contributors_req:
            project_contributors.append(project_contributor.contributors_user_id)
        if self.request.user in project_contributors:
            if comment_id:
                queryset = queryset.filter(id=comment_id)
            return queryset
        else:
            raise PermissionDenied()

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_pk")
        project = Projects.objects.get(id=project_id)
        project_contributors = []
        project_contributors_req = Contributors.objects.filter(contributors_project_id=project)
        for project_contributor in project_contributors_req:
            project_contributors.append(project_contributor.contributors_user_id)
        issue_id = self.kwargs.get('issues_pk')
        issue = Issues.objects.get(id=issue_id)
        if self.request.user in project_contributors:
            try:
                serializer.save(comments_issue_id=issue, comments_author_user_id=self.request.user)
            except:
                raise Exception("Ce commentaire n'a pas pu être ajouté.")
        else:
            raise PermissionDenied()

    def perform_destroy(self, serializer):
        comment_id = self.kwargs.get("pk")
        comment = get_object_or_404(Comments, id=comment_id)
        comment_user_id = comment.comments_author_user_id.pk
        comment_creator = get_object_or_404(Users, id=comment_user_id)
        if self.request.user == comment_creator:
            comment.delete()
        else:
            raise PermissionDenied()

    def perform_update(self, serializer):
        comment_id = self.kwargs.get("pk")
        comment = get_object_or_404(Comments, id=comment_id)
        comment_user_id = comment.comments_author_user_id.pk
        comment_creator = get_object_or_404(Users, id=comment_user_id)
        if self.request.user == comment_creator:
            serializer.save()
        else:
            raise PermissionDenied()
