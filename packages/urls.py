from django.contrib import admin
from django.urls import path, re_path

from packages import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'package/([a-z0-9-]+)/request', views.request, name='request'),
    re_path(r'package/([a-z0-9-]+)', views.package, name='package'),
    path('admin/', admin.site.urls),
]
