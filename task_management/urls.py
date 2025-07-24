from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
from core.views import HomeView, NoPermissionView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path("tasks/", include("tasks.urls")),
    path("users/", include('users.urls')),
    # Use .as_view() for class-based views
    path('', HomeView.as_view(), name="home"),
    path('no-permission/', NoPermissionView.as_view(), name='no-permission')
]+debug_toolbar_urls()

# Ctrl + Shift + P
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)