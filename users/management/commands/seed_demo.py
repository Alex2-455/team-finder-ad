from django.core.management.base import BaseCommand
from django.core.management import call_command
from users.models import User
from projects.models import Project, Skill
import os
from django.conf import settings


class Command(BaseCommand):
    help = "Создаёт тестовые данные для демонстрации"

    def handle(self, *args, **options):
        call_command("migrate", "--noinput")

        skills_data = [
            "Python", "Django", "JavaScript",
            "PostgreSQL", "C++",
            "HTML", "CSS", "1C", "C#",
        ]
        for name in skills_data:
            Skill.objects.get_or_create(name=name)

        users_data = [
            {
                "email": "admin@mail.ru",
                "name": "admin",
                "surname": "admin",
                "password": "admin",
                "phone": "+79220953942",
                "about": "",
                "is_superuser": True,
                "is_staff": True,
            },
            {
                "email": "aleks.malygin200@yandex.ru",
                "name": "Валерий",
                "surname": "Умаров",
                "password": "1234",
                "phone": "+79220953941",
                "about": "",
            },
            {
                "email": "aleks.malygin200@mail.ru",
                "name": "Алексей",
                "surname": "Малыгин",
                "password": "1234",
                "phone": "",
                "about": "",
            },
        ]

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

                first_letter = data["name"][0].upper()
                avatar_dir = os.path.join(settings.MEDIA_ROOT, "avatars")
                existing_avatar = None
                if os.path.exists(avatar_dir):
                    for filename in sorted(os.listdir(avatar_dir)):
                        if filename.startswith(f"avatar_{first_letter}") and filename.endswith(".png") and len(filename) < 70:
                            existing_avatar = filename
                            break
                if existing_avatar:
                    user.avatar = f"avatars/{existing_avatar}"

                user.save()
            created_users[data["email"]] = user

        projects_data = [
            {
                "owner_email": "admin@mail.ru",
                "name": "Помощь с обслуживанием сайта TeamFinder",
                "description": "требуются трудолюбивые программисты готовые вводить нововведения",
                "status": "open",
                "skills": ["Python", "Django", "JavaScript", "HTML", "CSS"],
                "participants": ["aleks.malygin200@yandex.ru", "aleks.malygin200@mail.ru"],
            },
            {
                "owner_email": "admin@mail.ru",
                "name": "Создание сайта",
                "description": "иметь навыки имеющиеся в описании",
                "status": "closed",
                "skills": ["Django", "PostgreSQL", "JavaScript"],
                "participants": ["aleks.malygin200@yandex.ru", "aleks.malygin200@mail.ru"],
            },
            {
                "owner_email": "aleks.malygin200@yandex.ru",
                "name": "Программирование подводного робота",
                "description": "требуется опыт, и возможность командировка",
                "status": "open",
                "skills": ["C#", "C++"],
                "participants": ["admin@mail.ru", "aleks.malygin200@mail.ru"],
            },
            {
                "owner_email": "aleks.malygin200@yandex.ru",
                "name": "Создание базы для бухгалтерии в компания",
                "description": "требуется команда для трудной и рутинной работы с большой оплатой",
                "status": "open",
                "skills": ["1C", "PostgreSQL"],
                "participants": ["admin@mail.ru"],
            },
            {
                "owner_email": "aleks.malygin200@mail.ru",
                "name": "создание браузера",
                "description": "нужно создать браузер с обширным функционалом, лучше Chrome",
                "status": "open",
                "skills": ["C++", "JavaScript", "HTML", "CSS"],
                "participants": [],
            },
        ]

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