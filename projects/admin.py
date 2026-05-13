from django.contrib import admin

from projects.models import Project, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "status", "created_at", "skills_list", "participants_list")
    search_fields = ("name", "description")
    list_filter = ("status", "created_at")

    @admin.display(description="Навыки")
    def skills_list(self, obj):
        return ", ".join(skill.name for skill in obj.skills.all())

    @admin.display(description="Участники")
    def participants_list(self, obj):
        return ", ".join(
            f"{user.name} {user.surname}" for user in obj.participants.all()
        )
