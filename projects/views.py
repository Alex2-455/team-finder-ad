import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from team_finder.constants import (
    PROJECT_STATUS_CLOSED,
    PROJECT_STATUS_OPEN,
    PROJECTS_PER_PAGE,
    SKILLS_AUTOCOMPLETE_LIMIT,
)
from users.utils import paginate
from projects.forms import ProjectForm
from projects.models import Project, Skill


def project_list(request):
    skill_filter = request.GET.get("skill")
    projects = Project.objects.select_related("owner").prefetch_related("participants").all()
    if skill_filter:
        projects = projects.filter(skills__name=skill_filter)

    page_obj = paginate(request, projects, PROJECTS_PER_PAGE)
    all_skills = Skill.objects.all()
    return render(request, "projects/project_list.html", {
        "projects": page_obj,
        "all_skills": all_skills,
        "active_skill": skill_filter,
    })


def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        project.participants.add(request.user)
        return redirect("projects:project_detail", project_id=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if form.is_valid():
        form.save()
        return redirect("projects:project_detail", project_id=project.pk)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if project.status == PROJECT_STATUS_OPEN:
        project.status = PROJECT_STATUS_CLOSED
        project.save()
        return JsonResponse({"status": "ok", "project_status": PROJECT_STATUS_CLOSED})
    return JsonResponse(
        {"status": "error", "message": "Проект уже закрыт"},
        status=HTTPStatus.BAD_REQUEST,
    )


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        return JsonResponse({"status": "ok", "participant": False})
    project.participants.add(request.user)
    return JsonResponse({"status": "ok", "participant": True})


def skills_autocomplete(request):
    query = request.GET.get("q", "")
    if query:
        skills = Skill.objects.filter(
            name__istartswith=query
        ).order_by("name")[:SKILLS_AUTOCOMPLETE_LIMIT]
    else:
        skills = Skill.objects.none()
    data = [{"id": skill.pk, "name": skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_skill(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse({"error": "Нет прав"}, status=HTTPStatus.FORBIDDEN)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        body = {}

    created = False
    added = False

    if "skill_id" in body:
        skill = get_object_or_404(Skill, pk=body["skill_id"])
    elif "name" in body:
        skill, created = Skill.objects.get_or_create(name=body["name"].strip())
    else:
        return JsonResponse(
            {"error": "Передайте skill_id или name"},
            status=HTTPStatus.BAD_REQUEST,
        )

    if not project.skills.filter(pk=skill.pk).exists():
        project.skills.add(skill)
        added = True

    return JsonResponse({
        "skill_id": skill.pk,
        "name": skill.name,
        "created": created,
        "added": added,
    })


@login_required
@require_POST
def remove_skill(request, project_id, skill_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse({"error": "Нет прав"}, status=HTTPStatus.FORBIDDEN)

    skill = get_object_or_404(Skill, pk=skill_id)
    if project.skills.filter(pk=skill.pk).exists():
        project.skills.remove(skill)
        return JsonResponse({"status": "ok"})
    return JsonResponse(
        {"error": "Навык не найден в проекте"},
        status=HTTPStatus.NOT_FOUND,
    )
