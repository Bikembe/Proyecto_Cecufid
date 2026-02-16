from django.urls import path
from .views import CustomLoginView, CustomLogoutView, dashboard

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', dashboard, name='dashboard'),
]