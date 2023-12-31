# Generated by Django 4.2.2 on 2023-09-01 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("API", "0005_alter_contributors_unique_together"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contributors",
            name="permission",
            field=models.CharField(
                choices=[("CP", "Complete"), ("LI", "Limitée")], max_length=2
            ),
        ),
        migrations.AlterField(
            model_name="contributors",
            name="role",
            field=models.CharField(
                choices=[("AU", "Auteur"), ("CT", "Contributeur")], max_length=2
            ),
        ),
    ]
