# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class VisitCount(models.Model):
    """Model to track page visit counts"""
    page_url = models.CharField(max_length=255, unique=True, help_text="URL path of the page")
    count = models.IntegerField(default=0, help_text="Number of visits to this page")
    last_visited = models.DateTimeField(auto_now=True, help_text="Last visit timestamp")
    created_at = models.DateTimeField(auto_now_add=True, help_text="First visit timestamp")

    class Meta:
        verbose_name = "Visit Count"
        verbose_name_plural = "Visit Counts"
        ordering = ['-count']

    def __str__(self):
        return f"{self.page_url} - {self.count} visits"

    @classmethod
    def increment(cls, page_url):
        """Increment visit count for a given page URL"""
        visit_count, created = cls.objects.get_or_create(page_url=page_url)
        visit_count.count += 1
        visit_count.save()
        return visit_count

    @classmethod
    def get_total_visits(cls):
        """Get total visits across all pages"""
        return cls.objects.aggregate(total=models.Sum('count'))['total'] or 0


class VisitRecord(models.Model):
    """Model to track individual visit records for analytics"""
    page_url = models.CharField(max_length=255, help_text="URL path of the page", db_index=True)
    visited_at = models.DateTimeField(auto_now_add=True, help_text="Visit timestamp", db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Visitor IP address")
    user_agent = models.TextField(null=True, blank=True, help_text="User agent string")

    class Meta:
        verbose_name = "Visit Record"
        verbose_name_plural = "Visit Records"
        ordering = ['-visited_at']
        indexes = [
            models.Index(fields=['page_url', 'visited_at']),
        ]

    def __str__(self):
        return f"{self.page_url} - {self.visited_at}"

    @classmethod
    def get_monthly_stats(cls, months=12):
        """Get visit counts grouped by month for the last N months"""
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        from datetime import datetime, timedelta
        from django.utils import timezone

        # Get date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=months * 30)

        # Query visits grouped by month
        monthly_data = cls.objects.filter(
            visited_at__gte=start_date
        ).annotate(
            month=TruncMonth('visited_at')
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')

        return monthly_data
# Unable to inspect table 'auth_group'
# The error was: __new__() missing 1 required positional argument: 'collation'
# Unable to inspect table 'auth_group_permissions'
# The error was: __new__() missing 1 required positional argument: 'collation'
# Unable to inspect table 'auth_permission'
# The error was: __new__() missing 1 required positional argument: 'collation'
# Unable to inspect table 'auth_user'
# The error was: __new__() missing 1 required positional argument: 'collation'
# Unable to inspect table 'auth_user_groups'
# The error was: __new__() missing 1 required positional argument: 'collation'
# Unable to inspect table 'auth_user_user_permissions'
# The error was: __new__() missing 1 required positional argument: 'collation'
# Unable to inspect table 'django_admin_log'
# The error was: __new__() missing 1 required positional argument: 'collation'
# Unable to inspect table 'django_content_type'
# The error was: __new__() missing 1 required positional argument: 'collation'
# Unable to inspect table 'django_migrations'
# The error was: __new__() missing 1 required positional argument: 'collation'
# Unable to inspect table 'django_session'
# The error was: __new__() missing 1 required positional argument: 'collation'
# Unable to inspect table 'file_info'
# The error was: 'NoneType' object is not subscriptable
# Unable to inspect table 'file_info_1'
# The error was: 'NoneType' object is not subscriptable
# Unable to inspect table 'file_info_gcs'
# The error was: 'NoneType' object is not subscriptable
# Unable to inspect table 'file_info_gcs_20210823'
# The error was: 'NoneType' object is not subscriptable
