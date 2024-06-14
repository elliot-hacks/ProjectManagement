from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Division(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class Ward(models.Model):
    division = models.ForeignKey(Division, related_name='wards', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('division', 'name')

    def __str__(self):
        return f"{self.name} ({self.division.name})"

class Village(models.Model):
    ward = models.ForeignKey(Ward, related_name='villages', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('ward', 'name')

    def __str__(self):
        return f"{self.name} ({self.ward.name})"


class Office(models.Model):
    name = models.CharField(max_length=100, unique=True)
    office_type = models.CharField(max_length=50, choices=[  # Example choices
        ('Village Office', 'Village Office'),
        ('Ward Executive Office', 'Ward Executive Office'),
        ('Division Office', 'Division Office'),
        ('Department of Planning and Coordination Office', 'Department of Planning and Coordination Office'),
        ('District Executive Director Office', 'District Executive Director Office'),
    ])
    location = models.ForeignKey(Division, related_name='offices', on_delete=models.CASCADE)  # Assuming offices are at Division level

    def __str__(self):
        return f"{self.name} ({self.type})"


class Project(models.Model):
    supervisor = models.ForeignKey(User, related_name='supervised_projects', on_delete=models.SET_NULL, null=True)
    office = models.ForeignKey(Office, related_name='projects', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    project_code = models.CharField(max_length=50, unique=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    source_of_fund = models.CharField(max_length=255)
    description = models.TextField()
    project_pictures = models.ImageField(upload_to='media/projects/pictures/', null=True, blank=True)
    evaluation_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0) 
    location = models.ForeignKey(Village, related_name='projects', on_delete=models.SET_NULL, null=True, blank=True)
    comments = models.TextField(null=True, blank=True) 

    def __str__(self):
        return self.name



class Task(models.Model):
    STATUS_CHOICES = [
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
    ]

    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey(User, related_name='tasks', on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')

    def __str__(self):
        return f"{self.name} ({self.project.name})"


# For logging all activities
class ActivityLog(models.Model):
    action = models.CharField(max_length=50)
    description = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now_add=True)
