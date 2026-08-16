from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.groups.models import StudentRecord

User = get_user_model()


class Command(BaseCommand):
    help = 'Автоматическая связь StudentRecord с User по passport или phone'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Только показать, что будет сделано, без изменений',
        )
        parser.add_argument(
            '--create-users',
            action='store_true',
            help='Создавать новых пользователей, если не найдены',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        create_users = options['create_users']

        # Находим все StudentRecord без связи с User
        unlinked = StudentRecord.objects.filter(user__isnull=True)
        total = unlinked.count()

        self.stdout.write(self.style.WARNING(f'Найдено {total} записей без связи с User'))

        linked_count = 0
        created_count = 0
        skipped_count = 0

        for record in unlinked:
            user = None

            # 1. Поиск по phone (если phone есть в записи)
            if record.phone:
                # Очищаем телефон от пробелов и дефисов для поиска
                clean_phone = record.phone.replace(' ', '').replace('-', '').replace('.', '')

                # Ищем по точному совпадению
                user = User.objects.filter(phone=record.phone).first()

                # Если не нашли, ищем по очищенному телефону
                if not user:
                    users_with_phone = User.objects.filter(phone__isnull=False)
                    for u in users_with_phone:
                        clean_u_phone = u.phone.replace(' ', '').replace('-', '').replace('.', '')
                        if clean_u_phone == clean_phone:
                            user = u
                            break

            # 2. Если не нашли по phone, ищем по full_name
            if not user and record.full_name:
                user = User.objects.filter(full_name=record.full_name).first()

                # Если не нашли точное совпадение, ищем по частичному
                if not user:
                    user = User.objects.filter(
                        Q(full_name__icontains=record.full_name.split()[0]) if record.full_name.split() else Q()
                    ).first()

            # 3. Если нашли пользователя - связываем
            if user:
                if not dry_run:
                    record.user = user
                    record.save()
                linked_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Связан: {record.full_name} → {user.username}')
                )
            else:
                # 4. Если не нашли и разрешено создавать - создаём
                if create_users:
                    if not dry_run:
                        # Создаём username из passport или phone
                        username = record.passport or record.phone or f'student_{record.id}'
                        username = username.replace(' ', '').lower()

                        # Проверяем уникальность username
                        base_username = username
                        counter = 1
                        while User.objects.filter(username=username).exists():
                            username = f'{base_username}_{counter}'
                            counter += 1

                        # Разбиваем full_name на first_name и last_name
                        first_name = ''
                        last_name = ''
                        if record.full_name:
                            parts = record.full_name.strip().split()
                            if len(parts) >= 2:
                                first_name = parts[0]
                                last_name = ' '.join(parts[1:])
                            elif len(parts) == 1:
                                first_name = parts[0]

                        # Создаём пользователя
                        user = User.objects.create_user(
                            username=username,
                            first_name=first_name,
                            last_name=last_name,
                            full_name=record.full_name,
                            phone=record.phone,
                            position=record.position,
                            role='student',
                            password='changeme123'  # Временный пароль
                        )

                        record.user = user
                        record.save()

                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Создан и связан: {record.full_name} → {user.username}')
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'✗ Не найден: {record.full_name} (passport: {record.passport}, phone: {record.phone})')
                    )

        # Итоговая статистика
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('ИТОГО:'))
        self.stdout.write(self.style.SUCCESS(f'  Связано: {linked_count}'))
        if create_users:
            self.stdout.write(self.style.SUCCESS(f'  Создано: {created_count}'))
        self.stdout.write(self.style.WARNING(f'  Пропущено: {skipped_count}'))
        self.stdout.write(self.style.SUCCESS('='*50))
