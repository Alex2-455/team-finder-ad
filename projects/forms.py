from django import forms

from team_finder.constants import PROJECT_STATUS_CHOICES
from users.forms import GithubURLValidatorMixin
from projects.models import Project


class ProjectForm(GithubURLValidatorMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "status": forms.Select(choices=PROJECT_STATUS_CHOICES),
        }
