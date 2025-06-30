# events/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'events/home.html', {'message': 'Welcome to the Event Management System!'})