from django.core.management.base import BaseCommand
from django.core.management import call_command
from users.models import User
from projects.models import Project, Skill


class Command(BaseCommand):
    help = "Создаёт тестовые данные для демонстрации"

    def handle(self, *args, **options):
        self.stdout.write("Применяю миграции...")
        call_command("migrate", "--noinput")

        # Создаём навыки
        self.stdout.write("Создаю навыки...")
        skills_data = [
            "Python", "Django", "JavaScript", "React", "TypeScript",
            "Docker", "PostgreSQL", "Redis", "Machine Learning",
            "UI/UX Design", "Figma", "Node.js", "Vue.js",
            "Kubernetes", "CI/CD", "Blockchain", "C++", "Go", "Rust",
            "HTML", "CSS", "1C", "C#",
        ]
        for name in skills_data:
            Skill.objects.get_or_create(name=name)

        # Пользователи
        self.stdout.write("Создаю пользователей...")
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
                user.save()
                role = "администратор" if is_superuser else "пользователь"
                self.stdout.write(f"  {data['name']} {data['surname']} ({role}) создан: {data['email']} / {data['password']}")
            else:
                self.stdout.write(f"  {data['name']} {data['surname']} уже существует")
            created_users[data["email"]] = user

        # Проекты
        self.stdout.write("Создаю проекты...")
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
                self.stdout.write(f"  Проект «{project.name}» создан ({proj['status']})")
            else:
                self.stdout.write(f"  Проект «{project.name}» уже существует")

        self.stdout.write(self.style.SUCCESS("\nГотово! Данные созданы."))
        self.stdout.write("")
        self.stdout.write("Для входа:")
        self.stdout.write("  admin@mail.ru / admin (администратор)")
        self.stdout.write("  aleks.malygin200@yandex.ru / 1234 (Валерий Умаров)")
        self.stdout.write("  aleks.malygin200@mail.ru / 1234 (Алексей Малыгин)")