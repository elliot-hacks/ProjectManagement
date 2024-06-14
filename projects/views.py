from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.signals import post_save, pre_delete
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.dispatch import receiver
from django.contrib import messages
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import plotly.graph_objects as go
from plotly.offline import plot
import plotly.express as px 
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


# Gant and Pie Charts
@login_required(login_url='login')
def project_dashboard(request):
    projects = Project.objects.all()
    tasks = Task.objects.select_related('project').all()
    
    # Prepare data for Gantt chart
    gantt_data = []
    for task in tasks:
        gantt_data.append({
            'Task': task.name,
            'Start': task.project.start_date,
            'Finish': task.due_date,
            'Resource': task.project.name,
            'Completion': task.get_status_display(),
            'Assigned To': task.assigned_to.username
        })
    
    # Create Gantt chart
    fig = px.timeline(
        gantt_data, 
        x_start='Start', 
        x_end='Finish', 
        y='Task',
        color='Resource', 
        title='Project Timeline',
        labels={'color': 'Project'}
    )
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Task',
        margin=dict(l=20, r=20, t=20, b=20),
        hovermode='x unified'
    )
    gantt_chart = plot(fig, output_type='div')

    # Create additional charts or stats as needed here
    # Example: Project status pie chart
    status_data = tasks.values('status').annotate(count=models.Count('status'))
    labels = [status['status'] for status in status_data]
    values = [status['count'] for status in status_data]

    pie_chart = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
    pie_chart.update_layout(title_text='Tasks Status Distribution')
    pie_chart_div = plot(pie_chart, output_type='div')

    return render(request, 'project_dashboard.html', {
        'gantt_chart': gantt_chart,
        'pie_chart_div': pie_chart_div,
        'projects': projects,
        'tasks': tasks
    })



# PDF generators
@login_required(login_url='login')
def project_report(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    tasks = Task.objects.filter(project=project)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{project.name}_report.pdf"'

    # Create a PDF document
    buffer = response
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Container for the PDF elements
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    # Title
    elements.append(Paragraph(f"Project Report: {project.name}", styles['Title']))
    # Project Details
    project_details = f"""
    <b>Project Name:</b> {project.name}<br/>
    <b>Project Code:</b> {project.id}<br/>
    <b>Supervisor:</b> {project.supervisor.get_full_name()}<br/>
    <b>Total Cost:</b> ${project.budget}<br/>
    <b>Start Date:</b> {project.start_date.strftime('%Y-%m-%d')}<br/>
    <b>End Date:</b> {project.end_date.strftime('%Y-%m-%d')}<br/>
    <b>Source of Fund:</b> {project.source_of_fund}<br/>
    """
    elements.append(Paragraph(project_details, styles['Normal']))
    elements.append(Spacer(1, 12))

    # Task Progress
    task_data = []
    task_data.append(['Task Name', 'Assigned To', 'Due Date', 'Status'])

    for task in tasks:
        task_data.append([
            task.name,
            task.assigned_to.get_full_name(),
            task.due_date.strftime('%Y-%m-%d'),
            task.get_status_display()
        ])

    table = Table(task_data, colWidths=[200, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    # Progress Evaluation
    completed_tasks = tasks.filter(status=Task.STATUS_DONE).count()
    total_tasks = tasks.count()
    progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    progress_evaluation = f"""
    <b>Progress Evaluation:</b> {progress_percentage:.2f}% Complete
    """
    elements.append(Paragraph(progress_evaluation, styles['Normal']))

    # Build the PDF
    doc.build(elements)

    return response


# Signals
@receiver(post_save, sender=Task)
def send_task_notification(sender, instance, created, **kwargs):
    if created:
        subject = f"New Task Assigned: {instance.name}"
        message = f"A new task has been assigned to you: {instance.name}\nDescription: {instance.description}\nDue Date: {instance.due_date}"
        recipient_list = [instance.assigned_to.email]
        send_mail(subject, message, 'admin@yourdomain.com', recipient_list)


@receiver(post_save, sender=Task)
def log_task_activity(sender, instance, created, **kwargs):
    action = 'Created' if created else 'Updated'
    ActivityLog.objects.create(
        action=action,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.id,
        description=f'{action} task: {instance.name}'
    )

@receiver(pre_delete, sender=Task)
def log_task_deletion(sender, instance, **kwargs):
    ActivityLog.objects.create(
        action='Deleted',
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.id,
        description=f'Deleted task: {instance.name}'
    )

