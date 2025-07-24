from django.urls import path
from tasks.views import (dashboard, HiHowGreetings, CreateTask, ViewProject, TaskDetail, UpdateTask,ManagerDashboard, EmployeeDashboard, DeleteTask)

urlpatterns = [
    # path('manager-dashboard/', manager_dashboard, name="manager-dashboard"), # Original line for function-based view
    path('manager-dashboard/', ManagerDashboard.as_view(), name="manager-dashboard"),
    # path('user-dashboard/', employee_dashboard, name='user-dashboard'), # Original line for function-based view
    path('user-dashboard/', EmployeeDashboard.as_view(), name='user-dashboard'),
    # path('create-task/', create_task, name='create-task'), # Original line for function-based view
    path('create-task/', CreateTask.as_view(), name='create-task'),
    # path('view_task/', view_task, name='view-task'), # Original line for function-based view
    path('view_task/', ViewProject.as_view(), name='view-task'),
    # path('task/<int:task_id>/details/', task_details, name='task-details'), # Original line for function-based view
    path('task/<int:task_id>/details/',
         TaskDetail.as_view(), name='task-details'),
    # path('update-task/<int:id>/', update_task, name='update-task'), # Original line for function-based view
    path('update-task/<int:id>/', UpdateTask.as_view(), name='update-task'),
    # path('delete-task/<int:id>/', delete_task, name='delete-task'), # Original line for function-based view
    path('delete-task/<int:id>/', DeleteTask.as_view(), name='delete-task'),
    path('dashboard/', dashboard, name='dashboard'),
    path('greetings/', HiHowGreetings.as_view(greetings='Hi Good Day!'), name='greetings')
]