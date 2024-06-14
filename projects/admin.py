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
