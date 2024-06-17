from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Division(models.Model):
    division_name = models.CharField(max_length=100, unique=True)
    # code = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.division_name

class Ward(models.Model):
    division = models.ForeignKey(Division, related_name='wards', on_delete=models.CASCADE)
    ward_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('division', 'ward_name')

    def __str__(self):
        return f"{self.ward_name} ({self.division.division_name})"

class Village(models.Model):
    ward = models.ForeignKey(Ward, related_name='villages', on_delete=models.CASCADE)
    village_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('ward', 'village_name')

    def __str__(self):
        return f"{self.village_name} ({self.ward.ward_name})"


# class ImplementationModel(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     office_type = models.CharField(max_length=50, choices=[  # Example choices
#         ('Village Office', 'Village Office'),
#         ('Ward Executive Office', 'Ward Executive Office'),
#         ('Division Office', 'Division Office'),
#         ('Department of Planning and Coordination Office', 'Department of Planning and Coordination Office'),
#         ('District Executive Director Office', 'District Executive Director Office'),
#     ])
    # location = models.ForeignKey(Division, related_name='offices', on_delete=models.CASCADE)
    # email = models.EmailField(max_length=50, unique=True, null=True, blank=True)
    # attachments = models.FileField(upload_to='media/projects/attachments', null=True, blank=True)


    # def __str__(self):
    #     return f"{self.name} ({self.office_type})"


class Project(models.Model):
    supervisor = models.ForeignKey(User, related_name='supervised_projects', on_delete=models.SET_NULL, null=True)
    # implementation_model = models.ForeignKey(ImplementationModel, related_name='projects', on_delete=models.SET_NULL, null=True, blank=True)
    project_name = models.CharField(max_length=255)
    project_code = models.CharField(max_length=50, unique=True)
    implementation_model = models.CharField(max_length=50, blank=True, null=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    source_of_fund = models.CharField(max_length=255)
    description = models.TextField()
    project_pictures = models.ImageField(upload_to='media/projects/pictures/', null=True, blank=True)
    evaluation_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0) 
    location = models.ForeignKey(Village, related_name='projects', on_delete=models.SET_NULL, null=True, blank=True)
    # comments = models.TextField(null=True, blank=True) 

    def __str__(self):
        return self.project_name


class TaskPlan(models.Model):
    task_state = models.CharField(max_length=20)

    def __str__(self):
        return self.task_state


class Task(models.Model):
    STATUS_CHOICES = [
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
    ]

    project = models.ForeignKey(Project, related_name='tasks', on_delete=models.CASCADE)
    task_name = models.CharField(max_length=255)
    description = models.TextField()
    task_state = models.ForeignKey(TaskPlan, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, related_name='tasks', on_delete=models.DO_NOTHING)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To Do')
    budget = models.DecimalField(max_digits=12, decimal_places=2)  # Assuming budget is a decimal field

    def __str__(self):
        return f"{self.task_name} ({self.project.project_name})"

    def clean(self):
        # Ensure task budget is within project's total cost range
        if self.budget < 0:
            raise ValidationError('Budget must be a positive number.')
        
        if self.budget > self.project.total_cost:
            raise ValidationError('Task budget cannot exceed project total cost.')

    def save(self, *args, **kwargs):
        self.full_clean()  # Validate model fields
        super().save(*args, **kwargs)


class Comment(models.Model):
    project = models.ForeignKey(Project, related_name='projects_comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='projects_comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.project_name}"

# For logging all activities
class ActivityLog(models.Model):
    action = models.CharField(max_length=50)
    description = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now_add=True)
