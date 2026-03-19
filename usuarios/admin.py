from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Rol, Nadador,
    Sede, Categoria, PlanCurso, Inscripcion
)


class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('email', 'first_name', 'last_name', 'rol', 'estado', 'is_staff')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {
            'fields': ('first_name', 'last_name', 'apellido_materno')
        }),
        ('Rol y Estado', {
            'fields': ('rol', 'estado')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas importantes', {
            'fields': ('last_login',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'rol', 'is_staff', 'is_superuser')}
        ),
    )

    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(PlanCurso)
class PlanCursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_curso', 'sede', 'categoria', 'precio', 'activo')
    list_filter = ('tipo_curso', 'sede', 'categoria', 'activo')
    search_fields = ('nombre',)


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('nadador', 'plan', 'fecha_inicio', 'fecha_fin')
    list_filter = ('plan',)
    search_fields = ('nadador__nombre', 'nadador__apellido_paterno')


admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Rol)
admin.site.register(Nadador)
admin.site.register(Sede)
admin.site.register(Categoria)