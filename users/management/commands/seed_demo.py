import json
import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from users.models import User
from projects.models import Project, Skill


FIXTURES_DIR = os.path.join(settings.BASE_DIR, "fixtures")


class Command(BaseCommand):
    help = "Создаёт тестовые данные для демонстрации"

    def handle(self, *args, **options):
        call_command("migrate", "--noinput")

        with open(os.path.join(FIXTURES_DIR, "skills.json"), encoding="utf-8") as f:
            skills_data = json.load(f)
        for name in skills_data:
            Skill.objects.get_or_create(name=name)

        with open(os.path.join(FIXTURES_DIR, "users.json"), encoding="utf-8") as f:
            users_data = json.load(f)

        created_users = {}
        for data in users_data:
            is_superuser = data.pop("is_superuser", False)
            is_staff = data.pop("is_staff", False)

            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "name": data["name"],
                    "surname": data["surname"],
                    "phone": data["phone"],
                    "about": data["about"],
                    "is_superuser": is_superuser,
                    "is_staff": is_staff,
                },
            )
            if created:
                user.set_password(data["password"])
                user.save()
            created_users[data["email"]] = user

        with open(os.path.join(FIXTURES_DIR, "projects.json"), encoding="utf-8") as f:
            projects_data = json.load(f)

        for proj in projects_data:
            owner = created_users[proj["owner_email"]]
            project, created = Project.objects.get_or_create(
                name=proj["name"],
                defaults={
                    "owner": owner,
                    "description": proj["description"],
                    "status": proj["status"],
                },
            )
            if created:
                project.participants.add(owner)
                for skill_name in proj["skills"]:
                    skill = Skill.objects.get(name=skill_name)
                    project.skills.add(skill)
                for email in proj["participants"]:
                    project.participants.add(created_users[email])

        self.stdout.write(self.style.SUCCESS("Данные загружены."))
