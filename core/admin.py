from django.contrib import admin
from .models import UserActivity

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'tool_name', 'action', 'ip_address', 'created_at')
    list_filter = ('tool_name', 'action', 'created_at')
    search_fields = ('user__username', 'action', 'details')
    readonly_fields = ('user', 'tool_name', 'action', 'details', 'ip_address', 'created_at', 'updated_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False