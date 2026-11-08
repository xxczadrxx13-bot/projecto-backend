from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def requiere_rol(*roles_permitidos):
    def decorador(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.groups.filter(name__in=roles_permitidos).exists():
                return view_func(request, *args, **kwargs)
            messages.error(request, "Acceso denegado: no tienes permisos para ejecutar esta acción.")
            return redirect('admin_dashboard')
        return wrapper
    return decorador