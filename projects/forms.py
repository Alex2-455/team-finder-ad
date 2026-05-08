from django import forms
from .models import Project
from team_finder.constants import GITHUB_URL_PATTERN, PROJECT_STATUS_CHOICES


class ProjectForm(forms.ModelForm):
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

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and GITHUB_URL_PATTERN not in url:
            raise forms.ValidationError("Ссылка должна вести на github.com")
        return url