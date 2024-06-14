from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone
from .models import Project, Task, Division, Ward, Village, Office
from .forms import UserRegistrationForm, ProjectForm, TaskForm


@login_required(login_url='login')
def index(request):
    divisions = Division.objects.prefetch_related('wards__villages').all()
    projects = Project.objects.select_related('supervisor', 'location__ward__division', 'office').all()
    tasks = Task.objects.select_related('project__location__ward__division', 'assigned_to').all()
    
    return render(request, 'index.html', {
        'divisions': divisions,
        'projects': projects,
        'tasks': tasks
    })

def u_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})

def u_login(request):
    return render(request, 'registration/login.html')

def about(request):
    return render(request, 'about.html')


def custom_logout(request):
    logout(request)
    return redirect(reverse('login'))


@login_required(login_url='login')
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = project.tasks.select_related('assigned_to').all()

    return render(request, 'project_detail.html', {
        'project': project,
        'tasks': tasks
    })


### arleady on top for post_detail
# @login_required(login_url='login')
# def task_detail(request, task_id):
#     task = get_object_or_404(Task, id=task_id)

#     return render(request, 'task_detail.html', {
#         'task': task
#     })

# Views for listing and filtering based on hierarchy

@login_required(login_url='login')
def division_detail(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    wards = division.wards.all()

    return render(request, 'division_detail.html', {
        'division': division,
        'wards': wards
    })

@login_required(login_url='login')
def ward_detail(request, ward_id):
    ward = get_object_or_404(Ward, id=ward_id)
    villages = ward.villages.all()

    return render(request, 'ward_detail.html', {
        'ward': ward,
        'villages': villages
    })

@login_required(login_url='login')
def village_detail(request, village_id):
    village = get_object_or_404(Village, id=village_id)
    projects = village.projects.all()

    return render(request, 'village_detail.html', {
        'village': village,
        'projects': projects
    })

# Project and Task creation views
@login_required(login_url='login')
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.supervisor = request.user  # Assuming the current user is the supervisor
            project.save()
            messages.success(request, 'Project created successfully.')
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()

    return render(request, 'create_project.html', {'form': form})


@login_required(login_url='login')
def create_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            messages.success(request, 'Task added successfully.')
            return redirect('project_detail', project_id=project.id)
    else:
        form = TaskForm()

    return render(request, 'create_task.html', {'form': form, 'project': project})
