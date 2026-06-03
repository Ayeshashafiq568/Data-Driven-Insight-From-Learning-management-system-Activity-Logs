from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Course, Student, ActivityLog, Prediction


class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    list_display = ['username', 'email', 'role', 'is_staff', 'is_active']
    list_filter = ['role', 'is_staff', 'is_active']


admin.site.register(User, CustomUserAdmin)
admin.site.register(Course)
admin.site.register(Student)
admin.site.register(ActivityLog)
admin.site.register(Prediction)
