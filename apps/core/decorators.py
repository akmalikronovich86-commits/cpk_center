from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def role_required(*roles):
    """Декоратор RBAC: пускает только перечисленные роли (или staff/superuser)."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            user = request.user
            if user.role in roles or user.is_staff or user.is_superuser:
                return view(request, *args, **kwargs)
            messages.warning(
                request,
                "Siz bu sahifaga kira olmaysiz. O'z shaxsiy kabinetingizga yo'naltirildingiz.",
            )
            return redirect('/')   # smart_redirect разведёт по роли
        return wrapper
    return decorator
