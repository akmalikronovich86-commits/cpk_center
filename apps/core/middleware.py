from django.shortcuts import redirect

class AdminAccessMiddleware:
    """Ограничение доступа к админке для аутентифицированных пользователей с правами staff"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Проверяем, если запрос к админке
        if request.path.startswith('/admin/'):
            # Если пользователь не аутентифицирован
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Запрещаем доступ лекторам к админке
            if hasattr(request.user, 'role') and request.user.role == 'lecturer':
                return redirect('lecturers:lecturer_dashboard')
            
            # Для остальных - проверяем is_staff
            if not request.user.is_staff:
                return redirect('login')
        
        response = self.get_response(request)
        return response
