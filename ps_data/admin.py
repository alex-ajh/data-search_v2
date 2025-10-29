from django.contrib import admin
from .models import VisitCount, VisitRecord


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


@admin.register(VisitRecord)
class VisitRecordAdmin(admin.ModelAdmin):
    """Admin interface for VisitRecord model"""
    list_display = ('page_url', 'visited_at', 'ip_address', 'short_user_agent')
    list_filter = ('visited_at', 'page_url')
    search_fields = ('page_url', 'ip_address')
    readonly_fields = ('page_url', 'visited_at', 'ip_address', 'user_agent')
    ordering = ('-visited_at',)
    date_hierarchy = 'visited_at'

    def has_add_permission(self, request):
        """Prevent manual addition of visit records"""
        return False

    def short_user_agent(self, obj):
        """Display truncated user agent"""
        if obj.user_agent:
            return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
        return '-'
    short_user_agent.short_description = 'User Agent'
