from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'home.html'

class NoPermissionView(TemplateView):
    template_name = 'no_permission.html'