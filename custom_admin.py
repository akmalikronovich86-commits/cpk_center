from django.contrib.admin import AdminSite


class CustomAdminSite(AdminSite):
    site_header = "Xodimlar Malakasini oshirish va Qayta tayyorlash Markazi"
    site_title = "Xodimlar Malakasini oshirish va Qayta tayyorlash Markazi"
    index_title = "Boshqaruv Paneli"

# Создаём экземпляр
custom_admin_site = CustomAdminSite(name='custom_admin')
