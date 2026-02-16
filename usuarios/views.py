from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")

@login_required
def dashboard(request):

    if not request.user.rol:
        return render(request, "dashboard.html")

    rol = request.user.rol.nombre

    if rol == "Administrador":
        return render(request, "dashboard_admin.html")

    elif rol == "Maestro":
        return render(request, "dashboard_maestro.html")

    elif rol == "Médico":
        return render(request, "dashboard_medico.html")

    elif rol == "Caja":
        return render(request, "dashboard_caja.html")

    return render(request, "dashboard.html")