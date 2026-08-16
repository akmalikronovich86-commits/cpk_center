from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def lecturer_required(view_func):
    """
    Декоратор для проверки роли преподавателя
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.role != 'lecturer':
            messages.error(request, 'Sizga bu sahifaga kirish taqiqlangan')
            return redirect('home')

        if not request.user.is_active:
            messages.error(request, 'Sizning profilingiz faol emas. Administrator bilan bog\'laning')
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper

def require_role(required_role):
    """
    Универсальный декоратор для проверки любой роли
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.role != required_role:
                messages.error(request, f'Sizga bu sahifaga kirish taqiqlangan. Kerakli rol: {required_role}')
                return redirect('home')

            if not request.user.is_active:
                messages.error(request, 'Sizning profilingiz faol emas')
                return redirect('login')

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
