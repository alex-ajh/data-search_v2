from django.contrib import admin
from .models import VisitCount


@admin.register(VisitCount)
class VisitCountAdmin(admin.ModelAdmin):
    """Admin interface for VisitCount model"""
    list_display = ('page_url', 'count', 'last_visited', 'created_at')
    list_filter = ('last_visited', 'created_at')
    search_fields = ('page_url',)
    readonly_fields = ('created_at', 'last_visited')
    ordering = ('-count',)

    def has_add_permission(self, request):
        """Prevent manual addition of visit counts"""
        return False
