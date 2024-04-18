from django.contrib import admin
from django.urls.resolvers import URLResolver
from django.contrib.auth.models import Permission

from .models import *

# Register your models here.
class TrainingPointManagerAdminSite(admin.AdminSite):
    site_header = 'Quản lý điểm rèn luyện'


admin_site = TrainingPointManagerAdminSite(name='myapp')
admin_site.register(Permission)
admin_site.register(Activity)
admin_site.register(News)
admin_site.register(User)
admin_site.register(Department)
admin_site.register(Grade)
admin_site.register(Achievement)