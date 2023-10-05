from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.http import request
from rest_framework import serializers

from API.models import Users, Projects, Contributors, Issues, Comments
from rest_framework.fields import ChoiceField
from rest_framework.validators import UniqueValidator


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class SignupSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Users.objects.all())]
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Users
        fields = ('email', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Les mots de passes ne sont pas identiques"})
        return attrs

    def create(self, validated_data):
        user = Users.objects.create(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserModelSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = Users
        fields = ['id', 'first_name', 'last_name']
        read_only_fields = ('first_name', 'last_name')


class UsersSerializer(DynamicFieldsModelSerializer):

    contributors_user = serializers.SerializerMethodField(read_only=True)
    permission = serializers.CharField(source='get_permission_display', read_only=True)
    role_long = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = Contributors
        fields = ['id', 'contributors_user_id', 'contributors_user', 'contributors_project_id', 'permission',
                  'role', 'role_long']
        read_only_fields = ('contributors_project_id', 'permission', 'role_long', 'contributors_user')
        extra_kwargs = {
            'role': {'write_only': True},
            'contributors_user_id': {'write_only': True}
        }

    def get_contributors_user(self, instance):
        queryset = instance.contributors_user_id
        serializer = UserModelSerializer(queryset, many=False)
        return serializer.data

    def validate_role(self, value):
        choice_possible = ['AU', 'CT']
        if value not in choice_possible:
            raise serializers.ValidationError('Veuillez entrez un role prédeterminé : "AU" pour Auteur, "CT" pour '
                                              'contributeur')
        return value


class CommentsListSerializer(DynamicFieldsModelSerializer):

    comments_author_user = serializers.SerializerMethodField()
    class Meta:
        model = Comments
        fields = ['id',
                  'description',
                  'comments_author_user',
                  'comments_author_user_id',
                  'comments_issue_id',
                  'created_time'
                  ]
        read_only_fields = ('id', 'comments_author_user', 'comments_author_user_id', 'comments_issue_id', 'created_time')

    def get_comments_author_user(self, instance):
        queryset = instance.comments_author_user_id
        serializer = UserModelSerializer(queryset, many=False)
        return serializer.data


class CommentsDetailSerializer(DynamicFieldsModelSerializer):

    comments_author_user_id = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = ['id',
                  'description',
                  'comments_author_user_id',
                  'comments_issue_id',
                  'created_time'
                  ]

        read_only_fields = ('id', 'description', 'comments_author_user_id', 'comments_issue_id', 'created_time')

    def get_comments_author_user_id(self, instance):
        queryset = instance.comments_author_user_id
        serializer = UserModelSerializer(queryset, many=False)
        return serializer.data


class IssuesListSerializer(DynamicFieldsModelSerializer):

    issue_author_user = serializers.SerializerMethodField()
    issue_assignee_user = serializers.SerializerMethodField()
    tag_long = serializers.CharField(source='get_tag_display', read_only=True)
    priority_long = serializers.CharField(source='get_priority_display', read_only=True)
    status_long = serializers.CharField(source='get_status_display', read_only=True)


    class Meta:
        model = Issues
        fields = ['id', 'title', 'description', 'tag', 'tag_long', 'priority', 'priority_long',
                  'issue_project_id', 'status', 'status_long', 'issue_author_user_id',
                  'issue_author_user', 'issue_assignee_user_id', 'issue_assignee_user',
                  'created_time']
        read_only_fields = ('issue_author_user_id', 'created_time', 'issue_project_id',
                            'issue_assignee_user_id', 'tag_long', 'priority_long', 'status display')
        extra_kwargs = {
            'tag' : {'write_only': True},
            'priority': {'write_only': True},
            'status': {'write_only': True},
            'issue_author_user': {'write_only': True},
            'issue_assignee_user': {'write_only': True}
        }

    def get_issue_author_user(self, instance):
        queryset = instance.issue_author_user_id
        serializer = UserModelSerializer(queryset, many=False)
        return serializer.data

    def get_issue_assignee_user(self, instance):
        queryset = instance.issue_assignee_user_id
        serializer = UserModelSerializer(queryset, many=False)
        return serializer.data


class IssuesDetailSerializer(DynamicFieldsModelSerializer):

    comments_issue = serializers.SerializerMethodField()
    issue_author_user = serializers.SerializerMethodField()
    issue_assignee_user = serializers.SerializerMethodField()
    tag_long = serializers.CharField(source='get_tag_display', read_only=True)
    priority_long = serializers.CharField(source='get_priority_display', read_only=True)
    status_long = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Issues
        fields = ['id', 'title', 'description', 'tag', 'tag_long', 'priority', 'priority_long', 'issue_project_id',
                  'status', 'status_long', 'issue_author_user_id', 'issue_assignee_user_id', 'issue_assignee_user',
                  'created_time', 'comments_issue_id', 'issue_author_user', 'comments_issue']
        read_only_fields = ('issue_author_user', 'created_time', 'issue_project_id', 'issue_assignee_user', 'tag_long',
                            'priority_long', 'status_long')
        extra_kwargs = {
            'issue_author_user_id': {'write_only': True},
            'comments_issue_id': {'write_only': True},
            'issue_assignee_user_id': {'write_only': True},
            'tag': {'write_only': True},
            'priority': {'write_only': True},
            'status': {'write_only': True}
        }

    def get_comments_issue_id(self, instance):
        queryset = instance.comments_issue_id
        serializer = CommentsListSerializer(queryset, many=True, fields=('id', 'description', 'comments_author_user_id',
                                                                         'created_time'))
        return serializer.data

    def get_issue_author_user_id(self, instance):
        queryset = instance.issue_author_user_id
        serializer = UserModelSerializer(queryset, many=False)
        return serializer.data

    def get_issue_assignee_user_id(self, instance):
        queryset = instance.issue_assignee_user_id
        serializer = UserModelSerializer(queryset, many=False)
        return serializer.data


class ProjectsListSerializer(DynamicFieldsModelSerializer):

    project_type_long = serializers.CharField(source='get_project_type_display', read_only=True)
    project_author_user = serializers.SerializerMethodField()


    class Meta:
        model = Projects
        fields = ['id',
                  'title',
                  'project_type',
                  'project_type_long',
                  'project_author_user_id',
                  'project_author_user',
                  'description'
                ]
        read_only_fields = ('project_author_user', 'project_author_user_id', 'project_type_long')
        extra_kwargs = {
            'description': {'write_only': True},
            'project_type': {'write_only': True}
        }

    def validate_title(self, value):
        if Projects.objects.filter(title=value).exists():
            raise serializers.ValidationError('Ce nom de projet existe déjà')
        return value

    def get_project_author_user(self, instance):
        queryset = instance.project_author_user_id
        serializer = UserModelSerializer(queryset, many=False)
        return serializer.data


class ProjectsDetailSerializer(DynamicFieldsModelSerializer):

    issue_project_id = serializers.SerializerMethodField()
    contributors_project_id = serializers.SerializerMethodField()
    project_author_user_id = serializers.SerializerMethodField()
    project_type = serializers.CharField(source='get_project_type_display')

    class Meta:
        model = Projects
        fields = ['id',
                  'title',
                  'project_type',
                  'project_author_user_id',
                  'description',
                  'contributors_project_id',
                  'issue_project_id'
                  ]

    def get_contributors_project_id(self, instance):
        queryset = instance.contributors_project_id
        serializer = UsersSerializer(queryset, many=True, fields=('id', 'contributors_user_id', 'role'))
        return serializer.data

    def get_issue_project_id(self, instance):
        queryset = instance.issue_project_id
        serializer = IssuesListSerializer(queryset, many=True, fields=('id', 'title','tag', 'priority', 'status',
                                                                       'issue_author_user_id','created_time'))
        return serializer.data

    def get_project_author_user_id(self, instance):
        queryset = instance.project_author_user_id
        serializer = UserModelSerializer(queryset, many=False)
        return serializer.data
