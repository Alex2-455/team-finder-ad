import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Project, Skill
from .forms import ProjectForm
from team_finder.constants import PROJECTS_PER_PAGE, SKILLS_AUTOCOMPLETE_LIMIT


def project_list(request):
    skill_filter = request.GET.get("skill")
    projects = Project.objects.select_related("owner").prefetch_related("participants").all()
    if skill_filter:
        projects = projects.filter(skills__name=skill_filter)

    paginator = Paginator(projects, PROJECTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

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
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:project_detail", project_id=project.pk)
    else:
        form = ProjectForm()
    return render(request, "projects/create-project.html", {"form": form, "is_edit": False})


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:project_detail", project_id=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, "projects/create-project.html", {"form": form, "is_edit": True})


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id, owner=request.user)
    if project.status == "open":
        project.status = "closed"
        project.save()
        return JsonResponse({"status": "ok", "project_status": "closed"})
    return JsonResponse({"status": "error", "message": "Проект уже закрыт"}, status=400)


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.user in project.participants.all():
        project.participants.remove(request.user)
        return JsonResponse({"status": "ok", "participant": False})
    else:
        project.participants.add(request.user)
        return JsonResponse({"status": "ok", "participant": True})


@login_required
@require_POST
def toggle_favorite(request, project_id):
    return JsonResponse({"status": "ok", "favorited": False})


def skills_autocomplete(request):
    q = request.GET.get("q", "")
    if q:
        skills = Skill.objects.filter(name__istartswith=q).order_by("name")[:SKILLS_AUTOCOMPLETE_LIMIT]
    else:
        skills = Skill.objects.none()
    data = [{"id": s.pk, "name": s.name} for s in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_skill(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if project.owner != request.user:
        return JsonResponse({"error": "Нет прав"}, status=403)

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
        return JsonResponse({"error": "Передайте skill_id или name"}, status=400)

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
        return JsonResponse({"error": "Нет прав"}, status=403)

    skill = get_object_or_404(Skill, pk=skill_id)
    if project.skills.filter(pk=skill.pk).exists():
        project.skills.remove(skill)
        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "Навык не найден в проекте"}, status=404)