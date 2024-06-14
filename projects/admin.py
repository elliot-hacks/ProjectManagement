from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.utils.html import format_html, urlencode
from django.urls import reverse
from django.contrib import messages
from . import models


# Register your models here.
class VillageInline(admin.TabularInline):
    model = models.Village
    extra = 1

class WardInline(admin.TabularInline):
    model = models.Ward
    extra = 1


@admin.register(models.Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    inlines = [WardInline]


@admin.register(models.Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'division')
    search_fields = ('name',)
    list_filter = ('division',)
    inlines = [VillageInline]


@admin.register(models.Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ('name', 'ward')
    search_fields = ('name',)
    list_filter = ('ward', 'ward__division')


class TaskInline(admin.TabularInline):
    model = models.Task
    extra = 1


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_code', 'supervisor', 'total_cost', 'start_date', 'end_date', 'evaluation_percentage', 'location', 'office')
    search_fields = ('name', 'project_code', 'supervisor__username', 'location__name')
    list_filter = ('start_date', 'end_date', 'supervisor', 'location', 'office')
    readonly_fields = ('start_date', 'supervisor')  # start_date and supervisor are read-only after creation
    inlines = [TaskInline]
    fieldsets = (
        ('General Information', {
            'fields': ('name', 'project_code', 'description', 'total_cost', 'start_date', 'end_date', 'source_of_fund', 'evaluation_percentage', 'supervisor')
        }),
        ('Location and Office', {
            'fields': ('location', 'office')
        }),
        ('Attachments', {
            'fields': ('project_pictures',)
        }),
    )

@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'assigned_to', 'status', 'due_date')
    search_fields = ('name', 'project__name', 'assigned_to__username')
    list_filter = ('status', 'due_date', 'project')
    readonly_fields = ('project',)  # Task should remain linked to its project and not changeable after creation
    fieldsets = (
        (None, {
            'fields': ('project', 'name', 'description', 'assigned_to', 'due_date', 'status')
        }),
    )


@admin.register(models.Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('name', 'office_type', 'location')
    search_fields = ('name', 'office_type')
    list_filter = ('office_type',)



# Custom dashbord for every user
# from admin_tools.dashboard import modules
# from admin_tools.dashboard.models import DashboardPreferences
# from admin_tools.utils import get_admin_site

# from .dashboard import CustomIndexDashboard, MyAppDashboard

# admin.site.unregister(DashboardPreferences)



# To be implemented if there is confict of one group deleting user from other group of superior priveledges
"""
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Profile  # Assuming Profile holds office_type


class CustomUserAdmin(UserAdmin):
    def has_delete_permission(self, request, obj=None):
        # Check if the user has the delete permission
        has_perm = super().has_delete_permission(request, obj)

        # Additional check: Prevent lower-level staff from deleting higher-level staff
        if obj is not None and has_perm:
            if not request.user.is_superuser:
                # Define hierarchy (higher numbers are more privileged)
                office_hierarchy = {
                    'Village Office': 1,
                    'Ward Executive Office': 2,
                    'Division Office': 3,
                    'Department of Planning and Coordination Office': 4,
                    'District Executive Director Office': 5,
                }

                # Get the user's office type
                user_office_type = getattr(request.user.profile, 'office_type', None)
                obj_office_type = getattr(obj.profile, 'office_type', None)

                if office_hierarchy.get(user_office_type, 0) < office_hierarchy.get(obj_office_type, 0):
                    return False  # Deny delete permission if user is in a lower-level group
        return has_perm

    def delete_model(self, request, obj):
        # Additional check before deletion
        if not self.has_delete_permission(request, obj):
            raise PermissionDenied("You do not have permission to delete this user.")
        super().delete_model(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)



def delete_user_view(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    
    if request.user.has_perm('auth.delete_user'):
        user_office_type = request.user.profile.office_type
        target_office_type = user_to_delete.profile.office_type

        office_hierarchy = {
            'Village Office': 1,
            'Ward Executive Office': 2,
            'Division Office': 3,
            'Department of Planning and Coordination Office': 4,
            'District Executive Director Office': 5,
        }

        if office_hierarchy.get(user_office_type, 0) < office_hierarchy.get(target_office_type, 0):
            return HttpResponseForbidden("You do not have permission to delete this user.")

        user_to_delete.delete()
        return redirect('success_page')
    
    return HttpResponseForbidden("You do not have delete permission.")

"""