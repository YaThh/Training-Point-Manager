from django.contrib import admin
from django.urls.resolvers import URLResolver

# Register your models here.
class TrainingPointManagerAdminSite(admin.AdminSite):
    site_header = 'Quản lý điểm rèn luyện'


admin_site = TrainingPointManagerAdminSite(name='myapp')