from django.contrib.auth.password_validation import validate_password
from django.db.models import Q
from django.http import request
from rest_framework import serializers

from API.models import Users, Projects, Contributors, Issues, Comments
from rest_framework.validators import UniqueValidator


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


class UsersSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contributors
        fields = ['id', 'contributors_user_id',  'contributors_project_id', 'permission', 'role']
        read_only_fields = ('contributors_project_id', 'permission')


class CommentsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ['id',
                  'description',
                  'comments_author_user_id',
                  'comments_issue_id',
                  'created_time'
                  ]
        read_only_fields = ('id', 'comments_author_user_id', 'comments_issue_id', 'created_time')


class CommentsDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ['id',
                  'description',
                  'comments_author_user_id',
                  'comments_issue_id',
                  'created_time'
                  ]

        read_only_fields = ('id', 'description', 'comments_author_user_id', 'comments_issue_id', 'created_time')


class IssuesListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issues
        fields = ['id', 'title', 'description', 'tag', 'priority', 'issue_project_id', 'status', 'issue_author_user_id',
                  'created_time']
        read_only_fields = ('issue_author_user_id', 'created_time', 'issue_project_id', 'issue_assignee_user_id')
        extra_kwargs = {
            'tag' : {'write_only': True},
            'priority': {'write_only': True},
        }


class IssuesDetailSerializer(serializers.ModelSerializer):

    comments_issue_id = serializers.SerializerMethodField()

    class Meta:
        model = Issues
        fields = ['id', 'title', 'description', 'tag', 'priority', 'issue_project_id', 'status', 'issue_author_user_id',
                  'issue_assignee_user_id', 'created_time', 'comments_issue_id']
        read_only_fields = ('issue_author_user_id', 'created_time', 'issue_project_id', 'issue_assignee_user_id')

    def get_comments_issue_id(self, instance):
        queryset = instance.comments_issue_id
        serializer = CommentsListSerializer(queryset, many=True)
        return serializer.data

class ProjectsListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Projects
        fields = ['id',
                  'title',
                  'project_type',
                  'project_author_user_id',
                  'description'
                ]
        read_only_fields = ('project_author_user_id',)
        extra_kwargs = {
            'description': {'write_only': True}
        }

    def validate_name(self, value):
        if Projects.objects.filter(title=value).exists():
            raise serializers.ValidationError('Project title already exists')
        return value


class ProjectsDetailSerializer(serializers.ModelSerializer):

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
