from django.urls import path
from . import views

app_name = 'grasshopper'
urlpatterns = [
    path('', views.athlet_list, name='athlet_list'),  # отображение списка спортсменов
    path('<int:id>/', views.athlet_detail, name='athlet_detail'),
    path('add/', views.athlet_add, name='athlet_add'),
    path('change/<int:id>/', views.athlet_change, name='athlet_change'),
    path('delete/<int:id>/', views.athlet_delete, name='athlet_delete'),
    path('results/', views.results_view, name='results_view'),
    path("login/", views.competition_login, name="competition_login"),
    path("register/", views.competition_register, name="competition_register"),
    path("logout/", views.logout_view, name="logout_view"),  # Добавьте выход, если необходимо
    path("list/", views.athlet_list, name="athlet_list"),
    path('logout/', views.logout_view, name='logout'),
    path('athletes/print/', views.print_protocol, name='print_protocol'),
]