from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.groups.models import StudentRecord
from django.db.models import Q

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

        # Все записи без связи
        unlinked = StudentRecord.objects.filter(user__isnull=True)
        total = unlinked.count()
        self.stdout.write(self.style.WARNING(f'Найдено {total} записей без связи с User'))

        # Уже занятые User (чтобы не нарушить OneToOne)
        assigned_user_ids = set(
            StudentRecord.objects.exclude(user__isnull=True).values_list('user_id', flat=True)
        )

        linked_count = 0
        created_count = 0
        skipped_duplicate_user = 0
        skipped_not_found = 0
        errors = 0

        for record in unlinked:
            user = None

            try:
                # 1. Поиск по phone
                if record.phone:
                    clean_phone = record.phone.replace(' ', '').replace('-', '').replace('.', '')
                    candidates = User.objects.filter(phone__isnull=False)
                    for u in candidates:
                        if u.phone.replace(' ', '').replace('-', '').replace('.', '') == clean_phone:
                            user = u
                            break

                # 2. Поиск по full_name
                if not user and record.full_name:
                    user = User.objects.filter(full_name=record.full_name).first()

                # 3. Проверка на дубликат OneToOne
                if user and user.id in assigned_user_ids:
                    skipped_duplicate_user += 1
                    self.stdout.write(self.style.WARNING(
                        f'⚠ Пропущен (User уже связан): {record.full_name} → User ID {user.id}'
                    ))
                    continue

                # 4. Связываем существующего
                if user:
                    if not dry_run:
                        record.user = user
                        record.save()
                        assigned_user_ids.add(user.id)
                    linked_count += 1
                    self.stdout.write(self.style.SUCCESS(
                        f'✓ Связан: {record.full_name} → {user.username}'
                    ))
                else:
                    # 5. Создаём нового (если разрешено)
                    if create_users:
                        if not dry_run:
                            username = record.passport or record.phone or f'student_{record.id}'
                            username = username.replace(' ', '').lower()
                            base_username = username
                            counter = 1
                            while User.objects.filter(username=username).exists():
                                username = f'{base_username}_{counter}'
                                counter += 1

                            first_name = last_name = ''
                            if record.full_name:
                                parts = record.full_name.strip().split()
                                if len(parts) >= 2:
                                    first_name = parts[0]
                                    last_name = ' '.join(parts[1:])
                                else:
                                    first_name = parts[0]

                            user = User.objects.create_user(
                                username=username,
                                first_name=first_name,
                                last_name=last_name,
                                full_name=record.full_name,
                                phone=record.phone,
                                position=record.position,
                                role='student',
                                password='changeme123'
                            )
                            record.user = user
                            record.save()
                            assigned_user_ids.add(user.id)

                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'✓ Создан и связан: {record.full_name} → {user.username}'
                        ))
                    else:
                        skipped_not_found += 1
                        self.stdout.write(self.style.WARNING(
                            f'✗ Не найден: {record.full_name} (passport: {record.passport}, phone: {record.phone})'
                        ))

            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f'❌ Ошибка при обработке {record.id}: {str(e)[:100]}'))
                continue

        # Итоговая статистика
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('ИТОГО:'))
        self.stdout.write(self.style.SUCCESS(f'  Связано с существующими: {linked_count}'))
        if create_users:
            self.stdout.write(self.style.SUCCESS(f'  Создано новых: {created_count}'))
        self.stdout.write(self.style.WARNING(f'  Пропущено (User уже занят): {skipped_duplicate_user}'))
        self.stdout.write(self.style.WARNING(f'  Пропущено (не найдено): {skipped_not_found}'))
        if errors:
            self.stdout.write(self.style.ERROR(f'  Ошибок: {errors}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
