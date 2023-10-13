from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Users(AbstractUser):

    # Model for user

    email = models.EmailField(unique=True)
    username = None
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']
    USERNAME_FIELD = 'email'


class Projects(models.Model):

    # Model for project

    PROJECT_TYPES = (
        ('B', 'Back-end'),
        ('F', 'Front-end'),
        ('A', 'Android'),
        ('I', 'iOS')
    )

    title = models.CharField(max_length=128)
    description = models.CharField(max_length=8192)
    project_type = models.CharField(max_length=1, choices=PROJECT_TYPES)
    project_author_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_author_user_id'
    )


class Contributors(models.Model):

    # Model for contributors (User added to a project)

    COMPLETE = "CP"
    LIMITEE = "LI"
    AUTEUR = "AU"
    CONTRIBUTEUR = "CT"

    PERMISSION_CHOICES = [
        (COMPLETE, 'Complete'),
        (LIMITEE, 'Limitée')
    ]
    ROLE_CHOICES = [
        (AUTEUR, 'Auteur'),
        (CONTRIBUTEUR, 'Contributeur')
    ]

    contributors_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contributors_user_id'
    )
    contributors_project_id = models.ForeignKey(
        to=Projects,
        on_delete=models.CASCADE,
        related_name="contributors_project_id"
    )
    permission = models.CharField(max_length=2, choices=PERMISSION_CHOICES)
    role = models.CharField(max_length=2, choices=ROLE_CHOICES)

    class Meta:
        unique_together = (
            'contributors_user_id',
            'contributors_project_id'
        )


class Issues(models.Model):

    # Model for issues

    TAG_CHOICES = (
        ('B', 'BUG'),
        ('A', 'AMÉLIORATION'),
        ('T', 'TÂCHE')
    )
    PRIORITY_CHOICES = (
        ('F', 'FAIBLE'),
        ('M', 'MOYENNE'),
        ('E', 'ÉLEVÉE')
    )
    STATUS_CHOICES = (
        ('A', 'À faire'),
        ('E', 'En cours'),
        ('T', 'Terminé')
    )

    title = models.CharField(max_length=128)
    description = models.CharField(max_length=8192)
    tag = models.CharField(max_length=1, choices=TAG_CHOICES)
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES)
    issue_project_id = models.ForeignKey(
        to=Projects,
        on_delete=models.CASCADE,
        related_name='issue_project_id'
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    issue_author_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='issue_author_user_id'
    )
    issue_assignee_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='issue_assignee_user_id'
    )
    created_time = models.DateTimeField(auto_now_add=True)


class Comments(models.Model):

    # Model for comments

    description = models.CharField(max_length=8192)
    comments_author_user_id = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments_author_user_id'
    )
    comments_issue_id = models.ForeignKey(
        to=Issues,
        on_delete=models.CASCADE,
        related_name='comments_issue_id'
    )
    created_time = models.DateTimeField(auto_now_add=True)
