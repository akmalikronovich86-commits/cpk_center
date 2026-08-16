from django.shortcuts import redirect


class AdminAccessMiddleware:
    """Ограничение доступа к админке: только staff, лекторы - в свой кабинет."""

    STAFF_ROLES = {'admin', 'director', 'department_head', 'methodist'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if not request.user.is_authenticated:
                return redirect('login')

            role = getattr(request.user, 'role', None)
            if role == 'lecturer':
                return redirect('lecturers:lecturer_dashboard')

            if not (request.user.is_staff or request.user.is_superuser or role in self.STAFF_ROLES):
                return redirect('login')

        return self.get_response(request)
